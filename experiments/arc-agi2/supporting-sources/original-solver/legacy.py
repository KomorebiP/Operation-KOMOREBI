"""Live integration of the inherited solver and Blocks 5–13.

Author: Komorebi P.
"""
from __future__ import annotations
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for p in [ROOT / "vendor/core/src"] + sorted((ROOT / "vendor").glob("block*/src")) + [ROOT / "vendor/block2", ROOT / "vendor/block4", ROOT / "entrants13"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import contract


def verify_sources():
    manifest = json.loads((ROOT / "vendor_manifest.json").read_text())
    for path, expected in manifest.items():
        if contract.sha256_file(ROOT / path) != expected:
            raise ValueError(f"inherited source changed: {path}")


def plain(value):
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, (tuple, list)):
        return [plain(x) for x in value]
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if hasattr(value, "item"):
        return value.item()
    return value


def normalized(source, block, family, program, outputs, task, complexity=10, verification="native_compiler_demo_fit"):
    outputs = [contract.validate_grid(plain(x)) for x in outputs]
    if len(outputs) != len(task["test"]):
        raise ValueError("legacy output arity mismatch")
    body = {"entrant": source, "source_block": block, "family": str(family),
            "program": plain(program), "test_outputs": outputs,
            "complexity": max(0, int(complexity)), "verification": verification,
            "behavior_hash": contract.digest(outputs), "task_semantic_hash": contract.digest(task)}
    body["candidate_hash"] = contract.digest(body)
    return body


def compile_old(task, *, include_base=True):
    """All inputs are sanitized by the caller; real task IDs never enter here."""
    from block4_solver import solve_task
    from komorebi_lasm_compiler.compiler import compile_record as compile6
    from komorebi_lasm_grammar.discovery import broad_candidates
    from komorebi_lasm_grammar.runtime import PersistentGrammarCompiler
    from komorebi_lasm_synthesis.compiler import compile_record as compile8
    from komorebi_lasm_composition.compiler import compile_record as compile9
    from komorebi_lasm_transfer.compiler import compile_transfer_task
    from komorebi_lasm_falsification.compiler import compile_falsification_task
    from action_adapter import compile_action_record

    candidates, receipts = [], {}
    base = None
    if include_base:
        try:
            base, diagnostic = solve_task(copy.deepcopy(task), time_limit=2.0)
            base = contract._validate_submission_task({"runtime": base}, "runtime", len(task["test"]))
            receipts["core_blocks2_4"] = {"status": "ok", "time_tier": 2.0,
                "note": "deterministic operation tier, not a wall-clock cutoff"}
        except Exception as error:
            receipts["core_blocks2_4"] = {"status": "error", "error": f"{type(error).__name__}: {error}"}
            base = [{"attempt_1": x["input"], "attempt_2": x["input"]} for x in task["test"]]

    def run(name, block, call, grouped=False):
        try:
            record = call()
            if isinstance(record, list):
                record = {"candidates": record}
            raw = record.get("candidates", [])
            if record.get("error") or record.get("selection_complete") is False:
                receipts[name] = {"status": "incomplete", "error": record.get("error"), "candidates": 0}
                return record
            count = 0
            accepted = []
            for row in raw:
                if grouped:
                    for mechanism in row["mechanisms"]:
                        program = mechanism.get("representative_program", mechanism.get("program", mechanism))
                        family = mechanism.get("mechanism_key", mechanism.get("schema_keys", mechanism.get("lane", name)))
                        family = ",".join(family) if isinstance(family, list) else family
                        accepted.append(normalized(name, block, family, program, row["test_predictions"], task,
                            program.get("cost", program.get("description_length", 10)) if isinstance(program, dict) else 10))
                        count += 1
                else:
                    program = row["program"]
                    outputs = row.get("outputs", row.get("test_outputs"))
                    if "training_outputs" in row and row["training_outputs"] != [x["output"] for x in task["train"]]:
                        raise ValueError("native replay did not fit demonstrations")
                    accepted.append(normalized(name, block, program.get("family", name), program, outputs, task,
                                                  program.get("cost", program.get("total_cost", 10))))
                    count += 1
            candidates.extend(accepted)
            receipts[name] = {"status": "ok", "candidates": count}
            return record
        except Exception as error:
            receipts[name] = {"status": "error", "error": f"{type(error).__name__}: {error}"}
            return {"error": str(error), "candidates": []}

    run("legacy_block6", 6, lambda: compile6(copy.deepcopy(task)))
    run("legacy_block7", 7, lambda: broad_candidates(copy.deepcopy(task), bank=PersistentGrammarCompiler.default().bank))
    run("legacy_block8", 8, lambda: compile8(copy.deepcopy(task)))
    block6_bank = json.loads((ROOT / "vendor/block7/src/komorebi_lasm_grammar/data/runtime_macro_bank.json").read_text())
    block8_bank = json.loads((ROOT / "vendor/block8/src/komorebi_lasm_synthesis/data/runtime_macro_bank.json").read_text())
    block9 = run("legacy_block9", 9, lambda: compile9(copy.deepcopy(task),
        block6_bank_record=block6_bank, block8_bank_record=block8_bank))
    block10 = run("legacy_block10", 10, lambda: compile_action_record("runtime", copy.deepcopy(task), block9), True)
    run("legacy_block11", 11, lambda: compile_transfer_task("runtime", copy.deepcopy(task), block10,
        allow_provisional_action=True, allow_provisional_shape=True, allow_provisional_residual=True,
        allow_provisional_ambient=True), True)
    run("legacy_block12", 12, lambda: compile_falsification_task("runtime", copy.deepcopy(task),
        allow_provisional_ambient=True, allow_provisional_shape=True, allow_provisional_singletons=True), True)
    return candidates, base, receipts
