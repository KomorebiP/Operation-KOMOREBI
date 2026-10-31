"""Faithful HTML chapters of the retained Proof Path Theory monograph.

Each reading page selects a contiguous line range of the existing TeX. The
printer-only commands below are translated for screen reading, not interpreted
as new claims. No source manuscript or recorded proof status is changed.
"""
import re
import hashlib
from pathlib import Path

WORK = "proof-path-theory"
BASE = "monographs/proof-path-theory/docs/"
MAIN = BASE + "Proof_Path_Theory.tex"
INDEX = "read/proof-path-theory/index.html"
BIB_PAGE = "read/proof-path-theory/references.html"

# Start line, authored title, kind, stable page name. Section boundaries are
# manually reviewed against the retained monograph, not inferred from prose.
MARKERS = [[187,"Preface","section","preface"],[204,"Reading map","section","reading-map"],[227,"Proof fields and certificates","part","part-1-proof-fields-and-certificates"],[229,"Introduction","section","introduction"],[270,"Claim types and logical boundaries","section","claim-types-and-logical-boundaries"],[298,"Typed proof fields","section","typed-proof-fields"],[365,"The ambient proof field and the meaning of failure","section","the-ambient-proof-field-and-the-meaning-of-failure"],[408,"Certificates and verification closure","section","certificates-and-verification-closure"],[479,"Alternative derivations and certificate complexity","section","alternative-derivations-and-certificate-complexity"],[522,"Certified paths as a category","section","certified-paths-as-a-category"],[572,"Coherent realization and information","part","part-2-coherent-realization-and-information"],[574,"Komorebi Space, realization fibers, and informative questions","section","komorebi-space-realization-fibers-and-informative-questions"],[661,"A checked realization bridge for proof fields","section","a-checked-realization-bridge-for-proof-fields"],[1251,"Compression, representation, and memory","part","part-3-compression-representation-and-memory"],[1253,"Compression relative to a task family","section","compression-relative-to-a-task-family"],[1446,"Endpoint, audit, and discovery equivalence","section","endpoint-audit-and-discovery-equivalence"],[1474,"Vector-valued loss","section","vector-valued-loss"],[1514,"Compression debt","section","compression-debt"],[1559,"A proof ecology rather than one ideal form","section","a-proof-ecology-rather-than-one-ideal-form"],[1587,"Proof compilers and shared ledgers","section","proof-compilers-and-shared-ledgers"],[1615,"Latent bridge graphs","section","latent-bridge-graphs"],[1680,"Retention under a budget","section","retention-under-a-budget"],[1756,"Revision, review, and inquiry","part","part-4-revision-review-and-inquiry"],[1758,"Versioned proof objects","section","versioned-proof-objects"],[1818,"Evidence ledgers and provenance","section","evidence-ledgers-and-provenance"],[1868,"Correlated review","section","correlated-review"],[1953,"Shared interpretation, review dependence, and identification","section","shared-interpretation-review-dependence-and-identification"],[1995,"Verification bandwidth and audit queues","section","verification-bandwidth-and-audit-queues"],[2037,"Recursive proof cubes and expansion depth","section","recursive-proof-cubes-and-expansion-depth"],[2096,"Examples, implementation, and boundaries","part","part-5-examples-implementation-and-boundaries"],[2098,"Worked finite examples","section","worked-finite-examples"],[2189,"Reference implementation","section","reference-implementation"],[2262,"What the theory establishes","section","what-the-theory-establishes"],[2294,"Limitations and claim boundaries","section","limitations-and-claim-boundaries"],[2314,"Open theorem program","section","open-theorem-program"],[2381,"Conclusion","section","conclusion"],[2406,"Notation and hypotheses","section","notation-and-hypotheses"],[2450,"Theorem ledger","section","theorem-ledger"],[2522,"Reproduction and verification records","section","reproduction-and-verification-records"],[2583,"A complete minimal proof-field record","section","a-complete-minimal-proof-field-record"]]
CHAPTERS = [
    dict(
        work=WORK, source=MAIN,
        url=INDEX.replace("index.html", slug + ".html"),
        title=title, start_line=start,
        end_line=MARKERS[i+1][0] - 1 if i+1 < len(MARKERS) else 2673,
        section_heading=(kind == "section"),
        kind=kind,
    )
    for i, (start, title, kind, slug) in enumerate(MARKERS)
]
BOOK = dict(
    work=WORK, label="Proof Path Theory", base=BASE, main=MAIN,
    bib=MAIN, inline_bibliography=True, index=INDEX, bib_page=BIB_PAGE,
    title="Certificates, compression, discovery fields, and mathematical memory",
    chapters=CHAPTERS, main_chapters=sum(s["kind"] == "section" for s in CHAPTERS),
    custom_reader="proof_path", figure_directory="figures",
    number_floats=True, statement_navigation=True,
    required_macros={"Pcal", "Jcal", "Qcal", "Rcal", "Ecal", "Vcal", "Ccal",
                     "Bcal", "Tcal", "Fcal", "Anc", "AncL", "Desc", "Reach",
                     "Cost", "Loss", "Debt", "argmin", "argmax"},
    reading_introduction=(
        "Read the full manuscript online, from its preface and five parts to "
        "the formal ledger and reproducing examples. This presentation preserves "
        "source lines and the original mathematical expressions. The full PDF "
        "and visual sampler remain available alongside it."
    ),
    part_figures={
        1: "fig_14_ambient_field.png",
        2: "fig_17_binary_cube.png",
        3: "fig_20_compression_collision.png",
        4: "fig_21_review_error_floor.png",
        5: "fig_13_repository_workflow.png",
    },
)


