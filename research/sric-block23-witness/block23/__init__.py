"""SRIC Block 23: endogenous semantic-witness growth and real-LRM audit contract."""

from __future__ import annotations

import os

# Keep the finite linear-algebra fixtures deterministic and avoid severe BLAS
# oversubscription on high-core hosts. Callers may override these values before
# importing the package when they intentionally want another thread budget.
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = os.environ.get(f"SRIC_{_name}", "1")

from .core import (
    FAMILIES,
    FINAL_CERTIFICATES,
    EpisodeSpec,
    audit_hidden,
    build_episode,
    compile_ontology,
    expected_certificate,
    summarize_records,
)

__all__ = [
    "FAMILIES",
    "FINAL_CERTIFICATES",
    "EpisodeSpec",
    "audit_hidden",
    "build_episode",
    "compile_ontology",
    "expected_certificate",
    "summarize_records",
]
