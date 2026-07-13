"""People say list comprehensions are faster than for-loop appends.
Let's actually measure it instead of taking it on faith."""

import time

N = 10_000_000

# For-loop append
start = time.perf_counter()
result = []
for i in range(N):
    result.append(i)
loop_time = time.perf_counter() - start

# List comprehension
start = time.perf_counter()
result = [i for i in range(N)]
comp_time = time.perf_counter() - start

print(f"For-loop append: {loop_time:.4f}s")
print(f"List comprehension: {comp_time:.4f}s")
print(f"Winner: {'comprehension' if comp_time < loop_time else 'for-loop'}")
print(f"Ratio: {loop_time / comp_time:.2f}x")
