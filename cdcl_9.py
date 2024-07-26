from cdcl_8 import cdcl_decision_heuristics_and_restarts
import copy
import time

class cdcl_clause_minimization_and_deletion(cdcl_decision_heuristics_and_restarts):
    def __init__(self, random_decision_frequency=200, vsids_multiplier=1.05, c=100, max_lbd=10, max_lbd_multiplier=1.1) -> None:
        super().__init__(random_decision_frequency, vsids_multiplier, c)
        self.max_lbd = max_lbd
        self.max_lbd_multiplier = max_lbd_multiplier

    # -> override to add deleted_clause_count
    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.deleted_clause_count = 0
        # lbd scores of learned clauses: {clause: lbd_score}
        self.lbd_scores = []

    # -> override to add deleted_clause_count
    def get_statistics(self):
        runtime = time.time()-self.time_start
        return {"runtime": runtime, "propagation_count": self.propagation_count, "decision_count": self.decision_count, "conflict_count": self.conflict_count, "learned_clause_count": self.learned_clause_count, "restart_count": self.restart_count, "deleted_clause_count": self.deleted_clause_count}

    # minimizes learned clause 
    def minimize_learned_clause(self, learned_clause):
        literals_to_delete = set()
        # loop over literals in learned clause
        for literal in learned_clause:
            # if literal has predecessors
            if literal in self.immediate_predecessors and self.immediate_predecessors[literal] != []:
                all_predecessors_within_learned_clause = True
                # check if all predecessors are within learned clause
                for predecessor in self.immediate_predecessors[literal]:
                    if predecessor not in learned_clause:
                        all_predecessors_within_learned_clause = False
                # if yes -> remove literal from learned clause
                if all_predecessors_within_learned_clause:
                    literals_to_delete.add(literal)
        if len(literals_to_delete) > 0:
            learned_clause = [l for l in learned_clause if l not in literals_to_delete]
        return learned_clause

    # -> override to add clause minimization
    def analyze_conflict(self):
        self.current_conflict_count += 1
        learned_clause, new_decision_level, involved_variables = self.get_learned_clause()
        learned_clause = self.minimize_learned_clause(learned_clause)
        if len(learned_clause) > 0:
            self.remember_learned_clause(learned_clause)
            self.update_vsids_scores(involved_variables)
        return new_decision_level
    
    # -> override to also remember lbd score of learned clause 
    def remember_learned_clause(self, learned_clause):
        super().remember_learned_clause(learned_clause)
        self.lbd_scores.append(self.lbd(learned_clause))
        
    # returns lbd score of clause
    def lbd(self,clause):
        unique_decision_levels = set()
        for literal in clause:
            unique_decision_levels.add(self.decision_level_per_assigned_literal[-literal])
        return len(unique_decision_levels)
    
    # applies clause deletion using lbd score
    def delete_learned_clauses(self):
        for learned_clause in copy.deepcopy(self.learned_clauses):
            lbd = self.lbd_scores[learned_clause]
            if lbd > self.max_lbd and lbd > 2:
                self.deleted_clause_count += 1
                self.known_clauses.remove(learned_clause)
                clause_index = self.learned_clauses.index(learned_clause)
                self.learned_clauses.pop(clause_index)
                self.lbd_scores.pop(clause_index)
        self.max_lbd *= self.max_lbd_multiplier

    # -> override to add deletion of learned clauses
    def apply_restart(self):
        self.delete_learned_clauses()
        super().apply_restart()

