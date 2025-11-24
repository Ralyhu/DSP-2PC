from collections import defaultdict, deque
from algorithms.subroutines.commons import *
from algorithms.eigensign import eigensign_binary
from utilities.time_measure import ExecutionTime
from utilities.print_console import print_end_algorithm

def greedy2PC(signed_graph, eigensign_solution, print_results=True):
    execution_time = ExecutionTime()
    
    # Initialize solution with all nodes
    nodes = set(i for i, value in enumerate(eigensign_solution) if value != 0)
    #solution_objective_function = evaluate_objective_function(signed_graph, eigensign_solution)
    
    # Compute the eigensign degree of each node
    degree = {}
    inconsistent_degree = {}
    degree_lists = defaultdict(set)
    max_inconsistent_degree = 0
    total_degree = 0.0

    for node in nodes:
        consistent_degree = 0
        inconsistent_degree[node] = 0
        for neighbor_type in [0, 1]:
            for neighbor in signed_graph.adjacency_list[node][neighbor_type]:
                if neighbor in nodes:
                    if eigensign_solution[node] == eigensign_solution[neighbor]:
                        if neighbor_type == 0:  # positive edge
                            consistent_degree += 1
                        else:  # negative edge
                            inconsistent_degree[node] += 1
                    else:
                        if neighbor_type == 0:  # positive edge
                            inconsistent_degree[node] += 1
                        else:  # negative edge
                            consistent_degree += 1
        
        degree[node] = consistent_degree - inconsistent_degree[node]
        degree_lists[degree[node]].add(node)
        total_degree += degree[node]
    
    # Pick a lowest eigensign degree node
    x = eigensign_solution.copy()
    current_density = total_degree / len(nodes)

    #assert current_density == solution_objective_function

    best_density = current_density
    best_solution = nodes.copy()
    best_solution_x = x.copy()

    min_degree = min(degree_lists.keys())
    while nodes:
        while not degree_lists[min_degree]:
            min_degree += 1

        node = degree_lists[min_degree].pop()
        nodes.remove(node)

        # Update the solution
        x[node] = 0
        total_degree -= (2 * degree[node])
        current_density = total_degree / len(nodes) if nodes else 0

        # Update max_inconsistent_degree
        max_inconsistent_degree = max(max_inconsistent_degree, inconsistent_degree[node])

        # Update the eigensign degree of its neighbors
        for neighbor_type in [0, 1]:
            for neighbor in signed_graph.adjacency_list[node][neighbor_type]:
                if neighbor in nodes:
                    old_degree = degree[neighbor]
                    degree_lists[old_degree].remove(neighbor)

                    if eigensign_solution[node] == eigensign_solution[neighbor]:
                        if neighbor_type == 0:  # positive edge
                            degree[neighbor] -= 1
                        else:  # negative edge
                            degree[neighbor] += 1
                            inconsistent_degree[neighbor] -= 1
                    else:
                        if neighbor_type == 0:  # positive edge
                            degree[neighbor] += 1
                            inconsistent_degree[neighbor] -= 1
                        else:  # negative edge
                            degree[neighbor] -= 1

                    degree_lists[degree[neighbor]].add(neighbor)
                    min_degree = min(min_degree, degree[neighbor])


        if current_density > best_density:
            best_density = current_density
            best_solution = nodes.copy()
            best_solution_x = x.copy()

    execution_time.end_algorithm()

    if print_results:
        print_end_algorithm(execution_time.execution_time_seconds, [best_solution_x], signed_graph, [best_density])

    return best_solution, best_solution_x, max_inconsistent_degree


