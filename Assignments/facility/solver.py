#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def facility_mip(facilities, customers):
    solution = [-1]*len(customers)
    used = [0]*len(facilities)

    solver = pywraplp.Solver.CreateSolver('SCIP')

    facility_var = {}
    allocation = {}
    if len(customers) <= 800:
        max_dist = math.inf
    else:
        max_dist = 100000
    # max_dist = 0 # COMMENT OUT LATER
    for facility in facilities:
        facility_var[facility.index] = solver.BoolVar('{}'.format(facility.index))

    for customer in customers:
        count = 0
        for facility in sorted(facilities, key = lambda x: x.setup_cost):
            temp_dist = length(facility.location, customer.location)
            if max_dist > temp_dist:
                # max_dist = temp_dist # COMMENT OUT LATER
                allocation[(facility.index, customer.index)] = solver.BoolVar('{}_{}'.format(facility.index, customer.index))
                count += 1
            if count > 200:
                break
        # if count == 0:
        #     print(customer)

    # CONSTRAINTS  
    for facility in facilities:
        constraint_expr = [customer.demand*allocation[(facility.index,customer.index)] for customer in customers if (facility.index,customer.index) in allocation.keys()]
        solver.Add(sum(constraint_expr) <= facility.capacity*facility_var[facility.index])
    
    for customer in customers:
        constraint_expr = [allocation[(facility.index, customer.index)] for facility in facilities if (facility.index,customer.index) in allocation.keys()]
        solver.Add(sum(constraint_expr) == 1)

    obj_expr = [facility.setup_cost*facility_var[facility.index] for facility in facilities]
    dist_expr = [length(facility.location, customer.location) * allocation[(facility.index, customer.index)] for facility in facilities \
                                for customer in customers if (facility.index,customer.index) in allocation.keys()]
    solver.Minimize(solver.Sum(obj_expr) + solver.Sum(dist_expr))

    solver.set_time_limit(300000)

    status = solver.Solve()
    
    if status == solver.OPTIMAL or status == solver.FEASIBLE:
        for facility in facilities:
            customer_served = []
            if facility_var[facility.index].solution_value():
                # print("Facility {} is setup".format(facility.index))
                used[facility.index] = 1
            for customer in customers:
                if (facility.index,customer.index) in allocation.keys():
                    if allocation[(facility.index,customer.index)].solution_value():
                        customer_served.append(customer.index)
                        solution[customer.index] = facility.index
        # print("Customers served: {}".format(customer_served))
    
    return solution, used

def facility_loc(facilities, customers):
    solution = [-1]*len(customers)
    used = [0]*len(facilities)

    model = cp_model.CpModel()

    # VARIABLES
    allocation ={}
    facility_vars = {}
    for facility in facilities:
        for customer in customers:
            allocation[(facility.index,customer.index)] = model.NewBoolVar('{}_{}'.format(facility.index,customer.index))
    
    for facility in facilities:
        facility_vars[facility.index] = model.NewBoolVar('{}'.format(facility.index))
    
    # COSNTRAINTS

    # Capacity constraints
    for facility in facilities:
        model.Add(sum([customer.demand*allocation[(facility.index,customer.index)] for customer in customers]) <= facility.capacity*facility_vars[facility.index])
    
    # allocation constraints
    for customer in customers:
        model.Add(sum([allocation[(facility.index,customer.index)] for facility in facilities]) == 1) 

    model.Minimize(sum([facility.setup_cost*facility_vars[facility.index] for facility in facilities]))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Objective Value: {}'.format(solver.ObjectiveValue()))
        for facility in facilities:
            customer_served = []
            if solver.BooleanValue(facility_vars[facility.index]):
                print("Facility {} is setup".format(facility.index))
            for customer in customers:
                if solver.BooleanValue(allocation[(facility.index,customer.index)]):
                    customer_served.append(customer.index)
            print("Customers served: {}".format(customer_served))    

    return solution, used

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    # build a trivial solution
    # pack the facilities one by one until all the customers are served

    solution, used = facility_mip(facilities, customers)

    if 0:
        solution = [-1]*len(customers)
        capacity_remaining = [f.capacity for f in facilities]

        facility_index = 0
        for customer in customers:
            if capacity_remaining[facility_index] >= customer.demand:
                solution[customer.index] = facility_index
                capacity_remaining[facility_index] -= customer.demand
            else:
                facility_index += 1
                assert capacity_remaining[facility_index] >= customer.demand
                solution[customer.index] = facility_index
                capacity_remaining[facility_index] -= customer.demand

        used = [0]*len(facilities)
        for facility_index in solution:
            used[facility_index] = 1

    # calculate the cost of the solution
    obj = sum([f.setup_cost*used[f.index] for f in facilities])
    for customer in customers:
        obj += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    import sys
    # if len(sys.argv) > 1:
    #     file_location = sys.argv[1].strip()
    if 1:
        file_location = r'C:\Users\Pradnya\Documents\Work\Coursera\DiscreteOptimization\Assignments\facility\data\fl_500_7'
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

