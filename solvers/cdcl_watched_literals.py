from solvers.cdcl_clause_learning import cdcl_clause_learning 
import random
import time
import copy
from collections import deque

class cdcl_watched_literals(cdcl_clause_learning):
    def __init__(self) -> None:
        super().__init__()

    # -> override to add extra data structures
    def reset_variables(self, formula):
        super().reset_variables(formula)
        # variables that are assigned and not yet propagated
        self.assigned_and_not_processed_variables = deque()
        # 100%-certain assignments due to learned unit clauses
        self.certain_assignments = [] 
        # watched literals
        self.watched_clauses = {}
        self.literals_seen_per_clause = {}
        for literal in self.unassigned_variables:
            self.watched_clauses[literal] = []
            self.watched_clauses[-literal] = []

    # sets watched literals for a clause
    # also checks if clause is unit -> add to certain_assignments and remember for propagation
    def init_watched_literals(self,clause):
        if len(clause) >= 2:
            literals_to_watch = random.sample(clause,2)
            # remember [clause, other_literal_watched_for_this_clause]
            self.watched_clauses[literals_to_watch[0]].append([clause,literals_to_watch[1]])
            self.watched_clauses[literals_to_watch[1]].append([clause,literals_to_watch[0]])
        else:
            self.certain_assignments.append(clause[0])
            if -clause[0] not in self.certain_assignments:
                self.remember_assignment(clause[0])
            else:
                self.sat = False

    # -> override to use watched literals
    def propagate(self):
        # propagate
        while len(self.assigned_and_not_processed_variables) > 0:
            new_assignment = self.assigned_and_not_processed_variables.popleft()

            watched_literal = -new_assignment
            # loop over clauses containing watched literal
            for clause, other_watched_literal in copy.deepcopy(self.watched_clauses[watched_literal]):
                # if clause isn't already true because other_watched_literal is true
                if not (other_watched_literal in self.decision_level_per_assigned_literal): 
                    # find new literal to watch
                    new_watched_literal = None
                    for possible_new_watched_literal in clause:
                        if (not (-possible_new_watched_literal in self.decision_level_per_assigned_literal) 
                                and possible_new_watched_literal != other_watched_literal):
                            new_watched_literal = possible_new_watched_literal
                            break
                    # if new watched literal is found -> set new watched literal
                    if new_watched_literal != None:
                        self.watched_clauses[watched_literal].remove([clause, other_watched_literal])
                        for other_watched_literal_information in self.watched_clauses[other_watched_literal]:
                            if clause == other_watched_literal_information[0]:
                                other_watched_literal_information[1] = new_watched_literal
                        self.watched_clauses[new_watched_literal].append([clause,other_watched_literal])
                    # if new watched literal isn't found
                    else:
                        # if other_watched_literal is false and we can't find another literal to watch -> conflict
                        if -other_watched_literal in self.decision_level_per_assigned_literal:
                            self.conflict_clause = clause
                            # add "conflict" node to conflict graph
                            self.update_conflict_graph()
                            self.assigned_and_not_processed_variables = deque()
                            return
                        # if other_watched_literal becomes unit -> remember and propagate
                        else:
                            self.propagation_count += 1
                            self.remember_assignment(other_watched_literal)
                            self.update_conflict_graph([[clause,other_watched_literal]])

    # -> override to add unit assignments to assigned_and_not_processed_variables
    def remember_assignment(self, assignment: int):
        super().remember_assignment(assignment)
        self.assigned_and_not_processed_variables.append(assignment)

    # re-instantiates 100%-certain assignments due to learned unit clauses in all data structures
    def reinstantiate_certain_assignments(self):
        for certain_assignment in self.certain_assignments:
            if certain_assignment not in self.assignments[0]:
                self.assignments[0].append(certain_assignment)
            self.decision_level_per_assigned_literal[certain_assignment] = 0
            if abs(certain_assignment) in self.unassigned_variables:
                self.unassigned_variables.remove(abs(certain_assignment))

    def backtrack(self, new_decision_level):
        super().backtrack(new_decision_level)
        # re-instantiate 100%-certain assignments due to learned unit clauses (backtracking might remove those too)
        self.reinstantiate_certain_assignments()
        # initiate complete unit propagation since there is a new learned clause
        self.assigned_and_not_processed_variables = deque(sum(self.assignments,[]))

    # -> override to also instantiate watched literals for new learned clause
    def remember_learned_clause(self, learned_clause):
        super().remember_learned_clause(learned_clause)
        self.init_watched_literals(self.learned_clauses[-1])

    # initialized watched literals for all known clauses, checks if 
    def init_all_watched_literals(self):
        for clause in self.known_clauses:
            self.init_watched_literals(clause)
    
    # -> override to remove input variables to propagate() and to add watched literals initialization and 
    def solve(self, formula):
        # initialize variables
        self.time_start = time.time()
        self.reset_variables(formula)
        self.init_all_watched_literals()

        # formula might be unsat due to unit clauses already
        if not self.sat:
            self.write_proof()
            return self.return_statement()

        # actual algorithm
        while len(self.unassigned_variables) > 0:
            self.decision_level += 1
            self.assignments.append([])
            # assign truth value to a literal
            self.decide()
            # unit propagate
            self.propagate()

            # if conflict occurs
            while self.conflict_clause != None:
                self.conflict_count += 1
                # if conflict occurs at the root level -> unsat
                if self.decision_level == 0:
                    self.sat = False
                    self.write_proof()
                    return self.return_statement()
                # learn clause and figure out backtracking level
                new_decision_level = self.analyze_conflict()
                # backtrack
                self.backtrack(new_decision_level)
                # unit propagate
                self.propagate()

            # restart occasionally
            self.apply_restart_policy()

        # return sat
        self.write_proof()
        return self.return_statement()