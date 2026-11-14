# check_integration.py  (final version)
# Person 1: runs all 12 algorithms on every test case and reports
# anything that breaks the team contract.
# If the reference solver is missing or broken, the exact answer from
# DFS is used instead, and the output says so.

import json
import importlib
from problem import load_case

TIME_LIMIT = 10          # seconds per run

# (name, possible file names with the contract name first,
#  True = must equal the best fare when it finishes)
ALGORITHMS = [
    ("BFS", ["bfs"], True),
    ("DFS", ["dfs"], True),
    ("DLS", ["dls"], True),
    ("IDDFS", ["iddfs"], True),
    ("UCS", ["ucs"], True),
    ("A*", ["astar"], True),
    ("IDA*", ["idastar", "ida_star"], True),
    ("CSP", ["csp"], True),
    ("AC-3", ["ac3"], True),
    ("Greedy", ["greedy"], False),
    ("Hill Climbing", ["hill_climbing"], False),
    ("Simulated Annealing", ["simulated_annealing"], False),
]

REQUIRED = ["algorithm", "accepted_ids", "rejected_ids", "invalid_ids",
            "total_fare", "occupancy", "nodes_explored", "time_sec",
            "peak_states", "timed_out", "valid"]

problems = []
timeouts = []


def report(case_id, name, message):
    problems.append(case_id + " | " + name + " | " + message)


# ----- load every algorithm -----
modules = {}
for name, file_names, must_match in ALGORITHMS:
    first_error = ""
    for i in range(len(file_names)):
        try:
            modules[name] = importlib.import_module("algorithms." + file_names[i])
            if i > 0:
                report("(file name)", name, "file is algorithms/" +
                       file_names[i] + ".py but the contract name is "
                       "algorithms/" + file_names[0] + ".py")
            break
        except Exception as e:
            if i == 0:
                first_error = str(e)
    if name not in modules:
        report("(import)", name, "cannot import algorithms/" +
               file_names[0] + ".py: " + first_error)

# ----- load the reference solver -----
reference_function = None
try:
    import reference_dp
    if hasattr(reference_dp, "solve_reference"):
        reference_function = reference_dp.solve_reference
    elif hasattr(reference_dp, "solve"):
        reference_function = reference_dp.solve
        report("(function name)", "Reference DP",
               "function is solve(...) but the contract name is "
               "solve_reference(...)")
    else:
        report("(import)", "Reference DP",
               "reference_dp.py has no solve_reference or solve function")
except Exception as e:
    report("(import)", "Reference DP",
           "cannot import reference_dp.py: " + str(e))

# ----- run every case -----
with open("data/testcases.json") as f:
    cases = json.load(f)

for c in cases:
    case_id = c["case_id"]
    problem = load_case(case_id)

    fare_of = {}
    for r in problem.requests:
        fare_of[r.id] = r.fare
    valid_ids = sorted(fare_of.keys())

    # best fare: from the reference solver, or DFS as a stand-in
    optimal = None
    source = "nowhere"
    if reference_function is not None:
        try:
            ref = reference_function(problem)
            optimal = ref["total_fare"]
            source = "reference"
            if not ref["valid"]:
                report(case_id, "Reference DP", "result is not capacity valid")
        except Exception as e:
            report(case_id, "Reference DP", "crashed: " + str(e))
    if optimal is None and "DFS" in modules:
        d = modules["DFS"].solve(problem, TIME_LIMIT)
        if not d["timed_out"]:
            optimal = d["total_fare"]
            source = "DFS stand-in"

    for name, file_names, must_match in ALGORITHMS:
        if name not in modules:
            continue
        try:
            r = modules[name].solve(problem, TIME_LIMIT)
        except Exception as e:
            report(case_id, name, "crashed: " + str(e))
            continue

        # 1. all contract keys are present
        missing = [k for k in REQUIRED if k not in r]
        if len(missing) > 0:
            report(case_id, name, "missing result keys: " + str(missing))
            continue

        # 2. capacity respected
        if r["valid"] != True:
            report(case_id, name, "valid flag is False (capacity broken)")
        for count in r["occupancy"]:
            if count > problem.capacity:
                report(case_id, name, "occupancy above capacity")
                break

        # 3. result is consistent with the problem
        together = sorted(r["accepted_ids"] + r["rejected_ids"])
        if together != valid_ids:
            report(case_id, name, "accepted + rejected ids are not "
                   "exactly the valid requests")
        if sorted(r["invalid_ids"]) != sorted(problem.invalid_ids):
            report(case_id, name, "invalid_ids does not match the filter")
        real_fare = 0
        for request_id in r["accepted_ids"]:
            if request_id in fare_of:
                real_fare += fare_of[request_id]
        if real_fare != r["total_fare"]:
            report(case_id, name, "total_fare " + str(r["total_fare"]) +
                   " does not match accepted requests (" + str(real_fare) + ")")

        # 4. fare compared with the best fare
        if r["timed_out"]:
            timeouts.append(case_id + " | " + name)
        if optimal is not None:
            if r["total_fare"] > optimal:
                report(case_id, name, "fare " + str(r["total_fare"]) +
                       " is ABOVE the best fare " + str(optimal))
            if must_match and not r["timed_out"] and r["total_fare"] != optimal:
                report(case_id, name, "fare " + str(r["total_fare"]) +
                       " but best fare is " + str(optimal) +
                       " (exact algorithm should match)")

    print("checked", case_id, "(best fare", optimal, "from", source + ")")

print()
print("Timed out runs:", len(timeouts))
for t in timeouts:
    print("  ", t)
print()
if len(problems) == 0:
    print("NO PROBLEMS FOUND. All algorithms follow the contract.")
else:
    print(len(problems), "PROBLEM(S) FOUND:")
    for p in problems:
        print("  ", p)