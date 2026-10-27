"""Synthetic regression for the isolated Block17 extraction envelope correction.

Only this synthetic extraction task is compiled. No ARC corpus or query
solutions are opened, and the original source tree is never written.
"""
from __future__ import annotations

import argparse
import ast
import copy
import dataclasses
import difflib
import hashlib
import importlib.util
import io
import json
import sys
import time
import unittest
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
WORKSPACE = Path(__file__).resolve().parents[2]
ORIGINAL = WORKSPACE / "arc-fullbank/block17"
PATCHED = WORKSPACE / "arc-block17-limitfix/block17"
EVIDENCE = Path(__file__).resolve().parent
SHARED_ONLY = {"max_replay_calls", "max_replay_stages", "max_trace_bytes"}
EXPECTED_CHANGED = {"entrants13/extraction.py", "bank13.json"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def inventory(root, names=None):
    paths = sorted(root.rglob("*")) if names is None else [root / name for name in sorted(names)]
    return {
        str(p.relative_to(root)): {"sha256": sha(p), "size": p.stat().st_size,
                                  "mtime_ns": p.stat().st_mtime_ns}
        for p in paths if p.is_file()
    }


TASK = {
    "train": [
        {"input": [[0,0,0,0,0,0], [0,1,2,1,0,0], [0,3,1,2,0,0],
                   [0,0,0,0,0,0], [0,0,0,0,0,0]],
         "output": [[1,2,1], [3,1,2]]},
        {"input": [[0,0,0,0,0], [0,0,0,0,0], [0,0,4,5,0],
                   [0,0,5,6,0], [0,0,4,6,0], [0,0,0,0,0]],
         "output": [[4,5], [5,6], [4,6]]},
    ],
    "test": [{"input": [[0,0,0,0,0,0,0], [0,0,0,0,0,0,0],
                        [0,7,8,9,7,0,0], [0,9,7,8,9,0,0],
                        [0,0,0,0,0,0,0]]}],
}
# A synthetic assertion computed from the designed operation, never attached
# to TASK or passed to any compiler.
EXPECTED_SYNTHETIC_QUERY = [[7,8,9,7], [9,7,8,9]]


class InputOnlyQuery(Mapping):
    """Fail if the native sanitizer observes anything but the input field."""
    def __init__(self, grid):
        self.grid, self.accesses = grid, []

    def __getitem__(self, key):
        self.accesses.append(key)
        if key != "input":
            raise AssertionError("query field other than input observed")
        return self.grid

    def __iter__(self):
        raise AssertionError("query fields were enumerated")

    def __len__(self):
        raise AssertionError("query fields were counted")


class Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = module("limitfix_original_extraction", ORIGINAL / "entrants13/extraction.py")
        cls.contract = module("limitfix_contract", PATCHED / "contract.py")
        cls.limits = dict(cls.contract.DEFAULT_LIMITS)
        cls.entrant = cls.contract.load_entrants(
            PATCHED / "entrants13", {"extraction": sha(PATCHED / "entrants13/extraction.py")}
        )[0]
        cls.patched = cls.entrant.module
        cls.candidates, cls.receipt = cls.contract._compile_one(
            cls.entrant, copy.deepcopy(TASK), cls.limits
        )

    def test_original_rejects_current_envelope_before_search(self):
        with self.assertRaisesRegex(ValueError, "unknown extraction limit"):
            self.original._parse_limits(self.limits)
        for name in SHARED_ONLY:
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "unknown extraction limit"):
                    self.original._parse_limits({name: self.limits[name]})
        self.assertEqual(self.original.compile_task(copy.deepcopy(TASK), self.limits), [])

    def test_shared_envelope_preserves_default_local_capacities(self):
        old_defaults = dataclasses.asdict(self.original._Limits())
        self.assertEqual(dataclasses.asdict(self.patched._Limits()), old_defaults)
        self.assertEqual(dataclasses.asdict(self.patched._parse_limits(self.limits)), old_defaults)
        for name in SHARED_ONLY:
            with self.subTest(name=name):
                for value in (1, 10**12):
                    self.assertEqual(dataclasses.asdict(self.patched._parse_limits({name: value})), old_defaults)

    def test_known_local_overrides_and_candidate_alias_preserved(self):
        for settings in ({"max_programs": 7}, {"candidate_cap": 3},
                         {"candidate_cap": 3, "max_candidates": 2},
                         {"max_candidates": 4, "max_objects": 5, "max_total_candidates": 9}):
            with self.subTest(settings=settings):
                self.assertEqual(dataclasses.asdict(self.patched._parse_limits(settings)),
                                 dataclasses.asdict(self.original._parse_limits(settings)))

    def test_unknown_keys_and_invalid_types_still_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown extraction limit"):
            self.patched._parse_limits({**self.limits, "arbitrary_limit": 1})
        for key in self.limits:
            for value in (True, False, 0, -1, 1.5, "1", None, [], {}):
                with self.subTest(key=key, value=value):
                    settings = {**self.limits, key: value}
                    with self.assertRaisesRegex(ValueError, "positive integers"):
                        self.patched._parse_limits(settings)
        for value in ([], 3, "limits"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.patched._parse_limits(value)

    def test_production_admission_returns_expected_synthetic_behavior(self):
        self.assertEqual(self.receipt["status"], "ok")
        self.assertGreater(self.receipt["proposals"], 0)
        self.assertEqual(self.receipt["proposals"], self.receipt["retained_candidates"])
        self.assertEqual(self.receipt["behavior_count"], 1)
        self.assertEqual(self.receipt["program_replay"], "not_supplied")
        self.assertIsNone(self.entrant.replay_program)
        self.assertEqual({frozenset(example) for example in TASK["test"]}, {frozenset({"input"})})
        for candidate in self.candidates:
            self.assertEqual(candidate["test_outputs"], [EXPECTED_SYNTHETIC_QUERY])
            self.assertEqual(candidate["train_outputs"], [example["output"] for example in TASK["train"]])
            self.assertEqual(candidate["execution_replay"]["status"], "not_supplied")

    def test_program_serialization_replays_independently(self):
        for candidate in self.candidates:
            program = json.loads(json.dumps(candidate["program"]))
            for example in TASK["train"]:
                result = self.patched._execute(self.patched._grid(example["input"]), program, 64)
                self.assertEqual([list(row) for row in result], example["output"])
            result = self.patched._execute(self.patched._grid(TASK["test"][0]["input"]), program, 64)
            self.assertEqual([list(row) for row in result], EXPECTED_SYNTHETIC_QUERY)

    def test_original_compatible_settings_produce_identical_candidate_records(self):
        previous_envelope = {key: value for key, value in self.limits.items() if key not in SHARED_ONLY}
        original = self.original.compile_task(copy.deepcopy(TASK), previous_envelope)
        # Production admission only adds authenticated metadata. Compare the
        # native candidate payload against the independently executed original.
        fields = self.contract._REQUIRED_CANDIDATE_KEYS
        patched = [{key: candidate[key] for key in fields} for candidate in self.candidates]
        self.assertEqual(original, patched)

    def test_native_sanitizer_observes_only_query_input(self):
        query = InputOnlyQuery(TASK["test"][0]["input"])
        self.patched._sanitize({"train": TASK["train"], "test": [query]}, self.patched._Limits())
        self.assertEqual(query.accesses, ["input"])

    def test_parser_ast_delta_only_adds_three_shared_keys(self):
        before = ast.parse((ORIGINAL / "entrants13/extraction.py").read_text())
        after = ast.parse((PATCHED / "entrants13/extraction.py").read_text())
        removed = []
        for node in ast.walk(after):
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "compatibility" for t in node.targets):
                kept = []
                for item in node.value.elts:
                    if isinstance(item, ast.Constant) and item.value in SHARED_ONLY:
                        removed.append(item.value)
                    else:
                        kept.append(item)
                node.value.elts = kept
        self.assertEqual(set(removed), SHARED_ONLY)
        self.assertEqual(len(removed), 3)
        self.assertEqual(ast.dump(before, include_attributes=False), ast.dump(after, include_attributes=False))

    def test_all_registry_pins_and_load_hooks_remain_valid(self):
        vendor = json.loads((PATCHED / "vendor_manifest.json").read_text())
        for relative, expected in vendor.items():
            self.assertEqual(sha(PATCHED / relative), expected, relative)
        paths = [PATCHED / "vendor/core/src"] + sorted((PATCHED / "vendor").glob("block*/src"))
        paths += [PATCHED / "vendor/block2", PATCHED / "vendor/block4", PATCHED / "entrants13", PATCHED / "entrants"]
        for path in paths:
            sys.path.insert(0, str(path))
        bank13 = json.loads((PATCHED / "bank13.json").read_text())
        bank_new = json.loads((PATCHED / "bank14_15.json").read_text())
        old = self.contract.load_entrants(PATCHED / "entrants13", bank13)
        new = self.contract.load_entrants(PATCHED / "entrants", {name: value["sha256"] for name, value in bank_new.items()})
        self.assertEqual((len(old), len(new)), (21, 48))
        for entrant in old + new:
            self.assertTrue(callable(entrant.compile_task))
            self.assertTrue(entrant.replay_program is None or callable(entrant.replay_program))


