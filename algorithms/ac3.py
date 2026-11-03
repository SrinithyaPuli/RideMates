import time
from problem import can_accept, make_result

def propagate(problem, domains, segment_map):
    """
    AC-3 propagation for capacity constraints.

    0 = Accept
    1 = Reject

    Returns:
        domains, domain_reduction, consistent
    """

    domain_reduction = 0
    changed = True

    while changed:
        changed = False

        for segment, request_indices in segment_map.items():

            # Count requests that are already forced to Accept
            forced_accepts = sum(
                1 for i in request_indices
                if domains[i] == {0}
            )

            # Capacity exceeded: contradiction
            if forced_accepts > problem.capacity:
                return domains, domain_reduction, False

            # If capacity is full, other requests using
            # this segment cannot be accepted.
            if forced_accepts == problem.capacity:

                for i in request_indices:

                    if domains[i] == {0}:
                        continue

                    if 0 in domains[i]:
                        domains[i].remove(0)
                        domain_reduction += 1
                        changed = True

                        if not domains[i]:
                            return domains, domain_reduction, False

    return domains, domain_reduction, True


def solve(problem, time_limit=30):

    start_time = time.time()

    best_accepted = ()
    best_fare = 0

    nodes_explored = 0
    backtracks = 0
    domain_reduction = 0
    peak_states = 0
    timed_out = False

    # Build a mapping:
    # route segment -> requests using that segment

    segment_map = {}

    for i in range(problem.m):
        for segment in problem.segments(i):
            if segment not in segment_map:
                segment_map[segment] = []

            segment_map[segment].append(i)

    # Initially every request can be accepted or rejected
    initial_domains = [{0, 1} for _ in range(problem.m)]

    def backtrack(k, accepted, current_fare, domains, depth):

        nonlocal best_accepted, best_fare
        nonlocal nodes_explored, backtracks
        nonlocal domain_reduction, peak_states, timed_out

        if time.time() - start_time >= time_limit:
            timed_out = True
            return

        nodes_explored += 1
        peak_states = max(peak_states, depth + 1)

        # Save the best feasible selection found so far
        if current_fare > best_fare:
            best_fare = current_fare
            best_accepted = accepted

        # All requests have been considered
        if k == problem.m:
            return

        # Skip requests already forced to Reject by AC-3
        if domains[k] == {1}:
            backtrack(
                k + 1, accepted, current_fare,
                domains, depth + 1
            )
            return

        # Branch-and-bound
        upper_bound = current_fare

        for i in range(k, problem.m):
            if 0 in domains[i]:
                upper_bound += problem.fare(i)

        if upper_bound <= best_fare:
            backtracks += 1
            return

        # -------------------------
        # Branch 1: Accept request
        # -------------------------

        if 0 in domains[k] and can_accept(problem, accepted, k):

            new_domains = [set(d) for d in domains]
            new_domains[k] = {0}

            new_domains, reductions, consistent = propagate(
                problem, new_domains, segment_map
            )

            domain_reduction += reductions

            if consistent:
                backtrack(
                    k + 1,
                    accepted + (k,),
                    current_fare + problem.fare(k),
                    new_domains,
                    depth + 1
                )
            else:
                backtracks += 1

        else:
            backtracks += 1

        if timed_out:
            return

        # -------------------------
        # Branch 2: Reject request
        # -------------------------

        new_domains = [set(d) for d in domains]
        new_domains[k] = {1}

        backtrack(
            k + 1,
            accepted,
            current_fare,
            new_domains,
            depth + 1
        )

    backtrack(
        0,
        (),
        0,
        initial_domains,
        0
    )

    return make_result(
        problem,
        "AC-3",
        best_accepted,
        nodes_explored,
        start_time,
        peak_states,
        timed_out,
        {
            "backtracks": backtracks,
            "domain_reduction": domain_reduction
        }
    )