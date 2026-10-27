# Lean guide rendered-layout and manuscript-concordance review

Reviewed the initial nineteen-page
`output/Komorebi_Quantum_Arithmetic_Lean_Guide.pdf` through all nineteen page
renders, all four contact sheets, and full-size checks of pages 7, 8, 9, 10, 13,
and 19. Crosschecked current traditional Markdown QA01–QA20 statements against
the guide and machine concordance. This is a read-only review of the initial
render; the parent is applying final layout corrections.

## Passed

- The cover, section hierarchy, headings, exact equations, source windows, and
  inventory tables render cleanly without observed overlap or clipping.
- Lean Unicode is legible with the XeLaTeX/fontspec/DejaVu Sans Mono setup.
  Quantifiers, arrows, logical conjunctions, number-system glyphs, the summation
  symbol, and adjoint notation appear in the actual proof excerpts.
- PDF text extraction contains every one of the 96 active theorem basenames.
  The inventory has 22 + 17 + 30 + 17 + 10 declarations, with the current physical
  source line numbers.
- The current source and formal status are stated with the correct 96-theorem
  later checkpoint, separately from the 59-theorem earlier checkpoint.
- General-modulus, generic Parseval, all-divisor families, generic measurement
  update, and polyphase scope are not falsely described as current Lean proofs.
- Fresh Lean execution is clearly NOT_RUN rather than a fresh pass.

## Exact layout fixes for the parent

1. **Remove the forced `\clearpage` before the complete theorem inventory.**
   Initial page 16 contains only the final two paragraphs of the reproducibility
   section, approximately 326 extracted text characters including headers and
   footers, followed by a largely empty page. The forced break appears in
   `lean/build_guide_body.py` immediately before `\section{Complete active theorem
   inventory}`. Let the inventory flow after those paragraphs.
2. **Keep a literal-source caption with at least the first few code lines.**
   Initial pages 4 and 7 end with a source caption while the code starts on the
   following page. Add a small `\Needspace` before the caption in the `excerpt`
   helper, using the `needspace` package, or an equivalent existing layout
   mechanism. Five or six baselines should prevent a stranded caption.
3. **Avoid splitting a declaration immediately after its name or first type
   line.** The `publication_bridge` window leaves its name at the end of initial
   page 13 and the conjunction on page 14. The `fourier_entry_formula` declaration
   starts at the end of initial page 10 and continues on page 11. Split the large
   convention window at source line 57, and keep the short final publication
   theorem window on one page, for example with a modest pre-block `Needspace`
   or `samepage=true` on that particular Verbatim block. Do not make every long
   source window unbreakable.
4. **Keep inventory subsection headings with the table header and first rows.**
   Initial page 18 ends with subsection 17.4, whereas its Conventions table starts
   on page 19. A modest pre-subsection `Needspace` of eight baselines resolves
   this; table continuations elsewhere already have clean repeated headings.

The parent's emergency stretch correction addresses the three initial overfull
paragraphs. No further font or glyph substitution is required by this review.

## Exact concordance updates for the parent

The current traditional manuscript now has twenty claim labels. The guide's
sentence that the paper labels results QA01 through QA18 is stale and should say
QA01 through QA20. Add two rows:

| Claim | Subject | Formal coverage |
|---|---|---|
| QA19 | Continuous relative-phase response, `sin²(theta/2)` | Prose extension; not an inherited Lean theorem |
| QA20 | Dephased selected probability, `1/3` | Prose density-matrix calculation; not an inherited Lean theorem |

The following refinements preserve the exact existing source coverage:

- QA01: the current Lean certificate verifies order twelve for the chosen root.
  It does not separately export the arbitrary-power formula
  `q/gcd(a,q)` for all character labels. The current guide already restricts to
  exact order twelve; retain that restriction.
- QA05: add `ramanujan12_energy` to the machine claim's supporting declarations
  because the manuscript QA05 includes both support and energy. The generic
  `q*phi(q)` statement remains prose, with the q=12 energy specialization checked.
- QA15: add a sentence that the no-inverse statement **up to global phase** is
  a proved prose strengthening. The exported Lean theorem forbids a vector-valued
  reconstruction function on the two exact vectors; it does not separately export
  the quotient-by-global-phase formulation.
- QA18: the main manuscript bundles more conclusions than the literal
  `publication_bridge` declaration. Its filter/energy clause, normalization of
  `unitState`, projector action on both states, and noninjectivity use additional
  checked declarations. Add to the machine claim's supporting list:
  `projector12_recovers_test_signal`, `signal_decomposition`,
  `retained_discarded_orthogonal`, `ramanujan12_energy`, `noise12_energy`,
  `testSignal12_energy`, `energy_decomposition`, `unitState_normalized`,
  `projector_fixes_psi`, `projector_kills_chi`, and `projector_not_injective`.
  The guide can state that the central manuscript theorem is covered by the
  publication bundle **together with these separately exported results**.
  No new Lean theorem or count is needed for this mapping refinement.

No mathematical-token changes to preserved Lean source are recommended.

## Rendering failure retained

The parent reports that the first LuaLaTeX rendering attempt failed because this
runtime lacked the `luaotfload` dependency. The build switched to XeLaTeX with the
same fontspec font selection. The resulting nineteen-page PDF is the successful
render reviewed here. This document-engine failure is separate from the HTTP 502
runtime-restoration failures that prevented fresh Lean execution.

## Final validation requested

After the minimal guide/generator corrections and rebuild, inspect the affected
source-caption/code page breaks, the inventory transition, and the Conventions
subsection. Confirm all 96 theorem names remain in PDF extraction, no missing
glyph warnings appear, and current QA19–QA20 scope rows render cleanly.

## Final rendered addendum

The final source was regenerated after implementing the caption, proof-block,
inventory, and QA01–QA20 concordance corrections. The rebuilt version initially
left a two-line final-page spill. The completion prose was minimally shortened
without changing scope or mathematical claims. Three isolated XeLaTeX passes
then produced a clean **nineteen-page** guide. The Conventions heading stays
with its table, the publication theorem block stays together, and completion
text fits entirely on page 19. All 96 theorem names and QA19–QA20 scope rows
remain in extracted PDF text. There are no overfull, underfull, missing-character,
or LaTeX warning messages. No clipping or glyph defects remain.

Approved candidate: `verification/document_build/lean_layout_confirmation/Komorebi_Quantum_Arithmetic_Lean_Guide.pdf`.

SHA-256: `becb0d0e3657698ee3542c5e5b873e821c64c07e82e058e5be65775707d0c925`.

The precise hash-bound record is `reviews/LEAN_LAYOUT_QA_FINAL.json`. The parent
may copy this approved candidate to the public output path or rebuild the same
source and bind the final output hash separately.

## Final public-output binding

The actual public output `output/Komorebi_Quantum_Arithmetic_Lean_Guide.pdf`
was checked after the parent rebuild. It has nineteen pages, and all nineteen
extracted page texts exactly match the approved candidate. Its completion page
was rendered and viewed again at full size: inventory headings, tables, and
both closing paragraphs fit cleanly above the footer. Final layout status: **PASS**.

Final output SHA-256: `bf6eddfd1701d6388ce7b8440f343299528c04677033e7d1b425e308938da694`.

`reviews/LEAN_LAYOUT_QA_FINAL.json` is now bound to these final public-output bytes.
