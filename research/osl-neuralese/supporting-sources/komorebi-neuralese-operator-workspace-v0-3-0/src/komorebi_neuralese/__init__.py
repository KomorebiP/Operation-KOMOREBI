"""Komorebi Neuralese Operator Workspace laboratory."""

from .algebra import D4_RELATIONS, N_STATES, canonical_maps
from .data import EpisodeBatch, EpisodeGenerator
from .models import (
    GRUOperatorRNN,
    LinearHyperOperatorRNN,
    LinearHyperMetricOperatorRNN,
    LearnedSPDMetric,
    OneShotMLP,
    TokenOnlyRNN,
    build_model,
)
from .hard_operator import ExactTableOracle, HardMetricOperatorRNN, HardOperatorRNN
from .version import VERSION as __version__
from .splits import (
    COORDINATE_SPLIT_COUNTS,
    COORDINATE_SPLIT_NAMESPACE,
    COORDINATE_SPLITS,
    WORD_PRODUCT_SCOPES,
    CoordinateSplitAudit,
    audit_coordinate_splits,
    enumerate_coordinate_split_audit,
    map_fingerprint,
    map_split,
    map_splits,
    maps_all_in_split,
    permutations_in_split,
    validate_coordinate_split,
    validate_word_product_scope,
    word_product_maps,
    word_products_all_in_split,
)

__all__ = [
    "D4_RELATIONS",
    "N_STATES",
    "canonical_maps",
    "COORDINATE_SPLIT_COUNTS",
    "COORDINATE_SPLIT_NAMESPACE",
    "COORDINATE_SPLITS",
    "WORD_PRODUCT_SCOPES",
    "CoordinateSplitAudit",
    "EpisodeBatch",
    "EpisodeGenerator",
    "ExactTableOracle",
    "GRUOperatorRNN",
    "HardMetricOperatorRNN",
    "HardOperatorRNN",
    "LinearHyperOperatorRNN",
    "LinearHyperMetricOperatorRNN",
    "LearnedSPDMetric",
    "OneShotMLP",
    "TokenOnlyRNN",
    "audit_coordinate_splits",
    "build_model",
    "enumerate_coordinate_split_audit",
    "map_fingerprint",
    "map_split",
    "map_splits",
    "maps_all_in_split",
    "permutations_in_split",
    "validate_coordinate_split",
    "validate_word_product_scope",
    "word_product_maps",
    "word_products_all_in_split",
    "__version__",
]
