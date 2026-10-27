"""Komorebi PR-LASM Bidirectional Relational Program Compiler."""
from .compiler import compile_programs, compile_record, execute_candidates, route_task
from .execution import execute_compiled, execute_spec
from .ir_bridge import compiler_registry, execute_via_ir, to_ir_program
from .model import CandidateExecution, CompilationTrace, CompiledProgram, RouteSignature

__version__ = "0.2.0"

__all__ = [
    "CandidateExecution", "CompilationTrace", "CompiledProgram", "RouteSignature",
    "compile_programs", "compile_record", "compiler_registry",
    "execute_candidates", "execute_compiled", "execute_spec", "execute_via_ir",
    "route_task", "to_ir_program",
]
