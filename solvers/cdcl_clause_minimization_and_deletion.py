from solvers.cdcl_decision_heuristics_and_restarts import cdcl_decision_heuristics_and_restarts

class cdcl_clause_minimization_and_deletion(cdcl_decision_heuristics_and_restarts):
    def __init__(self, random_decision_frequency=200, vsids_multiplier=1.05, c=100, use_decision_heuristics=True, use_restarts=True, 
                 max_lbd=7, max_lbd_multiplier=1.1, use_clause_minimization=True, use_clause_deletion=True) -> None:
        super().__init__(random_decision_frequency, vsids_multiplier, c, use_decision_heuristics, use_restarts)
        self.max_lbd = max_lbd # deletion threshold for learned clauses based on lbd score
        self.max_lbd_multiplier = max_lbd_multiplier # factor to multiply max_lbd with
        self.use_clause_minimization = use_clause_minimization
        self.use_clause_deletion = use_clause_deletion

    # -> override to add deleted_clause_count
    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.lbd_scores = []  # lbd scores of learned clauses, uses same order as self.learned_clauses

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
        # minimize learned clause if possible
        if len(literals_to_delete) > 0:
            self.minimized_clause_count += 1
            learned_clause = [l for l in learned_clause if l not in literals_to_delete]
        return learned_clause

    # -> override to add clause minimization
    def analyze_conflict(self):
        self.current_conflict_count += 1
        learned_clause, new_decision_level, involved_variables = self.get_learned_clause()
        if self.use_clause_minimization: learned_clause = self.minimize_learned_clause(learned_clause)
        if len(learned_clause) > 0:
            self.remember_learned_clause(learned_clause)
            self.update_vsids_scores(involved_variables)
        return new_decision_level
    
    # -> override to also remember lbd score of learned clause 
    def remember_learned_clause(self, learned_clause):
        super().remember_learned_clause(learned_clause)
        if self.use_clause_deletion: self.lbd_scores.append(self.lbd(learned_clause))
    
    # returns lbd score of clause
    def lbd(self,clause):
        unique_decision_levels = set()
        for literal in clause:
            unique_decision_levels.add(self.decision_level_per_assigned_literal[-literal])
        return len(unique_decision_levels)
    
    # removes given learned clause from all data structures
    def remove_clause(self,learned_clause):
        self.known_clauses.remove(learned_clause)
        clause_index = self.learned_clauses.index(learned_clause)
        self.learned_clauses.pop(clause_index)
        self.lbd_scores.pop(clause_index)
        for _, watched_literal_information in self.watched_clauses.items():
            for clause, other_watched_literal in watched_literal_information:
                if clause == learned_clause:
                    watched_literal_information.remove([clause,other_watched_literal])
    
    # applies clause deletion using lbd score
    def delete_learned_clauses(self):
        clauses_to_delete = []
        for i, learned_clause in enumerate(self.learned_clauses):
            lbd = self.lbd_scores[i]
            if lbd > self.max_lbd and lbd > 2:
                self.deleted_clause_count += 1
                clauses_to_delete.append(learned_clause)
        for learned_clause in clauses_to_delete:
            self.remove_clause(learned_clause)
        self.max_lbd *= self.max_lbd_multiplier

    # -> override to add deletion of learned clauses
    def apply_restart(self):
        if self.use_clause_deletion: self.delete_learned_clauses()
        super().apply_restart()

