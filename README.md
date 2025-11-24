# Polarized Communities meet Densest Subgraph: Efficient and Effective Polarization Detection in Signed Networks

## Overview 

This project is developed as part of the following research paper:

F. Gullo, D. Mandaglio, A. Tagarelli. "Polarized Communities meet Densest Subgraph: Efficient and Effective
Polarization Detection in Signed Networks" published in ACM Transactions on Knowledge Discovery from Data (TKDD), 2025

This research codebase includes the implementations of the proposed `greedy2PC` and `greedy2PC++` algorithms for discovering polarized communities in signed networks, together with existing baselines (eigensign variants, bansal, local search, etc.). Each dataset is a signed edge list (see `datasets/`), and every algorithm implementation is in `code/algorithms/`. The `code/main.py` entrypoint glues everything together: it parses the CLI, loads the requested signed graph, runs the chosen method, prints intermediate information, and stores structured results under `output/<dataset>/<algorithm>_results.json`.
## Dependencies

- numpy==2.3.5
- scipy==1.16.3

The code was tested with Python 3.11.14.

## Running algorithms

From the `code/` directory, run the following command:

```bash
python main.py <dataset> <algorithm> \
  [-p/--print_results] [-b B] [-lsmi LS] [-ct CT] \
  [-T ITER] [-uc/--use_convergence]
```

- `dataset`: any filename in `datasets/` without the `.txt` suffix (e.g. `congress`, `slashdot`, `wikiconflict`…).
- `algorithm`: `greedy2PC` or `greedy2PC++` (proposed methods). The CLI also accepts the paper’s baselines `eigensign`, `eigensign-binary`, `random_eigensign`, `bansal`, `random_local`, and `greedy` for comparison.
- `-T` / `--use_convergence`: control the refinement iterations and stopping rule for `greedy2PC++`.
- `-b`: multiplicative factor (float or `l1`) for `random_eigensign`.
- `-lsmi` / `-ct`: maximum iterations and convergence threshold for `random_local`.

Examples:

```bash
python main.py congress greedy2PC
```

```bash
python main.py congress greedy2PC++ -T 10 --use_convergence
```

## Outputs

Every execution writes (or updates) a JSON entry like the existing `output/congress/greedy2PC_results.json`. The file contains:

- `solutions`: the two polarized communities (`S1`, `S2`) derived from the final vector solution.
- `polarity_scores` and `agreement_ratios`: scalar metrics per solution, as computed in `commons.py`.
- `running_time`: wall-clock seconds.
- Algorithm-specific extras (`beta`, `maximum_inconsistent_degree`, `iterations`, etc.).
- `parameters`: the subset of CLI arguments that influenced the run.
- `timestamp`: when the experiment finished.

Delete or rename the output file if you want to keep multiple experiment histories; otherwise the script transparently updates the entry matching the same parameter tuple.
