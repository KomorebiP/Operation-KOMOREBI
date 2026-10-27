from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import fuzzy_komorebi as fk

summary = json.loads((ROOT / "results/HOLDOUT_SUMMARY.json").read_text())
analysis = json.loads((ROOT / "results/HOLDOUT_ANALYSIS.json").read_text())
models = analysis["models"]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# 1. Architecture and algebra diagram.
fig, ax = plt.subplots(figsize=(15, 9))
ax.set_xlim(0, 15)
ax.set_ylim(0, 10)
ax.axis("off")
ax.set_title("RRCT v0.57: Fuzzy Komorebi Coalition Formation", fontsize=18, pad=18)


def box(x: float, y: float, w: float, h: float, text: str, lw: float = 1.7) -> None:
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.08",
        fill=False, linewidth=lw,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10.5)


def arrow(x1: float, y1: float, x2: float, y2: float, text: str | None = None) -> None:
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, linewidth=1.5))
    if text:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.13, text, ha="center", fontsize=9)

box(0.6, 7.6, 3.4, 1.25, "Anonymous noisy task-demand cue\nNo family or membership labels")
box(5.2, 7.6, 4.6, 1.25, "Terminally trained membership router\nU ∈ [0,1]⁴ˣ⁴; rows sum to one", 2.0)
box(11.0, 7.6, 3.4, 1.25, "Fuzzy packet operators\nEₖ = diag(U:ₖ)\nΣEₖ = I; Eₖ² need not equal Eₖ", 2.0)
box(1.1, 4.7, 3.6, 1.3, "Crisp task\nMembership sharpens\nLow entropy and lower idempotence defect")
box(5.7, 4.7, 3.6, 1.3, "Overlapping task\nGraded memberships remain\nNon-idempotence is task-relevant")
box(10.3, 4.7, 3.6, 1.3, "Fuzzy transfer blocks\nTᵢⱼ = Eᵢ T Eⱼ\nΣᵢⱼTᵢⱼ = T", 2.0)
box(4.8, 2.25, 5.4, 1.2, "Graded coalition coupling\nC(U) = Σₖ gₖ U:ₖ U:ₖᵀ\nTerminal action y = tanh(x + βC(U)x)", 2.0)
box(5.1, 0.45, 4.8, 0.95, "Causal tests\nHardening, membership ablation, transport, and direct-edge control")

