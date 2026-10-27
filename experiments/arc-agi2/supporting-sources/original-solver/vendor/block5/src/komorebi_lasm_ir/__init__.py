"""Komorebi PR-LASM typed relational Program IR v2."""

from .arc_scene import (
    AmbientFace, ArcObject, ArcRuntimeAdapter, Box, Canvas, Cell, Edit, Layout,
    Relation, Scene, analyze_grid, freeze_grid, infer_background,
    standard_arc_registry,
)
from .behavior import BehaviorQuotient, BehaviorSignature, program_behavior_signature
from .delta import (
    AmbiguousCorrespondence, DeltaGraph, DeltaPattern, ObjectCorrespondence,
    anti_unify_delta_graphs, derive_delta_graph, derive_task_delta_pattern,
)
from .migration import migrate_v1_ast, registry_from_v1_definitions
from .interpreter import (
    AmbiguityError, ExecutionError, ExecutionLimitError, ExecutionLimits,
    ExecutionResult, ExecutionTrace, Interpreter, NonConvergenceError,
)
from .nodes import (
    AllNode, AnyNode, ArgExtremeNode, CallNode, CartesianMapNode, CaseBranch,
    CaseNode, CountNode, FilterNode, FoldNode, HoleNode, IfNode, InputNode,
    LetNode, LiteralNode, MapNode, PackNode, RenderNode, RepeatUntilStableNode,
    SelectNode, SortNode, TileNode, VariableNode,
)
from .program import (
    IR_SCHEMA, IR_SCHEMA_VERSION, InputSpec, Program, ProgramMetrics,
    ProgramValidationError, StaticLimits,
)
from .registry import OperatorDefinition, OperatorRegistry
from .sketch import ProgramSketch, anti_unify_programs
from .types import ValueType

__version__ = "0.1.0"

__all__ = [
    "AllNode", "AmbientFace", "AmbiguityError", "AmbiguousCorrespondence",
    "AnyNode", "ArcObject",
    "ArcRuntimeAdapter", "ArgExtremeNode", "BehaviorQuotient", "BehaviorSignature", "Box",
    "CallNode", "Canvas", "CartesianMapNode", "CaseBranch", "CaseNode",
    "Cell", "CountNode", "DeltaGraph", "DeltaPattern", "Edit",
    "ExecutionError",
    "ExecutionLimitError", "ExecutionLimits", "ExecutionResult", "ExecutionTrace",
    "FilterNode", "FoldNode", "HoleNode", "IR_SCHEMA", "IR_SCHEMA_VERSION", "IfNode",
    "InputNode", "InputSpec", "Interpreter", "Layout", "LetNode",
    "LiteralNode", "MapNode", "NonConvergenceError", "OperatorDefinition",
    "ObjectCorrespondence", "OperatorRegistry", "PackNode", "Program", "ProgramMetrics",
    "ProgramSketch", "ProgramValidationError", "Relation", "RenderNode",
    "RepeatUntilStableNode", "Scene", "SelectNode", "SortNode", "StaticLimits", "TileNode",
    "ValueType", "VariableNode", "analyze_grid", "anti_unify_delta_graphs",
    "anti_unify_programs",
    "derive_delta_graph", "derive_task_delta_pattern", "freeze_grid",
    "infer_background", "migrate_v1_ast", "program_behavior_signature",
    "registry_from_v1_definitions", "standard_arc_registry",
]
