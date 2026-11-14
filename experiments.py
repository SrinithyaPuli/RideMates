import csv
import json
import statistics
from pathlib import Path

from problem import load_case
from reference_dp import solve as dp_solve

# Keep the same time limit for every algorithm so the comparison is fair.
TIME_LIMIT = 30
LOCAL_SEARCH_SEEDS = range(10)  # seeds 0 to 9
DATA_FOLDER = Path("data")
RESULTS_FOLDER = Path("results")

# (display name, module path, is stochastic)

ALGORITHMS = [
    ("BFS", "algorithms.bfs", False),
    ("DFS", "algorithms.dfs", False),
    ("DLS", "algorithms.dls", False),
    ("IDDFS", "algorithms.iddfs", False),
    ("UCS", "algorithms.ucs", False),
    ("Greedy", "algorithms.greedy", False),
    ("A*", "algorithms.astar", False),
    ("IDA*", "algorithms.idastar", False),
    ("Hill Climbing", "algorithms.hill_climbing", True),
    ("Simulated Annealing", "algorithms.simulated_annealing", True),
    ("CSP", "algorithms.csp", False),
    ("AC-3", "algorithms.ac3", False),
]

def load_algorithms():
    """Import the solve() function from each algorithm file."""
    import importlib

    solvers = []
    for name, module_name, stochastic in ALGORITHMS:
        module = importlib.import_module(module_name)
        solvers.append((name, module.solve, stochastic))
    return solvers


def calculate_gap(optimal_fare, obtained_fare):
    """Return optimality gap as a percentage."""
    if optimal_fare is None:
        return ""
    if optimal_fare == 0:
        return 0.0 if obtained_fare == 0 else ""
    return ((optimal_fare - obtained_fare) / optimal_fare) * 100


def make_row(case_id, vehicle, request_count, optimal_fare,
             algorithm, result, seed=""):
    gap = calculate_gap(optimal_fare, result["total_fare"])
    return {
        "case_id": case_id,
        "vehicle": vehicle,
        "valid_requests": request_count,
        "algorithm": algorithm,
        "seed": seed,
        "optimal_fare": "" if optimal_fare is None else optimal_fare,
        "total_fare": result["total_fare"],
        "optimality_gap_percent": "" if gap == "" else round(gap, 4),
        "accepted_count": len(result["accepted_ids"]),
        "rejected_count": len(result["rejected_ids"]),
        "invalid_count": len(result["invalid_ids"]),
        "valid": result["valid"],
        "time_sec": round(result["time_sec"], 6),
        "nodes_explored": result["nodes_explored"],
        "peak_states": result["peak_states"],
        "timed_out": result["timed_out"],
        "backtracks": result.get("backtracks", ""),
        "domain_reduction": result.get("domain_reduction", ""),
    }


def average(values):
    values = [value for value in values if value != "" and value is not None]
    return round(statistics.mean(values), 4) if values else ""


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_case_summary(raw_rows):
    """One row per case and algorithm; stochastic runs are aggregated."""
    groups = {}
    for row in raw_rows:
        key = (row["case_id"], row["algorithm"])
        groups.setdefault(key, []).append(row)

    summary = []
    for (case_id, algorithm), rows in groups.items():
        first = rows[0]
        fares = [r["total_fare"] for r in rows]
        gaps = [float(r["optimality_gap_percent"])
                for r in rows if r["optimality_gap_percent"] != ""]
        times = [r["time_sec"] for r in rows]
        nodes = [r["nodes_explored"] for r in rows]
        summary.append({
            "case_id": case_id,
            "vehicle": first["vehicle"],
            "valid_requests": first["valid_requests"],
            "algorithm": algorithm,
            "optimal_fare": first["optimal_fare"],
            "best_fare": max(fares),
            "average_fare": round(statistics.mean(fares), 4),
            "worst_fare": min(fares),
            "average_gap_percent": average(gaps),
            "average_time_sec": average(times),
            "average_nodes_explored": average(nodes),
            "timed_out_runs": sum(1 for r in rows if r["timed_out"]),
            "runs": len(rows),
        })
    return summary


