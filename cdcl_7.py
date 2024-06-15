from cdcl_6 import cdcl_clause_learning 
import random
import time
import copy

# MOMENTAN: ENTWEDER SAT ODER INFINITE LOOP

class cdcl_watched_literals(cdcl_clause_learning):
    def __init__(self) -> None:
        super().__init__()

    def set_watched_literals(self,clause,index):
        if len(clause) >= 2:
            literals_to_watch = random.sample(clause,2)
            # remember [clause, other_literal_watched_for_this_clause]
            self.watched_clauses[literals_to_watch[0]].append([clause,index,literals_to_watch[1]])
            self.watched_clauses[literals_to_watch[1]].append([clause,index,literals_to_watch[0]])
        else:
            self.certain_assignments.append(clause[0])

    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.watched_clauses = {}
        self.literals_seen_per_clause = {}
        for literal in self.unassigned_variables:
            self.watched_clauses[literal] = []
            self.watched_clauses[-literal] = []
        for i, clause in enumerate(self.known_clauses):
            self.set_watched_literals(clause,i)
        self.assigned_and_not_processed_variables = []
        self.certain_assignments = []

    def decide(self):
        decision_variable = super().decide()
        self.assigned_and_not_processed_variables.append(decision_variable)
    
    def propagate(self):
        # propagate
        while len(self.assigned_and_not_processed_variables) > 0:
            self.propagation_count += 1
            new_assignment = self.assigned_and_not_processed_variables.pop()

            first_watched_literal = -new_assignment
            for watched_literal_information in copy.deepcopy(self.watched_clauses[first_watched_literal]):
                clause, clause_index, other_watched_literal = watched_literal_information
                # if clause isn't already true because other_literal_watched_for_this_clause is true
                if not (other_watched_literal in self.decision_level_per_assigned_literal): 
                    # find new literal to watch
                    new_watched_literal = None
                    for possible_new_watched_literal in clause:
                        if (not (-possible_new_watched_literal in self.decision_level_per_assigned_literal) 
                                and possible_new_watched_literal != other_watched_literal):
                            new_watched_literal = possible_new_watched_literal
                    if new_watched_literal != None:
                        # set new watched literal
                        self.watched_clauses[first_watched_literal].remove(watched_literal_information)
                        for item in self.watched_clauses[other_watched_literal]:
                            if clause_index == item[1]:
                                item[2] = new_watched_literal
                        self.watched_clauses[new_watched_literal].append([clause,clause_index,other_watched_literal])
                    else:
                        # other_literal_watched_for_this_clause is false and we can't find another literal to watch -> conflict
                        if -other_watched_literal in self.decision_level_per_assigned_literal:
                            self.conflict_clause = clause
                        # other_literal_watched_for_this_clause becomes unit
                        else:
                            self.remember_unit_assignments([other_watched_literal])
                            self.assigned_and_not_processed_variables.append(other_watched_literal)
                            self.update_conflict_graph([[clause_index,other_watched_literal]])

        # add potential "conflict" node to conflict graph
        self.update_conflict_graph([])

    def reinstantiate_certain_assignments(self):
        for certain_assignment in self.certain_assignments:
            if certain_assignment not in self.assignments[0]:
                self.assignments[0].append(certain_assignment)
            self.decision_level_per_assigned_literal[certain_assignment] = 0
            if abs(certain_assignment) in self.unassigned_variables:
                self.unassigned_variables.remove(abs(certain_assignment))

    def backtrack(self, new_decision_level):
        super().backtrack(new_decision_level) 
        # re-instantiate 100%-certain assignments due to learned unit clauses
        self.reinstantiate_certain_assignments()
        # initiate complete unit propagation since there is a new learned clause
        self.assigned_and_not_processed_variables = list(self.decision_level_per_assigned_literal.keys())

    def remember_learned_clause(self, learned_clause):
        super().remember_learned_clause(learned_clause)
        self.set_watched_literals(self.learned_clauses[-1],len(self.known_clauses)-1)
    
    # -> override to remove formula / copy.deepcopy(formula) from input variables to propagate()
    def solve(self, formula):
        self.time_start = time.time()
        self.reset_variables(formula)

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
                    self.write_proof(sat=False)
                    return self.return_statement(sat=False)
                # learn clause and figure out backtracking level
                new_decision_level = self.analyze_conflict()
                # backtrack
                self.backtrack(new_decision_level)
                # unit propagate
                self.propagate()

            # restart occasionally
            self.apply_restart_policy()

        # return sat
        self.write_proof(sat=True)
        return self.return_statement(sat=True)

