"""Fresh, pinned Lean build, own-kernel replay, axiom audit and negative controls.

The compiler and dependency cache are supplied separately. No network access is
performed. This verifies the named bridge declarations, not the entire paper.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "formal"
EVIDENCE = ROOT / "evidence" / "formal_1.8.0"
MODULES = ["Field", "Views", "Realization", "Protected", "Compression", "Examples", "Binary", "Generated", "Recovery", "Extension", "Transport", "ExtensionExamples", "SemanticCover", "Trace", "TraceCompleteness", "TraceWire", "TraceExamples", "TraceFixtures"]
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED_LEAN_SHA = "e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550"
EXPECTED_COMMIT = "6a10ac8c22beadecabdbb0919c2b50214762f91d"


def digest(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def strip_comments(s: str) -> str:
    # Nested Lean block comments, and line comments. Preserve line counts.
    out, i, depth = [], 0, 0
    while i < len(s):
        if s.startswith("/-", i): depth += 1; out.extend("  "); i += 2
        elif depth and s.startswith("-/", i): depth -= 1; out.extend("  "); i += 2
        elif depth: out.append("\n" if s[i] == "\n" else " "); i += 1
        elif s.startswith("--", i):
            j = s.find("\n", i)
            if j < 0: j = len(s)
            out.extend(" " * (j-i)); i = j
        else: out.append(s[i]); i += 1
    if depth: raise ValueError("unterminated Lean comment")
    return "".join(out)


def inventory(path: Path) -> list[dict]:
    ns, rows = [], []
    for line, text in enumerate(strip_comments(path.read_text()).splitlines(), 1):
        m = re.match(r"\s*namespace\s+([\w.]+)", text)
        if m: ns.append(m[1]); continue
        if re.match(r"\s*end(?:\s+[\w.]+)?\s*$", text):
            if ns: ns.pop()
            continue
        m = re.match(r"\s*(?:@\[[^\]]*\]\s*)?(theorem|lemma|def|structure|inductive)\s+([\w.]+)", text)
        if m:
            rows.append({"name": ".".join(ns + [m[2]]), "kind": m[1],
                         "file": str(path.relative_to(ROOT)), "line": line})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=os.environ.get("KOMOREBI_LEAN_RUNTIME"))
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    if args.runtime is None:
        parser.error("--runtime or KOMOREBI_LEAN_RUNTIME is required")
    runtime = args.runtime.resolve()
    lean = runtime / "toolchain/bin/lean"
    checker = runtime / "toolchain/bin/leanchecker"
    packages = runtime / "workspace/.lake/packages"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    report = {"version": "1.8.0", "started_utc": datetime.now(timezone.utc).isoformat(),
              "status": "RUNNING", "scope": "Eighteen proof-field modules, all explicit named declarations in those sources, own-kernel replays, negative controls, and selected native export. Not the entire manuscript or Mathlib.",
              "commands": [], "dependency_pins": [], "declarations": []}
    output = EVIDENCE / "verification.json"
    output.write_text(json.dumps(report, indent=2)+"\n")
    env = os.environ.copy()
    env["PATH"] = str(lean.parent) + os.pathsep + env.get("PATH", "")
    env["MALLOC_ARENA_MAX"] = "2"

    def run(argv, label, cwd=FORMAL, expected=0):
        argv = list(map(str, argv)); start = time.monotonic()
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, start_new_session=True)
        timed_out = False
        try: text, _ = process.communicate(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            text, _ = process.communicate()
        logfile = EVIDENCE / (label+".log")
        logfile.write_text(text)
        record = {"label": label, "command": argv, "cwd": str(cwd), "exit_code": process.returncode,
                  "timed_out": timed_out, "seconds": round(time.monotonic()-start, 4),
                  "log": str(logfile.relative_to(ROOT)), "log_sha256": digest(logfile)}
        report["commands"].append(record)
        if timed_out: raise RuntimeError(f"{label} timed out; not a successful rejection")
        if expected is not None and process.returncode != expected:
            raise RuntimeError(f"{label} returned {process.returncode}: {text[-2500:]}")
        print(f"{label}: exit {process.returncode}", flush=True)
        return text, process.returncode

    try:
        if digest(lean) != EXPECTED_LEAN_SHA: raise RuntimeError("compiler SHA-256 mismatch")
        version, _ = run([lean, "--version"], "lean_version")
        if EXPECTED_COMMIT not in version or "4.34.0-rc2" not in version:
            raise RuntimeError("compiler version or commit mismatch")
        report["compiler"] = {"version": version.strip(), "sha256": digest(lean),
                              "leanchecker_sha256": digest(checker)}
        pins = json.loads((FORMAL/"dependency-pins.json").read_text())
        if len(pins) != 9: raise RuntimeError("expected all nine dependency pins")
        for pin in pins:
            text, _ = run(["git", "rev-parse", "HEAD"], "pin_"+pin["name"], packages/pin["name"])
            if text.strip() != pin["rev"]: raise RuntimeError(f"dependency pin mismatch: {pin['name']}")
            report["dependency_pins"].append(pin)
        production = [FORMAL/"ProofPath"/(m+".lean") for m in MODULES]
        forbidden = []
        for path in production:
            body = strip_comments(path.read_text())
            for m in re.finditer(r"\b(sorry|admit|axiom|unsafe|native_decide|implemented_by)\b", body):
                forbidden.append({"file": str(path.relative_to(ROOT)), "token": m[1]})
            report["declarations"].extend(inventory(path))
        if forbidden: raise RuntimeError(f"forbidden production tokens: {forbidden}")
        report["source_scan"] = {"status": "PASS", "forbidden_hits": []}
        names = [d["name"] for d in report["declarations"]]
        if len(names) != len(set(names)): raise RuntimeError("duplicate declaration inventory")
        report["named_theorems"] = sum(d["kind"] in {"lemma", "theorem"} for d in report["declarations"])
        report["named_declarations"] = len(names)
        report["source_hashes"] = {str(p.relative_to(ROOT)): digest(p) for p in production+[FORMAL/"ExportNative.lean", FORMAL/"CheckTraceJson.lean"]}
        # Never import stale project objects from formal/. Only this fresh temp tree.
        with tempfile.TemporaryDirectory(prefix="proof-path-clean-") as td:
            build = Path(td); (build/"ProofPath").mkdir()
            env["LEAN_PATH"] = os.pathsep.join([str(build)] + [str(packages/p["name"]/".lake/build/lib/lean") for p in pins])
            for m, source in zip(MODULES, production):
                target = build/"ProofPath"/(m+".olean")
                run([lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false", "-o", target, source.relative_to(FORMAL)], "build_"+m)
            for m in MODULES:
                run([checker, "--verbose", "ProofPath."+m], "replay_"+m)
            report["replay_kind"] = "Lean own-kernel replay of new module declarations against cached imports. Not an independent verifier or a fresh replay of all Mathlib."
            audit = "\n".join("import ProofPath."+m for m in MODULES)+"\n\n"+"\n".join("#print axioms "+n for n in names)+"\n"
            audit_path = EVIDENCE/"AxiomConsumer.lean"; audit_path.write_text(audit)
            text, _ = run([lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false", audit_path], "axiom_audit")
            seen = {}
            for match in re.finditer(r"'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)", text):
                seen[match[1]] = [a.strip() for a in (match[2] or "").replace("\n", " ").split(",") if a.strip()]
            if set(seen) != set(names):
                raise RuntimeError(f"axiom inventory mismatch, missing {set(names)-set(seen)}, extra {set(seen)-set(names)}")
            for n, axioms in seen.items():
                if set(axioms)-ALLOWED: raise RuntimeError(f"unexpected axioms for {n}: {axioms}")
            report["axioms"] = seen
            report["object_hashes"] = {"ProofPath/"+m+".olean": digest(build/"ProofPath"/(m+".olean")) for m in MODULES}
            run([lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false", "ExportNative.lean"], "native_export")
            report["native_export_sha256"] = digest(ROOT/"data/native_lean_field.json")
            # Execute the real JSON-text adapter only against the newly built modules.
            # Its standard text parser/printer and IO remain outside the proved AST codec.
            cases = ROOT / "data/trace_exchange_cases.ndjson"
            expected = (ROOT / "data/trace_exchange_expected.txt").read_text().splitlines()
            text, _ = run([lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false",
                           "--run", "CheckTraceJson.lean", cases], "trace_json_conformance")
            answers = text.splitlines()
            if len(answers) != len(expected):
                raise RuntimeError(f"JSON adapter returned {len(answers)} rows for {len(expected)} inputs")
            mismatches = [i for i, (want, got) in enumerate(zip(expected, answers))
                          if not (got.startswith("REJECT_") if want == "REJECT" else got == want)]
            if mismatches:
                raise RuntimeError(f"JSON conformance mismatches at {mismatches[:20]}")
            from collections import Counter
            report["trace_json_conformance"] = {
                "status": "PASS", "cases": len(answers), "mismatches": 0,
                "verdicts": dict(Counter(answers)), "input_sha256": digest(cases),
                "expected_sha256": digest(ROOT / "data/trace_exchange_expected.txt"),
                "actual_log_sha256": digest(EVIDENCE / "trace_json_conformance.log"),
                "scope": "Executed exact canonical text cases; general proof covers the decoded Json AST, not IO or the text parser."
            }
            controls = [
                ("FalseEquality", "proved that the proposition"),
                ("WrongWitness", "proved that the proposition"),
                ("MissingSupport", "proved that the proposition"),
                ("Placeholder", "declaration uses `sorry`"),
                ("WrongDecoder", "proved that the proposition"),
                ("MergedContext", "proved that the proposition"),
                ("ForgedClosure", "proved that the proposition"),
                ("PartialClosure", "proved that the proposition"),
                ("BooleanIndex", "proved that the proposition"),
                ("ChangedObservations", "proved that the proposition"),
            ]
            report["negative_controls"] = []
            for control, diagnostic in controls:
                text, code = run([lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false", "negative_controls/"+control+".lean"], "negative_"+control, expected=None)
                if code == 0 or diagnostic not in text:
                    raise RuntimeError(f"negative control {control} did not produce its expected proof diagnostic: {text}")
                report["negative_controls"].append({"name": control, "status": "REJECTED_AS_EXPECTED", "diagnostic": diagnostic})
            text, code = run([lean, "-j1", "-DwarningAsError=true", "-DautoImplicit=false", "negative_controls/ExtraAxiom.lean"], "negative_ExtraAxiom")
            if "ExtraAxiom.assumedFalse" not in text:
                raise RuntimeError("extra axiom not found in dependency report")
            report["negative_controls"].append({"name": "ExtraAxiom", "status": "LEAN_ACCEPTED_RELATIVE_TO_AXIOM_POLICY_REJECTED", "axiom": "ExtraAxiom.assumedFalse"})
        report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"; report["failure"] = str(exc)
        print(str(exc), file=sys.stderr)
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ["status", "named_theorems", "named_declarations"] if k in report}))
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
