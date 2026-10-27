#!/usr/bin/env python3
"""Preserve the complete monograph while applying explicit, reviewable edits."""
from __future__ import annotations

import hashlib
import html
import json
import subprocess
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
BUILD = ROOT / "build"
ORIGINAL = SOURCE / "Original_Monograph.pdf"
OUTPUT = BUILD / "Realization_Calculus_Large_Signal_Model.pdf"
FONT_DIR = ROOT / "assets" / "fonts"
if not FONT_DIR.exists():
    FONT_DIR = Path("/usr/share/fonts/opentype/urw-base35")
ROMAN = FONT_DIR / "P052-Roman.otf"
BOLD = FONT_DIR / "P052-Bold.otf"
ITALIC = FONT_DIR / "P052-Italic.otf"
COLOR = "#252a33"
CSS = f"""
@font-face {{font-family: LSM; src: url('{ROMAN.name}');}}
@font-face {{font-family: LSM; src: url('{BOLD.name}'); font-weight: bold;}}
@font-face {{font-family: LSM; src: url('{ITALIC.name}'); font-style: italic;}}
body {{font-family: LSM; color: {COLOR}; font-size: 11.457pt; line-height: 15.541pt;}}
p {{margin: 0; padding: 0;}}
b {{color: #252c49;}}
"""
ARCHIVE = fitz.Archive(str(ROMAN.parent))
changed: dict[int, list[str]] = {}
operations: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block(page: fitz.Page, needle: str) -> tuple:
    found = [b for b in page.get_text("blocks") if needle in b[4]]
    if len(found) != 1:
        raise ValueError(f"Page {page.number + 1}: expected one block for {needle!r}, found {len(found)}")
    return found[0]


def replace_box(doc: fitz.Document, index: int, rect: fitz.Rect, text: str,
                label: str, *, size: float = 11.457, leading: float = 15.541,
                align: str = "justify", old: str | None = None) -> None:
    rect = fitz.Rect(rect)
    css = CSS + f"body {{font-size:{size}pt;line-height:{leading}pt;text-align:{align};}}"
    probe = fitz.open()
    pg = probe.new_page(width=612, height=792)
    spare, scale = pg.insert_htmlbox(rect, text, css=css, archive=ARCHIVE, scale_low=1)
    probe.close()
    if spare < -0.001 or scale < .999:
        raise ValueError(f"Replacement does not fit without shrinking: {label}, {spare}, {scale}")
    page = doc[index]
    page.add_redact_annot(rect, fill=(1, 1, 1))
    page.apply_redactions(images=0, graphics=0)
    spare, scale = page.insert_htmlbox(rect, text, css=css, archive=ARCHIVE, scale_low=1)
    if spare < -0.001:
        raise ValueError(f"Unexpected insertion failure: {label}")
    changed.setdefault(index, []).append(label)
    operations.append({"pdf_page": index + 1, "label": label,
                       "rectangle": list(rect), "old_text": old,
                       "new_html": text, "font_size": size,
                       "spare_height": spare})


def replace_block(doc: fitz.Document, index: int, needle: str, text: str,
                  label: str, *, bottom_extra: float = 4, **kwargs) -> None:
    b = block(doc[index], needle)
    rect = fitz.Rect(b[:4])
    rect.x0 = 67.68 if index % 2 == 0 else 63.36
    rect.x1 = rect.x0 + 480.96
    rect.y0 -= 2
    rect.y1 += bottom_extra
    replace_box(doc, index, rect, text, label, old=b[4], **kwargs)


