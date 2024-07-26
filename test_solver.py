from solve_2_sat import solve_2_sat
from davis_putnam import davis_putnam
from pysat.solvers import Cadical103
from random_cnf import random_cnf
from dpll import dpll
from cdcl import cdcl 
from cdcl_6 import cdcl_clause_learning 
from cdcl_7 import cdcl_watched_literals 
from cdcl_8 import cdcl_decision_heuristics_and_restarts 
from cdcl_9 import cdcl_clause_minimization_and_deletion 
import numpy as np

def test_solver(n,c,k,solver,args={},num_tests=50,print_progress=False):
    times = []
    for _ in range(num_tests):
        # generate random formula
        formula = random_cnf(n,c,k)

        # solve formula
        if isinstance(solver,type): # check if solver is a class
            solver_instance = solver(**args)
            outputs = solver_instance.solve(formula)
        else: 
            outputs = solver(formula)
        solver_sat = outputs["SAT"]
        times.append(outputs["runtime"])
        cadical = Cadical103()
        cadical.append_formula(formula)
        cadical_sat = cadical.solve()

        # print lots of information (good for debugging)
        if print_progress:
            print("-"*10)
            print(f"Using: {solver.__name__}")
            print(f"Formula: {formula}")
            print(f"Solver: {solver_sat}")
            print(f"Cadical: {cadical_sat}")
            if solver_sat: print(f"solver model: {outputs["model"]}")
            if cadical_sat: print(f"cadical model: {cadical.get_model()}")

        assert solver_sat == cadical_sat

    return np.mean(times)


if __name__ == "__main__":
    test_solver(3,5,2,solve_2_sat)
    test_solver(100,100,2,solve_2_sat)

    solvers = [dpll,davis_putnam,cdcl,cdcl_clause_learning,cdcl_watched_literals,cdcl_decision_heuristics_and_restarts,cdcl_clause_minimization_and_deletion]
    print_progress = False
    args = {}

    for n,c,k in [(4,16,3)]:
        times = {solver.__module__: 0 for solver in solvers}
        for solver in solvers:
            times[solver.__module__] = test_solver(n,c,k,solver,args,print_progress=print_progress,num_tests=100)

        print(f"Times for {n},{c},{k}")
        for solver,time in times.items():
            print(f"{solver}: {time}")
        
        print(f"Time order of solvers: {sorted(times,key=times.get)}")
    
    print("All tests passed")

    