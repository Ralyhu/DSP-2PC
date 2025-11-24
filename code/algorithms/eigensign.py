from algorithms.subroutines.commons import *
from utilities.time_measure import ExecutionTime
from utilities.print_console import print_end_algorithm
from scipy.sparse.linalg import eigs, eigsh


def eigensign(signed_graph, print_results=True):
    # start of the algorithm
    execution_time = ExecutionTime()

    # initialize the solution as empty
    solution_x = None
    solution_objective_function = np.finfo(float).min
    solution_threshold = None

    # obtain the adjacency matrix
    a = signed_graph.get_adjacency_matrix()

    # get the eigenvector corresponding to the maximum eigenvalue
    maximum_eigenvector = np.squeeze(eigsh(a, k=1, which='LA')[1])

    #print("All in range? ", np.all((maximum_eigenvector >= -1) & (maximum_eigenvector <= 1)))

    # get the thresholds from the eigenvector
    thresholds = {int(np.abs(element) * 1000) / 1000.0 for element in maximum_eigenvector}

    # compute x for all the values of the threshold
    for threshold in thresholds:
        x = np.array([np.sign(element) if np.abs(element) >= threshold else 0 for element in maximum_eigenvector])

        # update the solution if needed
        objective_function = evaluate_objective_function(signed_graph, x)
        if objective_function > solution_objective_function:
            solution_x = x
            solution_objective_function = objective_function
            solution_threshold = threshold

    # build the solution
    solution = build_solution(solution_x)

    # end of the algorithm
    execution_time.end_algorithm()

    # print algorithm's results
    if print_results:
        print_end_algorithm(execution_time.execution_time_seconds, [solution_x], signed_graph, [solution_objective_function], thresholds=[solution_threshold])

    # return the solution
    return solution, solution_x


def eigensign_binary(signed_graph, print_results=False):
    # start of the algorithm
    execution_time = ExecutionTime()

    # obtain the adjacency matrix
    a = signed_graph.get_adjacency_matrix()

    
    # get the eigenvector corresponding to the maximum eigenvalue
    maximum_eigenvector = np.squeeze(eigsh(a, k=1, which='LA')[1]) # OLD
    #_, maximum_eigenvector = eigs(a, k=1, which='LR')
    #print(maximum_eigenvector)

    #solution_x = np.sign(maximum_eigenvector)
    # assign nodes to groups based on the sign of the eigenvector
    solution_x = np.where(maximum_eigenvector >= 0, 1, -1)

    # Compute the objective function
    solution_objective_function = evaluate_objective_function(signed_graph, solution_x)

    #print(f"Objective function before sign change: {solution_objective_function}")

    # Check if there's at least one +1 and one -1 in solution_x
    # if 1 in solution_x and -1 in solution_x:
    #     # Find the index of the maximum absolute value in maximum_eigenvector
    #     min_abs_index = np.argmin(np.abs(maximum_eigenvector))

    #     # Change the sign of the element in solution_x corresponding to max_abs_index
    #     solution_x[min_abs_index] *= -1

    #     solution_objective_function = evaluate_objective_function(signed_graph, solution_x)
        #print(f"Objective function after sign change: {solution_objective_function}")
    #else:
        #print("No sign change performed: solution_x does not contain both +1 and -1")

    

    # build the solution
    solution = build_solution(solution_x)

    #print(solution_x, solution, signed_graph.number_of_nodes)

    #assert len(solution) == signed_graph.number_of_nodes - np.sum(maximum_eigenvector == 0) # check every node is assigned to S_1 or S_2
    assert len(solution) == signed_graph.number_of_nodes

    # end of the algorithm
    execution_time.end_algorithm()

    if print_results:
        # print algorithm's results
        print_end_algorithm(execution_time.execution_time_seconds, [solution_x], signed_graph, [solution_objective_function], thresholds=["Binary"])

    # return the solution
    return solution, solution_x, maximum_eigenvector
