"""Komorebi Neuralese ambient-packet laboratory."""

__version__ = "0.3.0"

from .algebra import D4_RELATIONS, N_STATES, canonical_maps
from .data import EpisodeBatch, EpisodeGenerator
from .ambient_packets import (
    ContinuationConstraintSet,
    PacketMarginResult,
    build_continuation_constraints,
    continuation_margins,
    enumerate_suffixes,
)
from .gauge import GaugeDecomposition, decompose_operator_gauge
from .models import (
    GRUOperatorRNN,
    LinearHyperOperatorRNN,
    OneShotMLP,
    TokenOnlyRNN,
    build_model,
)

__all__ = [
    "D4_RELATIONS",
    "N_STATES",
    "canonical_maps",
    "EpisodeBatch",
    "EpisodeGenerator",
    "ContinuationConstraintSet",
    "PacketMarginResult",
    "build_continuation_constraints",
    "continuation_margins",
    "enumerate_suffixes",
    "GaugeDecomposition",
    "decompose_operator_gauge",
    "GRUOperatorRNN",
    "LinearHyperOperatorRNN",
    "OneShotMLP",
    "TokenOnlyRNN",
    "build_model",
]
