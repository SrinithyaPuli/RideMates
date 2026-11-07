
# compare_greedy_dp.py
# Compare Greedy Best-First Search with Reference DP

import json

from problem import load_case
from greedy import solve as greedy_solve
from reference_dp import solve as dp_solve


with open("data/testcases.json") as f:
    cases = json.load(f)


print("\nGREEDY vs DP COMPARISON")
print("=" * 85)

print(
    f"{'Test Case':<18}"
    f"{'Greedy Fare':<15}"
    f"{'DP Fare':<12}"
    f"{'Fare Gap':<12}"
    f"{'Greedy Nodes':<15}"
)

print("-" * 85)

all_passed = True

for case in cases:

    case_id = case["case_id"]
    problem = load_case(case_id)

    greedy_result = greedy_solve(problem)
    dp_result = dp_solve(problem)

    greedy_fare = greedy_result["total_fare"]
    dp_fare = dp_result["total_fare"]

    gap = dp_fare - greedy_fare

    # Basic result checks
    passed = (
        greedy_result["valid"]
        and dp_result["valid"]
        and not greedy_result["timed_out"]
        and not dp_result["timed_out"]
        and gap >= 0
    )

    if not passed:
        all_passed = False

    print(
        f"{case_id:<18}"
        f"{greedy_fare:<15}"
        f"{dp_fare:<12}"
        f"{gap:<12}"
        f"{greedy_result['nodes_explored']:<15}"
    )

print("-" * 85)

print(
    "Overall:",
    "ALL COMPARISONS PASSED" if all_passed
    else "CHECK FAILED RESULTS"
)
