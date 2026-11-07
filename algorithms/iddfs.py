# algorithms/iddfs.py
# Person 1: Iterative Deepening DFS.
# Runs DLS with limits 1, 2, 3 ... m. Only the last round (limit m)
# reaches complete selections, so the earlier rounds are pure overhead.

import time
from problem import make_result
from algorithms.dls import solve as dls_solve


def solve(problem, time_limit=30):
    start_time = time.time()

    # which limits to try (m = 0 means nothing to decide: one round, limit 0)
    if problem.m == 0:
        limits = [0]
    else:
        limits = list(range(1, problem.m + 1))

    # request id -> index k, to turn DLS results back into indices
    index_of = {}
    for k in range(problem.m):
        index_of[problem.requests[k].id] = k

    nodes_per_round = []
    peak = 0
    timed_out = False
    best_accepted = ()

    for limit in limits:
        # stop if the shared time budget is used up
        remaining = time_limit - (time.time() - start_time)
        if remaining < 0:
            timed_out = True
            break

        result = dls_solve(problem, remaining, limit)
        nodes_per_round.append(result["nodes_explored"])
        if result["peak_states"] > peak:
            peak = result["peak_states"]

        # keep the selection from this round (empty until limit reaches m)
        best_accepted = ()
        for request_id in result["accepted_ids"]:
            best_accepted = best_accepted + (index_of[request_id],)
        best_accepted = tuple(sorted(best_accepted))

        if result["timed_out"]:
            timed_out = True
            break

    total_nodes = sum(nodes_per_round)
    overhead = sum(nodes_per_round[:-1])      # every round except the last

    return make_result(problem, "IDDFS", best_accepted, total_nodes,
                       start_time, peak, timed_out,
                       {"overhead_nodes": overhead})