from unit_propagate_using_lists import unit_propagate, simplify
from formula_preprocessing import get_unique_literals_in_formula
import copy
import random
import time

class cdcl:
    def __init__(self) -> None:
        pass

    def reset_variables(self, formula):
        self.formula = copy.deepcopy(formula)
        self.known_clauses = copy.deepcopy(formula)
        self.propagation_count = 0
        self.decision_count = 0
        self.conflict_count = 0
        self.learned_clause_count = 0

        # init data structures
        self.decision_level = 0
        self.assignments = [[]]
        self.implications = []
        self.unassigned_variables = get_unique_literals_in_formula(self.known_clauses, only_positive=True)
        self.num_literals = len(self.unassigned_variables)
        self.learned_clauses = []
        self.decision_level_per_assigned_literal = {}
        self.conflict_clause = None


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
                    self.write_proof(sat=False)
                    return self.return_statement(sat=False)
                # learn clause and figure out backtracking level
                new_decision_level = self.analyze_conflict()
                # backtrack
                self.backtrack(new_decision_level)
                # unit propagate
                self.propagate(copy.deepcopy(self.known_clauses))

            # restart occasionally
            self.apply_restart_policy()

        # return sat
        self.write_proof(sat=True)
        return self.return_statement(sat=True)
    
    def get_statistics(self):
        runtime = time.time()-self.time_start
        return [runtime, self.propagation_count, self.decision_count, self.conflict_count, self.learned_clause_count]

    def return_statement(self, sat):
        return_statement = []
        if sat:
            return_statement.append("SAT")
            return_statement.append(sum(self.assignments,[]))
        else:
            return_statement.append("UNSAT")
        return return_statement + self.get_statistics()
            
    def get_decision_variable(self):
        decision_variable = random.sample(self.unassigned_variables,1)[0]
        return decision_variable if random.choice([True,False]) else -decision_variable

    def decide(self):
        self.decision_count += 1
        decision_variable = self.get_decision_variable()
        self.unassigned_variables.remove(abs(decision_variable))
        self.assignments[-1].append(decision_variable)
        self.decision_level_per_assigned_literal[decision_variable] = len(self.assignments)-1
        return decision_variable
    
    def remember_learned_clause(self,learned_clause):
        self.learned_clauses.append(learned_clause)
        self.known_clauses.append(learned_clause)
        self.learned_clause_count += 1

    def analyze_conflict(self):
        learned_clause = [-decision_level_assignments[0] for decision_level_assignments in self.assignments[1:]]
        self.remember_learned_clause(learned_clause)
        return self.decision_level-1

    def backtrack(self, new_decision_level):
        for literal, decision_level in list(self.decision_level_per_assigned_literal.items()):
            if decision_level > new_decision_level:
                del self.decision_level_per_assigned_literal[literal]
        for _ in range(self.decision_level-new_decision_level):
            decision_level_assignments = self.assignments.pop()
            for literal in decision_level_assignments:
                self.unassigned_variables.append(abs(literal))
        self.decision_level = new_decision_level
        self.conflict_clause = None

    def remember_unit_assignments(self, unit_assignments):
        if type(unit_assignments) == int:
            self.assignments[-1].append(unit_assignments)
            self.decision_level_per_assigned_literal[unit_assignments] = len(self.assignments)-1
            try: self.unassigned_variables.remove(abs(unit_assignments))
            except: pass
        elif type(unit_assignments) == list:
            self.assignments[-1] = self.assignments[-1] + unit_assignments
            for unit_assignment in unit_assignments:
                self.decision_level_per_assigned_literal[unit_assignment] = len(self.assignments)-1
                try: self.unassigned_variables.remove(abs(unit_assignment))
                except: pass

    def propagate(self, formula):
        self.formula, unit_assignments, extra_propagations = unit_propagate(simplify(formula,self.assignments),return_assignments=True,count_propagations=True)
        self.propagation_count += extra_propagations

        if [] in self.formula:
            self.conflict_clause = self.known_clauses[self.formula.index([])]

        self.remember_unit_assignments(unit_assignments)


    def apply_restart_policy(self):
        pass


    # writes proof in DRAT format
    def write_proof(self, sat):
        num_clauses = len(self.learned_clauses) + 1 if not sat else len(self.learned_clauses)

        file_name = "proof.drat"
        with open(file_name, "w") as file:
            file.write("p cnf " + str(self.num_literals) + " " + str(num_clauses) + "\n")
            for learned_clause in self.learned_clauses:
                file.write(" ".join(map(str,learned_clause)) + " 0\n")
            if not sat:
                file.write("0\n")