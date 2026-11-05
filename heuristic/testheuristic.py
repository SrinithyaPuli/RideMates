import os
import json
import random
from problem import Request, Problem, capacity_ok, load_case
from algorithms.heuristic import h_zero, h_main, segment_costs
# ---------------------------------------------------------------
# Helper functions used by the tests
# ---------------------------------------------------------------

def true_remaining_loss(problem, k, accepted):
    #Finds the exact, true minimum fare you are forced to lose from the current state onward.
    remaining = list(range(k, problem.m))
    best_extra = 0
    for mask in range(1 << len(remaining)):
        extra = tuple(remaining[i] for i in range(len(remaining))
                      if mask & (1 << i))
        if capacity_ok(problem, accepted + extra):
            fare = sum(problem.fare(i) for i in extra)
            if fare > best_extra:
                best_extra = fare
    remaining_fare = sum(problem.fare(i) for i in remaining)
    return remaining_fare - best_extra


def all_states(problem):
    #Generates every single valid search state (k, accepted) that could possibly happen during a search for a given problem.
    states = []
    for k in range(problem.m + 1):
        for mask in range(1 << k):
            accepted = tuple(i for i in range(k) if mask & (1 << i))
            if capacity_ok(problem, accepted):
                states.append((k, accepted))
    return states


def make_random_problem(seed):
    #Generates a random test problem (using a fixed random seed so it's repeatable) with a random vehicle type, route, and passenger requests.
    rng = random.Random(seed)
    route = ["A", "B", "C", "D", "E", "F", "G"]
    vehicle = rng.choice(["Bike", "Auto", "Car"])
    count = rng.randint(3, 8)
    requests = []
    for n in range(1, count + 1):
        i = rng.randint(0, len(route) - 2)
        j = rng.randint(i + 1, len(route) - 1)
        requests.append(Request("Q" + str(n), route[i], route[j],
                                rng.randint(10, 100)))
    return Problem(route, vehicle, requests)


# ---------------------------------------------------------------
# The worked example from the spec
# ---------------------------------------------------------------
route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
]
# Sorted order is Q1, Q3, Q2, Q4  ->  k = 0, 1, 2, 3
bike = Problem(route, "Bike", requests)

#Test 1:Verifies that h_zero always returns 0 regardless of the state.
assert h_zero(bike, 0, ()) == 0
assert h_zero(bike, 2, (1,)) == 0
print("Test 1 passed: h_zero is always 0")

# Test 2:Uses a hardcoded manual example (from the project spec) to check if segment_costs and h_main compute the correct bottleneck value (50) right at the beginning (k=0).
assert segment_costs(bike, 0, ()) == [30, 50, 40, 40]
assert h_main(bike, 0, ()) == 50
print("Test 2 passed: Bike example gives h = 50 at the start")

# Test 3:Checks a mid-game state where some requests have already been decided, ensuring the heuristic updates and calculates the correct remaining loss (40).
assert h_main(bike, 2, (1,)) == 40
print("Test 3 passed: middle state gives h = 40")

#Test 4:Verifies that when all requests are decided (k =total), the heuristic correctly returns 0 because there are no future losses left.
assert h_main(bike, 4, (1, 2)) == 0
print("Test 4 passed: h is 0 at a goal state")

#Test 5:Ensures that if a vehicle (like an Auto) has enough capacity and no one overflows, the heuristic correctly returns 0.
auto = Problem(route, "Auto", requests)
assert h_main(auto, 0, ()) == 0
print("Test 5 passed: no overload means h = 0")

#Test 6:Checks that when an overload happens, the heuristic targets and sums up the cheapest conflicting fares (e.g., rejecting 10 and 20 out of 5 requests gives h = 30) and matches true_remaining_loss.
five = [
    Request("Q1", "A", "B", 10),
    Request("Q2", "A", "B", 20),
    Request("Q3", "A", "B", 30),
    Request("Q4", "A", "B", 40),
    Request("Q5", "A", "B", 50),
]
auto5 = Problem(route, "Auto", five)
assert h_main(auto5, 0, ()) == 30
assert true_remaining_loss(auto5, 0, ()) == 30
print("Test 6 passed: rejects the two cheapest fares (h = 30)")

#Test 7:Handles edge cases where requests might be invalid or out of bounds, ensuring it safely returns 0.
none_valid = Problem(route, "Bike", [Request("Q1", "A", "Z", 10)])
assert h_main(none_valid, 0, ()) == 0
print("Test 7 passed: zero valid requests gives h = 0")

#Test 8:It loops through every possible state across 60 different random problems and asserts that your heuristic value $h$ is always greater than or equal to $0$ and never exceeds the real true remaining loss ($h \le \text{real}$).
checked = 0
positive = 0
exact = 0
for seed in range(60):
    problem = make_random_problem(seed)
    for (k, accepted) in all_states(problem):
        h = h_main(problem, k, accepted)
        real = true_remaining_loss(problem, k, accepted)
        assert h >= 0, "h is negative"
        assert h <= real, ("h too high! seed=" + str(seed) +
                           " k=" + str(k) + " accepted=" + str(accepted) +
                           " h=" + str(h) + " real=" + str(real))
        if k == problem.m:
            assert h == 0, "h must be 0 at a goal state"
        checked += 1
        if h > 0:
            positive += 1
        if h == real:
            exact += 1

print("Test 8 passed: h never overestimates in " + str(checked) +
      " states (h > 0 in " + str(positive) + ", exactly right in " +
      str(exact) + ")")

#Test 9:it compares your heuristic against a reference Dynamic Programming (solve) solution to ensure it is safe and accurate on real-world test cases.
if os.path.exists("data/testcases.json"):
    from reference_dp import solve
    with open("data/testcases.json") as f:
        cases = json.load(f)
    for case in cases:
        problem = load_case(case["case_id"])
        dp = solve(problem)
        real_lost = problem.total_fare - dp["total_fare"]
        h = h_main(problem, 0, ())
        assert h <= real_lost, case["case_id"] + ": h is too high"
        print("   ", case["case_id"], "| h =", h, "| real fare lost =", real_lost)
    print("Test 9 passed: h is safe on every dataset case")
else:
    print("Test 9 skipped: data/testcases.json not found")
print("\nAll heuristic tests passed!")