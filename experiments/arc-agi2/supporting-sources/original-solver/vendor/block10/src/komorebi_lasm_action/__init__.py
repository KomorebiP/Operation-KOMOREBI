"""PR-LASM Block 10: action-congruent capsules and typed tool synthesis.

Author: Komorebi P.
"""
from __future__ import annotations

from . import temporal
from .algebra import (
    ActionAtom,
    ProgramWord,
    RelationCertificate,
    RelationRegistry,
    TrustTier,
    normalize_program_word,
)
from .capsule import (
    audit_action_congruence,
    coarsest_action_congruent_partition,
    oracle_refinement_gap,
    refine_capsule_from_collisions,
)
from .gauge import (
    GaugeOrbit,
    GaugeTransport,
    GridGauge,
    canonical_gauge_orbit,
    transport_mechanism,
)
from .model import (
    ActionContract,
    ActionReceipt,
    AmbientPacket,
    CapsuleSnapshot,
    CongruenceAudit,
    LeakageWitness,
    PredictiveCapsule,
    RefinementProposal,
    RuntimeCoordinates,
    StaticTransitionState,
    TargetAwareSynthesisContext,
)
from .persistence import load_snapshot, save_snapshot, snapshot_roundtrip
from .routing import compile_routed_programs, execute_routed_program
from .targeted import compile_targeted_tools, compile_targeted_tools_traced
from .tools import (
    ToolProgram,
    ToolSynthesisLimits,
    synthesize_complete_scene_native_tools,
    synthesize_tools,
)

__version__ = "0.6.0"

__all__ = [
    "ActionAtom",
    "ActionContract",
    "ActionReceipt",
    "AmbientPacket",
    "CapsuleSnapshot",
    "CongruenceAudit",
    "GaugeOrbit",
    "GaugeTransport",
    "GridGauge",
    "LeakageWitness",
    "PredictiveCapsule",
    "ProgramWord",
    "RefinementProposal",
    "RelationCertificate",
    "RelationRegistry",
    "RuntimeCoordinates",
    "StaticTransitionState",
    "TargetAwareSynthesisContext",
    "ToolProgram",
    "ToolSynthesisLimits",
    "TrustTier",
    "audit_action_congruence",
    "canonical_gauge_orbit",
    "coarsest_action_congruent_partition",
    "compile_routed_programs",
    "compile_targeted_tools",
    "compile_targeted_tools_traced",
    "execute_routed_program",
    "load_snapshot",
    "normalize_program_word",
    "oracle_refinement_gap",
    "refine_capsule_from_collisions",
    "save_snapshot",
    "snapshot_roundtrip",
    "synthesize_complete_scene_native_tools",
    "synthesize_tools",
    "temporal",
    "transport_mechanism",
]
