from unit_propagate import simplify
from pysat.solvers import Cadical103
from random_cnf import random_cnf

def test_simplify(n,c,k):
    for _ in range(50):
        formula = random_cnf(n,c,k)
        cadical = Cadical103()
        cadical.append_formula(formula)

        if cadical.solve():
            model = cadical.get_model()
            assignments = {abs(literal): True if literal > 0 else False for literal in model}
            assert simplify(formula, assignments) == []
        else:
            assert simplify(formula, {}) != []


if __name__ == "__main__":
    assignments = {2: False, 3: False}
    formula = [[1, 3, -4], [-1, -3, -4], [-1, -3, 4], [-1, 3, -4], [1, 3, 4], [1, -2, -3], [1, -3, -4]]
    print(simplify(formula, assignments))
    assert len(simplify(formula, assignments)) == 0

    # test_simplify(3,5,2)
    # test_simplify(10,50,3)

    print("All tests passed")
