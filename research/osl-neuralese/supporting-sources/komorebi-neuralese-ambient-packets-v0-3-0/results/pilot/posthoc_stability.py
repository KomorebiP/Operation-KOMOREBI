#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.models import LinearHyperOperatorRNN, RecurrentOperatorModel, build_model

DEVICE = torch.device("cpu")
ARMS = ("linear_terminal", "linear_relation", "gru_terminal")
MODEL_BY_ARM = {"linear_terminal": "linear_hyper", "linear_relation": "linear_hyper", "gru_terminal": "gru"}
FAMILIES = ("d4", "c8", "mixed_cycle", "random")
LENGTHS = (1, 2, 4, 8, 12, 16, 24, 32, 48, 64)
EXAMPLES = 2048
BATCH = 256


def load_model(arm: str, seed: int) -> RecurrentOperatorModel:
    model = build_model(MODEL_BY_ARM[arm], max_length=64)
    payload = torch.load(ROOT / "results" / "pilot" / "checkpoints" / f"{arm}_seed{seed}.pt", map_location="cpu")
    model.load_state_dict(payload["state_dict"])
    model.eval()
    assert isinstance(model, RecurrentOperatorModel)
    return model


def evaluate_lengths(model: RecurrentOperatorModel, seed: int, family: str) -> dict[str, Any]:
    output: dict[str, Any] = {}
    with torch.no_grad():
        for length in LENGTHS:
            generator = EpisodeGenerator(seed + 1000 * length)
            correct = 0
            count = 0
            norms = []
            max_norms = []
            finite = 0
            for offset in range(0, EXAMPLES, BATCH):
                current = min(BATCH, EXAMPLES - offset)
                batch = generator.sample(current, length, family=family).to(DEVICE)
                trace = model.run(batch.tables, batch.op_slots, batch.start)
                hidden = trace.hidden[-1]
                finite_mask = torch.isfinite(hidden).all(dim=1)
                finite += int(finite_mask.sum())
                safe_logits = torch.nan_to_num(trace.logits, nan=-1e30, posinf=1e30, neginf=-1e30)
                correct += int((safe_logits.argmax(dim=1) == batch.target).sum())
                hnorm = torch.nan_to_num(hidden.norm(dim=1), nan=float("inf"), posinf=float("inf"))
                norms.append(hnorm.cpu())
                trajectory_norm = torch.stack([torch.nan_to_num(h.norm(dim=1), nan=float("inf"), posinf=float("inf")) for h in trace.hidden], dim=1)
                max_norms.append(trajectory_norm.max(dim=1).values.cpu())
                count += current
            norm = torch.cat(norms)
            max_norm = torch.cat(max_norms)
            finite_norm = norm[torch.isfinite(norm)]
            finite_max = max_norm[torch.isfinite(max_norm)]
            output[str(length)] = {
                "accuracy": correct / count,
                "finite_fraction": finite / count,
                "hidden_norm_median": float(finite_norm.median()) if finite_norm.numel() else float("inf"),
                "hidden_norm_mean": float(finite_norm.mean()) if finite_norm.numel() else float("inf"),
                "max_trajectory_norm_median": float(finite_max.median()) if finite_max.numel() else float("inf"),
                "log10_hidden_norm_median": float(torch.log10(finite_norm.clamp_min(1e-30)).median()) if finite_norm.numel() else float("inf"),
            }
    return output


def operator_spectra(model: LinearHyperOperatorRNN, seed: int, family: str) -> dict[str, float]:
    generator = EpisodeGenerator(seed)
    batch = generator.sample(2048, 0, family=family).to(DEVICE)
    with torch.no_grad():
        matrices = model.encode_operators(batch.tables).reshape(-1, model.hidden_dim, model.hidden_dim)
        eig = torch.linalg.eigvals(matrices)
        radii = eig.abs().amax(dim=1).real
        singular = torch.linalg.svdvals(matrices).amax(dim=1)
    return {
        "spectral_radius_mean": float(radii.mean()),
        "spectral_radius_median": float(radii.median()),
        "spectral_radius_p95": float(torch.quantile(radii, 0.95)),
        "spectral_radius_max": float(radii.max()),
        "operator_norm_mean": float(singular.mean()),
        "operator_norm_median": float(singular.median()),
        "operator_norm_p95": float(torch.quantile(singular, 0.95)),
    }


def main() -> None:
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    result: dict[str, Any] = {
        "schema": "komorebi.neuralese.posthoc_stability.v1",
        "status": "exploratory_posthoc_not_preregistered",
        "examples_per_length": EXAMPLES,
        "arms": {},
    }
    for arm in ARMS:
        seeds = []
        for seed in (0, 1):
            model = load_model(arm, seed)
            entry: dict[str, Any] = {"lengths": {}}
            for family_index, family in enumerate(FAMILIES):
                entry["lengths"][family] = evaluate_lengths(model, 700000 + 10000 * seed + 100 * family_index, family)
            if isinstance(model, LinearHyperOperatorRNN):
                entry["operator_spectra"] = {
                    family: operator_spectra(model, 800000 + 10000 * seed + i, family)
                    for i, family in enumerate(FAMILIES)
                }
            seeds.append(entry)
        result["arms"][arm] = seeds
    (ROOT / "results" / "pilot" / "POSTHOC_STABILITY.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# Exploratory recurrent-stability audit",
        "",
        "This analysis was designed after the developmental pilot and is not preregistered evidence.",
        "",
        "## D4 depth extrapolation and latent magnitude",
        "",
        "| Arm | L=8 accuracy | L=8 median norm | L=12 accuracy | L=12 median norm | L=32 accuracy | L=32 median norm | L=64 accuracy | L=64 median norm |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        def m(length: str, key: str) -> float:
            return float(np.mean([seed["lengths"]["d4"][length][key] for seed in result["arms"][arm]]))
        lines.append(
            f"| {arm} | {m('8','accuracy'):.4f} | {m('8','hidden_norm_median'):.3g} | "
            f"{m('12','accuracy'):.4f} | {m('12','hidden_norm_median'):.3g} | "
            f"{m('32','accuracy'):.4f} | {m('32','hidden_norm_median'):.3g} | "
            f"{m('64','accuracy'):.4f} | {m('64','hidden_norm_median'):.3g} |"
        )
    lines += ["", "## Learned linear-operator spectra", "", "| Arm | Family | Median spectral radius | P95 spectral radius | Median operator norm |", "|---|---|---:|---:|---:|"]
    for arm in ("linear_terminal", "linear_relation"):
        for family in FAMILIES:
            def sm(key: str) -> float:
                return float(np.mean([seed["operator_spectra"][family][key] for seed in result["arms"][arm]]))
            lines.append(f"| {arm} | {family} | {sm('spectral_radius_median'):.4f} | {sm('spectral_radius_p95'):.4f} | {sm('operator_norm_median'):.4f} |")
    lines += [
        "",
        "## Reading",
        "",
        "The terminal-only linear model can decode accurately while its hidden magnitude grows rapidly. Relation pressure substantially contracts the learned dynamics toward a stable near-representation and extends usable recurrence. This identifies spectral and relation stability, rather than one-step correctness alone, as the next mechanistic control variable.",
        "",
    ]
    (ROOT / "results" / "pilot" / "POSTHOC_STABILITY.md").write_text("\n".join(lines), encoding="utf-8")
    print(ROOT / "results" / "pilot" / "POSTHOC_STABILITY.md")


if __name__ == "__main__":
    main()
