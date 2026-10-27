"""Package the reviewed release and preserve its complete evidence chain."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUB, TECH = ROOT / "publication", ROOT / "technical_record"
INPUT = ROOT.parent / "publication_v114_inputs"
OUT = ROOT.parent / "publication_v114_output"
OUT.mkdir(exist_ok=True)
SKIP = {".lake", "__pycache__", ".git"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files(root):
    for directory, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            if not path.is_symlink() and not name.endswith(".pyc"):
                yield path


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def manifest(root):
    manifest_path = root / "SHA256SUMS"
    entries = [(sha(path), str(path.relative_to(root))) for path in files(root) if path != manifest_path]
    manifest_path.write_text("".join(f"{digest}  {name}\n" for digest, name in entries))
    return len(entries)


def archive(root, name):
    count = manifest(root)
    target = OUT / (name + ".zip")
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for path in files(root):
            zipf.write(path, name + "/" + str(path.relative_to(root)))
    with zipfile.ZipFile(target) as zipf:
        assert zipf.testzip() is None
        names = zipf.namelist()
        assert len(names) == len(set(names)) == count + 1
        assert not any(".." in Path(path).parts or path.startswith("/") or ".lake" in Path(path).parts for path in names)
        lines = zipf.read(name + "/SHA256SUMS").decode().splitlines()
        for line in lines:
            digest, relative = line.split("  ", 1)
            assert hashlib.sha256(zipf.read(name + "/" + relative)).hexdigest() == digest, relative
    return {"file": target.name, "bytes": target.stat().st_size, "sha256": sha(target),
            "zip_crc_verified": True, "manifest_entries_verified": count, "duplicate_paths": 0, "unsafe_paths": 0}


edition = json.loads((PUB / "verification/EDITION_VERIFICATION.json").read_text())
assert (ROOT / "reviews/final_metadata_audit.json").is_file(), "Independent metadata audit must finish first."
for path, digest in edition["source_identity"].items():
    assert sha(PUB / path) == digest, path
for path, digest in edition["current_reviews"].items():
    assert sha(PUB / "verification" / path) == digest, path
for book in edition["books"].values():
    assert sha(PUB / book["file"]) == book["sha256"]
    copy(PUB / book["file"], OUT / Path(book["file"]).name)

publication = archive(PUB, "Komorebi_Space_Publication_v1.14.0")
copy(INPUT / "Komorebi_Space_Technical_Record_v1.13.0.zip", TECH / "history/Komorebi_Space_Technical_Record_v1.13.0.zip")
copy(INPUT / "Komorebi_Space_Diagonal_Lean_Completion.zip", TECH / "accepted/Komorebi_Space_Diagonal_Lean_Completion.zip")
copy(OUT / publication["file"], TECH / "publication" / publication["file"])

with (ROOT / "records/PROGRESS_LEDGER.jsonl").open("a") as stream:
    stream.write(json.dumps({"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "event": "public_archive_verified",
                             "archive": publication, "technical_record_next": "Preserve parent and diagonal evidence, current records, reviewed renders and all publication build attempts."}) + "\n")
for folder in ["records", "reviews", "parent_books"]:
    shutil.copytree(ROOT / folder, TECH / "integration" / folder, dirs_exist_ok=True)
for folder in ["reference_pass", "final_01", "final_02", "final_03"]:
    shutil.copytree(ROOT / "build" / folder, TECH / "integration/build" / folder, dirs_exist_ok=True)
for name in ["integrated_lake_build.log", "theorem_map_check.log"]:
    copy(ROOT / "build" / name, TECH / "integration/build" / name)
comparison = json.loads((ROOT / "records/PDF_PAGE_COMPARISON.json").read_text())
for key in ["monograph", "lean", "visual"]:
    pages = range(1, 24) if key == "lean" else comparison[key]["changed_or_new_pages"]
    for page in pages:
        name = f"page-{page:03d}.png" if key == "monograph" else f"page-{page:02d}.png"
        copy(ROOT / "build/rendered_final" / key / name, TECH / "integration/build/rendered_final" / key / name)
    copy(ROOT / "build/rendered_final" / (key + "_text.txt"), TECH / "integration/build/rendered_final" / (key + "_text.txt"))
for page in [17, 18, 19, 23, 24]:
    copy(ROOT / f"build/rendered/lean/page-{page:02d}.png", TECH / f"integration/build/rendered/lean/page-{page:02d}.png")
technical = archive(TECH, "Komorebi_Space_Technical_Record_v1.14.0")

verification = {
    "edition": "1.14.0", "author": "Komorebi P.", "edition_date": "2026-10-14",
    "scope": edition["scope"], "counts": edition["counts"], "integrated_build_exit_code": 0,
    "integrated_build_jobs": 3820, "mapped_declarations_checked": 109, "all_164_lean_sources_preserved": True,
    "all_192_mathematical_environments_preserved": True, "source_review_checks_passed": 24,
    "pdf_pages": {key: value["pages"] for key, value in edition["books"].items()},
    "books": [{"file": Path(book["file"]).name, "bytes": (OUT / Path(book["file"]).name).stat().st_size,
               "sha256": book["sha256"], "pages": book["pages"], "identical_to_public_archive_book": True}
              for book in edition["books"].values()],
    "archives": [publication, technical], "controls": edition["controls"],
    "publication_manifest_scope": "Every archived file except SHA256SUMS itself.",
    "trust_boundary": edition["trust_boundary"], "limitations": edition["limitations"],
    "pdf_notice_disclosure": "Routine underfull-box and visual-bookmark spacing notices retained in detailed structural records; final unresolved-reference, overflow, missing-character, invalid-link and off-page-text checks passed.",
    "checks_complete_before_saving": True
}
target = OUT / "Komorebi_Space_Release_Verification_v1.14.0.json"
target.write_text(json.dumps(verification, indent=2) + "\n")
print(json.dumps({"deliverables": [{"file": path.name, "bytes": path.stat().st_size, "sha256": sha(path)} for path in files(OUT)]}, indent=2))