def one_line(doc: fitz.Document, index: int, needle: str, text: str, label: str,
             italic_token: str | None = None) -> None:
    b = block(doc[index], needle)
    rect = fitz.Rect(b[:4])
    # Use the existing baseline and matching full P052 font for an exact one-line edit.
    spans = [s for d in doc[index].get_text("dict")["blocks"]
             for line in d.get("lines", []) for s in line["spans"]
             if fitz.Rect(s["bbox"]).intersects(rect)]
    baseline = spans[0]["origin"][1]
    x = b[0]
    font = fitz.Font(fontfile=str(ROMAN))
    if font.text_length(text, fontsize=11.457) > 548.64 - x:
        raise ValueError(f"One-line text too long: {label}")
    page = doc[index]
    page.add_redact_annot(rect, fill=(1, 1, 1))
    page.apply_redactions(images=0, graphics=0)
    page.insert_font(fontname="LSMroman", fontfile=str(ROMAN))
    if italic_token:
        before, token, after = text.rpartition(italic_token)
        if not token:raise ValueError(f"Missing italic token: {italic_token}")
        page.insert_font(fontname="LSMitalic", fontfile=str(ITALIC))
        pos=x
        for part,font_name,font_path in [(before,"LSMroman",ROMAN),(token,"LSMitalic",ITALIC),(after,"LSMroman",ROMAN)]:
            page.insert_text((pos, baseline),part,fontsize=11.457,fontname=font_name,
                             color=(37/255,42/255,51/255))
            pos+=fitz.Font(fontfile=str(font_path)).text_length(part,fontsize=11.457)
    else:
        page.insert_text((x, baseline), text, fontsize=11.457, fontname="LSMroman",
                         color=(37/255,42/255,51/255))
    changed.setdefault(index, []).append(label)
    operations.append({"pdf_page": index + 1, "label": label,
                       "rectangle": list(rect), "old_text": b[4], "new_text": text})


def body_edits(doc: fitz.Document) -> None:
    one_line(doc, 9, "On realizable coefficients",
             "For a nonempty atlas family, define transport on realizable coefficients by",
             "P2: nonempty atlas family")
    one_line(doc, 22, "The observation map need not",
             "The observation map may be noninjective. For a positive integer h, define",
             "P14: positive delay length", italic_token="h")
    replace_block(doc,23,"upper bound on the hidden dimension",
        "<p>When these statements hold, <i>D</i><sub>h</sub> is unique on <i>V</i><sub>h</sub>. "
        "The history state obeys <i>z</i><sub>t+1</sub> = <i>D</i><sub>h</sub><i>z</i><sub>t</sub>, "
        "and its last output block is <i>y</i><sub>t</sub>. Its iterates determine every later observed "
        "output. If a positive integer <i>d</i> bounds the hidden dimension, <i>h</i> = <i>d</i> "
        "suffices for closure, though a smaller positive <i>h</i> may suffice.</p>",
        "P14: positive dimension bound",bottom_extra=5)
    replace_block(doc, 50, "Fix M finite words",
        "<p>Fix positive integers <i>M</i> and <i>N</i> and choose <i>M</i> finite words before estimation. "
        "For each word, reset to the same initial distribution, execute its action sequence, and record whether "
        "all observations match. Obtain <i>N</i> independent trials per word. Estimates for different words may "
        "be dependent, but each word's <i>N</i> trials must be independent with the declared success probability.</p>",
        "P35: positive experiment and sample counts", bottom_extra=5)
    # The formula-bearing first two lines remain untouched.
    page = doc[60]
    matches = page.search_for("identities. The mixture")
    if len(matches) != 1:
        raise ValueError("Could not uniquely locate the positivity-repair prose")
    rect = matches[0]
    page.add_redact_annot(rect, fill=(1,1,1))
    page.apply_redactions(images=0, graphics=0)
    page.insert_font(fontname="LSMroman", fontfile=str(ROMAN))
    text = "identities. For a mixing weight in [0, 1], the mixture"
    page.insert_text((67.68,179.202), text, fontname="LSMroman", fontsize=11.457,
                     color=(37/255,42/255,51/255))
    changed.setdefault(60, []).append("Positivity repair: convex mixing weight")
    operations.append({"pdf_page":61,"label":"Positivity repair: convex mixing weight",
                       "old_text":"identities. The mixture", "new_text":text})
    b=block(doc[80],"The correction is positive semidefinite")
    replace_box(doc,80,fitz.Rect(67.68,228.32,548.64,262.35),
        "<p>For positive semidefinite <i>X</i>, so is the correction. For "
        "<i>K</i>(<i>u</i>) = <i>K</i><sub>0</sub> + <i>uK</i><sub>1</sub> with scalar "
        "<i>u</i> of finite second moment, it is Var<sub>ν</sub>(<i>u</i>)"
        "<i>K</i><sub>1</sub><i>XK</i><sub>1</sub><sup>T</sup>. A uniform interval of width "
        "<i>h</i> has variance <i>h</i><sup>2</sup>/12.</p>",
        "P57: finite second moment for the affine scalar",old=b[4])


