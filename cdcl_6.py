from unit_propagate_using_lists import unit_propagate, simplify
from cdcl import cdcl
import networkx as nx


class cdcl_clause_learning(cdcl):
    def __init__(self) -> None:
        super().__init__()

    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.conflict_graph = nx.DiGraph()

    def update_conflict_graph(self, unit_clause_indices_and_respective_units):
        # save implications in conflict graph
        for unit_clause_index, unit_assignment in unit_clause_indices_and_respective_units:
            clause_that_became_unit = self.known_clauses[unit_clause_index]
            implicating_literals = [-literal for literal in clause_that_became_unit if literal != unit_assignment]
            for literal in implicating_literals:
                self.conflict_graph.add_edge(literal,unit_assignment)

        # save possible conflicts in conflict graph
        if [] in self.formula:
            conflict_clause_index = self.formula.index([])
            conflict_clause = self.known_clauses[conflict_clause_index]
            for literal in conflict_clause:
                self.conflict_graph.add_edge(-literal,"conflict")

    def propagate(self, formula):
        self.formula, unit_assignments, extra_propagations, unit_clause_indices_and_respective_units = unit_propagate(simplify(formula,self.assignments),return_assignments=True,count_propagations=True,return_unit_clause_indices_and_respective_units=True)
        self.propagation_count += extra_propagations

        self.update_conflict_graph(unit_clause_indices_and_respective_units)

        self.remember_unit_assignments(unit_assignments)

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

        # get new decision level
        new_decision_level = 0
        for i, decision_level_assignments in enumerate(reversed(self.assignments[:-1])):
            intersection = [item for item in decision_level_assignments if item in learned_clause]
            if len(intersection) > 0:
                new_decision_level = len(self.assignments)-(i+2)

        return new_decision_level
    
    def backtrack(self, new_decision_level):
        for _ in range(self.decision_level-new_decision_level):
            decision_level_assignments = self.assignments.pop()
            for literal in decision_level_assignments:
                try: self.conflict_graph.remove_node(literal)
                except: pass
                self.unassigned_variables.append(abs(literal))
        self.decision_level = new_decision_level


