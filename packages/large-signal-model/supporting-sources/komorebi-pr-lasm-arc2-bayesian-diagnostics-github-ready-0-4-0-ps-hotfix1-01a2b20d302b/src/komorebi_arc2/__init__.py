"""Bayesian PR-LASM ARC-AGI-2 package."""

from .atlas import ARCAtlasAnalyzer, TaskSignalState, analyze_task_signal
from .entry import AUTHOR, SOLVER_NAME, SOLVER_VERSION, solve_task
from .lasm_bayesian import (
    BayesianProjectorResolvedLargeSignalModel,
    LASMCalibration,
    LASMTaskPosterior,
    load_calibration,
)

__all__ = [
    "ARCAtlasAnalyzer",
    "AUTHOR",
    "BayesianProjectorResolvedLargeSignalModel",
    "LASMCalibration",
    "LASMTaskPosterior",
    "SOLVER_NAME",
    "SOLVER_VERSION",
    "TaskSignalState",
    "analyze_task_signal",
    "load_calibration",
    "solve_task",
]
__version__ = SOLVER_VERSION
