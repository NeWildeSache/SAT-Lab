from solvers import *
from statistics_utils import *

if __name__ == "__main__":
    stats_module = StatisticsModule(check_correctness=True, num_tests=100) # check_correctness enables the validation against cadical

    solvers = [cdcl_decision_heuristics_and_restarts]
    ns = [200]
    statistics = stats_module.get_statistics_for_multiple_n(ns,solvers)

    print("All tests passed!")

    # solvers = [cdcl_clause_minimization_and_deletion]
    # ns = [25,30]
    # stats_module = StatisticsModule(gamma=4.5)
    # all_solver_statistics = stats_module.get_average_statistics_for_multiple_n(ns,solvers)
    # stats_module.plot_multiple_statistics(all_solver_statistics,ns,["runtime","decision_count","conflict_count","learned_clause_count","deleted_clause_count"])