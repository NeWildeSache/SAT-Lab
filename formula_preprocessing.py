from itertools import combinations

# returns formula without tautological clauses
def remove_tautologies(formula):
    if len(formula) == 0:
        return formula
    
    tautological_clauses = []
    for clause in formula:
        for literal in clause:
            if -literal in clause:
                tautological_clauses.append(clause)
    return [clause for clause in formula if clause not in tautological_clauses]

# returns formula without doubles
def remove_doubles(formula):
    formula = set(map(frozenset, formula))
    formula = list(map(list,formula))
    return formula

# returns formula without pure literals
def pure_literal_elimination(formula, count_eliminations=False, return_assignments=False):
    pure_literals = []
    original_length = len(formula)

    if len(formula) != 0:
        literals = get_unique_literals_in_formula(formula)
        for literal in literals:
            if literal in literals and -literal not in literals:
                pure_literals.append(literal)
        formula = [clause for clause in formula if not any(literal in pure_literals for literal in clause)]
    else:
        formula = formula

    # return what's needed
    if not return_assignments and not count_eliminations:
        return formula
    return_statement = [formula]
    if return_assignments:
        return_statement.append(pure_literals)
    if count_eliminations:
        return_statement.append(original_length-len(formula))
    return return_statement
    
# returns unique literals in formula
def get_unique_literals_in_formula(formula, only_positive=False):
    flattened_formula = sum(formula, [])
    # return literals only in positive form
    if only_positive: 
        flattened_formula = map(abs, flattened_formula)
        return list(set(flattened_formula))
    # differentiate between positive and negative literals
    else:
        return list(set(flattened_formula))

# returns formula without subsumed clauses
def subsumption(formula, count_subsumptions=False):
    subsumption_count = 0
        
    if len(formula) != 0:
        unnecessary_clauses = []
        for (clause_index, clause), (second_clause_index, second_clause) in combinations(enumerate(formula), 2):
            if len(clause) < len(second_clause):
                if set(clause).issubset(set(second_clause)):
                    unnecessary_clauses.append(second_clause_index)
                    subsumption_count += 1
            else:
                if set(second_clause).issubset(set(clause)):
                    unnecessary_clauses.append(clause_index)
                    subsumption_count += 1

        formula = [clause for i, clause in enumerate(formula) if i not in unnecessary_clauses]
    
    if count_subsumptions:
        return formula, subsumption_count
    else:
        return formula


if __name__ == "__main__":
    formula = [[1,2,3],[-2,-3],[-3,-2],[2,3],[2,-2]]
    print(f"Original formula: {formula}")
    print(f"Without doubles: {remove_doubles(formula)}")
    print(f"Without tautologies: {remove_tautologies(formula)}")
    print(f"Without pure literals: {pure_literal_elimination(formula)}")
    print(f"Without subsumptions: {subsumption(formula)}")

    formula = [[-2,-3],[-2,-3]]
    assert subsumption(formula) == [[-2,-3]] or subsumption(formula) == [[-3,-2]]

    formula = [[],[],[]]
    assert remove_tautologies(formula) == formula
    assert remove_doubles(formula) == [[]]
    assert pure_literal_elimination(formula) == formula
    assert subsumption(formula) == [[]]

    formula = []
    assert pure_literal_elimination(formula) == formula
    assert remove_doubles(formula) == formula
    assert subsumption(formula) == formula
    assert remove_tautologies(formula) == formula