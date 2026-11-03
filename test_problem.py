# test_problem.py
# One test file for problem.py Part A (filter) and Part B (Problem class).
import time
from problem import (Request, Problem, filter_requests, capacity_ok,
                     can_accept, make_result)
route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
    Request("Q5", "A", "Z", 20),   # Z is not on the route -> invalid
    Request("Q6", "C", "B", 25),   # wrong order -> invalid
]

# ---------- Part A: the filter ----------
valid, invalid = filter_requests(route, requests)
assert [r.id for r in valid] == ["Q1", "Q3", "Q2", "Q4"]
assert [r.id for r in invalid] == ["Q5", "Q6"]

# tie rule: same pickup, so the id NUMBER decides (Q2 before Q10)
tie = [Request("Q10", "A", "B", 10), Request("Q2", "A", "C", 20)]
valid_tie, _ = filter_requests(route, tie)
assert [r.id for r in valid_tie] == ["Q2", "Q10"]
print("Part A tests passed")

# ---------- Part B: the Problem class ----------
p = Problem(route, "Bike", requests)

assert p.m == 4
assert p.capacity == 1
assert p.invalid_ids == ["Q5", "Q6"]
assert p.total_fare == 190

# sorted order is Q1, Q3, Q2, Q4 -> k = 0, 1, 2, 3
assert [r.id for r in p.requests] == ["Q1", "Q3", "Q2", "Q4"]
assert p.segments(0) == [0, 1]       # Q1: A->C
assert p.segments(1) == [0]          # Q3: A->B
assert p.segments(2) == [1, 2, 3]    # Q2: B->E
assert p.segments(3) == [2, 3]       # Q4: C->E
assert p.fare(2) == 70

# the spec's best answer: Q3 + Q2 = Rs.100, no shared segment
assert p.occupancy((1, 2)) == [1, 1, 1, 1]
# Q1 + Q3 clash on segment 0 (2 passengers, but a Bike holds 1)
assert p.occupancy((0, 1)) == [2, 1, 0, 0]

# vehicle capacities
assert Problem(route, "Auto", requests).capacity == 3
assert Problem(route, "Car", requests).capacity == 4

# a wrong vehicle name must give an error
try:
    Problem(route, "Truck", requests)
    assert False, "Truck should have been rejected"
except ValueError:
    pass
print("Part B tests passed")

print("All problem tests passed")

# ---------- Part C: capacity functions ----------
# Bike example: k=0 is Q1 (A->C), k=1 is Q3 (A->B), k=2 is Q2 (B->E), k=3 is Q4 (C->E)
assert capacity_ok(p, ()) == True            # nothing accepted
assert capacity_ok(p, (1, 2)) == True        # Q3 + Q2, the best answer
assert capacity_ok(p, (0, 3)) == True        # Q1 + Q4 = Rs.90, feasible
assert capacity_ok(p, (0, 1)) == False       # Q1 + Q3 clash on segment 0
assert capacity_ok(p, (2, 3)) == False       # Q2 + Q4 clash on segments 2, 3

assert can_accept(p, (1,), 2) == True        # Q3 then Q2: fine
assert can_accept(p, (0,), 1) == False       # Q1 then Q3: clash
assert can_accept(p, (1,), 1) == False       # already accepted

# Auto holds 3, so all four requests fit together
auto = Problem(route, "Auto", requests)
assert capacity_ok(auto, (0, 1, 2, 3)) == True
assert capacity_ok(p, (0, 1, 2, 3)) == False  # but not on the Bike

print("Part C tests passed")

# ---------- Part D: make_result ----------
res = make_result(p, "Test", (1, 2), 5, time.time(), 3, False)
assert res["algorithm"] == "Test"
assert res["accepted_ids"] == ["Q3", "Q2"]
assert res["rejected_ids"] == ["Q1", "Q4"]
assert res["invalid_ids"] == ["Q5", "Q6"]
assert res["total_fare"] == 100
assert res["occupancy"] == [1, 1, 1, 1]
assert res["nodes_explored"] == 5
assert res["peak_states"] == 3
assert res["timed_out"] == False
assert res["valid"] == True
assert res["time_sec"] >= 0

# a selection that breaks capacity must be flagged as not valid
bad = make_result(p, "Bad", (0, 1), 1, time.time(), 1, False)
assert bad["valid"] == False
assert bad["total_fare"] == 80
assert bad["occupancy"] == [2, 1, 0, 0]

# extra keys are added
ex = make_result(p, "DLS", (), 1, time.time(), 1, False, {"cutoff": True})
assert ex["cutoff"] == True

# edge case: zero valid requests
zero = Problem(route, "Bike", [Request("Q1", "A", "Z", 10)])
assert zero.m == 0
z = make_result(zero, "Test", (), 0, time.time(), 0, False)
assert z["accepted_ids"] == []
assert z["rejected_ids"] == []
assert z["invalid_ids"] == ["Q1"]
assert z["total_fare"] == 0
assert z["occupancy"] == [0, 0, 0, 0]
assert z["valid"] == True
assert z["timed_out"] == False

print("Part D tests passed")