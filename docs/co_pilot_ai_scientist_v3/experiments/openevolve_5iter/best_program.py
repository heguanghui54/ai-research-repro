import random


def minimize_function(func, bounds, max_evals=80):
    best_x = None
    best_val = float("inf")
    low, high = bounds
    
    # Phase 1: Global exploration (55% of budget) - slightly more exploration
    exploration_evals = int(max_evals * 0.55)
    candidates = []
    
    for _ in range(exploration_evals):
        x = random.uniform(low, high)
        val = func(x)
        candidates.append((x, val))
        if val < best_val:
            best_x = x
            best_val = val
    
    # Sort candidates by fitness for local search initialization
    candidates.sort(key=lambda pair: pair[1])
    
    # Phase 2: Local refinement on top candidates (45% of budget)
    local_evals = max_evals - exploration_evals
    top_n = min(4, len(candidates))  # Use 4 top candidates instead of 3
    
    for i in range(top_n):
        if local_evals <= 0:
            break
        
        # Use top candidate as starting point
        start_x = candidates[i][0]
        # Adaptive initial step size based on candidate rank
        step_size = (high - low) * (0.12 - 0.01 * i)  # Smaller steps for better candidates
        
        # Local random walk with adaptive step size
        local_budget = local_evals // top_n
        for j in range(local_budget):
            # Random perturbation with adaptive step size
            perturbation = random.uniform(-step_size, step_size)
            new_x = start_x + perturbation
            new_x = max(low, min(high, new_x))  # Keep within bounds
            
            val = func(new_x)
            if val < best_val:
                best_x = new_x
                best_val = val
                start_x = new_x  # Move to better point
                step_size *= 0.97  # More gradual step size reduction
            else:
                # Occasionally accept worse solutions to escape local minima
                if random.random() < 0.05:  # 5% chance to explore
                    start_x = new_x
                    step_size *= 1.02  # Slightly increase step size when exploring
            
            local_evals -= 1
    
    return best_x, best_val
