"""Source and driver checks, explicitly separate from Lean compilation."""
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument("--formal", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
formal = a.formal.resolve()
driver = formal / "scripts/verify.py"
completed = subprocess.run([sys.executable, str(driver), "--plan-only"], capture_output=True, text=True, check=True)
plan = json.loads(completed.stdout)
actual = {path.stem for path in (formal / "Komorebi/SufficientResolution").glob("*.lean")}
order = plan["topological_modules"]
assert set(order) == actual and len(order) == len(actual) == 93
positions = {name: i for i, name in enumerate(order)}
edges = 0
for path in (formal / "Komorebi/SufficientResolution").glob("*.lean"):
    for line in path.read_text().splitlines():
        if line.startswith("import Komorebi.SufficientResolution."):
            dependency = line.removeprefix("import Komorebi.SufficientResolution.").strip()
            assert dependency in positions and positions[dependency] < positions[path.stem]
            edges += 1
assert plan["theorem_declarations"] == 998 and plan["named_declarations"] == 1159
registry_tree = ast.parse(driver.read_text())
registry_function = next(node for node in registry_tree.body if isinstance(node, ast.FunctionDef) and node.name == "registry")
registry_namespace = {"ROOT": formal, "re": re}
exec(compile(ast.Module(body=[registry_function], type_ignores=[]), str(driver), "exec"), registry_namespace)
registry_names = {row["name"] for row in registry_namespace["registry"]()}
audit_names = [line.removeprefix("#print axioms ").strip() for line in (formal / "AxiomAudit.lean").read_text().splitlines() if line.startswith("#print axioms ")]
assert len(audit_names) == len(set(audit_names)) == 1159 and set(audit_names) == registry_names

preservation = json.loads((formal.parent / "verification/PRODUCTION_SOURCE_PRESERVATION.json").read_text())
for entry in preservation["files"]:
    assert hashlib.sha256((formal / entry["file"]).read_bytes()).hexdigest() == entry["sha256"]

# Execute only the discovery function AST in temporary synthetic source trees.
# No Lean statements, archived runtime commands, or proof kernels are executed.
tree = ast.parse(driver.read_text())
function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "discover_modules")
code = compile(ast.Module(body=[function], type_ignores=[]), str(driver), "exec")
controls = []
with TemporaryDirectory() as temporary:
    root = Path(temporary)
    sources = root / "Komorebi/SufficientResolution"
    sources.mkdir(parents=True)
    namespace = {"ROOT": root, "re": re}
    exec(code, namespace)
    discover = namespace["discover_modules"]
    (sources / "A.lean").write_text("import Komorebi.SufficientResolution.Missing\n")
    try:
        discover()
    except ValueError as exc:
        assert "Missing production import" in str(exc)
        controls.append("missing dependency rejected")
    else:
        raise AssertionError("Missing dependency accepted")
    (sources / "A.lean").write_text("import Komorebi.SufficientResolution.B\n")
    (sources / "B.lean").write_text("import Komorebi.SufficientResolution.A\n")
    try:
        discover()
    except ValueError as exc:
        assert "cycle" in str(exc)
        controls.append("dependency cycle rejected")
    else:
        raise AssertionError("Dependency cycle accepted")

shell = formal / "verify_low_memory.sh"
subprocess.run(["bash", "-n", str(shell)], check=True)
missing = subprocess.run(["bash", str(shell), str(formal / "runtime-deliberately-absent")], capture_output=True, text=True)
assert missing.returncode == 2 and "Missing pinned portable runtime" in missing.stderr
controls.append("missing runtime rejected before Lean execution")
result = {"status": "PASS", "source_module_count": len(actual),
          "project_import_edges_checked": edges, "production_hashes_checked": len(preservation["files"]),
          "theorem_declarations": plan["theorem_declarations"], "named_declarations": plan["named_declarations"],
          "root_axiom_audit_command_count": len(audit_names), "root_axiom_audit_registry_coverage": "PASS",
          "controls": controls, "shell_syntax": "PASS", "source_plan": plan,
          "boundary": "Source identity, dependency discovery and driver guards only; no fresh Lean compilation, axiom audit or kernel replay."}
a.output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: value for key, value in result.items() if key != "source_plan"}, indent=2))
