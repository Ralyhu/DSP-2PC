import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

import argparse
import numpy as np
import json
import time
import os
from typing import Dict, Any, List, Tuple
from algorithms.subroutines import commons
from algorithms.subroutines.commons import build_solution_two_sets

from signed_graph.signed_graph import SignedGraph

from algorithms.eigensign import eigensign
from algorithms.eigensign import eigensign_binary
from algorithms.random_eigensign import random_eigensign

from algorithms.bansal import bansal
from algorithms.local_search import local_search

from algorithms.greedy_degree_removal import greedy_degree_removal
from algorithms.greedy2PC import greedy2PC
from algorithms.greedy2PC import greedy2PC_plus_plus

from utilities.print_console import print_input

from datetime import datetime

def save_results(dataset: str, algorithm: str, results: Dict[str, Any]):
    output_dir = os.path.join("output", dataset)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{algorithm}_results.json")
    
    # Add timestamp to results in a human-readable format
    results["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load existing results if file exists
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_results = json.load(f)
    else:
        existing_results = []
    
    # Check if an entry with the same parameters already exists
    updated = False
    for i, entry in enumerate(existing_results):
        if isinstance(entry, dict) and entry.get("parameters") == results.get("parameters"):
            existing_results[i] = results
            updated = True
            break
    
    # If no matching entry was found, append the new results
    if not updated:
        existing_results.append(results)
    
    # Save the updated results
    with open(output_file, "w") as f:
        json.dump(existing_results, f, indent=2, separators=(',', ': '))
    
    print(f"Results saved to {output_file}")

def format_results(signed_graph, xs: List[np.ndarray], running_time: float) -> Dict[str, Any]:
    return {
        "solutions": [{"S1": list(S1), "S2": list(S2)} for x in xs for S1, S2 in [build_solution_two_sets(x)]],
        "polarity_scores": [commons.evaluate_objective_function(signed_graph, x) for x in xs],
        "agreement_ratios": [commons.compute_agreement_ratio(signed_graph, x) for x in xs],
        "running_time": running_time
    }

def get_relevant_parameters(algorithm: str, args: argparse.Namespace) -> Dict[str, Any]:
    
    algorithm_params = {
        "eigensign": {},
        "eigensign-binary": {},
        "random_eigensign": {"beta": args.b},
        "bansal": {},
        "random_local": {"max_iterations": args.lsmi, "convergence_threshold": args.ct},
        "greedy": {},
        "greedy2PC": {},
        "greedy2PC++": {"T": args.T, "use_convergence": args.use_convergence},
    }
    
    return {**algorithm_params[algorithm]}

if __name__ == '__main__':
    # create a parser
    parser = argparse.ArgumentParser(description='Algorithms for the 2PC problem')

    # create and read the arguments
    parser.add_argument('d', help='dataset', type=str)
    parser.add_argument('a', help='algorithm', type=str)
    parser.add_argument('-p', '--print_results', help='print results inside each method', action='store_true', default=True)
    parser.add_argument('-T', help='number of iterations (for greedy++)', type=int, default=10)
    parser.add_argument('-uc', '--use_convergence', help='use convergence check (for greedy++)', action='store_true', default=False)
    parser.add_argument('-lsmi', help='maximum iterations for local search', type=int, default=10)
    parser.add_argument('-ct', help='convergence threshold', type=float, default=0.2)
    parser.add_argument('-b', help='multiplicative factor for random_eigensign', type=str, default='l1')

    args = parser.parse_args()

    # read the input graph
    signed_graph = SignedGraph(args.d)
    print_input(args.d, signed_graph.number_of_nodes, signed_graph.number_of_edges, args.a)

    # execute the algorithm and save results
    start_time = time.time()
    
    if args.a == 'eigensign':
        _, x = eigensign(signed_graph, print_results=args.print_results)
        results = format_results(signed_graph, [x], time.time() - start_time)
    
    elif args.a == 'eigensign-binary':
        _, x, _ = eigensign_binary(signed_graph, print_results=args.print_results)
        results = format_results(signed_graph, [x], time.time() - start_time)

    elif args.a == 'random_eigensign':
        _, x, maximum_eigenvector, execution_time_seconds, beta = random_eigensign(signed_graph, args.b, print_results=args.print_results)
        results = format_results(signed_graph, [x], time.time() - start_time)
        results["beta"] = beta

    elif args.a == 'bansal':
        _, x = bansal(signed_graph, print_results=args.print_results)
        results = format_results(signed_graph, [x], time.time() - start_time)

    elif args.a == 'random_local':
        _, x = local_search(signed_graph, args.mi, args.ct, print_results=args.print_results)
        results = format_results(signed_graph, [x], time.time() - start_time)

    elif args.a == 'greedy':
        _, x = greedy_degree_removal(signed_graph, print_results=args.print_results)
        results = format_results(signed_graph, [x], time.time() - start_time)
    
    elif args.a == 'greedy2PC':
        _, eigensign_binary_solution, _ = eigensign_binary(signed_graph, print_results=False)
        _, x, maximum_inconsistent_degree = greedy2PC(signed_graph, eigensign_binary_solution, print_results=args.print_results)
        results = format_results(signed_graph, [x], time.time() - start_time)
        results["maximum_inconsistent_degree"] = maximum_inconsistent_degree
    
    
    elif args.a == 'greedy2PC++':
        _, eigensign_binary_solution, _ = eigensign_binary(signed_graph, print_results=args.print_results)
        _, x, maximum_inconsistent_degree, n_iterations = greedy2PC_plus_plus(
            signed_graph, 
            eigensign_binary_solution, 
            args.T, 
            use_convergence=args.use_convergence,
            print_results=args.print_results
        )
        results = format_results(signed_graph, [x], time.time() - start_time)
        results["maximum_inconsistent_degree"] = maximum_inconsistent_degree
        results["iterations"] = n_iterations

    # Add the relevant parameters to the results
    results["parameters"] = get_relevant_parameters(args.a, args)

    save_results(args.d, args.a, results)
