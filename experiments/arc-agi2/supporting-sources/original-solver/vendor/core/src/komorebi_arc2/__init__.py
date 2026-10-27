"""Bayesian PR-LASM ARC-AGI-2 package."""

from .atlas import ARCAtlasAnalyzer, TaskSignalState, analyze_task_signal
from .entry import AUTHOR, SOLVER_NAME, SOLVER_VERSION, solve_task
from .lasm_bayesian import (
    BayesianProjectorResolvedLargeSignalModel,
    LASMCalibration,
    LASMTaskPosterior,
    load_calibration,
)
from .macro_runtime import LearnerSnapshot
from .prequential_learning import (
    MacroMinerConfig,
    PrequentialLearnerState,
    begin_prequential_query,
    reveal_prequential_query,
    solve_prequential_query,
)

__all__ = [
    "ARCAtlasAnalyzer",
    "AUTHOR",
    "BayesianProjectorResolvedLargeSignalModel",
    "LASMCalibration",
    "LASMTaskPosterior",
    "LearnerSnapshot",
    "MacroMinerConfig",
    "PrequentialLearnerState",
    "SOLVER_NAME",
    "SOLVER_VERSION",
    "TaskSignalState",
    "analyze_task_signal",
    "begin_prequential_query",
    "load_calibration",
    "reveal_prequential_query",
    "solve_prequential_query",
    "solve_task",
]
__version__ = SOLVER_VERSION
