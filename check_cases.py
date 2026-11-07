# check_cases.py
# Loads every test case and prints how many requests are valid and invalid.
import json
from problem import load_case

with open("data/testcases.json") as f:
    cases = json.load(f)

print("Number of cases:", len(cases))

for c in cases:
    try:
        p = load_case(c["case_id"])
        print(c["case_id"], c["route_id"], c["vehicle"],
              "valid:", p.m, "invalid:", len(p.invalid_ids))
    except Exception as e:
        print(c["case_id"], "ERROR:", e)