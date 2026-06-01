def partition_graph(num_nodes, edges, seed=0):
    """Return one side of a weighted graph cut.

    The starter alternates node labels. It is intentionally simple so that
    direct rewrites and evolutionary search both have room to improve.
    """
    return [node for node in range(num_nodes) if node % 2 == 0]
