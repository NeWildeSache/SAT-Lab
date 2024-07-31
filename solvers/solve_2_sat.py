from .unit_propagate import unit_propagate, simplify
from .utils import read_dimacs
import copy
import time
import argparse

def solve_2_sat(formula):
    time_start = time.time()
    # do initial unit propagation
    formula, assignments, propagation_count = unit_propagate(copy.deepcopy(formula), return_assignments=True, count_propagations=True)
    num_decisions = 0

    while len(formula) > 0 and not [] in formula:
        # take arbitrary decision variable
        decision_variable = abs(formula[0][0])
        # set variable to False
        new_assignments = [-decision_variable]
        new_formula, unit_assignments, extra_propagations = unit_propagate(simplify(copy.deepcopy(formula), new_assignments), return_assignments=True, count_propagations=True)
        new_assignments.extend(unit_assignments)
        # update statistics
        num_decisions = num_decisions + 1
        propagation_count = propagation_count + extra_propagations

        if [] in new_formula:
            # try True instead
            new_assignments = [decision_variable]
            new_formula, unit_assignments, extra_propagations = unit_propagate(simplify(copy.deepcopy(formula), new_assignments), return_assignments=True, count_propagations=True)
            new_assignments.extend(unit_assignments)
            # update statistics
            num_decisions = num_decisions + 1
            propagation_count = propagation_count + extra_propagations

        # use simplified formula with new assignments
        assignments.extend(new_assignments)
        formula = new_formula

    if [] in formula:
        sat = False
    else:
        sat = True

    time_spent = time.time() - time_start
    return_dict = {"SAT": sat, "runtime": time_spent, "num_decisions": num_decisions, "propagation_count": propagation_count}
    if sat: return_dict["model"] = assignments
    return return_dict

# run this from parent folder using "python -m solvers.solve_2_sat <path>"
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2-SAT Solver")
    parser.add_argument("path", nargs="?", default="random_cnf.cnf")
    args=parser.parse_args()
    path = args.path
    formula = read_dimacs(path)
    stats = solve_2_sat(formula)
    print("s", "SATISFIABLE" if stats["SAT"] else "UNSATISFIABLE")
    if stats["SAT"]:
        print("v", " ".join([str(l) for l in stats["model"]]))
    print("c", "Runtime:", stats["runtime"])
    print("c", "Number of Decisions:", stats["num_decisions"])
    print("c", "Number of Propagations:", stats["propagation_count"])
    