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

        # init data structures
        self.decision_level = 0
        self.assignments = [[]]
        self.implications = []
        self.unassigned_variables = get_unique_literals_in_formula(self.known_clauses, only_positive=True)
        self.num_literals = len(self.unassigned_variables)
        self.learned_clauses = []
        self.decision_level_per_literal = {}


    def solve(self, formula):
        time_start = time.time()
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
            while [] in self.formula:
                self.conflict_count += 1
                # if conflict occurs at the root level -> unsat
                if self.decision_level == 0:
                    self.write_proof(sat=False)
                    runtime = time.time()-time_start
                    return "UNSAT", runtime, self.propagation_count, self.decision_count, self.conflict_count
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
        runtime = time.time()-time_start
        flattened_assignments = sum(self.assignments,[])
        return "SAT", flattened_assignments, runtime, self.propagation_count, self.decision_count, self.conflict_count

    def get_decision_variable(self):
        decision_variable = random.sample(self.unassigned_variables,1)[0]
        return decision_variable if random.choice([True,False]) else -decision_variable

    def decide(self):
        self.decision_count += 1
        decision_variable = self.get_decision_variable()
        self.unassigned_variables.remove(abs(decision_variable))
        self.assignments[-1].append(decision_variable)
        self.decision_level_per_literal[decision_variable] = len(self.assignments)-1
        return decision_variable

    def analyze_conflict(self):
        learned_clause = [-decision_level_assignments[0] for decision_level_assignments in self.assignments[1:]]
        self.learned_clauses.append(learned_clause)
        self.known_clauses.append(learned_clause)
        return self.decision_level-1

    def backtrack(self, new_decision_level):
        for literal, decision_level in list(self.decision_level_per_literal.items()):
            if decision_level > new_decision_level:
                del self.decision_level_per_literal[literal]
        for _ in range(self.decision_level-new_decision_level):
            decision_level_assignments = self.assignments.pop()
            for literal in decision_level_assignments:
                self.unassigned_variables.append(abs(literal))
        self.decision_level = new_decision_level

    def remember_unit_assignments(self, unit_assignments):
        self.assignments[-1] = self.assignments[-1] + unit_assignments
        for unit_assignment in unit_assignments:
            self.decision_level_per_literal[unit_assignment] = len(self.assignments)-1
            try: self.unassigned_variables.remove(abs(unit_assignment))
            except: pass

    def propagate(self, formula):
        self.formula, unit_assignments, extra_propagations = unit_propagate(simplify(formula,self.assignments),return_assignments=True,count_propagations=True)
        self.propagation_count += extra_propagations

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