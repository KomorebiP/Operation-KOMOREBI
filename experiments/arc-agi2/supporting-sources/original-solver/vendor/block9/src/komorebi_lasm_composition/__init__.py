"""PR-LASM Block 9: Recursive Schema Composition and Abstraction Closure."""
import json
from importlib.resources import files
from .abstraction import (
    CompositeMacroTemplate,
    LeafTemplate,
    PromotionStatus,
    SubtreeOccurrence,
    TypedHole,
    extract_contiguous_subtrees,
    mine_composite_templates,
)
from .bank import AbstractionEvidenceBank, RuntimeAbstractionBank
from .compiler import (
    DEFAULT_LIMITS,
    compile_programs,
    compile_record,
    execute_candidates,
    execute_program,
)
from .model import (
    CompositionCandidate,
    CompositionLimits,
    CompositionTrace,
    CompositeProgram,
    LeafInvocation,
    ProgressCertificate,
    ResidualBatch,
    validate_grid,
)
from .task import TrainingTask, sanitize_training_task

__version__ = "0.5.0"


def load_runtime_abstraction_bank() -> RuntimeAbstractionBank:
    """Load and hash-verify the packaged stable abstraction bank."""

    resource = files(__package__).joinpath("data/runtime_abstraction_bank.json")
    return RuntimeAbstractionBank.verify_runtime_record(
        json.loads(resource.read_text(encoding="utf-8"))
    )

__all__ = [
    "AbstractionEvidenceBank",
    "CompositeMacroTemplate",
    "CompositionCandidate",
    "CompositionLimits",
    "CompositionTrace",
    "CompositeProgram",
    "DEFAULT_LIMITS",
    "LeafInvocation",
    "LeafTemplate",
    "ProgressCertificate",
    "PromotionStatus",
    "ResidualBatch",
    "RuntimeAbstractionBank",
    "SubtreeOccurrence",
    "TrainingTask",
    "TypedHole",
    "compile_programs",
    "compile_record",
    "execute_candidates",
    "execute_program",
    "extract_contiguous_subtrees",
    "mine_composite_templates",
    "load_runtime_abstraction_bank",
    "sanitize_training_task",
    "validate_grid",
]
