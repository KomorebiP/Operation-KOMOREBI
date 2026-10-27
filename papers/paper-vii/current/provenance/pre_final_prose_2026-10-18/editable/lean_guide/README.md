# Paper VII Lean and evidence guide — completed proofreading

This 84-page guide teaches the retained v0.6.0 source through
exact contracts and proof walkthroughs. It includes 19 scoped finite manuscript
items, 323 named theorem declarations across 25 active modules, 67 exact source
excerpts, nine dependency pins and six separately audited constructed objects.
The five physical continuum targets remain open.

Two inline binder examples also use the appropriate text wrapper so escaped braces do not print literal backslashes. Six October 18 prose corrections clarify the code-fixed recovery scale, the
nonempty row hypothesis, the sine-square upper bound, the natural-number meaning
of `Fin n`, grammar, and the reference to two constructions. Every raw source
excerpt and active Lean file is unchanged. The inherited comment that calls a
code-fixed scale code-independent is recorded as a comment erratum in the
current focused review; the formal quantifiers and theorem body are unchanged.

Cross-reading tables locate all 19 core items, 79 proof-bearing strengthened
statements and six supplement groups. Their 110 locators (including twelve
supplement endpoints) are resolved against the actual traditional PDF labels.
Shared ingredients do not extend formal coverage.

Run `python3 build.py`, optionally with `--output-directory DIR` or `--check-only`.
The builder stages current sources in isolation, runs four XeLaTeX passes, and
emits the PDF with xdvipdfmx. It regenerates no prose, catalog, source excerpts or
formal evidence. Requirements and the explicit installed-font fallback are in
the root README. DejaVu Sans Mono is also used for code; no standalone font
binaries are included in the retrieved delivery.

`static_check.py` reconciles the existing source/excerpt/catalog and inherited
logs. `navigation.py` refreshes cross-reading locators after the traditional
volume and map are rebuilt. `assemble.py` is an earlier authoring operation that
expects additional font/assembly inputs; it is unnecessary for rebuilding this
proofread reading set. Do not regenerate reviewed chapters to perform a PDF
build. The retained `.lean.txt` excerpts contain exact raw UTF-8; corresponding
`.render.txt` files provide the established TeX escaping and glyph fallback.

Current source reconciliation and final PDF acceptance are under
`../../verification/proofread_2026-10-18/`. October 9 numerical/rational/symbolic
reports remain earlier evidence with their own finite caps and hashes. The
current verifier-software regression run is documentation/tool validation;
it is not a Lean proof or a new scientific computation.

Kernel evidence is inherited from the 6 September v0.6.0 release. Lean, Lake and
Elan are absent on the review host; the retrieved snapshot also lacks the
portable compiler kit and compiled interfaces. No fresh kernel compilation or
compiler-control execution is claimed. See the replay chapter for the pinned
procedure and the root report for the precise remaining scope.

`historical_assembly/` preserves earlier authoring inputs and evidence text.
Its dates, page locators, source pins and host descriptions are historical; it
is excluded from current PDF builds.
