# algorithms/dls.py
# Person 1: Depth-Limited Search.
# DFS that never goes deeper than depth_limit.
# Depth = number of requests decided so far.
#   limit < m  -> cutoff, no complete selection, empty result
#   limit >= m -> behaves exactly like DFS

import time
from problem import can_accept, make_result


def solve(problem, time_limit=30, depth_limit=None):
    start_time = time.time()

    # no limit given means "use m", which behaves like DFS
    if depth_limit is None:
        depth_limit = problem.m

    info = {
        "nodes": 0,
        "peak": 0,
        "timed_out": False,
        "cutoff": False,         # True if the limit stopped the search
        "best_fare": -1,
        "best_accepted": (),
    }

    def explore(k, accepted, fare, depth):
        if info["timed_out"]:
            return
        if time.time() - start_time > time_limit:
            info["timed_out"] = True
            return

        info["nodes"] += 1
        if depth + 1 > info["peak"]:
            info["peak"] = depth + 1

        # goal: every request has been decided
        if k == problem.m:
            if fare > info["best_fare"]:
                info["best_fare"] = fare
                info["best_accepted"] = accepted
            return

        # depth limit reached before all requests were decided: cut off
        if depth >= depth_limit:
            info["cutoff"] = True
            return

        # choice 1: accept request k (only if capacity allows)
        if can_accept(problem, accepted, k):
            explore(k + 1, accepted + (k,), fare + problem.fare(k), depth + 1)

        # choice 2: reject request k (always allowed)
        explore(k + 1, accepted, fare, depth + 1)

    explore(0, (), 0, 0)

    return make_result(problem, "DLS", info["best_accepted"], info["nodes"],
                       start_time, info["peak"], info["timed_out"],
                       {"cutoff": info["cutoff"]})