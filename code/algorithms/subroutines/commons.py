from scipy.sparse.linalg import eigsh
import numpy as np

def evaluate_objective_function(signed_graph, x):
    # special case with no nodes in the solution
    if x.dot(x) == 0:
        return np.nan

    # obtain the adjacency matrix
    a = signed_graph.get_adjacency_matrix()

    # compute the objective function
    a_dot_x = a.dot(x)
    return x.dot(a_dot_x) / x.dot(x)

def build_solution(x):
    # return the nodes having the corresponding index of x different from 0
    return {node for node, element in enumerate(x) if element != 0}


def build_x(signed_graph, nodes, eigenvector=None):
    # get the maximum eigenvector of the adjacency matrix
    if eigenvector is None:
        a = signed_graph.get_adjacency_matrix()
        eigenvector = np.squeeze(eigsh(a, k=1, which='LA')[1])

    # build x from the signs of the minimum eigenvector
    return np.array([np.sign(element) if node in nodes else 0 for node, element in enumerate(eigenvector)])

def build_solution_two_sets(x):
    # Separate nodes into S1 (value 1) and S2 (value -1)
    S1 = {node for node, element in enumerate(x) if element == 1}
    S2 = {node for node, element in enumerate(x) if element == -1}
    return S1, S2

def build_x_from_two_sets(signed_graph, S1, S2):
    # Create a zero vector with length equal to the number of nodes in the graph
    x = np.zeros(signed_graph.number_of_nodes)
    
    # Set 1 for nodes in S1
    x[list(S1)] = 1
    
    # Set -1 for nodes in S2
    x[list(S2)] = -1
    
    return x

def get_edges_clusters(A, membership):
    cx = A.tocoo()
    int_p1 = 0
    int_p2 = 0
    int_n1 = 0
    int_n2 = 0
    inter_p = 0
    inter_n = 0
    for i,j,v in zip(cx.row, cx.col, cx.data):
        if (membership[i] == 1 or membership[i] == -1) and (membership[j] == 1 or membership[j] == -1):
            ci = membership[i]
            cj = membership[j]
            if ci == cj:
                if ci == 1:
                    if v == 1:
                        int_p1 += 1
                    elif v == -1:
                        int_n1 +=1
                elif ci == -1:
                    if v == 1:
                        int_p2 += 1
                    elif v == -1:
                        int_n2 +=1
            else:
                if v == 1:
                    inter_p += 1
                elif v == -1:
                    inter_n +=1
    # each edge is counted twice in the previous loop
    int_p1 /= 2
    int_p2 /= 2
    int_n1 /= 2
    int_n2 /= 2
    inter_p /= 2
    inter_n /= 2
    n1 = 0
    n2 = 0
    for v in membership:
        if v == 1:
            n1 += 1
        elif v == 2:
            n2 += 1
    if n1 >= n2:
        return int_p1, int_p2, int_n1, int_n2, inter_p, inter_n
    else:
        return int_p2, int_p1, int_n2, int_n1, inter_p, inter_n

def compute_agreement_ratio(signed_graph, x):
    A = signed_graph.get_adjacency_matrix()
    int_p1, int_p2, int_n1, int_n2, inter_p, inter_n = get_edges_clusters(A, x)
    m = int_p1 + int_p2 + int_n1 + int_n2 + inter_p + inter_n
    if m!= 0:
        ag_ratio = ((int_p1) + (int_p2) + (inter_n))/m
    else: 
        ag_ratio = 0.0
    return ag_ratio