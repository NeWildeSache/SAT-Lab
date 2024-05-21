from itertools import combinations

def remove_tautologies(formula):
    if len(formula) == 0:
        return formula
    
    tautological_clauses = []
    for clause in formula:
        for literal in clause:
            if -literal in clause:
                tautological_clauses.append(clause)
    return [clause for clause in formula if clause not in tautological_clauses]

def remove_doubles(formula):
    formula = set(map(frozenset, formula))
    formula = list(map(list,formula))
    return formula

def pure_literal_elimination(formula, count_eliminations=False, return_assignments=False):
    # check if formula is empty -> return
    if len(formula) == 0:
        if count_eliminations:
            if return_assignments:
                return formula, {}, 0
            return formula, 0
        else:
            if return_assignments:
                return formula, {}
            return formula

    # eliminate pure literals
    literals = get_unique_literals_in_formula(formula)
    pure_literals = []
    for literal in literals:
        if literal in literals and -literal not in literals:
            pure_literals.append(literal)
    eliminated_formula = [clause for clause in formula if not any(literal in pure_literals for literal in clause)]

    # return what's needed
    if return_assignments:
        assignments = {abs(literal): True if literal > 0 else False for literal in pure_literals}
        if count_eliminations:
            return eliminated_formula, assignments, len(formula)-len(eliminated_formula)
        return eliminated_formula, assignments
    else:
        if count_eliminations:
            return eliminated_formula, len(formula)-len(eliminated_formula)
        return eliminated_formula
    
def get_unique_literals_in_formula(formula, only_positive=False):
    flattened_formula = sum(formula, [])
    # return literals only in positive form
    if only_positive: 
        flattened_formula = map(abs, flattened_formula)
        return list(set(flattened_formula))
    # differentiate between positive and negative literals
    else:
        return list(set(flattened_formula))

def subsumption(formula, count_subsumptions=False):
    if len(formula) == 0:
        if count_subsumptions:
            return formula, 0
        else:
            return formula

    formula = remove_doubles(formula)
    unnecessary_clauses = []
    for clause, second_clause in combinations(formula, 2):
        if set(clause).issubset(set(second_clause)):
            unnecessary_clauses.append(second_clause)
            continue
        if set(second_clause).issubset(set(clause)):
            unnecessary_clauses.append(clause)

    formula = [clause for clause in formula if clause not in unnecessary_clauses]
    if count_subsumptions:
        count = len(unnecessary_clauses)
        return formula, count
    else:
        return formula


if __name__ == "__main__":
    formula = [[1,2,3],[-2,-3],[-3,-2],[2,3]]
    print(remove_doubles(formula))
    print(pure_literal_elimination(formula))
    print(subsumption(formula))

    formula = [[-2,-3],[-2,-3]]
    print(subsumption(formula))

    print(pure_literal_elimination([[],[],[]]))
