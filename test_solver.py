from two_sat_solver import solve_2_sat
from davis_putnam import davis_putnam
from pysat.solvers import Cadical103
from random_cnf import random_cnf
from dpll import dpll
from cdcl import cdcl as cdcl
from cdcl_6 import cdcl_clause_learning as cdcl_clause_learning

def test_solver(n,c,k,solver,num_tests=50):
    for _ in range(num_tests):
        print("-"*10)
        print(f"Using: {solver.__name__}")
        formula = random_cnf(n,c,k)
        print(f"Formula: {formula}")

        if isinstance(solver,type): # check if solver is a class
            outputs = solver().solve(formula)
        else: 
            outputs = solver(formula)
        sat = outputs[0]
        cadical = Cadical103()
        cadical.append_formula(formula)
        cadical_sat = "SAT" if cadical.solve() else "UNSAT"

        print(f"Solver: {sat}")
        print(f"Cadical: {cadical_sat}")

        if sat == "SAT":
            print(f"solver model: {outputs[1]}")
        if cadical_sat == "SAT":
            model = cadical.get_model()
            model = {abs(literal): True if literal > 0 else False for literal in model}
            print(f"cadical model: {model}")

        assert sat == cadical_sat


if __name__ == "__main__":
    # test_solver(3,5,2,solve_2_sat)
    # test_solver(100,100,2,solve_2_sat)

    # test_solver(4,16,3,davis_putnam)
    # test_solver(10,38,3,davis_putnam)

    # test_solver(4,16,3,dpll)
    # test_solver(10,38,3,dpll)

    # test_solver(4,16,3,cdcl)
    # test_solver(10,38,3,cdcl)

    test_solver(4,16,3,cdcl_clause_learning)
    test_solver(10,38,3,cdcl_clause_learning)
    
    print("All tests passed")

    