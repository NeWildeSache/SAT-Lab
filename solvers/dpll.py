from solvers.unit_propagate import unit_propagate, simplify
from solvers.utils import pure_literal_elimination, get_unique_literals_in_formula
import random
import copy
import gc
import time

class dpll:
    def __init__(self, use_pure_literal_elimination=True) -> None:
        self.use_pure_literal_elimination = use_pure_literal_elimination

    def solve(self, formula):
        # set globals
        self.reset_variables(formula)
        # solve and track time
        time_start = time.time()
        assignments = self.dpll_step(assignments=[])
        time_spent = time.time() - time_start
        # return
        return_dict = {"SAT": self.sat, "runtime": time_spent, "propagation_count": self.propagation_count, "pure_literal_elimination_count": self.pure_literal_elimination_count, "decision_count": self.decision_count}
        if self.sat: return_dict["model"] = assignments
        return return_dict
        
    def reset_variables(self, formula):
        self.formula = formula
        self.literals = get_unique_literals_in_formula(self.formula, only_positive=True)
        self.propagation_count = 0
        self.pure_literal_elimination_count = 0
        self.decision_count = 0
        self.sat = False

    def dpll_step(self, assignments):
        # get formula with current assignments
        simplified_formula = simplify(copy.deepcopy(self.formula), assignments)
        # resolve formula using unit propagation and pure literal elimination
        while True:
            old_len = len(simplified_formula)

            simplified_formula, unit_assignments, extra_propagations = unit_propagate(simplified_formula, count_propagations=True, return_assignments=True)
            self.propagation_count += extra_propagations
            assignments.extend(unit_assignments)

            if self.use_pure_literal_elimination:
                simplified_formula, pure_literal_assignments, extra_eliminations = pure_literal_elimination(simplified_formula, count_eliminations=True, return_assignments=True)
                self.pure_literal_elimination_count += extra_eliminations
                assignments.extend(pure_literal_assignments)

            if old_len == len(simplified_formula) or [] in simplified_formula or len(simplified_formula) == 0:
                break
        
        # check if we're done
        if len(simplified_formula) == 0:
            self.sat = True
            return assignments
        if [] in simplified_formula:
            return assignments

        # choose random variable to assign
        decision_variable = self.get_decision_variable(assignments)

        # free memory
        del simplified_formula
        gc.collect()

        # test with assigned variable -> first test with False, then with True
        assignments.append(-decision_variable)
        self.decision_count += 1
        assignments_for_return = self.dpll_step(copy.deepcopy(assignments))
        if self.sat != True:
            assignments[-1] = decision_variable
            self.decision_count += 1
            assignments_for_return = self.dpll_step(copy.deepcopy(assignments))
        return assignments_for_return

    def get_decision_variable(self, assignments):
        possible_variables = [literal for literal in self.literals if literal not in assignments and -literal not in assignments]
        return random.sample(possible_variables, 1)[0]
