#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.models import RecurrentOperatorModel, build_model

DEVICE = torch.device("cpu")
ARMS = ("linear_terminal", "linear_relation", "gru_terminal")
MODEL_BY_ARM = {
    "linear_terminal": "linear_hyper",
    "linear_relation": "linear_hyper",
    "gru_terminal": "gru",
}
FAMILIES = ("d4", "c8", "mixed_cycle", "random")
LENGTHS = (1, 4, 8, 12)
EXAMPLES = 4096
BATCH = 512


def load_model(arm: str, seed: int) -> RecurrentOperatorModel:
    model = build_model(MODEL_BY_ARM[arm], max_length=12)
    payload = torch.load(ROOT / "results" / "pilot" / "checkpoints" / f"{arm}_seed{seed}.pt", map_location="cpu")
    model.load_state_dict(payload["state_dict"])
    model.eval()
    if not isinstance(model, RecurrentOperatorModel):
        raise TypeError(arm)
    return model


def summarize_model(model: RecurrentOperatorModel, seed: int) -> dict[str, Any]:
    output: dict[str, Any] = {"families": {}}
    with torch.no_grad():
        for family_index, family in enumerate(FAMILIES):
            family_out: dict[str, Any] = {}
            for length in LENGTHS:
                generator = EpisodeGenerator(seed + 10000 * family_index + 100 * length)
                cosines: list[torch.Tensor] = []
                normalized_l2: list[torch.Tensor] = []
                nearest_exact = 0
                decoder_exact = 0
                count = 0
                hidden_chunks: list[torch.Tensor] = []
                target_chunks: list[torch.Tensor] = []
                for offset in range(0, EXAMPLES, BATCH):
                    current = min(BATCH, EXAMPLES - offset)
                    batch = generator.sample(current, length, family=family).to(DEVICE)
                    trace = model.run(batch.tables, batch.op_slots, batch.start)
                    hidden = trace.hidden[-1]
                    target_embedding = model.initial_hidden(batch.target)
                    cosines.append(F.cosine_similarity(hidden, target_embedding, dim=1).cpu())
                    normalized_l2.append(
                        ((hidden - target_embedding).norm(dim=1) / target_embedding.norm(dim=1).clamp_min(1e-8)).cpu()
                    )
                    embeddings = model.initial_hidden(torch.arange(8, device=DEVICE))
                    distance = torch.cdist(hidden, embeddings)
                    nearest_exact += int((distance.argmin(dim=1) == batch.target).sum())
                    decoder_exact += int((trace.logits.argmax(dim=1) == batch.target).sum())
                    count += current
                    if family == "d4" and length == 8:
                        hidden_chunks.append(hidden.cpu())
                        target_chunks.append(batch.target.cpu())
                cos = torch.cat(cosines)
                l2 = torch.cat(normalized_l2)
                family_out[str(length)] = {
                    "examples": count,
                    "decoder_exact": decoder_exact / count,
                    "nearest_state_embedding_exact": nearest_exact / count,
                    "hidden_to_target_embedding_cosine_mean": float(cos.mean()),
                    "hidden_to_target_embedding_cosine_median": float(cos.median()),
                    "hidden_to_target_embedding_normalized_l2_mean": float(l2.mean()),
                    "hidden_to_target_embedding_normalized_l2_median": float(l2.median()),
                }
                if hidden_chunks:
                    h = torch.cat(hidden_chunks)
                    y = torch.cat(target_chunks)
                    global_mean = h.mean(dim=0)
                    total_ss = ((h - global_mean) ** 2).sum()
                    within_ss = torch.zeros(())
                    centroids = []
                    for state in range(8):
                        group = h[y == state]
                        centroid = group.mean(dim=0)
                        centroids.append(centroid)
                        within_ss += ((group - centroid) ** 2).sum()
                    centroids_t = torch.stack(centroids)
                    centroid_exact = int((torch.cdist(h, centroids_t).argmin(dim=1) == y).sum()) / h.shape[0]
                    family_out[str(length)]["within_state_fraction_of_total_ss"] = float(within_ss / total_ss.clamp_min(1e-8))
                    family_out[str(length)]["nearest_state_centroid_exact"] = centroid_exact
            output["families"][family] = family_out
    return output


def main() -> None:
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    result: dict[str, Any] = {
        "schema": "komorebi.neuralese.posthoc_geometry.v1",
        "status": "exploratory_posthoc_not_preregistered",
        "examples_per_cell": EXAMPLES,
        "arms": {},
    }
    for arm in ARMS:
        per_seed = []
        for seed in (0, 1):
            per_seed.append(summarize_model(load_model(arm, seed), 900000 + seed))
        result["arms"][arm] = per_seed
    path = ROOT / "results" / "pilot" / "POSTHOC_GEOMETRY.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Exploratory posthoc geometry audit",
        "",
        "This audit was designed after the developmental pilot and is not preregistered evidence.",
        "It asks whether successful decoded computation requires recurrent states to collapse onto the original state-embedding points.",
        "",
        "| Arm | D4 length 8 decoded | Nearest original embedding | Nearest empirical state centroid | Within-state variance fraction | Hidden/embedding cosine | Hidden/embedding normalized L2 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        cells = [seed_result["families"]["d4"]["8"] for seed_result in result["arms"][arm]]
        mean = lambda key: float(np.mean([cell[key] for cell in cells]))
        lines.append(
            f"| {arm} | {mean('decoder_exact'):.4f} | {mean('nearest_state_embedding_exact'):.4f} | "
            f"{mean('nearest_state_centroid_exact'):.4f} | {mean('within_state_fraction_of_total_ss'):.4f} | "
            f"{mean('hidden_to_target_embedding_cosine_mean'):.4f} | "
            f"{mean('hidden_to_target_embedding_normalized_l2_mean'):.4f} |"
        )
    lines += [
        "",
        "## Reading",
        "",
        "High decoded accuracy with materially lower nearest-embedding recovery means the recurrent trajectory need not return to a single canonical point for each state. The relevant semantics can instead occupy a path-dependent region or decision-equivalence class. Relation regularization can then be evaluated by how strongly it contracts those classes without assuming exact point identity.",
        "",
    ]
    (ROOT / "results" / "pilot" / "POSTHOC_GEOMETRY.md").write_text("\n".join(lines), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
