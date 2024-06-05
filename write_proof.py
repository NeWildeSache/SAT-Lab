# writes proof in DRAT format
def write_proof(learned_clauses, sat, num_literals):
    num_clauses = len(learned_clauses) + 1 if not sat else len(learned_clauses)

    file_name = "proof.drat"
    with open(file_name, "w") as file:
        file.write("p cnf " + str(num_literals) + " " + str(num_clauses) + "\n")
        for learned_clause in learned_clauses:
            file.write(" ".join(map(str,learned_clause)) + " 0\n")
        if not sat:
            file.write("0\n")