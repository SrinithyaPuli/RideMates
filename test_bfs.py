# test_bfs.py
from problem import Request, Problem, load_case
from algorithms import bfs, dfs

route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
    Request("Q5", "A", "Z", 20),   # invalid
]

# Bike: the spec says the best is Q2 + Q3 = Rs.100
bike = bfs.solve(Problem(route, "Bike", requests))
assert bike["total_fare"] == 100
assert sorted(bike["accepted_ids"]) == ["Q2", "Q3"]
assert bike["valid"] == True
assert bike["timed_out"] == False
assert bike["invalid_ids"] == ["Q5"]

# Auto: all four valid requests fit
auto = bfs.solve(Problem(route, "Auto", requests))
assert auto["total_fare"] == 190

# zero valid requests
zero = bfs.solve(Problem(route, "Bike", [Request("Q1", "A", "Z", 10)]))
assert zero["accepted_ids"] == []
assert zero["total_fare"] == 0
assert zero["valid"] == True
assert zero["timed_out"] == False

# time limit already passed: BFS has no complete selection yet
late = bfs.solve(Problem(route, "Bike", requests), time_limit=-1)
assert late["timed_out"] == True
assert late["accepted_ids"] == []
assert late["valid"] == True
print("BFS small tests passed")

# real cases: BFS must match DFS exactly when both finish
for size in ["6_1", "10_1"]:
    for vehicle in ["bike", "auto", "car"]:
        name = vehicle + "_" + size
        b = bfs.solve(load_case(name))
        d = dfs.solve(load_case(name))
        assert b["valid"] == True
        assert b["total_fare"] == d["total_fare"]
        assert b["nodes_explored"] == d["nodes_explored"]
        print(name, "fare:", b["total_fare"],
              "nodes:", b["nodes_explored"],
              "peak queue (BFS):", b["peak_states"],
              "peak depth (DFS):", d["peak_states"])
print("BFS real-case tests passed")