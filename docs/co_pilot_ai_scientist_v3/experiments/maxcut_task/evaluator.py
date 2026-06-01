import importlib.util
import random


def make_instances():
    rng = random.Random(24680)
    instances = []
    for num_nodes in [24, 30, 36, 42]:
        for case in range(4):
            communities = [rng.randrange(4) for _ in range(num_nodes)]
            edges = []
            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    same = communities[i] == communities[j]
                    p = 0.18 if same else 0.34
                    if rng.random() < p:
                        weight = rng.randint(1, 7)
                        if not same:
                            weight += rng.randint(0, 5)
                        edges.append((i, j, weight))
            instances.append((num_nodes, edges))
    return instances


def _cut_value(bits, edges):
    return sum(weight for i, j, weight in edges if bits[i] != bits[j])


def _normalize_partition(partition, num_nodes):
    if isinstance(partition, (list, tuple)) and len(partition) == num_nodes:
        values = [int(x) for x in partition]
        if all(x in (0, 1) for x in values):
            return values
    selected = set(int(x) for x in partition)
    return [1 if node in selected else 0 for node in range(num_nodes)]


def _reference_value(num_nodes, edges):
    rng = random.Random(9000 + num_nodes + len(edges))
    best = 0
    starts = []
    starts.append([node % 2 for node in range(num_nodes)])
    starts.append([(node // 2) % 2 for node in range(num_nodes)])
    for _ in range(10):
        starts.append([rng.randrange(2) for _ in range(num_nodes)])

    adjacency = [[] for _ in range(num_nodes)]
    for i, j, weight in edges:
        adjacency[i].append((j, weight))
        adjacency[j].append((i, weight))

    for bits in starts:
        current = _cut_value(bits, edges)
        improved = True
        passes = 0
        while improved and passes < 20:
            improved = False
            passes += 1
            order = list(range(num_nodes))
            rng.shuffle(order)
            for node in order:
                delta = 0
                node_bit = bits[node]
                for other, weight in adjacency[node]:
                    if bits[other] == node_bit:
                        delta += weight
                    else:
                        delta -= weight
                if delta > 0:
                    bits[node] = 1 - bits[node]
                    current += delta
                    improved = True
        best = max(best, current)
    return best


def load_program(path):
    spec = importlib.util.spec_from_file_location("candidate_program", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def evaluate(path):
    try:
        module = load_program(path)
        ratios = []
        invalid = 0
        total_value = 0
        total_reference = 0
        for idx, (num_nodes, edges) in enumerate(make_instances()):
            raw = module.partition_graph(num_nodes, edges, seed=idx)
            bits = _normalize_partition(raw, num_nodes)
            if len(bits) != num_nodes or any(bit not in (0, 1) for bit in bits):
                invalid += 1
                ratios.append(0.0)
                continue
            value = _cut_value(bits, edges)
            reference = _reference_value(num_nodes, edges)
            total_value += value
            total_reference += reference
            ratios.append(value / reference if reference else 0.0)
        avg_ratio = sum(ratios) / len(ratios)
        score = avg_ratio - 0.05 * invalid
        return {
            "combined_score": float(score),
            "score": float(score),
            "avg_ratio": float(avg_ratio),
            "invalid": invalid,
            "total_value": int(total_value),
            "total_reference": int(total_reference),
            "instances": len(ratios),
        }
    except Exception as exc:
        return {
            "combined_score": -1e9,
            "score": -1e9,
            "error": type(exc).__name__ + ": " + str(exc)[:300],
        }
