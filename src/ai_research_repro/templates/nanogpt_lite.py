from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


def build_corpus() -> str:
    base_sentences = [
        "scientific discovery requires experiments, analysis, and iteration.",
        "small changes to optimization can improve validation loss.",
        "language models learn patterns from repeated tokens.",
        "a careful baseline makes improvements easier to measure.",
        "research agents benefit from clear hypotheses and feedback loops.",
        "we compare ideas by training tiny models on the same corpus.",
        "good charts make the effect of each patch visible.",
        "the best idea is the one that survives debugging and evaluation.",
        "open-ended search works best when the environment is stable.",
        "simple models are useful because they run quickly and reliably.",
    ]
    return "\n".join(base_sentences * 80)


def build_vocab(text: str) -> tuple[dict[str, int], list[str]]:
    chars = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = chars[:]
    return stoi, itos


def encode(text: str, stoi: dict[str, int]) -> list[int]:
    return [stoi[ch] for ch in text]


def decode(tokens: Iterable[int], itos: list[str]) -> str:
    return "".join(itos[int(i)] for i in tokens)


class CharDataset:
    def __init__(self, tokens: list[int], block_size: int):
        self.tokens = tokens
        self.block_size = block_size
        self.max_start = max(1, len(tokens) - block_size - 1)

    def sample_batch(self, rng: np.random.Generator, batch_size: int) -> tuple[np.ndarray, np.ndarray]:
        starts = rng.integers(0, self.max_start, size=batch_size)
        x = np.stack([self.tokens[s : s + self.block_size] for s in starts]).astype(np.int64)
        y = np.array([self.tokens[s + self.block_size] for s in starts], dtype=np.int64)
        return x, y

    def validation_batches(self, rng: np.random.Generator, batch_size: int, num_batches: int) -> list[tuple[np.ndarray, np.ndarray]]:
        return [self.sample_batch(rng, batch_size) for _ in range(num_batches)]


@dataclass
class NanoGPTConfig:
    block_size: int = 32
    batch_size: int = 64
    max_steps: int = 400
    eval_interval: int = 50
    eval_batches: int = 20
    lr: float = 0.05
    weight_decay: float = 1e-4
    grad_clip: float = 1.0
    n_embd: int = 32
    hidden_size: int = 128
    seed: int = 42
    train_ratio: float = 0.9


def default_config() -> NanoGPTConfig:
    return NanoGPTConfig()


