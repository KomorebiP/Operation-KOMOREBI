#!/usr/bin/env python3
"""Build and qualify a source-bound Constructive Repair beta distribution.

The imported component is read only. A separate build directory receives the
current README and license metadata. Qualification uses its existing acceptance
runner. Historical proof/monograph checks are source consistency, not a new Lean
execution. All build and result directories must be new.
"""
from __future__ import annotations

import argparse
import base64
import csv
from datetime import datetime, timezone
from email.parser import BytesParser
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile

VERSION = "1.0.0rc3"
BUILD_TOOLS = {"setuptools": "84.1.0", "wheel": "0.48.0"}
EPOCH = 1792368000
WINDOWS_SKIPS = {
    "test_portability_release.LocaleRegressionTests.test_export_under_ascii_locale",
    "test_portability_release.RuntimePinTests.test_matching_version_wrong_commit_rejected",
    "test_portability_release.RuntimePinTests.test_matching_lean_wrong_mathlib_rejected",
}
SYMLINK_TESTS = {
    "test_release_integrity.PathsAndBindings.test_symlink_rejected",
    "test_release_integrity.WheelBinding.test_symlink_wheel",
}
SCHEMA = "komorebi.repair.qualified-distribution.v1"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def native(value):
    path = Path(value).resolve()
    if os.name == "nt" and not str(path).startswith("\\\\?\\"):
        path = Path("\\\\?\\" + str(path))
    return path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")


def safe(root, name):
    require(type(name) is str and name and "\\" not in name, "Invalid path")
    rel = PurePosixPath(name)
    require(not rel.is_absolute() and ".." not in rel.parts and
            str(rel) == name and ":" not in name, "Unsafe path: " + name)
    target = root.joinpath(*rel.parts)
    require(target.resolve().is_relative_to(root.resolve()), "Escaping path: " + name)
    require(not any(p.is_symlink() for p in (target, *target.parents)
                    if p.is_relative_to(root) and p != root), "Symlink: " + name)
    return target


def inventory(root):
    require(not root.is_symlink(), "Symlink root")
    return {p.relative_to(root).as_posix(): p
            for p in root.rglob("*") if p.is_file()}


def verify_import(source, receipt):
    rows = receipt["files"]
    require(receipt["component"] == "constructive-repair" and
            receipt["file_count"] == len(rows) == 2254, "Wrong component inventory")
    names = {row["path"] for row in rows}
    require(len(names) == len(rows), "Duplicate source record")
    require(set(inventory(source)) == names, "Source-file inventory differs")
    for row in rows:
        path = safe(source, row["path"])
        require(path.is_file() and path.stat().st_size == row["size"] and
                sha(path) == row["sha256"], "Source mismatch: " + row["path"])
    return {"files": len(rows), "bytes": sum(row["size"] for row in rows),
            "tree_sha256": receipt["tree_sha256"]}


def runtime_names(source):
    return ["repair_certificates.py", "rational_menu.py", "branch_menu.py"] + sorted(
        p.relative_to(source / "python").as_posix()
        for p in (source / "python/komorebi_repair").glob("*.py"))


def normalized_wheel(wheel):
    temp = wheel.with_suffix(".normalizing")
    require(not temp.exists(), "Normalization output already exists")
    with zipfile.ZipFile(wheel) as original:
        require(len(original.namelist()) == len(set(original.namelist())),
                "Duplicate wheel members")
        contents = {name: original.read(name) for name in original.namelist()}
    for name in contents:
        if name.endswith((".dist-info/METADATA", ".dist-info/WHEEL")):
            contents[name] = contents[name].replace(b"\r\n", b"\n")
    records = [name for name in contents if name.endswith(".dist-info/RECORD")]
    require(len(records) == 1, "Missing wheel RECORD")
    record = records[0]
    rows = []
    for name in sorted(contents):
        if name != record:
            data = contents[name]
            digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
            rows.append([name, "sha256=" + digest, str(len(data))])
    rows.append([record, "", ""])
    stream = io.StringIO()
    csv.writer(stream, lineterminator="\n").writerows(rows)
    contents[record] = stream.getvalue().encode("utf-8")
    with zipfile.ZipFile(temp, "w") as out:
        for name in sorted(contents):
            info = zipfile.ZipInfo(name, time.gmtime(EPOCH)[:6])
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            out.writestr(info, contents[name])
    os.replace(temp, wheel)


