import argparse

def read_cnf():
    parser = argparse.ArgumentParser(description="Read cnf file")
    parser.add_argument("input_file", nargs="?", default="random_cnf.cnf")
    args=parser.parse_args()
    path = args.input_file
    f = open(path, "r")
    lines = f.readlines()
    f.close()
    clauses = []
    for line in lines:
        if line[0] == 'c':
            continue
        if line[0] == 'p':
            continue
        clause = line.split()
        clause = [int(l) for l in clause[:-1]]
        clauses.append(clause)
    return clauses

if __name__ == "__main__":
    print(read_cnf())