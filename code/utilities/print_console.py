import numpy as np

from algorithms.subroutines.commons import evaluate_objective_function

def print_input(dataset, num_nodes, num_edges, algorithm):
    print('------------- Input -------------')
    print('dataset:               ' + dataset)
    print('number of nodes:               ' + str(num_nodes))
    print('number of edges:               ' + str(num_edges))
    print('algorithm:             ' + algorithm)


def print_end_algorithm(runtime, xs, signed_graph, polarity_scores, beta=np.nan, thresholds=np.nan):
    print('------------- Output ------------')

    # performance information
    print('runtime:               ' + str(runtime))

    print("Total polarity:        " + str(sum(polarity_scores))            )

    for i, x in enumerate(xs):

        print("----------- solution {} --------------".format(i + 1))

        
        # parameters
        if not np.isnan(thresholds) and not np.isnan(beta): 
            print('tau:                   ' + str(thresholds[i] if type(thresholds)==list else np.nan))
            print('multiplicative factor: ' + str(beta))

        # quality of the solution
        #assert evaluate_objective_function(signed_graph, x) == polarity_scores[i]
        print('polarity:              ' + str(evaluate_objective_function(signed_graph, x)))

        # print the nodes of the two communities
        community_p1 = {node for node, element in enumerate(x) if element == 1}
        community_m1 = {node for node, element in enumerate(x) if element == -1}

        print('S_1:                   ' + str(str(community_p1).replace('set([', '').replace('])', '')))
        print("|S_1| = " + str(len(community_p1)))
        print('S_2:                   ' + str(str(community_m1).replace('set([', '').replace('])', '')))
        print("|S_2| = " + str(len(community_m1)))