def greedy2PC_plus_plus(signed_graph, eigensign_solution, T, print_results=True, use_convergence=False, convergence_threshold=0.001):
    execution_time = ExecutionTime()

    best_solution = None
    best_solution_x = None
    best_objective_function = float('-inf')
    overall_max_inconsistent_degree = 0
    previous_objective = None

    # Initialize l_v for each node
    l_v = {node: 0 for node in signed_graph.nodes_iterator}

    iteration = 0
    while True:
        # Initialize solution with all nodes
        solution = set(signed_graph.nodes_iterator)
        solution_x = build_x(signed_graph, solution)
        solution_objective_function = evaluate_objective_function(signed_graph, solution_x)

        # Compute the eigensign degree of each node
        degree = {}
        inconsistent_degree = {}
        degree_sets = defaultdict(set)
        max_inconsistent_degree = 0

        for node in signed_graph.nodes_iterator:
            consistent_degree = 0
            inconsistent_degree[node] = 0
            for neighbor_type in [0, 1]:
                for neighbor in signed_graph.adjacency_list[node][neighbor_type]:
                    if eigensign_solution[node] == eigensign_solution[neighbor]:
                        if neighbor_type == 0:  # positive edge
                            consistent_degree += 1
                        else:  # negative edge
                            inconsistent_degree[node] += 1
                    else:
                        if neighbor_type == 0:  # positive edge
                            inconsistent_degree[node] += 1
                        else:  # negative edge
                            consistent_degree += 1
            
            degree[node] = consistent_degree - inconsistent_degree[node] + l_v[node]
            degree_sets[degree[node]].add(node)

        # Pick a lowest eigensign degree node
        nodes = solution.copy()
        x = solution_x.copy()
        while degree_sets:
            lowest_degree = min(degree_sets.keys())
            while degree_sets[lowest_degree]:
                node = degree_sets[lowest_degree].pop()

                l_v[node] = lowest_degree

                # Update max_inconsistent_degree
                max_inconsistent_degree = max(max_inconsistent_degree, inconsistent_degree[node])

                # Update the eigensign degree of its neighbors
                for neighbor_type in [0, 1]:
                    for neighbor in signed_graph.adjacency_list[node][neighbor_type]:
                        if neighbor in nodes:
                            old_degree = degree[neighbor]
                            degree_sets[old_degree].remove(neighbor)

                            if eigensign_solution[node] == eigensign_solution[neighbor]:
                                if neighbor_type == 0:  # positive edge
                                    degree[neighbor] -= 1
                                else:  # negative edge
                                    degree[neighbor] += 1
                                    inconsistent_degree[neighbor] -= 1
                            else:
                                if neighbor_type == 0:  # positive edge
                                    degree[neighbor] += 1
                                    inconsistent_degree[neighbor] -= 1
                                else:  # negative edge
                                    degree[neighbor] -= 1

                            degree_sets[degree[neighbor]].add(neighbor)
                            lowest_degree = min(lowest_degree, degree[neighbor])

                # Remove the node from the current set of nodes
                nodes.remove(node)

                # Update the solution if needed
                x[node] = 0
                objective_function = evaluate_objective_function(signed_graph, x)
                if objective_function > solution_objective_function:
                    solution = nodes.copy()
                    solution_x = x.copy()
                    solution_objective_function = objective_function

            # Remove the empty set from the dict
            if not degree_sets[lowest_degree]:
                del degree_sets[lowest_degree]

        # Check convergence if flag is set
        if use_convergence and previous_objective is not None:
            relative_change = abs(solution_objective_function - previous_objective) / (abs(previous_objective) if previous_objective != 0 else 1)
            if relative_change < convergence_threshold:
                break

        previous_objective = solution_objective_function
        iteration += 1

        # Check iteration limit if not using convergence
        if not use_convergence and iteration >= T:
            break

        # Update best solution if needed
        if solution_objective_function > best_objective_function:
            best_solution = solution
            best_solution_x = solution_x
            best_objective_function = solution_objective_function

        overall_max_inconsistent_degree = max(overall_max_inconsistent_degree, max_inconsistent_degree)

    execution_time.end_algorithm()

    # Output the best solution found across all iterations
    if print_results:
        print_end_algorithm(execution_time.execution_time_seconds, [best_solution_x], signed_graph, [best_objective_function])

    return best_solution, best_solution_x, overall_max_inconsistent_degree, iteration if use_convergence else T



