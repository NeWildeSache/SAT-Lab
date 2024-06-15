from cdcl_7 import cdcl_watched_literals 
import time
from formula_preprocessing import get_unique_literals_in_formula

class cdcl_decision_heuristics_and_restarts(cdcl_watched_literals):
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

    # -> override to add restart_count
    def get_statistics(self):
        runtime = time.time()-self.time_start
        return [runtime, self.propagation_count, self.decision_count, self.conflict_count, self.learned_clause_count, self.restart_count]

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

    def update_vsids_scores(self, involved_variables):
        self.adjust_for_vsids_overflow()
        for literal in involved_variables:
            self.vsids_scores[abs(literal)] += self.vsids_value_to_add
        self.vsids_value_to_add *= self.vsdids_multiplier

    # -> override to update vsids scores
    def analyze_conflict(self):
        learned_clause, new_decision_level, involved_variables = self.get_learned_clause()
        self.remember_learned_clause(learned_clause)
        self.update_vsids_scores(involved_variables)
        return new_decision_level
    
    def remember_unit_assignments(self, unit_assignments):
        super().remember_unit_assignments(unit_assignments)
        if type(unit_assignments) == int:
            self.phases[abs(unit_assignments)] = True if unit_assignments > 0 else False
        elif type(unit_assignments) == list:
            for unit_assignment in unit_assignments:
                self.phases[abs(unit_assignment)] = True if unit_assignment > 0 else False

    def apply_restart(self):
        self.assignments = [[]]
        self.decision_level_per_assigned_literal = {}
        self.unassigned_variables = get_unique_literals_in_formula(self.known_clauses, only_positive=True)
        self.reinstantiate_certain_assignments()

    def apply_restart_policy(self):
        if self.conflict_count == self.c * self.current_luby_sequence[self.current_luby_index]:
            self.restart_count += 1
            # append luby sequence if necessary
            if self.current_luby_index == len(self.current_luby_sequence)-1:
                self.current_luby_index = 0
                self.current_luby_sequence.append(self.current_luby_sequence[-1]*2)
            # restart
            self.apply_restart()

        