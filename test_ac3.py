
from problem import Request, Problem
from algorithms.ac3 import solve

route = ["A", "B", "C", "D", "E"]

requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40)
]


# -------------------------
# TEST 1: BIKE (Capacity 1)
# -------------------------

print("========== BIKE ==========")

p1 = Problem(route, "Bike", requests)
result1 = solve(p1, time_limit=30)

print("Accepted:", result1["accepted_ids"])
print("Rejected:", result1["rejected_ids"])
print("Total fare:", result1["total_fare"])
print("Occupancy:", result1["occupancy"])
print("Valid:", result1["valid"])
print("Backtracks:", result1["backtracks"])
print("Domain reduction:", result1["domain_reduction"])

assert result1["total_fare"] == 100
assert set(result1["accepted_ids"]) == {"Q2", "Q3"}
assert result1["valid"] is True


# -------------------------
# TEST 2: AUTO (Capacity 3)
# -------------------------

print("\n========== AUTO ==========")

auto_requests = [
    Request("Q1", "A", "B", 10),
    Request("Q2", "A", "B", 20),
    Request("Q3", "A", "B", 30),
    Request("Q4", "A", "B", 40)
]

p2 = Problem(route, "Auto", auto_requests)
result2 = solve(p2, time_limit=30)

print("Accepted:", result2["accepted_ids"])
print("Rejected:", result2["rejected_ids"])
print("Total fare:", result2["total_fare"])
print("Occupancy:", result2["occupancy"])
print("Valid:", result2["valid"])
print("Backtracks:", result2["backtracks"])
print("Domain reduction:", result2["domain_reduction"])

assert result2["total_fare"] == 90
assert set(result2["accepted_ids"]) == {"Q2", "Q3", "Q4"}
assert result2["valid"] is True


# -------------------------
# TEST 3: CAR (Capacity 4)
# -------------------------

print("\n========== CAR ==========")

p3 = Problem(route, "Car", auto_requests)
result3 = solve(p3, time_limit=30)

print("Accepted:", result3["accepted_ids"])
print("Rejected:", result3["rejected_ids"])
print("Total fare:", result3["total_fare"])
print("Occupancy:", result3["occupancy"])
print("Valid:", result3["valid"])
print("Backtracks:", result3["backtracks"])
print("Domain reduction:", result3["domain_reduction"])

assert result3["total_fare"] == 100
assert set(result3["accepted_ids"]) == {"Q1", "Q2", "Q3", "Q4"}
assert result3["valid"] is True


print("All AC-3 vehicle tests passed!")
