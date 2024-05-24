import copy

def unit_propagate(formula, count_propagations=False, return_assignments=True):
    # preprocess
    assignments = []
    num_propagations = 0
    while True:
        # figure out unit clauses
        unit_clauses = [c for c in formula if len(c) == 1]
        # remember information for stopping 
        old_len = len(formula)
        # derive assignments
        for unit in unit_clauses:
            literal = unit[0]
            if not (-literal in assignments or literal in assignments):
                assignments.append(literal)
        # simplify formula with given assignments
        formula = simplify(formula, assignments)
        # count propagations
        num_propagations += 1
        # stop if nothing happens or unsat
        if old_len == len(formula) or [] in formula:
            break
    # return what's needed
    if count_propagations:
        if return_assignments:
            return formula, assignments, num_propagations
        return formula, num_propagations
    else:
        if return_assignments:
            return formula, assignments
        return formula

# simplifies a formula given an assignment
# also works if only one assignment was given (e.g. x=0 is explicitly stated but !x=1 isn't)
def simplify(formula, assignments):
    if len(assignments) != 0:
        if type(assignments[0]) == list:
            assignments = sum(assignments, [])
    
    clauses_to_remove = []
    for i, clause in enumerate(formula):
        clause_copy = copy.deepcopy(clause)
        for literal in clause_copy:
            if literal in assignments:
                clauses_to_remove.append(i)
                continue
            elif -literal in assignments:
                clause.remove(literal)
                
    formula = [clause for i, clause in enumerate(formula) if i not in clauses_to_remove]
    return formula


# TESTING
if __name__ == "__main__":
    unsat_formula = [[1],[-1],[3,4]]
    print(unsat_formula)
    unsat_formula, assignments = unit_propagate(unsat_formula)
    print(unsat_formula)

    sat_formula = [[1],[-1,2]]
    print(sat_formula)
    sat_formula, assignments = unit_propagate(sat_formula)
    print(sat_formula)

    formula_with_remains = [[1],[-1,2],[3,4]]
    print(formula_with_remains)
    formula_with_remains, assignments = unit_propagate(formula_with_remains)
    print(formula_with_remains)

    formula_to_test_simplify = [[1,2,3],[-2,-3],[-3,-2],[2,3]]
    print(simplify(formula_to_test_simplify, [-1,-2,-3]))

