
# check_greedy.py
# Tests for Greedy Best-First Search

from greedy import solve
from problem import load_case

case_ids = [
    "bike_6_1", "auto_6_1", "car_6_1",
    "bike_10_1", "auto_10_1", "car_10_1",
    "bike_15_1", "auto_15_1", "car_15_1",
    "bike_20_1", "auto_20_1", "car_20_1",
    "bike_none_1", "auto_none_1", "car_none_1"
]

print("\nGREEDY BEST-FIRST SEARCH TESTING")
print("=" * 55)

passed = 0

for case_id in case_ids:

    problem = load_case(case_id)
    result = solve(problem)

    # Check that the result is valid.
    assert result["valid"], case_id + ": Invalid capacity"

    # Check accepted and rejected requests.
    assert set(result["accepted_ids"]).isdisjoint(
        set(result["rejected_ids"])
    ), case_id + ": Duplicate classification"

    assert (
        set(result["accepted_ids"]) |
        set(result["rejected_ids"])
    ) == {r.id for r in problem.requests}, (
        case_id + ": Missing or extra requests"
    )

    # Check invalid requests.
    assert result["invalid_ids"] == problem.invalid_ids

    # Check total fare.
    expected_fare = sum(
        r.fare for r in problem.requests
        if r.id in result["accepted_ids"]
    )

    assert result["total_fare"] == expected_fare

    # Check occupancy.
    assert result["occupancy"] == problem.occupancy(
        tuple(i for i, r in enumerate(problem.requests)
              if r.id in result["accepted_ids"])
    )

    assert result["nodes_explored"] >= 0
    assert result["peak_states"] >= 1

    print(
        case_id,
        "| Fare:", result["total_fare"],
        "| Accepted:", len(result["accepted_ids"]),
        "| Nodes:", result["nodes_explored"],
        "| Valid:", result["valid"]
    )

    passed += 1

print("=" * 55)
print("Passed:", passed, "/", len(case_ids))
print("ALL GREEDY TESTS PASSED!")
