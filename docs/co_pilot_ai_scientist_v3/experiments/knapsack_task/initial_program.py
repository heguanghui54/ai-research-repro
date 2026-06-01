def select_items(items, capacity):
    """Return selected item indices for a 0/1 knapsack instance.

    items is a list of dictionaries with keys: weight, value, category.
    """
    ranked = sorted(range(len(items)), key=lambda i: items[i]["value"] / max(items[i]["weight"], 1), reverse=True)
    total_weight = 0
    selected = []
    for i in ranked:
        weight = items[i]["weight"]
        if total_weight + weight <= capacity:
            selected.append(i)
            total_weight += weight
    return selected
