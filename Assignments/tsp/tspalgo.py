import os
import math
from time import time
from platform import node
from turtle import distance 
# from solver import length
from itertools import combinations

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

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

def local_search(points):
    start_node = 0
    # distance_matrix = compute_euclidean_distance_matrix(points)
    tour = [start_node]
    neighbors = list(range(len(points)))
    neighbors.remove(start_node)
    node_from = start_node
    while len(tour) < len(points) and neighbors:
        closest = math.inf
        closest_node = None
        for node in neighbors[:4000]:
            edge_len = length(points[node_from],points[node])
            if closest > edge_len:
                closest_node = node
                closest = edge_len
        node_from = closest_node
        # dist_dict = {node:distance_matrix[node_from][node] }
        # node_from = min(dist_dict, key=dist_dict.get)
        tour.append(node_from)
        neighbors.remove(node_from)
    tour.append(start_node)
        # print(tour)
    # new_tour = improve_solution_2opt(points,tour)
    tour = list(range(len(points))) + [0]
    new_tour = improve_solution_3opt(points,tour)
    return new_tour[:-1]

def improve_solution_3opt(points, tour):
    tour_len = sum([length(points[node1], points[node2]) for node1,node2 in zip(tour,tour[1:])])
    count = 0
    t = time()
    progress =  True
    t_threshold = 100
    THRESHOLD = 10 ** -4
    while progress:
        progress = False
        if count > 200 or time() - t > t_threshold: #(tour_len - new_len <= THRESHOLD) and
            break
        print(tour)
        for node1 in range(1, len(tour)-5):
            for node2 in range(node1+2, len(tour)-3):
                for node3 in range(node2+2, len(tour)-1):
                    print(node1,node2,node3)
                    new_tour, new_len = swap_3opt(node1, node2, node3, tour, tour_len, points)
                    if tour_len - THRESHOLD > new_len:
                        tour = new_tour
                        tour_len = new_len
                        progress = True
                        break
                    if time() - t > t_threshold:
                        break
                if progress:
                    break
            if progress:
                break
        count += 1
    return tour

def swap_3opt(node1, node2, node3, tour, tour_len, points):
    A = points[tour[node1 - 1]]
    B = points[tour[node1]]
    C = points[tour[node2 - 1]]
    D = points[tour[node2]]
    E = points[tour[node3 - 1]]
    F = points[tour[node3]]
    d0 = length(A,B) + length(C,D) + length(E,F)
    d1 = length(A,B) + length(C,E) + length(D,F)
    d2 = length(A,C) + length(B,D) + length(E,F)
    d3 = length(F,B) + length(C,D) + length(E,A)
    d4 = length(A,D) + length(E,B) + length(C,F)
    orig_nodes = len(tour)
    orig_tour = tour

    if d0 > d1:
        tour[node2:node3] = tour[node2:node3][::-1]
        tour_len = tour_len - d0 + d1
    elif d0 > d2:
        tour[node1:node2] = tour[node1:node2][::-1]
        tour_len = tour_len - d0 + d2
    elif d0 > d3:
        tour = tour[node3:][::-1] + tour[node2:node3] + tour[:node1][::-1]
        tour_len = tour_len - d0 + d3
    elif d0 > d4:
        tmp = tour[node2:node3] + tour[node1:node2]
        tour[node1:node3] = tmp
        tour_len = tour_len - d0 + d4
    if len(tour) < orig_nodes:
        print()
    return tour, tour_len

def improve_solution_2opt(points, tour):
    progress = True
    THRESHOLD = 10 ** -4
    tour_len = sum([length(points[node1], points[node2]) for node1,node2 in zip(tour,tour[1:])])
    new_len = 0
    count = 0
    t = time()
    multip = 200000
    t_threshold = 200
    while progress:
        progress = False
        if count > 200 or time() - t > t_threshold: #(tour_len - new_len <= THRESHOLD) and
            break
        for node1, node2 in list(combinations(range(1,min(multip,len(tour)-1)),2)):
        # for node1, node2 in list(combinations(range(1,len(tour)-1),2))[:multip]:
            new_tour, new_len = swap_2opt(node1, node2, tour, tour_len, points)
            if tour_len - THRESHOLD > new_len:
                tour = new_tour
                tour_len = new_len
                progress = True
                break
            if time() - t > t_threshold:
                break
        count += 1
    return tour

def swap_2opt(start, end, tour, tour_len, points):
    new_tour = tour[:start] + tour[start:end+1][::-1] + tour[end+1:]
    try:
        tourL = tour_len - (length(points[tour[start-1]], points[tour[start]]) + length(points[tour[end]], points[tour[end+1]])) \
                + (length(points[tour[start-1]], points[tour[end]]) + length(points[tour[start]], points[tour[end+1]]))
    except:
        print()
    # tourL = sum([distance_matrix[node1][node2] for node1,node2 in zip(new_tour,new_tour[1:])])    
    return new_tour, tourL

def tour_length(tour):
    return 

def choose_closest():
    return

def neighbor_search():
    return