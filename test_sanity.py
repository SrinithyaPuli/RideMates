# These checks tell us quickly if something in the project is broken,
# BEFORE we trust any experiment results. 
# Every check prints a FAIL line if it breaks, and the program keeps going,
# so one run shows ALL the problems. At the end you get a summary.
# If an algorithm file is missing, it is skipped with a note.
import importlib
import json
import random
from problem import (Request, Problem, load_case, load_requests,
                     filter_requests, capacity_ok, can_accept)
from graph import load_graph, validate_route
from reference_dp import solve as dp_solve
from algorithms.heuristic import h_zero, h_main
TIME_LIMIT = 10          # seconds per algorithm run
# (display name, module name, kind)
#   exact  = must find the best answer when it finishes
#   approx = may be lower than the best, but never higher
#   random = like approx, and also needs a seed
ALGORITHMS = [
    ("BFS", "bfs", "exact"),
    ("DFS", "dfs", "exact"),
    ("DLS", "dls", "exact"),
    ("IDDFS", "iddfs", "exact"),
    ("UCS", "ucs", "exact"),
    ("A*", "astar", "exact"),
    ("IDA*", "ida_star", "exact"),
    ("CSP", "csp", "exact"),
    ("AC-3", "ac3", "exact"),
    ("Greedy", "greedy", "approx"),
    ("Hill Climbing", "hill_climbing", "random"),
    ("Simulated Annealing", "simulated_annealing", "random"),
]
# These try every accept/reject combination, so they are too slow when
# there are 20 requests. They are skipped on the biggest cases.
BRUTE_FORCE = ["BFS", "DFS", "DLS", "IDDFS"]
BIGGEST_SIZE = 20
failures = []
checks_run = 0


def check(condition, message):
    # Counts a check. If it fails, remember the message and print it.
    global checks_run
    checks_run += 1
    if not condition:
        failures.append(message)
        print("   FAIL:", message)


def get_solver(module_name):
    # Finds solve() in algorithms/<module_name>.py, or in <module_name>.py
    # next to problem.py. Returns None if the file does not exist.
    for prefix in ["algorithms.", ""]:
        try:
            module = importlib.import_module(prefix + module_name)
            return module.solve
        except ModuleNotFoundError:
            pass
    return None


def run(solver, kind, problem, time_limit=TIME_LIMIT):
    if kind == "random":
        return solver(problem, time_limit, seed=0)
    return solver(problem, time_limit)


def load_solvers():
    solvers = []
    for name, module_name, kind in ALGORITHMS:
        solver = get_solver(module_name)
        if solver is None:
            print("   (skipped, file not found:", module_name + ".py)")
        else:
            solvers.append((name, solver, kind))
    return solvers


def check_well_formed(name, problem, result, label):
    # The rules every result must follow, whatever the algorithm.
    all_ids = [r.id for r in problem.requests]

    check(result["valid"] == True, label + ": " + name + " broke capacity")

    accepted = result["accepted_ids"]
    rejected = result["rejected_ids"]
    check(len(set(accepted) & set(rejected)) == 0,
          label + ": " + name + " put a request in both lists")
    check(sorted(accepted + rejected) == sorted(all_ids),
          label + ": " + name + " lost or repeated a request")
    check(result["invalid_ids"] == problem.invalid_ids,
          label + ": " + name + " invalid ids are wrong")

    fares = {}
    for r in problem.requests:
        fares[r.id] = r.fare
    expected_fare = sum(fares[i] for i in accepted if i in fares)
    check(result["total_fare"] == expected_fare,
          label + ": " + name + " total fare does not match accepted list")

    picked = tuple(k for k in range(problem.m)
                   if problem.requests[k].id in accepted)
    check(result["occupancy"] == problem.occupancy(picked),
          label + ": " + name + " occupancy is wrong")
    check(capacity_ok(problem, picked),
          label + ": " + name + " selection is over capacity")


def make_random_problem(seed):
    # Small random problem (same seed = same problem).
    rng = random.Random(seed)
    route = ["A", "B", "C", "D", "E", "F", "G"]
    vehicle = rng.choice(["Bike", "Auto", "Car"])
    count = rng.randint(3, 8)
    requests = []
    for n in range(1, count + 1):
        i = rng.randint(0, len(route) - 2)
        j = rng.randint(i + 1, len(route) - 1)
        requests.append(Request("Q" + str(n), route[i], route[j],
                                rng.randint(10, 100)))
    return Problem(route, vehicle, requests)


def brute_force_best(problem):
    # Tries every accept/reject combination. Slow, but certainly correct.
    best = 0
    for mask in range(1 << problem.m):
        picked = tuple(k for k in range(problem.m) if mask & (1 << k))
        if capacity_ok(problem, picked):
            fare = sum(problem.fare(k) for k in picked)
            if fare > best:
                best = fare
    return best
