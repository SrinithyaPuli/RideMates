
import time
import random

from problem import can_accept, make_result


def calculate_fare(problem, accepted):
    """Calculate the total fare of accepted requests."""
    total = 0

    for k in accepted:
        total += problem.fare(k)

    return total


def generate_neighbors(problem, accepted, start_time, time_limit):
    """Generate valid neighbours using Add, Remove and Swap."""

    accepted = tuple(sorted(accepted))
    accepted_set = set(accepted)

    rejected = [
        k for k in range(problem.m)
        if k not in accepted_set
    ]

    # 1. ADD: Try adding one rejected request.
    for k in rejected:
        if time.time() - start_time >= time_limit:
            return

        if can_accept(problem, accepted, k):
            yield tuple(sorted(accepted + (k,)))

    # 2. REMOVE: Try removing one accepted request.
    for k in accepted:
        if time.time() - start_time >= time_limit:
            return

        new_selection = tuple(
            x for x in accepted if x != k
        )

        yield new_selection

    # 3. SWAP: Remove one accepted request and add a rejected one.
    for old in accepted:
        if time.time() - start_time >= time_limit:
            return

        reduced = tuple(
            x for x in accepted if x != old
        )

        for new in rejected:
            if time.time() - start_time >= time_limit:
                return

            if can_accept(problem, reduced, new):
                yield tuple(sorted(reduced + (new,)))


def solve(problem, time_limit=30, seed=0):
    """Solve the carpool problem using Simple Hill Climbing."""

    start_time = time.time()
    rng = random.Random(seed)

    # Step 1: Generate a random valid initial selection.
    current = []
    requests = list(range(problem.m))
    rng.shuffle(requests)

    timed_out = False

    for k in requests:
        if time.time() - start_time >= time_limit:
            timed_out = True
            break

        if rng.random() < 0.5:
            if can_accept(problem, current, k):
                current.append(k)

    current = tuple(sorted(current))

    # Step 2: Store the best selection found.
    best_selection = current
    best_fare = calculate_fare(problem, current)

    nodes_explored = 0
    peak_states = 1

    # Step 3: Continue searching for an improvement.
    while not timed_out:

        if time.time() - start_time >= time_limit:
            timed_out = True
            break

        current_fare = calculate_fare(problem, current)
        improved = False

        # Simple Hill Climbing: choose the FIRST improving neighbour.
        for neighbor in generate_neighbors(
            problem, current, start_time, time_limit
        ):
            if time.time() - start_time >= time_limit:
                timed_out = True
                break

            nodes_explored += 1

            neighbor_fare = calculate_fare(problem, neighbor)

            # Update the best selection found.
            if neighbor_fare > best_fare:
                best_fare = neighbor_fare
                best_selection = neighbor

            # Move to the first neighbour with a higher fare.
            if neighbor_fare > current_fare:
                current = neighbor
                improved = True
                break

        # Check whether the time limit was reached.
        if time.time() - start_time >= time_limit:
            timed_out = True

        if timed_out:
            break

        # Stop when no improving neighbour exists.
        if not improved:
            break

    # Step 4: Return the result in the common project format.
    return make_result(
        problem,
        "Hill Climbing",
        best_selection,
        nodes_explored,
        start_time,
        peak_states,
        timed_out
    )
