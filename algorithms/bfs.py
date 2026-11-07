# algorithms/bfs.py
# Person 1: Breadth-First Search.
# Explores the decision tree level by level using a queue.
# Explores the whole tree and keeps the best complete selection.

import time
from collections import deque
from problem import can_accept, make_result


def solve(problem, time_limit=30):
    start_time = time.time()

    nodes = 0
    peak = 1
    timed_out = False
    best_fare = -1
    best_accepted = ()

    # each queue entry: (k, accepted, fare)
    queue = deque()
    queue.append((0, (), 0))

    while len(queue) > 0:
        # stop if the time limit has passed
        if time.time() - start_time > time_limit:
            timed_out = True
            break

        k, accepted, fare = queue.popleft()
        nodes += 1

        # goal: every request has been decided
        if k == problem.m:
            if fare > best_fare:
                best_fare = fare
                best_accepted = accepted
            continue

        # choice 1: accept request k (only if capacity allows)
        if can_accept(problem, accepted, k):
            queue.append((k + 1, accepted + (k,), fare + problem.fare(k)))

        # choice 2: reject request k (always allowed)
        queue.append((k + 1, accepted, fare))

        if len(queue) > peak:
            peak = len(queue)

    return make_result(problem, "BFS", best_accepted, nodes,
                       start_time, peak, timed_out)