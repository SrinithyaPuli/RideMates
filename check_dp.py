from problem import load_case, capacity_ok
from reference_dp import solve
import json


def brute_force(problem):
    best_fare = 0

    for mask in range(1 << problem.m):
        accepted = tuple(
            k for k in range(problem.m)
            if mask & (1 << k)
        )

        if capacity_ok(problem, accepted):
            fare = sum(problem.fare(k) for k in accepted)
            best_fare = max(best_fare, fare)

    return best_fare


with open("data/testcases.json") as f:
    cases = json.load(f)

all_passed = True

for case in cases:
    problem = load_case(case["case_id"])

    dp_result = solve(problem)
    expected = brute_force(problem)

    passed = dp_result["total_fare"] == expected
    all_passed = all_passed and passed

    print(
        case["case_id"],
        "| DP:", dp_result["total_fare"],
        "| Expected:", expected,
        "|", "PASS" if passed else "FAIL"
    )

print("\nOverall:", "ALL PASSED" if all_passed else "SOME FAILED")