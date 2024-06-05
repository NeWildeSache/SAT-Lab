from unit_propagate_using_lists import unit_propagate, simplify
from formula_preprocessing import get_unique_literals_in_formula
from cdcl_5 import apply_restart_policy
from write_proof import write_proof
import copy
import random
import time


def decide(assignments, literals):
    global decision_count
    decision_count += 1
    decision_variable = random.sample(literals,1)[0]
    literals.remove(decision_variable)
    decision_variable = decision_variable if random.choice([True,False]) else -decision_variable
    assignments[-1].append(decision_variable)

def analyze_conflict(assignments, decision_level):
    learned_clause = [-decision_level_assignments[0] for decision_level_assignments in assignments[1:]]
    return learned_clause, decision_level-1

def backtrack(decision_level, new_decision_level, assignments, literals):
    for _ in range(decision_level-new_decision_level):
        decision_level_assignments = assignments.pop()
        for literal in decision_level_assignments:
            literals.append(abs(literal))
    return new_decision_level

def propagate(formula, assignments, literals, original_formula):
    global propagation_count
    simplified_formula, unit_assignments, extra_propagations, unit_clause_indices = unit_propagate(simplify(formula,assignments),return_assignments=True,count_propagations=True,return_unit_clause_indices=True)
    propagation_count += extra_propagations

    for unit_clause_index, unit_assignment in zip(unit_clause_indices, unit_assignments):
        clause_that_became_unit = original_formula[unit_clause_index]
        implicating_literals = [literal for literal in clause_that_became_unit if literal != unit_assignment]

    # remember unit assignments
    assignments[-1] = assignments[-1] + unit_assignments
    for unit_assignment in unit_assignments:
        literals.remove(abs(unit_assignment))

    return simplified_formula


def cdcl(formula):
    # init statistics
    time_start = time.time()
    original_formula = copy.deepcopy(formula)
    formula = copy.deepcopy(formula) # makes sure that input formula isn't changed outside of the algorithm
    global propagation_count
    propagation_count = 0
    global decision_count
    decision_count = 0
    conflict_count = 0

    # init data structures
    decision_level = 0
    assignments = [[]]
    literals = get_unique_literals_in_formula(original_formula, only_positive=True)
    num_literals = len(literals)
    learned_clauses = []

    # actual algorithm
    while len(literals) > 0:
        decision_level += 1
        assignments.append([])
        # assign truth value to a literal
        decide(assignments,literals)
        # unit propagate
        formula = propagate(formula, assignments, literals, original_formula)

        # if conflict occurs
        while [] in formula:
            conflict_count += 1
            # if conflict occurs at the root level -> unsat
            if decision_level == 0:
                write_proof(learned_clauses, sat=False, num_literals=num_literals)
                runtime = time.time()-time_start
                return "UNSAT", runtime, propagation_count, decision_count, conflict_count
            # learn clause and figure out backtracking level
            learned_clause, new_decision_level = analyze_conflict(assignments, decision_level)
            learned_clauses.append(learned_clause)
            original_formula.append(learned_clause)
            # backtrack
            decision_level = backtrack(decision_level, new_decision_level, assignments, literals)
            # unit propagate
            formula = propagate(copy.deepcopy(original_formula), assignments, literals, original_formula)

        # restart occasionally
        apply_restart_policy()

    # return sat
    write_proof(learned_clauses, sat=True, num_literals=num_literals)
    runtime = time.time()-time_start
    flattened_assignments = sum(assignments,[])
    return "SAT", flattened_assignments, runtime, propagation_count, decision_count, conflict_count


if __name__ == "__main__":
    formula = [[-1, -2, 3], [1, -2, 3], [-1, 2, 3], [1, -2, -3]]
    print(cdcl(formula))