# ---------------------------------------------------------------
# Section 1: data files
# ---------------------------------------------------------------
print("\n[1] Data files")
graph = None
try:
    graph = load_graph("data/graph.json")
    check(True, "")
except Exception as error:
    check(False, "graph.json does not load: " + str(error))
with open("data/routes.json") as f:
    routes = json.load(f)
if graph is not None:
    for r in routes:
        ok, message = validate_route(graph, r["nodes"])
        check(ok == r["should_be_valid"],
              "route " + r["route_id"] + " does not match its should_be_valid flag")
with open("data/testcases.json") as f:
    cases = json.load(f)
for case in cases:
    try:
        load_case(case["case_id"])
        check(True, "")
    except Exception as error:
        check(False, case["case_id"] + " does not load: " + str(error))
# same file loaded twice gives the same requests
first = load_requests("data/requests_10_seed1.json")
second = load_requests("data/requests_10_seed1.json")
check([(r.id, r.pickup, r.dropoff, r.fare) for r in first] ==
      [(r.id, r.pickup, r.dropoff, r.fare) for r in second],
      "the same request file gave different requests")
print("   done")
# ---------------------------------------------------------------
# Section 2: request filter
# ---------------------------------------------------------------
print("\n[2] Request filter")
route = ["A", "B", "C", "D"]
test_requests = [
    Request("Q1", "A", "C", 50),   # valid
    Request("Q2", "X", "C", 40),   # pickup not on the route
    Request("Q3", "B", "X", 30),   # drop-off not on the route
    Request("Q4", "C", "A", 20),   # drop-off before pickup
    Request("Q5", "B", "B", 10),   # same stop
]
valid, invalid = filter_requests(route, test_requests)
check([r.id for r in valid] == ["Q1"], "filter kept the wrong requests")
check(sorted(r.id for r in invalid) == ["Q2", "Q3", "Q4", "Q5"],
      "filter rejected the wrong requests")
print("   done")
# ---------------------------------------------------------------
# Section 3: capacity check (worked example from the spec)
# ---------------------------------------------------------------
print("\n[3] Capacity check")
route = ["A", "B", "C", "D", "E"]
example = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
]
bike = Problem(route, "Bike", example)      # order: Q1, Q3, Q2, Q4
auto = Problem(route, "Auto", example)
check(capacity_ok(bike, (1, 2)), "Bike: Q3 + Q2 should fit")
check(capacity_ok(bike, (0, 3)), "Bike: Q1 + Q4 should fit")
check(not capacity_ok(bike, (0, 1)), "Bike: Q1 + Q3 share A-B and must not fit")
check(not capacity_ok(bike, (2, 3)), "Bike: Q2 + Q4 share C-E and must not fit")
check(capacity_ok(auto, (0, 1, 2, 3)), "Auto: all four should fit")
check(can_accept(bike, (1,), 2), "Bike: accepting Q2 after Q3 should be allowed")
check(not can_accept(bike, (0,), 1), "Bike: accepting Q3 after Q1 should be refused")
# four passengers on one segment: Auto (3 seats) must refuse, Car (4) accepts
four = [Request("Q" + str(i), "A", "B", 10) for i in range(1, 5)]
check(not capacity_ok(Problem(route, "Auto", four), (0, 1, 2, 3)),
      "Auto: 4 passengers on one segment must not fit")
check(capacity_ok(Problem(route, "Car", four), (0, 1, 2, 3)),
      "Car: 4 passengers on one segment should fit")
print("   done")
# ---------------------------------------------------------------
# Section 4: known answers (worked example)
# ---------------------------------------------------------------
print("\n[4] Known answers (worked example)")
solvers = load_solvers()
example_with_invalid = example + [Request("Q5", "A", "Z", 20)]
expected = {"Bike": 100, "Auto": 190, "Car": 190}
for name, solver, kind in solvers:
    for vehicle in ["Bike", "Auto", "Car"]:
        problem = Problem(route, vehicle, example_with_invalid)
        result = run(solver, kind, problem)
        check_well_formed(name, problem, result, "example " + vehicle)
        if kind == "exact":
            check(result["total_fare"] == expected[vehicle],
                  name + " got " + str(result["total_fare"]) + " for the " +
                  vehicle + " example, expected " + str(expected[vehicle]))
        else:
            check(result["total_fare"] <= expected[vehicle],
                  name + " beat the best possible answer on the " +
                  vehicle + " example")
