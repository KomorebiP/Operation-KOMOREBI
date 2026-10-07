#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
MODE="${1:-}"

case "$MODE" in
  ""|--full) ;;
  *)
    printf 'Usage: %s [--full]\n' "$0" >&2
    exit 2
    ;;
esac

for required_command in sha256sum python3; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' "$required_command" >&2
    exit 1
  fi
done

python3 - "$PACKAGE_ROOT" <<'PY'
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys


root = Path(sys.argv[1]).resolve()


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


manifest_path = root / "SHA256SUMS.txt"
if not manifest_path.is_file() or not manifest_path.stat().st_size:
    fail("missing or empty SHA256SUMS.txt")

excluded_parts = {".git", ".lake", "__pycache__"}
excluded_suffixes = {
    ".aux",
    ".fdb_latexmk",
    ".fls",
    ".ilean",
    ".log",
    ".olean",
    ".out",
    ".pyc",
    ".synctex.gz",
    ".toc",
    ".trace",
    ".zip",
}


def excluded(relative_name: str) -> bool:
    pure = PurePosixPath(relative_name)
    return any(part in excluded_parts for part in pure.parts) or any(
        relative_name.endswith(suffix) for suffix in excluded_suffixes
    )


symlinks = sorted(
    path.relative_to(root).as_posix()
    for path in root.rglob("*")
    if path.is_symlink() and not excluded(path.relative_to(root).as_posix())
)
if symlinks:
    fail(f"release contains symbolic links: {symlinks}")

actual_files = sorted(
    path.relative_to(root).as_posix()
    for path in root.rglob("*")
    if path.is_file()
    and path != manifest_path
    and not excluded(path.relative_to(root).as_posix())
)

