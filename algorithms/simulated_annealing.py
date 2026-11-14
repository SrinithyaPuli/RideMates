
import time
import random
import math

from problem import can_accept, make_result


# Simulated Annealing parameters
INITIAL_TEMPERATURE = 1000.0
COOLING_RATE = 0.995
MIN_TEMPERATURE = 0.01
MAX_ITERATIONS = 2000


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

    neighbors = []

    # 1. ADD: Add one rejected request.
    for k in rejected:
        if time.time() - start_time >= time_limit:
            return []

        if can_accept(problem, accepted, k):
            neighbors.append(tuple(sorted(accepted + (k,))))

    # 2. REMOVE: Remove one accepted request.
    for k in accepted:
        if time.time() - start_time >= time_limit:
            return []

        new_selection = tuple(
            x for x in accepted if x != k
        )

        neighbors.append(new_selection)

    # 3. SWAP: Remove one accepted request and add another.
    for old in accepted:
        if time.time() - start_time >= time_limit:
            return []

        reduced = tuple(
            x for x in accepted if x != old
        )

        for new in rejected:
            if time.time() - start_time >= time_limit:
                return []

            if can_accept(problem, reduced, new):
                neighbors.append(
                    tuple(sorted(reduced + (new,)))
                )

    return neighbors


def solve(problem, time_limit=30, seed=0):
    """Solve the carpool problem using Simulated Annealing."""

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

    current_fare = calculate_fare(problem, current)

    nodes_explored = 0
    peak_states = 1

    temperature = INITIAL_TEMPERATURE
    iteration = 0

    # Step 3: Perform the annealing search.
    while (
        not timed_out
        and temperature > MIN_TEMPERATURE
        and iteration < MAX_ITERATIONS
    ):

        if time.time() - start_time >= time_limit:
            timed_out = True
            break

        neighbors = generate_neighbors(
            problem, current, start_time, time_limit
        )

        if time.time() - start_time >= time_limit:
            timed_out = True
            break

        if not neighbors:
            break

        # Choose one random neighbour.
        neighbor = rng.choice(neighbors)
        nodes_explored += 1

        neighbor_fare = calculate_fare(problem, neighbor)

        # Difference between current and neighbouring fare.
        delta = current_fare - neighbor_fare

        # Step 4: Decide whether to accept the neighbour.
        if delta <= 0:
            # Accept a better or equal-fare neighbour.
            current = neighbor
            current_fare = neighbor_fare

        else:
            # Sometimes accept a worse neighbour.
            probability = math.exp(-delta / temperature)

            if rng.random() < probability:
                current = neighbor
                current_fare = neighbor_fare

        # Update the best selection found so far.
        if current_fare > best_fare:
            best_fare = current_fare
            best_selection = current

        # Step 5: Reduce the temperature.
        temperature *= COOLING_RATE
        iteration += 1

    # Step 6: Return the result in the common project format.
    return make_result(
        problem,
        "Simulated Annealing",
        best_selection,
        nodes_explored,
        start_time,
        peak_states,
        timed_out
    )
