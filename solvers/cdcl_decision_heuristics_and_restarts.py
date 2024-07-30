from solvers.cdcl_watched_literals import cdcl_watched_literals 
from solvers.utils import get_unique_literals_in_formula

class cdcl_decision_heuristics_and_restarts(cdcl_watched_literals):
    def __init__(self, random_decision_frequency=200, vsids_multiplier=1.05, c=100, use_decision_heuristics=True, use_restarts=True) -> None:
        super().__init__()
        self.random_decision_frequency = random_decision_frequency
        self.vsdids_multiplier = vsids_multiplier
        self.c = c
        self.use_decision_heuristics = use_decision_heuristics
        self.use_restarts = use_restarts

    # -> override to add vsids scores, phases, luby sequence and restart count
    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.vsids_scores = {variable: 0 for variable in self.unassigned_variables}
        self.vsids_value_to_add = 2
        self.phases = {variable: False for variable in self.unassigned_variables}
        # just remember "current" sequence of luby sequence and current position in it
        self.current_luby_sequence = [1,1,2]
        self.current_luby_index = 0
        self.current_conflict_count = 0

    # -> override to apply vsids heuristic and phase saving
    def get_decision_variable(self):
        if self.use_decision_heuristics:
            # return random decision variable every 200 conflicts
            if self.conflict_count % self.random_decision_frequency == 0:
                return super().get_decision_variable()
            
            # get decision variable with highest vsids score
            vsids_without_assigned_variables = {variable: score for variable, score in self.vsids_scores.items() if variable in self.unassigned_variables}
            decision_variable = max(vsids_without_assigned_variables,key=vsids_without_assigned_variables.get)

            # return decision variable with correct phase
            decision_variable = decision_variable if self.phases[decision_variable] else -decision_variable
            return decision_variable
        else:
            return super().get_decision_variable()
            
    # lowers vsids_scores and vsids_value_to_add to prevent overflow if necessary
    def adjust_for_vsids_overflow(self):
        max_score = max(self.vsids_scores.values())
        overflow = max_score + self.vsids_value_to_add < 0
        if overflow:
            for variable in self.vsids_scores:
                self.vsids_scores[variable] = self.vsids_scores[variable] >> 20
            self.vsids_value_to_add = self.vsids_value_to_add >> 20

    # updates vsids scores for involved variables
    def update_vsids_scores(self, involved_variables):
        self.adjust_for_vsids_overflow()
        for literal in involved_variables:
            self.vsids_scores[abs(literal)] += self.vsids_value_to_add
        self.vsids_value_to_add *= self.vsdids_multiplier

    # -> override to also update vsids scores
    def analyze_conflict(self):
        self.current_conflict_count += 1
        learned_clause, new_decision_level, involved_variables = self.get_learned_clause()
        self.remember_learned_clause(learned_clause)
        if self.use_decision_heuristics: self.update_vsids_scores(involved_variables)
        return new_decision_level
    
    # -> override to also remember phase unit assignments
    def remember_assignment(self, assignment: int):
        super().remember_assignment(assignment)
        self.phases[abs(assignment)] = True if assignment > 0 else False

    # resets data structures
    def apply_restart(self):
        self.assignments = [[]]
        self.decision_level_per_assigned_literal = {}
        self.decision_level = 0
        self.unassigned_variables = get_unique_literals_in_formula(self.formula, only_positive=True)
        self.reinstantiate_certain_assignments()

    # new restart policy: luby restarts
    def apply_restart_policy(self):
        if self.use_restarts:
            if self.current_conflict_count == self.c * self.current_luby_sequence[self.current_luby_index]:
                self.current_conflict_count = 0
                self.restart_count += 1
                self.current_luby_index += 1
                # if current luby sequence is finished -> append it accordingly and reset position to 0
                if self.current_luby_index == len(self.current_luby_sequence)-1:
                    self.current_luby_index = 0
                    self.current_luby_sequence.append(self.current_luby_sequence[-1]*2)
                # restart
                self.apply_restart()
