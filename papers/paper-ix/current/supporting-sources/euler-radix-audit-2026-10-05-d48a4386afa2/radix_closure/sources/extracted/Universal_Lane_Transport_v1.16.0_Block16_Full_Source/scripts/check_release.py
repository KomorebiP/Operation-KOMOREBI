from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import sys

import fitz
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAX_GITHUB_FILE = 100 * 1024 * 1024
VERSION = "1.16.0"
INTEGRATED = "Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.pdf"
STANDALONE = "Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.pdf"

REQUIRED = [
    ROOT / "VERSION",
    ROOT / "README.md",
    ROOT / "CITATION.cff",
    ROOT / "LICENSE",
    ROOT / "release" / INTEGRATED,
    ROOT / "release" / STANDALONE,
    ROOT / "release" / "SHA256SUMS.txt",
    ROOT / "release" / "PDF_PREFLIGHT.json",
    ROOT / "release" / "VALIDATION.md",
    ROOT / "theorem" / "Universal_Lane_Transport_Theorem_section.tex",
    ROOT / "theorem" / "Holonomy_Twisted_Lane_Transport_section.tex",
    ROOT / "standalone" / "Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex",
    ROOT / "manuscript" / "Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.tex",
    ROOT / "manuscript" / "block15_section.tex",
    ROOT / "manuscript" / "block16_section.tex",
    ROOT / "manuscript" / "Komorebi_Theorem_Concordance_v0.3.json",
    ROOT / "manuscript" / "results" / "block15_lane_transport_validation.json",
    ROOT / "manuscript" / "results" / "block16_holonomy_lane_transport_validation.json",
    ROOT / "manuscript" / "results" / "block16_publication_audit.json",
]


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        checksum, name = line.split(None, 1)
        entries[name.strip()] = checksum
    return entries


