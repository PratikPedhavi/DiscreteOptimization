#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
# import networkx as nx
from collections import namedtuple
from itertools import combinations
import tspalgo
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp
# from ortools.sat.python import cp_model
# import matplotlib.pyplot as plt

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # build a trivial solution
    # visit the nodes in the order they appear in the file
    # solution = range(0, nodeCount)
    # solution = graph_tour(points)
    # solution = or_tour(points)
    # solution = mip_tour(points)
    print()
    solution = tspalgo.local_search(points)

    # calculate the length of the tour
    obj = length(points[solution[-1]], points[solution[0]])
    for index in range(0, nodeCount-1):
        obj += length(points[solution[index]], points[solution[index+1]])

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def graph_tour(points):
    G = nx.Graph()
    # G.add_nodes_from(points)
    for k,i in enumerate(points):
        G.add_node(k,pos=(i.x, i.y))
    edges = list(combinations(list(range(len(points))),2))
    weights = list(map(lambda x: length(points[x[0]],points[x[1]]),edges))
    for k,i in enumerate(edges):
        G.add_edge(i[0],i[1],weight=weights[k])
    SA_tsp = nx.approximation.simulated_annealing_tsp
    method = lambda G, wt: SA_tsp(G, "greedy",temp=500)
    tour = nx.approximation.traveling_salesman_problem(G, method=method)
    return tour[:-1]

def plotter(G):
    subax1 = plt.subplot(121)
    # nx.draw(G, with_labels=True)
    positions = nx.spring_layout(G)
    nx.draw(G,positions,with_labels=True)
    weights = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G,positions,edge_labels=weights)
    plt.show()
    return

def create_data_model(points):
    data = {}
    data['locations'] = [(point.x,point.y) for point in points]
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data

def compute_euclidean_distance_matrix(locations):
    """Creates callback to return distance between points."""
    distances = {}
    for from_counter, from_node in enumerate(locations):
        distances[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter:
                distances[from_counter][to_counter] = 0
            else:
                # Euclidean distance
                distances[from_counter][to_counter] = length(from_node,to_node)
    return distances

def or_tour(points):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(points)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['locations']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    distance_matrix = compute_euclidean_distance_matrix(points)
    
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 10
    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    tour = convert_solution(manager, routing, solution)
    return tour

def convert_solution(manager, routing, solution):
    """Prints solution on console."""
    index = routing.Start(0)
    tour = [manager.IndexToNode(index)]
    while not routing.IsEnd(index):
        index = solution.Value(routing.NextVar(index))
        tour.append(manager.IndexToNode(index))
    return tour[:-1]

def mip_tour(points):
    data = create_data_model(points)

    distance_matrix = compute_euclidean_distance_matrix(points)
    
    model = cp_model.CpModel()

    edges = {}
    for node_from in range(len(points)):
        for node_to in range(len(points)):
            if node_from != node_to:
                edges[node_from,node_to] = model.NewBoolVar('{}_{}'.format(node_from, node_to))

    # CONSTRAINTS
    for node_from in range(len(points)):
        model.Add(sum([edges[node_from,node_to] for node_to in range(len(points)) if node_from != node_to]) == 1)
    for node_to in range(len(points)):
        model.Add(sum([edges[node_from,node_to] for node_from in range(len(points)) if node_from != node_to]) == 1)
    
    travel_distance = sum([distance_matrix[node_from][node_to] * edges[node_from,node_to] 
                            for node_from in range(len(points)) for node_to in range(len(points)) if node_from != node_to])

    model.Minimize(travel_distance)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        node_from = 0
        node_to = None
        tour = [node_from]
        while len(tour) < len(points):
            for next_node in range(len(points)):
                if node_from != next_node:
                    if solver.BooleanValue(edges[node_from,next_node]):
                        node_from = next_node
                        tour.append(next_node)
                        break
    return tour

import sys

if __name__ == '__main__':
    import sys
    # if len(sys.argv) > 1:
    #     file_location = sys.argv[1].strip()
    if 1:
        file_location = r'C:\Users\Pradnya\Documents\Work\Coursera\DiscreteOptimization\Assignments\tsp\data\tsp_10_1'
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

