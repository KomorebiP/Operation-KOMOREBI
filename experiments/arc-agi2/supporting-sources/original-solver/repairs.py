"""Executable negative evidence for explicitly scoped repairs.

An abstention is not a veto. A veto must name its ancestor and a checked
structural witness. This module has no task IDs or evaluation labels.
Author: Komorebi P.
"""
from __future__ import annotations
import contract


def inspect_repair(candidate):
    program = candidate.get("program", {})
    if candidate["entrant"] != "multiscale_codec" or program.get("operator") != "scalar_feature_codebook":
        return {"status": "out_of_scope"}
    if program.get("feature") == "orthogonal_symmetry_span3":
        return {"status": "out_of_scope"}
    mapping = program.get("mapping")
    if not isinstance(mapping, list):
        return {"status": "unknown", "reason": "malformed_codebook"}
    by_label = {}
    for item in mapping:
        if not isinstance(item, list) or len(item) != 2:
            return {"status": "unknown", "reason": "malformed_codebook"}
        key, label = item
        by_label.setdefault(str(label), []).append(key)
    collisions = {k: sorted(set(v)) for k, v in by_label.items() if len(set(v)) > 1}
    if not collisions:
        return {"status": "supported", "reason": "injective_structural_codebook"}
    witness = {"ancestor": candidate["entrant"], "program_hash": contract.digest(program),
               "repair": "multiscale_codec_v2.injective_scalar_guard", "collisions": collisions}
    return {"status": "veto", "reason": "noninjective_structural_codebook",
            "witness": witness, "witness_hash": contract.digest(witness)}
