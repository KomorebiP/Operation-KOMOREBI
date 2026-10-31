"""Publish source-bound wavelet/polyphase walkthrough and exact teaching records.

The website builder only copies checked source and snapshots. The Pages CI
separately executes the research program and compares all output bytes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

PROGRAM = "examples/wavelet_polyphase.py"
MANUSCRIPT = "docs/demonstrations/WAVELET_POLYPHASE.md"
READER = "read/wavelet-polyphase.html"
PREFIX = "downloads/wavelet-polyphase/"
DOWNLOAD = PREFIX + "wavelet_polyphase.py"
RECORD = PREFIX + "source-record.json"
ARCHIVE = PREFIX + "source-and-results.zip"
FILES = ("phase-transfer.csv", "haar-coefficients.csv", "weighted-budget.csv",
         "results.json", "signal-comparison.svg")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def publish(site):
    program = (site.root/PROGRAM).read_bytes()
    manuscript = (site.root/MANUSCRIPT).read_bytes()
    sources = {PROGRAM: program, MANUSCRIPT: manuscript}
    target = site.output/DOWNLOAD
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(program)
    exports = []
    for name in FILES:
        path = "verification/wavelet-polyphase/" + name
        raw = (site.root/path).read_bytes()
        sources[path] = raw
        published = PREFIX + name
        (site.output/published).write_bytes(raw)
        exports.append({"source": path, "url": published,
                        "sha256": digest(raw), "size": len(raw)})
    sources["LICENSE.md"] = (site.root/"LICENSE.md").read_bytes()
    archive = site.output/ARCHIVE
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path, raw in sources.items():
            info = zipfile.ZipInfo(path, (2026, 10, 30, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, raw)

    record = {
        "title": "Wavelets and polyphase transfer: exact worked derivation",
        "collection_revision": site.revision,
        "program_source": PROGRAM,
        "program_sha256": digest(program),
        "program_size": len(program),
        "manuscript_source": MANUSCRIPT,
        "manuscript_sha256": digest(manuscript),
        "reader_url": READER,
        "manuscript_url": "collection/demonstrations/WAVELET_POLYPHASE.html",
        "download_url": DOWNLOAD,
        "tables": exports,
        "archive_url": ARCHIVE,
        "archive_sha256": digest(archive.read_bytes()),
        "archive_files": [{"source": key, "sha256": digest(raw)}
                          for key, raw in sources.items()],
        "scope": ("Exact rational sixteen-sample Haar/FIR worked example with "
                  "finite lifting, periodic filter stability, optimal fixed-basis "
                  "selection, boundary repair and reproducible checks. "
                  "No infinite-signal or formal Lean replay.")
    }
    site.write(RECORD, json.dumps(record, ensure_ascii=False, indent=2)+"\n")

    from reader_documents import source_lines
    body = (
        '<h1>Wavelets and polyphase transfer / exact Python program</h1>'
        '<p>Four Haar levels, circular three-tap FIR filtering, exact '
        'polyphase and Haar operator transfers, exact lifting, weighted '
        'coefficient budgets, finite filter stability, boundary repair and '
        'counterexamples. Python 3.10 or later, standard library only.</p>'
        '<p><a class="button" href="../collection/demonstrations/WAVELET_POLYPHASE.html">'
        'Read the complete worked example</a> '
        '<a download href="../'+DOWNLOAD+'">Download Python</a> · '
        '<a href="../'+ARCHIVE+'">Source and results bundle</a> · '
        '<a href="../'+RECORD+'">Source identities</a></p>'
        '<p>Reproducible records: ' +
        ' · '.join('<a href="../'+item["url"]+'">'+item["url"].split("/")[-1]+'</a>'
                   for item in exports) + '</p>'
        '<p>Run <code>python -B wavelet_polyphase.py</code>. '
        'Add <code>--output wavelet-results</code> to generate all exact '
        'CSV, SVG, and JSON records.</p>'
    )
    site.page(READER, "Wavelets and polyphase transfer / exact Python program",
              body+source_lines(program.decode("utf-8")),
              "https://github.com/KomorebiP/Operation-KOMOREBI/blob/"
              +site.revision+"/"+PROGRAM)
    site.search.append(dict(
        title="Wavelets and polyphase transfer / exact Python checker",
        group="Collection", kind="Code",
        work_ids=["paper-ii", "paper-v", "information-realization", "streaming-skat"],
        url=READER,
        text=("Haar multiresolution lifting predict update weighted optimal "
              "coefficient selection filter stability cyclic convolution "
              "polyphase energy defect residual repair circular FIR three tap "
              "operator conjugacy direct transfer boundary correction "
              "Python exact fractions independently checked")))
    return record


def verify_site(root: Path, pages: dict) -> int:
    record = json.loads((root/RECORD).read_bytes())
    assert record["reader_url"] in pages
    assert record["manuscript_url"] in pages
    raw = (root/record["download_url"]).read_bytes()
    assert len(raw) == record["program_size"]
    assert digest(raw) == record["program_sha256"]
    for item in record["tables"]:
        exported = (root/item["url"]).read_bytes()
        assert len(exported) == item["size"] and digest(exported) == item["sha256"]
    archive = root/record["archive_url"]
    assert digest(archive.read_bytes()) == record["archive_sha256"]
    with zipfile.ZipFile(archive) as bundle:
        assert set(bundle.namelist()) == {
            item["source"] for item in record["archive_files"]}
        for item in record["archive_files"]:
            assert digest(bundle.read(item["source"])) == item["sha256"]
        assert digest(bundle.read(record["manuscript_source"])) == record["manuscript_sha256"]
    from reader_documents import source_lines
    reader_html = (root/record["reader_url"]).read_text(encoding="utf-8")
    assert source_lines(raw.decode("utf-8")) in reader_html
    assert "WAVELET_POLYPHASE.html" in reader_html
    assert record["scope"].startswith("Exact rational")
    return 1
