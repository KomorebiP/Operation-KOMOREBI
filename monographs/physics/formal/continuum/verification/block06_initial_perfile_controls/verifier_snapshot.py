#!/usr/bin/env python3
"""Fresh, sequential verification of the Komorebi Physics block.

The existing exact-pin Mathlib cache is used, not rebuilt. All active
local modules are recompiled. Timeouts and tool failures never count as proofs.
This script is Linux/WSL-oriented because the recovered kit is Linux x86-64.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
VERSION = "4.34.0-rc2"
MATHLIB = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_comments_and_strings(text: str) -> str:
    """Conservative token precheck, not a replacement for the kernel/axiom audit."""
    out: list[str] = []
    depth, quoted, i = 0, False, 0
    while i < len(text):
        c = text[i]
        if depth:
            if text.startswith("/-", i):
                depth += 1; out.extend("  "); i += 2; continue
            if text.startswith("-/", i):
                depth -= 1; out.extend("  "); i += 2; continue
            out.append("\n" if c == "\n" else " "); i += 1; continue
        if quoted:
            if c == "\\" and i + 1 < len(text):
                out.extend("  "); i += 2; continue
            if c == '"': quoted = False
            out.append("\n" if c == "\n" else " "); i += 1; continue
        if text.startswith("--", i):
            end = text.find("\n", i)
            if end == -1: end = len(text)
            out.extend(" " * (end - i)); i = end; continue
        if text.startswith("/-", i):
            depth = 1; out.extend("  "); i += 2; continue
        if c == '"': quoted = True; out.append(" "); i += 1; continue
        out.append(c); i += 1
    if depth or quoted:
        raise ValueError("Unterminated source comment or string")
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kit", type=Path, required=True, help="Restored exact-pin portable Lean kit")
    ap.add_argument("--out", type=Path, default=Path("verification/local_run"))
    ap.add_argument("--timeout", type=int, default=240, help="Wall-clock seconds per command/module/audit batch")
    args = ap.parse_args()
    kit = args.kit.expanduser().resolve()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    runner = kit / "run.sh"
    report: dict = {
        "schema_version": 1, "started_utc": datetime.now(timezone.utc).isoformat(),
        "status": "INCOMPLETE", "checks": [], "allowed_axioms": sorted(ALLOWED_AXIOMS),
        "limits": {"seconds_per_command": args.timeout, "lean_workers": 1},
        "trust_boundary": "Fresh local proof terms against the restored pinned cache; imported Mathlib/Lean libraries not independently rebuilt.",
        "verifier_sha256": sha256(Path(__file__)),
    }
    start = time.monotonic()

    def save_progress() -> None:
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")

    save_progress()

    def run(label: str, argv: list[str], *, expected_failure: bool = False,
            diagnostic: str | None = None) -> str:
        log = out / (label + ".log")
        t0 = time.monotonic()
        record = {"label": label, "argv": argv, "cwd": str(ROOT),
                  "expected_failure": expected_failure, "status": "INCOMPLETE"}
        report["checks"].append(record)
        save_progress()
        try:
            result = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, timeout=args.timeout)
            text = result.stdout
            log.write_text(text)
            record.update(returncode=result.returncode, seconds=round(time.monotonic() - t0, 4),
                          log=str(log.relative_to(out)), log_sha256=sha256(log))
            if expected_failure:
                ok = result.returncode != 0 and diagnostic is not None and diagnostic in text
                # An import/environment failure is not a successful negative control.
                ok = ok and "unknown module prefix" not in text and "object file" not in text
            else:
                ok = result.returncode == 0
            record["status"] = "PASS" if ok else "FAIL"
            save_progress()
            if not ok:
                raise RuntimeError(f"{label} failed its contract; see {log}")
            print(f"PASS {label} ({record['seconds']:.2f}s)", flush=True)
            return text
        except subprocess.TimeoutExpired as exc:
            text = exc.stdout or ""
            if isinstance(text, bytes): text = text.decode(errors="replace")
            log.write_text(text + "\nTIMEOUT: not a proof.\n")
            record.update(status="TIMEOUT", seconds=round(time.monotonic() - t0, 4),
                          log=str(log.relative_to(out)), log_sha256=sha256(log))
            raise RuntimeError(f"{label} timed out; no verification result claimed") from exc

    try:
        if not runner.is_file():
            raise FileNotFoundError(f"Portable launcher not found: {runner}")
        inventory = json.loads((ROOT / "declaration_inventory.json").read_text())
        modules: list[str] = inventory["modules"]
        declarations: list[dict] = inventory["declarations"]
        names = [e["name"] for e in declarations]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate declaration names in inventory")
        files = [ROOT / (mod.replace(".", "/") + ".lean") for mod in modules]
        files += [ROOT / "KomorebiPhysics.lean", ROOT / "Audit.lean"]
        prohibited = re.compile(r"\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern|ofReduceBool)\b|skipKernelTC|#eval|#run")
        for f in files:
            clean = strip_comments_and_strings(f.read_text())
            bad = prohibited.search(clean)
            if bad: raise ValueError(f"Prohibited active token in {f}: {bad.group()}")
        report["source_precheck"] = "PASS"
        declared_count = sum(len(re.findall(r"\btheorem\s+", strip_comments_and_strings(f.read_text()))) for f in files[:-2])
        if declared_count != sum(e["kind"] == "theorem" for e in declarations):
            raise ValueError("Source theorem count differs from inventory")
        audit_commands = re.findall(r"^#print axioms (\S+)$", (ROOT / "Audit.lean").read_text(), re.M)
        if audit_commands != names:
            raise ValueError("Axiom audit commands do not exactly match inventory")
        sources = files + sorted((ROOT / "negative_controls").glob("*.lean")) + [ROOT / "reference/block01_preservation.json", ROOT / "reference/block02_preservation.json", ROOT / "reference/block03_preservation.json", ROOT / "reference/block04_preservation.json", ROOT / "reference/block05_preservation.json", ROOT / "declaration_inventory.json", ROOT / "lakefile.toml",
                           ROOT / "lean-toolchain", ROOT / "lake-manifest.json", Path(__file__)]
        report["source_sha256"] = {str(f.relative_to(ROOT)): sha256(f) for f in sources}
        version = run("lean_version", ["bash", str(runner), "lean", "--version"]).strip()
        if f"version {VERSION}," not in version:
            raise ValueError(f"Wrong Lean version: {version}")
        report["lean_version"] = version
        if (ROOT / "lean-toolchain").read_bytes() != (kit / "workspace/lean-toolchain").read_bytes():
            raise ValueError("Project and portable-kit toolchains differ")
        manifest = json.loads((ROOT / "lake-manifest.json").read_text())
        report["dependencies"] = []
        for dep in manifest["packages"]:
            path = kit / "workspace/.lake/packages" / dep["name"]
            actual = run("revision_" + dep["name"], ["git", "-C", str(path), "rev-parse", "HEAD"]).strip()
            if actual != dep["rev"]:
                raise ValueError("Dependency revision mismatch: " + dep["name"])
            dirty = run("tracked_status_" + dep["name"],
                        ["git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"])
            if dirty.strip():
                raise ValueError("Tracked dependency modifications: " + dep["name"])
            report["dependencies"].append({"name": dep["name"], "revision": actual, "tracked_tree_clean": True})
        if not any(d["name"] == "mathlib" and d["revision"] == MATHLIB for d in report["dependencies"]):
            raise ValueError("Pinned Mathlib dependency absent")
        report["runtime_sha256"] = {
            str(q.relative_to(kit)): sha256(q)
            for q in [runner, kit / "toolchain/bin/lean", kit / "toolchain/bin/lake",
                      kit / "toolchain/lib/lean/libleanshared.so"]
        }
        run("attach", ["bash", str(runner), "attach", str(ROOT)])
        build = ROOT / ".lake/build"
        if build.exists(): shutil.rmtree(build)
        objroot = build / "lib/lean"
        objroot.mkdir(parents=True)
        for mod in modules + ["KomorebiPhysics"]:
            rel = mod.replace(".", "/")
            obj = objroot / (rel + ".olean")
            obj.parent.mkdir(parents=True, exist_ok=True)
            run("compile_" + mod.replace(".", "_"),
                ["bash", str(runner), "lake", "env", "lean", "-j1", "-DwarningAsError=true",
                 "-o", str(obj), rel + ".lean"])
        # Audit the entire exact inventory in one bounded Lean invocation.
        # The 579-name timing probe established that this fits the command cap.
        # No declaration is omitted; output is still checked for exact name match
        # and allowed dependencies below. Reusing one import avoids repeatedly
        # loading the same complete aggregate for every small module batch.
        audit = out / "audit_complete.lean"
        audit.write_text("import KomorebiPhysics\n\n" +
            "".join("#print axioms " + e["name"] + "\n" for e in declarations))
        record = {"module": "ALL", "declarations": len(declarations),
                  "input_sha256": sha256(audit), "path": audit.name}
        report["axiom_batches"] = [record]
        chunks = [run("axioms_complete_inventory",
            ["bash", str(runner), "lake", "env", "lean", "-j1",
             "-DwarningAsError=true", str(audit)])]
        if sha256(audit) != record["input_sha256"]:
            raise RuntimeError("Axiom audit input changed during run")
        text = "\n".join(chunks)
        (out / "axioms.log").write_text(text)
        found: dict[str, list[str]] = {}
        pattern = r"'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
        for m in re.finditer(pattern, text, flags=re.S):
            name = m[1]
            if name in found: raise ValueError("Duplicate axiom output for " + name)
            axioms = [] if m[2] is None else [a.strip() for a in m[2].split(",") if a.strip()]
            found[name] = axioms
        if set(found) != set(names):
            raise ValueError(f"Incomplete axiom audit: missing {set(names)-set(found)}, extra {set(found)-set(names)}")
        for name, axioms in found.items():
            if not set(axioms) <= ALLOWED_AXIOMS:
                raise ValueError(f"Unexpected axioms for {name}: {axioms}")
        report["axiom_audit"] = {"status": "PASS", "declaration_count": len(found), "dependencies": found}
        controls = {"FalseEquality": "rfl", "AdmittedProof": "sorry",
                    "MissingSkew": "unsolved goals", "WrongHamiltonianSign": "unsolved goals",
                    "OmittedIntrinsic": "unsolved goals", "OmittedLeftFrame": "unsolved goals",
                    "OmittedRightFrame": "unsolved goals", "WrongCommutatorSign": "unsolved goals",
                    "NonunitaryOrthogonality": "unsolved goals",
                    "WrongMixedSign": "unsolved goals", "MissingTraceConjugation": "unsolved goals",
                    "MissingDensityHermiticity": "unsolved goals", "MissingHamiltonianHermiticity": "unsolved goals",
                    "BinaryWithoutPartition": "unsolved goals", "OmittedSource": "unsolved goals",
                    "JointProbabilityFactorization": "unsolved goals", "MarginalsDetermineJoint": "unsolved goals",
                    "BellProductMixture": "unsolved goals", "OmittedPartialTraceFactor": "unsolved goals",
                    "WrongEntropySign": "unsolved goals", "UniversalEntropyIncrease": "unsolved goals",
                    "WrongRenyiFactor": "unsolved goals", "WeightedBalanceWithoutAntisymmetry": "unsolved goals",
                    "WrongJumpOrientation": "unsolved goals",
                    "WrongRateAmplitude": "unsolved goals",
                    "NegativeRateSquareRoot": "unsolved goals",
                    "JumpWithoutLoss": "unsolved goals",
                    "WrongAnticommutatorFactor": "unsolved goals",
                    "SelfJumpNoCoherence": "unsolved goals",
                    "OmittedCoherentCurrent": "unsolved goals",
                    "WrongCoherenceRate": "unsolved goals",
                    "RelativeEntropyWrongSign": "unsolved goals",
                    "RelativeEntropyWithoutBalance": "unsolved goals",
                    "ZeroDissipationUnique": "unsolved goals",
                    "WrongRefinementWeight": "unsolved goals",
                    "WrongRefinementQuadraticSign": "unsolved goals",
                    "RefinementExtraCancellation": "unsolved goals",
                    "RefinementExtraOrder": "unsolved goals",
                    "RefinementUnitRatio": "unsolved goals",
                    "RefinementNoiseContraction": "unsolved goals",
                    "WrongRefinementThirdDenominator": "unsolved goals",
                   }
        control_files = {q.stem for q in (ROOT / "negative_controls").glob("*.lean")}
        if control_files != set(controls):
            raise ValueError("Negative-control inventory differs from files")
        for name, diagnostic in controls.items():
            run("negative_" + name,
                ["bash", str(runner), "lake", "env", "lean", "-j1", "-DwarningAsError=true",
                 "negative_controls/" + name + ".lean"], expected_failure=True, diagnostic=diagnostic)
        report["negative_controls"] = {"passed": len(controls), "total": len(controls)}
        for file, old in report["source_sha256"].items():
            if sha256(ROOT / file) != old: raise RuntimeError("Source changed during run: " + file)
        preservation = json.loads((ROOT / "reference/upstream_preservation.json").read_text())
        for e in preservation["preserved_files"]:
            if sha256(ROOT / e["local_file"]) != e["source_sha256"]:
                raise RuntimeError("Upstream source preservation failed: " + e["local_file"])
        report["upstream_preservation"] = "PASS"
        block01 = json.loads((ROOT / "reference/block01_preservation.json").read_text())
        for e in block01["preserved_files"]:
            if sha256(ROOT / e["local_file"]) != e["source_sha256"]:
                raise RuntimeError("Block 01 source preservation failed: " + e["local_file"])
        report["block01_source_preservation"] = "PASS"
        block02 = json.loads((ROOT / "reference/block02_preservation.json").read_text())
        for e in block02["preserved_files"]:
            if sha256(ROOT / e["local_file"]) != e["source_sha256"]:
                raise RuntimeError("Block 02 source preservation failed: " + e["local_file"])
        report["block02_source_preservation"] = {"status": "PASS", "modules": len(block02["preserved_files"])}
        block03 = json.loads((ROOT / "reference/block03_preservation.json").read_text())
        for e in block03["preserved_files"]:
            if sha256(ROOT / e["local_file"]) != e["source_sha256"]:
                raise RuntimeError("Block 03 source preservation failed: " + e["local_file"])
        report["block03_source_preservation"] = {"status": "PASS", "modules": len(block03["preserved_files"])}
        block04 = json.loads((ROOT / "reference/block04_preservation.json").read_text())
        for e in block04["preserved_files"]:
            if sha256(ROOT / e["local_file"]) != e["source_sha256"]:
                raise RuntimeError("Block 04 source preservation failed: " + e["local_file"])
        report["block04_source_preservation"] = {"status": "PASS", "modules": len(block04["preserved_files"])}
        block05 = json.loads((ROOT / "reference/block05_preservation.json").read_text())
        for e in block05["preserved_files"]:
            if sha256(ROOT / e["local_file"]) != e["source_sha256"]:
                raise RuntimeError("Block 05 source preservation failed: " + e["local_file"])
        report["block05_source_preservation"] = {"status": "PASS", "modules": len(block05["preserved_files"])}
        report["compiled_outputs_sha256"] = {
            str(q.relative_to(ROOT)): sha256(q) for q in sorted(objroot.rglob("*")) if q.is_file()
        }
        theorems = [e for e in declarations if e["kind"] == "theorem"]
        report["counts"] = {
            "active_modules": len(modules), "new_theorems": sum(e["origin"].startswith("new") for e in theorems),
            "block01_new_theorems": sum(e["origin"] == "new_full_edition_block_01" for e in theorems),
            "block02_new_theorems": sum(e["origin"] == "new_full_edition_block_02" for e in theorems),
            "block03_new_theorems": sum(e["origin"] == "new_full_edition_block_03" for e in theorems),
            "block04_new_theorems": sum(e["origin"] == "new_full_edition_block_04" for e in theorems),
            "block05_new_theorems": sum(e["origin"] == "new_full_edition_block_05" for e in theorems),
            "block06_new_theorems": sum(e["origin"] == "new_full_edition_block_06" for e in theorems),
            "rechecked_upstream_theorems": sum(e["origin"].startswith("preserved") for e in theorems),
            "total_theorems": len(theorems), "audited_declarations": len(declarations),
        }
        report["status"] = "PASS"
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        report["status"] = "FAIL"
        report["error"] = str(exc)
        print("FAIL:", exc, file=sys.stderr, flush=True)
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        report["seconds"] = round(time.monotonic() - start, 4)
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    if report["status"] == "PASS":
        print(json.dumps(report["counts"], indent=2))
        print("PASS: all active local modules, complete declaration axiom inventory, and all listed negative controls.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
