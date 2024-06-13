import copy

def unit_propagate(formula, count_propagations=False, return_assignments=False, return_unit_clause_indices_and_respective_units=False):
    # preprocess
    assignments = []
    num_propagations = 0
    unit_clause_indices_and_respective_units = []
    while True:
        # figure out unit clauses
        unit_clauses = [[c, i] for i, c in enumerate(formula) if len(c) == 1]
        # remember information for stopping 
        old_formula = copy.deepcopy(formula)
        # derive assignments
        for unit, index in unit_clauses:
            literal = unit[0]
            unit_clause_indices_and_respective_units.append([index, literal])
            if not (-literal in assignments or literal in assignments):
                assignments.append(literal)
        # simplify formula with given assignments
        formula = simplify(formula, assignments)
        # count propagations
        num_propagations += 1
        # stop if nothing happens or unsat
        if old_formula == formula or [] in formula:
            break
    # return what's needed
    if not return_assignments and not count_propagations and not return_unit_clause_indices_and_respective_units:
        return formula
    return_statement = [formula]
    if return_assignments:
        return_statement.append(assignments)
    if count_propagations:
        return_statement.append(num_propagations)
    if return_unit_clause_indices_and_respective_units:
        return_statement.append(unit_clause_indices_and_respective_units)
    return return_statement

# simplifies a formula given an assignment
# also works if only one assignment was given (e.g. x=0 is explicitly stated but !x=1 isn't)
def simplify(formula, assignments):
    if len(assignments) != 0:
        if type(assignments[0]) == list:
            assignments = sum(assignments, [])
    
    clauses_to_remove = []
    for literal in assignments:
        for i, clause in enumerate(formula):
            if type(clause) == str:
                continue
            if literal in clause:
                clauses_to_remove.append(i)
            elif -literal in clause:
                clause.remove(-literal)
                
    formula = [clause if i not in clauses_to_remove else "True" for i, clause in enumerate(formula)]
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

