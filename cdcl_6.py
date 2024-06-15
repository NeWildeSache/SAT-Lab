from unit_propagate_using_lists import unit_propagate, simplify
from cdcl import cdcl

class cdcl_clause_learning(cdcl):
    def __init__(self) -> None:
        super().__init__()

    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.immediate_predecessors = {}


    def update_conflict_graph(self, unit_clause_indices_and_respective_units):
        # save implications in conflict graph (overwrites old values so no backtrack needed)
        for unit_clause_index, unit_assignment in unit_clause_indices_and_respective_units:
            clause_that_became_unit = self.known_clauses[unit_clause_index]
            implicating_literals = [-literal for literal in clause_that_became_unit if literal != unit_assignment]
            self.immediate_predecessors[unit_assignment] = implicating_literals

        # save possible conflicts in conflict graph (overwrites old values so no backtrack needed)
        if self.conflict_clause != None:
            implicating_literals = [-literal for literal in self.conflict_clause]
            self.immediate_predecessors["conflict"] = implicating_literals


    def propagate(self, formula):
        self.formula, unit_assignments, extra_propagations, unit_clause_indices_and_respective_units = unit_propagate(simplify(formula,self.assignments),return_assignments=True,count_propagations=True,return_unit_clause_indices_and_respective_units=True)
        self.propagation_count += extra_propagations

        if [] in self.formula:
            self.conflict_clause = self.known_clauses[self.formula.index([])]

        self.remember_unit_assignments(unit_assignments)

        self.update_conflict_graph(unit_clause_indices_and_respective_units)

    def analyze_conflict(self):
        # learn clause -> https://efforeffort.wordpress.com/2009/03/09/linear-time-first-uip-calculation/
        learned_clause = []
        stack = sum(self.assignments, [])
        p = "conflict"
        c = 0
        seen = set()
        new_decision_level = 0
        
        while True:
            for q in self.immediate_predecessors[p]:
                if q not in seen:
                    seen.add(q)
                    if q in self.assignments[-1]:
                        c += 1
                    else:
                        decision_level = self.decision_level_per_assigned_literal[q]
                        if decision_level > new_decision_level:
                            new_decision_level = decision_level
                        learned_clause.append(-q)
            while True:
                p = stack.pop()
                if p in seen: break
            c -= 1
            if c == 0: break

        learned_clause.append(-p)
        
        self.learned_clauses.append(learned_clause)
        self.known_clauses.append(learned_clause)

        return new_decision_level


