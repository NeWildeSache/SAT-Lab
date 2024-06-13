from cdcl_6 import cdcl_clause_learning 
from unit_propagate_using_lists import unit_propagate, simplify
import random

class cdcl_watched_literals(cdcl_clause_learning):
    def __init__(self) -> None:
        super().__init__()

    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.watched_clauses = {}
        for literal in self.unassigned_variables:
            self.watched_clauses[literal] = []
            self.watched_clauses[-literal] = []
        for i, clause in enumerate(formula):
            literals_to_watch = random.sample(clause,2)
            self.watched_clauses[literals_to_watch[0]].append(i)
            self.watched_clauses[literals_to_watch[1]].append(i)
        self.assigned_and_not_processed_variables = []

    def decide(self):
        decision_variable = super().decide()
        self.assigned_and_not_processed_variables.insert(0,decision_variable)
    
    def propagate(self, formula):
        unit_assignments = []
        unit_clause_indices_and_respective_units = []

        # propagate
        while len(self.assigned_and_not_processed_variables) > 0:
            self.propagation_count += 1
            new_assignments = self.assigned_and_not_processed_variables
            self.assigned_and_not_processed_variables = []
            self.formula = simplify(formula,new_assignments)

            for literal in new_assignments:
                for clause_index in self.watched_clauses[-literal]:
                    clause = self.formula[clause_index]
                    if clause != "True":
                        # if clause became unit
                        if len(clause) == 1:
                            unit_assignment = clause[0]
                            if (unit_assignment not in unit_assignments and -unit_assignment not in unit_assignments):
                                unit_assignments.append(unit_assignment)
                            unit_clause_indices_and_respective_units.append([clause_index, unit_assignment])
                            if unit_assignment not in self.assigned_and_not_processed_variables:
                                self.assigned_and_not_processed_variables.append(clause[0])
                        else:
                            for literal in clause:
                                if clause_index not in self.watched_clauses[literal]:
                                    self.watched_clauses[literal].append(clause_index)

                self.watched_clauses[-literal] = []
                
            # Falls beide Literale belegt sind, und eins ist falsch: Dessen decision-level darf nicht niedriger sein als das erfüllte ????

        # update conflict graph
        self.update_conflict_graph(unit_clause_indices_and_respective_units)

        self.remember_unit_assignments(unit_assignments)

