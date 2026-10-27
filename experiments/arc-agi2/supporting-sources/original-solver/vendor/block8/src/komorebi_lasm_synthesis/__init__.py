"""PR-LASM Obstruction-Guided Macro Synthesis."""
from __future__ import annotations

from importlib.resources import files
import json

from .bank import build_schema_evidence, permitted_schemas
from .compiler import compile_programs, compile_record, execute_candidates
from .families import DEFINITIONS, DEFINITION_BY_NAME, SCHEMA_FAMILIES, execute_family, family_sketches
from .ir_bridge import execute_via_ir, synthesis_registry, to_ir_program
from .model import (
    CandidateExecution, HoleSpec, MacroSchemaEvidence, MacroSketch, MacroStatus,
    ObstructionKind, ObstructionPacket, SynthesizedProgram, SynthesisTrace,
)
from .obstruction import derive_obstruction_packet

__version__ = "0.4.0"


def load_runtime_macro_bank() -> dict:
    path = files("komorebi_lasm_synthesis").joinpath("data/runtime_macro_bank.json")
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "CandidateExecution", "DEFINITIONS", "DEFINITION_BY_NAME", "HoleSpec",
    "MacroSchemaEvidence", "MacroSketch", "MacroStatus", "ObstructionKind",
    "ObstructionPacket", "SCHEMA_FAMILIES", "SynthesizedProgram", "SynthesisTrace",
    "build_schema_evidence", "compile_programs", "compile_record",
    "derive_obstruction_packet", "execute_candidates", "execute_family",
    "execute_via_ir", "family_sketches", "load_runtime_macro_bank",
    "permitted_schemas", "synthesis_registry", "to_ir_program",
]
