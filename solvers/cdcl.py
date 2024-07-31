from solvers.unit_propagate import unit_propagate, simplify
from solvers.utils import get_unique_literals_in_formula
import copy
import random
import time

class cdcl:
    def __init__(self) -> None:
        pass

    # resets/initializes all variables
    def reset_variables(self, formula):
        self.formula = copy.deepcopy(formula) # = original formula
        self.known_clauses = copy.deepcopy(formula) # = original formula + learned clauses
        self.propagation_count = 0
        self.decision_count = 0
        self.conflict_count = 0
        self.learned_clause_count = 0
        self.deleted_clause_count = 0
        self.restart_count = 0
        self.minimized_clause_count = 0
        self.sat = True

        # init data structures
        self.decision_level = 0
        self.assignments = [[]] # [[decision_level_0_assignments],[decision_level_1_assignments],[decision_level_2_assignments],...]
        self.unassigned_variables = get_unique_literals_in_formula(self.known_clauses, only_positive=True) 
        self.num_literals = len(self.unassigned_variables)
        self.learned_clauses = []
        self.decision_level_per_assigned_literal = {} # {literal: decision_level} -> also helpful for O(1) lookups if literal is assigned
        self.conflict_clause = None

    # main function to solve formula
    def solve(self, formula):
        self.time_start = time.time()
        self.reset_variables(formula)

        # actual algorithm
        while len(self.unassigned_variables) > 0:
            self.decision_level += 1
            self.assignments.append([])
            # assign truth value to a literal
            self.decide()
            # unit propagate
            self.propagate(self.formula)

            # if conflict occurs
            while self.conflict_clause != None:
                self.conflict_count += 1
                # if conflict occurs at the root level -> unsat
                if self.decision_level == 0:
                    self.sat = False
                    self.write_proof()
                    return self.return_statement()
                # learn clause and figure out backtracking level
                new_decision_level = self.analyze_conflict()
                # backtrack
                self.backtrack(new_decision_level)
                # unit propagate
                self.propagate(copy.deepcopy(self.known_clauses))

            # restart occasionally
            self.apply_restart_policy()

        # return sat
        self.write_proof()
        return self.return_statement()
    
    # returns statistics for last solve run
    def get_statistics(self):
        runtime = time.time()-self.time_start
        return {"runtime": runtime, "propagation_count": self.propagation_count, "decision_count": self.decision_count, 
                "conflict_count": self.conflict_count, "learned_clause_count": self.learned_clause_count, 
                "restart_count": self.restart_count, "deleted_clause_count": self.deleted_clause_count, 
                "minimized_clause_count": self.minimized_clause_count}

    # creates the return statement for the last solve run
    def return_statement(self):
        return_statement = {"SAT": self.sat}
        if self.sat: return_statement["model"] = sum(self.assignments, [])
        return_statement.update(self.get_statistics())
        return return_statement
            
    # returns the new decision variable using random variable and polarity
    def get_decision_variable(self):
        decision_variable = random.sample(self.unassigned_variables,1)[0]
        return decision_variable if random.choice([True,False]) else -decision_variable

    # returns the new decision variable and updates data structures accordingly
    def decide(self):
        self.decision_count += 1
        decision_variable = self.get_decision_variable()
        self.remember_assignments(decision_variable)
        self.decision_level_per_assigned_literal[decision_variable] = len(self.assignments)-1
        return decision_variable
    
    # updates data structures with new learned clause
    def remember_learned_clause(self,learned_clause):
        self.learned_clauses.append(learned_clause)
        self.known_clauses.append(learned_clause)
        self.learned_clause_count += 1

    # learns new clause and returns new decision level
    def analyze_conflict(self):
        learned_clause = [-decision_level_assignments[0] for decision_level_assignments in self.assignments[1:]]
        self.remember_learned_clause(learned_clause)
        return self.decision_level-1

    # backtracks data structures to new decision level
    def backtrack(self, new_decision_level):
        # backtrack decision_level_per_assigned_literal
        for literal, decision_level in list(self.decision_level_per_assigned_literal.items()):
            if decision_level > new_decision_level:
                del self.decision_level_per_assigned_literal[literal]
        # backtrack assignments and unassigned_variables
        for _ in range(self.decision_level-new_decision_level):
            decision_level_assignments = self.assignments.pop()
            for literal in decision_level_assignments:
                self.unassigned_variables.append(abs(literal))
        self.decision_level = new_decision_level
        self.conflict_clause = None

    # updates data structures with new assignment
    def remember_assignment(self, assignment: int):
        self.assignments[-1].append(assignment)
        self.decision_level_per_assigned_literal[assignment] = len(self.assignments)-1
        if abs(assignment) in self.unassigned_variables: 
            self.unassigned_variables.remove(abs(assignment))

    # updates data structures with new assignments
    # allows for input as list or integer
    def remember_assignments(self, assignments):
        if type(assignments) == list:
            for unit_assignment in assignments:
                self.remember_assignments(unit_assignment)
        elif type(assignments) == int:
            self.remember_assignment(assignments)

    # applies assignments and unit propagates formula 
    def propagate(self, formula):
        self.formula, unit_assignments, extra_propagations = unit_propagate(simplify(formula,self.assignments),return_assignments=True,count_propagations=True)
        self.propagation_count += extra_propagations

        if [] in self.formula:
            self.conflict_clause = self.known_clauses[self.formula.index([])]

        self.remember_assignments(unit_assignments)

    # applies restart policy
    def apply_restart_policy(self):
        pass

    # writes proof in DRAT format
    def write_proof(self):
        num_clauses = len(self.learned_clauses) + 1 if not self.sat else len(self.learned_clauses)

        file_name = "proof.drat"
        with open(file_name, "w") as file:
            file.write("p cnf " + str(self.num_literals) + " " + str(num_clauses) + "\n")
            for learned_clause in self.learned_clauses:
                file.write(" ".join(map(str,learned_clause)) + " 0\n")
            if not self.sat:
                file.write("0\n")