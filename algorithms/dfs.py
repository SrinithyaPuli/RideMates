# algorithms/dfs.py
# Person 1: Depth-First Search.
# Tries accept/reject for every request, follows each choice to the end,
# then backtracks. Explores the whole tree and keeps the best selection.
import time
from problem import can_accept, make_result
def solve(problem, time_limit=30):
    start_time=time.time()
    # numbers shared by all the recursive calls
    info={
        "nodes":0,              # states visited
        "peak":0,               # deepest point reached
        "timed_out":False,
        "best_fare":-1,         # best accepted fare found so far
        "best_accepted":(),     # the selection that gave it
    }
    def explore(k, accepted, fare, depth):
        # k = number of requests decided so far
        # accepted = tuple of accepted request indices
        # fare = total accepted fare so far
        if info["timed_out"]:
            return
        if time.time()-start_time>time_limit:
            info["timed_out"]=True
            return

        info["nodes"]+=1
        if depth + 1>info["peak"]:
            info["peak"]=depth+1
        # goal: every request has been decided
        if k==problem.m:
            if fare>info["best_fare"]:
                info["best_fare"]=fare
                info["best_accepted"]=accepted
            return
        # choice 1: accept request k (only if capacity allows)
        if can_accept(problem, accepted, k):
            explore(k+1,accepted+(k,),fare+problem.fare(k),depth + 1)
        # choice 2: reject request k (always allowed)
        explore(k+1,accepted,fare,depth+1)
    explore(0,(),0,0)
    return make_result(problem,"DFS",info["best_accepted"],info["nodes"],start_time,info["peak"],info["timed_out"])