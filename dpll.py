from unit_propagate import unit_propagate, simplify
from formula_preprocessing import pure_literal_elimination, get_unique_literals_in_formula
from get_solver_results import get_solver_results
import random
import copy
import gc
import numpy as np
import time

def dpll(formula, use_pure_literal_elimination=True):
    # set globals
    dpll_init()
    # solve
    time_start = time.time()
    assignments = dpll_step(formula, assignments={}, use_pure_literal_elimination=use_pure_literal_elimination)
    time_end = time.time()
    # return
    if sat == "SAT":
        return sat, assignments, time_end-time_start, propagation_count, pure_literal_elimination_count, decision_count
    else:
        return sat, time_end-time_start, propagation_count, pure_literal_elimination_count, decision_count
    

# does the actual dpll algorithm
def dpll_step(formula, assignments, use_pure_literal_elimination=True):

    # get formula with current assignments
    simplified_formula = simplify(copy.deepcopy(formula), assignments)
    global propagation_count
    global pure_literal_elimination_count
    global decision_count
    global sat

    # resolve formula using unit propagation and pure literal elimination
    while True:
        old_len = len(simplified_formula)

        simplified_formula, unit_assignments, extra_propagations = unit_propagate(simplified_formula, count_propagations=True)
        propagation_count += extra_propagations
        assignments.update(unit_assignments)

        if use_pure_literal_elimination:
            simplified_formula, pure_literal_assignments, extra_eliminations = pure_literal_elimination(simplified_formula, count_eliminations=True, return_assignments=True)
            pure_literal_elimination_count += extra_eliminations
            assignments.update(pure_literal_assignments)

        if old_len == len(simplified_formula) or [] in simplified_formula or len(simplified_formula) == 0:
            break
    
    # check if we're done
    if len(simplified_formula) == 0:
        sat = "SAT"
        return assignments
    if [] in simplified_formula:
        return assignments

    # choose random variable to assign
    decision_variable = get_decision_variable(assignments, simplified_formula)

    # free memory
    del simplified_formula
    gc.collect()

    # test with assigned variable
    assignments[decision_variable] = True
    decision_count += 1
    assignments_for_return = dpll_step(formula, copy.deepcopy(assignments), use_pure_literal_elimination)
    if sat != "SAT":
        assignments[decision_variable] = False
        decision_count += 1
        assignments_for_return = dpll_step(formula, copy.deepcopy(assignments), use_pure_literal_elimination)
    return assignments_for_return
    

def get_decision_variable(assignments, simplified_formula):
    literals = get_unique_literals_in_formula(simplified_formula)
    possible_variables = [literal for literal in literals if literal not in assignments and -literal not in assignments]
    return random.sample(possible_variables, 1)[0]
    

def dpll_init():
    global propagation_count 
    propagation_count = 0
    global pure_literal_elimination_count
    pure_literal_elimination_count = 0
    global decision_count
    decision_count = 0
    global sat 
    sat = "UNSAT"



# TESTING
if __name__ == "__main__":
    args_false={"use_pure_literal_elimination": False}
    args_true={"use_pure_literal_elimination": True}
    results_3_5_2_true = np.array(get_solver_results(3,5,2,dpll,solver_args=args_true))
    results_3_5_2_false = np.array(get_solver_results(3,5,2,dpll,solver_args=args_false))
    results_10_50_3_true = np.array(get_solver_results(10,50,3,dpll,solver_args=args_true))
    results_10_50_3_false = np.array(get_solver_results(10,50,3,dpll,solver_args=args_false))
    results_10_200_3_true = np.array(get_solver_results(10,200,3,dpll,solver_args=args_true))
    results_10_200_3_false = np.array(get_solver_results(10,200,3,dpll,solver_args=args_false))
    results_10_200_4_true = np.array(get_solver_results(10,200,4,dpll,solver_args=args_true))
    results_10_200_4_false = np.array(get_solver_results(10,200,4,dpll,solver_args=args_false))
    results_10_500_4_true = np.array(get_solver_results(10,500,4,dpll,solver_args=args_true))
    results_10_500_4_false = np.array(get_solver_results(10,500,4,dpll,solver_args=args_false))

    print("3,5,2")
    print("Using pure literal elimination")
    print("Average time: ", np.mean(results_3_5_2_true[:,2]))
    print("Not using pure literal elimination")
    print("Average time: ", np.mean(results_3_5_2_false[:,2]))
    print("10,50,3")
    print("Using pure literal elimination")
    print("Average time: ", np.mean(results_10_50_3_true[:,2]))
    print("Not using pure literal elimination")
    print("Average time: ", np.mean(results_10_50_3_false[:,2]))
    print("10,200,3")
    print("Using pure literal elimination")
    print("Average time: ", np.mean(results_10_200_3_true[:,2]))
    print("Not using pure literal elimination")
    print("Average time: ", np.mean(results_10_200_3_false[:,2]))
    print("10,200,4")
    print("Using pure literal elimination")
    print("Average time: ", np.mean(results_10_200_4_true[:,2]))
    print("Not using pure literal elimination")
    print("Average time: ", np.mean(results_10_200_4_false[:,2]))
    print("10,500,4")
    print("Using pure literal elimination")
    print("Average time: ", np.mean(results_10_500_4_true[:,2]))
    print("Not using pure literal elimination")
    print("Average time: ", np.mean(results_10_500_4_false[:,2]))

