from random_cnf import random_cnf

def get_solver_results(n,c,k,solver,solver_args={},num_tests=50):
    results = []
    for _ in range(num_tests):
        formula = random_cnf(n,c,k)
        outputs = solver(formula=formula,**solver_args)
        results.append(outputs)
    return results