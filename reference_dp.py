
import time
from problem import make_result


def solve(problem, time_limit=30):
    start_time = time.time()

    # Precompute pickup and drop-off positions
    pickup_positions = {}
    dropoff_positions = {}

    for k in range(problem.m):
        request = problem.requests[k]

        pickup_positions[k] = problem.route.index(request.pickup)
        dropoff_positions[k] = problem.route.index(request.dropoff)

    # Group requests by pickup position
    pickups = {}

    for k in range(problem.m):
        position = pickup_positions[k]

        if position not in pickups:
            pickups[position] = []

        pickups[position].append(k)

    # State: passengers currently onboard
    # Value: (best fare, accepted request indices)
    dp = {(): (0, ())}

    nodes_explored = 0
    peak_states = 1
    timed_out = False

    # Check timeout immediately
    def time_exceeded():
        return time.time() - start_time >= time_limit

    for position in range(len(problem.route)):

        if time_exceeded():
            timed_out = True
            break

        # Remove passengers dropping off at this location
        updated = {}

        for onboard, (fare, accepted) in dp.items():

            if time_exceeded():
                timed_out = True
                break

            nodes_explored += 1

            new_onboard = tuple(
                k for k in onboard
                if dropoff_positions[k] > position
            )

            if (new_onboard not in updated or
                    fare > updated[new_onboard][0]):
                updated[new_onboard] = (fare, accepted)

        if timed_out:
            break

        dp = updated
        peak_states = max(peak_states, len(dp))

        # Consider requests picked up at this location
        for k in pickups.get(position, []):

            if time_exceeded():
                timed_out = True
                break

            updated = {}

            for onboard, (fare, accepted) in dp.items():

                if time_exceeded():
                    timed_out = True
                    break

                nodes_explored += 1

                # Option 1: Reject request
                if (onboard not in updated or
                        fare > updated[onboard][0]):
                    updated[onboard] = (fare, accepted)

                # Option 2: Accept request if capacity allows
                if len(onboard) < problem.capacity:

                    new_onboard = tuple(sorted(onboard + (k,)))
                    new_accepted = tuple(sorted(accepted + (k,)))
                    new_fare = fare + problem.fare(k)

                    if (new_onboard not in updated or
                            new_fare > updated[new_onboard][0]):
                        updated[new_onboard] = (
                            new_fare, new_accepted
                        )

            if timed_out:
                break

            dp = updated
            peak_states = max(peak_states, len(dp))

        if timed_out:
            break

    # Select the best feasible selection found so far
    best_fare = -1
    best_accepted = ()

    for fare, accepted in dp.values():
        if fare > best_fare:
            best_fare = fare
            best_accepted = accepted

    return make_result(
        problem,
        "Reference DP",
        best_accepted,
        nodes_explored,
        start_time,
        peak_states,
        timed_out
    )
