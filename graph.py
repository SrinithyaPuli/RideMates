# graph.py
# Person 1: graph class, loader and route validator.
# Roads are two-way, so every road is stored in both directions.

import json


class Graph:
    def __init__(self, nodes, edges):
        # nodes: list of names, like ["A", "B", ...]
        # edges: list of dicts, like {"a": "A", "b": "B", "distance": 4.0}
        self.nodes = list(nodes)
        self.edge_count = 0

        # roads[x] = {neighbour: distance}
        self.roads = {}
        for node in self.nodes:
            self.roads[node] = {}

        for edge in edges:
            a = edge["a"]
            b = edge["b"]
            d = edge["distance"]

            if a not in self.roads or b not in self.roads:
                raise ValueError("Road " + str(a) + "-" + str(b) +
                                 " uses a location that does not exist")
            if d <= 0:
                raise ValueError("Road " + str(a) + "-" + str(b) +
                                 " must have a positive distance")
            if b in self.roads[a]:
                raise ValueError("Road " + str(a) + "-" + str(b) +
                                 " is written twice")

            # two-way road: store in both directions
            self.roads[a][b] = d
            self.roads[b][a] = d
            self.edge_count += 1

    def has_road(self, a, b):
        # True if a road joins a and b
        if a not in self.roads:
            return False
        return b in self.roads[a]

    def distance(self, a, b):
        # distance of the road between a and b
        return self.roads[a][b]


def load_graph(path):
    # Reads graph.json and builds a Graph.
    # Contract rule: exactly 20 nodes and 36 unique roads.
    with open(path) as f:
        data = json.load(f)

    graph = Graph(data["nodes"], data["edges"])

    if len(graph.nodes) != 20:
        raise ValueError("Graph must have exactly 20 nodes, found " +
                         str(len(graph.nodes)))
    if graph.edge_count != 36:
        raise ValueError("Graph must have exactly 36 roads, found " +
                         str(graph.edge_count))
    return graph


def validate_route(graph, route):
    # Returns (True, "") if the route is valid,
    # or (False, "message") explaining the first problem found.

    # Rule 1: at least 2 locations
    if len(route) < 2:
        return (False, "Route must have at least 2 locations")

    # Rule 2: every location exists
    for place in route:
        if place not in graph.roads:
            return (False, "Location " + str(place) + " does not exist")

    # Rule 3: no location appears twice
    seen = []
    for place in route:
        if place in seen:
            return (False, "Location " + place + " appears more than once")
        seen.append(place)

    # Rule 4: every consecutive pair is joined by a road
    for i in range(len(route) - 1):
        if not graph.has_road(route[i], route[i + 1]):
            return (False, "No road between " + route[i] +
                    " and " + route[i + 1])

    return (True, "")