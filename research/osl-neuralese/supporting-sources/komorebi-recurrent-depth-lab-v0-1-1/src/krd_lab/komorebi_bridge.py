"""Optional bridge to the existing ``komorebi_math`` package."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import numpy as np


def verify_with_komorebi(
    operator: np.ndarray,
    projectors: Sequence[np.ndarray],
    names: Sequence[str],
    *,
    komorebi_src: str | None = None,
    exponent: int = 5,
) -> dict:
    if komorebi_src:
        source = str(Path(komorebi_src).expanduser().resolve())
        if source not in sys.path:
            sys.path.insert(0, source)
    try:
        from komorebi_math.core import PacketOperator, PacketSystem
    except ImportError as exc:
        return {"available": False, "reason": str(exc)}

    system = PacketSystem(projectors, names=names, backend="numpy", tolerance=1e-10)
    packet_operator = PacketOperator.from_operator(operator, system)
    powered = packet_operator.power(exponent)
    target = np.linalg.matrix_power(np.asarray(operator), exponent)
    return {
        "available": True,
        "packet_certificate_valid": system.certificate().valid,
        "operator_certificate_valid": packet_operator.certificate().valid,
        "one_step_reconstruction_residual": float(np.linalg.norm(packet_operator.reconstruct() - operator)),
        "path_power_residual": float(np.linalg.norm(powered.reconstruct() - target)),
        "block_norms": [list(row) for row in packet_operator.block_norms()],
        "theorem_ids": ["PSC-I-T20", "PSC-I-T27"],
    }

