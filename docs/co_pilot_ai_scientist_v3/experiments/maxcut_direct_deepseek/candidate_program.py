import random

def partition_graph(num_nodes, edges, seed=0):
    """Return one side of a weighted graph cut using a greedy local search."""
    rng = random.Random(seed)
    
    # Build adjacency list
    adj = [[] for _ in range(num_nodes)]
    for i, j, w in edges:
        adj[i].append((j, w))
        adj[j].append((i, w))
    
    # Initialize with a random partition
    bits = [rng.randint(0, 1) for _ in range(num_nodes)]
    
    # Compute initial cut value
    current = 0
    for i, j, w in edges:
        if bits[i] != bits[j]:
            current += w
    
    # Local search: multiple passes
    improved = True
    passes = 0
    while improved and passes < 30:
        improved = False
        passes += 1
        order = list(range(num_nodes))
        rng.shuffle(order)
        for node in order:
            delta = 0
            node_bit = bits[node]
            for other, w in adj[node]:
                if bits[other] == node_bit:
                    delta += w
                else:
                    delta -= w
            if delta > 0:
                bits[node] = 1 - node_bit
                current += delta
                improved = True
    
    # Return nodes on one side (those with bit 1)
    return [node for node in range(num_nodes) if bits[node] == 1]
