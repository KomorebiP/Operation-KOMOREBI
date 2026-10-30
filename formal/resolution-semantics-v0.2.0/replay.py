"""Compile fresh proof objects, audit every theorem, and check rejection controls.

Uses only Python's standard library and the pinned Lean compiler. Never installs
dependencies or modifies the original source edition. The output must be a new
directory so that an existing execution record cannot be overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIN = "4.24.0"
SOURCES = ("KRSCore.lean", "TwoWorld.lean", "ResolutionSemantics.lean", "AxiomAudit.lean")
MAIN_THEOREMS = (
    "KRS.TwoWorld.no_swap_equivariant_additive_retraction",
    "KRS.TwoWorld.no_swap_equivariant_boolean_retraction",
)
ALLOWED_AXIOMS = {"propext", "Quot.sound", "Classical.choice"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def theorem_names() -> list[str]:
    names = []
    for filename, namespace in (("KRSCore.lean", "KRS"), ("TwoWorld.lean", "KRS.TwoWorld")):
        text = (HERE / filename).read_text(encoding="utf-8")
        names += [namespace + "." + name for name in
                  re.findall(r"^theorem\s+([A-Za-z_][A-Za-z_0-9.]*)", text, re.M)]
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", default="lean", help="Pinned Lean executable or elan shim")
    parser.add_argument("--output", type=Path, required=True, help="New execution-record directory")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "schema": 1,
        "kind": "bounded-lean-replay",
        "component": "resolution-semantics",
        "companion_version": "0.2.0",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "lean_pin": (HERE / "lean-toolchain").read_text(encoding="utf-8").strip(),
        "inputs": {name: sha256(HERE / name) for name in
                   (*SOURCES, "replay.py", "lean-toolchain", "lakefile.toml", "PROVENANCE.json")},
        "steps": [],
        "status": "FAIL",
        "scope": "The 15 scaffold theorems and the explicit two-world theorem and assumption controls. No whole-paper verification.",
    }
    try:
        lean = shutil.which(args.lean)
        if lean is None:
            raise RuntimeError("Lean executable not found; install the pinned toolchain separately.")
        # Keep the invoked basename: on Unix, resolving an elan-managed `lean`
        # symlink can turn the command into `elan --version` instead.
        lean = str(Path(lean).absolute())
        git = shutil.which("git")
        if git:
            result = subprocess.run([git, "rev-parse", "HEAD"], cwd=ROOT,
                                    text=True, capture_output=True, check=True)
            receipt["checkout_revision"] = result.stdout.strip()
            result = subprocess.run([git, "status", "--porcelain", "--", str(HERE.relative_to(ROOT))],
                                    cwd=ROOT, text=True, capture_output=True, check=True)
            receipt["companion_has_local_changes"] = bool(result.stdout.strip())
        env = dict(os.environ)
        # Do not let an ambient project or editor search path supply stale proofs.
        env.pop("LEAN_PATH", None)
        env.pop("LEAN_SRC_PATH", None)
        env.pop("LEAN_SYSROOT", None)

        def run(label: str, command: list[str], cwd: Path, *, expected_zero: bool = True,
                diagnostic: str | None = None) -> str:
            result = subprocess.run(command, cwd=cwd, env=env, text=True,
                                    encoding="utf-8", errors="replace", capture_output=True, timeout=120)
            stdout = output / (label + ".stdout.txt")
            stderr = output / (label + ".stderr.txt")
            stdout.write_text(result.stdout, encoding="utf-8", newline="\n")
            stderr.write_text(result.stderr, encoding="utf-8", newline="\n")
            accepted = ((result.returncode == 0) == expected_zero)
            combined = result.stdout + result.stderr
            if diagnostic:
                accepted = accepted and diagnostic in combined
            forbidden = ("unknown module", "unknown identifier", "file not found", "object file",
                         "failed to synthesize", "unknown namespace", "unexpected token")
            if not expected_zero:
                accepted = accepted and not any(x in combined.lower() for x in forbidden)
            receipt["steps"].append({
                "name": label, "command": [Path(command[0]).name, *command[1:]],
                "exit_code": result.returncode, "expected_zero": expected_zero,
                "required_diagnostic": diagnostic, "accepted": accepted,
                "stdout": stdout.name, "stderr": stderr.name,
                "stdout_sha256": sha256(stdout), "stderr_sha256": sha256(stderr),
            })
            if not accepted:
                raise RuntimeError(label + " did not meet its acceptance criteria; see its raw logs.")
            return result.stdout

        version = run("version", [lean, "--version"], HERE)
        receipt["lean_version"] = version.strip()
        if not re.search(r"version " + re.escape(PIN) + r"(?:,|\s)", version):
            raise RuntimeError("Compiler differs from the pinned Lean " + PIN)
        prefix = run("compiler-prefix", [lean, "--print-prefix"], HERE).strip()
        compiler = Path(prefix) / "bin" / ("lean.exe" if os.name == "nt" else "lean")
        if not compiler.is_file():
            raise RuntimeError("Could not resolve the pinned compiler behind the Lean/elan command.")
        lean = str(compiler.resolve())
        receipt["compiler_executable_sha256"] = sha256(compiler)
        provenance = json.loads((HERE / "PROVENANCE.json").read_text(encoding="utf-8"))
        original = ROOT / provenance["original"]["path"]
        original_bytes = original.read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(original_bytes).hexdigest() != provenance["original"]["sha256"]:
            raise RuntimeError("Original scaffold differs from its recorded source identity.")
        receipt["original_scaffold_sha256"] = hashlib.sha256(original_bytes).hexdigest()
        receipt["original_checkout_sha256"] = sha256(original)
        signatures = lambda text: [" ".join(s.split()) for s in
                                   re.findall(r"^theorem\s+([\s\S]*?)\s*:=\s*by", text, re.M)]
        if signatures(original.read_text(encoding="utf-8")) != signatures((HERE / "KRSCore.lean").read_text(encoding="utf-8")):
            raise RuntimeError("The companion changed an original scaffold theorem statement.")
        names = theorem_names()
        expected_audit = "import ResolutionSemantics\n\n" + "".join("#print axioms " + n + "\n" for n in names)
        if (HERE / "AxiomAudit.lean").read_text(encoding="utf-8") != expected_audit:
            raise RuntimeError("AxiomAudit.lean does not cover every declared theorem exactly once.")
        with tempfile.TemporaryDirectory(prefix=".build-", dir=output) as temporary:
            build = Path(temporary)
            for name in SOURCES:
                shutil.copyfile(HERE / name, build / name)
            env["LEAN_PATH"] = str(build)
            for name in SOURCES:
                run("compile-" + Path(name).stem,
                    [lean, "-DwarningAsError=true", "-o", Path(name).stem + ".olean", name], build)
            audit_text = (output / "compile-AxiomAudit.stdout.txt").read_text(encoding="utf-8")
            axioms = {}
            for name in names:
                empty = "'" + name + "' does not depend on any axioms"
                match = re.search(r"'" + re.escape(name) + r"' depends on axioms:\s*\[([^]]*)\]", audit_text)
                if empty in audit_text:
                    axioms[name] = []
                elif match:
                    axioms[name] = [a.strip() for a in match.group(1).split(",") if a.strip()]
                else:
                    raise RuntimeError("Missing axiom inventory for " + name)
                if not set(axioms[name]) <= ALLOWED_AXIOMS:
                    raise RuntimeError("Unexpected axiom in " + name + ": " + repr(axioms[name]))
            if any(axioms[name] for name in MAIN_THEOREMS):
                raise RuntimeError("The two main obstruction theorems must be axiom-free.")
            receipt["theorem_axioms"] = axioms
            receipt["theorem_count"] = len(names)

            controls = {
                "reject-false-symmetry": """import ResolutionSemantics
open KRS.TwoWorld
example : leftProjection.toFun (swap (true, false)) =
    swap (leftProjection.toFun (true, false)) := by rfl
""",
                "reject-false-additivity": """import ResolutionSemantics
open KRS.TwoWorld
example : lowerSummary (xor (true, false) (false, true)) =
    xor (lowerSummary (true, false)) (lowerSummary (false, true)) := by rfl
""",
                "reject-sorry": """import ResolutionSemantics
example : False := by sorry
""",
            }
            for label, source in controls.items():
                (build / "Control.lean").write_text(source, encoding="utf-8", newline="\n")
                (output / (label + ".lean.txt")).write_text(source, encoding="utf-8", newline="\n")
                run(label, [lean, "-DwarningAsError=true", "Control.lean"], build,
                    expected_zero=False,
                    diagnostic="declaration uses 'sorry'" if label == "reject-sorry" else "Tactic `rfl` failed")
            receipt["negative_controls"] = len(controls)
        receipt["status"] = "PASS"
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as error:
        receipt["error"] = str(error)
    finally:
        receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
        (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": receipt["status"], "theorems": receipt.get("theorem_count"),
                      "negative_controls": receipt.get("negative_controls"), "receipt": str(output / "receipt.json")}))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
