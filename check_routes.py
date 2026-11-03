# check_routes.py
import json
from graph import load_graph, validate_route

graph = load_graph("data/graph.json")
with open("data/routes.json") as f:
    routes = json.load(f)

for r in routes:
    ok, message = validate_route(graph, r["nodes"])
    print(r["route_id"], "->", ok, message)
    assert ok == r["should_be_valid"], r["route_id"] + " does not match"

print("All routes match their should_be_valid flag")