# Appendix conversion audit — Publication Block07

All 15 original construction notes were recovered from the actual Block01 archive and pinned by SHA-256. They are unchanged under `raw_sources/`. The conversion audit reconstructs the selected Markdown AST with Pandoc3.1.11.1 and compares the converted TeX with these original notes.

The parser produces44 superscript nodes and one link node. The link node is the `[k:F_p](n−n/p)` expression restored in Block06. The 44 superscript spans were malformed combinations of separate caret exponents. They are now restored in nine appendix files. `CONVERSION_REPAIRS.json` records each raw expression, before/after replacement, occurrence count and source hash. The source audit reconstructs the exact edited appendix bytes from the prior files plus that map.

Examples include `J^1/H^1`, `s(P^r)=Q^r`, the Artin–Schreier polynomial, filtered unit quotients, character conjugation identities and the double exponent in the dyadic Heisenberg dimension. These are restorations of existing source expressions, not new arithmetic results.

A separate one-line clarification labels the dyadic table's `2^d` column as **Source carrier dimension**. Its entries measure the representation dimension, not the `2d`-dimensional source symplectic quotient. No numerical entry changed. This is recorded in `EDITORIAL_CLARIFICATIONS.json`.

No malformed superscript nodes remain in the fifteen converted appendix files. All literal Verbatim blocks are byte-preserved. Six appendix files remain wholly unchanged from Block06. The raw notes retain their original plain source notation elsewhere, including readable inline caret expressions. The audit does not claim that a syntactic scan proves every underlying arithmetic argument or that every possible typography issue is excluded.

The main manuscript's68 explicit proof bodies and 105 statement bodies remain byte-identical. All 423 selected Lean modules,40 teaching excerpts and 4,342 named lexical declaration records retain their source hashes. The release changes neither formal binders nor the four open mathematical obligations.
