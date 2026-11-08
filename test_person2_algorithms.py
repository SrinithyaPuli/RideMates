import json
from problem import Request, Problem, load_case
from reference_dp import solve as dp_solve
from algorithms import ucs, astar, ida_star
from algorithms.heuristic import h_zero


def astar_h_zero(problem, time_limit=30):
    # A* with the "always 0" heuristic. It should find the same answer as UCS.
    return astar.solve(problem, time_limit, h_zero)


ALGORITHMS = [
    ("UCS", ucs.solve),
    ("A* (h = 0)", astar_h_zero),
    ("A*", astar.solve),
    ("IDA*", ida_star.solve),
]
# ---------------------------------------------------------------
# The worked example from the spec
# ---------------------------------------------------------------
route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
    Request("Q5", "A", "Z", 20),   # invalid: Z is not on the route
]
for name, solve in ALGORITHMS:
    # Bike (1 seat): the best is Q2 + Q3 = Rs.100
    bike = solve(Problem(route, "Bike", requests))
    assert bike["total_fare"] == 100, name + ": Bike fare"
    assert sorted(bike["accepted_ids"]) == ["Q2", "Q3"], name + ": Bike accepted"
    assert bike["valid"] == True
    assert bike["timed_out"] == False
    assert bike["invalid_ids"] == ["Q5"]
    # Auto (3 seats) and Car (4 seats): every valid request fits = 190
    assert solve(Problem(route, "Auto", requests))["total_fare"] == 190
    assert solve(Problem(route, "Car", requests))["total_fare"] == 190
    # Five requests on one segment, Auto holds 3: keep the best three
    five = [
        Request("Q1", "A", "B", 10),
        Request("Q2", "A", "B", 20),
        Request("Q3", "A", "B", 30),
        Request("Q4", "A", "B", 40),
        Request("Q5", "A", "B", 50),
    ]
    r5 = solve(Problem(route, "Auto", five))
    assert r5["total_fare"] == 120, name + ": five requests"
    assert sorted(r5["accepted_ids"]) == ["Q3", "Q4", "Q5"]
    # No valid requests: empty answer, still valid
    zero = solve(Problem(route, "Bike", [Request("Q1", "A", "Z", 10)]))
    assert zero["accepted_ids"] == []
    assert zero["total_fare"] == 0
    assert zero["valid"] == True
    assert zero["timed_out"] == False
    # A time limit that has already passed must set timed_out
    late = solve(Problem(route, "Bike", requests), time_limit=-1)
    assert late["timed_out"] == True, name + ": timeout flag"
    assert late["valid"] == True
    print(name + ": small tests passed")
# ---------------------------------------------------------------
# IDA* extra information
# ---------------------------------------------------------------
r = ida_star.solve(Problem(route, "Bike", requests))
assert r["rounds"] >= 1
assert r["overhead_nodes"] <= r["nodes_explored"]
print("IDA*: rounds =", r["rounds"], "| overhead nodes =", r["overhead_nodes"])
# ---------------------------------------------------------------
# Real dataset cases: every algorithm must match the reference DP
# ---------------------------------------------------------------
with open("data/testcases.json") as f:
    cases = json.load(f)
print()
print("case".ljust(13) + "DP fare".ljust(9) +
      "UCS nodes".ljust(11) + "A*(h=0)".ljust(10) +
      "A* nodes".ljust(10) + "IDA* nodes".ljust(12) + "IDA* rounds")
for case in cases:
    problem = load_case(case["case_id"])
    best = dp_solve(problem)["total_fare"]
    nodes = {}
    rounds = 0
    for name, solve in ALGORITHMS:
        result = solve(problem, 30)
        assert result["valid"] == True, case["case_id"] + " " + name
        assert result["timed_out"] == False, case["case_id"] + " " + name
        assert result["total_fare"] == best, (
            case["case_id"] + " " + name + ": got " +
            str(result["total_fare"]) + ", expected " + str(best))
        nodes[name] = result["nodes_explored"]
        if name == "IDA*":
            rounds = result["rounds"]
    print(case["case_id"].ljust(13) + str(best).ljust(9) +
          str(nodes["UCS"]).ljust(11) + str(nodes["A* (h = 0)"]).ljust(10) +
          str(nodes["A*"]).ljust(10) + str(nodes["IDA*"]).ljust(12) +
          str(rounds))
print("\nAll Person 2 algorithm tests passed!")