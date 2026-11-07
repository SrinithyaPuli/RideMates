import time

from problem import Request, Problem
from algorithms.csp import solve

# Sample route
route = ["A", "B", "C", "D", "E"]

# Sample requests
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
]

# Create Bike problem
p = Problem(route, "Bike", requests)

# Run CSP
result = solve(p, time_limit=30)

# Display result
print("Algorithm:", result["algorithm"])
print("Accepted:", result["accepted_ids"])
print("Rejected:", result["rejected_ids"])
print("Total Fare: Rs.", result["total_fare"])
print("Occupancy:", result["occupancy"])
print("Nodes Explored:", result["nodes_explored"])
print("Backtracks:", result["backtracks"])
print("Peak States:", result["peak_states"])
print("Capacity Valid:", result["valid"])
print("Timed Out:", result["timed_out"])

# Check expected answer
assert result["total_fare"] == 100
assert set(result["accepted_ids"]) == {"Q2", "Q3"}
assert result["valid"] == True

print("All CSP tests passed!\n")