class TinyNumpyLM:
    def __init__(self, vocab_size: int, block_size: int, n_embd: int, hidden_size: int, seed: int):
        self.vocab_size = vocab_size
        self.block_size = block_size
        self.n_embd = n_embd
        self.hidden_size = hidden_size
        self.rng = np.random.default_rng(seed)
        scale = 0.02
        self.params = {
            "E": self.rng.normal(0.0, scale, size=(vocab_size, n_embd)),
            "W1": self.rng.normal(0.0, scale, size=(block_size * n_embd, hidden_size)),
            "b1": np.zeros(hidden_size, dtype=np.float64),
            "W2": self.rng.normal(0.0, scale, size=(hidden_size, vocab_size)),
            "b2": np.zeros(vocab_size, dtype=np.float64),
        }
        self.opt_m = {name: np.zeros_like(value) for name, value in self.params.items()}
        self.opt_v = {name: np.zeros_like(value) for name, value in self.params.items()}
        self.opt_step = 0

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, dict]:
        emb = self.params["E"][x]  # (B, T, D)
        z = emb.reshape(x.shape[0], -1)  # (B, T*D)
        h_pre = z @ self.params["W1"] + self.params["b1"]
        h = np.tanh(h_pre)
        logits = h @ self.params["W2"] + self.params["b2"]
        cache = {"x": x, "emb": emb, "z": z, "h_pre": h_pre, "h": h}
        return logits, cache

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        shifted = logits - logits.max(axis=-1, keepdims=True)
        exp = np.exp(shifted)
        return exp / exp.sum(axis=-1, keepdims=True)

    def loss_and_grads(self, x: np.ndarray, y: np.ndarray) -> tuple[float, dict[str, np.ndarray]]:
        logits, cache = self.forward(x)
        probs = self._softmax(logits)
        batch = x.shape[0]
        loss = -np.log(probs[np.arange(batch), y] + 1e-12).mean()

        dlogits = probs
        dlogits[np.arange(batch), y] -= 1.0
        dlogits /= batch

        grads = {}
        grads["W2"] = cache["h"].T @ dlogits
        grads["b2"] = dlogits.sum(axis=0)
        dh = dlogits @ self.params["W2"].T
        dh_pre = dh * (1.0 - np.tanh(cache["h_pre"]) ** 2)
        grads["W1"] = cache["z"].T @ dh_pre
        grads["b1"] = dh_pre.sum(axis=0)

        dz = dh_pre @ self.params["W1"].T
        demb = dz.reshape(batch, self.block_size, self.n_embd)
        dE = np.zeros_like(self.params["E"])
        np.add.at(dE, cache["x"].reshape(-1), demb.reshape(-1, self.n_embd))
        grads["E"] = dE
        return float(loss), grads

    def _clip_grads(self, grads: dict[str, np.ndarray], max_norm: float) -> dict[str, np.ndarray]:
        total = 0.0
        for g in grads.values():
            total += float(np.sum(g * g))
        total_norm = math.sqrt(total)
        if total_norm <= max_norm or total_norm == 0.0:
            return grads
        scale = max_norm / (total_norm + 1e-12)
        return {k: v * scale for k, v in grads.items()}

    def step(self, grads: dict[str, np.ndarray], lr: float, weight_decay: float, grad_clip: float) -> None:
        self.opt_step += 1
        grads = self._clip_grads(grads, grad_clip)
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        for name, param in self.params.items():
            grad = grads[name]
            if name != "b1" and name != "b2":
                grad = grad + weight_decay * param
            m = self.opt_m[name] = beta1 * self.opt_m[name] + (1 - beta1) * grad
            v = self.opt_v[name] = beta2 * self.opt_v[name] + (1 - beta2) * (grad * grad)
            m_hat = m / (1 - beta1 ** self.opt_step)
            v_hat = v / (1 - beta2 ** self.opt_step)
            self.params[name] = param - lr * m_hat / (np.sqrt(v_hat) + eps)

    def predict_next(self, context: np.ndarray) -> np.ndarray:
        logits, _ = self.forward(context[None, :])
        return self._softmax(logits)[0]


def _evaluate(model: TinyNumpyLM, val_ds: CharDataset, rng: np.random.Generator, batch_size: int, eval_batches: int) -> float:
    losses = []
    for x, y in val_ds.validation_batches(rng, batch_size, eval_batches):
        loss, _ = model.loss_and_grads(x, y)
        losses.append(loss)
    return float(sum(losses) / max(1, len(losses)))


def generate_sample(
    model: TinyNumpyLM,
    stoi: dict[str, int],
    itos: list[str],
    *,
    prompt: str,
    max_new_tokens: int = 120,
) -> str:
    tokens = [stoi.get(ch, 0) for ch in prompt]
    if len(tokens) < model.block_size:
        tokens = [0] * (model.block_size - len(tokens)) + tokens
    for _ in range(max_new_tokens):
        context = np.array(tokens[-model.block_size :], dtype=np.int64)
        probs = model.predict_next(context)
        next_token = int(model.rng.choice(np.arange(model.vocab_size), p=probs))
        tokens.append(next_token)
    return decode(tokens, itos)