def corrected_markdown(status: dict | None) -> None:
    body_path=SOURCE/"FOUNDATIONS.md"
    generation_state=SOURCE/"GENERATED_SOURCE_STATE.json"
    if generation_state.exists() and body_path.exists():
        expected=json.loads(generation_state.read_text())['last_generated_sha256']
        if sha(body_path)!=expected:
            raise ValueError("FOUNDATIONS.md was edited; refusing to overwrite those source edits")
    original = (SOURCE / "Original_Foundations.md").read_text()
    body = original[original.index("# 1. Three objects") :]
    replacements = {
        "On realizable coefficients, define transport from atlas $a$ to atlas $b$ by":
          "For a nonempty atlas family, define transport on realizable coefficients from atlas $a$ to atlas $b$ by",
        "The observation map need not be injective. Define the length-$h$ observation map":
          "The observation map need not be injective. For a positive integer $h$, define the observation map",
        "If $d$ is an upper bound on the hidden dimension, $h=d$ is sufficient for closure, though a smaller $h$ may suffice.":
          "If a positive integer $d$ bounds the hidden dimension, $h=d$ is sufficient for closure, though a smaller positive $h$ may suffice.",
        "Fix $M$ finite words before estimation.":
          "Fix positive integers $M$ and $N$ and choose $M$ finite words before estimation.",
        "identities. The mixture\n":
          "identities. For $0\\leq\\eta\\leq1$, the mixture\n",
        "For $K(u)=K_0+uK_1$, it equals":
          "For an affine matrix function $K(u)=K_0+uK_1$ with scalar $u$ of finite second moment, it equals",
        "# 100. Frozen release scope and research boundary":
          "# 100. Scope and research boundary",
        " Production PR-LASM 2.3.0 is unchanged. This 0.9.0 edition is a release candidate pending final editorial acceptance and a separate license decision before open-source publication.": ""
    }
    for old,new in replacements.items():
        if body.count(old) != 1:
            raise ValueError(f"Expected one editable-body passage: {old!r}")
        body = body.replace(old,new)
    body=body.replace("../figures/", "../assets/figures/")
    prefix = "# Large Signal Model\n\n## Foundations of realization, refinement and predictive closure\n\nKomorebi P.\n\n"
    prefix += "This mathematical body contains 87 numbered propositions with written proofs. The complete publication also includes its proof register, formal companion, glossary and references. "
    if status:
        partial=status.get('partial_count',0)
        partial_text=('no partial mappings' if partial==0 else 'one partial mapping' if partial==1 else f'{partial} partial mappings')
        prefix += (f"The formal companion records {status['complete_count']} complete mappings, {partial_text}, and "
                   f"{87-status['complete_count']-partial} propositions without a formalization. "
                   "The exact scope and accepted execution evidence are recorded separately in the formal coverage map.\n\n")
    else:
        prefix += "Formal correspondence is reported separately from written proof status.\n\n"
    body_path.write_text(prefix+body)
    generation_state.write_text(json.dumps({'last_generated_sha256':sha(body_path)},indent=2))


