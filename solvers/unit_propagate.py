import copy

def unit_propagate(formula, return_assignments=False, count_propagations=False, return_unit_clause_indices_and_respective_units=False):
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
            if not (-literal in assignments or literal in assignments):
                unit_clause_indices_and_respective_units.append([index, literal])
                assignments.append(literal)
                num_propagations += 1
                formula = simplify(formula, [literal], placeholders_for_fulfilled_clauses=return_unit_clause_indices_and_respective_units)
                if [] in formula:
                    break

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
def simplify(formula, assignments, placeholders_for_fulfilled_clauses=False):
    assignments = validated_assignments(assignments)
    
    clauses_to_remove = []
    for literal in assignments:
        for i, clause in enumerate(formula):
            if type(clause) == str:
                continue
            if literal in clause:
                clauses_to_remove.append(i)
            elif -literal in clause:
                clause.remove(-literal)
                
    if placeholders_for_fulfilled_clauses:
        formula = [clause if i not in clauses_to_remove else "True" for i, clause in enumerate(formula)]
    else:
        formula = [clause for i, clause in enumerate(formula) if i not in clauses_to_remove]
    return formula

# if assignments is a list of lists, it will be flattened
def validated_assignments(assignments):
    if len(assignments) != 0:
        if type(assignments[0]) == list:
            return sum(assignments, [])
    return assignments