def verify_wheel(wheel, source, code_license, collection_license, readme):
    expected = runtime_names(source)
    require(len(expected) == 7, "Unexpected runtime inventory")
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
        require(len(names) == len(set(names)) and z.testzip() is None,
                "Duplicate or corrupt wheel member")
        require(sorted(n for n in names if n.endswith(".py")) == sorted(expected),
                "Wheel runtime inventory differs")
        for name in expected:
            require(z.read(name) == safe(source, "python/" + name).read_bytes(),
                    "Wheel/source mismatch: " + name)
        metadata = [n for n in names if n.endswith(".dist-info/METADATA")]
        records = [n for n in names if n.endswith(".dist-info/RECORD")]
        require(len(metadata) == len(records) == 1, "Missing wheel metadata")
        msg = BytesParser().parsebytes(z.read(metadata[0]))
        require(msg["Name"] == "komorebi-constructive-repair" and
                msg["Version"] == VERSION, "Wrong wheel name/version")
        require(msg["License-Expression"] == "MIT", "Wrong current code license")
        body = msg.get_payload(decode=True).decode("utf-8").replace("\r\n", "\n")
        require(body.strip() == readme.read_text(encoding="utf-8").strip(),
                "Wheel uses a different release README")
        for filename, path in (("LICENSE-CODE.txt", code_license),
                               ("LICENSE-COLLECTION.md", collection_license)):
            matches = [n for n in names if n.endswith("/licenses/" + filename)]
            require(len(matches) == 1 and z.read(matches[0]) == path.read_bytes(),
                    "Missing or different current license: " + filename)
        rows = list(csv.reader(io.StringIO(z.read(records[0]).decode("utf-8"))))
        require(len(rows) == len(names) and {r[0] for r in rows} == set(names),
                "Wheel RECORD coverage differs")
        for name, digest, size in rows:
            if name == records[0]:
                require(digest == size == "", "Invalid RECORD self-entry")
            else:
                data = z.read(name)
                encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
                require(digest == "sha256=" + encoded and size == str(len(data)),
                        "Invalid wheel RECORD entry: " + name)
    return {"name": wheel.name, "sha256": sha(wheel), "bytes": wheel.stat().st_size,
            "runtime_files": {n: sha(source / "python" / n) for n in expected},
            "license_expression": "MIT"}


def release_test_results(text, system):
    rows = re.findall(r"^\S+\s+\(([^)]+)\)\s+\.\.\.\s+(ok|skipped [^\n]+)$",
                      text, re.MULTILINE)
    require(len(rows) == 100 and len({name for name, _ in rows}) == 100,
            "Expected 100 individually recorded release tests")
    skipped = {name for name, result in rows if result.startswith("skipped")}
    allowed = WINDOWS_SKIPS if system == "Windows" else set()
    require(skipped == allowed, "Unexpected skipped release tests")
    passed = {name for name, result in rows if result == "ok"}
    require(SYMLINK_TESTS <= passed, "Symlink rejection controls did not pass")
    return {"run": 100, "passed": len(passed), "skipped": sorted(skipped),
            "errors": 0, "failures": 0,
            "symlink_controls": sorted(SYMLINK_TESTS)}


def check_acceptance(receipt, wheel_hash):
    require(receipt["status"] == "PASS" and receipt["wheel_sha256"] == wheel_hash,
            "Acceptance is failed or belongs to a different wheel")
    checks = receipt.get("checks", {})
    require(bool(checks) and all(r.get("pass") is True for r in checks.values()),
            "Missing or failed acceptance check")
    require(checks["release_test_count"]["detail"] == 100 and
            checks["engine_test_count"]["detail"] == 134 and
            checks["installed_problem_count"]["detail"] == 72,
            "Acceptance coverage differs")
    require(receipt["source_sha256"], "Missing acceptance source binding")


