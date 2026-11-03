
import json
import random
from pathlib import Path

DATA_DIR = Path("data")

# Each request file is generated for one predefined route.
ROUTE_MAPPING = {
    6: "R1",
    10: "R4",
    15: "R5",
    20: "R6"
}

def load_routes():
    with open(DATA_DIR / "routes.json", "r") as file:
        routes = json.load(file)

    return {
        route["route_id"]: route["nodes"]
        for route in routes
        if route["should_be_valid"]
    }


def generate_requests(route, count, seed):
    rng = random.Random(seed)

    # Generate every possible forward pickup-dropoff pair.
    possible_pairs = [
        (route[i], route[j])
        for i in range(len(route))
        for j in range(i + 1, len(route))
    ]

    if count > len(possible_pairs):
        raise ValueError("Not enough valid pickup-dropoff pairs.")

    selected_pairs = rng.sample(possible_pairs, count)

    requests = []

    # Generate the required valid requests.
    for i, (pickup, dropoff) in enumerate(selected_pairs, start=1):
        requests.append({
            "id": f"Q{i}",
            "pickup": pickup,
            "dropoff": dropoff,
            "fare": rng.randint(30, 150)
        })

    # Add three invalid requests.
    outside_nodes = [
        node for node in "ABCDEFGHIJKLMNOPQRST"
        if node not in route
    ]

    # Invalid request 1: pickup outside the route.
    requests.append({
        "id": f"Q{count + 1}",
        "pickup": rng.choice(outside_nodes),
        "dropoff": route[0],
        "fare": rng.randint(30, 150)
    })

    # Invalid request 2: dropoff outside the route.
    requests.append({
        "id": f"Q{count + 2}",
        "pickup": route[0],
        "dropoff": rng.choice(outside_nodes),
        "fare": rng.randint(30, 150)
    })

    # Invalid request 3: pickup comes after dropoff.
    pickup, dropoff = selected_pairs[0]
    requests.append({
        "id": f"Q{count + 3}",
        "pickup": dropoff,
        "dropoff": pickup,
        "fare": rng.randint(30, 150)
    })

    return requests


def generate_none_valid():
    requests = [
        {"id": "Q1", "pickup": "E", "dropoff": "A", "fare": 60},
        {"id": "Q2", "pickup": "A", "dropoff": "Z", "fare": 80},
        {"id": "Q3", "pickup": "Z", "dropoff": "T", "fare": 45},
        {"id": "Q4", "pickup": "D", "dropoff": "B", "fare": 70}
    ]

    with open(DATA_DIR / "requests_none_valid.json", "w") as file:
        json.dump(requests, file, indent=4)


def generate_testcases():
    testcases = []

    for size, route_id in ROUTE_MAPPING.items():
        request_file = f"requests_{size}_seed1.json"

        for vehicle in ["Bike", "Auto", "Car"]:
            testcases.append({
                "case_id": f"{vehicle.lower()}_{size}_1",
                "route_id": route_id,
                "vehicle": vehicle,
                "request_file": request_file
            })

    # Add zero-valid-request cases for all three vehicles.
    for vehicle in ["Bike", "Auto", "Car"]:
        testcases.append({
            "case_id": f"{vehicle.lower()}_none_1",
            "route_id": "R1",
            "vehicle": vehicle,
            "request_file": "requests_none_valid.json"
        })

    with open(DATA_DIR / "testcases.json", "w") as file:
        json.dump(testcases, file, indent=4)


def main():
    DATA_DIR.mkdir(exist_ok=True)

    routes = load_routes()

    for size, route_id in ROUTE_MAPPING.items():
        requests = generate_requests(
            routes[route_id],
            size,
            seed=1
        )

        filename = DATA_DIR / f"requests_{size}_seed1.json"

        with open(filename, "w") as file:
            json.dump(requests, file, indent=4)

        print(f"Created {filename}: {size} valid + 3 invalid requests")

    generate_none_valid()
    print("Created requests_none_valid.json")

    generate_testcases()
    print("Created testcases.json")


if __name__ == "__main__":
    main()
