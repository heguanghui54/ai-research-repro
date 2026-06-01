def select_items(items, capacity):
    """Return selected item indices for a 0/1 knapsack instance.

    items is a list of dictionaries with keys: weight, value, category.
    Uses a two-phase approach: greedy selection followed by local improvement.
    """
    n = len(items)
    # Precompute value/weight ratios for efficiency
    ratios = [items[i]["value"] / max(items[i]["weight"], 1) for i in range(n)]
    
    # Phase 1: Greedy selection by value/weight ratio
    ranked = sorted(range(n), key=lambda i: ratios[i], reverse=True)
    total_weight = 0
    selected = []
    selected_set = set()
    for i in ranked:
        weight = items[i]["weight"]
        if total_weight + weight <= capacity:
            selected.append(i)
            selected_set.add(i)
            total_weight += weight
    
    # Phase 2: Local search - try multi-item swaps to improve value
    current_value = sum(items[i]["value"] for i in selected)
    
    # Pre-sort all items by ratio for faster candidate generation
    all_sorted = sorted(range(n), key=lambda i: ratios[i], reverse=True)
    
    improved = True
    while improved:
        improved = False
        
        # Try removing one selected item and adding multiple unselected items
        for remove_idx in range(len(selected)):
            removed_item = selected[remove_idx]
            removed_weight = items[removed_item]["weight"]
            removed_value = items[removed_item]["value"]
            
            # Calculate freed capacity
            remaining_capacity = capacity - (total_weight - removed_weight)
            
            # Greedily fill freed space with best unselected items
            new_selected = []
            new_weight = 0
            for i in all_sorted:
                if i not in selected_set and new_weight + items[i]["weight"] <= remaining_capacity:
                    new_selected.append(i)
                    new_weight += items[i]["weight"]
            
            new_value = sum(items[i]["value"] for i in new_selected)
            
            # If swapping improves value, apply the change
            if new_value > removed_value:
                # Remove the item
                selected.pop(remove_idx)
                selected_set.remove(removed_item)
                total_weight -= removed_weight
                
                # Add new items
                for i in new_selected:
                    selected.append(i)
                    selected_set.add(i)
                    total_weight += items[i]["weight"]
                
                current_value = current_value - removed_value + new_value
                improved = True
                break  # Restart search after change
        
        # If no improvement from single-item removal, try two-item removal
        if not improved and len(selected) >= 2:
            for remove_idx1 in range(len(selected)):
                for remove_idx2 in range(remove_idx1 + 1, len(selected)):
                    removed_item1 = selected[remove_idx1]
                    removed_item2 = selected[remove_idx2]
                    removed_weight = items[removed_item1]["weight"] + items[removed_item2]["weight"]
                    removed_value = items[removed_item1]["value"] + items[removed_item2]["value"]
                    
                    # Calculate freed capacity
                    remaining_capacity = capacity - (total_weight - removed_weight)
                    
                    # Greedily fill freed space with best unselected items
                    new_selected = []
                    new_weight = 0
                    for i in all_sorted:
                        if i not in selected_set and new_weight + items[i]["weight"] <= remaining_capacity:
                            new_selected.append(i)
                            new_weight += items[i]["weight"]
                    
                    new_value = sum(items[i]["value"] for i in new_selected)
                    
                    # If swapping improves value, apply the change
                    if new_value > removed_value:
                        # Remove items (remove larger index first to avoid index issues)
                        if remove_idx1 < remove_idx2:
                            selected.pop(remove_idx2)
                            selected.pop(remove_idx1)
                        else:
                            selected.pop(remove_idx1)
                            selected.pop(remove_idx2)
                        selected_set.discard(removed_item1)
                        selected_set.discard(removed_item2)
                        total_weight -= removed_weight
                        
                        # Add new items
                        for i in new_selected:
                            selected.append(i)
                            selected_set.add(i)
                            total_weight += items[i]["weight"]
                        
                        current_value = current_value - removed_value + new_value
                        improved = True
                        break
                if improved:
                    break
    
    return selected
