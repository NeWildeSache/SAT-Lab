from solvers.unit_propagate import unit_propagate, simplify
from solvers.cdcl import cdcl
import copy

class cdcl_clause_learning(cdcl):
    def __init__(self) -> None:
        super().__init__()

    # -> override to add immediate-predecessors-dictionary (represents conflict graph)
    def reset_variables(self, formula):
        super().reset_variables(formula)
        self.immediate_predecessors = {}

    # adds unit assignments to conflict graph
    # also adds "conflict" node if conflict occurs
    def update_conflict_graph(self, unit_clause_information=[]):
        # save implications in conflict graph
        for clause_that_became_unit, unit_assignment in unit_clause_information:
            implicating_literals = [-literal for literal in clause_that_became_unit if literal != unit_assignment]
            self.immediate_predecessors[unit_assignment] = implicating_literals

        # save possible conflicts in conflict graph
        if self.conflict_clause != None:
            implicating_literals = [-literal for literal in self.conflict_clause]
            self.immediate_predecessors["conflict"] = implicating_literals

    # -> override to also update conflict graph
    def propagate(self, formula):
        # unit propagate
        self.formula, unit_assignments, extra_propagations, unit_clause_indices_and_respective_units = unit_propagate(
            simplify(formula,self.assignments, placeholders_for_fulfilled_clauses=True),
            return_assignments=True,count_propagations=True,return_unit_clause_indices_and_respective_units=True)
        self.propagation_count += extra_propagations

        self.remember_assignments(unit_assignments)

        # set conflict clause if conflict occurs
        if [] in self.formula:
            self.conflict_clause = self.known_clauses[self.formula.index([])]

        # update conflict graph
        unit_clause_information = [[self.known_clauses[index], unit_assignment] for index, unit_assignment in unit_clause_indices_and_respective_units]
        self.update_conflict_graph(unit_clause_information)

    # -> override to also backtrack conflict graph
    def backtrack(self, new_decision_level):
        # backtrack decision_level_per_assigned_literal
        for literal, decision_level in list(self.decision_level_per_assigned_literal.items()):
            if decision_level > new_decision_level:
                del self.decision_level_per_assigned_literal[literal]
        for _ in range(self.decision_level-new_decision_level):
            # backtrack assignments
            decision_level_assignments = self.assignments.pop()
            for literal in decision_level_assignments:
                # backtrack conflict graph
                self.immediate_predecessors[literal] = []
                for predecessors in self.immediate_predecessors.values():
                    if literal in predecessors:
                        predecessors.remove(literal)
                # backtrack unassigned variables 
                self.unassigned_variables.append(abs(literal))
        self.decision_level = new_decision_level
        self.conflict_clause = None

    # returns new learned clause, new decision level and list of involved variables using 1st UIP learning
    def get_learned_clause(self):
        # algorithm -> https://efforeffort.wordpress.com/2009/03/09/linear-time-first-uip-calculation/
        learned_clause = []
        stack = copy.deepcopy(self.assignments[-1])
        current_node = "conflict"
        counter = 0
        seen = set()
        new_decision_level = 0
        involved_variables = []
        
        while True:
            for predecessor in self.immediate_predecessors[current_node]:
                if predecessor not in seen:
                    seen.add(predecessor)
                    if predecessor in self.assignments[-1]:
                        counter += 1
                        involved_variables.append(predecessor)
                    else:
                        decision_level = self.decision_level_per_assigned_literal[predecessor]
                        if decision_level > new_decision_level:
                            new_decision_level = decision_level
                        learned_clause.append(-predecessor)
                        involved_variables.append(-predecessor)
            while True:
                current_node = stack.pop()
                if current_node in seen: break
            counter -= 1
            if counter == 0: break
        learned_clause.append(-current_node)

        return learned_clause, new_decision_level, involved_variables

    # -> override to use first_uip learning
    def analyze_conflict(self):
        learned_clause, new_decision_level, _ = self.get_learned_clause()
        self.remember_learned_clause(learned_clause)
        return new_decision_level


# run this from parent folder using "python -m solvers.cdcl_clause_learning <path>"
if __name__ == "__main__":
    import argparse
    from .utils import read_dimacs
    parser = argparse.ArgumentParser(description="CDCL SAT Solver with Clause Learning")
    parser.add_argument("path", nargs="?", default="random_cnf.cnf")
    args=parser.parse_args()
    path = args.path
    formula = read_dimacs(path)
    solver = cdcl_clause_learning()
    stats = solver.solve(formula)
    print("s", "SATISFIABLE" if stats["SAT"] else "UNSATISFIABLE")
    if stats["SAT"]:
        print("v", " ".join([str(l) for l in stats["model"]]))
    print("c", "Runtime:", stats["runtime"])
    print("c", "Number of Decisions:", stats["decision_count"])
    print("c", "Number of Propagations:", stats["propagation_count"])
    print("c", "Number of Conflicts:", stats["conflict_count"])
    print("c", "Number of Learned Clauses:", stats["learned_clause_count"])
    print("c", "Number of Restarts:", stats["restart_count"])
    print("c", "Number of Deleted Clauses:", stats["deleted_clause_count"])
    print("c", "Number of Minimized Clauses:", stats["minimized_clause_count"])