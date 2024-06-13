from cdcl_6 import cdcl_clause_learning 
import networkx as nx
import sys

class cdcl_decision_heuristics_and_restarts(cdcl_clause_learning):
    def __init__(self, random_decision_frequency=200, vsids_multiplier=1.05) -> None:
        super().__init__()
        self.random_decision_frequency = random_decision_frequency
        self.vsdids_multiplier = vsids_multiplier
        self.c = 100

    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.vsids_scores = {variable: 0 for variable in self.unassigned_variables}
        self.vsids_value_to_add = 2
        self.phases = {variable: False for variable in self.unassigned_variables}
        self.current_luby_sequence = [1,1,2]
        self.current_luby_index = 0
        self.restart_count = 0

    def get_decision_variable(self):
        # return random decision variable every 200 conflicts
        if self.conflict_count % self.random_decision_frequency == 0:
            return super().get_decision_variable()
        
        # get decision variable with highest vsids score
        vsids_without_assigned_variables = {variable: score for variable, score in self.vsids_scores.items() if variable in self.unassigned_variables}
        decision_variable = max(vsids_without_assigned_variables,key=vsids_without_assigned_variables.get)

        # return decision variable with correct phase
        decision_variable = decision_variable if self.phases[decision_variable] else -decision_variable
        return decision_variable

    def adjust_for_vsids_overflow(self):
        max_score = max(self.vsids_scores.values())
        overflow = max_score + self.vsids_value_to_add < 0
        if overflow:
            for variable in self.vsids_scores:
                self.vsids_scores[variable] = self.vsids_scores[variable] >> 20
            self.vsids_value_to_add = self.vsids_value_to_add >> 20

    def analyze_conflict(self):
        # get learned clause using first uip
        last_decision_literal = self.assignments[-1][0]
        first_uip = nx.immediate_dominators(self.conflict_graph, last_decision_literal)["conflict"]
        last_decision_level_literals = self.assignments[-1]
        descendants_of_uip = list(nx.descendants(self.conflict_graph, first_uip))
        predecessors_of_uip_descendants = set()
        for descendant in descendants_of_uip:
            predecessors = list(self.conflict_graph.predecessors(descendant))
            for predecessor in predecessors:
                predecessors_of_uip_descendants.add(predecessor)
        predecessors_of_uip_descendants = list(predecessors_of_uip_descendants)
        learned_clause = [-literal for literal in predecessors_of_uip_descendants if literal not in last_decision_level_literals]
        learned_clause.append(-first_uip)
        
        self.learned_clauses.append(learned_clause)
        self.known_clauses.append(learned_clause)

        # update vsids scores
        self.adjust_for_vsids_overflow()
        descendants_of_uip.remove("conflict")
        involved_variables = set(learned_clause+descendants_of_uip)
        for literal in involved_variables:
            self.vsids_scores[abs(literal)] += self.vsids_value_to_add
        self.vsids_value_to_add *= self.vsdids_multiplier
        
        # get new decision level
        new_decision_level = 0
        for i, decision_level_assignments in enumerate(reversed(self.assignments[:-1])):
            intersection = [item for item in decision_level_assignments if item in learned_clause]
            if len(intersection) > 0:
                new_decision_level = len(self.assignments)-(i+2)

        return new_decision_level
    
    def remember_unit_assignments(self, unit_assignments):
        super().remember_unit_assignments(unit_assignments)
        for unit_assignment in unit_assignments:
            self.phases[abs(unit_assignment)] = True if unit_assignment > 0 else False

    def apply_restart_policy(self):
        if self.conflict_count == self.c * self.current_luby_sequence[self.current_luby_index]:
            self.restart_count += 1
            # append luby sequence if necessary
            if self.current_luby_index == len(self.current_luby_sequence)-1:
                self.current_luby_index = 0
                self.current_luby_sequence.append(self.current_luby_sequence[-1]*2)
            # restart
            self.assignments = [[]]

        