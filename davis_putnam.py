from unit_propagate import unit_propagate
from formula_preprocessing import remove_doubles, remove_tautologies, subsumption, pure_literal_elimination

def davis_putnam(formula):
    while True:
        propagation_count = 0
        elimination_count = 0
        subsumption_count = 0
        added_clause_count = 0

        # Preprocessing
        while True:
            len_before = len(formula)
            formula, _, extra_propagations = unit_propagate(formula, True)
            propagation_count += extra_propagations

            if [] in formula:
                return "UNSAT", propagation_count, added_clause_count, elimination_count, subsumption_count

            formula = remove_doubles(remove_tautologies(formula))
            formula, extra_eliminations = pure_literal_elimination(formula, True)
            formula, extra_subsumptions = subsumption(formula, True)
            elimination_count += extra_eliminations
            subsumption_count += extra_subsumptions

            if len(formula) == len_before:
                break
        if len(formula) == 0:
            return "SAT", propagation_count, added_clause_count, elimination_count, subsumption_count
        
        # choose arbitrary variable
        variable = formula[0][0]
        # find clauses containing variable and -variable
        clauses_containing_variable = []
        clauses_containing_complement = []
        for clause in formula:
            if variable in clause:
                clauses_containing_variable.append(clause)
            if -variable in clause:
                clauses_containing_complement.append(clause)
        
        # remove clauses with variable
        formula = [clause for clause in formula if clause not in clauses_containing_complement or clause in clauses_containing_variable]

        # create resolved clauses 
        resolved_clauses = []
        for variable_clause in clauses_containing_variable:
            for complement_clause in clauses_containing_complement:
                a = [x for x in variable_clause if x != variable]
                b = [x for x in complement_clause if x != -variable]
                resolved_clauses.append(a+b)
        
        # add resolved clauses
        formula = formula + resolved_clauses
        added_clause_count = added_clause_count + len(resolved_clauses)

if __name__ == "__main__":
    formula = [[1], [-1]]
    print(davis_putnam(formula))