def verification_edits(doc: fitz.Document, status: dict) -> None:
    n = status["complete_count"]
    partial = status.get("partial_count", 0)
    remaining = 87-n-partial
    if (not 39 <= n <=87 or len(status["complete_ids"]) != n or remaining<0
        or len(status.get("partial_ids",[]))!=partial
        or set(status["complete_ids"]) & set(status.get("partial_ids",[]))):
        raise ValueError("Invalid formal coverage count")
    partial_phrase=("no partial mappings" if partial==0 else
                    "one partial mapping" if partial==1 else f"{partial} partial mappings")
    replace_block(doc,6,"The accompanying Lean archive",
        f"<p>The accompanying Lean project records complete formal coverage for {n} propositions in their "
        f"stated mapped scopes, {partial_phrase}, and {remaining} propositions without a formalization. "
        "These counts describe manuscript correspondence, not proof difficulty. The kernel checks formal "
        "declarations. Matching those declarations to the English propositions remains a separate reviewed step.</p>",
        "Preface: current formal coverage", bottom_extra=5)
    replace_block(doc,6,"Finite symbolic and numerical checks",
        "<p>Finite symbolic and numerical checks exercise particular examples and certificate replays. They do not "
        "replace general proofs. The formal companion reports the current clean Lean compilation, axiom audit and "
        "replay evidence with their exact scopes. No independent external referee review is claimed.</p>",
        "Preface: current verification provenance",bottom_extra=5)
    replace_block(doc,7,"The proof and evidence register gathers",
        "<p>The proof and evidence register records each proposition's assumptions, principal dependencies "
        "and code counterparts. The formal companion describes the current kernel checks, reproduces two "
        "complete endpoint modules and summarizes the additional formal results. The glossary and references "
        "close the volume. The source package retains the original manuscripts, scientific figures, reference "
        "laboratory, formal sources and verification records.</p>",
        "Reading route: current formal companion",bottom_extra=5)
    replace_block(doc,129,"The principal dependencies are curated",
        "<p>The dependency register is curated rather than extracted from Lean proof terms. The source "
        "package retains the full register, statement hashes, code locations and current coverage map. "
        "Hashes establish identity rather than mathematical truth.</p>",
        "Evidence-register introduction: current coverage",bottom_extra=5)
    replace_block(doc,152,"The archived formal project contains",
        "<p>"+html.escape(status["inventory_paragraph"])+"</p>",
        "Formal companion: current inventory",bottom_extra=5)
    replace_block(doc,152,"The archived cumulative run records",
        "<p>"+html.escape(status["execution_paragraph"])+"</p>",
        "Formal companion: current execution",bottom_extra=5)
    replace_block(doc,152,"These are archived verification results",
        "<p>The current verification records distinguish fresh kernel checks from inherited evidence. "
        "The source package retains both. The manuscript correspondence and internal proof review are "
        "separate from kernel acceptance, and no independent external referee or second proof assistant is claimed.</p>",
        "Formal companion: evidence scope",bottom_extra=5)
    page=doc[152]
    # Replace only the right-hand coverage cells, preserving the table grid and labels.
    noun=lambda count: f"{count} proposition" + ("s" if count!=1 else "")
    cells={"39 propositions":noun(n), "0 propositions":noun(partial),
           "48 propositions":noun(remaining),
           "1,117 supporting and example theorems":status["theorem_cell"],
           "81 isolated checks":status["rejection_cell"], "Archived scope":"Current scope"}
    table_updates=[]
    for old,new in cells.items():
        hits=page.search_for(old)
        if len(hits)!=1:raise ValueError(f"Missing unique table cell: {old}")
        rect=hits[0]
        # Preserve the original text baseline with the matching font.
        spans=[s for b in page.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans']
               if old in s['text']]
        baseline=spans[0]['origin'][1]
        table_updates.append((old,new,rect,baseline,'Bold' in spans[0]['font']))
    for old,new,rect,baseline,is_bold in table_updates:
        page.add_redact_annot(rect,fill=(1,1,1));page.apply_redactions(images=0,graphics=0)
        fontname='LSMbold' if is_bold else 'LSMroman'
        page.insert_font(fontname=fontname,fontfile=str(BOLD if is_bold else ROMAN))
        page.insert_text((rect.x0,baseline),new,fontname=fontname,fontsize=11.457,color=(37/255,42/255,51/255))
    changed.setdefault(152,[]).append("Coverage table")
    # Replace the scope summary underneath the table without altering its continuation.
    replace_block(doc,152,"The complete mappings are",
        "<p>"+html.escape(status["coverage_paragraph"])+"</p>",
        "Formal companion: mapped proposition list",bottom_extra=5)
    # Update the evidence-register lines for newly proved propositions.
    for entry in status["new_entries"]:
        title_i=entry["register_pdf_page"]-1
        i=entry.get("coverage_pdf_page",entry["register_pdf_page"])-1
        if i not in (title_i,title_i+1):
            raise ValueError("Coverage line must be on the title page or its continuation")
        pg=doc[i]
        title=f"P{entry['id']}."
        target=next(b for b in doc[title_i].get_text("blocks") if b[4].startswith(title))
        blocks=pg.get_text("blocks")
        later=[b for b in blocks if (i>title_i or b[1]>target[1]) and b[4].startswith("Formal coverage.")]
        if not later:raise ValueError(f"No coverage line after {title}")
        b=min(later,key=lambda b:b[1])
        hits=[r for r in pg.search_for("Not formalized in the archive.")
              if abs(r.y0-b[1])<2]
        if len(hits)!=1:raise ValueError(f"No unformalized register phrase after {title}")
        rect=hits[0]
        spans=[s for d in pg.get_text('dict')['blocks'] for l in d.get('lines',[]) for s in l['spans']
               if "Not formalized in the archive." in s['text'] and abs(s['bbox'][1]-b[1])<2]
        baseline=spans[0]['origin'][1]
        pg.add_redact_annot(rect,fill=(1,1,1));pg.apply_redactions(images=0,graphics=0)
        pg.insert_font(fontname='LSMroman',fontfile=str(ROMAN))
        pg.insert_text((rect.x0,baseline),entry['register_text'],fontname='LSMroman',fontsize=11.457,
                       color=(37/255,42/255,51/255))
        changed.setdefault(i,[]).append(f"Evidence register P{entry['id']}")
        operations.append({"pdf_page":i+1,"label":f"Evidence register P{entry['id']}",
                           "old_text":"Not formalized in the archive.","new_text":entry['register_text']})
    guide="<p><b>Additional formal coverage</b></p>"
    guide_spacing=float(status.get("guide_spacing_pt",7))
    if not 4 <= guide_spacing <= 10:
        raise ValueError("Guide spacing outside the reviewed readable range")
    guide_entries=status.get("guide_entries",status["new_entries"])
    guide_ids=[i for e in guide_entries for i in e.get("ids",[e["id"]])]
    if len(guide_ids)!=len(set(guide_ids)) or set(guide_ids)!={e["id"] for e in status["new_entries"]}:
        raise ValueError("Guide groups must cover each registered mapping update exactly once")
    for e in guide_entries:
        label=e.get("label",f"P{e['id']}")
        guide+=f"<p style='margin-top:{guide_spacing}pt'><b>"+html.escape(label)+". "+html.escape(e['title'])+".</b> "+html.escape(e['guide_text'])+"</p>"
    guide+="<p style='margin-top:10pt'>"+html.escape(status["guide_boundary"])+"</p>"
    replace_box(doc,166,fitz.Rect(67.68,120,548.64,710),guide,
                "Additional formal scope guide",size=10.4,leading=14,align="justify")
    (SOURCE/"FORMAL_COMPANION_UPDATE.md").write_text(status["markdown_guide"])


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    status_path=SOURCE/"FORMAL_STATUS.json"
    status=json.loads(status_path.read_text()) if status_path.exists() else None
    doc=fitz.open(ORIGINAL)
    original_text=[p.get_text() for p in doc]
    body_edits(doc)
    if status:verification_edits(doc,status)
    corrected_markdown(status)
    # Prior content credentials cannot attest to a modified publication.
    for name in doc.embfile_names():doc.embfile_del(name)
    metadata=doc.metadata
    metadata.update({"title":"Realization Calculus: Large Signal Model","author":"Komorebi P.",
                     "subject":"Foundations of realization, refinement and predictive closure"})
    doc.set_metadata(metadata)
    fitz.TOOLS.reset_mupdf_warnings()
    display_errors=fitz.TOOLS.mupdf_display_errors()
    fitz.TOOLS.mupdf_display_errors(False)
    try:
        doc.save(OUTPUT,garbage=4,deflate=True,no_new_id=True)
    finally:
        fitz.TOOLS.mupdf_display_errors(display_errors)
    inherited_save_diagnostics=fitz.TOOLS.mupdf_warnings()
    doc.close()
    check=fitz.open(OUTPUT)
    if len(check)!=174:raise ValueError("Page sequence changed")
    original_toc=fitz.open(ORIGINAL).get_toc()
    if check.get_toc()!=original_toc:raise ValueError("Bookmark titles or destinations changed")
    unexpected=[i+1 for i,p in enumerate(check) if i not in changed and p.get_text()!=original_text[i]]
    if unexpected:raise ValueError(f"Unexpected text changes: {unexpected}")
    original_for_render=fitz.open(ORIGINAL)
    render_changed=[]
    for i,p in enumerate(check):
        if i in changed:continue
        a=original_for_render[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
        b=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
        if a.samples!=b.samples:render_changed.append(i+1)
    original_for_render.close()
    if render_changed:raise ValueError(f"Unexpected visual changes: {render_changed}")
    outside=[]
    for i,p in enumerate(check):
        for b in p.get_text('blocks'):
            if b[0]<-1 or b[1]<-1 or b[2]>613 or b[3]>793:outside.append(i+1)
    if outside:raise ValueError(f"Text outside page: {outside}")
    # Use a fresh process so MuPDF's coalesced diagnostics from the original
    # document cannot be mistaken for a warning from the normalized output.
    structure_check=subprocess.run([sys.executable,"-c",
        "import fitz,json,sys; d=fitz.open(sys.argv[1]); "
        "d.tobytes(garbage=4,deflate=True,no_new_id=True); "
        "print(json.dumps(fitz.TOOLS.mupdf_warnings()))",str(OUTPUT)],
        capture_output=True,text=True,check=True)
    output_structure_diagnostics=json.loads(structure_check.stdout)
    if 'format error' in output_structure_diagnostics:
        raise ValueError(f"Output structure diagnostics: {output_structure_diagnostics}")
    ready=bool(status) and status.get('execution_status')=='PASS'
    report={"status":"PASS" if ready else "LAYOUT_PASS_EXECUTION_PENDING",
            "source_sha256":sha(ORIGINAL),"output_sha256":sha(OUTPUT),
            "page_count":len(check),"original_bookmarks":len(fitz.open(ORIGINAL).get_toc()),
            "output_bookmarks":len(check.get_toc()),"changed_pages":{str(k+1):v for k,v in changed.items()},
            "bookmark_titles_and_destinations_identical":True,
            "unchanged_pages_text_identical":174-len(changed),
            "unchanged_pages_pixel_identical_at_72dpi":174-len(changed),
            "out_of_page_text":outside,
            "source_save_diagnostics_normalized":inherited_save_diagnostics,
            "output_repack_diagnostics":output_structure_diagnostics,
            "formal_status_integrated":bool(status),"operations":operations}
    (BUILD/"MONOGRAPH_VALIDATION.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps({k:v for k,v in report.items() if k!='operations'},indent=2))


if __name__=="__main__":main()
