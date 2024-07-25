from unit_propagate import unit_propagate, simplify
from formula_preprocessing import pure_literal_elimination, get_unique_literals_in_formula
import random
import copy
import gc
import time

class dpll:
    def __init__(self, use_pure_literal_elimination=True) -> None:
        self.use_pure_literal_elimination = use_pure_literal_elimination

    def solve(self, formula):
        # set globals
        self.reset_variables()
        # solve
        time_start = time.time()
        assignments = self.dpll_step(formula, assignments={}, use_pure_literal_elimination=self.use_pure_literal_elimination)
        time_end = time.time()
        # return
        if self.sat == "SAT":
            return self.sat, assignments, time_end-time_start, self.propagation_count, self.pure_literal_elimination_count, self.decision_count
        else:
            return self.sat, time_end-time_start, self.propagation_count, self.pure_literal_elimination_count, self.decision_count
        
    def reset_variables(self):
        self.propagation_count = 0
        self.pure_literal_elimination_count = 0
        self.decision_count = 0
        self.sat = "UNSAT"

    def dpll_step(self, formula, assignments, use_pure_literal_elimination=True):
        # get formula with current assignments
        simplified_formula = simplify(copy.deepcopy(formula), assignments)
        # resolve formula using unit propagation and pure literal elimination
        while True:
            old_len = len(simplified_formula)

            simplified_formula, unit_assignments, extra_propagations = unit_propagate(simplified_formula, count_propagations=True)
            self.propagation_count += extra_propagations
            assignments.update(unit_assignments)

            if use_pure_literal_elimination:
                simplified_formula, pure_literal_assignments, extra_eliminations = pure_literal_elimination(simplified_formula, count_eliminations=True, return_assignments=True)
                self.pure_literal_elimination_count += extra_eliminations
                assignments.update(pure_literal_assignments)

            if old_len == len(simplified_formula) or [] in simplified_formula or len(simplified_formula) == 0:
                break
        
        # check if we're done
        if len(simplified_formula) == 0:
            self.sat = "SAT"
            return assignments
        if [] in simplified_formula:
            return assignments

        # choose random variable to assign
        decision_variable = self.get_decision_variable(assignments, simplified_formula)

        # free memory
        del simplified_formula
        gc.collect()

        # test with assigned variable
        assignments[decision_variable] = True
        self.decision_count += 1
        assignments_for_return = self.dpll_step(formula, copy.deepcopy(assignments), use_pure_literal_elimination)
        if self.sat != "SAT":
            assignments[decision_variable] = False
            self.decision_count += 1
            assignments_for_return = self.dpll_step(formula, copy.deepcopy(assignments), use_pure_literal_elimination)
        return assignments_for_return

    def get_decision_variable(self, assignments, simplified_formula):
        literals = get_unique_literals_in_formula(simplified_formula)
        possible_variables = [literal for literal in literals if literal not in assignments and -literal not in assignments]
        return random.sample(possible_variables, 1)[0]




# def dpll(formula, use_pure_literal_elimination=True):
#     # set globals
#     dpll_init()
#     # solve
#     time_start = time.time()
#     assignments = dpll_step(formula, assignments={}, use_pure_literal_elimination=use_pure_literal_elimination)
#     time_end = time.time()
#     # return
#     if sat == "SAT":
#         return sat, assignments, time_end-time_start, propagation_count, pure_literal_elimination_count, decision_count
#     else:
#         return sat, time_end-time_start, propagation_count, pure_literal_elimination_count, decision_count
    

# # does the actual dpll algorithm
# def dpll_step(formula, assignments, use_pure_literal_elimination=True):

#     # get formula with current assignments
#     simplified_formula = simplify(copy.deepcopy(formula), assignments)
#     global propagation_count
#     global pure_literal_elimination_count
#     global decision_count
#     global sat

#     # resolve formula using unit propagation and pure literal elimination
#     while True:
#         old_len = len(simplified_formula)

#         simplified_formula, unit_assignments, extra_propagations = unit_propagate(simplified_formula, count_propagations=True)
#         propagation_count += extra_propagations
#         assignments.update(unit_assignments)

#         if use_pure_literal_elimination:
#             simplified_formula, pure_literal_assignments, extra_eliminations = pure_literal_elimination(simplified_formula, count_eliminations=True, return_assignments=True)
#             pure_literal_elimination_count += extra_eliminations
#             assignments.update(pure_literal_assignments)

#         if old_len == len(simplified_formula) or [] in simplified_formula or len(simplified_formula) == 0:
#             break
    
#     # check if we're done
#     if len(simplified_formula) == 0:
#         sat = "SAT"
#         return assignments
#     if [] in simplified_formula:
#         return assignments

#     # choose random variable to assign
#     decision_variable = get_decision_variable(assignments, simplified_formula)

#     # free memory
#     del simplified_formula
#     gc.collect()

#     # test with assigned variable
#     assignments[decision_variable] = True
#     decision_count += 1
#     assignments_for_return = dpll_step(formula, copy.deepcopy(assignments), use_pure_literal_elimination)
#     if sat != "SAT":
#         assignments[decision_variable] = False
#         decision_count += 1
#         assignments_for_return = dpll_step(formula, copy.deepcopy(assignments), use_pure_literal_elimination)
#     return assignments_for_return
    

# def get_decision_variable(assignments, simplified_formula):
#     literals = get_unique_literals_in_formula(simplified_formula)
#     possible_variables = [literal for literal in literals if literal not in assignments and -literal not in assignments]
#     return random.sample(possible_variables, 1)[0]
    

# def dpll_init():
#     global propagation_count 
#     propagation_count = 0
#     global pure_literal_elimination_count
#     pure_literal_elimination_count = 0
#     global decision_count
#     decision_count = 0
#     global sat 
#     sat = "UNSAT"
