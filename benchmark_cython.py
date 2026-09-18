import timeit

from chronosmatch.matching.cython.match_core import match_quantity


def python_match_quantity(incoming_quantity, resting_quantity):
    if incoming_quantity < resting_quantity:
        return incoming_quantity
    return resting_quantity


N = 1_000_000

python_time = timeit.timeit(
    "python_match_quantity(100, 70)",
    globals=globals(),
    number=N,
)

cython_time = timeit.timeit(
    "match_quantity(100, 70)",
    globals=globals(),
    number=N,
)

print(f"Iterations : {N:,}")
print(f"Python     : {python_time:.6f} seconds")
print(f"Cython     : {cython_time:.6f} seconds")

if cython_time > 0:
    print(f"Speed ratio: {python_time / cython_time:.2f}x")
