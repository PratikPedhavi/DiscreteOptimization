#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

    # a trivial algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    value = 0
    weight = 0
    taken = [0]*len(items)

    # Using Recursion
    # value, outlist = optimal_comb(items,capacity,item_count-1,[])
    # taken = [1 if k in outlist else taken[k] for k in range(len(taken))]

    # Using Dynamic Programming
    value, taken = dynamic_prog(items, capacity)

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data

def optimal_comb(items, cap, item, outlist):
    if item == -1:
        return 0, outlist
    elif items[item].weight <= cap:
        cond1 = optimal_comb(items,cap,item-1,outlist)
        cond2 = optimal_comb(items,cap-items[item].weight,item-1,outlist)
        skipped = cond1[0]
        selected = items[item].value + cond2[0]
        if skipped > selected:
            return skipped, cond1[1]
        else:
            return selected, cond2[1] + [item]
    else:
        skipped = optimal_comb(items,cap,item-1,outlist)
        return skipped[0], outlist + skipped[1]

def dynamic_prog(items, cap):
    value_dict = {(i,j):0 for i in range(len(items)+1) for j in range(int(cap)+1)}
    for j in range(int(cap)+1):
        for item in items:
            # if item.index > 0:
            if item.weight <= j:
                value_dict[(item.index+1,j)] = max(value_dict[(item.index, j)], item.value + value_dict[(item.index, j - item.weight)])
            else:
                value_dict[(item.index+1,j)] = value_dict[(item.index,j)]
    # BACKTRACKER
    selection = []
    temp_cap = cap
    for item in items[::-1]:
        # if item.index > 0:
        if value_dict[(item.index+1,temp_cap)] == value_dict[(item.index,temp_cap)]:
            selection.append(0)
        else:
            selection.append(1)
            temp_cap -= item.weight
    return value_dict[(len(items),cap)],selection


if __name__ == '__main__':
    import sys
    # if len(sys.argv) > 1:
    #     file_location = sys.argv[1].strip()
    if 1:
        file_location = r'C:\Users\Pradnya\Documents\Work\Coursera\DiscreteOptimization\Assignments\knapsack\data\ks_50_0'
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')
