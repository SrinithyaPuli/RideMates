# problem.py  (Part A: Request model and filter)
# Person 1

import json


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
