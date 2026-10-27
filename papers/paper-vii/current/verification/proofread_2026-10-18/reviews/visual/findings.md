# Paper VII visual guide proofreading review

Date: 2026-10-18
Mode: review only. No active manuscript, generator, or graphic source was edited.
Scope: the active visual guide, its shared atlas prose, and all 42 pages of the supplied baseline PDF.

## Findings requiring local correction

### 1. Scalar dimension multiplication is written as a tensor product (mathematical token)

- Worked page: V29. Baseline physical PDF page: 31.
- `editable/visual_guide/graphics_extended/s3.tex:7` and `editable/visual_guide/source/generate_extensions.py:12` contain `$2\otimes2=4$`.
- Recommended exact correction: `$2\cdot2=4$`.
- Rationale: these are the two scalar dimensions. The adjacent prose explicitly gives `2\cdot2=4`, while the tensor-product spaces are already correctly represented in the plate's lower formula `\CC^2\otimes\CC^2`. This is a uniquely forced, isolated symbol correction. It does not change the mathematical example or require a new argument.
- Apply to the corresponding traditional atlas plate as well.

### 2. Coherence-order wording assigns the order to the wrong object

- Worked page: V31. Baseline physical PDF page: 33.
- `editable/visual_guide/source/extended_pages.tex:49` and `editable/traditional/monograph_atlas.tex:581`.
- Current sentence: `Conjugation $X\mapsto ZXZ$ has order zero on diagonal matrices and order one modulo two on off-diagonal matrices.`
- Recommended sentence: `Under conjugation $X\mapsto ZXZ$, diagonal matrices have coherence order zero and off-diagonal matrices have coherence order one modulo two.`
- Rationale: the integers are coherence-sector labels of matrices. As written, "conjugation has order zero" can instead be read as a false statement about the order of the conjugation map. The surrounding projectors and the traditional coherence-order definition uniquely fix the intended meaning. No formula changes.

### 3. The array count in the text does not match the plate

- Worked page: V13. Baseline physical PDF page: 15.
- `editable/visual_guide/source/pages.tex:236` and `editable/traditional/monograph_atlas.tex:241`.
- Replace `by multiplying four small arrays` with `by multiplying the displayed small arrays`.
- The figure displays three arrays, namely `P(0)`, `\dot P(0)`, and `C`. Removing the incidental count preserves the intended instruction and every equation.

### 4. The coherence comparison label collides with a matrix row label

- Worked page: V16. Baseline physical PDF page: 18.
- `editable/visual_guide/graphics/dephasing.tex:80` and the corresponding generator text at `editable/visual_guide/source/generate_graphics.py:167`.
- The centered node at `(6.8,2.3)` reads `same diagonal\\different coherence` and touches/overlaps the right matrix's row label `10`.
- Recommended layout correction: move the node left to `(6.1,2.3)`, preserving its text. Verify the final rendering because the atlas uses a different plate scale.

### 5. The transfer arrow is drawn through the endpoint numbers

- Worked page: V27. Baseline physical PDF page: 29.
- `editable/visual_guide/graphics/perfect_transfer.tex:15` and corresponding generator code.
- The dashed arrow from `(1.5,2.8)` to `(4.5,0.7)` is drawn after the radius-0.24 site circles and numbers, so it crosses the digits `0` and `2`.
- Recommended layout correction: add `shorten <=0.27cm,shorten >=0.27cm` to that arrow, or use the circle boundary coordinates. Preserve the mathematical endpoints and direction.

### 6. The rotated complement label extends beyond its box

- Worked page: V38. Baseline physical PDF page: 40.
- `editable/visual_guide/graphics_extended/constraint_image.tex:7` and `editable/visual_guide/source/generate_extensions.py:56`.
- The rotated `new coordinate` label crosses the top and bottom edges of the shaded complement box.
- Recommended layout correction: use `font=\footnotesize` for this one rotated label, preserving its wording, and verify it fits fully inside the box.

## Validation and coverage

- Read the full active main visual `.tex`, `source/front.tex`, `source/pages.tex`, `source/extended_pages.tex`, and `source/visual_macros.tex`.
- Reviewed all 38 current TikZ plates through fresh PDF render inspection and source caption/label extraction. The historical assembly and provenance copies were excluded from active-source review.
- Programmatically compared the bodies of all 40 V-pages to `editable/traditional/monograph_atlas.tex`: every body matched exactly before edits. Locator and setup material was intentionally excluded from that body comparison.
- Freshly rendered and visually inspected all 42 baseline pages individually at 108 dpi (918 by 1188 pixels), including front matter, all figures, captions, matrices, displays, tables, headers, footers, page numbering, and page transitions.
- Baseline layout findings are limited to V16, V27, and V38 above. No other clipping, missing glyphs, or meaningful overlaps were observed. V30 contains a large inline matrix split from its preceding equality by a line break. It remains readable and is a layout preference, not an objective defect requiring an additional change.
- Checked all 40 reading locator lines and all 80 traditional targets against the current `canonical_label_to_final.json`, the actual traditional PDF page labels, and the number appearing on each targeted page. PASS, with zero errors. See `crosswalk_check.json`.
- The natural-unit convention `\hbar=1` is stated in the current traditional finite core, and the visual formulas use it consistently. All phase, amplitude/probability, dimension, channel-family, norm, and scaling conventions were reviewed locally.
- No new proof gap or substantive mathematical inconsistency was found within this proofreading scope. This is not a full correctness audit or literature audit.
- No active source was modified and no post-correction build was run by this reviewer. Root must rebuild, refresh locators after traditional pagination is final, and re-render final affected pages plus the shared atlas.

## Mathematical-token changes recommended

Exactly one: the scalar-dimension glyph `\otimes` to `\cdot` in the V29 plate (and its duplicate/generator sources). The remaining corrections affect prose or layout only.

## Review artifacts

- `page_01.png` through `page_42.png`: fresh baseline page renders.
- `crosswalk_check.json`: read-only locator verification results.
- `coverage.json`: file inventory and baseline hashes.
- `findings.md`: this report.
