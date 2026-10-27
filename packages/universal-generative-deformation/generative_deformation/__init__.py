"""Universal Generative Deformation Calculus reference implementation."""

from .branches import first_direction_selector, follow_branch
from .covers import IntervalDirectionFamily, dyadic_signed_directions
from .examples import (
    AnalyticExpressionSystem,
    DyadicLimitSystem,
    IntegerWalkSystem,
    PolynomialDeformationSystem,
    ScalarInteractionSystem,
    catalan_numbers,
    fibonacci_numbers,
)
from .extended_examples import (
    AffineShapeSystem,
    CongruenceLiftSystem,
    GaussianFamilySystem,
    GraphDeformationSystem,
    MatrixDeformationSystem,
    QubitGateSystem,
    SequenceTransformSystem,
    path_graph,
    triangle_seed,
)
from .families import (
    FamilyCertificate,
    certify_family,
    cluster_by_signature,
    infer_constant_coefficient_recurrence,
)
from .forest import PerturbationForest, reconstruct_path
from .interactions import generate_interactions
from .metrics import (
    branching_entropy,
    geometric_tree_partition,
    growth_series,
    propagated_cover_error,
    weighted_partition_function,
)
from .model import (
    DeformationSystem,
    Direction,
    ExplorationConfig,
    ForestEdge,
    ForestNode,
    InteractionRule,
    InteractionSystem,
    PathRecord,
    ValidationResult,
)

__all__ = [
    "AnalyticExpressionSystem",
    "DeformationSystem",
    "Direction",
    "DyadicLimitSystem",
    "ExplorationConfig",
    "FamilyCertificate",
    "ForestEdge",
    "ForestNode",
    "IntegerWalkSystem",
    "InteractionRule",
    "InteractionSystem",
    "IntervalDirectionFamily",
    "PathRecord",
    "PerturbationForest",
    "PolynomialDeformationSystem",
    "ScalarInteractionSystem",
    "ValidationResult",
    "branching_entropy",
    "catalan_numbers",
    "certify_family",
    "cluster_by_signature",
    "dyadic_signed_directions",
    "fibonacci_numbers",
    "first_direction_selector",
    "follow_branch",
    "generate_interactions",
    "geometric_tree_partition",
    "growth_series",
    "infer_constant_coefficient_recurrence",
    "propagated_cover_error",
    "reconstruct_path",
    "AffineShapeSystem",
    "CongruenceLiftSystem",
    "GaussianFamilySystem",
    "GraphDeformationSystem",
    "MatrixDeformationSystem",
    "QubitGateSystem",
    "SequenceTransformSystem",
    "path_graph",
    "triangle_seed",
    "weighted_partition_function",
]

__version__ = "1.1.0"
