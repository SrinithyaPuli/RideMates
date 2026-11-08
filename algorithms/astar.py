# A* orders the queue by   f = g + h
#     g = fare already lost
#     h = guess of the fare we are still FORCED to lose (from heuristic.py)
# h_zero makes A* behave like UCS (useful for comparing).
import heapq
import time
from itertools import count
from problem import can_accept, make_result
from algorithms.heuristic import h_main


def solve(problem, time_limit=30, heuristic_fn=h_main):
    start_time = time.time()

    # Every queue entry is: (f, -k, counter, g, k, accepted, fare)
    #   f       = g + h, this decides the order
    #   -k      = if two states have the same f, the one that has decided
    #             MORE requests (bigger k) goes first. This helps A* finish sooner.
    #   counter = unique number so tuples are never compared further
    counter = count()
    frontier = []
    h_start = heuristic_fn(problem, 0, ())
    heapq.heappush(frontier, (h_start, 0, next(counter), 0, 0, (), 0))
    nodes_explored = 0
    peak_states = 1
    timed_out = False
    best_fare = 0
    best_accepted = ()
    extra = {"heuristic": heuristic_fn.__name__}
    while len(frontier) > 0:
        # Stop if the time limit has passed
        if time.time() - start_time >= time_limit:
            timed_out = True
            break
        f, _, _, g, k, accepted, fare = heapq.heappop(frontier)
        nodes_explored += 1
        # Remember the best selection seen (only used if we time out)
        if fare > best_fare:
            best_fare = fare
            best_accepted = accepted
        # Goal: every request has been decided
        if k == problem.m:
            return make_result(problem, "A*", accepted, nodes_explored,
                               start_time, peak_states, False, extra)
        # Choice 1: reject request k. Its fare is lost.
        reject_g = g + problem.fare(k)
        reject_h = heuristic_fn(problem, k + 1, accepted)
        heapq.heappush(frontier, (reject_g + reject_h, -(k + 1),
                                  next(counter), reject_g, k + 1,
                                  accepted, fare))
        # Choice 2: accept request k, only if capacity allows.
        if can_accept(problem, accepted, k):
            new_accepted = accepted + (k,)
            accept_h = heuristic_fn(problem, k + 1, new_accepted)
            heapq.heappush(frontier, (g + accept_h, -(k + 1),
                                      next(counter), g, k + 1,
                                      new_accepted,
                                      fare + problem.fare(k)))
        if len(frontier) > peak_states:
            peak_states = len(frontier)
    # We only get here after a timeout
    return make_result(problem, "A*", best_accepted, nodes_explored,
                       start_time, peak_states, timed_out, extra)