def main():
    global ORIGINAL, PATCHED, EVIDENCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root", type=Path, default=ORIGINAL)
    parser.add_argument("--patched-root", type=Path, default=PATCHED)
    parser.add_argument("--baseline", type=Path, default=EVIDENCE / "original_source_identity.json")
    parser.add_argument("--output", type=Path, default=EVIDENCE / "extraction_limitfix_regression.json")
    args = parser.parse_args()
    ORIGINAL, PATCHED, EVIDENCE = args.original_root.resolve(), args.patched_root.resolve(), args.output.resolve().parent
    if ORIGINAL == PATCHED:
        parser.error("original and patched roots must be distinct")
    if args.output.exists():
        parser.error("output already exists; choose a new report path")
    for source_root in (ORIGINAL, PATCHED):
        if EVIDENCE == source_root or source_root in EVIDENCE.parents:
            parser.error("evidence output must be outside both source trees")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    original_before = inventory(ORIGINAL)
    baseline = json.loads(args.baseline.read_text())
    branch_before = inventory(PATCHED, baseline["files"])
    branch_extra = sorted(str(p.relative_to(PATCHED)) for p in PATCHED.rglob("*")
                          if p.is_file() and str(p.relative_to(PATCHED)) not in baseline["files"])
    # Captured old mtimes are meaningful only at the original workspace path.
    # Portable restores instead authenticate exact content against the supplied
    # archived baseline, then require identical inventory/size/mtime before/after.
    historical_mtimes_checked = False
    historical = WORKSPACE / "arc-evidence/later-source-audit/block17_source_before.json"
    if str(ORIGINAL) == baseline.get("source") and historical.is_file():
        prior = json.loads(historical.read_text())
        assert original_before == prior, "original source inventory/bytes/sizes/mtimes changed"
        historical_mtimes_checked = True
    assert {name: value["sha256"] for name, value in original_before.items()} == baseline["files"]
    assert set(branch_before) == set(original_before)
    changed = sorted(name for name in branch_before if branch_before[name]["sha256"] != original_before[name]["sha256"])
    assert set(changed) == EXPECTED_CHANGED, changed
    old_bank = json.loads((ORIGINAL / "bank13.json").read_text())
    new_bank = json.loads((PATCHED / "bank13.json").read_text())
    assert set(old_bank) == set(new_bank)
    assert [name for name in old_bank if old_bank[name] != new_bank[name]] == ["extraction"]
    assert new_bank["extraction"] == sha(PATCHED / "entrants13/extraction.py")
    stream = io.StringIO()
    compile_start = time.monotonic()
    outcome = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Regression))
    test_seconds = time.monotonic() - compile_start
    original_after = inventory(ORIGINAL)
    branch_after = inventory(PATCHED, baseline["files"])
    assert original_before == original_after, "original source changed during tests"
    assert branch_before == branch_after, "branch source changed during tests"
    diff = "".join("".join(difflib.unified_diff((ORIGINAL / name).read_text().splitlines(True),
                                            (PATCHED / name).read_text().splitlines(True),
                                            fromfile="original/" + name, tofile="limitfix/" + name))
                   for name in changed)
    (EVIDENCE / "extraction_limitfix.patch").write_text(diff)
    (EVIDENCE / "extraction_limitfix_tests.log").write_text(stream.getvalue())
    body = {
        "schema": "block17.extraction_limitfix.synthetic_regression.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "success": outcome.wasSuccessful(), "tests_run": outcome.testsRun,
        "failures": len(outcome.failures), "errors": len(outcome.errors),
        "test_seconds": test_seconds, "total_seconds_including_source_authentication": time.monotonic() - start,
        "test_script_sha256": sha(Path(__file__)),
        "original_root": str(ORIGINAL), "patched_root": str(PATCHED),
        "baseline": {"path": str(args.baseline.resolve()), "sha256": sha(args.baseline)},
        "original_source_files": len(original_before), "original_source_unchanged_bytes_sizes_mtimes_inventory": True,
        "historical_original_mtimes_checked": historical_mtimes_checked,
        "branch_source_unchanged_during_tests": True, "changed_files": {
            name: {"original": original_before[name], "patched": branch_after[name]} for name in changed
        },
        "branch_unpinned_extra_paths_excluded_from_source_and_installer": branch_extra,
        "branch_unpinned_extra_file_contents_opened": False,
        "registry_delta": {"extraction": {"original": old_bank["extraction"], "patched": new_bank["extraction"]}},
        "shared_keys_accepted_without_local_budget_effect": sorted(SHARED_ONLY),
        "original_local_default_capacities": dataclasses.asdict(Regression.original._Limits()),
        "patched_local_default_capacities": dataclasses.asdict(Regression.patched._Limits()),
        "production_contract_receipt": Regression.receipt,
        "production_candidate_count": len(Regression.candidates),
        "production_replay_hook": None, "production_replay_status": "not_supplied",
        "serialized_program_independent_synthetic_replay": outcome.wasSuccessful(),
        "all69_registry_pins_and_callable_compile_hooks_checked": outcome.wasSuccessful(),
        "synthetic_task": TASK, "synthetic_query_assertion_never_passed_to_compiler": EXPECTED_SYNTHETIC_QUERY,
        "production_candidates": Regression.candidates,
        "no_arc_corpus_or_query_solution_files_opened": True,
        "no_full_engine_compilations": True,
        "interpretation": "Separate source version. Synthetic regression only; no score or accuracy claim.",
        "test_log": stream.getvalue(),
    }
    body["content_hash"] = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    report = args.output.resolve()
    report.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"success": body["success"], "tests_run": outcome.testsRun,
                      "failures": len(outcome.failures), "errors": len(outcome.errors),
                      "test_seconds": test_seconds, "receipt": Regression.receipt,
                      "report": str(report), "report_sha256": sha(report)}))
    raise SystemExit(0 if outcome.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