def build_overall_summary(case_rows):
    """Average the case-level results for each algorithm."""
    groups = {}
    for row in case_rows:
        groups.setdefault(row["algorithm"], []).append(row)

    summary = []
    for algorithm, rows in groups.items():
        summary.append({
            "algorithm": algorithm,
            "cases": len(rows),
            "average_gap_percent": average(
                [r["average_gap_percent"] for r in rows]),
            "average_time_sec": average(
                [r["average_time_sec"] for r in rows]),
            "average_nodes_explored": average(
                [r["average_nodes_explored"] for r in rows]),
            "total_timed_out_runs": sum(r["timed_out_runs"] for r in rows),
        })
    return summary


def main():
    RESULTS_FOLDER.mkdir(exist_ok=True)

    with open(DATA_FOLDER / "testcases.json", encoding="utf-8") as file:
        cases = json.load(file)

    solvers = load_algorithms()
    raw_rows = []

    runs_per_case = 1 + sum(
        len(LOCAL_SEARCH_SEEDS) if stochastic else 1
        for _, _, stochastic in solvers
    )  # one DP run plus every algorithm run
    total_runs = len(cases) * runs_per_case
    completed = 0

    print("RideMates experiment runner")
    print("Cases:", len(cases))
    print("Algorithms:", len(solvers))
    print("Time limit per run:", TIME_LIMIT, "seconds")
    print("Local-search seeds: 0 to 9")
    print("\nStarting experiments...\n")

    for case in cases:
        case_id = case["case_id"]
        problem = load_case(case_id, data_folder=str(DATA_FOLDER))

        # DP supplies the exact reference answer for calculating the gap.
        dp_result = dp_solve(problem, time_limit=TIME_LIMIT)
        optimal_fare = None if dp_result["timed_out"] else dp_result["total_fare"]
        raw_rows.append(make_row(
            case_id, case["vehicle"], problem.m, optimal_fare,
            "Reference DP", dp_result
        ))
        completed += 1
        print(f"[{completed}/{total_runs}] {case_id}: Reference DP done")

        for name, solver, stochastic in solvers:
            seeds = LOCAL_SEARCH_SEEDS if stochastic else [""]

            for seed in seeds:
                if stochastic:
                    result = solver(problem, time_limit=TIME_LIMIT, seed=seed)
                else:
                    result = solver(problem, time_limit=TIME_LIMIT)

                raw_rows.append(make_row(
                    case_id, case["vehicle"], problem.m, optimal_fare,
                    name, result, seed
                ))
                completed += 1
                seed_text = f" seed={seed}" if stochastic else ""
                print(f"[{completed}/{total_runs}] {case_id}: {name}{seed_text} "
                      f"fare={result['total_fare']} "
                      f"time={result['time_sec']:.3f}s")

        # Save progress after each case, so completed results are not lost.
        write_csv(RESULTS_FOLDER / "experiment_runs.csv", raw_rows)

    case_summary = build_case_summary(raw_rows)
    overall_summary = build_overall_summary(case_summary)

    write_csv(RESULTS_FOLDER / "experiment_case_summary.csv", case_summary)
    write_csv(RESULTS_FOLDER / "experiment_overall_summary.csv", overall_summary)

    with open(RESULTS_FOLDER / "experiment_results.json", "w",
              encoding="utf-8") as file:
        json.dump({
            "time_limit_sec": TIME_LIMIT,
            "local_search_seeds": list(LOCAL_SEARCH_SEEDS),
            "runs": raw_rows,
            "case_summary": case_summary,
            "overall_summary": overall_summary,
        }, file, indent=4)

    print("\nAll experiments completed.")
    print("Files saved in the results folder:")
    print("  experiment_runs.csv")
    print("  experiment_case_summary.csv")
    print("  experiment_overall_summary.csv")
    print("  experiment_results.json")


if __name__ == "__main__":
    main()
