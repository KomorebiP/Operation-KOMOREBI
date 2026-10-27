"""Komorebi Neuralese stable-quotient laboratory."""

__version__ = "0.2.0"

from .algebra import D4_RELATIONS, N_STATES, canonical_maps
from .data import EpisodeBatch, EpisodeGenerator
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
    "GRUOperatorRNN",
    "LinearHyperOperatorRNN",
    "OneShotMLP",
    "TokenOnlyRNN",
    "build_model",
]
