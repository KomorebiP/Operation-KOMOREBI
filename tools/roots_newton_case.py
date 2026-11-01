"""Publish and verify the exact roots-of-unity / Newton coordinate demonstration.

The source, generated records, SVG and deterministic ZIP are byte-bound to
the committed program and manuscript. No numerical or Lean proof is implied.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

PROGRAM = "examples/roots_unity_falling_factorial.py"
MANUSCRIPT = "docs/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md"
READER = "read/roots-unity-falling-factorial.html"
PREFIX = "downloads/roots-unity-falling-factorial/"
DOWNLOAD = PREFIX + "roots_unity_falling_factorial.py"
RECORD = PREFIX + "source-record.json"
ARCHIVE = PREFIX + "source-and-results.zip"
FILES = (
    "newton-stirling.csv",
    "image-histograms.csv",
    "packet-egfs.csv",
    "spectral-projectors.csv",
    "translation-blocks.csv",
    "shifted-packet-ledger.csv",
    "finite-characteristic-obstruction.csv",
    "packet-contributions.csv",
    "difference-transfer.csv",
    "refinement.csv",
    "projector-matrix.csv",
    "projection-diagram.svg",
    "function-image-histogram.svg",
    "translation-carry.svg",
    "results.json",
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_program(root):
    spec = importlib.util.spec_from_file_location(
        "roots_unity_falling_factorial_publication", root / PROGRAM)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def publish(site):
    module = load_program(site.root)
    counts = module.check()
    target = site.output / PREFIX
    target.mkdir(parents=True, exist_ok=True)
    module.save(target, counts)
    assert tuple(module.FILES) == FILES

    program = (site.root / PROGRAM).read_bytes()
    manuscript = (site.root / MANUSCRIPT).read_bytes()
    (site.output / DOWNLOAD).write_bytes(program)
    sources = {
        PROGRAM: program,
        MANUSCRIPT: manuscript,
        "LICENSE.md": (site.root / "LICENSE.md").read_bytes(),
    }
    tables = []
    for filename in FILES:
        content = (target / filename).read_bytes()
        sources["generated/" + filename] = content
        tables.append(dict(
            name=filename,
            url=PREFIX + filename,
            size=len(content),
            sha256=sha256(content),
        ))
    archive = site.output / ARCHIVE
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for filename, data in sorted(sources.items()):
            info = zipfile.ZipInfo(filename, (2026,10,31,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data)

    result = json.loads((target / "results.json").read_text(encoding="utf-8"))
    record = dict(
        title="Roots of unity, projectors and falling-factorial coordinates",
        collection_revision=site.revision,
        program_source=PROGRAM,
        program_sha256=sha256(program),
        program_size=len(program),
        manuscript_source=MANUSCRIPT,
        manuscript_sha256=sha256(manuscript),
        manuscript_url="collection/demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.html",
        reader_url=READER,
        download_url=DOWNLOAD,
        tables=tables,
        archive_url=ARCHIVE,
        archive_sha256=sha256(archive.read_bytes()),
        archive_files=[
            dict(path=filename,sha256=sha256(data))
            for filename, data in sorted(sources.items())
        ],
        case_assertions=result["total_assertions"],
        case_groups=result["checks_by_group"],
        scope=("Exact classical rational-polynomial theory; roots-of-unity degree "
               "filters, conjugated projectors, Newton inversion, cyclic difference "
               "transfer, exact function enumeration, spectral projectors, "
               "formal packet EGFs, general translation and cyclic carry, "
               "finite-characteristic spectral obstructions, star multiplication "
               "and explicit failed controls. "
               "No new Lean or novelty claim."),
    )
    site.write(RECORD, json.dumps(record, ensure_ascii=False, indent=2) + "\n")

    from reader_documents import source_lines
    html = (
        '<h1>Roots of unity, projectors, and falling factorials / exact Python</h1>'
        '<p>Reconstruct x^5 from three transported character packets. '
        'Includes exact Newton/Stirling inverses, difference-transfer identities, '
        'a six-packet refinement, an induced star product, direct function enumeration, '
        'the spectral number operator, filtered EGFs, translation carry blocks, '
        'finite-characteristic obstructions, and counterexamples. '
        'No complex floating-point arithmetic or third-party package is required.</p>'
        '<p><a class="button" href="../' + record["manuscript_url"] + '">'
        'Read the complete mathematical derivation</a> · '
        '<a download href="../' + DOWNLOAD + '">Download standalone Python</a> · '
        '<a href="../' + ARCHIVE + '">Source and results ZIP</a> · '
        '<a href="../' + RECORD + '">Source identity record</a></p>'
        '<p>Exact generated files: ' +
        ' · '.join('<a href="../' + row["url"] + '">' + row["name"] + '</a>'
                   for row in tables) + '</p>'
        '<p>Run <code>python -B roots_unity_falling_factorial.py</code> to check, '
        'or use <code>--output roots-results</code> for the CSV and SVG outputs.</p>'
    )
    site.page(
        READER,
        "Roots of unity and falling-factorial coordinates / exact source",
        html + source_lines(program.decode("utf-8")),
        "https://github.com/KomorebiP/Operation-KOMOREBI/blob/"
        + site.revision + "/" + PROGRAM,
    )
    site.search.append(dict(
        title="Roots of unity, projection and falling factorials / exact source",
        group="Collection", kind="Code",
        work_ids=["paper-i", "paper-iv", "paper-ix", "monographs-special-functions"],
        url=READER,
        text=("cyclotomic orthogonality cyclic permutation trace projectors "
              "Stirling Newton coefficients falling factorial polynomial "
              "transported operator finite difference derivative composition "
              "conjugation six lane residue refinement umbral star product "
              "character Fourier roots of unity Python exact rational certificate "
              "functions image sizes independent enumeration combinatorial "
              "backward difference number operator rational spectral projectors "
              "formal filtered exponential generating functions "
              "cyclic shift translation packet carry cross-channel matrix "
              "characteristic three finite fields eigenvalue collision"),
    ))
    return record


def verify_site(root: Path, pages: dict) -> int:
    record = json.loads((root / RECORD).read_bytes())
    assert record["reader_url"] in pages
    assert record["manuscript_url"] in pages
    program = (root / record["download_url"]).read_bytes()
    assert len(program) == record["program_size"]
    assert sha256(program) == record["program_sha256"]
    assert len(record["tables"]) == len(FILES)
    assert {x["name"] for x in record["tables"]} == set(FILES)
    assert record["case_assertions"] == sum(record["case_groups"].values())
    assert record["case_assertions"] >= 6800

    results = json.loads((root / PREFIX / "results.json").read_bytes())
    assert results["row5"] == [0,1,15,25,10,1]
    assert results["image_count_histogram_n5_x4"] == [0,4,180,600,240,0]
    assert results["number_operator_on_x_squared"] == ["0","-1","2"]
    assert results["shift_one_project_after_translate_at_4"] == ["1561","484","1080"]
    assert results["shift_one_translate_existing_packet_at_4"] == ["1500","1205","420"]
    assert results["shift_one_cross_packet_carries_at_4"] == ["961","240","900"]
    assert results["finite_characteristic_obstruction"]["falling_degree_3_mod_3"] == [0,2,0,1]
    assert results["packet_egf_n5_x4"] == ["600","244","180"]
    assert results["packet_values_at_x4"] == ["600","244","180"]
    assert results["difference_values_at_x4"] == ["900","961","240"]
    assert results["reconstructed_value_at_x4"] == "1024"
    assert results["correct_residue2_at_x4"] == "180"
    assert results["naive_residue2_at_x4"] == "1024"
    assert results["star_x_x_coefficients"] == ["0","-1","1"]
    for entry in record["tables"]:
        content = (root / entry["url"]).read_bytes()
        assert len(content) == entry["size"]
        assert sha256(content) == entry["sha256"]
    assert "2,2,15,12,180,1" in (
        root / PREFIX / "packet-contributions.csv").read_text(encoding="utf-8")
    assert "0,600,900,900" in (
        root / PREFIX / "difference-transfer.csv").read_text(encoding="utf-8")
    assert "5,4,3,600,600" in (root / PREFIX / "image-histograms.csv").read_text(encoding="utf-8")
    assert "0,600,1500,900,961,1561" in (
        root / PREFIX / "shifted-packet-ledger.csv").read_text(encoding="utf-8")
    assert "F3,0,0,1,1,0" in (
        root / PREFIX / "finite-characteristic-obstruction.csv").read_text(encoding="utf-8")
    assert "4,3,0,5,5,600" in (root / PREFIX / "packet-egfs.csv").read_text(encoding="utf-8")
    histogram_svg = (root / PREFIX / "function-image-histogram.svg").read_text(encoding="utf-8")
    assert 'role="img"' in histogram_svg
    assert "600 + 244 + 180 = 1024 functions" in histogram_svg
    translation_svg=(root / PREFIX / "translation-carry.svg").read_text(encoding="utf-8")
    assert 'role="img"' in translation_svg
    assert "1561 + 484 + 1080 = 3125" in translation_svg
    svg = (root / PREFIX / "projection-diagram.svg").read_text(encoding="utf-8")
    assert 'role="img"' in svg
    assert "600 + 244 + 180 = 1024" in svg
    zip_path = root / record["archive_url"]
    assert sha256(zip_path.read_bytes()) == record["archive_sha256"]
    with zipfile.ZipFile(zip_path) as bundle:
        assert set(bundle.namelist()) == {
            entry["path"] for entry in record["archive_files"]}
        for entry in record["archive_files"]:
            assert sha256(bundle.read(entry["path"])) == entry["sha256"]
        assert sha256(bundle.read(record["manuscript_source"])) == record["manuscript_sha256"]
    from reader_documents import source_lines
    html = (root / record["reader_url"]).read_text(encoding="utf-8")
    assert source_lines(program.decode("utf-8")) in html
    assert "ROOTS_UNITY_FALLING_FACTORIAL.html" in html
    return 1
