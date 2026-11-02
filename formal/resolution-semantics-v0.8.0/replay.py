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
SOURCES = ("KRSCore.lean", "TwoWorld.lean", "GraphReconstruction.lean", "GraphSolver.lean",
           "GraphExamples.lean", "GraphCounting.lean", "GraphCountExamples.lean",
           "GraphPinning.lean", "GraphPinExamples.lean", "GraphTraversalSolver.lean",
           "GraphTraversalExamples.lean", "GraphPathSearch.lean", "GraphAutomaticTraversal.lean",
           "GraphAutomaticExamples.lean", "GraphFiniteCounting.lean", "GraphEdgeSpace.lean", "GraphQuotient.lean", "GraphRanks.lean", "GraphRankExamples.lean", "ResolutionSemantics.lean",
           "GraphDemo.lean", "GraphCountDemo.lean", "GraphPinDemo.lean", "GraphTraversalDemo.lean", "GraphAutomaticDemo.lean", "GraphRankDemo.lean", "AxiomAudit.lean")
MAIN_THEOREMS = (
    "KRS.TwoWorld.no_swap_equivariant_additive_retraction",
    "KRS.TwoWorld.no_swap_equivariant_boolean_retraction",
)
ALLOWED_AXIOMS = {"propext", "Quot.sound", "Classical.choice"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def theorem_names() -> list[str]:
    names = []
    for filename, namespace in (("KRSCore.lean", "KRS"), ("TwoWorld.lean", "KRS.TwoWorld"), ("GraphReconstruction.lean", "KRS.Graph"), ("GraphSolver.lean", "KRS.Graph"), ("GraphExamples.lean", "KRS.Graph.Examples"), ("GraphCounting.lean", "KRS.Graph"), ("GraphCountExamples.lean", "KRS.Graph.CountExamples"), ("GraphPinning.lean", "KRS.Graph"), ("GraphPinExamples.lean", "KRS.Graph.PinExamples"), ("GraphTraversalSolver.lean", "KRS.Graph"), ("GraphTraversalExamples.lean", "KRS.Graph.TraversalExamples"), ("GraphPathSearch.lean", "KRS.Graph"), ("GraphAutomaticTraversal.lean", "KRS.Graph"), ("GraphAutomaticExamples.lean", "KRS.Graph.AutomaticExamples"), ("GraphFiniteCounting.lean", "KRS.Graph"), ("GraphEdgeSpace.lean", "KRS.Graph"), ("GraphQuotient.lean", "KRS.Graph"), ("GraphRanks.lean", "KRS.Graph"), ("GraphRankExamples.lean", "KRS.Graph.RankExamples")):
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
        "companion_version": "0.8.0",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "lean_pin": (HERE / "lean-toolchain").read_text(encoding="utf-8").strip(),
        "inputs": {name: sha256(HERE / name) for name in
                   (*SOURCES, "replay.py", "lean-toolchain", "lakefile.toml", "PROVENANCE.json")},
        "steps": [],
        "status": "FAIL",
        "scope": "The inherited scaffold and two-world obstruction; simple-cycle graph integrability, kernel, component parameterization and root-fixed uniqueness; verified finite search and controls. Exact unpinned and partial-pin reconstruction counts using actual component classes; empty output exactly for jointly inconsistent edge data and pins. Verified reconstruction from supplied checked rooted traversals, with soundness, completeness and reference agreement on existence. Automatic tabulated finite path construction, actual component indexing and sound/complete reconstruction without caller-supplied traversals. No sparse forest constructor, rank formulas, runtime bound or whole-paper verification.",
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
        for name, digest in provenance["inherited_companion"]["unchanged_sources"].items():
            if sha256(HERE / name) != digest:
                raise RuntimeError("Inherited companion input changed: " + name)
        manuscript = ROOT / provenance["manuscript"]["path"]
        manuscript_bytes = manuscript.read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(manuscript_bytes).hexdigest() != provenance["manuscript"]["sha256"]:
            raise RuntimeError("Manuscript differs from its recorded source identity.")
        receipt["manuscript_sha256"] = hashlib.sha256(manuscript_bytes).hexdigest()
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

            expected_demo = """diamond-root-false: some [false, true, false, true]
diamond-root-true: some [true, false, true, false]
inconsistent-triangle: none
disconnected-with-isolated-vertex: some [false, true, true, true, true]
empty-graph: some []
isolated-vertex-true: some [true]
contradictory-root-pins: none
"""
            demo = run("run-graph-examples", [lean, "-DwarningAsError=true", "--run", "GraphDemo.lean"], build)
            if demo != expected_demo:
                raise RuntimeError("Executable graph examples differ from their checked results.")
            receipt["graph_example_cases"] = 7
            expected_counts = """diamond-connected: 2
inconsistent-triangle: 0
two-edges-and-isolated-vertex: 8
empty-graph: 1
isolated-vertex: 2
four-isolated-vertices: 16
"""
            counts = run("run-count-examples", [lean, "-DwarningAsError=true", "--run", "GraphCountDemo.lean"], build)
            if counts != expected_counts:
                raise RuntimeError("Executable reconstruction counts differ from their checked results.")
            receipt["count_example_cases"] = 6


            expected_pins = """diamond-no-pins: 2
diamond-one-pin: 1
diamond-duplicate-pin: 1
diamond-compatible-pins: 1
diamond-conflicting-pins: 0
diamond-contradictory-vertex-pins: 0
disconnected-no-pins: 8
disconnected-one-pin: 4
disconnected-same-component-pins: 4
disconnected-two-components-pinned: 2
disconnected-all-components-pinned: 1
empty-graph-no-pins: 1
isolated-vertex-pinned: 1
nonintegrable-triangle-pinned: 0
"""
            pins_demo = run("run-pin-examples", [lean, "-DwarningAsError=true", "--run", "GraphPinDemo.lean"], build)
            if pins_demo != expected_pins:
                raise RuntimeError("Executable partial-pin counts differ from their checked results.")
            receipt["pin_example_cases"] = 14

            expected_traversals = """traversal-diamond-root-false: some [false, true, false, true]
traversal-diamond-root-true: some [true, false, true, false]
traversal-diamond-nonroot-pin: some [true, false, true, false]
traversal-diamond-duplicate-pin: some [false, true, false, true]
traversal-diamond-conflicting-pins: none
traversal-diamond-alternate-path: some [false, true, false, true]
traversal-diamond-other-root: some [true, false, true, false]
traversal-nonintegrable-triangle: none
traversal-consistent-triangle: some [false, false, false]
traversal-disconnected-partial-pin: some [true, false, false, false, false]
traversal-disconnected-covered: some [false, true, true, true, true]
traversal-empty-graph: some []
traversal-isolated-pin: some [true]
traversal-contradictory-pins: none
"""
            traversals = run("run-traversal-examples", [lean, "-DwarningAsError=true", "--run", "GraphTraversalDemo.lean"], build)
            if traversals != expected_traversals:
                raise RuntimeError("Executable traversal solutions differ from their checked results.")
            receipt["traversal_example_cases"] = 14

            expected_automatic = """automatic-diamond-unpinned: some [false, true, false, true]
automatic-diamond-root-true: some [true, false, true, false]
automatic-diamond-nonroot-pin: some [true, false, true, false]
automatic-diamond-conflicting-pins: none
automatic-diamond-duplicate-pin: some [false, true, false, true]
automatic-inconsistent-triangle: none
automatic-consistent-triangle: some [false, false, false]
automatic-asymmetric-field: none
automatic-disconnected-partial-pin: some [true, false, false, false, false]
automatic-disconnected-covered: some [false, true, true, true, true]
automatic-disconnected-unpinned: some [false, true, false, false, false]
automatic-empty-graph: some []
automatic-isolated-pin: some [true]
automatic-contradictory-pins: none
automatic-line-eight: some [false, true, false, true, false, true, false, true]
automatic-line-eight-terminal-pin: some [true, false, true, false, true, false, true, false]
automatic-line-thirty-two: some [false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true, false, true]
automatic-components-diamond: 1
automatic-components-disconnected: 3
automatic-components-empty: 0
automatic-components-four-isolated: 4
"""
            automatic = run("run-automatic-examples", [lean, "-DwarningAsError=true", "--run", "GraphAutomaticDemo.lean"], build)
            if automatic != expected_automatic:
                raise RuntimeError("Executable automatic traversal cases differ from their checked results.")
            receipt["automatic_example_cases"] = 21

            expected_ranks = """rank-empty: n=0,m=0,c=0,cuts=1,classes=1,rank=0,quotient=0
rank-isolated: n=1,m=0,c=1,cuts=1,classes=1,rank=0,quotient=0
rank-four-isolated: n=4,m=0,c=4,cuts=1,classes=1,rank=0,quotient=0
rank-single-edge: n=2,m=1,c=1,cuts=2,classes=1,rank=1,quotient=0
rank-line-four: n=4,m=3,c=1,cuts=8,classes=1,rank=3,quotient=0
rank-triangle: n=3,m=3,c=1,cuts=4,classes=2,rank=2,quotient=1
rank-diamond: n=4,m=4,c=1,cuts=8,classes=2,rank=3,quotient=1
rank-disconnected: n=5,m=2,c=3,cuts=4,classes=1,rank=2,quotient=0
rank-complete-four: n=4,m=6,c=1,cuts=8,classes=8,rank=3,quotient=3
rank-triangle-isolated: n=4,m=3,c=2,cuts=4,classes=2,rank=2,quotient=1
rank-two-triangles: n=6,m=6,c=2,cuts=16,classes=4,rank=4,quotient=2
"""
            ranks = run("run-rank-examples", [lean, "-DwarningAsError=true", "--run", "GraphRankDemo.lean"], build)
            if ranks != expected_ranks:
                raise RuntimeError("Executable image and quotient counts differ from their checked results.")
            receipt["rank_example_cases"] = 11

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
            controls["reject-dropped-cycle-condition"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (solve triangle triangleResidual []).isSome = true := by decide
"""
            controls["reject-dropped-root-coverage"] = """import ResolutionSemantics
example : (fun _ : Fin 1 => false) = (fun _ : Fin 1 => true) := by rfl
"""
            controls["reject-dropped-integrability"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (allSolutions triangle triangleResidual).length = 2 := by decide
"""
            controls["reject-omitted-isolated-component"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (allSolutions disconnected disconnectedResidual).length = 4 := by decide
"""
            controls["reject-empty-graph-zero-count"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (allSolutions (edgeless 0) (fun _ _ => false)).length = 0 := by decide
"""
            controls["reject-count-pins-instead-of-components"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (pinnedSolutions disconnected disconnectedResidual [(0, false), (1, true)]).length = 2 := by decide
"""
            controls["reject-ignore-conflicting-pins"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (pinnedSolutions diamond diamondResidual [(0, false), (1, false)]).length = 1 := by decide
"""
            controls["reject-unpinned-isolated-component"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (pinnedSolutions disconnected disconnectedResidual [(0, false), (2, false)]).length = 1 := by decide
"""
            controls["reject-omit-nontree-edge-check"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples KRS.Graph.TraversalExamples
example : Integrates (G := triangle) triangleResidual (traversalCandidate triangleTraversal triangleResidual []) := by decide
"""
            controls["reject-ignore-nonroot-pin"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples KRS.Graph.TraversalExamples
example : (traversalSolve diamondTraversal diamondResidual [(3, false)]).map List.ofFn = some [false, true, false, true] := by decide
"""
            controls["reject-traversal-conflicting-pins"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples KRS.Graph.TraversalExamples
example : (traversalSolve (edgelessTraversal 1) (fun _ _ => false) [(0, false), (0, true)]).isSome = true := by decide
"""
            controls["reject-uncovered-exact-reference-equality"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples KRS.Graph.TraversalExamples
example : (traversalSolve diamondOtherRootTraversal diamondResidual []).map List.ofFn = (solve diamond diamondResidual []).map List.ofFn := by decide
"""
            controls["reject-zero-round-reachability"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (pathAt (boundedPaths diamond 0) 0 3).isSome = true := by decide
"""
            controls["reject-insufficient-search-rounds"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.AutomaticExamples
example : (pathAt (boundedPaths (lineGraph 4) 1) 0 3).isSome = true := by decide
"""
            controls["reject-merging-disconnected-components"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (buildTraversal disconnected).2.index.label 0 = (buildTraversal disconnected).2.index.label 4 := by decide
"""
            controls["reject-automatic-conflicting-pins"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (automaticSolve (edgeless 1) (fun _ _ => false) [(0, false), (0, true)]).isSome = true := by decide
"""
            controls["reject-phantom-empty-component"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (buildTraversal (edgeless 0)).1 = 1 := by decide
"""
            controls["reject-double-oriented-edge-count"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : edgeCount triangle = 6 := by decide
"""
            controls["reject-full-triangle-cut-rank"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : cutRank triangle = 3 := by decide
"""
            controls["reject-collapsed-triangle-quotient"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : (quotientClasses triangle).length = 1 := by decide
"""
            controls["reject-omitted-rank-components"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples KRS.Graph.CountExamples
example : cutRank disconnected = 4 := by
  rw [cut_rank_formula disconnected disconnectedIndex]
  decide
"""
            controls["reject-premature-natural-subtraction"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : quotientRank (edgeless 4) = 0 - 4 + 4 := by
  rw [KRS.Graph.RankExamples.edgeless_quotient_rank]
  decide
"""
            controls["reject-identifying-noncut-field"] = """import ResolutionSemantics
open KRS.Graph KRS.Graph.Examples
example : edgeClass triangle (fun i => i.val == 0) = edgeClass triangle (fun _ => false) := by decide
"""
            for label, source in controls.items():
                (build / "Control.lean").write_text(source, encoding="utf-8", newline="\n")
                (output / (label + ".lean.txt")).write_text(source, encoding="utf-8", newline="\n")
                run(label, [lean, "-DwarningAsError=true", "Control.lean"], build,
                    expected_zero=False,
                    diagnostic=("declaration uses 'sorry'" if label == "reject-sorry" else
                                "Tactic `decide` proved that the proposition" if label in {
                                    "reject-dropped-cycle-condition", "reject-dropped-integrability",
                                    "reject-omitted-isolated-component", "reject-empty-graph-zero-count",
                                    "reject-count-pins-instead-of-components", "reject-ignore-conflicting-pins",
                                    "reject-unpinned-isolated-component", "reject-omit-nontree-edge-check",
                                    "reject-ignore-nonroot-pin", "reject-traversal-conflicting-pins",
                                    "reject-uncovered-exact-reference-equality", "reject-zero-round-reachability",
                                    "reject-insufficient-search-rounds", "reject-merging-disconnected-components",
                                    "reject-automatic-conflicting-pins", "reject-phantom-empty-component", "reject-double-oriented-edge-count", "reject-full-triangle-cut-rank", "reject-collapsed-triangle-quotient", "reject-omitted-rank-components", "reject-premature-natural-subtraction", "reject-identifying-noncut-field"} else
                                "Tactic `rfl` failed"))
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
