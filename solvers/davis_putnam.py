from solvers.unit_propagate import unit_propagate
from solvers.utils import remove_doubles, remove_tautologies, subsumption, pure_literal_elimination, read_dimacs
import time
import argparse

def davis_putnam(formula, use_unit_propagation=True, use_pure_literal_elimination=True, use_subsumption=True, use_tautology_elimination=True, use_double_elimination=True):
    time_start = time.time()
    while True:
        propagation_count = 0
        elimination_count = 0
        subsumption_count = 0
        added_clause_count = 0

        # Preprocessing
        while True:
            len_before = len(formula)
            if use_unit_propagation:
                formula, extra_propagations = unit_propagate(formula, count_propagations=True)
                propagation_count += extra_propagations

            if use_tautology_elimination:
                formula = remove_tautologies(formula)
            if use_double_elimination:
                formula = remove_doubles(formula)
            if use_pure_literal_elimination:
                formula, extra_eliminations = pure_literal_elimination(formula, True)
                elimination_count += extra_eliminations
            if use_subsumption:
                formula, extra_subsumptions = subsumption(formula, True)
                subsumption_count += extra_subsumptions

            if len(formula) == len_before:
                break
        
        # check if we're done
        if len(formula) == 0:
            runtime = time.time()-time_start
            return_dict = {"SAT": True, "runtime": runtime ,"propagation_count": propagation_count, "added_clause_count": added_clause_count, "elimination_count": elimination_count, "subsumption_count": subsumption_count}
            return return_dict
        if [] in formula:
            runtime = time.time()-time_start
            return_dict = {"SAT": False, "runtime": runtime, "propagation_count": propagation_count, "added_clause_count": added_clause_count, "elimination_count": elimination_count, "subsumption_count": subsumption_count}
            return return_dict
        
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

# run this from parent folder using "python -m solvers.davis_putnam <path>"
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Davis Putnam SAT Solver")
    parser.add_argument("path", nargs="?", default="random_cnf.cnf")
    args=parser.parse_args()
    path = args.path
    formula = read_dimacs(path)
    stats = davis_putnam(formula)
    print("s", "SATISFIABLE" if stats["SAT"] else "UNSATISFIABLE")
    if stats["SAT"]:
        print("v", " ".join([str(l) for l in stats["model"]]))
    print("c", "Runtime:", stats["runtime"])
    print("c", "Number of Propagations:", stats["propagation_count"])
    print("c", "Number of Added Clauses:", stats["added_clause_count"])
    print("c", "Number of Eliminations:", stats["elimination_count"])
    print("c", "Number of Subsumptions:", stats["subsumption_count"])