arrow(4.0, 8.2, 5.2, 8.2)
arrow(9.8, 8.2, 11.0, 8.2)
arrow(7.5, 7.6, 2.9, 6.0)
arrow(7.5, 7.6, 7.5, 6.0)
arrow(12.7, 7.6, 12.1, 6.0)
arrow(2.9, 4.7, 6.2, 3.45)
arrow(7.5, 4.7, 7.5, 3.45)
arrow(12.1, 4.7, 8.8, 3.45)
arrow(7.5, 2.25, 7.5, 1.4)
ax.text(0.6, 0.08, "Private packet 0 plus three shared workspace packets. Fuzziness is membership degree, not probability or subjective uncertainty.", fontsize=9.8)
fig.savefig(FIG / "01_fuzzy_packet_architecture.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# 2. Family-specific predictive error.
variants = ["direct", "fuzzy", "crystal", "hard"]
labels = ["Direct fuzzy edges", "Fuzzy packets", "Crystallized packets", "Learned hard packets"]
families = ["crisp", "familiar_blend", "diffuse", "novel_blend"]
family_labels = ["Crisp", "Familiar blends", "Diffuse", "Held-out mid-blends"]
x = np.arange(len(families))
width = 0.18
fig, ax = plt.subplots(figsize=(13, 7.2))
for index, (variant, label) in enumerate(zip(variants, labels)):
    values = [summary[variant][f"mean_{family}_mse"] for family in families]
    ax.bar(x + (index - 1.5) * width, values, width, label=label)
# Oracle hard control from fuzzy diagnostics.
oracle_values = [
    summary["fuzzy_diagnostics"]["oracle_hard_crisp_mse"],
    np.mean([row["result"]["oracle_hard_familiar_blend_mse"] for row in models if row["variant"] == "fuzzy"]),
    np.mean([row["result"]["oracle_hard_diffuse_mse"] for row in models if row["variant"] == "fuzzy"]),
    summary["fuzzy_diagnostics"]["oracle_hard_novel_blend_mse"],
]
ax.plot(x, oracle_values, marker="o", linestyle="--", label="Oracle crispification")
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels(family_labels)
ax.set_ylabel("Mean squared terminal error (log scale)")
ax.set_title("Fuzzy Structure Is Necessary on Graded Coalition Tasks", fontsize=16, pad=14)
ax.grid(axis="y", alpha=0.2)
ax.legend()
fig.savefig(FIG / "02_family_error_comparison.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# 3. Entropy and idempotence separation.
fuzzy_rows = [row["result"] for row in models if row["variant"] == "fuzzy"]
metrics = {
    "Membership entropy": (
        np.mean([r["crisp_membership_entropy"] for r in fuzzy_rows]),
        np.mean([r["novel_blend_membership_entropy"] for r in fuzzy_rows]),
    ),
    "Idempotence defect": (
        np.mean([r["crisp_idempotence_defect"] for r in fuzzy_rows]),
        np.mean([r["novel_blend_idempotence_defect"] for r in fuzzy_rows]),
    ),
}
fig, ax = plt.subplots(figsize=(9.5, 6.5))
x = np.arange(len(metrics))
width = 0.34
crisp_values = [value[0] for value in metrics.values()]
overlap_values = [value[1] for value in metrics.values()]
ax.bar(x - width/2, crisp_values, width, label="Crisp tasks")
ax.bar(x + width/2, overlap_values, width, label="Held-out overlap tasks")
ax.set_xticks(x)
ax.set_xticklabels(list(metrics.keys()))
ax.set_ylabel("Normalized magnitude")
ax.set_ylim(0, 1.05)
ax.set_title("The Learned Geometry Sharpens Selectively", fontsize=16, pad=14)
ax.grid(axis="y", alpha=0.2)
ax.legend()
for index, value in enumerate(crisp_values):
    ax.text(index - width/2, value + 0.025, f"{value:.3f}", ha="center")
for index, value in enumerate(overlap_values):
    ax.text(index + width/2, value + 0.025, f"{value:.3f}", ha="center")
fig.savefig(FIG / "03_crisp_vs_fuzzy_geometry.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# 4. Training trajectory averaged across holdout seeds.
steps = [100, 200, 400, 800, 1200, 1600, 2000]
curve_rows = [row["curve"] for row in models if row["variant"] == "fuzzy"]
mean_mse = [np.mean([curve[str(step)]["mse"] for curve in curve_rows]) for step in steps]
mean_crisp_entropy = [np.mean([curve[str(step)]["crisp_entropy"] for curve in curve_rows]) for step in steps]
mean_fuzzy_entropy = [np.mean([curve[str(step)]["fuzzy_entropy"] for curve in curve_rows]) for step in steps]
fig, ax = plt.subplots(figsize=(11, 6.7))
ax.plot(steps, mean_crisp_entropy, marker="o", label="Crisp-task membership entropy")
ax.plot(steps, mean_fuzzy_entropy, marker="s", label="Fuzzy-task membership entropy")
ax.set_xlabel("Training updates")
ax.set_ylabel("Membership entropy")
ax.set_title("Fuzzy-to-Crisp Differentiation During Training", fontsize=16, pad=14)
ax.grid(alpha=0.2)
ax.legend()
fig.savefig(FIG / "04_training_entropy_trajectory.png", dpi=220, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 6.7))
ax.plot(steps, mean_mse, marker="o")
ax.set_yscale("log")
ax.set_xlabel("Training updates")
ax.set_ylabel("Holdout MSE (log scale)")
ax.set_title("Terminal Performance Improves as Packet Geometry Organizes", fontsize=16, pad=14)
ax.grid(alpha=0.2)
fig.savefig(FIG / "05_training_error_trajectory.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# 5. Causal membership calibration from one frozen model.
seed = summary["holdout_seeds"][0]
model, _ = fk.load_model(ROOT / f"models/holdout/fuzzy_{seed}.pt")
batch = fk.sample_batch(3000, torch.Generator().manual_seed(fk.deterministic_seed(f"figure-causal:{seed}")), split="holdout")
with torch.no_grad():
    _, membership = model(batch["cue"], batch["values"])
base = ((fk.actions(batch["values"], membership) - batch["target"]) ** 2).mean(dim=-1)
strengths = []
effects = []
for agent in range(fk.N_AGENTS):
    for packet in range(1, fk.N_PACKETS):
        modified = membership.clone()
        mass = modified[:, agent, packet].clone()
        modified[:, agent, packet] = 0.0
        modified[:, agent, 0] += mass
        effect = ((fk.actions(batch["values"], modified) - batch["target"]) ** 2).mean(dim=-1) - base
        strength = membership[:, agent, packet] * (membership[:, :, packet].sum(dim=-1) - membership[:, agent, packet]) * fk.GAINS[packet - 1]
        strengths.append(strength.numpy())
        effects.append(effect.numpy())
strength = np.concatenate(strengths)
effect = np.concatenate(effects)
# Plot a deterministic subsample for legibility.
index = np.linspace(0, len(strength)-1, 6000, dtype=int)
fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(strength[index], effect[index], s=8, alpha=0.18)
ax.set_xlabel("Predicted membership interaction strength")
ax.set_ylabel("Increase in terminal loss after membership ablation")
ax.set_title("Fuzzy Membership Strength Predicts Causal Importance", fontsize=16, pad=14)
ax.grid(alpha=0.2)
ax.text(0.03, 0.95, f"Frozen-seed correlation = {np.corrcoef(strength, effect)[0,1]:.3f}", transform=ax.transAxes, va="top")
fig.savefig(FIG / "06_causal_membership_calibration.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# 6. Temperature sweep.
temperatures = [0.15, 0.25, 0.5, 1.0, 2.0]
crisp = []
novel = []
for temperature in temperatures:
    key = str(temperature)
    crisp.append(np.mean([r["temperature_sweep"][key]["crisp_mse"] for r in fuzzy_rows]))
    novel.append(np.mean([r["temperature_sweep"][key]["novel_blend_mse"] for r in fuzzy_rows]))
fig, ax = plt.subplots(figsize=(10, 6.7))
ax.plot(temperatures, crisp, marker="o", label="Crisp tasks")
ax.plot(temperatures, novel, marker="s", label="Held-out overlap tasks")
ax.set_yscale("log")
ax.set_xscale("log")
ax.set_xlabel("Post-hoc membership temperature")
ax.set_ylabel("MSE (log scale)")
ax.set_title("Uniform Sharpening Is Not a Free Improvement", fontsize=16, pad=14)
ax.grid(alpha=0.2)
ax.legend()
fig.savefig(FIG / "07_temperature_sweep.png", dpi=220, bbox_inches="tight")
plt.close(fig)

print("figures", len(list(FIG.glob("*.png"))))
