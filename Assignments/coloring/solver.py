#!/usr/bin/python
# -*- coding: utf-8 -*-

from turtle import color
from ortools.sat.python import cp_model
import networkx as nx

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    # build a trivial solution
    # every node has its own color
    # solution = range(0, node_count)
    color_count,solution = greedy(node_count,edges)
    # solution = mip(edges,node_count,color_count)
    # print(max(solution))

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def create_graph(node_count, edges):
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(edges)
    return graph

def greedy(node_count,edges):
    graph = create_graph(node_count, edges)
    strategy = [nx.coloring.strategy_largest_first, nx.coloring.strategy_saturation_largest_first]
    color_count, color_list = node_count, []
    for strat in strategy:
        temp_color_count, temp_color_list = run_strategy(graph,strat)
        if temp_color_count < color_count:
            color_count = temp_color_count
            color_list = temp_color_list
    return color_count, [color_list[i] for i in range(node_count)]

def run_strategy(graph,strategy):
    color_list = nx.coloring.greedy_color(G=graph, strategy=strategy)
    color_count = max(color_list.values()) + 1
    return color_count,color_list

def mip(edges, node_count, color_count):
    model = cp_model.CpModel()

    # VARIABLES 
    node_color = {}
    for node in range(node_count):
        for color in range(color_count):
            node_color[(node,color)] = model.NewBoolVar('{}_{}'.format(node,color))
    
    colors = {}
    for color in range(color_count):
        colors[color] = model.NewBoolVar('{}'.format(color))
    
    # CONSTRAINTS
    for edge in edges:
        for color in range(color_count):
            model.Add(node_color[(edge[0],color)] + node_color[(edge[1],color)] <= colors[color])
    
    for node in range(node_count):
        model.Add(sum([node_color[(node,color)] for color in range(color_count)]) == 1)
    
    model.Minimize(sum([(color+1)*colors[color] for color in range(color_count)]))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # colors_used = sum([solver.BooleanValue(colors[color]) for color in range(node_count)])
        colors_used = []
        for node in range(node_count):
            for color in range(color_count):
                if solver.BooleanValue(node_color[(node,color)]):
                    colors_used.append(color)
        # print('Total unique colors used: {}'.format(colors_used))
    return colors_used

import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
    # if 1:
    #     file_location = './coloring/data/gc_250_7'
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

