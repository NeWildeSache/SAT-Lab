from pysat.solvers import Cadical103
from formula_generation import random_cnf
import numpy as np
import math
import copy
from tqdm.auto import tqdm
from IPython.display import clear_output
from matplotlib import pyplot as plt
import multiprocessing

# allows computation and plotting of statistics for multiple solvers
class StatisticsModule():
    def __init__(self, k=3, gamma=4.26, seed=100, num_tests=100, print_solving_information=False, print_progress=True, check_correctness=False, formula_creator=random_cnf, timeout_threshold=60, use_timeouts=True, averaging_function=np.mean):
        self.k = k
        self.gamma = gamma    
        self.seed = seed
        self.num_tests = num_tests
        self.print_solving_information = print_solving_information
        self.check_correctness = check_correctness
        self.formula_creator = formula_creator
        self.timeout_threshold = timeout_threshold
        self.use_timeouts = use_timeouts
        self.averaging_function = averaging_function
        self.print_progress = print_progress

    # creates self.num_tests random formulas and solves them with the given solver
    # returns a dictionary with the statistics of the solver ({statistic: [values]})
    # if check_correctness is True, the solver is compared to cadical
    def solver_statistics(self,n,solver,solver_args={},c=None,k=None): 
        statistics = {}
        c = math.ceil(n*self.gamma) if c == None else c
        k = self.k if k == None else k

        # create formula seeds using a general seed
        np.random.seed(self.seed)
        formula_seeds = np.random.randint(0,self.num_tests*1000,size=self.num_tests)

        # test solver on multiple formulas
        for formula_seed in formula_seeds:
            # generate random formula
            if self.formula_creator == random_cnf:
                formula = self.formula_creator(n,c,k,seed=int(formula_seed))
            else:
                formula = self.formula_creator(n)
            if formula == None: break

            # solve formula
            if isinstance(solver,type): # check if solver is a class
                solver_instance = solver(**solver_args)
                outputs = solver_instance.solve(formula)
            else: 
                outputs = solver(formula)
            solver_sat = outputs["SAT"]

            # add statistics to dictionary, each entry contains a list with the values of all tests
            for key in outputs.keys():
                if key not in statistics:
                    statistics[key] = []
                statistics[key].append(outputs[key])

            # get cadical result for comparison (if check_correctness is True)
            if self.check_correctness:
                cadical = Cadical103()
                cadical.append_formula(formula)
                cadical_sat = cadical.solve()

            # print lots of information (good for debugging)
            if self.print_solving_information:
                print("-"*10)
                print(f"Using: {solver.__name__}")
                print(f"Formula: {formula}")
                print(f"Solver: {solver_sat}")
                if self.check_correctness: print(f"Cadical: {cadical_sat}")
                if solver_sat: print(f"solver model: {outputs["model"]}")
                if self.check_correctness and cadical_sat: print(f"cadical model: {cadical.get_model()}")

            # assert correctness
            if self.check_correctness: assert solver_sat == cadical_sat

        return statistics
    
    # returns a string for the solver and its arguments
    def get_key_for_solver_with_args(self,solver,args: dict):
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

    # returns a dictionary with the statistics of multiple solvers ({solver: {statistics_dict: [values]}})
    # if self.use_timeouts is True, the solver is run in a separate process and terminated if it takes too long
    # the timeout threshold is set by self.timeout_threshold
    # if return_timeouts is True, also returns a list of indices of solvers that took too long
    def get_statistics_for_multiple_solvers(self,n,solvers,solver_args=[],return_timeouts=False):
        # initialize solver_args if not given
        if solver_args == []:
            solver_args = [{} for _ in range(len(solvers))]
        statistics = {}
        solvers_that_took_too_long = []
        # get statistics for each solver
        for i, (solver, args) in tqdm(enumerate(zip(solvers,solver_args)),total=len(solvers),disable=not self.print_progress):
            if self.use_timeouts:
                pool = multiprocessing.Pool(processes=1)
                result = pool.apply_async(self.solver_statistics, (n,solver,args))
                try:
                    statistics[self.get_key_for_solver_with_args(solver,args)] = result.get(timeout=self.timeout_threshold)
                except multiprocessing.TimeoutError:
                    solvers_that_took_too_long.append(i)
                finally:
                    pool.terminate()
            else:
                statistics[self.get_key_for_solver_with_args(solver,args)] = self.solver_statistics(n,solver,args)
        # return statistics
        if self.print_progress: clear_output() # clear tqdm output
        if return_timeouts:
            return statistics, solvers_that_took_too_long
        else:
            return statistics

    # returns a dictionary with the statistics of multiple solvers for multiple n values ({n: {solver: {statistics_dict: [values]}}})
    def get_statistics_for_multiple_n(self,n_values,solvers,solver_args=[]):
        solvers = copy.deepcopy(solvers)
        statistics = {}
        for n in n_values:
            if self.print_progress: print("Testing with n =",n)
            # get statistics
            n_stats, solvers_that_took_too_long = self.get_statistics_for_multiple_solvers(n,solvers,solver_args=solver_args,return_timeouts=True)
            statistics[n] = n_stats
            solvers = [solvers[i] for i in range(len(solvers)) if i not in solvers_that_took_too_long]
            solver_args = [solver_args[i] for i in range(len(solver_args)) if i not in solvers_that_took_too_long]
        if self.print_progress: clear_output() # clear progress output
        return statistics
    
    # averages the statistics of a solver 
    # {n: {solver: {statistics_dict: [values]}}} -> {n: {solver: {statistics_dict: [average_value]}}}
    def average_statistics(self,statistics):
        if statistics == {}: return statistics
        statistics = copy.deepcopy(statistics)
        if type(list(statistics.values())[0]) == dict:
            for key in statistics.keys():
                statistics[key] = self.average_statistics(statistics[key])
        elif type(list(statistics.values())[0]) == list:
            for key in statistics.keys():
                if isinstance(statistics[key][0], (int, float, complex, bool)):
                    statistics[key] = self.averaging_function(statistics[key])
        return statistics

    # returns a dictionary with averaged statistics of multiple solvers for multiple n values ({n: {solver: {statistics_dict: [average_value]}}})
    def get_average_statistics_for_multiple_n(self,n_values,solvers,solver_args=[]):
        statistics = self.get_statistics_for_multiple_n(n_values,solvers,solver_args=solver_args)
        return self.average_statistics(statistics)

    # returns a dictionary with {solver_name: [values]} for a specific statistic
    # this means that the values are grouped by solver and not by n
    def get_values_per_solver(self,statistics_per_n,n_values,statistic="runtime"):
        values = {}
        for n in n_values:
            if n in statistics_per_n:
                n_statistics = statistics_per_n[n]
                for solver in n_statistics.keys():
                    if solver not in values:
                        values[solver] = []
                    values[solver].append(n_statistics[solver][statistic])
        return values
    
    # plots a statistic for multiple solvers for multiple n values
    def plot_statistic(self,statistics_per_n,n_values,statistic="runtime",title_addition="",title="",yscale="log"):
        values = self.get_values_per_solver(statistics_per_n,n_values,statistic)
        for solver, stat_values in values.items():
            plt.plot(n_values[0:len(stat_values)],stat_values,label=solver)

        plt.yscale(yscale)
        plt.xlabel("n")
        plt.ylabel(statistic)
        plt.legend()
        if title == "":
            plt.title(statistic + f" per solver for different n (k={self.k}, c={self.gamma}n)" + title_addition)
        else:
            plt.title(title)
        plt.show()

    # plots multiple statistics for multiple solvers for multiple n values
    def plot_multiple_statistics(self,statistics_per_n,n_values,statistics=["runtime"]):
        for statistic in statistics:
            self.plot_statistic(statistics_per_n,n_values,statistic)