def source_specs(load):
    """Stop on a changed section order, shifted line or incomplete coverage."""
    main = load(MAIN)
    lines = main.splitlines()
    if len(lines) != 2673 or len(MARKERS) != 40:
        raise ValueError("Review Proof Path Theory manuscript length and section boundaries")
    if lines[157] != r"\begin{document}" or lines[2672] != r"\end{document}":
        raise ValueError("Proof Path Theory document boundaries changed")
    if MARKERS[0][0] != 187 or CHAPTERS[-1]["end_line"] != 2673:
        raise ValueError("Proof Path Theory reading span changed")
    for start, title, kind, slug in MARKERS:
        line = lines[start - 1]
        if kind == "section":
            match = re.fullmatch(r"\\section\*?\{([^{}]+)\}", line)
            if not match or match[1] != title:
                raise ValueError("Review Proof Path Theory section " + title)
        else:
            if not line.startswith(r"\monographpart{" + title + "}"):
                raise ValueError("Review Proof Path Theory part " + title)
    actual = [(i+1, "section" if r"\section" in line[:8] else "part")
              for i, line in enumerate(lines)
              if i >= 186 and (re.match(r"\\section\*?\{", line)
                               or line.startswith(r"\monographpart{"))]
    expected = [(start, kind) for start, _, kind, _ in MARKERS]
    if actual != expected:
        raise ValueError("Proof Path Theory reading section order changed")
    for i, spec in enumerate(CHAPTERS):
        if i and CHAPTERS[i-1]["end_line"] + 1 != spec["start_line"]:
            raise ValueError("Proof Path Theory chapters overlap or omit source lines")
    return CHAPTERS


def _mask(text):
    return "".join("\n" if c == "\n" else " " for c in text)


def _rewrite(text, name, count, change):
    from readable_chapters import group
    pattern = re.compile(r"\\" + re.escape(name) + r"\b")
    position = 0
    while match := pattern.search(text, position):
        end, args = match.end(), []
        for _ in range(count):
            while end < len(text) and text[end].isspace():
                end += 1
            value, end = group(text, end)
            args.append(value)
        original = text[match.start():end]
        replacement = change(*args)
        missing = original.count("\n") - replacement.count("\n")
        if missing < 0:
            raise ValueError("Reading normalization shifts source lines: " + name)
        replacement += "\n" * missing
        text = text[:match.start()] + replacement + text[end:]
        position = match.start() + len(replacement)
    return text


def _style_groups(text):
    """Remove printer-only typography inside *textual* TeX groups."""
    from readable_chapters import group
    pattern = re.compile(r"\{\\(?:sffamily|footnotesize|small|bfseries)\b")
    position = 0
    while match := pattern.search(text, position):
        body, end = group(text, match.start())
        prefix = re.match(
            r"(?:\\(?:sffamily|bfseries|footnotesize|small)\b|\\color\{[A-Za-z0-9]+\})+",
            body
        )
        if not prefix:
            raise ValueError("Unsupported formatted prose group")
        content = body[prefix.end():]
        replacement = (r"\textbf{" + content + "}") if r"\bfseries" in prefix[0] else content
        original = text[match.start():end]
        if original.count("\n") != replacement.count("\n"):
            raise ValueError("A formatted prose group changed source line count")
        text = text[:match.start()] + replacement + text[end:]
        position = match.start() + len(replacement)
    return text


