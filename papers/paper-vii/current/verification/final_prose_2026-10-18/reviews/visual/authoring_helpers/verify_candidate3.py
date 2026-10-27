from pathlib import Path
import ast
import hashlib
import json
import re
import shutil

import fitz
from pypdf import PdfReader

BASE = Path("/workspace/scratch/be33f0b6c391")
ROOT = BASE / "output/Komorebi_Paper_VII_Final_2026-10-18"
BASELINE = BASE / "output/Komorebi_Paper_VII_Complete_Proofread_2026-10-18"
QA = BASE / "tmp/p7_final_visual_prose"
SNAPSHOT = QA / "candidate3_source_snapshot"
PDFS = {
    "traditional": BASE / "tmp/p7_final_candidate_3/Paper_VII_Traditional_Final.pdf",
    "visual": BASE / "tmp/p7_final_candidate_3/Paper_VII_Visual_Guide_Final.pdf",
}
EXPECTED = {
    "traditional": "a709b6aa717e12460501edc8c08dd119dcb17411d13510eb3718bde73034a4cf",
    "visual": "4833bf68cb5babdaa65781d0a904cbdfde9ceddc0e56852f22b8b9dfdd67a244",
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def norm(s):
    return " ".join(s.replace("--", "–").split())


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n")


for name, path in PDFS.items():
    assert sha(path) == EXPECTED[name], name

crosswalk_rel = "editable/visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json"
map_rel = "editable/traditional/canonical_label_to_final.json"
crosswalk_bytes = (ROOT / crosswalk_rel).read_bytes()
map_bytes = (ROOT / map_rel).read_bytes()
crosswalk = json.loads(crosswalk_bytes)
canonical = json.loads(map_bytes)
assert crosswalk["visual_pdf_sha256"] == EXPECTED["visual"]
assert crosswalk["traditional_pdf_sha256"] == EXPECTED["traditional"]
assert crosswalk["traditional_map_sha256"] == hashlib.sha256(map_bytes).hexdigest()

review = json.loads((QA / "PROSE_REVIEW.json").read_text())
SNAPSHOT.mkdir(exist_ok=True)
for rel, data in [(crosswalk_rel, crosswalk_bytes), (map_rel, map_bytes)]:
    dest = SNAPSHOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
owned = []
for record in review["files"]:
    rel = record["path"]
    dest = SNAPSHOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / rel, dest)
    owned.append({
        "path": rel,
        "baseline_sha256": record["before_sha256"],
        "prose_freeze_stage_sha256": record["after_sha256"],
        "candidate3_source_sha256": sha(dest),
        "changed_after_prose_freeze": record["after_sha256"] != sha(dest),
    })

visual = fitz.open(PDFS["visual"])
traditional = fitz.open(PDFS["traditional"])
reader = PdfReader(PDFS["traditional"])
destinations = reader.named_destinations
assert len(visual) == 42
assert len(traditional) == 159
vtoc = {
    int(re.match(r"V(\d+)\.", title)[1]): page
    for level, title, page in visual.get_toc()
    if re.match(r"V\d+\.", title)
}
assert set(vtoc) == set(range(1, 41))

source_pattern = re.compile(r"\\vpage\{(\d+)\}\{([^\n]*?)\}\{([^\n]*?)\}\{([^\n]*?)\}")
narrative = "\n".join(
    (SNAPSHOT / "editable/visual_guide/source" / name).read_text()
    for name in ["pages.tex", "extended_pages.tex"]
)
source_rows = {int(m[1]): m.groups() for m in source_pattern.finditer(narrative)}
assert set(source_rows) == set(range(1, 41))
checked = []
for row in crosswalk["pages"]:
    n = row["visual_page"]
    p = row["visual_physical_pdf_page"]
    assert p == n + 2 == vtoc[n]
    assert visual[p - 1].get_label() == str(n) == row["visual_printed_page"]
    assert source_rows[n][1] == row["title"]
    assert source_rows[n][3] == row["source_line_current"]
    rendered = [
        block[4].strip()
        for block in visual[p - 1].get_text("blocks")
        if block[4].startswith("Traditional p")
    ]
    assert len(rendered) == 1
    assert norm(rendered[0]) == norm(row["source_line_current"]), n
    targets = []
    for target in row["traditional_targets"]:
        label = target["final_label"]
        data = canonical[label]
        physical = target["physical_pdf_page"]
        printed = str(target["printed_page"])
        assert data["number"] == target["number"]
        assert data["physical_pdf_page"] == physical
        assert str(data["printed_page"]) == printed
        assert traditional[physical - 1].get_label() == printed
        destination_page = reader.get_destination_page_number(destinations[data["destination"]]) + 1
        assert destination_page == physical
        targets.append({
            "label": label,
            "number": target["number"],
            "printed_page": printed,
            "physical_pdf_page": physical,
            "actual_named_destination": data["destination"],
            "status": "PASS",
        })
    checked.append({"visual_page": n, "visual_physical_page": p, "locator": rendered[0], "targets": targets})

