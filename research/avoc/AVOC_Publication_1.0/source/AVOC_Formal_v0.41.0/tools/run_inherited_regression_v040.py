#!/usr/bin/env python3
"""Rerun unchanged predecessor regressions with evidence and fixture relocation.

Only evidence destinations and selected fixture filesystem paths are relocated.
The original check and runtime sources remain unchanged. Transformations and
source hashes are recorded for reproduction.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, sys, types, uuid

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "results/v0.40.0"
CASES = {
    "oracle": "test_robust_quote.py",
    "workflow": "test_robust_quote_workflow.py",
    "recovery": "test_robust_quote_recovery.py",
    "lazy": "test_lazy_staged_workflow.py",
    "calibration": "test_calibration.py",
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=[*CASES, "all"], default="all")
    args = parser.parse_args()
    run_name = datetime.datetime.now(datetime.timezone.utc).strftime("run_%Y%m%dT%H%M%S_") + uuid.uuid4().hex[:12]
    out = EVIDENCE / "inherited_replays" / run_name
    out.mkdir(parents=True, exist_ok=False)
    relative_out = out.relative_to(ROOT).as_posix()
    fixtures = out / "fixtures"
    fixtures.mkdir(exist_ok=True)
    for name, key in (("workflow_warm", "warm_artifact"), ("workflow_cold", "cold_artifact")):
        value = json.loads((ROOT / "examples/robust_quote" / (name + ".json")).read_text())
        value[key] = str(ROOT / "examples/robust_quote" / Path(value[key]).name)
        (fixtures / (name + ".json")).write_text(json.dumps(value, indent=2) + "\n")
    selected = list(CASES) if args.case == "all" else [args.case]
    behavior_sources = [ROOT / "tools" / name for name in ("run_inherited_regression_v040.py", "calibrate_quote.py", "run_calibration_lean.py", "robust_quote_workflow.py", "run_robust_quote.py", "lazy_staged_workflow.py", "run_lazy_staged.py", "artifact_gate.py")]
    behavior_sources += [ROOT / "checks" / name for name in CASES.values()]
    behavior_sources += list((ROOT / "AVOC").glob("*.lean"))
    behavior_sources = [p for p in behavior_sources if p.name not in {"Audit.lean", "FullAudit.lean"}]
    source_hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in behavior_sources}
    summary = {"run_directory": relative_out, "selected_cases": selected, "source_sha256": source_hashes,
               "all_passed": False, "cases": []}
    for case in selected:
        source = ROOT / "checks" / CASES[case]
        original = source.read_text()
        adapted = original.replace("results/v0.38.0/", relative_out + "/")
        adapted = adapted.replace("results/v0.39.0/", relative_out + "/")
        adapted = adapted.replace("results/v0.37.0/runtime/final", relative_out + "/lazy_staged")
        for name in ("workflow_warm", "workflow_cold"):
            adapted = adapted.replace("ROOT/'examples/robust_quote/" + name + ".json'",
                                      "ROOT/'" + relative_out + "/fixtures/" + name + ".json'")
        module = types.ModuleType("inherited_" + case)
        module.__file__ = str(source)
        ns = vars(module)
        sys.modules[module.__name__] = module
        record = {
            "case": case,
            "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source": str(source.relative_to(ROOT)),
            "source_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "adapted_source_sha256": hashlib.sha256(adapted.encode()).hexdigest(),
            "changes": "Relocate evidence outputs and selected fixture paths only.",
        }
        prior_argv = sys.argv
        try:
            exec(compile(adapted, str(source), "exec"), ns)
            sys.argv = [str(source)] + (["--case", "all"] if case == "lazy" else (["--lean"] if case == "calibration" else []))
            result = ns["main"]()
            if result not in (None, 0):
                raise RuntimeError("Inherited check returned " + str(result))
            record["passed"] = True
        except BaseException as exc:
            record["passed"] = False
            record["error"] = repr(exc)
            raise
        finally:
            sys.argv = prior_argv
            sys.modules.pop(module.__name__, None)
            record["finished_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            (out / ("reproduction_" + case + ".json")).write_text(json.dumps(record, indent=2) + "\n")
            summary["cases"].append(record)
            summary["output_sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob("*")) if p.is_file() and p.name != "summary.json"}
            summary["all_passed"] = len(summary["cases"]) == len(selected) and all(r["passed"] for r in summary["cases"])
            (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
            (EVIDENCE / "inherited_regression_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"inherited_regressions_passed": len(summary["cases"]),
                      "evidence": relative_out}, sort_keys=True))

if __name__ == "__main__":
    main()
