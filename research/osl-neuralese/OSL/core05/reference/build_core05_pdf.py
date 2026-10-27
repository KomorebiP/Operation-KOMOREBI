#!/usr/bin/env python3
"""Build the concise OSL-Core 0.5 semantic-independence technical update."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import wrap

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "OSL_Core_0.5_Semantic_Independence_Technical_Update.pdf"

W, H = letter
M = 48

INK = HexColor("#14212B")
NAVY = HexColor("#173A4A")
TEAL = HexColor("#147D7A")
MINT = HexColor("#DDF2EC")
SKY = HexColor("#E8F2F6")
CORAL = HexColor("#E56B58")
GOLD = HexColor("#D9A441")
PAPER = HexColor("#F8F7F2")
WHITE = HexColor("#FFFFFF")
MUTED = HexColor("#5C6B73")
LINE = HexColor("#C9D4D8")
SOFT = HexColor("#EFF3F2")


def load_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def register_fonts() -> None:
    base = Path("/usr/share/fonts/truetype/dejavu")
    pdfmetrics.registerFont(TTFont("DV", str(base / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DV-Bold", str(base / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DV-Mono", str(base / "DejaVuSansMono.ttf")))
    pdfmetrics.registerFont(TTFont("DV-Mono-Bold", str(base / "DejaVuSansMono-Bold.ttf")))


def paragraph(c: canvas.Canvas, text: str, x: float, y: float, width: float,
              size: float = 9.2, leading: float | None = None,
              color=INK, font: str = "DV", before: float = 0,
              bullet_indent: float = 0) -> float:
    leading = leading or size * 1.43
    style = ParagraphStyle(
        "p",
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=0,
        leftIndent=bullet_indent,
        firstLineIndent=-bullet_indent if bullet_indent else 0,
    )
    p = Paragraph(text, style)
    _, ph = p.wrap(width, H)
    p.drawOn(c, x, y - before - ph)
    return y - before - ph


def page_base(c: canvas.Canvas, page: int, section: str) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(TEAL)
    c.rect(0, H - 7, W, 7, stroke=0, fill=1)
    c.setStrokeColor(LINE)
    c.line(M, 32, W - M, 32)
    c.setFont("DV", 7.4)
    c.setFillColor(MUTED)
    c.drawString(M, 19, "OSL-Core 0.5 · Semantic Independence")
    c.drawRightString(W - M, 19, f"{section}   {page:02d}")


def heading(c: canvas.Canvas, kicker: str, title: str, subtitle: str | None = None) -> float:
    c.setFont("DV-Bold", 8.2)
    c.setFillColor(TEAL)
    c.drawString(M, H - 48, kicker.upper())
    c.setFont("DV-Bold", 24)
    c.setFillColor(INK)
    c.drawString(M, H - 81, title)
    y = H - 101
    if subtitle:
        y = paragraph(c, subtitle, M, y, W - 2 * M, 9.2, 13.2, MUTED)
    c.setStrokeColor(LINE)
    c.line(M, y - 14, W - M, y - 14)
    return y - 32


def rounded_box(c: canvas.Canvas, x: float, y: float, w: float, h: float,
                fill=WHITE, stroke=LINE, radius: float = 10) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)


def metric(c: canvas.Canvas, x: float, y: float, w: float,
           value: str, label: str, accent=TEAL) -> None:
    rounded_box(c, x, y, w, 74, WHITE, LINE, 9)
    c.setFillColor(accent)
    c.rect(x, y, 5, 74, stroke=0, fill=1)
    c.setFont("DV-Bold", 20)
    c.setFillColor(INK)
    c.drawString(x + 16, y + 40, value)
    c.setFont("DV", 7.5)
    c.setFillColor(MUTED)
    c.drawString(x + 16, y + 20, label.upper())


def label(c: canvas.Canvas, text: str, x: float, y: float,
          fill=SKY, color=NAVY) -> float:
    c.setFont("DV-Bold", 7.2)
    width = pdfmetrics.stringWidth(text, "DV-Bold", 7.2) + 15
    c.setFillColor(fill)
    c.roundRect(x, y - 5, width, 17, 8.5, stroke=0, fill=1)
    c.setFillColor(color)
    c.drawCentredString(x + width / 2, y + 0.5, text)
    return width


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float,
          color=TEAL) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.5)
    c.line(x1, y1, x2, y2)
    c.line(x2, y2, x2 - 6, y2 + 3)
    c.line(x2, y2, x2 - 6, y2 - 3)


def table(c: canvas.Canvas, x: float, y_top: float, widths: list[float],
          headers: list[str], rows: list[list[str]], row_heights: list[float] | None = None,
          font_size: float = 7.6) -> float:
    header_h = 28
    total_w = sum(widths)
    c.setFillColor(NAVY)
    c.roundRect(x, y_top - header_h, total_w, header_h, 7, stroke=0, fill=1)
    cx = x
    for header, width in zip(headers, widths):
        c.setFont("DV-Bold", 7.2)
        c.setFillColor(WHITE)
        c.drawString(cx + 8, y_top - 18, header.upper())
        cx += width
    y = y_top - header_h
    row_heights = row_heights or [38] * len(rows)
    for idx, (row, rh) in enumerate(zip(rows, row_heights)):
        fill = WHITE if idx % 2 == 0 else SOFT
        c.setFillColor(fill)
        c.setStrokeColor(LINE)
        c.rect(x, y - rh, total_w, rh, stroke=1, fill=1)
        cx = x
        for col, (value, width) in enumerate(zip(row, widths)):
            if col:
                c.line(cx, y, cx, y - rh)
            paragraph(c, value, cx + 7, y - 8, width - 14, font_size,
                      font_size * 1.25, INK if col else NAVY,
                      font="DV-Bold" if col == 0 else "DV")
            cx += width
        y -= rh
    return y


def bullet(c: canvas.Canvas, text: str, x: float, y: float, width: float,
           color=INK, dot=TEAL, size: float = 8.7) -> float:
    c.setFillColor(dot)
    c.circle(x + 3.2, y - 6.5, 2.2, stroke=0, fill=1)
    return paragraph(c, text, x + 14, y, width - 14, size, size * 1.4, color) - 5


def finish(c: canvas.Canvas) -> None:
    c.showPage()


def build() -> None:
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    conf = load_json("CORE05_CONFORMANCE_REPORT.json")
    sem = load_json("CORE05_SEMANTIC_REPORT.json")
    focused = load_json("CORE05_FOCUSED_REPORT.json")
    tests = load_json("TEST_REPORT.json")
    bridge = load_json("CORE05_DISCOVERY_BRIDGE_REPORT.json")

    c = canvas.Canvas(str(OUTPUT), pagesize=letter, pageCompression=1)
    c.setTitle("OSL-Core 0.5 Semantic Independence — Concise Technical Update")
    c.setAuthor("Komorebi P.")
    c.setSubject("Executable semantic-independence update for Operator-Symbolic Languages")
    c.setKeywords("OSL, operator-symbolic language, receipts, independent verification, provenance")

    # 1 — Cover
    page_base(c, 1, "Technical update")
    c.setFillColor(NAVY)
    c.roundRect(M, H - 355, W - 2 * M, 260, 18, stroke=0, fill=1)
    c.setFillColor(TEAL)
    c.circle(W - 92, H - 153, 54, stroke=0, fill=1)
    c.setStrokeColor(Color(1, 1, 1, alpha=0.45))
    c.setLineWidth(1.2)
    for r in (18, 31, 44):
        c.circle(W - 92, H - 153, r, stroke=1, fill=0)
    c.setFillColor(WHITE)
    c.circle(W - 92, H - 153, 5, stroke=0, fill=1)
    c.setFont("DV-Bold", 9)
    c.setFillColor(MINT)
    c.drawString(M + 28, H - 132, "OPERATOR-SYMBOLIC LANGUAGES")
    c.setFont("DV-Bold", 32)
    c.setFillColor(WHITE)
    c.drawString(M + 28, H - 184, "OSL-Core 0.5")
    c.setFont("DV-Bold", 20)
    c.drawString(M + 28, H - 218, "Semantic Independence")
    c.setFont("DV", 10)
    c.setFillColor(MINT)
    c.drawString(M + 28, H - 252, "Concise executable-language update · 01 September 2026")
    c.setFont("DV", 8.3)
    c.drawString(M + 28, H - 284, "Komorebi P.  ·  Core release v0.1.0")

    y = H - 392
    c.setFont("DV-Bold", 14)
    c.setFillColor(INK)
    c.drawString(M, y, "The result in one sentence")
    y = paragraph(
        c,
        "Core 0.5 keeps the Core 0.4 source grammar and receipt-v2 lifecycle, while adding separate semantic evaluators for numerical operators, contracts, sessions, metadata-facing state, and the receipt-verification intrinsic.",
        M, y - 14, W - 2 * M, 10.2, 15.0, MUTED,
    )
    y -= 24
    gap = 10
    mw = (W - 2 * M - 3 * gap) / 4
    metric(c, M, y - 74, mw, f"{conf['passed_count']}/{conf['program_count']}", "corpus programs", TEAL)
    metric(c, M + (mw + gap), y - 74, mw, f"{tests['pytest_passed']}/{tests['pytest_passed']}", "tests passed", NAVY)
    metric(c, M + 2 * (mw + gap), y - 74, mw, f"{focused['passed_count']}/{focused['case_count']}", "focused gate", CORAL)
    metric(c, M + 3 * (mw + gap), y - 74, mw, f"{conf['receipt_count']:,}", "native receipts", GOLD)
    y -= 108
    rounded_box(c, M, y - 91, W - 2 * M, 91, MINT, TEAL, 10)
    c.setFont("DV-Bold", 9.2)
    c.setFillColor(TEAL)
    c.drawString(M + 16, y - 21, "STATUS")
    c.setFont("DV-Bold", 15)
    c.setFillColor(INK)
    c.drawString(M + 16, y - 48, "All packaged release gates pass.")
    paragraph(c, "Finite executable evidence—not a universal theorem or proof-assistant verification.",
              M + 16, y - 57, W - 2 * M - 32, 8.3, 12, MUTED)
    finish(c)

    # 2 — Architectural delta
    page_base(c, 2, "Architecture")
    y = heading(c, "01 · Architectural delta", "From trace to checked semantics",
                "The new layer does not merely re-run the interpreter. Each domain report reconstructs its own receipt-facing state and is aggregated beside the protected-state kernel.")
    box_w, box_h, gap = 142, 82, 28
    x1, x2, x3 = M, M + box_w + gap, M + 2 * (box_w + gap)
    yb = y - 108
    for x, fill in [(x1, SKY), (x2, MINT), (x3, WHITE)]:
        rounded_box(c, x, yb, box_w, box_h, fill, LINE, 9)
    c.setFont("DV-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString(x1 + 14, yb + 56, "SOURCE PROGRAM")
    c.setFont("DV-Mono", 7.2)
    c.setFillColor(MUTED)
    c.drawString(x1 + 14, yb + 35, "typed statements")
    c.drawString(x1 + 14, yb + 21, "+ expected outcome")
    c.setFont("DV-Bold", 10)
    c.setFillColor(TEAL)
    c.drawString(x2 + 14, yb + 56, "CORE 0.5 RUNTIME")
    c.setFont("DV", 7.3)
    c.setFillColor(MUTED)
    c.drawString(x2 + 14, yb + 35, "append-only receipt v2")
    c.drawString(x2 + 14, yb + 21, "terminal + final state")
    c.setFont("DV-Bold", 10)
    c.setFillColor(CORAL)
    c.drawString(x3 + 14, yb + 56, "CHECKED RESULT")
    c.setFont("DV", 7.3)
    c.setFillColor(MUTED)
    c.drawString(x3 + 14, yb + 35, "base kernel + domains")
    c.drawString(x3 + 14, yb + 21, "fail-closed aggregation")
    arrow(c, x1 + box_w + 5, yb + box_h / 2, x2 - 6, yb + box_h / 2)
    arrow(c, x2 + box_w + 5, yb + box_h / 2, x3 - 6, yb + box_h / 2)
    y = yb - 36
    c.setFont("DV-Bold", 12)
    c.setFillColor(INK)
    c.drawString(M, y, "Independent coverage added in 0.5")
    y -= 19
    domain_rows = [
        ("NUM", "spaces · vectors · operators", "apply, transport, residual checks"),
        ("CTR", "temporal contracts", "deadlines, violations, finalization"),
        ("SES", "finite protocol graphs", "verification, advance, terminal state"),
        ("META", "metadata-facing state", "secret digests, publish, show binding"),
        ("INT", "receipt intrinsic", "exact-prefix verify_receipts report"),
    ]
    for i, (code, name, detail) in enumerate(domain_rows):
        ry = y - i * 55
        rounded_box(c, M, ry - 40, W - 2 * M, 44, WHITE if i % 2 == 0 else SOFT, LINE, 7)
        c.setFillColor(TEAL if i < 3 else NAVY)
        c.roundRect(M + 10, ry - 30, 42, 24, 12, stroke=0, fill=1)
        c.setFont("DV-Bold", 7.5)
        c.setFillColor(WHITE)
        c.drawCentredString(M + 31, ry - 21.5, code)
        c.setFont("DV-Bold", 9)
        c.setFillColor(INK)
        c.drawString(M + 66, ry - 17, name)
        c.setFont("DV", 7.7)
        c.setFillColor(MUTED)
        c.drawString(M + 268, ry - 17, detail)
    y = y - len(domain_rows) * 55 - 8
    rounded_box(c, M, y - 81, W - 2 * M, 81, SKY, NAVY, 9)
    c.setFont("DV-Bold", 9)
    c.setFillColor(NAVY)
    c.drawString(M + 14, y - 19, "WHAT REMAINS SHARED")
    paragraph(c, "The base kernel, metadata verifier, and intrinsic verifier still rely on primary parsing/static components. Python, NumPy, canonical serialization, and SHA-256 remain inside the trusted computing base.",
              M + 14, y - 29, W - 2 * M - 28, 8.2, 12.2, INK)
    finish(c)

    # 3 — Language and evidence contract
    page_base(c, 3, "Language contract")
    y = heading(c, "02 · Language contract", "Stable syntax, stricter values",
                "Core 0.5 is an evidence-profile evolution: the source grammar remains compatible while numeric and declaration edge cases now fail explicitly.")
    left_w = 294
    rounded_box(c, M, y - 228, left_w, 228, NAVY, NAVY, 10)
    c.setFont("DV-Bold", 8.2)
    c.setFillColor(MINT)
    c.drawString(M + 16, y - 23, "SMALL OSL PROGRAM")
    code = [
        "module geo",
        "space V dim 2",
        "vector x in V values [1,0]",
        "operator P : V -> V kind projector matrix [[1,0],[0,0]]",
        "apply y = P(x)",
        "check_projector P tolerance 1e-12",
        "assert vector y approx [1,0] tolerance 1e-12",
    ]
    c.setFont("DV-Mono", 6.75)
    c.setFillColor(WHITE)
    cy = y - 50
    for line in code:
        c.drawString(M + 16, cy, line)
        cy -= 20
    rx = M + left_w + 18
    rw = W - M - rx
    c.setFont("DV-Bold", 12)
    c.setFillColor(INK)
    c.drawString(rx, y - 2, "Receipt lifecycle")
    lifecycle = [
        ("1", "program_open", "exact source commitment"),
        ("2", "parse + static", "AST and report binding"),
        ("3", "statement spans", "effects and semantic deltas"),
        ("4", "one terminal", "complete or reject, last"),
    ]
    ly = y - 30
    for num, title, sub in lifecycle:
        c.setFillColor(TEAL)
        c.circle(rx + 12, ly - 7, 12, stroke=0, fill=1)
        c.setFont("DV-Bold", 8)
        c.setFillColor(WHITE)
        c.drawCentredString(rx + 12, ly - 10, num)
        c.setFont("DV-Bold", 8.4)
        c.setFillColor(INK)
        c.drawString(rx + 33, ly - 4, title)
        c.setFont("DV", 6.9)
        c.setFillColor(MUTED)
        c.drawString(rx + 33, ly - 17, sub)
        ly -= 50
    y -= 264
    c.setFont("DV-Bold", 12)
    c.setFillColor(INK)
    c.drawString(M, y, "Hardening in this release")
    y -= 20
    rows = [
        ["Operator kinds", "Allowlist: linear, projector, transport, external", "Unknown kind rejected"],
        ["Names", "Transport results, secrets, and metadata must be unique", "No silent overwrite"],
        ["Numbers", "Finite binary64 inputs and computed values", "NaN / infinity rejected"],
        ["Geometry", "Shape checks; projector is a square endomorphism", "No raw dimension faults"],
        ["Bounds", "Confidence in [0,1]; tolerances finite and ≥ 0", "Explicit domain failure"],
    ]
    y = table(c, M, y, [112, 250, 154], ["Area", "Rule", "Failure behavior"], rows,
              [46, 46, 46, 46, 46], 7.25)
    y -= 17
    c.setFont("DV", 7.7)
    c.setFillColor(MUTED)
    c.drawString(M, y, "Receipt schema remains osl.core.receipt.v2; core_version = 0.5 distinguishes this profile.")
    finish(c)

    # 4 — Domain reconstruction
    page_base(c, 4, "Independent semantics")
    y = heading(c, "03 · Independent semantics", "Five reconstructed domains",
                "Each checker consumes source, receipts, and terminal state; recomputes domain facts; and rejects malformed, rehashed, or semantically inconsistent evidence.")
    rows = [
        ["Numerical", "Independent fragment parser", "Spaces, vectors, matrices, apply, transport, projector/intertwiner residuals, numeric rollback"],
        ["Contracts", "Independent source parser", "All five templates, feedback deadlines, violations, terminal/finalization conditions, rollback"],
        ["Sessions", "Independent source parser", "Protocol schema, finite graph report, start/advance/history/current/active, rollback"],
        ["Metadata", "Shared primary parser", "Secret digests, published value/source/step/digest, assertion accounting, show semantic binding"],
        ["Intrinsics", "Shared primary parser", "Embedded verify_receipts report over the exact preceding receipt prefix"],
    ]
    y = table(c, M, y, [96, 132, 288], ["Domain", "Frontend", "Reconstructed semantics"], rows,
              [72, 72, 72, 72, 72], 7.35)
    y -= 26
    rounded_box(c, M, y - 116, W - 2 * M, 116, MINT, TEAL, 10)
    c.setFont("DV-Bold", 10)
    c.setFillColor(TEAL)
    c.drawString(M + 16, y - 24, "AGGREGATION RULE")
    c.setFont("DV-Mono-Bold", 10)
    c.setFillColor(INK)
    c.drawString(M + 16, y - 51, "independent_checks_pass = AND(domain_reports)")
    paragraph(c, "A single false, missing, malformed, or inconsistent domain report makes the aggregate fail closed. The base protected-state kernel remains a parallel requirement, not a substitute.",
              M + 16, y - 65, W - 2 * M - 32, 8.1, 12.0, INK)
    finish(c)

    # 5 — Numeric profile and transactions
    page_base(c, 5, "Numeric profile")
    y = heading(c, "04 · Numeric and rollback semantics", "Defined behavior at the sharp edges",
                "The numerical fragment now has an explicit implementation profile so that runtime and independent checking can be compared without vague real-number claims.")
    cards = [
        ("Representation", "JSON numbers are converted to finite IEEE-754 binary64 values. Boolean values are not accepted as numbers."),
        ("Linear algebra", "Matrix–vector multiplication, inversion, and residual norms use NumPy binary64 operations."),
        ("Projectors", "P must be a square endomorphism. The check uses ‖P² − P‖ ≤ tolerance."),
        ("Intertwiners", "For T, L, R, the check uses ‖TL − RT‖ ≤ tolerance with finite nonnegative tolerance."),
    ]
    cw = (W - 2 * M - 14) / 2
    for i, (title, body) in enumerate(cards):
        col, row = i % 2, i // 2
        x = M + col * (cw + 14)
        yy = y - row * 116
        rounded_box(c, x, yy - 99, cw, 99, WHITE, LINE, 9)
        c.setFont("DV-Bold", 9.2)
        c.setFillColor(TEAL if col == 0 else NAVY)
        c.drawString(x + 14, yy - 23, title.upper())
        paragraph(c, body, x + 14, yy - 36, cw - 28, 7.8, 11.6, INK)
    y -= 254
    c.setFont("DV-Bold", 12)
    c.setFillColor(INK)
    c.drawString(M, y, "Transaction evidence")
    y -= 24
    # Compact rollback timeline
    tx_x = [M + 34, M + 170, M + 306, M + 442]
    tx_labels = [
        ("BEGIN", "checkpoint digest"),
        ("BODY", "domain effects"),
        ("FAULT", "explicit cause"),
        ("ROLLBACK", "restored state"),
    ]
    c.setStrokeColor(LINE)
    c.setLineWidth(3)
    c.line(tx_x[0], y - 28, tx_x[-1], y - 28)
    for idx, (x, (top, sub)) in enumerate(zip(tx_x, tx_labels)):
        c.setFillColor(CORAL if idx == 2 else TEAL)
        c.circle(x, y - 28, 8, stroke=0, fill=1)
        c.setFont("DV-Bold", 7.5)
        c.setFillColor(INK)
        c.drawCentredString(x, y - 51, top)
        c.setFont("DV", 6.6)
        c.setFillColor(MUTED)
        c.drawCentredString(x, y - 64, sub)
    y -= 94
    rounded_box(c, M, y - 122, W - 2 * M, 122, SKY, NAVY, 9)
    c.setFont("DV-Bold", 9)
    c.setFillColor(NAVY)
    c.drawString(M + 15, y - 22, "PRECISE BOUNDARY")
    yb = y - 37
    yb = bullet(c, "Numeric, contract, session, and metadata domain states are reconstructed across tested commit and rollback cases.", M + 15, yb, W - 2 * M - 30, dot=TEAL, size=7.8)
    yb = bullet(c, "The exact complete cross-domain transaction projection digest is not yet independently reconstructed end to end.", M + 15, yb, W - 2 * M - 30, dot=CORAL, size=7.8)
    finish(c)

    # 6 — Evidence
    page_base(c, 6, "Evidence")
    y = heading(c, "05 · Finite evidence", "What was actually run",
                "All counts below are read from the generated release reports, not projected from a plan.")
    gap = 12
    mw = (W - 2 * M - 2 * gap) / 3
    metric(c, M, y - 76, mw, "66 / 66", "source corpus", TEAL)
    metric(c, M + mw + gap, y - 76, mw, "42 / 24", "accept / reject", NAVY)
    metric(c, M + 2 * (mw + gap), y - 76, mw, "1,825", "receipt-v2 records", GOLD)
    y -= 112
    c.setFont("DV-Bold", 11.5)
    c.setFillColor(INK)
    c.drawString(M, y, "Terminal outcomes")
    y -= 22
    phases = [("complete", 42, TEAL), ("statement", 20, CORAL), ("static", 2, NAVY), ("finalization", 2, GOLD)]
    max_bar = 330
    for name, value, color in phases:
        c.setFont("DV", 7.7)
        c.setFillColor(MUTED)
        c.drawString(M, y - 2, name)
        c.setFillColor(SOFT)
        c.roundRect(M + 92, y - 7, max_bar, 12, 6, stroke=0, fill=1)
        c.setFillColor(color)
        c.roundRect(M + 92, y - 7, max_bar * value / 42, 12, 6, stroke=0, fill=1)
        c.setFont("DV-Bold", 7.7)
        c.setFillColor(INK)
        c.drawRightString(W - M, y - 2, str(value))
        y -= 29
    y -= 10
    rows = [
        ["Full tests", f"{tests['pytest_passed']} / {tests['pytest_passed']}", "0 failed · 0 skipped · 0 errors"],
        ["Focused Core 0.5", f"{focused['passed_count']} / {focused['case_count']}", "five semantic domains + integration + hardening"],
        ["Base independent kernel", f"{conf['base_independent_verified_count']} / {conf['program_count']}", "lifecycle and protected state"],
        ["Semantic aggregate", f"{conf['semantic_independence_verified_count']} / {conf['program_count']}", "all five domain reports"],
        ["Supplementary replay", f"{conf['supplementary_replay_verified_count']} / {conf['program_count']}", "same-runtime exact replay; explicitly secondary"],
        ["Discovery Bridge", f"{bridge['program_count']} / {bridge['program_count']}", f"finite candidate paths · {bridge['receipt_count']} receipts"],
    ]
    y = table(c, M, y, [154, 92, 270], ["Gate", "Result", "Scope"], rows,
              [39, 39, 39, 39, 39, 39], 7.2)
    finish(c)

    # 7 — Reproduce and inspect
    page_base(c, 7, "Reproducibility")
    y = heading(c, "06 · Reproducible package", "One verifier, explicit artifacts",
                "The archive includes the runtime, independent checkers, tests, deterministic report generators, manifest, hashes, and this technical update.")
    rounded_box(c, M, y - 114, W - 2 * M, 114, NAVY, NAVY, 10)
    c.setFont("DV-Bold", 8)
    c.setFillColor(MINT)
    c.drawString(M + 16, y - 23, "POWERSHELL")
    ps = [
        "python -m pip install -r requirements.txt;",
        "if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE };",
        ".\\verify_core05.ps1",
    ]
    c.setFont("DV-Mono", 7.4)
    c.setFillColor(WHITE)
    cy = y - 50
    for line in ps:
        c.drawString(M + 16, cy, line)
        cy -= 19
    y -= 145
    c.setFont("DV-Bold", 12)
    c.setFillColor(INK)
    c.drawString(M, y, "Verification pipeline")
    y -= 28
    steps = [
        ("01", "Integrity", "Validate manifest and SHA-256 inventory."),
        ("02", "Execute", "Run all 168 tests with no skips or errors."),
        ("03", "Rebuild", "Regenerate corpus, semantic, focused, and bridge reports."),
        ("04", "Compare", "Require expected outcomes and every named checker to pass."),
        ("05", "Recheck", "Confirm regenerated artifacts still match the package."),
    ]
    for i, (num, title, body) in enumerate(steps):
        sy = y - i * 72
        c.setFillColor(TEAL)
        c.roundRect(M, sy - 45, 46, 46, 8, stroke=0, fill=1)
        c.setFont("DV-Bold", 11)
        c.setFillColor(WHITE)
        c.drawCentredString(M + 23, sy - 27, num)
        c.setFont("DV-Bold", 9.2)
        c.setFillColor(INK)
        c.drawString(M + 64, sy - 12, title)
        paragraph(c, body, M + 64, sy - 22, W - 2 * M - 64, 7.8, 11.4, MUTED)
    y = y - len(steps) * 72 - 2
    rounded_box(c, M, y - 64, W - 2 * M, 64, MINT, TEAL, 8)
    paragraph(c, "Offline after dependencies are installed. A failure, missing file, stale digest, or unexpected test outcome makes the release non-passing.",
              M + 14, y - 16, W - 2 * M - 28, 8.0, 12.0, INK)
    finish(c)

    # 8 — Claim boundary and next work
    page_base(c, 8, "Claim boundary")
    y = heading(c, "07 · Interpretation", "The strongest justified claim",
                "Core 0.5 improves semantic separation while keeping the limits visible.")
    rounded_box(c, M, y - 132, W - 2 * M, 132, MINT, TEAL, 11)
    c.setFont("DV-Bold", 8.2)
    c.setFillColor(TEAL)
    c.drawString(M + 16, y - 23, "PASSING CLAIM")
    paragraph(c,
              "For the packaged finite corpus, the OSL-Core 0.5 runtime, protected-state kernel, and five domain semantic evaluators agree on the declared outcomes and satisfy the implemented receipt-v2, state-reconstruction, rollback, and language-hardening checks.",
              M + 16, y - 38, W - 2 * M - 32, 10.0, 15.0, INK, font="DV-Bold")
    y -= 164
    c.setFont("DV-Bold", 11.5)
    c.setFillColor(INK)
    c.drawString(M, y, "Not established")
    y -= 19
    gaps = [
        "General truth of every assertion form; metadata checks assertion accounting and selected binding, not universal truth evaluation.",
        "Exact complete cross-domain transaction projection digests or every rejection cause outside reconstructed domain predicates.",
        "Parser/static-checker correctness, Python/NumPy correctness, or proof-assistant verification of the interpreter.",
        "Universal safety, open-world discovery, neural semantic truth, consciousness, personhood, intent, or subjective awareness.",
        "Identity, authorship, consent, or nonrepudiation from SHA-256; OS sandboxing or rollback of external effects.",
    ]
    for item in gaps:
        y = bullet(c, item, M, y, W - 2 * M, dot=CORAL, size=7.7) - 4
    y -= 10
    c.setFont("DV-Bold", 11.5)
    c.setFillColor(INK)
    c.drawString(M, y, "Next independence targets")
    y -= 22
    targets = [
        ("1", "Second frontend", "Independent parse + static semantics"),
        ("2", "Assertions", "Truth evaluation for all 14 forms"),
        ("3", "Transactions", "Complete projection-digest reconstruction"),
    ]
    tw = (W - 2 * M - 20) / 3
    for i, (num, title, body) in enumerate(targets):
        x = M + i * (tw + 10)
        rounded_box(c, x, y - 98, tw, 98, WHITE, LINE, 8)
        c.setFillColor(NAVY)
        c.circle(x + 19, y - 22, 11, stroke=0, fill=1)
        c.setFont("DV-Bold", 7.6)
        c.setFillColor(WHITE)
        c.drawCentredString(x + 19, y - 25, num)
        c.setFont("DV-Bold", 8.4)
        c.setFillColor(INK)
        c.drawString(x + 38, y - 25, title)
        paragraph(c, body, x + 12, y - 43, tw - 24, 7.3, 10.8, MUTED)
    y -= 123
    c.setStrokeColor(LINE)
    c.line(M, y, W - M, y)
    c.setFont("DV-Bold", 8)
    c.setFillColor(TEAL)
    c.drawString(M, y - 23, "PRIMARY RELEASE REFERENCES")
    paragraph(c, "README.md · CORE05_SEMANTIC_INDEPENDENCE_SPEC.md · CORE05_RECEIPT_SPEC.md · CORE05_NUMERIC_PROFILE.md · CLAIM_BOUNDARY.md · CORE05_CONFORMANCE_REPORT.json",
              M, y - 33, W - 2 * M, 7.2, 11.0, MUTED)
    finish(c)

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