authoring_source = (QA / "edit_visual_prose.py").read_text()
tree = ast.parse(authoring_source)
math_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "math_spans")
scope = {}
exec(compile(ast.Module(body=[math_node], type_ignores=[]), "<read-only math extraction>", "exec"), scope)
math_spans = scope["math_spans"]
math_records = []
for name in ["front.tex", "pages.tex", "extended_pages.tex"]:
    rel = "editable/visual_guide/source/" + name
    current = (SNAPSHOT / rel).read_text()
    old = (BASELINE / rel).read_text()
    assert math_spans(current) == math_spans(old), rel
    math_records.append({
        "path": rel,
        "span_count": len(math_spans(current)),
        "math_spans_sha256": hashlib.sha256(json.dumps(math_spans(current)).encode()).hexdigest(),
        "status": "PASS",
    })
assert sum(r["span_count"] for r in math_records) == 488

atlas = (SNAPSHOT / "editable/traditional/monograph_atlas.tex").read_text()
atlas = atlas[atlas.index(r"\vpage{1}"):]
atlas = atlas.rsplit(r"\endgroup", 1)[0].strip()


def normalized_pages(text):
    starts = list(source_pattern.finditer(text))
    pages = {}
    for i, match in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        chunk = text[match.start():end].strip()
        chunk = source_pattern.sub(
            lambda m: r"\vpage{" + m[1] + "}{" + m[2] + "}{" + m[3] + "}{LOCATOR}", chunk
        )
        pages[int(match[1])] = chunk
    return pages


assert normalized_pages(narrative) == normalized_pages(atlas)
assert len(re.findall(r"\\vfigx?\{", narrative)) == 38

caption_node = next(
    n for n in tree.body
    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "captions" for t in n.targets)
)
captions = ast.literal_eval(caption_node.value)
caption_map = {(d, name + ".tex"): (old, new) for d, name, old, new in captions}
plates = []
for directory, counterpart in [("graphics", "visual_graphics"), ("graphics_extended", "visual_graphics_extended")]:
    for old_path in sorted((BASELINE / "editable/visual_guide" / directory).glob("*.tex")):
        name = old_path.name
        old = old_path.read_text()
        current_path = ROOT / "editable/visual_guide" / directory / name
        paired_path = ROOT / "editable/traditional" / counterpart / name
        current = current_path.read_text()
        assert current_path.read_bytes() == paired_path.read_bytes()
        expected = old
        if (directory, name) in caption_map:
            before, after = caption_map[(directory, name)]
            assert old.count(before) == 1
            expected = old.replace(before, after)
        assert current == expected, (directory, name)
        assert math_spans(current) == math_spans(old)
        plates.append({
            "path": str(current_path.relative_to(ROOT)),
            "sha256": sha(current_path),
            "paired_atlas_sha256": sha(paired_path),
            "geometry_byte_preserved_outside_exact_caption_replacement": True,
            "mathematical_spans_byte_identical": True,
        })
assert len(plates) == 38

output = {
    "status": "PASS_CANDIDATE3_STAGE_SPECIFIC",
    "pdf_sha256": EXPECTED,
    "source_snapshot": str(SNAPSHOT.relative_to(BASE)),
    "hash_policy": "Baseline and prose-freeze source hashes remain the historical hashes of those stages. Candidate 3 source hashes are recorded separately. This report does not rebind an earlier report to a later PDF.",
    "owned_source_hashes": owned,
    "atlas_body_synchronization": "All 40 bodies are equal after removing only atlas setup and normalizing locator strings.",
    "narrative_math_preservation": math_records,
    "vector_plate_preservation": plates,
    "crosswalk_sha256": hashlib.sha256(crosswalk_bytes).hexdigest(),
    "canonical_map_sha256": hashlib.sha256(map_bytes).hexdigest(),
    "crosswalk_visual_pages": len(checked),
    "crosswalk_target_occurrences": sum(len(row["targets"]) for row in checked),
    "crosswalk_checks": checked,
    "fresh_symbolic_or_scientific_execution": False,
    "generator_note": "GENERATOR_REPLAY.json records the earlier isolated 12-plate source replay. The original 26-plate generator requires unavailable SymPy and was not run. This read-only final audit performs no scientific calculation.",
}
write_json(QA / "CANDIDATE3_SOURCE_AND_CROSSWALK.json", output)
print(json.dumps({
    "status": output["status"],
    "owned_sources": len(owned),
    "source_hash_changes_after_freeze": [r["path"] for r in owned if r["changed_after_prose_freeze"]],
    "visual_pages": len(checked),
    "reading_targets": output["crosswalk_target_occurrences"],
    "math_spans": 488,
    "plates": len(plates),
}))
