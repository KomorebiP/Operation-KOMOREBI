"""Build the verified Stirling/Bell/Fubini reader and source-bound downloads.

Outputs are regenerated from the committed exact standard-library program;
no external plotter or opaque binary data is used. A separate test replays
the arithmetic and source-to-site checks before Pages deployment.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

PROGRAM="examples/stirling_bell_fubini.py"
MANUSCRIPT="docs/demonstrations/STIRLING_BELL_FUBINI.md"
READER="read/stirling-bell-fubini.html"
PREFIX="downloads/stirling-bell-fubini/"
RECORD=PREFIX+"source-record.json"
ARCHIVE=PREFIX+"source-and-results.zip"
FILES=("stirling-rows.csv","sequence-checks.csv","moment-bridge.csv","signed-transfer.csv",
       "obstruction.csv","reciprocal-packets.csv","stirling-transform.svg",
       "results.json")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def program_module(root):
    path=root/PROGRAM
    spec=importlib.util.spec_from_file_location("stirling_bell_fubini_publication",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def publish(site):
    root=site.root
    module=program_module(root)
    checks=module.test_cases()
    target=site.output/PREFIX
    target.mkdir(parents=True,exist_ok=True)
    module.save(target,checks)
    program=(root/PROGRAM).read_bytes()
    manuscript=(root/MANUSCRIPT).read_bytes()
    (target/"stirling_bell_fubini.py").write_bytes(program)
    sources={
        PROGRAM:program,
        MANUSCRIPT:manuscript,
        "LICENSE.md":(root/"LICENSE.md").read_bytes()
    }
    items=[]
    for name in FILES:
        raw=(target/name).read_bytes()
        path="generated/"+name
        sources[path]=raw
        items.append(dict(name=name,url=PREFIX+name,size=len(raw),sha256=sha256(raw)))
    archive=site.output/ARCHIVE
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as bundle:
        for path,raw in sorted(sources.items()):
            info=zipfile.ZipInfo(path,(2026,10,31,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            bundle.writestr(info,raw)
    result=json.loads((target/"results.json").read_bytes())
    record={
        "title":"Stirling, Bell and Fubini: exact triangular and reciprocal transfer",
        "collection_revision":site.revision,
        "program_source":PROGRAM,
        "program_sha256":sha256(program),
        "program_size":len(program),
        "manuscript_source":MANUSCRIPT,
        "manuscript_sha256":sha256(manuscript),
        "reader_url":READER,
        "manuscript_url":"collection/demonstrations/STIRLING_BELL_FUBINI.html",
        "download_url":PREFIX+"stirling_bell_fubini.py",
        "tables":items,
        "archive_url":ARCHIVE,
        "archive_sha256":sha256(archive.read_bytes()),
        "archive_files":[dict(path=path,sha256=sha256(raw)) for path,raw in sorted(sources.items())],
        "case_assertions":result["total_assertions"],
        "case_groups":result["checks_by_group"],
        "scope":("Classical finite combinatorics, exact triangular matrices, formal "
                 "reciprocal series and two/three residue packets. The site's "
                 "bounded tests do not constitute a new Lean or novelty claim.")
    }
    site.write(RECORD,json.dumps(record,ensure_ascii=False,indent=2)+"\n")

    from reader_documents import source_lines
    body=(
        '<h1>Stirling, Bell and Fubini / complete exact Python source</h1>'
        '<p>Triangular matrices, signed inverse, Bell and ordered Bell numbers, '
        'Touchard and exponential-moment families, formal generating functions, a parity transfer system, '
        'three residue packets and an explicit information-loss witness. '
        'Python 3.10 or later, standard library only.</p>'
        '<p><a class="button" href="../collection/demonstrations/STIRLING_BELL_FUBINI.html">'
        'Read the complete hand derivation</a> '
        '<a download href="../'+record["download_url"]+'">Download Python</a> · '
        '<a href="../'+ARCHIVE+'">Source and results ZIP</a> · '
        '<a href="../'+RECORD+'">Source identities</a></p>'
        '<p>Generated exact files: '+
        ' · '.join('<a href="../'+entry["url"]+'">'+entry["name"]+'</a>' for entry in items)
        +'</p>'
        '<p>Run <code>python -B stirling_bell_fubini.py</code> for exact checks; '
        'add <code>--output stirling-results</code> for downloadable records.</p>'
    )
    site.page(READER,"Stirling, Bell and Fubini / exact Python source",
              body+source_lines(program.decode("utf-8")),
              "https://github.com/KomorebiP/Operation-KOMOREBI/blob/"
              +site.revision+"/"+PROGRAM)
    site.search.append(dict(
        title="Stirling, Bell and Fubini / exact Python checker",
        group="Collection",kind="Code",
        work_ids=["monographs-special-functions","paper-iv"],
        url=READER,
        text=("set partition Stirling numbers of second kind "
              "Bell numbers ordered Bell Fubini factorial Stirling transform "
              "signed Stirling first kind inverse Bell EGF reciprocal "
              "root of unity filters even odd polyphase residues "
              "Touchard polynomials gamma moments geometric distribution "
              "obstruction finite matrices exact rational Python")))
    return record


def verify_site(root:Path,pages:dict)->int:
    record=json.loads((root/RECORD).read_bytes())
    assert record["reader_url"] in pages
    assert record["manuscript_url"] in pages
    raw=(root/record["download_url"]).read_bytes()
    assert len(raw)==record["program_size"]
    assert sha256(raw)==record["program_sha256"]
    assert record["case_assertions"] == sum(record["case_groups"].values())
    results=json.loads((root/PREFIX/"results.json").read_bytes())
    assert results["bell5"]==52 and results["fubini5"]==541
    assert results["row5"]==[0,1,15,25,10,1]
    assert results["moment_bridge_n5"]["2"] == {"touchard":"454","exponential_moment":"9002"}
    assert results["moment_bridge_n5"]["1/2"] == {"touchard":"257/32","exponential_moment":"91/2"}
    assert results["packet_split_n5"]=={
        "even_degree_tap_contribution":135,"odd_degree_tap_contribution":406}
    assert results["witness_n4"]["alternative_row"]==[0,5,2,7,1]
    for item in record["tables"]:
        data=(root/item["url"]).read_bytes()
        assert len(data)==item["size"] and sha256(data)==item["sha256"]
    archive=root/record["archive_url"]
    assert sha256(archive.read_bytes())==record["archive_sha256"]
    with zipfile.ZipFile(archive) as bundle:
        assert set(bundle.namelist())=={entry["path"] for entry in record["archive_files"]}
        for entry in record["archive_files"]:
            assert sha256(bundle.read(entry["path"]))==entry["sha256"]
        assert sha256(bundle.read(record["manuscript_source"]))==record["manuscript_sha256"]
    from reader_documents import source_lines
    html=(root/record["reader_url"]).read_text(encoding="utf-8")
    assert source_lines(raw.decode("utf-8")) in html
    assert "STIRLING_BELL_FUBINI.html" in html
    return 1
