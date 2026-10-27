"""Komorebi recurrent-depth analysis lab."""

from .analysis import (
    AffineDMDResult,
    BlockTransportCertificate,
    ContractionCertificate,
    LinearFitResult,
    PathIndependenceResult,
    affine_dmd,
    block_transport_certificate,
    classify_eigenvalues,
    contraction_certificate,
    coordinate_projectors,
    detect_slider,
    last_write_selector,
    linear_operator_fit,
    modulo_cache_profile,
    path_independence,
    pca_reduce,
)

__all__ = [
    "AffineDMDResult",
    "BlockTransportCertificate",
    "ContractionCertificate",
    "LinearFitResult",
    "PathIndependenceResult",
    "affine_dmd",
    "block_transport_certificate",
    "classify_eigenvalues",
    "contraction_certificate",
    "coordinate_projectors",
    "detect_slider",
    "last_write_selector",
    "linear_operator_fit",
    "modulo_cache_profile",
    "path_independence",
    "pca_reduce",
]

__version__ = "0.1.1"
