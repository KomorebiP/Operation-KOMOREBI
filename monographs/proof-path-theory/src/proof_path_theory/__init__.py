from .views import ProofFieldViews, RuleConstraint
from .ambient import FiniteViewSystem, Restriction
from .realization import (
    AffineRealizationReport,
    analyze_affine_realizations,
    check_obstruction_witness,
)
from .audit import (
    AuditQueueResult,
    AuditRegime,
    audit_priority,
    constant_rate_regime,
    simulate_audit_queue,
)
from .bridges import (
    BridgeGraph,
    RetentionResult,
    exact_cardinality_retention,
    greedy_cardinality_retention,
    greedy_cost_retention,
    is_monotone_submodular_coverage,
)
from .certificate import (
    AlternativeJustificationError,
    Certificate,
    CertificateReport,
    certificate_cost,
    is_and_dag,
    minimum_certificate,
    unique_and_dag_certificate,
    validate_certificate,
)
from .compression import (
    CompressionReport,
    GoalWeights,
    Representation,
    RepresentationProfile,
    TaskRequirement,
    compression_debt,
    compression_report,
    pareto_front,
    recoverability_equivalent,
    recoverability_preorder,
    retention_join,
    retention_meet,
    retention_projection,
    representation_utility,
    select_representation,
    task_signature,
    task_sufficient,
)
from .io import (
    bundled_schema,
    certificate_from_dict,
    certificate_to_dict,
    load_certificate,
    load_proof_field,
    proof_field_from_dict,
    proof_field_to_dict,
    save_certificate,
    save_proof_field,
)
from .model import (
    ClaimNode,
    CostVector,
    EvidenceKind,
    EvidenceRecord,
    Justification,
    NodeKind,
    ProofField,
    ValueVector,
)
from .refinement import (
    RefinementDecision,
    optimal_depth,
    refinement_decision,
    stopping_depth,
)
from .review import (
    effective_reviewer_count,
    equal_weight_variance,
    equicorrelated_covariance,
    equicorrelated_effective_count,
    generalized_least_squares_weights,
    shared_bias_mse,
    weighted_estimator_variance,
)
from .versioning import (
    ClaimRevision,
    LedgerSnapshot,
    affected_descendants,
    append_only_derivability_preserved,
    provenance_digest,
)

from .recovery import (
    DecoderCertificate, CollisionWitness, FactorizationResult,
    factor_task, verify_factorization, compose_decoders, joint_task_scheme,
)
from .extension import (
    DerivationWitness, ExtensionResult, solve_extension, extend_partial,
    verify_derivation, verify_extension_obstruction, verify_extension_result,
)

__all__ = [name for name in globals() if not name.startswith("_")]
__version__ = "1.6.0"

from .semantic_cover import (
    RuleEntailment, SemanticCoverResult, analyze_semantic_cover,
    verify_semantic_cover, glue_semantic,
)
__all__ += ["RuleEntailment", "SemanticCoverResult", "analyze_semantic_cover", "verify_semantic_cover", "glue_semantic"]

from .trace_codec import (
    IndexedRule, IndexedProblem, IndexedWitness, IndexedCertificate, IndexedBinding,
    WireFormatError, WireResourceError, dumps_problem, loads_problem,
    dumps_trace_certificate, loads_trace_certificate, check_trace_json,
    check_indexed_certificate, check_indexed_witness, index_problem,
    index_certificate, export_trace_exchange,
)
__all__ += ["IndexedRule", "IndexedProblem", "IndexedWitness", "IndexedCertificate", "IndexedBinding",
    "WireFormatError", "WireResourceError", "dumps_problem", "loads_problem",
    "dumps_trace_certificate", "loads_trace_certificate", "check_trace_json",
    "check_indexed_certificate", "check_indexed_witness", "index_problem",
    "index_certificate", "export_trace_exchange"]
