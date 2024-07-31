import math
import random
import numpy as np
import argparse

def binom(x,y):
    if y == 1:
        return(x)
    if y == x:
        return(1)
    if y > x:
        return(0)      
    else:
        a = math.factorial(x)
        b = math.factorial(y)
        div = a // (b*(x-y))
        return(div)  
    
# n = number of variables, c = number of clauses
def convert_to_dimacs(formula,n,c):
    return "p cnf " + str(n) + " " + str(c) + "\n" + "\n".join([" ".join([str(l) for l in clause]) + " 0" for clause in formula])

def random_cnf(n,c,k,seed=42):
    # stop for wrong input
    num_possible_clauses = binom(n,k)*2**k
    if n <= 0 or c <= 0 or k <= 0 or k > n or num_possible_clauses<c:
        print("Invalid input")
        return None
    # initialize
    formula = []
    random.seed(seed)
    # generate random cnf
    possible_literals = list(range(1, n+1))
    i = 0
    used_clauses = []
    while i < c:
        # choose literals
        literals = set(random.sample(possible_literals,k))
        # choose positive/negative encoding
        pos_neg_encoding = random.randint(0,2**k-1)
        # check if clause already exists
        if (literals,pos_neg_encoding) in used_clauses:
            continue
        used_clauses.append((literals,pos_neg_encoding))
        # negate literals
        pos_neg_encoding = np.binary_repr(pos_neg_encoding,width=k)
        literals = list(literals)
        for pos, char in enumerate(str(pos_neg_encoding)):
            if char == '1':
                literals[pos] = -literals[pos]
        # append new clause
        formula.append(literals)
        i = i+1
    return formula

# run this from parent folder using "python -m formula_generation.random_cnf <n> <c> <k>"
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="n c k random cnf generator")
    parser.add_argument("num_variables", nargs="?", default="50")
    parser.add_argument("num_clauses", nargs="?", default="100")
    parser.add_argument("num_literals", nargs="?", default="3")
    args=parser.parse_args()
    n = int(args.num_variables)
    c = int(args.num_clauses)
    k = int(args.num_literals)
    formula = random_cnf(n,c,k)
    if formula is None:
        exit()
    output = convert_to_dimacs(formula,n,c)
    print(output)
    # write to file
    f = open("random_cnf.cnf", "w")
    f.write(output)
    f.close()
