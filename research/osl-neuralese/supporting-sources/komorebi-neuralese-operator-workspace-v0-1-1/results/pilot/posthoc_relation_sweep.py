#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.evaluate import accuracy_by_length, relation_metrics
from komorebi_neuralese.models import LinearHyperOperatorRNN
from komorebi_neuralese.train import _relation_loss

WEIGHTS = (0.0, 0.01, 0.03, 0.10, 0.15, 0.30, 0.60)
SEEDS = (0, 1)
STEPS = 1600
BATCH = 256
DEVICE = torch.device("cpu")


def train(seed: int, relation_weight: float) -> tuple[LinearHyperOperatorRNN, float]:
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = LinearHyperOperatorRNN(hidden_dim=8).to(DEVICE)
    generator = EpisodeGenerator(10_000 + seed)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-6)
    started = time.perf_counter()
    for _ in range(STEPS):
        length = int(generator.rng.integers(1, 5))
        batch = generator.sample(BATCH, length, family="d4").to(DEVICE)
        trace = model.run(batch.tables, batch.op_slots, batch.start)
        loss = F.cross_entropy(trace.logits, batch.target)
        if relation_weight:
            loss = loss + relation_weight * _relation_loss(
                model, batch.tables, batch.start, batch.canonical_to_slot, hidden_weight=0.05
            )
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
    return model, time.perf_counter() - started


def hidden_norm(model: LinearHyperOperatorRNN, seed: int, length: int, family: str = "d4") -> float:
    generator = EpisodeGenerator(seed)
    values = []
    with torch.no_grad():
        for _ in range(4):
            batch = generator.sample(256, length, family=family).to(DEVICE)
            values.append(model.run(batch.tables, batch.op_slots, batch.start).hidden[-1].norm(dim=1).cpu())
    return float(torch.cat(values).median())


def spectral_radius(model: LinearHyperOperatorRNN, seed: int, family: str = "d4") -> tuple[float, float]:
    batch = EpisodeGenerator(seed).sample(1024, 0, family=family).to(DEVICE)
    with torch.no_grad():
        codes = model.encode_operators(batch.tables).reshape(-1, 8, 8)
        radius = torch.linalg.eigvals(codes).abs().amax(dim=1).real
    return float(radius.median()), float(torch.quantile(radius, 0.95))


