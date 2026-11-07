from problem import Request, filter_requests

route = ["A", "B", "C", "D"]

requests = [
    Request("Q1", "A", "C", 50),  # Valid
    Request("Q2", "X", "C", 40),  # Pickup not on route
    Request("Q3", "B", "X", 30),  # Drop-off not on route
    Request("Q4", "C", "A", 20),  # Pickup after drop-off
    Request("Q5", "B", "B", 10)   # Same pickup and drop-off
]

valid, invalid = filter_requests(route, requests)

print("Valid requests:")
print([r.id for r in valid])

print("\nInvalid requests:")
print([r.id for r in invalid])

assert [r.id for r in valid] == ["Q1"]
assert set(r.id for r in invalid) == {"Q2", "Q3", "Q4", "Q5"}

print("All filter tests passed!")

valid, invalid = filter_requests(
    route,
    [
        Request("Q6", "X", "Y", 50)
    ]
)

assert len(valid) == 0
assert len(invalid) == 1

print("Zero-valid-request test passed!")