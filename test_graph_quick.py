# test_graph_quick.py
from graph import Graph, validate_route

nodes = ["A", "B", "C", "D", "E"]
edges = [
    {"a": "A", "b": "B", "distance": 1.0},
    {"a": "B", "b": "C", "distance": 2.0},
    {"a": "C", "b": "D", "distance": 3.0},
]
g = Graph(nodes, edges)

tests = [
    (["A", "B", "C", "D"], True),        # valid
    (["D", "C", "B"], True),             # valid, roads work both ways
    (["A", "B", "C", "B", "D"], False),  # repeats B
    (["A", "C"], False),                 # no direct road
    (["A"], False),                      # only 1 location
    (["A", "Z"], False),                 # Z does not exist
]

for route, expected in tests:
    ok, message = validate_route(g, route)
    print(route, "->", ok, message)
    assert ok == expected

print("All graph tests passed")