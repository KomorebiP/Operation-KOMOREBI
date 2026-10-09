"""Adaptive Multiscale Singular Packet Decomposition."""

from ._version import __version__ as __version__
from .api import (
    AMSpdConfig,
    AMSpdResult,
    config_from_mapping,
    reconstruct,
    reconstruct_from_core,
    resume_model,
)
from .batch import BatchRecord, BatchResult, discover_images, run_batch
from .benchmark import BenchmarkRecord, run_builtin_benchmark
from .components import (
    BaselineResult,
    PixelClosure,
    TreeOptimizationResult,
    compare_baselines,
    complete_with_pixels,
    component_summary,
    fit_packet_core,
    fit_portfolio,
    fit_singular_packets,
    optimize_trees,
)
from .io import load_image, save_image
from .model import AMSpdModel
from .reference import (
    PaperCaseResult,
    available_paper_cases,
    load_paper_reference,
    reproduce_paper,
    reproduce_paper_case,
)
from .tiled import (
    TiledAMSpdModel,
    TiledAMSpdResult,
    TiledConfig,
    TileRegion,
    compare_model_archives,
    load_model_archive,
    resume_tiled_model,
    tile_regions,
    tiled_reconstruct,
)
from .tuning import AutoTuneResult, TuningRecord, auto_tune, tuning_candidates

# Intuitive compatibility aliases for the consolidated tiled implementation.
TileConfig = TiledConfig
reconstruct_tiled = tiled_reconstruct

__all__ = [
    "AMSpdConfig",
    "AMSpdModel",
    "AMSpdResult",
    "AutoTuneResult",
    "BaselineResult",
    "BatchRecord",
    "BatchResult",
    "BenchmarkRecord",
    "PaperCaseResult",
    "TileConfig",
    "PixelClosure",
    "TileRegion",
    "TiledAMSpdModel",
    "TiledAMSpdResult",
    "TiledConfig",
    "TreeOptimizationResult",
    "TuningRecord",
    "auto_tune",
    "available_paper_cases",
    "compare_baselines",
    "compare_model_archives",
    "complete_with_pixels",
    "component_summary",
    "config_from_mapping",
    "discover_images",
    "fit_packet_core",
    "fit_portfolio",
    "fit_singular_packets",
    "load_image",
    "load_model_archive",
    "load_paper_reference",
    "optimize_trees",
    "reconstruct",
    "reconstruct_tiled",
    "reconstruct_from_core",
    "reproduce_paper",
    "reproduce_paper_case",
    "resume_model",
    "resume_tiled_model",
    "run_batch",
    "run_builtin_benchmark",
    "save_image",
    "tile_regions",
    "tiled_reconstruct",
    "tuning_candidates",
]
