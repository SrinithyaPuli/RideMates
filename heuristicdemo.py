# Optional: prints how the heuristic is worked out, step by step,
from problem import Request, Problem
from algorithms.heuristic import segment_costs, h_main
route = ["A", "B", "C", "D", "E"]
requests = [
    Request("Q1", "A", "C", 50),
    Request("Q2", "B", "E", 70),
    Request("Q3", "A", "B", 30),
    Request("Q4", "C", "E", 40),
]
problem = Problem(route, "Bike", requests)
print("Vehicle:", problem.vehicle, "| capacity:", problem.capacity)
print("Requests in decision order:")
for k in range(problem.m):
    print("  k =", k, "|", problem.requests[k])

# Start state: nothing decided yet, nothing accepted
k = 0
accepted = ()
costs = segment_costs(problem, k, accepted)
print("\nForced fare loss on each segment:")
for s in range(problem.num_segments):
    name = route[s] + "-" + route[s + 1]
    users = []
    for i in range(k, problem.m):
        if s in problem.segments(i):
            users.append(problem.requests[i].id)
    print("  segment", name, "| used by", users, "| forced loss:", costs[s])
print("\nh = biggest forced loss =", h_main(problem, k, accepted))
print("(The real fare lost is 90, so h = 50 is safe: it is not higher.)")

# A state in the middle: Q1 rejected, Q3 accepted, Q2 and Q4 undecided
k = 2
accepted = (1,)
print("\nMiddle state: k = 2, accepted = (1,)  i.e. Q1 rejected, Q3 accepted")
print("Forced loss per segment:", segment_costs(problem, k, accepted))
print("h =", h_main(problem, k, accepted))