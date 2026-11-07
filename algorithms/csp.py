import time
from problem import can_accept, make_result

def solve(problem, time_limit=30):

    start_time = time.time()

    best_accepted = ()
    best_fare = 0

    nodes_explored = 0
    backtracks = 0
    peak_states = 0
    timed_out = False

    def backtrack(k, accepted, current_fare, depth):
        nonlocal best_accepted, best_fare
        nonlocal nodes_explored, backtracks
        nonlocal peak_states, timed_out

        # Stop if the time limit is reached
        if time.time() - start_time >= time_limit:
            timed_out = True
            return

        nodes_explored += 1
        peak_states = max(peak_states, depth + 1)

        # Update the best feasible solution
        if current_fare > best_fare:
            best_fare = current_fare
            best_accepted = accepted

        # All requests have been considered
        if k == problem.m:
            return

        # Branch and Bound:
        # Maximum possible fare from this state
        upper_bound = current_fare

        for i in range(k, problem.m):
            upper_bound += problem.fare(i)

        # Prune if this branch cannot beat the best solution
        if upper_bound <= best_fare:
            backtracks += 1
            return

        # Choice 1: Accept request k
        if can_accept(problem, accepted, k):

            new_accepted = accepted + (k,)
            new_fare = current_fare + problem.fare(k)

            backtrack(
                k + 1,
                new_accepted,
                new_fare,
                depth + 1
            )

        else:
            # Accept branch is not feasible
            backtracks += 1

        # Stop exploring if timeout occurred
        if timed_out:
            return

        # Choice 2: Reject request k
        backtrack(
            k + 1,
            accepted,
            current_fare,
            depth + 1
        )

    # Start the backtracking search
    backtrack(0, (), 0, 0)

    # Return the common result format
    return make_result(
        problem,
        "CSP",
        best_accepted,
        nodes_explored,
        start_time,
        peak_states,
        timed_out,
        {"backtracks": backtracks}
    )