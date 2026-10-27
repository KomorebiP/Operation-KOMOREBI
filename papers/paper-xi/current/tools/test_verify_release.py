#!/usr/bin/env python3
"""Reproduce the existing 23 focused controls for verify_release.py.

    python tools/test_verify_release.py --output /outside/release/controls.json

Requires Python 3.10+ and PyMuPDF. Fixtures and the report are written outside
the release. No compiler, network access, or final release verification is run.
The intentionally invalid PDF page target may emit a MuPDF diagnostic. A
successful run proves that these controls behave as expected, not that the
current publication package passes its final integrity checks.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import warnings
import zipfile

sys.dont_write_bytecode = True


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def controls(root, output):
    tool = root / "tools/verify_release.py"
    module = load_module("paperxi_verifier_tested", tool)
    results = []

    def run_check(folder, name, method, expected):
        verifier = module.Verifier(folder)
        try:
            verifier.run(name, getattr(verifier, method))
            passed = not verifier.report["errors"]
            assert passed == expected, (name, method, expected, verifier.report["errors"])
            results.append({"test": method, "check": name,
                            "expected_pass": expected, "observed_pass": passed,
                            "errors": verifier.report["errors"]})
            return verifier.report
        finally:
            verifier.close()

    with tempfile.TemporaryDirectory(prefix="paperxi_verifier_fixture_", dir=output.parent) as work:
        fixture = Path(work)
        release = fixture / "release"
        release.mkdir()
        payload = release / "payload.txt"
        payload.write_bytes(b"verifier fixture, not publication evidence\n")
        manifest = {"schema_version": 1, "files": [{"path": "payload.txt",
                    "bytes": payload.stat().st_size, "sha256": module.sha256(payload)}]}
        (release / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")

        def zipped(path, extra=None, replacement=None):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
                    archive.write(release / "MANIFEST.json", "release/MANIFEST.json")
                    if replacement is None:
                        archive.write(payload, "release/payload.txt")
                    else:
                        archive.writestr("release/payload.txt", replacement)
                    if extra:
                        archive.writestr(*extra)

        good = fixture / "good.zip"
        zipped(good)
        verifier = module.Verifier(release)
        verifier.run("manifest", verifier.check_manifest)
        verifier.run("zip", lambda: verifier.check_zip(good))
        assert not verifier.report["errors"], verifier.report["errors"]
        results.append({"test": "valid manifest plus prefixed ZIP",
                        "expected_pass": True, "observed_pass": True})

        original = payload.read_bytes()
        payload.write_bytes(b"X" + original[1:])
        run_check(release, "manifest", "check_manifest", False)
        payload.write_bytes(original)
        (release / "extra.txt").write_text("unexpected", encoding="utf-8")
        run_check(release, "manifest", "check_manifest", False)
        (release / "extra.txt").unlink()

        for label, extra, replacement in [
            ("unsafe archive path", ("../escape.txt", b"x"), None),
            ("duplicate archive member", ("release/payload.txt", original), None),
            ("extra archive member", ("release/extra.txt", b"x"), None),
            ("member hash corruption", None, b"X" + original[1:]),
        ]:
            archive = fixture / (label.replace(" ", "_") + ".zip")
            zipped(archive, extra, replacement)
            verifier = module.Verifier(release)
            verifier.run("manifest", verifier.check_manifest)
            verifier.run("zip", lambda: verifier.check_zip(archive))
            assert verifier.report["checks"]["zip"]["status"] == "failed", label
            results.append({"test": label, "expected_pass": False,
                            "observed_pass": False, "errors": verifier.report["errors"]})

        corrupt = fixture / "crc.zip"
        zipped(corrupt)
        with zipfile.ZipFile(corrupt) as archive:
            offset = archive.getinfo("release/payload.txt").header_offset
        data = bytearray(corrupt.read_bytes())
        name_length = int.from_bytes(data[offset + 26:offset + 28], "little")
        extra_length = int.from_bytes(data[offset + 28:offset + 30], "little")
        data[offset + 30 + name_length + extra_length] ^= 1
        corrupt.write_bytes(data)
        verifier = module.Verifier(release)
        verifier.run("manifest", verifier.check_manifest)
        verifier.run("zip", lambda: verifier.check_zip(corrupt))
        assert verifier.report["checks"]["zip"]["status"] == "failed"
        assert any("CRC" in error["message"] for error in verifier.report["errors"])
        results.append({"test": "ZIP CRC corruption", "expected_pass": False,
                        "observed_pass": False, "errors": verifier.report["errors"]})

        # Raw PDF actions can expose bad destinations omitted by get_links().
        pdf_directory = release / "publication/pdfs"
        pdf_directory.mkdir(parents=True)
        for name in ["a.pdf", "b.pdf", "c.pdf", "d.pdf", "e.pdf"]:
            doc = module.fitz.open()
            doc.new_page()
            doc.new_page()
            if name == "a.pdf":
                names_xref = doc.get_new_xref()
                doc.update_object(names_xref,
                    f"<< /Dests << /Names [(valid.name) [{doc.page_xref(1)} 0 R /XYZ 0 0 0]] >> >>")
                doc.xref_set_key(doc.pdf_catalog(), "Names", f"{names_xref} 0 R")
                doc[0].insert_link({"kind": module.fitz.LINK_GOTO,
                    "from": module.fitz.Rect(10, 10, 50, 30), "page": 1})
                doc[0].insert_link({"kind": module.fitz.LINK_GOTOR,
                    "from": module.fitz.Rect(10, 40, 50, 60), "file": "b.pdf",
                    "page": 0, "to": module.fitz.Point(0, 0)})
                doc[0].insert_link({"kind": module.fitz.LINK_URI,
                    "from": module.fitz.Rect(10, 70, 50, 90),
                    "uri": "https://example.org/reference"})
            doc.save(pdf_directory / name)
            doc.close()

        doc = module.fitz.open(pdf_directory / "a.pdf")
        local_xref = next(link["xref"] for link in doc[0].get_links()
                          if link["kind"] == module.fitz.LINK_GOTO)
        doc.xref_set_key(local_xref, "A", "<< /S /GoTo /D (valid.name) >>")
        doc.saveIncr()
        doc.close()
        run_check(release, "pdfs", "check_pdfs", True)
        valid_pdf = (pdf_directory / "a.pdf").read_bytes()
        for label, action in [
            ("unresolved named destination", "<< /S /GoTo /D (missing.name) >>"),
            ("local page out of bounds", "<< /S /GoTo /D [999 /Fit] >>"),
            ("remote page out of bounds", "<< /S /GoToR /F (b.pdf) /D [999 /Fit] >>"),
            ("placeholder URI", "<< /S /URI /URI (https://komorebi.invalid/b07/x) >>"),
        ]:
            doc = module.fitz.open(pdf_directory / "a.pdf")
            doc.xref_set_key(local_xref, "A", action)
            doc.saveIncr()
            doc.close()
            run_check(release, "pdfs", "check_pdfs", False)
            results[-1]["test"] = label
            (pdf_directory / "a.pdf").write_bytes(valid_pdf)

        # Synthetic receipts test the diagnostic/signoff gate, not publication evidence.
        evidence = release / module.EVIDENCE
        evidence.mkdir(parents=True)
        (release / "tools").mkdir()
        (release / "tools/build_readers.py").write_text("# synthetic verifier fixture\n", encoding="utf-8")
        records = {}
        mapping = dict(zip(module.KINDS, ["a.pdf", "b.pdf", "c.pdf"]))
        for kind, name in mapping.items():
            source = release / "publication/source" / kind
            source.mkdir(parents=True)
            (source / "fixture.tex").write_text("Synthetic integrity-test input.\n", encoding="utf-8")
            records[kind] = {"status": "compiled",
                "source_fingerprint": module.fingerprint(source),
                "sha256": module.sha256(pdf_directory / name), "pages": 2,
                "commands": [{"returncode": 0}], "diagnostics": []}
        build = {"status": "passed", "records": records}
        (evidence / "READING_ROUTES.json").write_text(json.dumps({"pdfs": mapping}), encoding="utf-8")
        (evidence / "BUILD_RECORD.json").write_text(json.dumps(build), encoding="utf-8")
        run_check(release, "build", "check_build", True)
        for diagnostic in [
            "LaTeX Warning: Citation `fixture' on page 1 undefined",
            "Missing character: There is no X",
            "Overfull \\hbox (2.0pt too wide) at lines 1--2",
        ]:
            records["traditional"]["diagnostics"] = [diagnostic]
            (evidence / "BUILD_RECORD.json").write_text(json.dumps(build), encoding="utf-8")
            run_check(release, "build", "check_build", False)
            results[-1]["test"] = "forbidden compile diagnostic: " + diagnostic

        records["traditional"]["diagnostics"] = ["Underfull \\hbox (badness 10000) at lines 1--2"]
        (evidence / "BUILD_RECORD.json").write_text(json.dumps(build), encoding="utf-8")
        run_check(release, "build", "check_build", False)
        results[-1]["test"] = "underfull without matching visual signoff"
        visual = {"status": "passed", "reviews": [{"file": "a.pdf",
            "pdf_sha256": module.sha256(pdf_directory / "a.pdf"),
            "contact_pages": [1], "detailed_pages": [],
            "findings": ["Synthetic fixture only; no publication visual review asserted."]}]}
        (evidence / "VISUAL_REVIEW.json").write_text(json.dumps(visual), encoding="utf-8")
        verifier = module.Verifier(release)
        verifier.run("visual_review", verifier.check_visual)
        verifier.run("build", verifier.check_build)
        assert not verifier.report["errors"], verifier.report["errors"]
        verifier.close()
        results.append({"test": "underfull with matching current-PDF visual record",
                        "expected_pass": True, "observed_pass": True})
        visual["reviews"][0]["pdf_sha256"] = "0" * 64
        (evidence / "VISUAL_REVIEW.json").write_text(json.dumps(visual), encoding="utf-8")
        run_check(release, "visual_review", "check_visual", False)
        results[-1]["test"] = "stale visual signoff rejected"

        tokens = ("/- outer /- sorry -/ admit -/\n-- axiom in comment\n"
                  "axiom fixture : True\ntheorem fixture2 : True := by sorry\n"
                  'def text := "admit"\n')
        masked, issues = module.lean_comment_mask(tokens)
        hits = re.findall(r"\b(sorry|admit|axiom)\b", masked)
        assert not issues and hits == ["axiom", "sorry", "admit"], (issues, hits)
        results.append({"test": "nested comment exclusion plus conservative noncomment tokens",
                        "expected_tokens": ["axiom", "sorry", "admit"], "observed_tokens": hits})

    builder = load_module("paperxi_builder_tested", root / "tools/build_readers.py")
    matches = {kind: module.fingerprint(root / "publication/source" / kind)
               == builder.fingerprint(root / "publication/source" / kind)
               for kind in module.KINDS}
    assert all(matches.values()), matches
    results.append({"test": "fingerprints agree with actual builder function", "matches": matches})

    target = root / "SHOULD_NOT_BE_WRITTEN.json"
    assert not target.exists(), "Output-refusal fixture path already exists; no release file was changed"
    command = subprocess.run([sys.executable, str(tool), "--output", str(target)],
                             text=True, capture_output=True)
    assert command.returncode == 2 and not target.exists(), (command.returncode, command.stdout, command.stderr)
    results.append({"test": "CLI refuses report output inside release",
                    "expected_exit_code": 2, "observed_exit_code": command.returncode,
                    "file_created": False})
    assert len(results) == 23
    output.write_text(json.dumps({
        "scope": "Verifier implementation fixtures and negative controls only; not a final release PASS",
        "tool_sha256": hashlib.sha256(tool.read_bytes()).hexdigest(),
        "results": results, "all_expected_outcomes_observed": True}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fixture_tests": len(results), "expected_outcomes_observed": True,
                      "report": str(output)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", required=True, type=Path, help="Control receipt JSON outside the release")
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if not root.is_dir():
        parser.error("--root must be an existing release directory")
    if output.is_relative_to(root):
        parser.error("--output must be outside the release")
    output.parent.mkdir(parents=True, exist_ok=True)
    controls(root, output)


if __name__ == "__main__":
    main()