def write_manifest(root):
    files = inventory(root)
    files.pop("MANIFEST.json", None)
    files.pop("SHA256SUMS.txt", None)
    rows = [{"path": name, "bytes": p.stat().st_size, "sha256": sha(p)}
            for name, p in sorted(files.items())]
    dump(root / "MANIFEST.json", {"schema": SCHEMA, "files": rows})
    checks = [(row["path"], row["sha256"]) for row in rows]
    checks.append(("MANIFEST.json", sha(root / "MANIFEST.json")))
    (root / "SHA256SUMS.txt").write_text(
        "".join(digest + "  " + name + "\n" for name, digest in sorted(checks)),
        encoding="utf-8", newline="\n")


def verify_bundle(root):
    root = native(root)
    manifest = load(root / "MANIFEST.json")
    require(manifest["schema"] == SCHEMA, "Unknown distribution manifest")
    rows = manifest["files"]
    names = {r["path"] for r in rows}
    require(len(names) == len(rows) and
            set(inventory(root)) == names | {"MANIFEST.json", "SHA256SUMS.txt"},
            "Distribution inventory differs")
    for row in rows:
        p = safe(root, row["path"])
        require(p.stat().st_size == row["bytes"] and sha(p) == row["sha256"],
                "Distribution hash mismatch: " + row["path"])
    checks = {}
    for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        require(name not in checks, "Duplicate checksum entry")
        checks[name] = digest
    require(set(checks) == names | {"MANIFEST.json"} and
            all(checks[r["path"]] == r["sha256"] for r in rows) and
            checks["MANIFEST.json"] == sha(root / "MANIFEST.json"),
            "Checksum coverage or manifest hash differs")
    report = load(root / "qualification.json")
    require(report["schema"] == SCHEMA and report["status"] == "PASS" and
            report["source_unchanged"] is True and report["new_lean_execution"] is False,
            "Unqualified distribution")
    require(sha(root / "SOURCE_IMPORT.json") == report["source_receipt_sha256"],
            "Source receipt differs")
    verify_import(root / "source", load(root / "SOURCE_IMPORT.json"))
    require(report["source_revision"] ==
            (root / "SOURCE_REVISION").read_text(encoding="utf-8").strip(),
            "Source revision differs")
    wheels = list((root / "dist").glob("*.whl"))
    require(len(wheels) == 1, "Expected one wheel")
    wheel = verify_wheel(wheels[0], root / "source", root / "LICENSE-CODE.txt",
                         root / "LICENSE-COLLECTION.md", root / "README.md")
    require(wheel == report["wheel"], "Wheel qualification record differs")
    acceptance = load(root / "evidence/acceptance.json")
    check_acceptance(acceptance, wheel["sha256"])
    tests = release_test_results((root / "evidence/release_tests.log").read_text(
        encoding="utf-8"), report["system"])
    require(tests == report["release_tests"], "Release test report differs")
    for name, expected in acceptance["source_sha256"].items():
        path = safe(root, "build-inputs/pyproject.toml" if name == "pyproject.toml"
                    else "source/" + name)
        require(sha(path) == expected, "Stale acceptance source: " + name)
    require(report["qualifier_sha256"] ==
            sha(root / "tools/constructive_repair_release.py"), "Qualifier changed")
    return report


def archive(root, target):
    require(not target.exists(), "Archive already exists")
    modes = {"source/" + r["path"]: int(r["mode"], 8)
             for r in load(root / "SOURCE_IMPORT.json")["files"]}
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as z:
        for name, path in sorted(inventory(root).items()):
            info = zipfile.ZipInfo(root.name + "/" + name, time.gmtime(EPOCH)[:6])
            info.create_system = 3
            info.external_attr = modes.get(name, 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, path.read_bytes(), compresslevel=6)
    with zipfile.ZipFile(target) as z:
        require(z.testzip() is None, "Archive CRC failed")


def copy_evidence(source, dest, replacements):
    variants = {}
    for old, new in replacements.items():
        ordinary = old[4:] if old.startswith("\\\\?\\") else old
        for value in (old, ordinary, old.replace("\\", "/"), ordinary.replace("\\", "/")):
            variants[value] = new
            variants[value.replace("\\", "\\\\")] = new
    for name, path in inventory(source).items():
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        try:
            text = data.decode("utf-8").replace("\r\n", "\n")
            for old in sorted(variants, key=len, reverse=True):
                text = text.replace(old, variants[old])
            data = text.encode("utf-8")
        except UnicodeDecodeError:
            pass
        target.write_bytes(data)


