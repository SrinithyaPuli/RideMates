# problem.py  (Part A: Request model and filter)
# Person 1
import time
import json
from graph import load_graph, validate_route

CAPACITY = {"Bike": 1, "Auto": 3, "Car": 4}


def id_number(request_id):
    # "Q12" -> 12. Used so that Q2 comes before Q10.
    if not request_id.startswith("Q") or not request_id[1:].isdigit():
        raise ValueError("Request id must look like Q1, Q2, ... but got " +
                         str(request_id))
    return int(request_id[1:])


class Request:
    def __init__(self, request_id, pickup, dropoff, fare):
        id_number(request_id)  # raises an error if the id format is wrong
        if not isinstance(fare, int) or fare <= 0:
            raise ValueError("Fare of " + request_id +
                             " must be a positive whole number")
        self.id = request_id
        self.pickup = pickup
        self.dropoff = dropoff
        self.fare = fare

    def __repr__(self):
        return (self.id + ": " + self.pickup + "->" + self.dropoff +
                " Rs." + str(self.fare))


def load_requests(path):
    # Reads a request JSON file and returns a list of Request objects.
    with open(path) as f:
        data = json.load(f)

    requests = []
    seen_ids = []
    for item in data:
        r = Request(item["id"], item["pickup"], item["dropoff"], item["fare"])
        if r.id in seen_ids:
            raise ValueError("Request id " + r.id + " appears twice")
        seen_ids.append(r.id)
        requests.append(r)
    return requests


def sort_key(route, request):
    # Sort by pickup position first, then by the number in the id.
    return (route.index(request.pickup), id_number(request.id))


def filter_requests(route, requests):
    # Returns (valid_list, invalid_list).
    # Valid = pickup and dropoff are on the route AND pickup comes first.
    # valid_list is already sorted by pickup position, ties by id number.
    valid = []
    invalid = []

    for r in requests:
        on_route = (r.pickup in route) and (r.dropoff in route)
        if on_route and route.index(r.pickup) < route.index(r.dropoff):
            valid.append(r)
        else:
            invalid.append(r)

    valid.sort(key=lambda r: sort_key(route, r))
    return (valid, invalid)
class Problem:
    def __init__(self, route, vehicle, requests):
        # route: list of locations, vehicle: "Bike", "Auto" or "Car"
        # requests: list of Request objects (valid and invalid mixed)
        if vehicle not in CAPACITY:
            raise ValueError("Vehicle must be Bike, Auto or Car, got " +
                             str(vehicle))

        self.route = list(route)
        self.vehicle = vehicle
        self.capacity = CAPACITY[vehicle]
        self.num_segments = len(self.route) - 1

        # The filter runs here, so algorithms only ever see valid requests
        valid, invalid = filter_requests(self.route, requests)
        self.requests = valid                       # sorted, index k = position
        self.invalid_ids = [r.id for r in invalid]
        self.m = len(self.requests)

        self.total_fare = 0
        for r in self.requests:
            self.total_fare += r.fare

        # segment list for every request, worked out once
        self._segments = []
        for r in self.requests:
            start = self.route.index(r.pickup)
            end = self.route.index(r.dropoff)
            self._segments.append(list(range(start, end)))

    def fare(self, k):
        return self.requests[k].fare

    def segments(self, k):
        return self._segments[k]

    def occupancy(self, accepted):
        # accepted: tuple of request indices, e.g. (0, 2, 5)
        # returns passengers on each segment, e.g. [1, 2, 0, 1]
        counts = [0] * self.num_segments
        for k in accepted:
            for s in self._segments[k]:
                counts[s] += 1
        return counts


def load_case(case_id, data_folder="data"):
    # Builds a Problem from the JSON files, using the contract formats.
    with open(data_folder + "/testcases.json") as f:
        cases = json.load(f)

    case = None
    for c in cases:
        if c["case_id"] == case_id:
            case = c
    if case is None:
        raise ValueError("Test case " + str(case_id) + " not found")

    with open(data_folder + "/routes.json") as f:
        routes = json.load(f)

    route = None
    for r in routes:
        if r["route_id"] == case["route_id"]:
            route = r["nodes"]
    if route is None:
        raise ValueError("Route " + str(case["route_id"]) + " not found")

    graph = load_graph(data_folder + "/graph.json")
    ok, message = validate_route(graph, route)
    if not ok:
        raise ValueError("Route " + case["route_id"] + " is invalid: " + message)

    requests = load_requests(data_folder + "/" + case["request_file"])
    return Problem(route, case["vehicle"], requests)
def capacity_ok(problem, accepted):
    # True if the whole selection respects capacity on every segment.
    # accepted: tuple of request indices, e.g. (0, 2, 5)
    counts = problem.occupancy(accepted)
    for c in counts:
        if c > problem.capacity:
            return False
    return True


def can_accept(problem, accepted, k):
    # True if adding request k to the selection keeps capacity valid.
    if k in accepted:
        return False                      # already accepted

    counts = problem.occupancy(accepted)
    for s in problem.segments(k):         # only the segments k uses
        if counts[s] + 1 > problem.capacity:
            return False
    return True
def make_result(problem, name, accepted, nodes_explored,
                start_time, peak_states, timed_out, extra=None):
    # Builds the result dictionary that every algorithm must return.
    # accepted: sorted tuple of request indices, e.g. (1, 2)
    accepted = tuple(sorted(accepted))

    accepted_ids = []
    rejected_ids = []
    total_fare = 0
    for k in range(problem.m):
        if k in accepted:
            accepted_ids.append(problem.requests[k].id)
            total_fare += problem.fare(k)
        else:
            rejected_ids.append(problem.requests[k].id)

    result = {
        "algorithm": name,
        "accepted_ids": accepted_ids,
        "rejected_ids": rejected_ids,
        "invalid_ids": list(problem.invalid_ids),
        "total_fare": total_fare,
        "occupancy": problem.occupancy(accepted),
        "nodes_explored": nodes_explored,
        "time_sec": time.time() - start_time,
        "peak_states": peak_states,
        "timed_out": timed_out,
        "valid": capacity_ok(problem, accepted),
    }

    # optional extra keys, such as {"cutoff": True} for DLS
    if extra is not None:
        for key in extra:
            result[key] = extra[key]

    return result