def main() -> None:
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    rows = []
    for weight in WEIGHTS:
        for seed in SEEDS:
            print(f"TRAIN relation_weight={weight:.2f} seed={seed}", flush=True)
            model, elapsed = train(seed, weight)
            d4 = accuracy_by_length(model, "d4", (4, 8, 12, 32, 64), 1024, 256, 300_000 + seed, DEVICE)
            c8 = accuracy_by_length(model, "c8", (8, 12, 32), 1024, 256, 310_000 + seed, DEVICE)
            random = accuracy_by_length(model, "random", (4, 8, 12), 1024, 256, 320_000 + seed, DEVICE)
            relations = relation_metrics(model, 1024, 256, 330_000 + seed, DEVICE)
            radius_median, radius_p95 = spectral_radius(model, 340_000 + seed)
            relation_hidden = float(np.mean([item["hidden_return_normalized_l2_mean"] for item in relations.values()]))
            row = {
                "relation_weight": weight,
                "seed": seed,
                "elapsed_seconds": elapsed,
                "d4_l4": d4["4"],
                "d4_l8": d4["8"],
                "d4_l12": d4["12"],
                "d4_l32": d4["32"],
                "d4_l64": d4["64"],
                "c8_l8": c8["8"],
                "c8_l12": c8["12"],
                "c8_l32": c8["32"],
                "random_l4": random["4"],
                "random_l8": random["8"],
                "random_l12": random["12"],
                "relation_hidden_residual": relation_hidden,
                "spectral_radius_median": radius_median,
                "spectral_radius_p95": radius_p95,
                "hidden_norm_l32_median": hidden_norm(model, 350_000 + seed, 32),
                "hidden_norm_l64_median": hidden_norm(model, 360_000 + seed, 64),
            }
            rows.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)

    json_path = ROOT / "results" / "pilot" / "POSTHOC_RELATION_SWEEP.json"
    csv_path = ROOT / "results" / "pilot" / "POSTHOC_RELATION_SWEEP.csv"
    json_path.write_text(json.dumps({"status":"exploratory_posthoc_not_preregistered","steps":STEPS,"rows":rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

    aggregate = []
    for weight in WEIGHTS:
        subset = [row for row in rows if row["relation_weight"] == weight]
        entry = {"relation_weight": weight}
        for key in rows[0]:
            if key not in {"relation_weight", "seed"}:
                entry[key] = float(np.mean([row[key] for row in subset]))
        aggregate.append(entry)

    lines = [
        "# Exploratory relation-pressure phase sweep",
        "",
        "This sweep was designed after the developmental pilot. It is mechanistic exploration, not confirmatory evidence.",
        "Every condition uses identical architecture, initialization by seed, data stream by seed, optimization budget, and terminal objective; only the D4 relation-loss weight changes.",
        "",
        "| Relation weight | D4 L12 | D4 L32 | D4 L64 | C8 L12 | Random L12 | Median spectral radius | Relation hidden residual | Median hidden norm L64 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(
            f"| {row['relation_weight']:.2f} | {row['d4_l12']:.4f} | {row['d4_l32']:.4f} | {row['d4_l64']:.4f} | "
            f"{row['c8_l12']:.4f} | {row['random_l12']:.4f} | {row['spectral_radius_median']:.4f} | "
            f"{row['relation_hidden_residual']:.4f} | {row['hidden_norm_l64_median']:.3g} |"
        )
    best = max(aggregate, key=lambda row: row["d4_l64"])
    lines += [
        "",
        "## Initial interpretation",
        "",
        f"The best tested D4 depth-64 condition used relation weight `{best['relation_weight']:.2f}` and reached `{best['d4_l64']:.4f}` mean accuracy across two seeds.",
        "The sweep tests whether relation consistency acts as a dynamical-stability regularizer. It does not establish that the hidden matrices form an exact group representation, because ambient and hidden-return residuals remain nonzero.",
        "",
    ]
    md_path = ROOT / "results" / "pilot" / "POSTHOC_RELATION_SWEEP.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
        x = [row["relation_weight"] for row in aggregate]
        figure = plt.figure(figsize=(8, 6), dpi=180)
        axis = figure.add_subplot(111)
        axis.plot(x, [row["d4_l12"] for row in aggregate], marker="o", label="D4 length 12")
        axis.plot(x, [row["d4_l32"] for row in aggregate], marker="o", label="D4 length 32")
        axis.plot(x, [row["d4_l64"] for row in aggregate], marker="o", label="D4 length 64")
        axis.set_xlabel("Relation-loss weight")
        axis.set_ylabel("Exact accuracy")
        axis.set_ylim(0.0, 1.03)
        axis.set_title("Depth stability under relation pressure")
        axis.legend()
        figure.tight_layout()
        figure.savefig(ROOT / "results" / "pilot" / "relation_weight_depth_accuracy.png")
        plt.close(figure)

        figure = plt.figure(figsize=(8, 6), dpi=180)
        axis = figure.add_subplot(111)
        axis.plot(x, [row["spectral_radius_median"] for row in aggregate], marker="o")
        axis.set_xlabel("Relation-loss weight")
        axis.set_ylabel("Median learned spectral radius")
        axis.set_title("Operator spectral contraction")
        figure.tight_layout()
        figure.savefig(ROOT / "results" / "pilot" / "relation_weight_spectral_radius.png")
        plt.close(figure)
    except Exception as exc:
        (ROOT / "results" / "pilot" / "POSTHOC_RELATION_SWEEP_PLOT_ERROR.txt").write_text(str(exc), encoding="utf-8")

    print(md_path, flush=True)


if __name__ == "__main__":
    main()
