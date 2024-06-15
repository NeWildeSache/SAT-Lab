from solve_2_sat import solve_2_sat
from davis_putnam import davis_putnam
from pysat.solvers import Cadical103
from random_cnf import random_cnf
from dpll import dpll
from cdcl import cdcl as cdcl
from cdcl_6 import cdcl_clause_learning as cdcl_clause_learning
from cdcl_7 import cdcl_watched_literals as cdcl_watched_literals
from cdcl_8 import cdcl_decision_heuristics_and_restarts as cdcl_decision_heuristics_and_restarts
import numpy as np

def test_solver(n,c,k,solver,num_tests=50,return_average_time=True,print_progress=False):
    times = []
    for _ in range(num_tests):
        formula = random_cnf(n,c,k)
        if print_progress:
            print("-"*10)
            print(f"Using: {solver.__name__}")
            print(f"Formula: {formula}")

        if isinstance(solver,type): # check if solver is a class
            outputs = solver().solve(formula)
        else: 
            outputs = solver(formula)
        solver_sat = outputs[0]
        cadical = Cadical103()
        cadical.append_formula(formula)
        cadical_sat = "SAT" if cadical.solve() else "UNSAT"

        if print_progress:
            print(f"Solver: {solver_sat}")
            print(f"Cadical: {cadical_sat}")

        if solver_sat == "SAT":
            if type(outputs[2]) != dict:
                times.append(outputs[2])
            if print_progress:
                print(f"solver model: {outputs[1]}")
        else:
            if type(outputs[1]) != dict:
                times.append(outputs[1])
        if cadical_sat == "SAT":
            model = cadical.get_model()
            model = {abs(literal): True if literal > 0 else False for literal in model}
            if print_progress:
                print(f"cadical model: {model}")

        assert solver_sat == cadical_sat

    return np.mean(times)


if __name__ == "__main__":
    test_solver(3,5,2,solve_2_sat, return_average_time=False)
    test_solver(100,100,2,solve_2_sat, return_average_time=False)

    solvers = [cdcl,cdcl_clause_learning,cdcl_watched_literals,cdcl_decision_heuristics_and_restarts]
    print_progress = False
    # print_progress = True
    # solvers = [cdcl_decision_heuristics_and_restarts]
    for n,c,k in [(3,8,3),(4,16,3),(20,76,3),(30,3.8*30,3)]:
        times = []
        for solver in solvers:
            times.append(test_solver(n,c,k,solver,print_progress=print_progress,num_tests=100))

        print(f"Times for {n},{c},{k}")
        for i,time in enumerate(times):
            print(f"{solvers[i].__name__}: {time}")
    
    print("All tests passed")

    