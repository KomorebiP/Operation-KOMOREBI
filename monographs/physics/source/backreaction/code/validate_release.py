#!/usr/bin/env python3
"""Read-only release validator for the covariant backreaction bridge.

The validator never creates, deletes, or modifies package files.  It checks the
frozen release in place, prints a machine-readable JSON report, and returns 1
when any required invariant fails.  PDF and LaTeX-log checks are optional so
the source package can be validated before a TeX toolchain is installed.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


TITLE = (
    "Covariant Refinement-Fiber Dynamics: Symmetry Classification, "
    "Constraint Closure, Backreaction, and Radiative Bounds"
)
AUTHOR = "Komorebi P."
VERSION = "1.0.0"
RELEASE_DATE = "2026-08-19"
MAIN_TEX = "Projector_Refinement_Physics_Covariant_Backreaction_Bridge.tex"
PDF_BASENAME = "Projector_Refinement_Physics_Covariant_Backreaction_Bridge.pdf"


class Audit:
    """Accumulate deterministic release checks without mutating the package."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.checks: list[dict[str, Any]] = []
        self.warnings: list[str] = []

    def check(self, check_id: str, passed: bool, detail: str) -> None:
        self.checks.append(
            {"id": check_id, "pass": bool(passed), "detail": str(detail)}
        )

    def warn(self, message: str) -> None:
        self.warnings.append(str(message))

    @property
    def failures(self) -> list[dict[str, Any]]:
        return [item for item in self.checks if not item["pass"]]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def close(a: float, b: float, *, rtol: float = 1e-10, atol: float = 0.0) -> bool:
    return math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=atol)


