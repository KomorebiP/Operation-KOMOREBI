"""Explicit import-only profiles for bounded retained-source browser workspaces.

Profiles do not certify the original full import environment. Proof source stays
unchanged, and missing declarations or tactics must remain Lean errors.
"""
import hashlib
from pathlib import Path

from lean_runner import imports

PAPER_I_PATH = 'papers/paper-i/current/formal/current/KomorebiVerification/MathlibImports.lean'
PAPER_I_SHA = '5c933dc53d733ab61856a33f777a16d0ac9384d97a2a8779856dfe77fb569bda'
PAPER_I_PROFILE_SHA = '3365b100ca6c7f29d73528323c43ef304271616825cb0860ef58e242f6167791'
PAPER_I_MODULE = 'KomorebiVerification.MathlibImports'
PAPER_I_IMPORTS = (
    'Mathlib.LinearAlgebra.TensorProduct.Tower', 'Mathlib.LinearAlgebra.Matrix.ToLin',
    'Mathlib.Tactic.Ring', 'Mathlib.Tactic.Linarith', 'Mathlib.Tactic.NormNum',
    'Mathlib.Tactic.FinCases', 'Mathlib.Tactic.FieldSimp', 'Mathlib.Tactic.Module',
    'Mathlib.Tactic.Nontriviality', 'Mathlib.Tactic.Push', 'Mathlib.Tactic.Abel',
    'Mathlib.Tactic.FunProp', 'Mathlib.Tactic.Convert', 'Mathlib.Tactic.Finiteness',
    'Mathlib.Tactic.Tauto', 'Mathlib.LinearAlgebra.Projection',
    'Mathlib.Analysis.SpecialFunctions.Complex.Log',
)
PAPER_I_SOURCE = ('-- Browser import profile for the original Paper I proof text.\n'
    '-- This is an import subset, not the retained complete MathlibImports module.\n'
    '-- No mathematical declarations or assumptions are added.\n' +
    ''.join('import ' + module + '\n' for module in PAPER_I_IMPORTS))
PROFILE_WORKSPACES = frozenset({'paper-i-basic', 'paper-i-projector-core'})
PROFILE_ASSET = 'lean/browser/import-profiles/paper-i-core.lean'


def uses_profile(workspace):
    return workspace in PROFILE_WORKSPACES


def profile_definition():
    if hashlib.sha256(PAPER_I_SOURCE.encode()).hexdigest() != PAPER_I_PROFILE_SHA:
        raise ValueError('Paper I browser profile changed; repeat browser qualification')
    return dict(id='paper-i-core', module=PAPER_I_MODULE,
        source=PAPER_I_SOURCE, sha256=PAPER_I_PROFILE_SHA,
        original_path=PAPER_I_PATH, original_sha256=PAPER_I_SHA)


def checked_original(raw):
    if hashlib.sha256(raw).hexdigest() != PAPER_I_SHA:
        raise ValueError('Paper I browser profile requires the exact retained import-only source')
    return raw


def validate_profile(root, available, members=None):
    """Bind the profile to original bytes, available artifacts and pinned ancestry."""
    raw = checked_original((Path(root) / PAPER_I_PATH).read_bytes())
    missing = set(PAPER_I_IMPORTS) - set(available)
    if missing:
        raise ValueError('Paper I browser profile imports unavailable modules: ' + ', '.join(sorted(missing)))
    if members is not None:
        reachable = set()
        def visit(module):
            if module in reachable:
                return
            reachable.add(module)
            path = module.replace('.', '/') + '.lean'
            if path in members:
                for dependency in imports(members[path].decode('utf8')):
                    visit(dependency)
        for module in imports(raw.decode('utf8')):
            visit(module)
        if not set(PAPER_I_IMPORTS) <= reachable:
            raise ValueError('Paper I browser profile escaped the original pinned import ancestry')
    return profile_definition()