manifest_entries: list[tuple[str, str]] = []
manifest_line_re = re.compile(r"([0-9a-f]{64})  ([^\x00-\x1f\x7f]+)")
for line_number, line in enumerate(
    manifest_path.read_text(encoding="utf-8").splitlines(), start=1
):
    match = manifest_line_re.fullmatch(line)
    if match is None:
        fail(f"malformed checksum entry on line {line_number}")
    digest, relative_name = match.groups()
    pure = PurePosixPath(relative_name)
    if (
        pure.is_absolute()
        or relative_name.startswith("./")
        or "\\" in relative_name
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        fail(f"unsafe checksum path on line {line_number}: {relative_name!r}")
    manifest_entries.append((digest, relative_name))

listed_files = [name for _, name in manifest_entries]
if listed_files != sorted(listed_files):
    fail("checksum paths are not in bytewise sorted order")
if len(listed_files) != len(set(listed_files)):
    fail("checksum manifest contains duplicate paths")
if "SHA256SUMS.txt" in listed_files:
    fail("checksum manifest must not list itself")
if listed_files != actual_files:
    missing = sorted(set(actual_files) - set(listed_files))
    extra = sorted(set(listed_files) - set(actual_files))
    fail(f"checksum manifest/file-set mismatch; missing={missing}; extra={extra}")

core_files = {
    "CITATION.cff",
    "LICENSE_STATUS.md",
    "README.md",
    "RELEASE.json",
    "RELEASE_NOTES.md",
    "VERIFY.sh",
    "formalization/lean/KomorebiPaperIII.lean",
    "formalization/lean/KomorebiPaperIII/CoordinateNaturality.lean",
    "formalization/lean/KomorebiPaperIII/EdgeExtensions.lean",
    "formalization/lean/KomorebiPaperIII/EdgeOperators.lean",
    "formalization/lean/KomorebiPaperIII/HolonomyBlocks.lean",
    "formalization/lean/KomorebiPaperIII/KernelAudit.lean",
    "formalization/lean/KomorebiPaperIII/NonlinearObstructions.lean",
    "formalization/lean/KomorebiPaperIII/ReversibleConnections.lean",
    "formalization/lean/KomorebiPaperIII/Transport.lean",
    "formalization/lean/INHERITED_DEPENDENCY_MANIFEST_v1.2.1.md",
    "formalization/lean/LEAN_THEOREM_MAP_v1.0.1.md",
    "formalization/lean/README.md",
    "formalization/lean/lake-manifest.json",
    "formalization/lean/lakefile.toml",
    "formalization/lean/lean-toolchain",
    "formalization/lean/scripts/verify_theorem_map.py",
    "kernel_audit_output.txt",
    "paper/Projector_Resolved_Seed_Calculus_III.pdf",
    "paper/Projector_Resolved_Seed_Calculus_III.tex",
    "paper/figures/holonomy_obstruction_blocks.png",
    "paper/figures/transport_vs_connection.png",
    "paper/figures/typed_edge_walks.png",
    "paper/requirements.txt",
    "paper/scripts/generate_figures.py",
    "provenance/Lean_Completion_Contract.md",
    "provenance/VERIFICATION_REPORT.md",
    "scripts/package_release.py",
}
missing_core = sorted(core_files - set(actual_files))
if missing_core:
    fail(f"release is missing required files: {missing_core}")

placeholder_re = re.compile(rb"__" + rb"FINAL_[A-Z0-9_]+__")
private_markers = (
    b"/" + b"workspace/",
    b"/" + b"dev/shm/",
    b"/" + b"root/",
)
for relative_name in actual_files:
    data = (root / relative_name).read_bytes()
    placeholder_match = placeholder_re.search(data)
    if placeholder_match is not None:
        fail(
            f"unresolved release sentinel in {relative_name}: "
            f"{placeholder_match.group().decode('ascii')}"
        )
    for marker in private_markers:
        if marker in data:
            fail(f"private build path found in {relative_name}")

release_path = root / "RELEASE.json"
try:
    release = json.loads(release_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    fail(f"invalid RELEASE.json: {error}")

cff_path = root / "CITATION.cff"
cff_text = cff_path.read_text(encoding="utf-8")
top_level_cff = dict(
    re.findall(r"(?m)^([a-z][a-z0-9-]*):(?:[ \t]*(.*))?$", cff_text)
)
for key, expected in {
    "cff-version": "1.2.0",
    "type": "software",
    "version": "1.0.1",
    "date-released": "2026-09-03",
}.items():
    if top_level_cff.get(key) != expected:
        fail(f"CITATION.cff top-level field {key!r} must equal {expected!r}")
if re.search(
    r"(?ms)^preferred-citation:\s*$.*?^  type: article\s*$.*?"
    r"^  version: 1\.0\.1\s*$.*?^  status: preprint\s*$",
    cff_text,
) is None:
    fail("CITATION.cff lacks the expected article preferred-citation record")

for key, expected in {
    "schema_version": "1.0",
    "author": "Komorebi P.",
    "release_version": "1.0.1",
    "release_date": "2026-09-03",
    "package_type": "source_lean_pdf",
}.items():
    if release.get(key) != expected:
        fail(f"RELEASE.json field {key!r} must equal {expected!r}")

verification = release.get("verification")
if not isinstance(verification, dict) or verification.get("status") != "passed":
    fail("RELEASE.json verification.status must be 'passed'")
formalization = verification.get("formalization")
manuscript = verification.get("manuscript")
figures = verification.get("figures")
archive = verification.get("archive")
if not all(isinstance(value, dict) for value in (formalization, manuscript, figures, archive)):
    fail("RELEASE.json verification sections are malformed")

for key in (
    "build_jobs",
    "theorem_map_rows",
    "mapped_declarations",
    "mapped_theorems",
    "mapped_constructions",
    "supporting_only_theorems",
    "explicit_kernel_audit_targets",
    "manuscript_status_invocations",
    "manuscript_status_references",
    "manuscript_status_unique",
    "inherited_status_invocations",
    "inherited_status_references",
    "inherited_status_unique",
    "namespace_audit_declarations",
    "namespace_theorem_declarations",
):
    value = formalization.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        fail(f"RELEASE.json formalization.{key} must be a nonnegative integer")
if formalization.get("build_status") != "passed":
    fail("RELEASE.json formalization.build_status must be 'passed'")
if formalization.get("warnings_as_errors") is not True:
    fail("RELEASE.json must record warnings_as_errors=true")

for key in ("pdf_pages", "pdftex_passes"):
    value = manuscript.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        fail(f"RELEASE.json manuscript.{key} must be a positive integer")
for key in ("compiled_pdf_included", "latex_log_clean", "full_document_render_inspected"):
    if manuscript.get(key) is not True:
        fail(f"RELEASE.json manuscript.{key} must be true")
if manuscript.get("pdf_structural_checks") != "passed":
    fail("RELEASE.json manuscript.pdf_structural_checks must be 'passed'")
if figures.get("generated_figures") != 3 or figures.get("deterministic_regeneration") is not True:
    fail("RELEASE.json must record three deterministically regenerated figures")
for key in ("clean_extraction", "deterministic_rebuild"):
    if archive.get(key) is not True:
        fail(f"RELEASE.json archive.{key} must be true")
for key in ("package_files", "checksum_manifest_entries"):
    value = archive.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        fail(f"RELEASE.json archive.{key} must be a positive integer")
if archive["package_files"] != len(actual_files) + 1:
    fail("RELEASE.json package_files does not match the complete release file set")
if archive["checksum_manifest_entries"] != len(manifest_entries):
    fail("RELEASE.json checksum_manifest_entries does not match SHA256SUMS.txt")

map_matches = sorted(root.rglob("LEAN_THEOREM_MAP_*.md"))
expected_map = root / "formalization/lean/LEAN_THEOREM_MAP_v1.0.1.md"
if map_matches != [expected_map]:
    fail(f"expected exactly one v1.0.1 theorem map; found {map_matches}")

gate_path = root / "formalization/lean/scripts/verify_theorem_map.py"
spec = importlib.util.spec_from_file_location("paper3_release_map_gate", gate_path)
if spec is None or spec.loader is None:
    fail("unable to load theorem-map checker")
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

try:
    row_ids, mapped_names = gate._parse_map(expected_map)
    audit_targets = gate._parse_audit(
        root / "formalization/lean/KomorebiPaperIII/KernelAudit.lean"
    )
    (
        status_invocations,
        status_targets,
        inherited_invocations,
        inherited_targets,
    ) = gate._parse_status_targets(root / "paper")
    inherited_manifest_targets = gate._parse_inherited_manifest(
        root
        / "formalization/lean/INHERITED_DEPENDENCY_MANIFEST_v1.2.1.md"
    )
except Exception as error:
    fail(f"static theorem-map/audit parsing failed: {error}")

computed_metrics = {
    "theorem_map_rows": len(row_ids),
    "mapped_declarations": len(mapped_names),
    "explicit_kernel_audit_targets": len(audit_targets),
    "supporting_only_theorems": len(set(audit_targets) - set(mapped_names)),
    "manuscript_status_invocations": status_invocations,
    "manuscript_status_references": len(status_targets),
    "manuscript_status_unique": len(set(status_targets)),
    "inherited_status_invocations": inherited_invocations,
    "inherited_status_references": len(inherited_targets),
    "inherited_status_unique": len(set(inherited_targets)),
}
for key, actual in computed_metrics.items():
    if formalization.get(key) != actual:
        fail(
            f"RELEASE.json formalization.{key}={formalization.get(key)!r} "
            f"but the release sources give {actual}"
        )
if not set(mapped_names) <= set(audit_targets):
    fail("one or more theorem-map declarations lack explicit kernel-audit coverage")
if not set(status_targets) <= set(mapped_names):
    fail("one or more manuscript Lean status targets are absent from the theorem map")
if set(inherited_targets) != set(inherited_manifest_targets):
    fail("inherited manuscript targets disagree with the frozen dependency manifest")
if any(name.startswith("Komorebi.PaperIII.") for name in inherited_targets):
    fail("an inherited manuscript target incorrectly points into Paper III")

transcript_path = root / "kernel_audit_output.txt"
transcript = transcript_path.read_text(encoding="utf-8")
transcript_targets = re.findall(
    r"^'(Komorebi\.PaperIII\.[^']+)' (?:does not depend|depends on axioms)",
    transcript,
    flags=re.MULTILINE,
)
if transcript_targets != audit_targets:
    fail("saved kernel-audit target order does not match KernelAudit.lean")
pass_re = re.compile(
    r"^FAIL-CLOSED PAPER III v1\.0\.1 KERNEL AUDIT PASS: "
    r"(\d+) declarations \((\d+) theoremInfo\); "
    r"(\d+) explicit mapped targets; allowed axioms only: "
    r"propext, Classical\.choice, Quot\.sound$",
    flags=re.MULTILINE,
)
pass_records = [tuple(map(int, values)) for values in pass_re.findall(transcript)]
expected_pass_record = (
    formalization["namespace_audit_declarations"],
    formalization["namespace_theorem_declarations"],
    formalization["explicit_kernel_audit_targets"],
)
if pass_records != [expected_pass_record]:
    fail("saved transcript lacks the unique expected fail-closed namespace pass")

tex_path = root / "paper/Projector_Resolved_Seed_Calculus_III.tex"
tex_source = tex_path.read_text(encoding="utf-8")
if re.search(r"\\statusmanuscript\s*\{", tex_source):
    fail("manuscript still contains an active manuscript-only status")
for stale in (
    "Version 0.1.0-dev",
    "LEAN_THEOREM_MAP_v0.1.0-dev",
    "\\statusdefinition{",
):
    if stale in tex_source:
        fail(f"manuscript contains stale development marker: {stale}")
lakefile = (root / "formalization/lean/lakefile.toml").read_text(encoding="utf-8")
if not re.search(r'(?m)^version\s*=\s*"1\.0\.1"\s*$', lakefile):
    fail("lakefile.toml is not version 1.0.1")

for lean_path in sorted((root / "formalization/lean").rglob("*.lean")):
    active = gate._strip_lean_comments(lean_path.read_text(encoding="utf-8"))
    if re.search(r"\b(?:sorry|admit|sorryAx|native_decide|ofReduceBool)\b", active):
        fail(f"forbidden proof shortcut found in {lean_path.relative_to(root)}")
    if re.search(
        r"(?m)^\s*(?:axiom|axioms|constant|constants|opaque|unsafe|partial|extern|implemented_by)\b",
        active,
    ):
        fail(f"forbidden declaration form found in {lean_path.relative_to(root)}")

artifact_paths = {
    "pdf_sha256": "paper/Projector_Resolved_Seed_Calculus_III.pdf",
    "tex_sha256": "paper/Projector_Resolved_Seed_Calculus_III.tex",
    "theorem_map_sha256": "formalization/lean/LEAN_THEOREM_MAP_v1.0.1.md",
    "kernel_audit_sha256": "kernel_audit_output.txt",
    "typed_edge_walks_sha256": "paper/figures/typed_edge_walks.png",
    "transport_vs_connection_sha256": "paper/figures/transport_vs_connection.png",
    "holonomy_obstruction_blocks_sha256": "paper/figures/holonomy_obstruction_blocks.png",
}
hashes = release.get("artifact_hashes")
if not isinstance(hashes, dict):
    fail("RELEASE.json artifact_hashes is malformed")
for key, relative_name in artifact_paths.items():
    recorded = hashes.get(key)
    if not isinstance(recorded, str) or re.fullmatch(r"[0-9a-f]{64}", recorded) is None:
        fail(f"RELEASE.json artifact_hashes.{key} is not a lowercase SHA-256")
    actual = sha256(root / relative_name)
    if recorded != actual:
        fail(f"artifact hash mismatch for {relative_name}")

pdf_path = root / artifact_paths["pdf_sha256"]
if not pdf_path.read_bytes().startswith(b"%PDF-"):
    fail("final manuscript is not recognizably a PDF")

print(
    "Static release checks passed: "
    f"{len(actual_files) + 1} files, {len(row_ids)} map rows, "
    f"{len(mapped_names)} mapped declarations, {len(audit_targets)} explicit "
    f"audit targets, and {formalization['namespace_audit_declarations']} "
    "fail-closed namespace declarations."
)
PY

(
  cd "$PACKAGE_ROOT"
  sha256sum --check --strict SHA256SUMS.txt
)

if [[ "$MODE" != "--full" ]]; then
  printf '%s\n' 'All Paper III v1.0.1 offline release-integrity checks passed.'
  exit 0
fi

for required_command in lake pdflatex pdfinfo pdffonts gs; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    printf 'ERROR: --full requires command: %s\n' "$required_command" >&2
    exit 1
  fi
done
if ! python3 -c 'import matplotlib' >/dev/null 2>&1; then
  printf '%s\n' 'ERROR: --full requires the Python package Matplotlib.' >&2
  exit 1
fi

VERIFY_TMP="$(mktemp -d "${TMPDIR:-/tmp}/prsc-paper3-verify.XXXXXX")"
trap 'rm -rf -- "$VERIFY_TMP"' EXIT HUP INT TERM
VERIFY_COPY="$VERIFY_TMP/release"
mkdir -p "$VERIFY_COPY"
cp -a "$PACKAGE_ROOT/." "$VERIFY_COPY/"

(
  cd "$VERIFY_COPY/paper"
  python3 scripts/generate_figures.py
)

python3 - "$VERIFY_COPY" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
release = json.loads((root / "RELEASE.json").read_text(encoding="utf-8"))
hashes = release["artifact_hashes"]
figure_paths = {
    "typed_edge_walks_sha256": root / "paper/figures/typed_edge_walks.png",
    "transport_vs_connection_sha256": root / "paper/figures/transport_vs_connection.png",
    "holonomy_obstruction_blocks_sha256": root / "paper/figures/holonomy_obstruction_blocks.png",
}
for key, path in figure_paths.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != hashes[key]:
        raise SystemExit(f"ERROR: regenerated figure differs: {path.name}")
print("Deterministic figure regeneration passed.")
PY

(
  cd "$VERIFY_COPY/formalization/lean"
  lake --wfail build
  python3 scripts/verify_theorem_map.py
  lake env lean -E warning KomorebiPaperIII/KernelAudit.lean
)

PDF_PASSES="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["verification"]["manuscript"]["pdftex_passes"])' "$VERIFY_COPY/RELEASE.json")"
export SOURCE_DATE_EPOCH=1788393600
export FORCE_SOURCE_DATE=1
export TZ=UTC
(
  cd "$VERIFY_COPY/paper"
  rm -f -- Projector_Resolved_Seed_Calculus_III.aux \
    Projector_Resolved_Seed_Calculus_III.log \
    Projector_Resolved_Seed_Calculus_III.out \
    Projector_Resolved_Seed_Calculus_III.pdf \
    Projector_Resolved_Seed_Calculus_III.toc
  for ((pass = 1; pass <= PDF_PASSES; pass++)); do
    pdflatex -interaction=nonstopmode -halt-on-error \
      Projector_Resolved_Seed_Calculus_III.tex \
      >"$VERIFY_TMP/pdflatex-pass-$pass.txt"
  done
  if grep -Eq 'LaTeX Warning|Package .* Warning|Overfull \\hbox|Underfull \\hbox|Overfull \\vbox|Underfull \\vbox' \
      Projector_Resolved_Seed_Calculus_III.log; then
    printf '%s\n' 'ERROR: final LaTeX log contains a warning or bad box.' >&2
    exit 1
  fi
)

python3 - "$VERIFY_COPY" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
release = json.loads((root / "RELEASE.json").read_text(encoding="utf-8"))
pdf = root / "paper/Projector_Resolved_Seed_Calculus_III.pdf"
actual = hashlib.sha256(pdf.read_bytes()).hexdigest()
expected = release["artifact_hashes"]["pdf_sha256"]
if actual != expected:
    raise SystemExit(
        "ERROR: clean pdfTeX rebuild differs from the released PDF; "
        f"expected {expected}, found {actual}"
    )
print("Deterministic PDF rebuild passed.")
PY

PDF_PATH="$VERIFY_COPY/paper/Projector_Resolved_Seed_Calculus_III.pdf"
EXPECTED_PAGES="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["verification"]["manuscript"]["pdf_pages"])' "$VERIFY_COPY/RELEASE.json")"
ACTUAL_PAGES="$(pdfinfo "$PDF_PATH" | awk '/^Pages:/ {print $2}')"
if [[ "$ACTUAL_PAGES" != "$EXPECTED_PAGES" ]]; then
  printf 'ERROR: PDF page count mismatch; expected %s, found %s.\n' \
    "$EXPECTED_PAGES" "$ACTUAL_PAGES" >&2
  exit 1
fi
if pdffonts "$PDF_PATH" | grep -Fq 'Type 3'; then
  printf '%s\n' 'ERROR: PDF contains a Type 3 font.' >&2
  exit 1
fi
gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=nullpage "$PDF_PATH"

printf '%s\n' 'All Paper III v1.0.1 full clean-room verification checks passed.'
