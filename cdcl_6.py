from unit_propagate_using_lists import unit_propagate, simplify
from cdcl import cdcl

class cdcl_clause_learning(cdcl):
    def __init__(self) -> None:
        super().__init__()

    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.immediate_predecessors = {}
        for literal in self.unassigned_variables:
            self.immediate_predecessors[literal] = []
            self.immediate_predecessors[-literal] = []
        self.immediate_predecessors["conflict"] = []


    def update_conflict_graph(self, unit_clause_indices_and_respective_units):
        # save implications in conflict graph
        for unit_clause_index, unit_assignment in unit_clause_indices_and_respective_units:
            clause_that_became_unit = self.known_clauses[unit_clause_index]
            # implicating_literals = [-literal for literal in clause_that_became_unit if literal != unit_assignment]
            # self.immediate_predecessors[unit_assignment] = implicating_literals
            for literal in clause_that_became_unit:
                if literal != unit_assignment:
                    self.immediate_predecessors[unit_assignment].append(-literal)

        # save possible conflicts in conflict graph
        if [] in self.formula:
            conflict_clause = self.known_clauses[self.formula.index([])]
            # implicating_literals = [-literal for literal in conflict_clause]
            # self.immediate_predecessors["conflict"] = implicating_literals
            for literal in conflict_clause:
                self.immediate_predecessors["conflict"].append(-literal)


    def propagate(self, formula):
        self.formula, unit_assignments, extra_propagations, unit_clause_indices_and_respective_units = unit_propagate(simplify(formula,self.assignments),return_assignments=True,count_propagations=True,return_unit_clause_indices_and_respective_units=True)
        self.propagation_count += extra_propagations

        self.remember_unit_assignments(unit_assignments)

        self.update_conflict_graph(unit_clause_indices_and_respective_units)
        

    def analyze_conflict(self):
        # learn clause -> https://efforeffort.wordpress.com/2009/03/09/linear-time-first-uip-calculation/
        learned_clause = []
        stack = sum(self.assignments, [])
        p = "conflict"
        c = 0
        seen = set()
        
        while True:
            for q in self.immediate_predecessors[p]:
                if q not in seen:
                    seen.add(q)
                    if q in self.assignments[-1]:
                        c += 1
                    else:
                        learned_clause.append(-q)
            while True:
                p = stack.pop()
                if p in seen: break
            c -= 1
            if c == 0: break

        learned_clause.append(-p)
        
        self.learned_clauses.append(learned_clause)
        self.known_clauses.append(learned_clause)

        # get new decision level -> second highest decision level in learned clause
        new_decision_level = 0
        for i, decision_level_assignments in enumerate(reversed(self.assignments[:-1])):
            intersection = [item for item in decision_level_assignments if item in learned_clause]
            if len(intersection) > 0:
                new_decision_level = len(self.assignments)-(i+2)

        return new_decision_level
    
    def backtrack(self, new_decision_level):
        self.conflict_clause = None
        for _ in range(self.decision_level-new_decision_level):
            decision_level_assignments = self.assignments.pop()
            for literal in decision_level_assignments:
                self.immediate_predecessors[literal] = []
                self.immediate_predecessors["conflict"] = []
                self.unassigned_variables.append(abs(literal))
        self.decision_level = new_decision_level


