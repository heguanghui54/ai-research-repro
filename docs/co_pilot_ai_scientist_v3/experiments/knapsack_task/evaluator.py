import importlib.util
import random
from functools import lru_cache


def make_instances():
    rng = random.Random(12345)
    instances = []
    for n in [18, 22, 26, 30, 34, 38]:
        for case in range(3):
            items = []
            for i in range(n):
                weight = rng.randint(2, 35)
                base = rng.randint(3, 90)
                category = rng.randint(0, 4)
                # Add mild structure so category-aware or density-aware heuristics can help.
                value = base + (category * 3) + (7 if weight % 5 == 0 else 0)
                items.append({"weight": weight, "value": value, "category": category})
            capacity = int(sum(item["weight"] for item in items) * rng.uniform(0.28, 0.45))
            instances.append((items, capacity))
    return instances


def optimal_value(items, capacity):
    weights = [item["weight"] for item in items]
    values = [item["value"] for item in items]

    @lru_cache(None)
    def dp(i, remaining):
        if i == len(items):
            return 0
        best = dp(i + 1, remaining)
        if weights[i] <= remaining:
            best = max(best, values[i] + dp(i + 1, remaining - weights[i]))
        return best

    return dp(0, capacity)


def load_program(path):
    spec = importlib.util.spec_from_file_location("candidate_program", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def evaluate(path):
    try:
        module = load_program(path)
        instances = make_instances()
        ratios = []
        invalid = 0
        total_value = 0
        total_opt = 0
        for items, capacity in instances:
            selected = module.select_items(items, capacity)
            if not isinstance(selected, (list, tuple)):
                invalid += 1
                ratios.append(0.0)
                continue
            selected = list(dict.fromkeys(int(i) for i in selected if 0 <= int(i) < len(items)))
            weight = sum(items[i]["weight"] for i in selected)
            value = sum(items[i]["value"] for i in selected)
            opt = optimal_value(items, capacity)
            total_opt += opt
            if weight > capacity:
                invalid += 1
                ratios.append(0.0)
            else:
                total_value += value
                ratios.append(value / opt if opt else 0.0)
        avg_ratio = sum(ratios) / len(ratios)
        score = avg_ratio - 0.05 * invalid
        return {
            "combined_score": float(score),
            "score": float(score),
            "avg_ratio": float(avg_ratio),
            "invalid": invalid,
            "total_value": total_value,
            "total_opt": total_opt,
            "instances": len(instances),
        }
    except Exception as exc:
        return {"combined_score": -1e9, "score": -1e9, "error": type(exc).__name__ + ": " + str(exc)[:300]}