print("   done")
# ---------------------------------------------------------------
# Section 5: every algorithm on every dataset case
# ---------------------------------------------------------------
print("\n[5] Dataset cases: every algorithm against the reference DP")
for case in cases:
    problem = load_case(case["case_id"])
    dp = dp_solve(problem)
    best = dp["total_fare"]
    check(dp["valid"] and not dp["timed_out"],
          case["case_id"] + ": reference DP failed")
    notes = []
    for name, solver, kind in solvers:
        if name in BRUTE_FORCE and problem.m >= BIGGEST_SIZE:
            continue
        result = run(solver, kind, problem)
        check_well_formed(name, problem, result, case["case_id"])
        if kind == "exact":
            if result["timed_out"]:
                notes.append(name + " timed out")
            else:
                check(result["total_fare"] == best,
                      case["case_id"] + ": " + name + " got " +
                      str(result["total_fare"]) + ", reference DP says " +
                      str(best))
        else:
            check(result["total_fare"] <= best,
                  case["case_id"] + ": " + name + " got " +
                  str(result["total_fare"]) + ", MORE than the best possible " +
                  str(best) + " (bug)")
    line = "   " + case["case_id"].ljust(13) + "best fare " + str(best)
    if len(notes) > 0:
        line = line + "   (" + ", ".join(notes) + ")"
    print(line)
# ---------------------------------------------------------------
# Section 6: heuristic is safe
# ---------------------------------------------------------------
print("\n[6] Heuristic")
for case in cases:
    problem = load_case(case["case_id"])
    dp = dp_solve(problem)
    fare_lost = problem.total_fare - dp["total_fare"]
    check(h_zero(problem, 0, ()) == 0, case["case_id"] + ": h_zero is not 0")
    check(h_main(problem, 0, ()) <= fare_lost,
          case["case_id"] + ": h is higher than the real fare lost")
    check(h_main(problem, 0, ()) >= 0, case["case_id"] + ": h is negative")
    # at the goal (everything decided) h must be 0
    picked = tuple(k for k in range(problem.m)
                   if problem.requests[k].id in dp["accepted_ids"])
    check(h_main(problem, problem.m, picked) == 0,
          case["case_id"] + ": h is not 0 at the goal")
print("   done")
# ---------------------------------------------------------------
# Section 7: repeatability (same seed = same result)
# ---------------------------------------------------------------
print("\n[7] Repeatability")
problem = load_case("auto_10_1")
for name, solver, kind in solvers:
    if kind == "random":
        a = run(solver, kind, problem)
        b = run(solver, kind, problem)
        check(a["accepted_ids"] == b["accepted_ids"] and
              a["total_fare"] == b["total_fare"],
              name + ": same seed gave different results")
print("   done")
# ---------------------------------------------------------------
# Section 8: edge cases
# ---------------------------------------------------------------
print("\n[8] Edge cases")
for name, solver, kind in solvers:
    # no valid requests
    problem = load_case("bike_none_1")
    result = run(solver, kind, problem)
    check(result["accepted_ids"] == [] and result["total_fare"] == 0 and
          result["valid"] and not result["timed_out"],
          name + ": wrong result when there are no valid requests")
    # time limit already passed
    problem = load_case("bike_6_1")
    result = run(solver, kind, problem, time_limit=-1)
    check(result["timed_out"] == True,
          name + ": did not set timed_out when time ran out")
    check(result["valid"] == True,
          name + ": result after a timeout is not valid")
    if kind != "exact":
        continue
    # one request
    problem = Problem(route, "Bike", [Request("Q1", "A", "B", 40)])
    check(run(solver, kind, problem)["total_fare"] == 40,
          name + ": wrong answer with one request")
    # more seats than requests: everything is accepted
    two = [Request("Q1", "A", "C", 40), Request("Q2", "B", "D", 25)]
    check(run(solver, kind, Problem(route, "Car", two))["total_fare"] == 65,
          name + ": wrong answer when capacity is larger than the requests")
    # identical requests on a Bike: only the best one fits
    same = [Request("Q1", "A", "B", 10), Request("Q2", "A", "B", 50),
            Request("Q3", "A", "B", 30)]
    check(run(solver, kind, Problem(route, "Bike", same))["total_fare"] == 50,
          name + ": wrong answer with identical requests")
print("   done")
# ---------------------------------------------------------------
# Section 9: brute force on small random problems
# ---------------------------------------------------------------
print("\n[9] Random small problems against brute force")
for seed in range(15):
    problem = make_random_problem(seed)
    best = brute_force_best(problem)
    label = "random seed " + str(seed)
    dp = dp_solve(problem)
    check(dp["total_fare"] == best,
          label + ": reference DP got " + str(dp["total_fare"]) +
          ", brute force says " + str(best))
    for name, solver, kind in solvers:
        result = run(solver, kind, problem)
        check_well_formed(name, problem, result, label)
        if kind == "exact":
            check(result["total_fare"] == best,
                  label + ": " + name + " got " + str(result["total_fare"]) +
                  ", brute force says " + str(best))
        else:
            check(result["total_fare"] <= best,
                  label + ": " + name + " beat the best possible answer")
print("   done")
# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print("\n" + "=" * 55)
print("Checks run:", checks_run)
print("Failures  :", len(failures))
if len(failures) == 0:
    print("ALL SANITY TESTS PASSED!")
else:
    print("SOME SANITY TESTS FAILED. Send each failure to the owner of that part.")