def qualify(args):
    root, out = native(args.root), native(args.output)
    require(not out.exists(), "Output directory must be new")
    out.mkdir(parents=True)
    report = {"schema": SCHEMA, "status": "RUNNING",
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "system": platform.system(), "python": platform.python_version(),
              "platform": platform.platform(), "machine": platform.machine(),
              "new_lean_execution": False, "commands": [],
              "temporary_directory": "<QUALIFICATION_ROOT>/test-temp"}
    test_temp = out / "test-temp"
    def save():
        dump(out / "qualification.json", report)
    def run(label, argv, cwd, timeout=600):
        env = os.environ.copy()
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
                   TMP=str(test_temp), TEMP=str(test_temp), TMPDIR=str(test_temp))
        started = time.monotonic()
        p = subprocess.run([str(x) for x in argv], cwd=cwd, env=env,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        (out / (label + ".log")).write_text(p.stdout + p.stderr, encoding="utf-8",
                                             newline="\n")
        report["commands"].append({"label": label, "returncode": p.returncode,
                                   "seconds": round(time.monotonic()-started, 3)})
        save()
        require(p.returncode == 0, label + " failed; see " + label + ".log")
    try:
        test_temp.mkdir()
        bundled = (root / "SOURCE_IMPORT.json").is_file()
        source = root / ("source" if bundled else "packages/constructive-repair")
        receipt_path = root / ("SOURCE_IMPORT.json" if bundled else
                              "manifests/source-imports/constructive-repair.json")
        code_license = root / "LICENSE-CODE.txt"
        collection_license = root / ("LICENSE-COLLECTION.md" if bundled else "LICENSE.md")
        readme = root / ("README.md" if bundled else "publication/constructive-repair/README.md")
        receipt = load(receipt_path)
        report["source"] = verify_import(source, receipt)
        revision = ((root / "SOURCE_REVISION").read_text(encoding="utf-8").strip()
                    if bundled else args.revision or os.environ.get("GITHUB_SHA", ""))
        require(re.fullmatch(r"[0-9a-f]{40}", revision), "Exact source revision required")
        report["source_revision"] = revision
        report["source_receipt_sha256"] = sha(receipt_path)
        report["qualifier_sha256"] = sha(Path(__file__))
        report["build_tools"] = {name: importlib.metadata.version(name) for name in BUILD_TOOLS}
        require(report["build_tools"] == BUILD_TOOLS, "Use the documented pinned build tools")
        stage = out / "build"
        shutil.copytree(source, stage)
        project = (stage / "pyproject.toml").read_text(encoding="utf-8")
        require(project.count('readme = "README.md"') == 1 and
                "license-files" not in project, "Unexpected source metadata")
        project = project.replace('readme = "README.md"',
            'readme = "RELEASE_README.md"\nlicense = "MIT"\n'
            'license-files = ["LICENSE-CODE.txt", "LICENSE-COLLECTION.md"]')
        (stage / "pyproject.toml").write_text(project, encoding="utf-8", newline="\n")
        shutil.copyfile(readme, stage / "RELEASE_README.md")
        shutil.copyfile(code_license, stage / "LICENSE-CODE.txt")
        shutil.copyfile(collection_license, stage / "LICENSE-COLLECTION.md")
        run("build-wheel", [sys.executable, "-B", stage / "scripts/build_wheel.py"], stage, 180)
        wheels = list((stage / "dist").glob("*.whl"))
        require(len(wheels) == 1, "Expected one rebuilt wheel")
        normalized_wheel(wheels[0])
        report["wheel"] = verify_wheel(wheels[0], source, code_license,
                                       collection_license, readme)
        if args.build_only:
            report.update(status="BUILD_ONLY", source_unchanged=True)
            verify_import(source, receipt)
            save()
            return report
        probe = out / "symlink-probe"
        probe.mkdir()
        (probe / "target").write_bytes(b"fixture")
        (probe / "link").symlink_to(probe / "target")
        require((probe / "link").read_bytes() == b"fixture", "Symlink fixture unavailable")
        run("acceptance", [sys.executable, "-B", stage / "scripts/accept_release.py",
                           "--output", out / "raw-acceptance"], stage, 900)
        acceptance = load(out / "raw-acceptance/acceptance.json")
        check_acceptance(acceptance, report["wheel"]["sha256"])
        report["release_tests"] = release_test_results(
            (out / "raw-acceptance/release_tests.log").read_text(encoding="utf-8"),
            report["system"])
        report["engine_tests"] = 134
        report["installed_cases"] = 72
        report["installed_checks"] = acceptance["installed_checks"]
        report["platform_checks"] = acceptance["platform_checks"]
        sys.path.insert(0, str(source / "scripts"))
        from release_gate import proof_check, monograph_check
        from verify_lineage import verify_lineage
        report["historical_source_bindings"] = {
            "proofs": proof_check(source), "monograph": monograph_check(source),
            "lineage": verify_lineage(source), "new_kernel_execution": False}
        verify_import(source, receipt)
        report["source_unchanged"] = True
        report["run_url"] = ("https://github.com/" + os.environ["GITHUB_REPOSITORY"] +
            "/actions/runs/" + os.environ["GITHUB_RUN_ID"]
            if os.environ.get("GITHUB_RUN_ID") else None)
        report.update(status="PASS", finished_utc=datetime.now(timezone.utc).isoformat())
        save()
        bundle = out / ("constructive-repair-" + VERSION + "-qualified")
        bundle.mkdir()
        shutil.copytree(source, bundle / "source")
        for src, name in ((readme, "README.md"), (code_license, "LICENSE-CODE.txt"),
                          (collection_license, "LICENSE-COLLECTION.md"),
                          (receipt_path, "SOURCE_IMPORT.json")):
            shutil.copyfile(src, bundle / name)
        (bundle / "SOURCE_REVISION").write_text(revision + "\n", encoding="utf-8", newline="\n")
        (bundle / "tools").mkdir()
        shutil.copyfile(Path(__file__), bundle / "tools/constructive_repair_release.py")
        (bundle / "build-inputs").mkdir()
        shutil.copyfile(stage / "pyproject.toml", bundle / "build-inputs/pyproject.toml")
        (bundle / "dist").mkdir()
        shutil.copyfile(wheels[0], bundle / "dist" / wheels[0].name)
        copy_evidence(out / "raw-acceptance", bundle / "evidence",
            {str(out): "<QUALIFICATION_ROOT>", str(root): "<SOURCE_ROOT>",
             str(sys.executable): "<PYTHON>"})
        report["published_evidence_normalization"] = (
            "Local root/interpreter paths replaced with placeholders; UTF-8 text "
            "line endings normalized to LF. Other file bytes and outcomes retained.")
        dump(bundle / "qualification.json", report)
        write_manifest(bundle)
        verify_bundle(bundle)
        artifacts = out / "artifacts"
        artifacts.mkdir()
        key = report["system"].lower() + "-py" + report["python"].replace(".", "")
        archive(bundle, artifacts / ("constructive-repair-" + VERSION + "-" + key + ".zip"))
        shutil.copyfile(wheels[0], artifacts / wheels[0].name)
        dump(artifacts / ("qualification-" + key + ".json"), report)
        return report
    except Exception as exc:
        report.update(status="FAIL", error=str(exc),
                      finished_utc=datetime.now(timezone.utc).isoformat())
        save()
        raise


def extract_verified(archive_path, dest):
    with zipfile.ZipFile(archive_path) as z:
        names = z.namelist()
        require(names and len(names) == len(set(names)), "Empty/duplicate archive")
        roots = {PurePosixPath(n).parts[0] for n in names}
        require(len(roots) == 1, "Archive needs one root")
        for info in z.infolist():
            target = safe(dest, info.filename)
            require(not info.is_dir() and (info.external_attr >> 16) & 0o170000 == 0o100000,
                    "Archive member is not a regular file")
            target.parent.mkdir(parents=True, exist_ok=True)
            require(not target.exists(), "Duplicate extracted path")
            target.write_bytes(z.read(info))
            if os.name == "posix":
                target.chmod((info.external_attr >> 16) & 0o777)
    bundle = dest / next(iter(roots))
    return bundle, verify_bundle(bundle)


def assemble(args):
    inputs, out = native(args.inputs), native(args.output)
    require(not out.exists(), "Assembly output must be new")
    out.mkdir(parents=True)
    archives = sorted(inputs.rglob("constructive-repair-*.zip"))
    require(len(archives) == 2, "Expected exactly two qualified platform archives")
    reports = []
    wheel_data = []
    for index, archive_path in enumerate(archives):
        bundle, report = extract_verified(archive_path, out / ("verified-" + str(index)))
        require(report["source_revision"] == args.revision, "Different source revision")
        reports.append(report)
        wheel = next((bundle / "dist").glob("*.whl"))
        wheel_data.append(wheel.read_bytes())
    require({(r["system"], r["python"]) for r in reports} ==
            {("Linux", "3.13.5"), ("Windows", "3.13.5")}, "Wrong qualification matrix")
    require(wheel_data[0] == wheel_data[1], "Platforms qualified different wheel bytes")
    for key in ("source", "source_receipt_sha256", "qualifier_sha256", "build_tools", "wheel"):
        require(reports[0][key] == reports[1][key], "Platform binding differs: " + key)
    assets = out / "assets"
    assets.mkdir()
    for path in archives:
        shutil.copyfile(path, assets / path.name)
    (assets / reports[0]["wheel"]["name"]).write_bytes(wheel_data[0])
    for report in reports:
        key = report["system"].lower() + "-py" + report["python"].replace(".", "")
        dump(assets / ("qualification-" + key + ".json"), report)
    record = {"schema": SCHEMA, "status": "PASS", "source_revision": args.revision,
              "version": VERSION, "wheel": reports[0]["wheel"],
              "platforms": reports, "new_lean_execution": False,
              "assets": {name: {"sha256": sha(path), "bytes": path.stat().st_size}
                         for name, path in sorted(inventory(assets).items())}}
    dump(assets / "RELEASE_RECORD.json", record)
    (assets / "SHA256SUMS.txt").write_text(
        "".join(sha(path) + "  " + name + "\n"
                for name, path in sorted(inventory(assets).items())),
        encoding="utf-8", newline="\n")
    notes = [
        "# Constructive Repair 1.0.0rc3 — qualified beta distribution", "",
        "Exact rational repair certificates, with a dependency-free Python wheel "
        "and complete source/evidence archives.", "",
        "Source revision: `" + args.revision + "`.", "",
        "| Platform | Release suite | Engine tests | Installed cases |",
        "|---|---|---|---|"]
    for report in sorted(reports, key=lambda r: r["system"]):
        tests = report["release_tests"]
        notes.append("| " + report["system"] + " / CPython " + report["python"] +
            " | " + str(tests["passed"]) + " passed, " + str(len(tests["skipped"])) +
            " platform-specific skips | 134 passed | 72 passed |")
    notes += ["", "Both symlink rejection controls passed on both platforms. "
              "The Linux suite ran all 100 release tests.",
              "", "The identical wheel was accepted on both platforms. Its seven runtime "
              "files match the 2,254-file imported source component. The build overlay "
              "supplies current README/license metadata and is recorded separately.",
              "", "Original code is covered by the collection's MIT grant; the collection "
              "notice in each archive states the applicable document and third-party terms.",
              "", "The archives include a verifier, reproduction instructions, full file "
              "checksums, and platform receipts. The standalone wheel needs no third-party "
              "runtime dependencies. Build reproduction uses the pinned build tools "
              "listed in the archive README.",
              "", "All software remains beta and work in progress. Historical formal "
              "source/receipt consistency was checked; this qualification performs no "
              "new Lean replay.", ""]
    (out / "release-notes.md").write_text("\n".join(notes), encoding="utf-8", newline="\n")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    q = sub.add_parser("qualify")
    q.add_argument("--root", type=Path, required=True)
    q.add_argument("--output", type=Path, required=True)
    q.add_argument("--revision")
    q.add_argument("--build-only", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("--root", type=Path, required=True)
    a = sub.add_parser("assemble")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--output", type=Path, required=True)
    a.add_argument("--revision", required=True)
    args = parser.parse_args()
    try:
        report = (qualify(args) if args.command == "qualify" else
                  verify_bundle(args.root) if args.command == "verify" else assemble(args))
        print(json.dumps({"status": report["status"], "command": args.command,
                          "source_revision": report["source_revision"]}))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "command": args.command, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
