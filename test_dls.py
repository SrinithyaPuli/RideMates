# test_dls.py
from problem import Request, Problem, load_case
from algorithms import dls, dfs

route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
    Request("Q5", "A", "Z", 20),   # invalid
]
bike = Problem(route, "Bike", requests)   # m = 4

# limit equal to m: behaves exactly like DFS, no cutoff
full = dls.solve(bike, depth_limit=4)
assert full["total_fare"] == 100
assert sorted(full["accepted_ids"]) == ["Q2", "Q3"]
assert full["cutoff"] == False
assert full["valid"] == True
assert full["nodes_explored"] == dfs.solve(bike)["nodes_explored"]

# no limit given: same as m
default = dls.solve(bike)
assert default["total_fare"] == 100
assert default["cutoff"] == False

# limit above m: still the same as DFS
above = dls.solve(bike, depth_limit=10)
assert above["total_fare"] == 100
assert above["cutoff"] == False

# limit below m: cutoff, no solution, empty result
for limit in [0, 1, 2, 3]:
    r = dls.solve(bike, depth_limit=limit)
    assert r["cutoff"] == True
    assert r["accepted_ids"] == []
    assert r["total_fare"] == 0
    assert r["valid"] == True
    assert r["timed_out"] == False

# exact node counts for tiny limits
assert dls.solve(bike, depth_limit=0)["nodes_explored"] == 1   # root only
assert dls.solve(bike, depth_limit=1)["nodes_explored"] == 3   # root + 2 children

# zero valid requests: nothing to decide, so no cutoff
zero = dls.solve(Problem(route, "Bike", [Request("Q1", "A", "Z", 10)]),
                 depth_limit=0)
assert zero["cutoff"] == False
assert zero["accepted_ids"] == []
assert zero["valid"] == True
print("DLS small tests passed")

# real cases: limit m matches DFS, limit m-1 gives cutoff
for name in ["bike_6_1", "auto_6_1", "car_10_1"]:
    p = load_case(name)
    d = dfs.solve(p)
    same = dls.solve(p, depth_limit=p.m)
    cut = dls.solve(p, depth_limit=p.m - 1)
    assert same["total_fare"] == d["total_fare"]
    assert same["nodes_explored"] == d["nodes_explored"]
    assert same["cutoff"] == False
    assert cut["cutoff"] == True
    assert cut["accepted_ids"] == []
    print(name, "limit m: fare", same["total_fare"], "nodes", same["nodes_explored"],
          "| limit m-1: cutoff, nodes", cut["nodes_explored"])
print("DLS real-case tests passed")