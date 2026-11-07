
# greedy.py
# Person 3 - Greedy Best-First Search

import heapq
import time
from itertools import count

from problem import can_accept, make_result
from algorithms.heuristic import heuristic


def solve(problem, time_limit=30):

    start_time = time.time()

    if problem.m == 0:
        return make_result(
            problem, "Greedy Best-First Search",
            (), 0, start_time, 1, False
        )

    frontier = []
    counter = count()

    # State: (k, accepted)
    # Priority: (h, g, counter, k, accepted)
    # h = estimated remaining fare loss
    # g = fare already lost

    initial_h = heuristic(problem, 0, ())

    heapq.heappush(
        frontier,
        (initial_h, 0, next(counter), 0, ())
    )

    visited = {(0, ())}

    nodes_explored = 0
    peak_states = 1

    best_accepted = ()
    best_fare = 0

    while frontier:

        if time.time() - start_time >= time_limit:
            return make_result(
                problem, "Greedy Best-First Search",
                best_accepted, nodes_explored,
                start_time, peak_states, True
            )

        h, g, _, k, accepted = heapq.heappop(frontier)

        nodes_explored += 1

        # Update best feasible selection.
        current_fare = sum(
            problem.fare(i) for i in accepted
        )

        if current_fare > best_fare:
            best_fare = current_fare
            best_accepted = accepted

        # Goal: all requests decided.
        if k == problem.m:
            return make_result(
                problem, "Greedy Best-First Search",
                accepted, nodes_explored,
                start_time, peak_states, False
            )

        # Option 1: Reject request k.
        reject_state = (k + 1, accepted)

        if reject_state not in visited:

            visited.add(reject_state)

            reject_g = g + problem.fare(k)
            reject_h = heuristic(
                problem, k + 1, accepted
            )

            heapq.heappush(
                frontier,
                (
                    reject_h, reject_g,
                    next(counter), k + 1, accepted
                )
            )

        # Option 2: Accept request k.
        if can_accept(problem, accepted, k):

            new_accepted = accepted + (k,)
            accept_state = (k + 1, new_accepted)

            if accept_state not in visited:

                visited.add(accept_state)

                accept_h = heuristic(
                    problem, k + 1, new_accepted
                )

                heapq.heappush(
                    frontier,
                    (
                        accept_h, g,
                        next(counter), k + 1, new_accepted
                    )
                )

        peak_states = max(peak_states, len(frontier))

    return make_result(
        problem, "Greedy Best-First Search",
        best_accepted, nodes_explored,
        start_time, peak_states, False
    )
