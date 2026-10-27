"""Label-free runtime interface for the promoted grammar bank."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from importlib import resources
from typing import Any, Mapping, Sequence
import json

from komorebi_lasm_compiler.model import sha256_record

from .discovery import (
    broad_candidates,
    candidate_family,
    candidate_outputs,
    candidate_parameters,
    candidate_signature,
    scrub_test_outputs,
)
from .model import MacroBank


@dataclass(frozen=True)
class MacroDecision:
    committed: bool
    reason: str
    outputs: tuple[tuple[tuple[int, ...], ...], ...] = ()
    signatures: tuple[str, ...] = ()
    macro_ids: tuple[str, ...] = ()
    output_hash: str = ""

    def to_record(self) -> dict[str, Any]:
        return {
            "committed": bool(self.committed),
            "reason": self.reason,
            "outputs": [[list(row) for row in grid] for grid in self.outputs],
            "signatures": list(self.signatures),
            "macro_ids": list(self.macro_ids),
            "output_hash": self.output_hash,
        }


class PersistentGrammarCompiler:
    """Activate stable grammar macros using task demonstrations only."""

    def __init__(self, bank: MacroBank) -> None:
        self.bank = bank

    @classmethod
    def from_json(cls, path: str | Path) -> "PersistentGrammarCompiler":
        record = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(MacroBank.from_runtime_record(record))

    @classmethod
    def default(cls) -> "PersistentGrammarCompiler":
        resource = resources.files("komorebi_lasm_grammar").joinpath("data/runtime_macro_bank.json")
        record = json.loads(resource.read_text(encoding="utf-8"))
        return cls(MacroBank.from_runtime_record(record))

    def compile(self, task: Mapping[str, Any]) -> MacroDecision:
        # Remove any attached test labels before candidate construction.
        clean = scrub_test_outputs(task)
        candidates = broad_candidates(clean, bank=self.bank)
        by_output: dict[Any, list[Mapping[str, Any]]] = {}
        for candidate in candidates:
            by_output.setdefault(candidate_outputs(candidate), []).append(candidate)
        if not by_output:
            return MacroDecision(False, "no_stable_macro_candidate")
        if len(by_output) != 1:
            return MacroDecision(False, "ambiguous_stable_macro_behaviors")
        output, matching = next(iter(by_output.items()))
        macro_ids = sorted({
            macro.macro_id
            for candidate in matching
            for macro in self.bank.matching(candidate_family(candidate), candidate_parameters(candidate))
        })
        return MacroDecision(
            committed=True,
            reason="unique_stable_macro_behavior",
            outputs=output,
            signatures=tuple(sorted({candidate_signature(candidate) for candidate in matching})),
            macro_ids=tuple(macro_ids),
            output_hash=sha256_record(output),
        )


__all__ = ["MacroDecision", "PersistentGrammarCompiler"]
