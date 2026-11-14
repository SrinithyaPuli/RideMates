# IDA* is A* that uses very little memory.
# Instead of a big queue it runs a depth-first search over and over,
# each time with a limit ("threshold") on f = g + h:
#     g = fare lost so far
#     h = guess of the fare still forced to be lost (from heuristic.py)
# Round 1: threshold = h of the start state.
#          Any state with f above the threshold is skipped.
# If no complete answer is found, the new threshold is the smallest f that
# was skipped, and we search again. The first complete answer found is the best.
# The price of low memory is repeated work: early rounds are searched again
# in later rounds. We count that repeated work as "overhead_nodes".
import time
from problem import can_accept, make_result
from algorithms.heuristic import h_main
FOUND = -1            # special return value meaning "complete answer found"
INFINITY = 10 ** 9    # bigger than any possible f value
def solve(problem, time_limit=30, heuristic_fn=h_main):
    start_time = time.time()
    # Numbers shared by all the recursive calls
    info = {
        "nodes": 0,              
        "peak": 0,               
        "timed_out": False,
        "answer": (),            
        "best_fare": 0,          
        "best_accepted": (),
    }

    def search(k, accepted, g, fare, depth, threshold):
        # Returns FOUND if a complete answer was found below this state.
        # Otherwise returns the smallest f value that went over the threshold.
        if info["timed_out"]:
            return INFINITY
        if time.time() - start_time >= time_limit:
            info["timed_out"] = True
            return INFINITY
        info["nodes"] += 1
        if depth + 1 > info["peak"]:
            info["peak"] = depth + 1
        if fare > info["best_fare"]:
            info["best_fare"] = fare
            info["best_accepted"] = accepted
        # f = fare lost so far + guess of the fare still forced to be lost
        f = g + heuristic_fn(problem, k, accepted)
        # Too expensive for this round: skip it, but report the f value
        if f > threshold:
            return f
        # Goal: every request has been decided
        if k == problem.m:
            info["answer"] = accepted
            return FOUND
        smallest_skipped = INFINITY
        # Choice 1: accept request k, only if capacity allows (nothing lost)
        if can_accept(problem, accepted, k):
            result = search(k + 1, accepted + (k,), g,
                            fare + problem.fare(k), depth + 1, threshold)
            if result == FOUND:
                return FOUND
            if result < smallest_skipped:
                smallest_skipped = result
        # Choice 2: reject request k (its fare is lost)
        result = search(k + 1, accepted, g + problem.fare(k),
                        fare, depth + 1, threshold)
        if result == FOUND:
            return FOUND
        if result < smallest_skipped:
            smallest_skipped = result
        return smallest_skipped
    # ---- The IDA* loop: try bigger and bigger thresholds ----
    threshold = heuristic_fn(problem, 0, ())
    rounds = 0
    nodes_before_last_round = 0
    found = False
    while True:
        rounds += 1
        nodes_before_last_round = info["nodes"]
        result = search(0, (), 0, 0, 0, threshold)
        if result == FOUND:
            found = True
            break
        if info["timed_out"]:
            break
        if result >= INFINITY:
            break              # cannot happen, but this stops an endless loop
        threshold = result     # next round allows the smallest skipped f
    # Choose what to return
    if found:
        chosen = info["answer"]
    else:
        chosen = info["best_accepted"]     # timed out: best partial answer
    extra = {
        "rounds": rounds,
        "overhead_nodes": nodes_before_last_round,
        "heuristic": heuristic_fn.__name__,
    }
    return make_result(problem, "IDA*", chosen, info["nodes"], start_time,
                       info["peak"], info["timed_out"], extra)