import random
import math


def minimize_function(func, bounds, max_evals=80):
    low, high = bounds
    # Initialize with random points
    best_x = random.uniform(low, high)
    best_val = func(best_x)
    
    # Simulated annealing approach with adaptive step size
    temperature = 1.0
    cooling_rate = 0.95
    step_size = (high - low) * 0.2  # Initial step size as 20% of range
    
    for i in range(1, max_evals):
        # Generate candidate point using current best with perturbation
        candidate = best_x + random.uniform(-step_size, step_size)
        # Clip to bounds
        candidate = max(low, min(high, candidate))
        
        candidate_val = func(candidate)
        
        # Always accept better solutions
        if candidate_val < best_val:
            best_x = candidate
            best_val = candidate_val
        else:
            # Sometimes accept worse solutions (exploration)
            delta = candidate_val - best_val
            acceptance_prob = math.exp(-delta / temperature) if temperature > 0 else 0
            if random.random() < acceptance_prob:
                best_x = candidate
                best_val = candidate_val
        
        # Occasionally do a random restart for diversity
        if i % 20 == 0:
            random_x = random.uniform(low, high)
            random_val = func(random_x)
            if random_val < best_val:
                best_x = random_x
                best_val = random_val
        
        # Adaptive step size based on progress
        if i % 10 == 0:
            step_size *= 0.95  # Gradually shrink step size
        
        # Cool down temperature
        temperature *= cooling_rate
    
    return best_x, best_val
