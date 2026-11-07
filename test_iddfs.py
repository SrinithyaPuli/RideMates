# test_iddfs.py
from problem import Request, Problem, load_case
from algorithms import iddfs, dls, dfs

route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
    Request("Q5", "A", "Z", 20),   # invalid
]
bike = Problem(route, "Bike", requests)   # m = 4

# same answer as the spec: Q2 + Q3 = Rs.100
r = iddfs.solve(bike)
assert r["total_fare"] == 100
assert sorted(r["accepted_ids"]) == ["Q2", "Q3"]
assert r["valid"] == True
assert r["timed_out"] == False
assert r["invalid_ids"] == ["Q5"]

# overhead = nodes of rounds 1..m-1, total = DFS nodes + overhead
expected_overhead = 0
for limit in [1, 2, 3]:
    expected_overhead += dls.solve(bike, depth_limit=limit)["nodes_explored"]
assert r["overhead_nodes"] == expected_overhead
assert r["nodes_explored"] == dfs.solve(bike)["nodes_explored"] + expected_overhead
assert r["overhead_nodes"] > 0

# Auto: all four valid requests fit
assert iddfs.solve(Problem(route, "Auto", requests))["total_fare"] == 190

# zero valid requests: empty, valid, no overhead
zero = iddfs.solve(Problem(route, "Bike", [Request("Q1", "A", "Z", 10)]))
assert zero["accepted_ids"] == []
assert zero["total_fare"] == 0
assert zero["valid"] == True
assert zero["timed_out"] == False
assert zero["overhead_nodes"] == 0

# time limit already passed
late = iddfs.solve(bike, time_limit=-1)
assert late["timed_out"] == True
assert late["valid"] == True
print("IDDFS small tests passed")

# real cases: same fare as DFS, extra work = overhead
for name in ["bike_6_1", "auto_6_1", "car_6_1", "bike_10_1", "auto_10_1", "car_10_1"]:
    p = load_case(name)
    d = dfs.solve(p)
    i = iddfs.solve(p)
    assert i["valid"] == True
    assert i["total_fare"] == d["total_fare"]
    assert i["nodes_explored"] == d["nodes_explored"] + i["overhead_nodes"]
    print(name, "fare:", i["total_fare"],
          "DFS nodes:", d["nodes_explored"],
          "IDDFS nodes:", i["nodes_explored"],
          "overhead:", i["overhead_nodes"])
print("IDDFS real-case tests passed")