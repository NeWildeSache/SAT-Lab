from itertools import combinations
import argparse
from random_cnf import convert_to_dimacs
import sys

def pigeonhole_cnf(n):
    # n+1 pigeons, n holes
    # x(i,j) -> pigeon i is in hole j
    # indices start at 0

    # variable naming: x(i,j) = i*n + j + 1
    # -> each pigeon gets n numbers, offset by 1 so first variable is 1 and not 0
    def get_pigeonhole_variable(i,j):
        return i*n + j + 1

    pigeonhole = []

    # each pigeon must be within one hole
    for i in range(n+1):
        clause = []
        for j in range(n):
            clause.append(get_pigeonhole_variable(i,j))
        pigeonhole.append(clause)

    # only one pigeon per hole
    for j in range(n):
        for i1, i2 in combinations(range(n+1),2):
            pigeonhole.append([-get_pigeonhole_variable(i1,j),-get_pigeonhole_variable(i2,j)])

    return pigeonhole

def pebbling_cnf(n):
    # n nodes, 2 colors
    # x(v,c) -> node v has color c
    # indices start at 0

    # variable naming: x(v,c) = v*2 + c + 1
    # -> each node gets 2 numbers, offset by 1 so first variable is 1 and not 0
    def get_pebbling_variable(v,c):
        return v*2 + c + 1

    # adjust n to fit pyramidal graph
    k=1
    while k*(k+1)/2 < n:
        k+=1
    n = int(k*(k+1)/2)

    # final formula
    pebbling = []

    # remember predecessors
    predecessors = {}
    nodes_per_row = []
    k = 4
    largest_node_in_current_row = 0
    for num_nodes_in_row in reversed(range(1,k+1)):
        nodes_per_row.append(list(range(largest_node_in_current_row,largest_node_in_current_row+num_nodes_in_row)))
        largest_node_in_current_row += num_nodes_in_row

    for row_index, row in enumerate(nodes_per_row):
        if row_index == 0: continue
        for node_index, node in enumerate(row):
            predecessors[node] = [nodes_per_row[row_index-1][node_index],nodes_per_row[row_index-1][node_index+1]]

    # each source node must have one of the colors
    for v in range(k):
        pebbling.append([get_pebbling_variable(v,0),get_pebbling_variable(v,1)])

    # predecessors must have same color as successors
    for v in range(k,n):
        pred_1, pred_2 = predecessors[v]
        pebbling.append([-get_pebbling_variable(pred_1,0),-get_pebbling_variable(pred_2,1),get_pebbling_variable(v,0),get_pebbling_variable(v,1)])
        pebbling.append([-get_pebbling_variable(pred_1,1),-get_pebbling_variable(pred_2,0),get_pebbling_variable(v,0),get_pebbling_variable(v,1)])

    # final node can't have either color
    pebbling.append([-get_pebbling_variable(n-1,0)])
    pebbling.append([-get_pebbling_variable(n-1,1)])

    return pebbling


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="special formula generator, supports 'pigeonhole','pebbling' as arguments for type")
    parser.add_argument("type", nargs="?",default="pigeonhole")
    parser.add_argument("n", nargs="?", default="10")
    args=parser.parse_args()
    type = args.type
    n = int(args.n)
    if type == "pigeonhole":
        formula = pigeonhole_cnf(n)
        num_variables = n+1*n
    elif type == "pebbling":
        num_variables = n*2
        formula = pebbling_cnf(n)
    else:
        print("Unsupported type!")
        sys.exit()
    output = convert_to_dimacs(formula,num_variables,len(formula))
    print(output)
    # write to file
    f = open(f"{type}.cnf", "w")
    f.write(output)
    f.close()