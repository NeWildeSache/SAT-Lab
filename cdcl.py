from unit_propagate import unit_propagate, simplify
from formula_preprocessing import get_unique_literals_in_formula
import copy
import random
from collections import OrderedDict
import time


def decide(assignments, literals):
    global decision_count
    decision_count += 1
    decision_variable = random.sample(literals,1)[0]
    assignments[decision_variable] = random.choice([True,False])
    literals.remove(decision_variable)

def analyze_conflict(assignments, decision_level):
    learned_clause = [-literal if assignments[literal] else literal for literal in assignments]
    return learned_clause, decision_level-1

def backtrack(decision_level, new_decision_level, assignments, literals):
    for _ in range(decision_level-new_decision_level):
        literal = assignments.popitem()[0]
        literals.append(literal)
    return new_decision_level

def propagate(formula, assignments):
    global propagation_count
    simplified_formula, extra_propagations = unit_propagate(simplify(copy.deepcopy(formula),assignments),return_assignments=False,count_propagations=True)
    propagation_count += extra_propagations
    return simplified_formula

def apply_restart_policy():
    pass

# writes proof in DRAT format
def write_proof(learned_clauses, sat, formula):
    num_literals = len(get_unique_literals_in_formula(formula, only_positive=True))
    num_clauses = len(learned_clauses) + 1 if not sat else len(learned_clauses)

    file_name = "proof.drat"
    with open(file_name, "w") as file:
        file.write("p cnf " + str(num_literals) + " " + str(num_clauses) + "\n")
        for learned_clause in learned_clauses:
            file.write(" ".join(map(str,learned_clause)) + " 0\n")
        if not sat:
            file.write("0\n")


def cdcl(formula):
    # init statistics
    time_start = time.time()
    global propagation_count
    propagation_count = 0
    global decision_count
    decision_count = 0
    conflict_count = 0

    # init data structures
    decision_level = 0
    assignments = OrderedDict()
    literals = get_unique_literals_in_formula(formula, only_positive=True)
    learned_clauses = []

    # actual algorithm
    while len(literals) > 0:
        decision_level += 1
        # assign truth value to a literal
        decide(assignments,literals)
        # unit propagate
        simplified_formula = propagate(formula, assignments)

        # if conflict occurs
        while [] in simplified_formula:
            conflict_count += 1
            # if conflict occurs at the root level -> unsat
            if decision_level == 0:
                write_proof(learned_clauses, sat=False, formula=formula)
                runtime = time.time()-time_start
                return "UNSAT", runtime, propagation_count, decision_count, conflict_count
            # learn clause and figure out backtracking level
            learned_clause, new_decision_level = analyze_conflict(assignments, decision_level)
            learned_clauses.append(learned_clause)
            formula.append(learned_clause)
            # backtrack
            decision_level = backtrack(decision_level, new_decision_level, assignments, literals)
            # unit propagate
            simplified_formula = propagate(formula, assignments)

        # restart occasionally
        apply_restart_policy()

    # return sat
    write_proof(learned_clauses, sat=True, formula=formula)
    runtime = time.time()-time_start
    return "SAT", assignments, runtime, propagation_count, decision_count, conflict_count


if __name__ == "__main__":
    formula = [[1,2,3],[-2,-3],[-3,-2],[2,3]]
    print(cdcl(formula))