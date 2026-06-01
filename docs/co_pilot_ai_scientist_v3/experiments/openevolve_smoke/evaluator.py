import importlib.util
import math


def objective(x: float) -> float:
    return (x - 1.2345) ** 2 + 0.05 * math.sin(8 * x)


def load_program(path: str):
    spec = importlib.util.spec_from_file_location("candidate_program", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def evaluate(path: str):
    try:
        module = load_program(path)
        best_x, best_val = module.minimize_function(objective, (-5.0, 5.0), max_evals=80)
        score = -float(best_val)
        return {
            "combined_score": score,
            "score": score,
            "best_x": float(best_x),
            "best_val": float(best_val),
        }
    except Exception as exc:
        return {
            "combined_score": -1e9,
            "score": -1e9,
            "error": type(exc).__name__ + ": " + str(exc)[:300],
        }
