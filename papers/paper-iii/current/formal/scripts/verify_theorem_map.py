#!/usr/bin/env python3
"""Fail-closed consistency gate for the Paper III v1.0.1 Lean theorem map."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


MAP_FILENAME = "LEAN_THEOREM_MAP_v1.0.1.md"
INHERITED_MANIFEST_FILENAME = "INHERITED_DEPENDENCY_MANIFEST_v1.2.1.md"
PAPERS_I_II_BUNDLE_FILENAME = (
    "Projector_Resolved_Seed_Calculus_Papers_I_II_v1.2.1_Complete_Bundle.zip"
)
PAPERS_I_II_BUNDLE_SHA256 = (
    "a20cf9353f0e882834d31e665dfd819a04e43fa606d402309be63e3b94447052"
)
EXPECTED_ROW_IDS = list(range(1, 42))
EXPECTED_MAPPED_TOTAL = 143
EXPECTED_MAPPED_THEOREMS = 88
EXPECTED_MAPPED_CONSTRUCTIONS = 55
EXPECTED_AUDIT_TOTAL = 143
EXPECTED_SUPPORTING_ONLY_TOTAL = 0
EXPECTED_SUPPORTING_ONLY_THEOREMS = 0
EXPECTED_STATUS_INVOCATIONS = 42
EXPECTED_STATUS_REFERENCES = 99
EXPECTED_STATUS_UNIQUE = 99
EXPECTED_INHERITED_INVOCATIONS = 6
EXPECTED_INHERITED_REFERENCES = 14
EXPECTED_INHERITED_UNIQUE = (
    "Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support",
    "Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates",
    "Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_self",
    "Komorebi.PaperII.NestedRefinement.coarsenCoordinates_refineCoordinates",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_coarsenCoordinates",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_comp",
    "Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv_trans",
    "Komorebi.PaperII.NestedRefinement.coordinateOperator_comp",
    "Komorebi.PaperII.NestedRefinement.coordinateOperator_naturality",
    "Komorebi.PacketNaturalityCompletion.Packets.transferBlock_pow_eq_packetPathSum",
)
EXPECTED_INHERITED_STATUS_TARGETS = (
    "Komorebi.PacketNaturalityCompletion.Reachability.algebraicOrbitHull_le_reachable_support",
    "Komorebi.PacketNaturalityCompletion.Reachability.unreachable_nonzero_packet_obstruction",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates",
    "Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_self",
    "Komorebi.PaperII.NestedRefinement.coarsenCoordinates_refineCoordinates",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_coarsenCoordinates",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_comp",
    "Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv_trans",
    "Komorebi.PaperII.NestedRefinement.coordinateOperator_comp",
    "Komorebi.PaperII.NestedRefinement.coordinateOperator_naturality",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_comp",
    "Komorebi.PaperII.NestedRefinement.refineCoordinates_self",
    "Komorebi.PacketNaturalityCompletion.Packets.transferBlock_pow_eq_packetPathSum",
)
MAP_HEADER = [
    "ID",
    "Manuscript result or construction",
    "Lean declaration",
    "Status and boundary",
]
LEAN_NAME_RE = re.compile(
    r"Komorebi(?:\.[A-Za-z_][A-Za-z0-9_']*)+\Z"
)
AUDIT_DIRECTIVE_RE = re.compile(
    r"^\s*#print\s+axioms\s+"
    r"(Komorebi(?:\.[A-Za-z_][A-Za-z0-9_']*)+)\s*$"
)
STATUS_MACRO_RE = re.compile(r"\\statusleanthree\b")
INHERITED_STATUS_MACRO_RE = re.compile(r"\\statusleanprior\b")


class GateError(RuntimeError):
    """A release-gate invariant was not satisfied."""


def _duplicates(items: list[str]) -> list[str]:
    return sorted(name for name, count in Counter(items).items() if count > 1)


def _split_markdown_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _parse_map(path: Path) -> tuple[list[int], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_indexes = [
        index
        for index, line in enumerate(lines)
        if _split_markdown_row(line) == MAP_HEADER
    ]
    if len(header_indexes) != 1:
        raise GateError(
            f"expected exactly one authoritative four-column table in {path.name}; "
            f"found {len(header_indexes)}"
        )

    header_index = header_indexes[0]
    if header_index + 1 >= len(lines):
        raise GateError("the authoritative table has no Markdown separator row")
    separator = _split_markdown_row(lines[header_index + 1])
    if separator is None or len(separator) != len(MAP_HEADER):
        raise GateError("the authoritative table has a malformed separator row")
    if any(re.fullmatch(r":?-{3,}:?", cell) is None for cell in separator):
        raise GateError("the authoritative table has a malformed separator row")

    row_ids: list[int] = []
    mapped_names: list[str] = []
    line_index = header_index + 2
    while line_index < len(lines) and lines[line_index].lstrip().startswith("|"):
        cells = _split_markdown_row(lines[line_index])
        line_number = line_index + 1
        if cells is None or len(cells) != len(MAP_HEADER):
            raise GateError(f"malformed theorem-map row at line {line_number}")
        try:
            row_id = int(cells[0])
        except ValueError as error:
            raise GateError(
                f"non-integer theorem-map row ID at line {line_number}: {cells[0]!r}"
            ) from error

        declaration_parts = [part.strip() for part in cells[2].split(",")]
        if not declaration_parts or any(not part for part in declaration_parts):
            raise GateError(
                f"empty declaration entry in theorem-map row {row_id}"
            )
        for part in declaration_parts:
            match = re.fullmatch(r"`([^`]+)`", part)
            if match is None:
                raise GateError(
                    f"row {row_id} declaration entries must be individually backticked: "
                    f"{part!r}"
                )
            name = match.group(1)
            if LEAN_NAME_RE.fullmatch(name) is None:
                raise GateError(
                    f"row {row_id} has a non-fully-qualified Komorebi declaration: "
                    f"{name!r}"
                )
            mapped_names.append(name)
        row_ids.append(row_id)
        line_index += 1

    if row_ids != EXPECTED_ROW_IDS:
        raise GateError(
            "theorem-map row IDs must be exactly 1..41 in order; "
            f"found {row_ids}"
        )
    duplicate_names = _duplicates(mapped_names)
    if duplicate_names:
        raise GateError(
            "mapped declaration names must be unique; duplicates: "
            + ", ".join(duplicate_names)
        )
    return row_ids, mapped_names


def _parse_inherited_manifest(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    if source.count(PAPERS_I_II_BUNDLE_FILENAME) != 1:
        raise GateError(
            "inherited manifest does not name the frozen Papers I-II bundle"
        )
    if source.count(PAPERS_I_II_BUNDLE_SHA256) != 1:
        raise GateError(
            "inherited manifest does not contain the exact bundle SHA-256"
        )

    row_re = re.compile(
        r"^\|\s*(\d+)\s*\|\s*`"
        r"(Komorebi(?:\.[A-Za-z_][A-Za-z0-9_']*)+)`\s*\|",
        re.MULTILINE,
    )
    rows = [(int(row_id), name) for row_id, name in row_re.findall(source)]
    if [row_id for row_id, _ in rows] != list(range(1, 13)):
        raise GateError(
            "inherited-manifest row IDs must be exactly 1..12 in order"
        )
    names = [name for _, name in rows]
    if tuple(names) != EXPECTED_INHERITED_UNIQUE:
        raise GateError(
            "inherited dependency manifest changed from the frozen target set"
        )
    if any(name.startswith("Komorebi.PaperIII.") for name in names):
        raise GateError(
            "inherited dependency manifest contains a Paper III target"
        )
    return names


def _strip_lean_comments(source: str) -> str:
    """Remove nested Lean comments while retaining line boundaries."""

    output: list[str] = []
    index = 0
    block_depth = 0
    in_string = False
    escaped = False
    while index < len(source):
        char = source[index]
        pair = source[index : index + 2]

        if block_depth:
            if pair == "/-":
                block_depth += 1
                output.extend("  ")
                index += 2
            elif pair == "-/":
                block_depth -= 1
                output.extend("  ")
                index += 2
            else:
                output.append("\n" if char == "\n" else " ")
                index += 1
            continue

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if pair == "/-":
            block_depth = 1
            output.extend("  ")
            index += 2
        elif pair == "--":
            while index < len(source) and source[index] != "\n":
                output.append(" ")
                index += 1
        else:
            output.append(char)
            if char == '"':
                in_string = True
            index += 1

    if block_depth:
        raise GateError("KernelAudit.lean contains an unterminated block comment")
    if in_string:
        raise GateError("KernelAudit.lean contains an unterminated string literal")
    return "".join(output)


def _parse_audit(path: Path) -> list[str]:
    active_source = _strip_lean_comments(path.read_text(encoding="utf-8"))
    targets: list[str] = []
    for line_number, line in enumerate(active_source.splitlines(), start=1):
        if "#print" not in line:
            continue
        match = AUDIT_DIRECTIVE_RE.fullmatch(line)
        if match is None:
            raise GateError(
                f"malformed or unsupported audit directive at "
                f"{path.name}:{line_number}: {line.strip()!r}"
            )
        targets.append(match.group(1))

    if not targets:
        raise GateError(f"{path.name} contains no active #print axioms directives")
    duplicate_targets = _duplicates(targets)
    if duplicate_targets:
        raise GateError(
            "KernelAudit.lean has duplicate #print axioms targets: "
            + ", ".join(duplicate_targets)
        )
    return targets


def _strip_tex_comments(source: str) -> str:
    output: list[str] = []
    for line in source.splitlines(keepends=True):
        comment_index: int | None = None
        for index, char in enumerate(line):
            if char != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                comment_index = index
                break
        if comment_index is None:
            output.append(line)
        else:
            output.append(line[:comment_index])
            if line.endswith("\n"):
                output.append("\n")
    return "".join(output)


def _status_payloads(
    source: str, source_name: str, macro_re: re.Pattern[str], macro_name: str
) -> list[str]:
    payloads: list[str] = []
    for match in macro_re.finditer(source):
        cursor = match.end()
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1
        # The occurrence in \newcommand{\statusleanthree}[1] is not an invocation.
        if cursor >= len(source) or source[cursor] != "{":
            continue

        start = cursor + 1
        cursor = start
        depth = 1
        while cursor < len(source) and depth:
            char = source[cursor]
            if char in "{}":
                backslashes = 0
                previous = cursor - 1
                while previous >= 0 and source[previous] == "\\":
                    backslashes += 1
                    previous -= 1
                if backslashes % 2 == 0:
                    depth += 1 if char == "{" else -1
            cursor += 1
        if depth:
            line_number = source.count("\n", 0, match.start()) + 1
            raise GateError(
                f"unterminated \\{macro_name} invocation at "
                f"{source_name}:{line_number}"
            )
        payload = source[start : cursor - 1]
        if "{" in payload or "}" in payload:
            raise GateError(
                f"nested braces are not permitted in \\{macro_name} payloads "
                f"in {source_name}"
            )
        payloads.append(payload)
    return payloads


def _payload_targets(
    payloads: list[str], tex_path: Path, macro_name: str
) -> list[str]:
    targets: list[str] = []
    for payload in payloads:
        parts = [part.strip() for part in payload.split(";")]
        if not parts or any(not part for part in parts):
            raise GateError(
                f"empty declaration in \\{macro_name} payload in {tex_path}"
            )
        for name in parts:
            if LEAN_NAME_RE.fullmatch(name) is None:
                raise GateError(
                    f"non-fully-qualified Komorebi declaration in "
                    f"\\{macro_name} payload in {tex_path}: {name!r}"
                )
            targets.append(name)
    return targets


def _parse_status_targets(
    paper_dir: Path,
) -> tuple[int, list[str], int, list[str]]:
    tex_files = sorted(path for path in paper_dir.rglob("*.tex") if path.is_file())
    if not tex_files:
        raise GateError(f"no manuscript .tex files found under {paper_dir}")

    targets: list[str] = []
    inherited_targets: list[str] = []
    invocation_count = 0
    inherited_invocation_count = 0
    forbidden_invocations: list[str] = []
    for tex_path in tex_files:
        source = _strip_tex_comments(tex_path.read_text(encoding="utf-8"))
        for forbidden_name in ("statusmanuscript", "statusdefinition"):
            forbidden_re = re.compile(r"\\" + forbidden_name + r"\b")
            count = len(
                _status_payloads(
                    source, str(tex_path), forbidden_re, forbidden_name
                )
            )
            if count:
                forbidden_invocations.append(
                    f"{tex_path}:{forbidden_name}={count}"
                )

        payloads = _status_payloads(
            source, str(tex_path), STATUS_MACRO_RE, "statusleanthree"
        )
        inherited_payloads = _status_payloads(
            source,
            str(tex_path),
            INHERITED_STATUS_MACRO_RE,
            "statusleanprior",
        )
        invocation_count += len(payloads)
        inherited_invocation_count += len(inherited_payloads)
        targets.extend(_payload_targets(payloads, tex_path, "statusleanthree"))
        inherited_targets.extend(
            _payload_targets(inherited_payloads, tex_path, "statusleanprior")
        )

    if forbidden_invocations:
        raise GateError(
            "final manuscript contains provisional status invocations: "
            + ", ".join(forbidden_invocations)
        )
    if invocation_count != EXPECTED_STATUS_INVOCATIONS:
        raise GateError(
            f"manuscript must contain exactly {EXPECTED_STATUS_INVOCATIONS} "
            f"\\statusleanthree invocations; found {invocation_count}"
        )
    if inherited_invocation_count != EXPECTED_INHERITED_INVOCATIONS:
        raise GateError(
            f"manuscript must contain exactly {EXPECTED_INHERITED_INVOCATIONS} "
            f"\\statusleanprior invocations; found {inherited_invocation_count}"
        )
    return invocation_count, targets, inherited_invocation_count, inherited_targets


def _compiled_declaration_kinds(
    lean_root: Path, declaration_names: list[str]
) -> dict[str, str]:
    lake = shutil.which("lake")
    if lake is None:
        raise GateError("lake is not available on PATH")

    with tempfile.TemporaryDirectory(
        prefix=".verify_theorem_map_", dir=lean_root
    ) as temporary_directory:
        check_file = Path(temporary_directory) / "MappedDeclarations.lean"
        source = [
            "import KomorebiPaperIII",
            "",
            "-- Generated by scripts/verify_theorem_map.py; do not edit.",
            "open Lean Elab Command",
            "",
            "run_cmd do",
            "  let env ← getEnv",
            "  for name in #[",
        ]
        source.extend(
            f"    `{name}{',' if index + 1 < len(declaration_names) else ''}"
            for index, name in enumerate(declaration_names)
        )
        source.extend(
            [
                "  ] do",
                "    match env.find? name with",
                "    | none => throwError \"compiled declaration not found: {name}\"",
                "    | some info =>",
                "        let kind :=",
                "          match info with",
                "          | .thmInfo _ => \"theorem\"",
                "          | _ => \"construction\"",
                "        logInfo m!\"THEOREM_MAP_GATE_META|{kind}|{name}|END\"",
            ]
        )
        check_file.write_text("\n".join(source) + "\n", encoding="utf-8")
        try:
            result = subprocess.run(
                [lake, "env", "lean", str(check_file)],
                cwd=lean_root,
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired as error:
            raise GateError(
                "compiled-environment declaration check timed out after 300 seconds"
            ) from error
        if result.returncode != 0:
            diagnostics = (result.stdout + result.stderr).strip()
            if len(diagnostics) > 12000:
                diagnostics = diagnostics[-12000:]
                diagnostics = "[diagnostics truncated to final 12000 characters]\n" + diagnostics
            raise GateError(
                "compiled Lean declaration metadata check failed:\n" + diagnostics
            )

        output = result.stdout + result.stderr
        metadata_re = re.compile(
            r"THEOREM_MAP_GATE_META\|(theorem|construction)\|"
            r"(Komorebi(?:\.[A-Za-z_][A-Za-z0-9_']*)+)\|END"
        )
        records = metadata_re.findall(output)
        recorded_names = [name for _, name in records]
        duplicate_records = _duplicates(recorded_names)
        if duplicate_records:
            raise GateError(
                "compiled metadata emitted duplicate records for: "
                + ", ".join(duplicate_records)
            )
        missing_records = sorted(set(declaration_names) - set(recorded_names))
        unexpected_records = sorted(set(recorded_names) - set(declaration_names))
        if missing_records or unexpected_records:
            details: list[str] = []
            if missing_records:
                details.append("missing=" + ", ".join(missing_records))
            if unexpected_records:
                details.append("unexpected=" + ", ".join(unexpected_records))
            raise GateError(
                "compiled metadata output was incomplete or contaminated: "
                + "; ".join(details)
            )
        return {name: kind for kind, name in records}


def main() -> int:
    script_path = Path(__file__).resolve()
    lean_root = script_path.parent.parent
    project_root = lean_root.parent.parent
    paper_root = project_root / "paper"

    map_matches = sorted(project_root.rglob("LEAN_THEOREM_MAP_v*.md"))
    expected_map_path = lean_root / MAP_FILENAME
    if map_matches != [expected_map_path]:
        raise GateError(
            f"expected only {expected_map_path} under {project_root}; "
            f"found {map_matches}"
        )
    map_path = map_matches[0]
    row_ids, mapped_names = _parse_map(map_path)
    if len(mapped_names) != EXPECTED_MAPPED_TOTAL:
        raise GateError(
            f"authoritative map must contain exactly {EXPECTED_MAPPED_TOTAL} unique "
            f"declarations; found {len(mapped_names)}"
        )

    inherited_manifest_path = lean_root / INHERITED_MANIFEST_FILENAME
    inherited_manifest_names = _parse_inherited_manifest(
        inherited_manifest_path
    )

    audit_path = lean_root / "KomorebiPaperIII" / "KernelAudit.lean"
    if not audit_path.is_file():
        raise GateError(f"missing kernel audit: {audit_path}")
    audit_targets = _parse_audit(audit_path)
    if len(audit_targets) != EXPECTED_AUDIT_TOTAL:
        raise GateError(
            f"KernelAudit.lean must contain exactly {EXPECTED_AUDIT_TOTAL} unique "
            f"#print axioms targets; found {len(audit_targets)}"
        )

    if audit_targets != mapped_names:
        missing_from_audit = sorted(set(mapped_names) - set(audit_targets))
        unexpected_audit = sorted(set(audit_targets) - set(mapped_names))
        details = []
        if missing_from_audit:
            details.append("missing=" + ", ".join(missing_from_audit))
        if unexpected_audit:
            details.append("unexpected=" + ", ".join(unexpected_audit))
        if not details:
            details.append("same set but different order")
        raise GateError(
            "audit targets must exactly match the ordered theorem map: "
            + "; ".join(details)
        )

    (
        status_invocations,
        status_targets,
        inherited_invocations,
        inherited_targets,
    ) = _parse_status_targets(paper_root)
    if len(status_targets) != EXPECTED_STATUS_REFERENCES:
        raise GateError(
            f"manuscript must contain exactly {EXPECTED_STATUS_REFERENCES} "
            f"\\statusleanthree declaration references; found {len(status_targets)}"
        )
    if len(set(status_targets)) != EXPECTED_STATUS_UNIQUE:
        raise GateError(
            f"manuscript must contain exactly {EXPECTED_STATUS_UNIQUE} unique "
            f"\\statusleanthree targets; found {len(set(status_targets))}"
        )
    missing_from_map = sorted(set(status_targets) - set(mapped_names))
    if missing_from_map:
        raise GateError(
            "manuscript \\statusleanthree targets absent from the authoritative map: "
            + ", ".join(missing_from_map)
        )
    if len(inherited_targets) != EXPECTED_INHERITED_REFERENCES:
        raise GateError(
            f"manuscript must contain exactly {EXPECTED_INHERITED_REFERENCES} "
            f"\\statusleanprior references; found {len(inherited_targets)}"
        )
    if tuple(inherited_targets) != EXPECTED_INHERITED_STATUS_TARGETS:
        raise GateError(
            "ordered inherited status surface changed from the frozen manifest use"
        )
    if set(inherited_targets) != set(EXPECTED_INHERITED_UNIQUE):
        raise GateError(
            "inherited status targets do not equal the frozen Papers I-II set"
        )
    if set(inherited_targets) != set(inherited_manifest_names):
        raise GateError(
            "inherited status targets disagree with the dependency manifest"
        )
    if any(name.startswith("Komorebi.PaperIII.") for name in inherited_targets):
        raise GateError(
            "an inherited status target accidentally points into Paper III"
        )

    supporting_only = [
        name for name in audit_targets if name not in set(mapped_names)
    ]
    if len(supporting_only) != EXPECTED_SUPPORTING_ONLY_TOTAL:
        raise GateError(
            f"audit must contain exactly {EXPECTED_SUPPORTING_ONLY_TOTAL} "
            f"supporting-only declarations; found {len(supporting_only)}"
        )

    declaration_kinds = _compiled_declaration_kinds(lean_root, audit_targets)
    mapped_theorems = sum(
        declaration_kinds[name] == "theorem" for name in mapped_names
    )
    mapped_constructions = sum(
        declaration_kinds[name] == "construction" for name in mapped_names
    )
    if (
        mapped_theorems != EXPECTED_MAPPED_THEOREMS
        or mapped_constructions != EXPECTED_MAPPED_CONSTRUCTIONS
    ):
        raise GateError(
            "compiled mapped-declaration classification must be exactly "
            f"{EXPECTED_MAPPED_THEOREMS} theoremInfo / "
            f"{EXPECTED_MAPPED_CONSTRUCTIONS} non-theorem constructions; found "
            f"{mapped_theorems} / {mapped_constructions}"
        )

    supporting_theorems = sum(
        declaration_kinds[name] == "theorem" for name in supporting_only
    )
    if supporting_theorems != EXPECTED_SUPPORTING_ONLY_THEOREMS:
        supporting_constructions = sorted(
            name
            for name in supporting_only
            if declaration_kinds[name] != "theorem"
        )
        raise GateError(
            "all supporting-only audit targets must be theoremInfo declarations; "
            "non-theorems: " + ", ".join(supporting_constructions)
        )

    print(
        "PASS theorem-map gate: "
        f"rows={len(row_ids)} "
        f"mapped={len(mapped_names)} "
        f"(theorem={mapped_theorems} construction={mapped_constructions}) "
        f"audit={len(audit_targets)} "
        f"supporting_only={len(supporting_only)} "
        f"(theorem={supporting_theorems}) "
        f"status_invocations={status_invocations} "
        f"status_references={len(status_targets)} "
        f"status_unique={len(set(status_targets))} "
        f"inherited_invocations={inherited_invocations} "
        f"inherited_references={len(inherited_targets)} "
        f"inherited_unique={len(set(inherited_targets))}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GateError as error:
        print(f"FAIL theorem-map gate: {error}", file=sys.stderr)
        raise SystemExit(1)
