# main.py
import json
import importlib
from graph import load_graph, validate_route
from problem import Request, Problem, load_case

DATA = "data"
TIME_LIMIT = 30

# (menu name, file name inside algorithms/) for all 12 algorithms
ALGORITHMS = [
    ("BFS", "bfs"),
    ("DFS", "dfs"),
    ("DLS", "dls"),
    ("IDDFS", "iddfs"),
    ("UCS", "ucs"),
    ("Greedy Best-First", "greedy"),
    ("A*", "astar"),
    ("IDA*", "idastar"),
    ("Hill Climbing", "hill_climbing"),
    ("Simulated Annealing", "simulated_annealing"),
    ("CSP", "csp"),
    ("AC-3", "ac3"),
]


def load_algorithm(file_name):
    # Tries to import algorithms/<file_name>.py
    # Returns the module, or None if the file is missing or broken.
    try:
        return importlib.import_module("algorithms." + file_name)
    except Exception:
        return None


def ask_number(text, low, high):
    # Keeps asking until the user types a whole number from low to high.
    while True:
        answer = input(text).strip()
        if answer.isdigit() and low <= int(answer) <= high:
            return int(answer)
        print("Please type a number from", low, "to", high)


def show_result(problem, r):
    print()
    print("Algorithm      :", r["algorithm"])
    print("Vehicle        :", problem.vehicle, "(capacity", problem.capacity, ")")
    print("Route          :", " -> ".join(problem.route))
    print("Accepted       :", r["accepted_ids"])
    print("Rejected       :", r["rejected_ids"])
    print("Invalid        :", r["invalid_ids"])
    print("Total fare     : Rs.", r["total_fare"])

    # passengers on each segment, labelled with the road
    parts = []
    for i in range(len(r["occupancy"])):
        label = problem.route[i] + "-" + problem.route[i + 1]
        parts.append(label + ": " + str(r["occupancy"][i]))
    print("Passengers     :", ", ".join(parts))

    print("Nodes explored :", r["nodes_explored"])
    print("Time (sec)     :", round(r["time_sec"], 4))
    print("Peak states    :", r["peak_states"])
    print("Timed out      :", r["timed_out"])
    print("Capacity OK    :", r["valid"])

    # extra keys some algorithms add (cutoff, overhead_nodes, backtracks ...)
    basic = ["algorithm", "accepted_ids", "rejected_ids", "invalid_ids",
             "total_fare", "occupancy", "nodes_explored", "time_sec",
             "peak_states", "timed_out", "valid"]
    for key in r:
        if key not in basic:
            print(key.ljust(15) + ":", r[key])
    print()


def choose_case():
    # Shows every test case from testcases.json and lets the user pick one.
    with open(DATA + "/testcases.json") as f:
        cases = json.load(f)

    print()
    print("Test cases:")
    for i in range(len(cases)):
        c = cases[i]
        print(" ", i + 1, ".", c["case_id"], "| route", c["route_id"],
              "|", c["vehicle"])
    number = ask_number("Choose a case number: ", 1, len(cases))
    return cases[number - 1]["case_id"]


def choose_algorithm():
    # Shows the 12 algorithms and lets the user pick an available one.
    print()
    print("Algorithms:")
    modules = []
    for i in range(len(ALGORITHMS)):
        name, file_name = ALGORITHMS[i]
        module = load_algorithm(file_name)
        modules.append(module)
        if module is None:
            print(" ", i + 1, ".", name, "(not available yet)")
        else:
            print(" ", i + 1, ".", name)

    while True:
        number = ask_number("Choose an algorithm number: ", 1, len(ALGORITHMS))
        if modules[number - 1] is None:
            print("That algorithm is not available yet. Choose another.")
        else:
            return ALGORITHMS[number - 1][0], ALGORITHMS[number - 1][1], modules[number - 1]


def run_algorithm(problem, name, file_name, module):
    # Runs one algorithm safely and returns its result (or None on error).
    try:
        if file_name == "dls":
            text = "DLS depth limit (blank = use m = " + str(problem.m) + "): "
            answer = input(text).strip()
            if answer.isdigit():
                return module.solve(problem, TIME_LIMIT, int(answer))
        return module.solve(problem, TIME_LIMIT)
    except Exception as e:
        print(name, "crashed with error:", e)
        return None


def option_run_one():
    case_id = choose_case()
    problem = load_case(case_id)
    name, file_name, module = choose_algorithm()
    result = run_algorithm(problem, name, file_name, module)
    if result is not None:
        show_result(problem, result)


def option_compare_all():
    case_id = choose_case()
    problem = load_case(case_id)

    print()
    print("Case:", case_id, "| valid requests:", problem.m,
          "| invalid:", len(problem.invalid_ids),
          "| time limit:", TIME_LIMIT, "sec")
    print()
    print("algorithm".ljust(21) + "fare".ljust(7) + "nodes".ljust(10) +
          "time(s)".ljust(9) + "peak".ljust(9) + "status")

    for name, file_name in ALGORITHMS:
        module = load_algorithm(file_name)
        if module is None:
            print(name.ljust(21) + "not available yet")
            continue
        try:
            r = module.solve(problem, TIME_LIMIT)
        except Exception as e:
            print(name.ljust(21) + "ERROR: " + str(e))
            continue

        if not r["valid"]:
            status = "INVALID (capacity broken)"
        elif r["timed_out"]:
            status = "TIMEOUT"
        else:
            status = "done"
        print(name.ljust(21) + str(r["total_fare"]).ljust(7) +
              str(r["nodes_explored"]).ljust(10) +
              str(round(r["time_sec"], 2)).ljust(9) +
              str(r["peak_states"]).ljust(9) + status)
    print()


def option_check_route():
    graph = load_graph(DATA + "/graph.json")
    print()
    print("Type a route as locations separated by spaces, e.g.  A B C D")
    text = input("Route: ").replace(",", " ").upper()
    route = text.split()
    ok, message = validate_route(graph, route)
    if ok:
        print("Valid route:", " -> ".join(route))
    else:
        print("Invalid route:", message)
    print()


def option_worked_example():
    # The example from the project specification (Bike, capacity 1).
    route = ["A", "B", "C", "D", "E"]
    requests = [
        Request("Q1", "A", "C", 50),
        Request("Q2", "B", "E", 70),
        Request("Q3", "A", "B", 30),
        Request("Q4", "C", "E", 40),
        Request("Q5", "A", "Z", 20),    # off the route -> filtered out
    ]
    problem = Problem(route, "Bike", requests)

    print()
    print("Worked example from the specification")
    print("Route A -> B -> C -> D -> E, Bike (capacity 1)")
    print("Requests: Q1 A-C Rs.50, Q2 B-E Rs.70, Q3 A-B Rs.30,")
    print("          Q4 C-E Rs.40, Q5 A-Z Rs.20 (invalid)")
    print("Expected best: Q2 + Q3 = Rs.100")

    module = load_algorithm("dfs")
    result = module.solve(problem, TIME_LIMIT)
    show_result(problem, result)


def main():
    print("=== RideMates ===")
    while True:
        print("1. Run one algorithm on a test case")
        print("2. Compare all available algorithms on a test case")
        print("3. Check if a route is valid")
        print("4. Run the worked example from the specification")
        print("5. Exit")
        choice = ask_number("Choose an option: ", 1, 5)

        if choice == 1:
            option_run_one()
        elif choice == 2:
            option_compare_all()
        elif choice == 3:
            option_check_route()
        elif choice == 4:
            option_worked_example()
        else:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()