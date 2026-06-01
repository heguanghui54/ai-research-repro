import random


def minimize_function(func, bounds, max_evals=80):
    best_x = None
    best_val = float("inf")
    low, high = bounds
    for _ in range(max_evals):
        x = random.uniform(low, high)
        val = func(x)
        if val < best_val:
            best_x = x
            best_val = val
    return best_x, best_val
