
# UCS always expands the state with the smallest g first.
# The first complete state (k == m) that comes off the queue has the
# smallest possible fare lost, so it is the best answer.
# The search space is a tree (every state is reached in only one way),
# so we do not need a "visited" set.
import heapq
import time
from itertools import count
from problem import can_accept, make_result


def solve(problem, time_limit=30):
    start_time = time.time()
    # Every queue entry is: (g, counter, k, accepted, fare)
    #   g       = fare lost so far (this decides the order)
    #   counter = a unique number, so Python never has to compare two
    #             "accepted" tuples when two entries have the same g
    #   fare    = fare earned so far (used to remember the best partial answer)
    counter = count()
    frontier = []
    heapq.heappush(frontier, (0, next(counter), 0, (), 0))
    nodes_explored = 0
    peak_states = 1 
    timed_out = False
    best_fare = 0
    best_accepted = ()
    while len(frontier) > 0:
        if time.time() - start_time >= time_limit:
            timed_out = True
            break
        # Take the state with the smallest fare lost
        g, _, k, accepted, fare = heapq.heappop(frontier)
        nodes_explored += 1
        # Remember the best selection seen (only used if we time out)
        if fare > best_fare:
            best_fare = fare
            best_accepted = accepted
        # Goal: every request has been decided.
        # This is the best possible answer, so we can stop.
        if k == problem.m:
            return make_result(problem, "UCS", accepted, nodes_explored,
                               start_time, peak_states, False)
        # Choice 1: reject request k. This is always allowed.
        # The fare of request k is lost, so g goes up.
        heapq.heappush(frontier, (g + problem.fare(k), next(counter),
                                  k + 1, accepted, fare))
        # Choice 2: accept request k, but only if capacity allows.
        # Nothing is lost, so g stays the same.
        if can_accept(problem, accepted, k):
            heapq.heappush(frontier, (g, next(counter), k + 1,
                                      accepted + (k,),
                                      fare + problem.fare(k)))
        if len(frontier) > peak_states:
            peak_states = len(frontier)
    # We only get here after a timeout
    return make_result(problem, "UCS", best_accepted, nodes_explored,
                       start_time, peak_states, timed_out)