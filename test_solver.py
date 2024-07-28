from pysat.solvers import Cadical103
from random_cnf import random_cnf
import numpy as np
import math
import copy
from tqdm.auto import tqdm
from IPython.display import clear_output
from matplotlib import pyplot as plt

def solver_statistics(n,c,k,solver,solver_args={},num_tests=100,print_progress=False,check_correctness=True,seed=100,output_clear=True):
    statistics = {}
    np.random.seed(seed)
    formula_seeds = np.random.randint(0,num_tests*1000,size=num_tests)
    for formula_seed in tqdm(formula_seeds,leave=False,total=num_tests):
        # generate random formula
        formula = random_cnf(n,c,k,seed=int(formula_seed))

        # solve formula
        if isinstance(solver,type): # check if solver is a class
            solver_instance = solver(**solver_args)
            outputs = solver_instance.solve(formula)
        else: 
            outputs = solver(formula)
        solver_sat = outputs["SAT"]

        for key in outputs.keys():
            if key != "SAT":
                if key not in statistics:
                    statistics[key] = []
                statistics[key].append(outputs[key])

        if check_correctness:
            cadical = Cadical103()
            cadical.append_formula(formula)
            cadical_sat = cadical.solve()

        # print lots of information (good for debugging)
        if print_progress:
            print("-"*10)
            print(f"Using: {solver.__name__}")
            print(f"Formula: {formula}")
            print(f"Solver: {solver_sat}")
            if check_correctness: print(f"Cadical: {cadical_sat}")
            if solver_sat: print(f"solver model: {outputs["model"]}")
            if check_correctness and cadical_sat: print(f"cadical model: {cadical.get_model()}")

        if output_clear: clear_output(wait=True)
        if check_correctness: assert solver_sat == cadical_sat

    return statistics

def _get_key_for_solver_with_args(solver,args: dict):
    key = solver.__name__
    if args != {}:
        key += "("
    for i, (arg, value) in enumerate(args.items()):
        key += str(arg) + "=" + str(value)
        if i < len(args)-1:
            key += ","
    if args != {}:
        key += ")"
    return key

def get_statistics_for_multiple_solvers(n,c,k,solvers,solver_args=[],num_tests=100):
    if solver_args == []:
        solver_args = [{} for _ in range(len(solvers))]
    statistics = {}
    for solver, args in tqdm(zip(solvers,solver_args),total=len(solvers)):
        statistics[_get_key_for_solver_with_args(solver,args)] = solver_statistics(n,c,k,solver,solver_args=args,num_tests=num_tests,output_clear=False,check_correctness=False)
    clear_output(wait=True) # clear tqdm output
    return statistics

def average_statistics(statistics,averaging_function=np.mean):
    statistics = copy.deepcopy(statistics)
    if type(list(statistics.values())[0]) == dict:
        for key in statistics.keys():
            statistics[key] = average_statistics(statistics[key],averaging_function=averaging_function)
    else:
        for key in statistics.keys():
            if isinstance(statistics[key][0], (int, float, complex)):
                statistics[key] = averaging_function(statistics[key])
    return statistics

def get_statistics_for_multiple_n(n_values,solvers,solver_args=[],num_tests=100,omissions={}):
    solvers = copy.deepcopy(solvers)
    statistics = {}
    k = 3
    for n in n_values:
        print("Testing with n =",n)
        # omit solvers according to omissions parameter
        if n in omissions:
            for solver in omissions[n]:
                solvers.remove(solver)
        # get statistics
        c = math.ceil(n*3.8)
        statistics[n] = get_statistics_for_multiple_solvers(n,c,k,solvers,solver_args=solver_args,num_tests=num_tests)
    clear_output(wait=True) # clear progress output
    return statistics

def get_average_statistics_for_multiple_n(n_values,solvers,solver_args=[],num_tests=100,averaging_function=np.mean):
    statistics = get_statistics_for_multiple_n(n_values,solvers,solver_args=solver_args,num_tests=num_tests)
    return average_statistics(statistics,averaging_function=averaging_function)

def plot_statistic(statistics_per_n,n_values,statistic="runtime",title_addition=""):
    values = {}
    for n in n_values:
        n_statistics = statistics_per_n[n]
        for solver in n_statistics.keys():
            if solver not in values:
                values[solver] = []
            values[solver].append(n_statistics[solver][statistic])

    for solver, stat_values in values.items():
        plt.plot(n_values[0:len(stat_values)],stat_values,label=solver)

    plt.yscale("log")
    plt.xlabel("n")
    plt.ylabel(statistic)
    plt.legend()
    plt.title(statistic + " per solver for different n (k=3, c=3.8n)" + title_addition)
    plt.show()

def plot_multiple_statistics(statistics_per_n,n_values,statistics=["runtime","conflicts","decisions","propagations"],title_addition=""):
    for statistic in statistics:
        plot_statistic(statistics_per_n,n_values,statistic,title_addition)



if __name__ == "__main__":
    from solve_2_sat import solve_2_sat
    from davis_putnam import davis_putnam
    from dpll import dpll
    from cdcl import cdcl 
    from cdcl_6 import cdcl_clause_learning 
    from cdcl_7 import cdcl_watched_literals 
    from cdcl_8 import cdcl_decision_heuristics_and_restarts 
    from cdcl_9 import cdcl_clause_minimization_and_deletion
    
    solvers = [dpll,davis_putnam,cdcl,cdcl_clause_learning,cdcl_watched_literals,cdcl_decision_heuristics_and_restarts,cdcl_clause_minimization_and_deletion]
    solvers = [cdcl_clause_minimization_and_deletion]
    for n,c,k in [(10,38,3)]:
            for solver in solvers:
                solver_statistics(n,c,k,solver)

    print("All tests passed!")