# run_uninformed.py
# Person 1: runs DFS, BFS, DLS and IDDFS on the large test cases
# to see which runs finish and which time out.

from problem import load_case
from algorithms import dfs, bfs, dls, iddfs

TIME_LIMIT = 5          # seconds per run, change this if you want

cases = ["bike_15_1", "auto_15_1", "car_15_1",
         "bike_20_1", "auto_20_1", "car_20_1"]

algorithms = [("DFS", dfs), ("BFS", bfs), ("DLS", dls), ("IDDFS", iddfs)]

print("Time limit per run:", TIME_LIMIT, "seconds")
print()
print("case".ljust(11) + "algorithm".ljust(11) + "fare".ljust(7) +
      "nodes".ljust(12) + "time(s)".ljust(9) + "peak".ljust(10) + "status")

for name in cases:
    problem = load_case(name)
    for alg_name, module in algorithms:
        r = module.solve(problem, TIME_LIMIT)

        # every result must respect capacity, even after a timeout
        assert r["valid"] == True, alg_name + " broke capacity on " + name

        if r["timed_out"]:
            status = "TIMEOUT"
        else:
            status = "done"

        print(name.ljust(11) + alg_name.ljust(11) +
              str(r["total_fare"]).ljust(7) +
              str(r["nodes_explored"]).ljust(12) +
              str(round(r["time_sec"], 2)).ljust(9) +
              str(r["peak_states"]).ljust(10) + status)
    print()