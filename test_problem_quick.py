# test_problem_quick.py
from problem import Request, filter_requests

route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
    Request("Q5", "A", "Z", 20),   # Z is not on the route -> invalid
    Request("Q6", "C", "B", 25),   # wrong order -> invalid
]

valid, invalid = filter_requests(route, requests)

valid_ids = [r.id for r in valid]
invalid_ids = [r.id for r in invalid]
print("valid  :", valid_ids)
print("invalid:", invalid_ids)

assert valid_ids == ["Q1", "Q3", "Q2", "Q4"]
assert invalid_ids == ["Q5", "Q6"]
print("All problem Part A tests passed")
