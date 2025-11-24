from heapq import heapify, heappop, heappush
from algorithms.subroutines.commons import *
from utilities.time_measure import ExecutionTime
from utilities.print_console import print_end_algorithm

def greedy_degree_removal(signed_graph, signed_degree=True, print_results=True):
    execution_time = ExecutionTime()

    solution = set(signed_graph.nodes_iterator)
    solution_x = build_x(signed_graph, solution)
    solution_objective_function = evaluate_objective_function(signed_graph, solution_x)

    degree = [len(neighbors[0]) - (len(neighbors[1]) if signed_degree else 0) 
              for neighbors in signed_graph.adjacency_list]
    degree_heap = [(d, node) for node, d in enumerate(degree)]
    heapify(degree_heap)

    nodes = solution.copy()
    x = solution_x.copy()

    while degree_heap:
        _, node = heappop(degree_heap)
        
        if node not in nodes:
            continue

        nodes.remove(node)
        x[node] = 0

        for neighbor_type, sign in [(0, -1), (1, 1)]:
            for neighbor in signed_graph.adjacency_list[node][neighbor_type]:
                if neighbor in nodes:
                    if neighbor_type == 0 or signed_degree:
                        degree[neighbor] += sign
                        heappush(degree_heap, (degree[neighbor], neighbor))

        objective_function = evaluate_objective_function(signed_graph, x)
        if objective_function > solution_objective_function:
            solution = nodes.copy()
            solution_x = x.copy()
            solution_objective_function = objective_function

    execution_time.end_algorithm()

    if print_results:
        print_end_algorithm(execution_time.execution_time_seconds, [solution_x], signed_graph, [solution_objective_function])

    return solution, solution_x

# def optimized_greedy_degree_removal(signed_graph, signed_degree=True):
#     execution_time = ExecutionTime()

#     # Initialize solution with all nodes
#     solution = set(signed_graph.nodes_iterator)
#     solution_x = build_x(signed_graph, solution)
#     solution_objective_function = evaluate_objective_function(signed_graph, solution_x)

#     # Compute degree of each node
#     degree = {}
#     degree_heap = []
#     for node, neighbors in enumerate(signed_graph.adjacency_list):
#         degree[node] = len(neighbors[0]) - (len(neighbors[1]) if signed_degree else 0)
#         heappush(degree_heap, (degree[node], node))

#     nodes = solution.copy()
#     x = solution_x.copy()

#     while degree_heap:
#         _, min_degree_node = heappop(degree_heap)
        
#         if min_degree_node not in nodes:
#             continue

#         # Remove node and update neighbors' degrees
#         nodes.remove(min_degree_node)
#         x[min_degree_node] = 0
#         for neighbor_type, sign in [(0, -1), (1, 1)]:
#             for neighbor in signed_graph.adjacency_list[min_degree_node][neighbor_type]:
#                 if neighbor in nodes:
#                     if neighbor_type == 0 or signed_degree:
#                         degree[neighbor] += sign
#                         heappush(degree_heap, (degree[neighbor], neighbor))

#         # Update solution if needed
#         objective_function = evaluate_objective_function(signed_graph, x)
#         if objective_function > solution_objective_function:
#             solution = nodes.copy()
#             solution_x = x.copy()
#             solution_objective_function = objective_function

#     execution_time.end_algorithm()

#     print_end_algorithm(execution_time.execution_time_seconds, [solution_x], signed_graph, [solution_objective_function])

#     return solution, solution_x
