from cnf_reader import read_cnf
from unit_propagate import unit_propagate
from unit_propagate import simplify
import copy

def solve_2_sat(formula):
    # do initial unit propagation
    formula, assignments, num_propagations = unit_propagate(copy.deepcopy(formula), count_propagations=True)
    num_decisions = 0

    while len(formula) > 0 and not [] in formula:
        # take arbitrary variable
        variable = abs(formula[0][0])
        # set variable to False
        new_assignments = {variable: False}
        new_formula, unit_assignments, extra_propagations = unit_propagate(simplify(copy.deepcopy(formula), new_assignments), count_propagations=True)
        new_assignments.update(unit_assignments)

        num_decisions = num_decisions + 1
        num_propagations = num_propagations + extra_propagations

        if [] in new_formula:
            # try True instead
            new_assignments = {variable: True}
            new_formula, unit_assignments, extra_propagations = unit_propagate(simplify(copy.deepcopy(formula), new_assignments), count_propagations=True)
            new_assignments.update(unit_assignments)

            num_decisions = num_decisions + 1
            num_propagations = num_propagations + extra_propagations

        # use simplified formula with new assignments
        assignments.update(new_assignments)
        formula = new_formula

    if [] in formula:
        sat = "UNSAT"
    else:
        sat = "SAT"

    return sat, assignments, num_decisions, num_propagations

if __name__ == "__main__":
    formula = read_cnf()
    # formula = [[2, 3], [-2, -3], [2, -3], [1, 2], [-1, -2]]
    print(f"input formula: {formula}")

    sat, assignments, num_decisions, num_propagations = solve_2_sat(formula)
    print(f"s {sat}")
    if sat == "SAT":
        print(f"v {str(assignments)}")
    print(f"c {num_decisions}")
    print(f"c {num_propagations}")

