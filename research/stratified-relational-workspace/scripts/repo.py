#!/usr/bin/env python3
"""Cross-platform build, verification, and release packaging for SRWT."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
MONOGRAPH_DIR = ROOT / "monograph"
TEX = MONOGRAPH_DIR / "Stratified_Relational_Workspace_Theory.tex"
COMMITTED_PDF = MONOGRAPH_DIR / "Stratified_Relational_Workspace_Theory.pdf"
BUILD = ROOT / "build"
DIST = ROOT / "dist"
RESULTS = ROOT / "verification" / "results"
MANIFEST = json.loads((ROOT / "metadata" / "manifest.json").read_text(encoding="utf-8"))
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PDF_NAME = "Stratified_Relational_Workspace_Theory.pdf"


def run(cmd: list[str], *, cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    return subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def require_tool(name: str, strict: bool) -> bool:
    if shutil.which(name):
        return True
    if strict:
        raise RuntimeError(f"Required tool not found: {name}")
    print(f"warning: optional verification tool not found: {name}")
    return False


def clean() -> None:
    for path in (BUILD, DIST, RESULTS):
        if path.exists():
            shutil.rmtree(path)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / ".gitkeep").touch()
    print("clean=PASS")


def build() -> Path:
    require_tool("latexmk", True)
    BUILD.mkdir(parents=True, exist_ok=True)
    run(
        [
            "latexmk",
            "-r",
            str(ROOT / "latexmkrc"),
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-outdir={BUILD}",
            TEX.name,
        ],
        cwd=MONOGRAPH_DIR,
    )
    output = BUILD / PDF_NAME
    if not output.exists():
        raise RuntimeError(f"Expected build output was not created: {output}")
    print(f"build=PASS pdf={output}")
    return output


def check_log() -> None:
    log = BUILD / "Stratified_Relational_Workspace_Theory.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    forbidden = {
        "LaTeX Warning": r"LaTeX Warning",
        "undefined references": r"undefined references|Reference .* undefined",
        "undefined citations": r"Citation .* undefined",
        "multiply defined labels": r"multiply defined|Label .* multiply defined",
        "overfull boxes": r"Overfull \\hbox|Overfull \\vbox",
        "underfull boxes": r"Underfull \\hbox|Underfull \\vbox",
    }
    found = [name for name, pattern in forbidden.items() if re.search(pattern, text, re.IGNORECASE)]
    if found:
        raise RuntimeError("LaTeX log failed hygiene checks: " + ", ".join(found))
    print("latex_log=PASS")


def pdfinfo(path: Path, strict: bool) -> dict[str, str]:
    if not require_tool("pdfinfo", strict):
        return {}
    proc = run(["pdfinfo", str(path)], capture=True)
    info: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
    return info


def check_fonts(path: Path, strict: bool) -> None:
    if not require_tool("pdffonts", strict):
        return
    proc = run(["pdffonts", str(path)], capture=True)
    rows = proc.stdout.splitlines()[2:]
    bad = []
    for row in rows:
        if not row.strip():
            continue
        fields = re.split(r"\s{2,}", row.strip())
        if len(fields) < 4 or fields[3].split()[0].lower() != "yes":
            bad.append(row)
    if bad:
        raise RuntimeError("Unembedded fonts detected:\n" + "\n".join(bad))
    print(f"font_embedding=PASS fonts={len(rows)}")


def extracted_text_hash(path: Path, strict: bool) -> str | None:
    if not require_tool("pdftotext", strict):
        return None
    target = BUILD / (path.stem + ".txt")
    run(["pdftotext", "-layout", str(path), str(target)])
    text = target.read_text(encoding="utf-8", errors="replace")
    normalized = "\n".join(line.rstrip() for line in text.replace("\f", "\n").splitlines()).strip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def check_pdf(built: Path, strict: bool) -> None:
    expected_pages = str(MANIFEST["expected"]["pages"])
    for path in (COMMITTED_PDF, built):
        info = pdfinfo(path, strict)
        if info:
            if info.get("Pages") != expected_pages:
                raise RuntimeError(f"{path.name}: expected {expected_pages} pages, found {info.get('Pages')}")
            if info.get("Encrypted", "no").lower().startswith("yes"):
                raise RuntimeError(f"{path.name}: PDF is encrypted")
    check_fonts(built, strict)
    committed_hash = extracted_text_hash(COMMITTED_PDF, strict)
    built_hash = extracted_text_hash(built, strict)
    if committed_hash and built_hash and committed_hash != built_hash:
        raise RuntimeError("Rebuilt and committed PDFs differ after text extraction")
    print("pdf_integrity=PASS")


def check_citation() -> None:
    data = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    required = {"cff-version", "message", "title", "type", "authors", "version", "date-released"}
    missing = sorted(required - set(data))
    if missing:
        raise RuntimeError("CITATION.cff missing keys: " + ", ".join(missing))
    if str(data["cff-version"]) != "1.2.0":
        raise RuntimeError("CITATION.cff must use CFF 1.2.0")
    if str(data["version"]) != VERSION:
        raise RuntimeError("CITATION.cff version differs from VERSION")
    preferred = data.get("preferred-citation")
    if not isinstance(preferred, dict) or preferred.get("type") != "book":
        raise RuntimeError("CITATION.cff must contain a book preferred-citation")
    print("citation_metadata=PASS")


def check_markdown_links() -> None:
    failures: list[str] = []
    link_re = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if any(part in {"build", "dist", ".git"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for raw in link_re.findall(text):
            target = raw.strip().split()[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)} -> {target}")
    if failures:
        raise RuntimeError("Broken relative Markdown links:\n" + "\n".join(failures))
    print("markdown_links=PASS")


def check_repo_hygiene() -> None:
    required = [
        "README.md", "CITATION.cff", "CITATION.bib", "LICENSE", "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md", "SECURITY.md", "CHANGELOG.md", "ERRATA.md", "VERSION",
        ".github/workflows/ci.yml", ".github/workflows/release.yml",
        "monograph/Stratified_Relational_Workspace_Theory.tex",
        "monograph/Stratified_Relational_Workspace_Theory.pdf",
        "audits/priority_register.csv", "audits/statement_index.csv",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise RuntimeError("Required repository files missing: " + ", ".join(missing))
    for marker in ("OWNER" + "/REPO", "USER" + "NAME", "CHANGE" + "ME"):
        hits = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or any(part in {"build", "dist", ".git"} for part in path.parts):
                continue
            if path.suffix.lower() in {".pdf", ".zip", ".gz"}:
                continue
            if marker in path.read_text(encoding="utf-8", errors="ignore"):
                hits.append(str(path.relative_to(ROOT)))
        if hits:
            raise RuntimeError(f"Placeholder {marker!r} found in: {', '.join(hits)}")
    check_markdown_links()
    print("repository_hygiene=PASS")


def run_math_checks() -> None:
    run([sys.executable, str(ROOT / "verification" / "run_all.py")])
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    if not summary.get("all_checks_passed"):
        raise RuntimeError("One or more mathematical regression checks failed")
    print("mathematical_checks=PASS")


def verify(strict: bool) -> Path:
    check_repo_hygiene()
    check_citation()
    run([sys.executable, str(ROOT / "scripts" / "split_monograph.py"), "--check"])
    run_math_checks()
    built = build()
    check_log()
    check_pdf(built, strict)
    report = {
        "version": VERSION,
        "strict": strict,
        "all_checks_passed": True,
        "built_pdf": str(built.relative_to(ROOT)),
        "expected_pages": MANIFEST["expected"]["pages"],
    }
    (RESULTS / "repository_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return built


def should_archive(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if not path.is_file():
        return False
    if rel.parts[0] in {"build", "dist", ".git"}:
        return False
    if rel.parts[:2] == ("verification", "results"):
        return False
    return True


def package(strict: bool) -> None:
    built = verify(strict)
    DIST.mkdir(parents=True, exist_ok=True)
    versioned_pdf = DIST / f"Stratified_Relational_Workspace_Theory-v{VERSION}.pdf"
    shutil.copy2(built, versioned_pdf)
    root_name = f"stratified-relational-workspace-theory-v{VERSION}"
    zip_path = DIST / f"{root_name}-source.zip"
    tar_path = DIST / f"{root_name}-source.tar.gz"
    files = sorted(path for path in ROOT.rglob("*") if should_archive(path))
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            zf.write(path, Path(root_name) / path.relative_to(ROOT))
    with tarfile.open(tar_path, "w:gz") as tf:
        for path in files:
            tf.add(path, arcname=Path(root_name) / path.relative_to(ROOT), recursive=False)
    assets = [versioned_pdf, zip_path, tar_path]
    sums = []
    for asset in assets:
        h = hashlib.sha256(asset.read_bytes()).hexdigest()
        sums.append(f"{h}  {asset.name}")
    (DIST / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"package=PASS assets={len(assets) + 1}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "test", "verify", "package", "clean"])
    parser.add_argument("--strict", action="store_true", help="require all external PDF-audit tools")
    args = parser.parse_args()
    try:
        if args.command == "build":
            build()
        elif args.command == "test":
            run_math_checks()
        elif args.command == "verify":
            verify(args.strict)
        elif args.command == "package":
            package(args.strict)
        elif args.command == "clean":
            clean()
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