def strip_tex_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def path_within(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def check_release_files(audit: Audit) -> None:
    required = [
        MAIN_TEX,
        "generated_values.tex",
        "README.md",
        "CLAIM_STATUS.md",
        "RELEASE_NOTES.md",
        "REPRODUCIBILITY.md",
        "VERSION",
        "CITATION.cff",
        "RIGHTS.md",
        "requirements.txt",
        "RELEASE_MANIFEST.json",
        "SOURCE_CONTENT_SHA256SUMS.txt",
        "claim_registry.csv",
        "parameter_registry.csv",
        "build.sh",
        "build.ps1",
        "code/audit_parent_releases.py",
        "code/generate_latex_values.py",
        "code/package_release.py",
        "code/verify_covariant_backreaction.py",
        "code/validate_release.py",
        "parent/Scale_Covariant_Dark_Sector_Verification.json",
        "data/backreaction_audit.json",
        "data/parent_release_audit.json",
        "data/verification_summary.json",
        "data/continuum_universality.csv",
        "data/cross_volume_lineage.csv",
        "data/discrete_convergence.csv",
        "data/energy_saturation_curve.csv",
        "data/errata_and_broken_references.csv",
        "data/frozen_verification_ledger.csv",
        "data/python_staging_audit.csv",
        "data/radiative_scaling.csv",
        "data/verification_checks.csv",
        "source/01_audit.tex",
        "source/02_covariant_eft.tex",
        "source/03_canonical_closure.tex",
        "source/04_universality.tex",
        "source/05_backreaction.tex",
        "source/06_radiative.tex",
        "source/07_assessment.tex",
        "source/appendix_reproducibility.tex",
    ]
    figure_stems = [
        "backreaction_obstruction",
        "constraint_negative_controls",
        "fixed_prime_log_sampling",
        "general_sigma_universality",
        "radiative_uv_growth",
    ]
    required.extend(
        f"figures/{stem}.{suffix}"
        for stem in figure_stems
        for suffix in ("pdf", "png")
    )
    missing = [relative for relative in required if not (audit.root / relative).is_file()]
    empty = [
        relative
        for relative in required
        if (audit.root / relative).is_file()
        and (audit.root / relative).stat().st_size == 0
    ]
    audit.check(
        "FILES_REQUIRED",
        not missing and not empty,
        f"required={len(required)}; missing={missing}; empty={empty}",
    )

    debris = sorted(
        str(path.relative_to(audit.root))
        for path in audit.root.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
    )
    if debris:
        audit.warn("Interpreter cache artifacts are present: " + ", ".join(debris))


def check_metadata(audit: Audit) -> None:
    root = audit.root
    try:
        observed_version = (root / "VERSION").read_text(encoding="utf-8").strip()
        audit.check(
            "META_VERSION",
            observed_version == VERSION,
            f"expected={VERSION}; observed={observed_version!r}",
        )
    except Exception as exc:
        audit.check("META_VERSION", False, f"unreadable VERSION: {exc}")

    try:
        cff = (root / "CITATION.cff").read_text(encoding="utf-8")
        expected_fragments = [
            "cff-version: 1.2.0",
            f'title: "{TITLE}"',
            'type: book',
            f'version: "{VERSION}"',
            f"date-released: {RELEASE_DATE}",
            "repository-code:",
            "Operation-KOMOREBI",
        ]
        missing = [fragment for fragment in expected_fragments if fragment not in cff]
        author_ok = 'given-names: "Komorebi"' in cff and 'family-names: "P."' in cff
        audit.check(
            "META_CITATION",
            not missing and author_ok,
            f"missing_fragments={missing}; author_fields={author_ok}",
        )
    except Exception as exc:
        audit.check("META_CITATION", False, f"unreadable CITATION.cff: {exc}")

    metadata_contract = {
        "README.md": [VERSION, RELEASE_DATE, "read-only", "does not claim"],
        "CLAIM_STATUS.md": [
            "THEOREM",
            "CONDITIONAL_THEOREM",
            "CONTROLLED_DIAGNOSTIC",
            "MODEL_PROPOSITION",
            "OPEN_PROBLEM",
        ],
        "RELEASE_NOTES.md": [VERSION, "19 bridge-specific checks", "203"],
        "REPRODUCIBILITY.md": ["read-only", "parent/Scale_Covariant", "negative controls"],
        "RIGHTS.md": ["All rights reserved", "software license"],
    }
    for filename, fragments in metadata_contract.items():
        try:
            text = (root / filename).read_text(encoding="utf-8")
            missing = [fragment for fragment in fragments if fragment not in text]
            audit.check(
                f"META_{Path(filename).stem.upper()}",
                not missing,
                f"missing_fragments={missing}",
            )
        except Exception as exc:
            audit.check(
                f"META_{Path(filename).stem.upper()}",
                False,
                f"unreadable {filename}: {exc}",
            )

    required_pins = {
        "matplotlib": "3.10.8",
        "numpy": "2.3.5",
        "pypdf": "6.10.0",
        "scipy": "1.17.0",
    }
    try:
        lines = [
            line.strip()
            for line in (root / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        pins = {}
        malformed = []
        for line in lines:
            if "==" not in line:
                malformed.append(line)
                continue
            name, version = line.split("==", 1)
            pins[name.lower()] = version
        audit.check(
            "META_REQUIREMENTS",
            pins == required_pins and not malformed,
            f"expected={required_pins}; observed={pins}; malformed={malformed}",
        )
    except Exception as exc:
        audit.check("META_REQUIREMENTS", False, f"unreadable requirements: {exc}")


def resolve_input(root: Path, tex_path: Path, reference: str) -> Path | None:
    ref = Path(reference.strip())
    if ref.suffix == "":
        ref = ref.with_suffix(".tex")
    candidates = [tex_path.parent / ref, root / ref]
    for candidate in candidates:
        if path_within(root, candidate) and candidate.is_file():
            return candidate.resolve()
    return None


def resolve_graphic(root: Path, tex_path: Path, reference: str) -> Path | None:
    ref = Path(reference.strip())
    suffixes = (ref.suffix,) if ref.suffix else (".pdf", ".png", ".jpg", ".jpeg")
    raw = ref.with_suffix("") if ref.suffix else ref
    bases = [tex_path.parent, root, root / "figures"]
    for base in bases:
        for suffix in suffixes:
            candidate = base / raw.with_suffix(suffix)
            if path_within(root, candidate) and candidate.is_file():
                return candidate.resolve()
    return None


def check_tex(audit: Audit) -> None:
    root = audit.root
    tex_paths = sorted(root.rglob("*.tex"))
    unreadable: list[str] = []
    inputs_missing: list[str] = []
    graphics_missing: list[str] = []
    labels: list[str] = []
    references: list[str] = []
    placeholders: list[str] = []
    bad_controls: list[str] = []

    for path in tex_paths:
        relative = str(path.relative_to(root))
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except Exception as exc:
            unreadable.append(f"{relative}: {exc}")
            continue
        for index, value in enumerate(raw):
            if value < 32 and value not in (9, 10, 13):
                bad_controls.append(f"{relative}:byte-{index}=0x{value:02x}")
        tab_escape_tails = ("ext", "heta", "imes", "au", "op", "itle", "he")
        for line_number, line in enumerate(text.splitlines(), 1):
            if any(("\t" + tail) in line for tail in tab_escape_tails):
                bad_controls.append(f"{relative}:{line_number}:tab-like TeX escape")
        clean = strip_tex_comments(text)
        for match in re.finditer(r"\\(?:input|include)\s*\{([^}]+)\}", clean):
            ref = match.group(1)
            if resolve_input(root, path, ref) is None:
                inputs_missing.append(f"{relative}:{ref}")
        for match in re.finditer(r"\\includegraphics(?:\[[^]]*\])?\s*\{([^}]+)\}", clean):
            ref = match.group(1)
            if resolve_graphic(root, path, ref) is None:
                graphics_missing.append(f"{relative}:{ref}")
        labels.extend(re.findall(r"\\label\{([^}]+)\}", clean))
        for group in re.findall(
            r"\\(?:Cref|cref|ref|eqref|autoref|pageref)\{([^}]+)\}", clean
        ):
            references.extend(item.strip() for item in group.split(",") if item.strip())
        for match in re.finditer(r"\b(?:TODO|TBD|FIXME)\b|\?\?\?", clean):
            line_number = clean.count("\n", 0, match.start()) + 1
            placeholders.append(f"{relative}:{line_number}:{match.group(0)}")

    duplicate_labels = sorted(
        label for label, count in Counter(labels).items() if count > 1
    )
    unresolved = sorted(set(references) - set(labels))
    audit.check(
        "TEX_READABLE",
        not unreadable and bool(tex_paths),
        f"files={len(tex_paths)}; unreadable={unreadable}",
    )
    audit.check("TEX_INPUTS", not inputs_missing, f"missing={inputs_missing}")
    audit.check("TEX_GRAPHICS", not graphics_missing, f"missing={graphics_missing}")
    audit.check(
        "TEX_LABELS",
        not duplicate_labels and not unresolved,
        f"labels={len(labels)}; duplicates={duplicate_labels}; unresolved={unresolved}",
    )
    audit.check("TEX_PLACEHOLDERS", not placeholders, f"found={placeholders}")
    audit.check("TEX_CONTROL_BYTES", not bad_controls, f"found={bad_controls}")

    asset_errors: list[str] = []
    for path in sorted((root / "figures").glob("*")):
        if not path.is_file():
            continue
        header = path.read_bytes()[:8]
        if path.suffix.lower() == ".pdf" and not header.startswith(b"%PDF-"):
            asset_errors.append(f"{path.name}: invalid PDF signature")
        if path.suffix.lower() == ".png" and header != b"\x89PNG\r\n\x1a\n":
            asset_errors.append(f"{path.name}: invalid PNG signature")
    audit.check("ASSET_SIGNATURES", not asset_errors, f"errors={asset_errors}")


def check_python(audit: Audit) -> None:
    errors: list[str] = []
    paths = sorted((audit.root / "code").glob("*.py"))
    for path in paths:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    audit.check(
        "PYTHON_SYNTAX",
        not errors and len(paths) >= 5,
        f"files={len(paths)}; errors={errors}; interpreter={sys.version.split()[0]}",
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_source_manifest(audit: Audit) -> None:
    root = audit.root
    try:
        manifest = read_json(root / "RELEASE_MANIFEST.json")
        rows = manifest.get("files", [])
        errors = []
        paths = []
        for row in rows:
            relative = row.get("path", "")
            target = root / relative
            paths.append(relative)
            if (
                not relative
                or Path(relative).is_absolute()
                or ".." in Path(relative).parts
                or not target.is_file()
            ):
                errors.append(f"{relative}:missing-or-unsafe")
                continue
            if target.stat().st_size != int(row.get("size_bytes", -1)):
                errors.append(f"{relative}:size")
            if file_sha256(target) != row.get("sha256"):
                errors.append(f"{relative}:sha256")
        audit.check(
            "SOURCE_MANIFEST",
            manifest.get("schema") == "operation-komorebi.source-release.v1"
            and manifest.get("version") == VERSION
            and bool(manifest.get("claim_boundary"))
            and len(rows) >= 45
            and len(paths) == len(set(paths))
            and not errors,
            f"entries={len(rows)}; errors={errors}",
        )
    except Exception as exc:
        audit.check("SOURCE_MANIFEST", False, f"invalid manifest: {exc}")

    try:
        rows = []
        errors = []
        for line in (root / "SOURCE_CONTENT_SHA256SUMS.txt").read_text(
            encoding="utf-8"
        ).splitlines():
            if not line.strip():
                continue
            expected, relative = line.split(None, 1)
            relative = relative.lstrip(" *")
            target = root / relative
            rows.append(relative)
            if not target.is_file() or file_sha256(target) != expected:
                errors.append(relative)
        audit.check(
            "SOURCE_HASHES",
            len(rows) >= 46 and len(rows) == len(set(rows)) and not errors,
            f"entries={len(rows)}; errors={errors}",
        )
    except Exception as exc:
        audit.check("SOURCE_HASHES", False, f"invalid checksum list: {exc}")


def check_claim_registry(audit: Audit) -> None:
    path = audit.root / "claim_registry.csv"
    required = {
        "claim_id",
        "title",
        "status",
        "outcome",
        "source",
        "hypotheses",
        "evidence",
        "boundary",
    }
    allowed_status = {
        "THEOREM",
        "CONDITIONAL_THEOREM",
        "CONTROLLED_DIAGNOSTIC",
        "MODEL_PROPOSITION",
        "OPEN_PROBLEM",
    }
    try:
        fields, rows = read_csv(path)
        ids = [row.get("claim_id", "") for row in rows]
        invalid_source = []
        for row in rows:
            source = row.get("source", "")
            if (
                not source
                or Path(source).is_absolute()
                or ".." in Path(source).parts
                or not (audit.root / source).is_file()
            ):
                invalid_source.append(f"{row.get('claim_id')}:{source}")
        invalid_rows = [
            row.get("claim_id", "")
            for row in rows
            if row.get("status") not in allowed_status
            or row.get("outcome") not in {"POSITIVE", "MIXED", "NEGATIVE", "OPEN"}
            or any(not row.get(field, "").strip() for field in required)
        ]
        audit.check(
            "REGISTRY_CLAIMS",
            required.issubset(fields)
            and len(rows) == 17
            and ids == [f"BR{index:02d}" for index in range(1, 18)]
            and len(ids) == len(set(ids))
            and not invalid_source
            and not invalid_rows,
            (
                f"rows={len(rows)}; fields={fields}; invalid_rows={invalid_rows}; "
                f"invalid_source={invalid_source}"
            ),
        )
    except Exception as exc:
        audit.check("REGISTRY_CLAIMS", False, f"unreadable registry: {exc}")


def check_parameter_registry(audit: Audit) -> None:
    path = audit.root / "parameter_registry.csv"
    required = {
        "parameter_id",
        "symbol",
        "value",
        "unit",
        "role",
        "status",
        "source",
        "notes",
    }
    allowed_status = {
        "FROZEN_BENCHMARK",
        "DERIVED_FROZEN",
        "NUMERICAL_CONTROL",
        "SCAN_CONTROL",
    }
    try:
        fields, rows = read_csv(path)
        ids = [row.get("parameter_id", "") for row in rows]
        invalid_source = []
        invalid_rows = []
        for row in rows:
            source = row.get("source", "")
            source_path = Path(source)
            if (
                not source
                or source_path.is_absolute()
                or ".." in source_path.parts
                or not (audit.root / source_path).is_file()
            ):
                invalid_source.append(f"{row.get('parameter_id')}:{source}")
            if row.get("status") not in allowed_status or any(
                not row.get(field, "").strip() for field in required
            ):
                invalid_rows.append(row.get("parameter_id", ""))
        audit.check(
            "REGISTRY_PARAMETERS",
            required.issubset(fields)
            and len(rows) == 30
            and ids == [f"PAR{index:03d}" for index in range(1, 31)]
            and len(ids) == len(set(ids))
            and not invalid_source
            and not invalid_rows,
            (
                f"rows={len(rows)}; fields={fields}; invalid_rows={invalid_rows}; "
                f"invalid_source={invalid_source}"
            ),
        )
    except Exception as exc:
        audit.check("REGISTRY_PARAMETERS", False, f"unreadable registry: {exc}")


def check_json_records(audit: Audit) -> None:
    root = audit.root
    try:
        summary = read_json(root / "data/verification_summary.json")
        expected = {"checks": 19, "pass": 19, "fail": 0, "negative_controls": 5}
        observed = {key: summary.get(key) for key in expected}
        audit.check(
            "DATA_VERIFICATION_SUMMARY",
            observed == expected and bool(summary.get("claim_boundary")),
            f"expected={expected}; observed={observed}",
        )
    except Exception as exc:
        audit.check("DATA_VERIFICATION_SUMMARY", False, f"invalid JSON: {exc}")

    try:
        back = read_json(root / "data/backreaction_audit.json")
        eta = float(back["eta"])
        overdraw = float(back["unprojected_energy_over_available"])
        fields_finite = all(
            isinstance(value, (int, float)) and math.isfinite(float(value))
            for value in back.values()
        )
        audit.check(
            "DATA_BACKREACTION",
            fields_finite
            and eta > 0.0
            and eta < 1.0
            and overdraw > 1.0
            and close(eta * overdraw, 1.0, rtol=5e-12),
            f"eta={eta:.17g}; overdraw={overdraw:.17g}; product={eta * overdraw:.17g}",
        )
    except Exception as exc:
        audit.check("DATA_BACKREACTION", False, f"invalid JSON: {exc}")

    try:
        parent = read_json(root / "data/parent_release_audit.json")
        expected = {
            "volume_ii_manifest_entries": 280,
            "volume_ii_manifest_failures": 0,
            "frozen_verification_files": 10,
            "frozen_internal_pass_count": 203,
            "frozen_internal_fail_count": 0,
            "cross_volume_identical_file_pairs": 42,
            "scripts_requiring_staging": 12,
            "missing_declared_paths": 4,
            "released_volume_i_supplement_typo_detected": True,
        }
        observed = {key: parent.get(key) for key in expected}
        audit.check(
            "DATA_PARENT_AUDIT",
            observed == expected and parent.get("manifest_failures") == [],
            f"expected={expected}; observed={observed}",
        )
    except Exception as exc:
        audit.check("DATA_PARENT_AUDIT", False, f"invalid JSON: {exc}")

    try:
        frozen_parent = read_json(
            root / "parent/Scale_Covariant_Dark_Sector_Verification.json"
        )
        benchmark = frozen_parent["calibrated_benchmark"]
        parameters = frozen_parent["parameters"]
        audit.check(
            "DATA_FROZEN_PARENT",
            close(benchmark["capture_normalization"], 3.806206917830343e-21)
            and close(benchmark["A_over_mu"], 1938448601.421746)
            and parameters.get("prime") == 2
            and close(parameters.get("sigma"), 1.0)
            and frozen_parent.get("counts") == {"pass": 20, "fail": 0},
            (
                "bundled parent input has the frozen normalization, crossing rate, "
                "prime/order, and 20/0 archival counts"
            ),
        )
    except Exception as exc:
        audit.check("DATA_FROZEN_PARENT", False, f"invalid JSON: {exc}")


def check_verification_table(audit: Audit) -> None:
    try:
        fields, rows = read_csv(audit.root / "data/verification_checks.csv")
        expected_ids = {
            "COV01",
            "COV02",
            "COV03",
            "COV04",
            "ADM01",
            "ADM02",
            "ADM03",
            "ADM04",
            "UNI01",
            "UNI02",
            "UNI03",
            "UNI04",
            "QUA01",
            "BKR01",
            "BKR02",
            "BKR03",
            "BKR04",
            "CPL01",
            "CPL02",
        }
        numerical_contract = True
        numeric_errors = []
        for row in rows:
            try:
                residual = abs(float(row["residual"]))
                tolerance = float(row["tolerance"])
                expectation = row["expected"].lower()
                if expectation == "pass":
                    ok = residual <= tolerance
                elif expectation == "fail":
                    ok = residual > tolerance
                else:
                    ok = False
                if not ok:
                    numerical_contract = False
                    numeric_errors.append(row.get("id", ""))
            except Exception:
                numerical_contract = False
                numeric_errors.append(row.get("id", ""))
        negative_controls = sum(row.get("expected", "").lower() == "fail" for row in rows)
        ids = {row.get("id", "") for row in rows}
        audit.check(
            "DATA_VERIFICATION_CHECKS",
            len(rows) == 19
            and ids == expected_ids
            and all(row.get("status") == "PASS" for row in rows)
            and negative_controls == 5
            and numerical_contract,
            (
                f"rows={len(rows)}; negative_controls={negative_controls}; "
                f"ids={sorted(ids)}; numeric_errors={numeric_errors}; fields={fields}"
            ),
        )
    except Exception as exc:
        audit.check("DATA_VERIFICATION_CHECKS", False, f"invalid CSV: {exc}")


def check_provenance_tables(audit: Audit) -> None:
    root = audit.root
    try:
        fields, rows = read_csv(root / "data/cross_volume_lineage.csv")
        data_count = sum(row.get("volume_ii_path", "").startswith("data/") for row in rows)
        figure_count = sum(
            row.get("volume_ii_path", "").startswith("figures/") for row in rows
        )
        invalid = [
            str(index)
            for index, row in enumerate(rows, 1)
            if not re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))
            or int(row.get("size_bytes", "0")) <= 0
            or "not independent reproduction" not in row.get("meaning", "")
        ]
        audit.check(
            "DATA_LINEAGE",
            len(rows) == 42
            and data_count == 38
            and figure_count == 4
            and not invalid,
            (
                f"rows={len(rows)}; data={data_count}; figures={figure_count}; "
                f"invalid_rows={invalid}; fields={fields}"
            ),
        )
    except Exception as exc:
        audit.check("DATA_LINEAGE", False, f"invalid CSV: {exc}")

    try:
        _, rows = read_csv(root / "data/frozen_verification_ledger.csv")
        passes = sum(int(row["pass"]) for row in rows)
        failures = sum(int(row["fail"]) for row in rows)
        audit.check(
            "DATA_FROZEN_LEDGER",
            len(rows) == 10
            and passes == 203
            and failures == 0
            and all(row.get("status") == "FROZEN_OUTPUT_ONLY" for row in rows),
            f"rows={len(rows)}; pass={passes}; fail={failures}",
        )
    except Exception as exc:
        audit.check("DATA_FROZEN_LEDGER", False, f"invalid CSV: {exc}")

    try:
        _, rows = read_csv(root / "data/python_staging_audit.csv")
        staged = sum(row.get("requires_staging") == "True" for row in rows)
        audit.check(
            "DATA_STAGING_AUDIT",
            len(rows) == 14
            and staged == 12
            and all(row.get("syntax") == "PASS" for row in rows)
            and all(
                row.get("status")
                == ("REQUIRES_STAGING" if row.get("requires_staging") == "True" else "STATIC_ONLY")
                for row in rows
            ),
            f"rows={len(rows)}; requiring_staging={staged}",
        )
    except Exception as exc:
        audit.check("DATA_STAGING_AUDIT", False, f"invalid CSV: {exc}")

    try:
        _, rows = read_csv(root / "data/errata_and_broken_references.csv")
        statuses = Counter(row.get("status", "") for row in rows)
        audit.check(
            "DATA_ERRATA",
            len(rows) == 5
            and statuses == Counter({"MISSING": 4, "RELEASED_TYPO": 1})
            and all(row.get("boundary", "") for row in rows),
            f"rows={len(rows)}; statuses={dict(statuses)}",
        )
    except Exception as exc:
        audit.check("DATA_ERRATA", False, f"invalid CSV: {exc}")


def check_numeric_tables(audit: Audit) -> None:
    contracts = {
        "continuum_universality.csv": (
            90,
            {
                "sigma",
                "alpha",
                "c_number",
                "c_rest",
                "c_energy",
                "c_pressure",
                "w",
                "rest_fraction",
                "mean_mass_over_a",
                "rest_peak_over_a",
            },
        ),
        "discrete_convergence.csv": (
            39,
            {
                "prime",
                "sigma",
                "lambda_over_a",
                "levels",
                "energy",
                "expected_energy",
                "relative_energy_error",
                "rest",
                "expected_rest",
                "relative_rest_error",
                "w",
                "rest_fraction",
            },
        ),
        "energy_saturation_curve.csv": (
            120,
            {
                "lambda_over_a",
                "a_over_mu",
                "energy_over_available",
                "w",
                "rest_fraction",
                "levels",
            },
        ),
        "radiative_scaling.csv": (
            72,
            {
                "sigma",
                "depth",
                "m_uv_over_lambda",
                "weighted_m4_sum",
                "fitted_exponent",
                "expected_exponent",
            },
        ),
    }
    errors: list[str] = []
    observed: dict[str, int] = {}
    for filename, (expected_rows, numeric_columns) in contracts.items():
        try:
            fields, rows = read_csv(audit.root / "data" / filename)
            observed[filename] = len(rows)
            if len(rows) != expected_rows or not numeric_columns.issubset(fields):
                errors.append(
                    f"{filename}: rows={len(rows)} fields={fields}"
                )
                continue
            for row_index, row in enumerate(rows, 2):
                for column in numeric_columns:
                    try:
                        value = float(row[column])
                        if not math.isfinite(value):
                            raise ValueError("not finite")
                    except Exception as exc:
                        errors.append(f"{filename}:{row_index}:{column}:{exc}")
        except Exception as exc:
            errors.append(f"{filename}: {exc}")
    audit.check("DATA_NUMERIC_TABLES", not errors, f"rows={observed}; errors={errors}")


def tex_number(value: str) -> float:
    compact = value.replace(" ", "")
    match = re.fullmatch(r"([+-]?[0-9]+(?:\.[0-9]+)?)\\times10\^\{([+-]?[0-9]+)\}", compact)
    if match:
        return float(match.group(1)) * 10.0 ** int(match.group(2))
    return float(compact)


def check_generated_values(audit: Audit) -> None:
    try:
        text = (audit.root / "generated_values.tex").read_text(encoding="utf-8")
        macros: dict[str, str] = {}
        for line in text.splitlines():
            match = re.fullmatch(
                r"\\newcommand\{\\([^}]+)\}\{(.*)\}", line.strip()
            )
            if match:
                macros[match.group(1)] = match.group(2)
        required_names = {
            "BridgeEta",
            "BridgeOverdraw",
            "BridgeContinuumSlow",
            "BridgeContinuumOverdraw",
            "BridgeContinuumA",
            "BridgeContinuumX",
            "BridgeContinuumExponent",
            "BridgeDiscreteA",
            "BridgeDiscreteX",
            "BridgeDiscreteW",
            "BridgeDiscreteRest",
            "BridgeDiscreteMeanMass",
            "BridgePeakCoupling",
            "BridgeLowestCoupling",
            "BridgeLambdaBound",
            "BridgeEnergyLambdaBound",
            "BridgePeakAtEnergyBound",
            "BridgeLowestAtEnergyBound",
            "BridgeSpectralResidual",
            "BridgeAliasResidual",
            "BridgeFiniteDifferenceResidual",
            "BridgeMissingGradientResidual",
            "BridgeWardNegativeResidual",
            "BridgeManifestEntries",
            "BridgeFrozenPasses",
            "BridgeLineageData",
            "BridgeLineageFigures",
            "BridgeStagingScripts",
            "BridgeMissingPaths",
        }
        fixed = {
            "BridgeManifestEntries": "280",
            "BridgeFrozenPasses": "203",
            "BridgeLineageData": "38",
            "BridgeLineageFigures": "4",
            "BridgeStagingScripts": "12",
            "BridgeMissingPaths": "4",
        }
        back = read_json(audit.root / "data/backreaction_audit.json")
        numeric_ok = close(tex_number(macros["BridgeEta"]), back["eta"], rtol=5e-11)
        numeric_ok = numeric_ok and close(
            tex_number(macros["BridgeOverdraw"]),
            back["unprojected_energy_over_available"],
            rtol=5e-11,
        )
        audit.check(
            "DATA_GENERATED_VALUES",
            required_names.issubset(macros)
            and all(macros.get(key) == value for key, value in fixed.items())
            and numeric_ok,
            (
                f"macros={len(macros)}; missing={sorted(required_names - set(macros))}; "
                f"fixed={ {key: macros.get(key) for key in fixed} }; numeric_ok={numeric_ok}"
            ),
        )
    except Exception as exc:
        audit.check("DATA_GENERATED_VALUES", False, f"invalid macro file: {exc}")


def check_pdf(audit: Audit, pdf_path: Path) -> None:
    if not pdf_path.is_file():
        audit.check("PDF_FILE", False, f"missing PDF: {pdf_path}")
        return
    try:
        from pypdf import PdfReader
    except Exception as exc:
        audit.check("PDF_IMPORT", False, f"pypdf unavailable: {exc}")
        return
    try:
        reader = PdfReader(str(pdf_path))
        metadata = reader.metadata
        page_count = len(reader.pages)
        title = metadata.title if metadata else None
        author = metadata.author if metadata else None
        geometry_errors = []
        for index, page in enumerate(reader.pages, 1):
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            if not (close(width, 594.0, atol=1.0) and close(height, 774.0, atol=1.0)):
                geometry_errors.append(
                    f"page {index}: {width:.3f} x {height:.3f} pt"
                )
        try:
            outline_count = len(reader.outline)
        except Exception:
            outline_count = 0
        audit.check(
            "PDF_STRUCTURE",
            not reader.is_encrypted
            and page_count > 0
            and title == TITLE
            and author == AUTHOR
            and outline_count > 0
            and not geometry_errors,
            (
                f"path={pdf_path}; pages={page_count}; encrypted={reader.is_encrypted}; "
                f"title={title!r}; author={author!r}; outline={outline_count}; "
                f"geometry_errors={geometry_errors}"
            ),
        )
    except Exception as exc:
        audit.check("PDF_STRUCTURE", False, f"invalid PDF: {exc}")


def check_latex_log(audit: Audit, log_path: Path) -> None:
    if not log_path.is_file():
        audit.check("LATEX_LOG", False, f"missing log: {log_path}")
        return
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
        fatal_patterns = {
            "fatal error": r"Fatal error occurred|Emergency stop|^! ",
            "undefined references": r"undefined references?|undefined citations?",
            "duplicate labels": r"multiply defined|There were multiply-defined labels",
            "rerun required": r"Rerun to get cross-references right|Label\(s\) may have changed",
            "overfull box": r"Overfull \\[hv]box",
        }
        found = {
            name: len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
            for name, pattern in fatal_patterns.items()
        }
        underfull = len(re.findall(r"Underfull \\[hv]box", text))
        generic_warnings = len(re.findall(r"(?:LaTeX|Package .+?) Warning:", text))
        if underfull:
            audit.warn(f"LaTeX log contains {underfull} underfull box warning(s).")
        if generic_warnings:
            audit.warn(f"LaTeX log contains {generic_warnings} package/LaTeX warning(s).")
        audit.check(
            "LATEX_LOG",
            "Output written on" in text and not any(found.values()),
            f"path={log_path}; blocking={found}; underfull={underfull}; warnings={generic_warnings}",
        )
    except Exception as exc:
        audit.check("LATEX_LOG", False, f"unreadable log: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="package root (default: parent of this script's code directory)",
    )
    parser.add_argument("--pdf", type=Path, help="compiled PDF to validate")
    parser.add_argument("--log", type=Path, help="final LaTeX log to validate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    audit = Audit(root)

    audit.check("ROOT", root.is_dir(), f"root={root}")
    if root.is_dir():
        check_release_files(audit)
        check_metadata(audit)
        check_tex(audit)
        check_python(audit)
        check_source_manifest(audit)
        check_claim_registry(audit)
        check_parameter_registry(audit)
        check_json_records(audit)
        check_verification_table(audit)
        check_provenance_tables(audit)
        check_numeric_tables(audit)
        check_generated_values(audit)
    if args.pdf is not None:
        check_pdf(audit, args.pdf.resolve())
    if args.log is not None:
        check_latex_log(audit, args.log.resolve())

    report = {
        "schema": "operation-komorebi.release-validation.v1",
        "package": TITLE,
        "version": VERSION,
        "root": str(root),
        "read_only": True,
        "status": "PASS" if not audit.failures else "FAIL",
        "summary": {
            "checks": len(audit.checks),
            "pass": len(audit.checks) - len(audit.failures),
            "fail": len(audit.failures),
            "warnings": len(audit.warnings),
        },
        "checks": audit.checks,
        "failures": audit.failures,
        "warnings": audit.warnings,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if audit.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
