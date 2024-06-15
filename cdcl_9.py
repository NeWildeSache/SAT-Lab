from cdcl_8 import cdcl_decision_heuristics_and_restarts
import copy
import time

class cdcl_clause_minimization_and_deletion(cdcl_decision_heuristics_and_restarts):
    def __init__(self) -> None:
        super().__init__()
        self.max_lbd = 10
        self.max_lbd_multiplier = 1.1

    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.deleted_clause_count = 0

    def minimize_learned_clause(self, learned_clause):
        literals_to_delete = set()
        for literal in learned_clause:
            if literal in self.immediate_predecessors and self.immediate_predecessors[literal] != []:
                all_predecessors_within_learned_clause = True
                for predecessor in self.immediate_predecessors[literal]:
                    if predecessor not in learned_clause:
                        all_predecessors_within_learned_clause = False
                if all_predecessors_within_learned_clause:
                    literals_to_delete.add(literal)
        if len(literals_to_delete) > 0:
            learned_clause = [l for l in learned_clause if l not in literals_to_delete]
        return learned_clause

    def analyze_conflict(self):
        learned_clause, new_decision_level, involved_variables = self.get_learned_clause()
        learned_clause = self.minimize_learned_clause(learned_clause)
        if len(learned_clause) > 0:
            self.remember_learned_clause(learned_clause)
        self.update_vsids_scores(involved_variables)
        return new_decision_level
    
    # -> override to add deleted_clause_count
    def get_statistics(self):
        runtime = time.time()-self.time_start
        return [runtime, self.propagation_count, self.decision_count, self.conflict_count, self.learned_clause_count, self.deleted_clause_count, self.restart_count]

    def lbd(self,clause):
        unique_decision_levels = set()
        for literal in clause:
            unique_decision_levels.add(self.decision_level_per_assigned_literal[literal])
        return len(unique_decision_levels)

    def apply_restart(self):
        for learned_clause in copy.deepcopy(self.learned_clauses):
            lbd = self.lbd(learned_clause)
            if lbd > self.max_lbd and lbd > 2:
                self.deleted_clause_count += 1
                self.known_clauses.remove(learned_clause)
                self.learned_clauses.remove(learned_clause)
        self.max_lbd *= self.max_lbd_multiplier
        super().apply_restart()

