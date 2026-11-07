
from problem import load_case, capacity_ok
from hill_climbing import solve


CASE_IDS = [
    "bike_6_1", "auto_6_1", "car_6_1",
    "bike_10_1", "auto_10_1", "car_10_1",
    "bike_15_1", "auto_15_1", "car_15_1",
    "bike_20_1", "auto_20_1", "car_20_1",
    "bike_none_1", "auto_none_1", "car_none_1"
]


def check_case(case_id):
    problem = load_case(case_id)

    result = solve(problem, time_limit=30, seed=0)

    # Check that the result is valid.
    assert result["valid"], f"{case_id}: Invalid result"

    # Check vehicle capacity.
    accepted_indices = [
        k for k, request in enumerate(problem.requests)
        if request.id in result["accepted_ids"]
    ]

    assert capacity_ok(problem, accepted_indices), (
        f"{case_id}: Capacity exceeded"
    )

    # Check accepted and rejected requests.
    all_valid_ids = {
        request.id for request in problem.requests
    }

    assert set(result["accepted_ids"]).issubset(all_valid_ids)
    assert set(result["rejected_ids"]).issubset(all_valid_ids)

    assert (
        set(result["accepted_ids"]) |
        set(result["rejected_ids"])
    ) == all_valid_ids

    assert (
        set(result["accepted_ids"]) &
        set(result["rejected_ids"])
    ) == set()

    # Check invalid request IDs.
    assert set(result["invalid_ids"]) == set(problem.invalid_ids)

    # Check total fare.
    fare_map = {
        request.id: request.fare
        for request in problem.requests
    }

    expected_fare = sum(
        fare_map[request_id]
        for request_id in result["accepted_ids"]
    )

    assert result["total_fare"] == expected_fare

    # Check search statistics.
    assert result["nodes_explored"] >= 0
    assert result["peak_states"] == 1

    # These normal test cases should finish within 30 seconds.
    assert not result["timed_out"], (
        f"{case_id}: Unexpected timeout"
    )

    # Check repeatability with the same seed.
    repeated = solve(problem, time_limit=30, seed=0)

    assert result["accepted_ids"] == repeated["accepted_ids"]
    assert result["total_fare"] == repeated["total_fare"]

    print(
        f"PASS: {case_id} | "
        f"Accepted: {result['accepted_ids']} | "
        f"Fare: Rs.{result['total_fare']} | "
        f"Nodes: {result['nodes_explored']}"
    )


def check_zero_time_timeout():
    problem = load_case("bike_6_1")

    result = solve(problem, time_limit=0, seed=0)

    assert result["timed_out"]
    assert result["valid"]
    assert result["total_fare"] == 0
    assert result["accepted_ids"] == []
    assert result["peak_states"] == 1

    print("PASS: Zero-time timeout test")


def main():
    print("\nHILL CLIMBING TEST RESULTS\n")

    for case_id in CASE_IDS:
        check_case(case_id)

    check_zero_time_timeout()

    print("\nALL HILL CLIMBING TESTS PASSED!")


if __name__ == "__main__":
    main()
