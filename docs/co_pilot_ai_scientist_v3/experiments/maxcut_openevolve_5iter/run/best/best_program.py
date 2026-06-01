def partition_graph(num_nodes, edges, seed=0):
    """Return one side of a weighted graph cut.

    Uses a degree-weighted approach that considers both node degrees and edge
    weights to find a partition. Nodes with high internal connectivity are
    grouped together based on their weighted degree patterns.
    """
    import random
    random.seed(seed)
    
    if num_nodes == 0:
        return []
    
    # Build adjacency list with weights
    adj = [[] for _ in range(num_nodes)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    
    # Calculate weighted degree for each node
    weighted_degree = [sum(w for _, w in neighbors) for neighbors in adj]
    
    # Sort nodes by weighted degree (high degree nodes tend to be more central)
    nodes_sorted = sorted(range(num_nodes), key=lambda x: weighted_degree[x], reverse=True)
    
    # Initialize partition: assign nodes alternately based on sorted order
    # This creates a more balanced initial partition
    side = [False] * num_nodes
    for i, node in enumerate(nodes_sorted):
        side[node] = (i % 2 == 0)
    
    # Refine with multiple passes of local search using different strategies
    # First pass: greedy improvement (flip if gain > 0)
    for _ in range(2):
        for node in range(num_nodes):
            gain = 0
            for neighbor, weight in adj[node]:
                if side[node] == side[neighbor]:
                    gain += weight
                else:
                    gain -= weight
            if gain > 0:
                side[node] = not side[node]
    
    # Second pass: try flipping nodes with zero gain to escape plateaus
    # This can help find better partitions by breaking symmetry
    import random as rnd
    rnd.seed(seed + 1)  # Different seed for variety
    for _ in range(2):
        # Process nodes in random order for better exploration
        nodes_random = list(range(num_nodes))
        rnd.shuffle(nodes_random)
        for node in nodes_random:
            gain = 0
            for neighbor, weight in adj[node]:
                if side[node] == side[neighbor]:
                    gain += weight
                else:
                    gain -= weight
            # Flip if gain > 0, or with small probability if gain == 0
            if gain > 0 or (gain == 0 and rnd.random() < 0.3):
                side[node] = not side[node]
    
    # Third pass: conservative refinement (only flip if gain > threshold)
    # This helps stabilize the solution
    for _ in range(1):
        for node in range(num_nodes):
            gain = 0
            for neighbor, weight in adj[node]:
                if side[node] == side[neighbor]:
                    gain += weight
                else:
                    gain -= weight
            # Only flip if significant improvement (more than 5% of max edge weight)
            max_weight = max((w for _, _, w in edges), default=1)
            if gain > 0.05 * max_weight * len(adj[node]):
                side[node] = not side[node]
    
    # Return nodes on the left side (True side)
    return [node for node in range(num_nodes) if side[node]]