def load_json(path: Path, failures: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        failures.append(f"invalid JSON: {path.relative_to(ROOT)}: {error}")
        return {}
    if not isinstance(value, dict):
        failures.append(f"JSON root is not an object: {path.relative_to(ROOT)}")
        return {}
    return value


def check_pdf(path: Path, expected_pages: int, title_fragment: str, failures: list[str]) -> None:
    try:
        with fitz.open(path) as document:
            if document.is_encrypted:
                failures.append(f"encrypted PDF: {path.relative_to(ROOT)}")
            if document.page_count != expected_pages:
                failures.append(
                    f"unexpected PDF page count for {path.name}: {document.page_count} != {expected_pages}"
                )
            title = str(document.metadata.get("title") or "")
            if title_fragment.lower() not in title.lower():
                failures.append(f"unexpected PDF title metadata for {path.name}: {title!r}")
            if not any(page.get_text().strip() for page in document):
                failures.append(f"PDF has no extractable text: {path.name}")
            for page in document:
                rect = page.rect
                portrait = abs(rect.width - 612) <= 1 and abs(rect.height - 792) <= 1
                landscape = abs(rect.width - 792) <= 1 and abs(rect.height - 612) <= 1
                if not (portrait or landscape):
                    failures.append(f"non-letter page in {path.name}: {rect.width} x {rect.height}")
                    break
    except Exception as error:
        failures.append(f"PDF preflight failed for {path.relative_to(ROOT)}: {error}")


def audit_markdown_links(path: Path, failures: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.replace("%20", " ")
        candidate = (path.parent / target).resolve()
        try:
            candidate.relative_to(ROOT.resolve())
        except ValueError:
            failures.append(f"Markdown link leaves repository in {path.relative_to(ROOT)}: {target}")
            continue
        if not candidate.exists():
            failures.append(f"broken Markdown link in {path.relative_to(ROOT)}: {target}")


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED:
        if not path.is_file():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    version_path = ROOT / "VERSION"
    if version_path.is_file() and version_path.read_text(encoding="utf-8").strip() != VERSION:
        failures.append("VERSION does not equal 1.16.0")

    oversized = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file() and path.stat().st_size >= MAX_GITHUB_FILE
    ]
    if oversized:
        failures.append("GitHub 100 MB file limit exceeded: " + ", ".join(map(str, oversized)))

    manifest_path = ROOT / "release" / "SHA256SUMS.txt"
    if manifest_path.is_file():
        for name, expected in parse_manifest(manifest_path).items():
            path = ROOT / "release" / name
            if not path.is_file():
                failures.append(f"release manifest entry missing: {name}")
            elif digest(path) != expected:
                failures.append(f"release hash mismatch: {name}")

    pairs = [
        (
            ROOT / "theorem" / "Universal_Lane_Transport_Theorem_section.tex",
            ROOT / "manuscript" / "block15_section.tex",
        ),
        (
            ROOT / "theorem" / "Holonomy_Twisted_Lane_Transport_section.tex",
            ROOT / "manuscript" / "block16_section.tex",
        ),
    ]
    for stable, source in pairs:
        if stable.is_file() and source.is_file() and stable.read_bytes() != source.read_bytes():
            failures.append(f"stable theorem copy differs from {source.relative_to(ROOT)}")

    b15_path = ROOT / "manuscript" / "results" / "block15_lane_transport_validation.json"
    if b15_path.is_file():
        data = load_json(b15_path, failures)
        failure_count = data.get("failure_count", len(data.get("failures", [])))
        if data.get("status") != "PASS" or failure_count != 0 or data.get("total_assertions") != 197099:
            failures.append("Block 15 validation is not PASS at 197099 assertions with zero failures")

    b16_path = ROOT / "manuscript" / "results" / "block16_holonomy_lane_transport_validation.json"
    if b16_path.is_file():
        data = load_json(b16_path, failures)
        if (
            data.get("status") != "PASS"
            or data.get("assertions") != 1344823
            or data.get("expected_assertions") != 1344823
            or data.get("failures") != []
            or not isinstance(data.get("counts"), dict)
            or sum(data.get("counts", {}).values()) != 1344823
        ):
            failures.append("Block 16 validation is not PASS at 1344823 assertions with zero failures")

    audit_path = ROOT / "manuscript" / "results" / "block16_publication_audit.json"
    if audit_path.is_file():
        data = load_json(audit_path, failures)
        if (
            data.get("status") != "PASS"
            or data.get("audit_checks") != 85
            or data.get("audit_failures") != 0
            or data.get("pdf_pages") != 239
            or data.get("validation_assertions") != 1344823
            or data.get("validation_failures") != 0
        ):
            failures.append("Block 16 publication audit is not the frozen PASS record")

    concordance_path = ROOT / "manuscript" / "Komorebi_Theorem_Concordance_v0.3.json"
    if concordance_path.is_file():
        data = load_json(concordance_path, failures)
        rows = data.get("concordance", [])
        ids = [row.get("id") for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
        if data.get("version") != "0.3" or len(ids) != 57 or "FND-17" not in ids or len(ids) != len(set(ids)):
            failures.append("theorem concordance is not synchronized through FND-17")

    cff_path = ROOT / "CITATION.cff"
    if cff_path.is_file():
        try:
            cff = yaml.safe_load(cff_path.read_text(encoding="utf-8"))
            if not isinstance(cff, dict) or str(cff.get("version")) != VERSION:
                failures.append("CITATION.cff version is not 1.16.0")
        except Exception as error:
            failures.append(f"invalid CITATION.cff YAML: {error}")

    integrated = ROOT / "release" / INTEGRATED
    standalone = ROOT / "release" / STANDALONE
    if integrated.is_file():
        check_pdf(integrated, 239, "Stratified Universality", failures)
    if standalone.is_file():
        check_pdf(standalone, 7, "Holonomy-Twisted Lane Transport", failures)

    public_text_files = [
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "GITHUB_READY_VALIDATION.md",
        ROOT / "ROADMAP.md",
        *ROOT.joinpath("docs").glob("*.md"),
        *ROOT.joinpath("release").glob("*.md"),
        *ROOT.joinpath("theorem").glob("*.md"),
        *ROOT.joinpath("standalone").glob("*.md"),
    ]
    absolute_markers = ("/mnt/data/", "C:\\Users\\")
    for path in public_text_files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in absolute_markers:
            if marker in text:
                failures.append(f"machine-specific path in {path.relative_to(ROOT)}: {marker}")
        audit_markdown_links(path, failures)

    main_source = ROOT / "manuscript" / "Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.tex"
    if main_source.is_file():
        text = main_source.read_text(encoding="utf-8")
        for token in [
            "Version 1.16.0",
            r"\input{block15_section.tex}",
            r"\input{block16_section.tex}",
            "Holonomy-Twisted",
        ]:
            if token not in text:
                failures.append(f"integrated source missing release token: {token}")

    if failures:
        print("REPOSITORY CHECK: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("REPOSITORY CHECK: PASS")
    print("- version and required release assets are synchronized")
    print("- release checksums match")
    print("- both theorem copies match their manuscript sources")
    print("- Block 15 and Block 16 exact validation records are PASS")
    print("- Block 16 publication audit is PASS")
    print("- both PDFs pass structural preflight")
    print("- CFF YAML and relative Markdown links are valid")
    print("- no file exceeds GitHub's 100 MB per-file limit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
