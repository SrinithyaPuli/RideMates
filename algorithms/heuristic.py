# A "state" in our search is two things:
#     k        = how many requests have been decided so far
#     accepted = tuple of the request indices that were accepted,
#                for example (1, 2)
#h(n)= an estimate of the remaining fare you will be forced to lose from this point forward until all requests are processed.
def h_zero(problem, k, accepted):
    #For every single state you pass into h_zero—regardless of how many requests you've decided (k) 
    # or which ones are in your accepted tuple—it completely ignores them and always returns 0.
    return 0


def segment_costs(problem, k, accepted):
    #Calculates the minimum fare you are forced to lose on each individual segment of the route, looking only at the undecided requests (from index k onward).
    load = problem.occupancy(accepted)
    costs = []
    for s in range(problem.num_segments):
        fares = []
        for i in range(k, problem.m):
            if s in problem.segments(i):
                fares.append(problem.fare(i))
        too_many = load[s] + len(fares) - problem.capacity
        if too_many > 0:
            fares.sort()
            costs.append(sum(fares[:too_many]))
        else:
            costs.append(0)
    return costs
def h_main(problem, k, accepted):
    #Computes the final heuristic value ($h(\text{state})$) by taking the results from segment_costs 
    # and returning the maximum value among them (max(costs)).
    costs = segment_costs(problem, k, accepted)
    if len(costs) == 0:
        return 0
    return max(costs)