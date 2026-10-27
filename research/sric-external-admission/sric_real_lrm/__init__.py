"""SRIC Block 24 external latent-reasoner causal-semantic admission."""

__version__ = "0.3.2"

from .schemas import AuditConfig, AuditThresholds, SemanticThresholds, TaskRecord, TraceObservation
from .pipeline import run_block24_pipeline

__all__ = [
    "AuditConfig",
    "AuditThresholds",
    "SemanticThresholds",
    "TaskRecord",
    "TraceObservation",
    "run_block24_pipeline",
]