def _svg_line_chart(history: dict, path: Path) -> None:
    width, height = 960, 420
    pad_left, pad_right, pad_top, pad_bottom = 70, 25, 25, 55
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom

    train = history.get("train_loss", [])
    val_points = history.get("val_loss", [])
    if not train:
        path.write_text("<svg xmlns='http://www.w3.org/2000/svg' width='1' height='1'/>", encoding="utf-8")
        return

    all_vals = list(train) + [float(item["loss"]) for item in val_points] if val_points else list(train)
    y_min = min(all_vals)
    y_max = max(all_vals)
    if y_max - y_min < 1e-9:
        y_max = y_min + 1.0

    def scale_x(i: int, n: int) -> float:
        return pad_left + (i / max(1, n - 1)) * plot_w

    def scale_y(v: float) -> float:
        return pad_top + (1.0 - (v - y_min) / (y_max - y_min)) * plot_h

    def polyline(points: list[tuple[float, float]], stroke: str) -> str:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        return f"<polyline fill='none' stroke='{stroke}' stroke-width='2.5' points='{pts}' />"

    train_points = [(scale_x(i, len(train)), scale_y(v)) for i, v in enumerate(train)]
    val_points_xy = [
        (scale_x(min(len(train) - 1, int(item["step"]) - 1), len(train)), scale_y(float(item["loss"])))
        for item in val_points
    ]

    svg = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        "<rect width='100%' height='100%' fill='#0b1020' />",
        f"<text x='{pad_left}' y='20' fill='#e5e7eb' font-size='16' font-family='monospace'>NanoGPT-lite learning curve</text>",
        f"<line x1='{pad_left}' y1='{pad_top}' x2='{pad_left}' y2='{pad_top + plot_h}' stroke='#6b7280' stroke-width='1' />",
        f"<line x1='{pad_left}' y1='{pad_top + plot_h}' x2='{pad_left + plot_w}' y2='{pad_top + plot_h}' stroke='#6b7280' stroke-width='1' />",
    ]
    if len(train_points) >= 2:
        svg.append(polyline(train_points, "#60a5fa"))
    if len(val_points_xy) >= 2:
        svg.append(polyline(val_points_xy, "#f59e0b"))
    for x, y in val_points_xy:
        svg.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.5' fill='#f59e0b' />")
    svg.append(
        f"<text x='{pad_left}' y='{height - 15}' fill='#9ca3af' font-size='12' font-family='monospace'>"
        f"train=blue  val=amber  min={y_min:.3f}  max={y_max:.3f}</text>"
    )
    svg.append("</svg>")
    path.write_text("\n".join(svg), encoding="utf-8")


def plot_history(history: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _svg_line_chart(history, path)


def apply_patch(base: NanoGPTConfig, patch: dict) -> NanoGPTConfig:
    data = asdict(base)
    for key, value in patch.items():
        if key in data and value is not None:
            data[key] = value
    return NanoGPTConfig(**data)


def summarize_config(cfg: NanoGPTConfig) -> str:
    return json.dumps(asdict(cfg), indent=2, sort_keys=True)


def train_and_evaluate(
    config: NanoGPTConfig,
    *,
    out_dir: Path,
    corpus_text: str | None = None,
) -> dict:
    random.seed(config.seed)
    np.random.seed(config.seed)
    rng = np.random.default_rng(config.seed)

    corpus_text = corpus_text or build_corpus()
    stoi, itos = build_vocab(corpus_text)
    tokens = encode(corpus_text, stoi)
    split = int(len(tokens) * config.train_ratio)
    train_tokens = tokens[:split]
    val_tokens = tokens[max(0, split - config.block_size - 1) :]
    train_ds = CharDataset(train_tokens, config.block_size)
    val_ds = CharDataset(val_tokens, config.block_size)

    model = TinyNumpyLM(
        vocab_size=len(itos),
        block_size=config.block_size,
        n_embd=config.n_embd,
        hidden_size=config.hidden_size,
        seed=config.seed,
    )

    history = {"train_loss": [], "val_loss": []}
    for step in range(1, config.max_steps + 1):
        x, y = train_ds.sample_batch(rng, config.batch_size)
        loss, grads = model.loss_and_grads(x, y)
        model.step(grads, config.lr, config.weight_decay, config.grad_clip)
        history["train_loss"].append(float(loss))
        if step % config.eval_interval == 0 or step == config.max_steps:
            val_loss = _evaluate(model, val_ds, rng, config.batch_size, config.eval_batches)
            history["val_loss"].append({"step": step, "loss": val_loss})

    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = {
        "final_train_loss": float(history["train_loss"][-1]),
        "final_val_loss": float(history["val_loss"][-1]["loss"]) if history["val_loss"] else float("nan"),
        "vocab_size": len(itos),
        "steps": config.max_steps,
    }

    np.savez_compressed(
        out_dir / "checkpoint.npz",
        **{name: value for name, value in model.params.items()},
        config=json.dumps(asdict(config), sort_keys=True),
        stoi=json.dumps(stoi, sort_keys=True),
        itos=json.dumps(itos, ensure_ascii=False),
    )
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    plot_history(history, out_dir / "learning_curve.svg")
    sample = generate_sample(model, stoi, itos, prompt="science ", max_new_tokens=160)
    (out_dir / "sample.txt").write_text(sample, encoding="utf-8")
    return {"metrics": metrics, "history": history, "sample": sample, "config": asdict(config)}