def normalize(source):
    """Translate only print-oriented wrappers, preserving math and line counts."""
    from readable_chapters import clean_tex
    text = clean_tex(source)
    count = text.count("\n")
    text = _rewrite(
        text, "monographpart", 3,
        lambda name, short, subtitle: r"\part{" + name + "} " + subtitle
    )
    text = _rewrite(
        text, "studyhead", 2,
        lambda number, title: r"\paragraph*{Visual study " + number + ": " + title + "}"
    )
    text = _rewrite(
        text, "calloutbox", 2,
        lambda title, body: r"\begin{readerroadmap}[title={" + title + "}]"
        + body + r"\end{readerroadmap}"
    )
    # Introductory print columns become ordinary sequential reading paragraphs.
    text = re.sub(
        r"\\begin\{minipage\}\[t\]\{0\.47\\linewidth\}(.*?)\\end\{minipage\}",
        lambda m: m[1] + "\n" * (m[0].count("\n") - m[1].count("\n")),
        text, flags=re.S
    )
    # Figure locations, paper headers and small-type styles do not change the text.
    text = re.sub(r"\\begin\{(figure|table)\}\[(?:htbp|H)\]", r"\\begin{\1}", text)
    text = text.replace(r"\includegraphics[width=\linewidth]",
                        r"\includegraphics[width=.96\linewidth]")
    text = text.replace(r"label=\textup{(\roman*)}", r"label=(\roman*)")
    text = text.replace(r"\\[0pt]", r"\\")
    text = re.sub(r"\\(?:markboth)\{[^{}]*\}\{[^{}]*\}", lambda m: _mask(m[0]), text)
    text = re.sub(r"\\renewcommand\{\\arraystretch\}\{[0-9.]+\}",
                  lambda m: _mask(m[0]), text)
    text = re.sub(r"\\(?:smallskip|bigskip|medskip|FloatBarrier|protect)\b",
                  lambda m: _mask(m[0]), text)
    text = _style_groups(text)
    if text.count("\n") != count:
        raise ValueError("Proof Path Theory HTML conversion changed source line count")
    return text


def prepare_book(reader, config):
    from readable_chapters import (Chapter, chapter_text, manuscript_macros,
                                   manuscript_bibliography, original_math)
    def load(path):
        record = reader.add(path)
        if not record:
            raise ValueError("Missing receipt-bound Proof Path Theory manuscript: " + path)
        return reader.site.read_source(record).decode("utf-8-sig")
    main = load(MAIN)
    source_specs(load)
    macros = manuscript_macros(main, config["required_macros"])
    references = manuscript_bibliography(main)
    state = {"number_floats": True}
    labels, chapters = {}, []
    for spec in CHAPTERS:
        source = chapter_text(main, spec)
        formatted = normalize(source)
        if original_math(source) != original_math(formatted):
            raise ValueError("Proof Path Theory math was changed by layout translation")
        chapter = Chapter(formatted, macros, state=state, check_refs=False)
        chapter.url, chapter.base = spec["url"], BASE
        chapter.bibliography_url = BIB_PAGE
        for key, node in chapter.labels.items():
            if key in labels:
                raise ValueError("Repeated Proof Path Theory label: " + key)
            node["url"] = chapter.url
            labels[key] = node
        state = {key: getattr(chapter, key)
                 for key in ("section", "appendix", "part", "subsection",
                             "subsubsection", "counter", "section_prefix",
                             "figure", "table", "number_floats")}
        chapters.append((spec, reader.site.read_source(reader.records[MAIN]), chapter))
    for _, _, chapter in chapters:
        chapter.labels = labels
        chapter.validate_references()
        chapter.citations = {
            ref["key"]: (ref["key"], chapter.relative(BIB_PAGE) + "#ref-" + ref["key"])
            for ref in references
        }
    return dict(config=config, chapters=chapters, references=references,
                macros=macros, main=main)
