def select_items(items, capacity):
    """Return selected item indices for a 0/1 knapsack instance.

    items is a list of dictionaries with keys: weight, value, category.
    """
    n = len(items)
    # Precompute density and category bonus
    densities = []
    for i, item in enumerate(items):
        w = item["weight"]
        v = item["value"]
        cat = item["category"]
        # Density with small epsilon to avoid division by zero
        density = v / (w + 1e-9)
        # Category bonus: items from same category might have synergy
        # We'll use a simple heuristic: prefer items with higher value per weight,
        # but also consider category diversity to avoid overloading one category
        densities.append((density, v, w, cat, i))
    
    # Sort by density descending, then value descending
    densities.sort(key=lambda x: (-x[0], -x[1]))
    
    # First pass: greedy by density
    selected = []
    total_weight = 0
    for density, v, w, cat, idx in densities:
        if total_weight + w <= capacity:
            selected.append(idx)
            total_weight += w
    
    # Second pass: try to improve by swapping or adding items with high value
    # Use a simple local search: try to replace items with better ones
    # We'll do a limited beam search: keep top candidates by value
    best_selected = selected[:]
    best_value = sum(items[i]["value"] for i in selected)
    
    # Try to add any missing high-value items by removing some low-value ones
    # Sort selected by value ascending for potential removal
    selected_sorted = sorted(selected, key=lambda i: items[i]["value"])
    for idx in range(n):
        if idx in selected:
            continue
        w_new = items[idx]["weight"]
        v_new = items[idx]["value"]
        # Try to remove items to make room
        temp_weight = total_weight
        temp_selected = selected[:]
        # Remove items with lowest value until we can fit the new one
        for rem_idx in selected_sorted:
            if temp_weight + w_new <= capacity:
                break
            temp_weight -= items[rem_idx]["weight"]
            temp_selected.remove(rem_idx)
        if temp_weight + w_new <= capacity:
            temp_selected.append(idx)
            temp_value = sum(items[i]["value"] for i in temp_selected)
            if temp_value > best_value:
                best_value = temp_value
                best_selected = temp_selected[:]
                selected = temp_selected[:]
                total_weight = temp_weight + w_new
                selected_sorted = sorted(selected, key=lambda i: items[i]["value"])
    
    # Final check: ensure no duplicates and valid indices
    result = list(dict.fromkeys(best_selected))
    # Verify capacity
    if sum(items[i]["weight"] for i in result) > capacity:
        # Fallback to simple greedy if something went wrong
        result = []
        total = 0
        for density, v, w, cat, idx in densities:
            if total + w <= capacity:
                result.append(idx)
                total += w
    return result
