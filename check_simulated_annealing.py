
from problem import load_case, capacity_ok
from simulated_annealing import solve


CASE_IDS = [
    "bike_6_1", "auto_6_1", "car_6_1",
    "bike_10_1", "auto_10_1", "car_10_1",
    "bike_15_1", "auto_15_1", "car_15_1",
    "bike_20_1", "auto_20_1", "car_20_1",
    "bike_none_1", "auto_none_1", "car_none_1"
]

SEEDS = range(10)


def check_case(case_id):
    problem = load_case(case_id)

    for seed in SEEDS:
        result = solve(problem, time_limit=30, seed=seed)

        # Check result validity.
        assert result["valid"], (
            f"{case_id}, seed {seed}: Invalid result"
        )

        # Check vehicle capacity.
        accepted_indices = [
            k for k, request in enumerate(problem.requests)
            if request.id in result["accepted_ids"]
        ]

        assert capacity_ok(problem, accepted_indices), (
            f"{case_id}, seed {seed}: Capacity exceeded"
        )

        # Check accepted and rejected request IDs.
        all_valid_ids = {
            request.id for request in problem.requests
        }

        accepted = set(result["accepted_ids"])
        rejected = set(result["rejected_ids"])

        assert accepted.issubset(all_valid_ids)
        assert rejected.issubset(all_valid_ids)
        assert accepted | rejected == all_valid_ids
        assert accepted & rejected == set()

        # Check invalid request IDs.
        assert set(result["invalid_ids"]) == set(problem.invalid_ids)

        # Check total fare.
        fare_map = {
            request.id: request.fare
            for request in problem.requests
        }

        expected_fare = sum(
            fare_map[request_id]
            for request_id in accepted
        )

        assert result["total_fare"] == expected_fare, (
            f"{case_id}, seed {seed}: Fare mismatch"
        )

        # Check search statistics.
        assert result["nodes_explored"] >= 0
        assert result["peak_states"] == 1

        # Check timeout.
        assert not result["timed_out"], (
            f"{case_id}, seed {seed}: Unexpected timeout"
        )

    print(f"PASS: {case_id} | All 10 seeds passed")


def check_repeatability():
    problem = load_case("auto_10_1")

    first = solve(problem, time_limit=30, seed=5)
    second = solve(problem, time_limit=30, seed=5)

    assert first["accepted_ids"] == second["accepted_ids"]
    assert first["total_fare"] == second["total_fare"]

    print("PASS: Same-seed repeatability test")


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
    print("\nSIMULATED ANNEALING TEST RESULTS\n")

    for case_id in CASE_IDS:
        check_case(case_id)

    check_repeatability()
    check_zero_time_timeout()

    print("\nALL SIMULATED ANNEALING TESTS PASSED!")


if __name__ == "__main__":
    main()
