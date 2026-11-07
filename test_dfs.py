# test_dfs.py
from problem import Request, Problem, load_case
from algorithms.dfs import solve

route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
    Request("Q5", "A", "Z", 20),   # invalid
]

# Bike: the spec says the best is Q2 + Q3 = Rs.100
bike = solve(Problem(route, "Bike", requests))
assert bike["total_fare"] == 100
assert sorted(bike["accepted_ids"]) == ["Q2", "Q3"]
assert bike["valid"] == True
assert bike["timed_out"] == False
assert bike["invalid_ids"] == ["Q5"]

# Auto holds 3, so all four valid requests fit: 50+70+30+40 = 190
auto = solve(Problem(route, "Auto", requests))
assert auto["total_fare"] == 190
assert auto["valid"] == True

# zero valid requests: empty result, still valid
zero = solve(Problem(route, "Bike", [Request("Q1", "A", "Z", 10)]))
assert zero["accepted_ids"] == []
assert zero["total_fare"] == 0
assert zero["valid"] == True
assert zero["timed_out"] == False

# a time limit that has already passed must give timed_out = True
late = solve(Problem(route, "Bike", requests), time_limit=-1)
assert late["timed_out"] == True
assert late["valid"] == True
print("DFS small tests passed")

# real cases: more capacity can never earn less
for size in ["6_1", "10_1"]:
    fares = []
    for vehicle in ["bike", "auto", "car"]:
        r = solve(load_case(vehicle + "_" + size))
        assert r["valid"] == True
        print(vehicle + "_" + size, "fare:", r["total_fare"],
              "nodes:", r["nodes_explored"],
              "time:", round(r["time_sec"], 2),
              "timed out:", r["timed_out"])
        fares.append(r["total_fare"])
    assert fares[0] <= fares[1] <= fares[2]
print("DFS real-case tests passed")