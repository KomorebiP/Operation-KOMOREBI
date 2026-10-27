"""Small public API over the separately audited exact engines.

Returned certificates are finite data. Call verify against the original input
before using an externally supplied certificate. No API in this file produces
KERNEL_CHECKED status: the separate Lean workflow performs that verification.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from copy import deepcopy
from repair_certificates import Mat, InvalidData, canonical, digest, read_json, require, MAX_BYTES
import repair_certificates as Free
import rational_menu as Menu
import branch_menu as Branch

@dataclass(frozen=True)
class Outcome:
    status: str
    mode: str | None = None
    problem_sha256: str | None = None
    certificate: dict[str, Any] | None = None
    checks: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)
    trace: tuple[str, ...] = ()
    error_code: str | None = None
    error: str | None = None

    @property
    def kernel_checked(self) -> bool:
        return False

    def to_dict(self, *, include_certificate: bool = True) -> dict[str, Any]:
        obj = {'status': self.status, 'mode': self.mode,
               'problem_sha256': self.problem_sha256, 'kernel_checked': False,
               'checks': deepcopy(self.checks), 'statistics': deepcopy(self.statistics),
               'error_code': self.error_code, 'error': self.error}
        if include_certificate:
            obj['certificate'] = deepcopy(self.certificate)
        return obj

def _engine(problem: Any):
    require(type(problem) is dict, 'Problem must be a JSON object')
    engines = {Free.SCHEMA: Free, Menu.SCHEMA: Menu, Branch.SCHEMA: Branch}
    schema = problem.get('schema')
    require(type(schema) is str and schema in engines, 'Unsupported problem schema')
    engine = engines[schema]
    engine.parse_problem(problem)
    return engine

def _snapshot(obj: Any) -> Any:
    # The original data are copied: producers cannot mutate caller-owned input.
    copied = deepcopy(obj)
    require(len(canonical(copied)) <= MAX_BYTES, 'JSON size resource limit')
    return copied

def _failure(exc: Exception, *, certificate: bool, mode: str | None,
             identity: str | None, trace: list[str], stats: dict[str, Any]) -> Outcome:
    if isinstance(exc, Menu.ResourceLimit) or 'resource limit' in str(exc).lower():
        code = 'RESOURCE_LIMIT'
    elif isinstance(exc, (RecursionError, MemoryError)):
        code = 'RESOURCE_LIMIT'
    else:
        code = 'INVALID_CERTIFICATE' if certificate else 'INVALID_INPUT_OR_GENERATED_CERTIFICATE'
    return Outcome('UNRESOLVED', mode=mode, problem_sha256=identity,
                   statistics=deepcopy(stats), trace=tuple(trace), error_code=code,
                   error=str(exc))

def load(path: str | Path) -> dict[str, Any]:
    """Load a bounded, strictly parsed problem; malformed input raises InvalidData."""
    obj = read_json(Path(path))
    _engine(obj)
    return obj

def free_problem(D: Mat, R: Mat) -> dict[str, Any]:
    """Create and validate the original free-repair problem using exact matrices."""
    obj = Free.problem(D, R)
    Free.parse_problem(obj)
    return obj

def menu_problem(D: Mat, E: Mat, R: Mat, costs: list[int],
                 admissible_masks: list[int] | None = None) -> dict[str, Any]:
    """Create a branch problem. None admits all subsets; [] admits none."""
    return Branch.problem(D, E, R, list(costs),
                          None if admissible_masks is None else list(admissible_masks))

def solve(problem: dict[str, Any], *, max_nodes: int = Branch.MAX_NODES,
          max_linear_trials: int = Branch.MAX_NODES,
          max_menu_trials: int = 256) -> Outcome:
    """Construct and recheck exact witnesses, never claiming Lean acceptance.

    Node and linear budgets apply to branch problems. max_menu_trials applies
    to legacy exhaustive menus. Free matrix repair is bounded by wire limits.
    Limits are work counters, not wall-clock or memory-sandbox guarantees.
    """
    trace: list[str] = []
    stats: dict[str, Any] = {}
    identity = mode = None
    try:
        p = _snapshot(problem)
        engine = _engine(p)
        mode, identity = p['kind'], digest(p)
        for value, cap in ((max_nodes, Branch.MAX_NODES),
                           (max_linear_trials, Branch.MAX_NODES),
                           (max_menu_trials, 256)):
            require(type(value) is int and 0 <= value <= cap, 'Invalid bounded work budget')
        if engine is Branch:
            cert = engine.construct(p, trace, max_nodes=max_nodes,
                                    max_linear_trials=max_linear_trials, stats=stats)
        elif engine is Menu:
            cert = engine.construct(p, trace, max_trials=max_menu_trials)
        else:
            cert = engine.construct(p, trace)
        _snapshot(cert)  # An output must satisfy the same serialization-size ceiling.
        checked = engine.check_certificate(p, cert)
        return Outcome('PYTHON_CERTIFICATE_VALID', mode, identity, deepcopy(cert),
                       deepcopy(checked), deepcopy(stats), tuple(trace))
    except (InvalidData, ValueError, TypeError, ArithmeticError, RecursionError, MemoryError) as exc:
        return _failure(exc, certificate=False, mode=mode, identity=identity,
                        trace=trace, stats=stats)

def verify(problem: dict[str, Any], certificate: dict[str, Any]) -> Outcome:
    """Recheck a supplied certificate against a copied, fixed original problem."""
    identity = mode = None
    try:
        p, cert = _snapshot(problem), _snapshot(certificate)
        engine = _engine(p)
        mode, identity = p['kind'], digest(p)
        checked = engine.check_certificate(p, cert)
        return Outcome('PYTHON_CERTIFICATE_VALID', mode, identity, cert, deepcopy(checked))
    except (InvalidData, ValueError, TypeError, ArithmeticError, RecursionError, MemoryError) as exc:
        return _failure(exc, certificate=True, mode=mode, identity=identity,
                        trace=[], stats={})
