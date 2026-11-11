# Smith chart presentation and completion edition

This continuation starts from repository revision
`f8dbf83bb2a67139be7800768ce9a8be2109b28a`. The original 172-file archive,
its manuscript, figures, and earlier proof receipts remain retained sources.

## Presentation and language

`figures.json` binds 42 vector edition figures to their source identities and
plotting programs. Most plots are regenerated from the archived equations
with one type system and palette. The combiner, circuit graph, storage map,
Kron reduction, and census receive new layouts. Four dense diagrams also have
stacked mobile versions. Every online figure links to its original.

One illustration required a component correction: the original figure 39
draws a faint resistor on section A's `(1,3)` branch, although the exact nodal
generator defines that branch as capacitor-only. The edition uses resistors
on `(0,2)`, `(0,3)`, `(1,2)`, `(2,3)`; inductors on `(0,3)`, `(1,2)`; and a
capacitor on `(1,3)`. The certified circuit and its component count are
unchanged. Symbol crossings in the redrawn graph do not add junctions.

`prose.json` records 45 wording rules affecting 66 occurrences, plus one
accessibility rule exposing 18 captions. Coverage includes the opening,
reading map, selected transitions, research headings, provenance language,
and ten figure descriptions and their alternative text. Mathematical
expressions, labels, hypotheses, and stable section identifiers are preserved
by build checks. No mathematical-token edit is made to the archived text.

Rebuild the artwork in an environment with Matplotlib `3.10.8`, NumPy
`2.5.4`, NetworkX `3.6.1`, SymPy `1.14.0`, and mpmath `1.3.0`:

```text
python -B research/smith-chart/edition/generate_figures.py
```

The generator checks the ZIP, runs plotting sources in a temporary copy, and
never loads an archived pickle. Markers in the cancellation illustration use
rounded centers of the certified algebraic values; the exact cancellation
claim comes from the certificate and written argument.

## Mathematical additions

The [singular-completion note](../../../docs/demonstrations/SMITH_SINGULAR_COMPLETION.md)
proves the range condition for a singular positive-semidefinite block,
computes a uniquely forced complex prediction, and gives the complete feasible
region for two **real scalar** packets at radius `1/2`. A
[selected Lean companion](../completion-formal/README.md) checks six real
algebraic statements. The general matrix lemma and square-root boundary
remain written proofs. The proof and source mapping are self-reviewed.

The [class-142 derivation](../computations/derive_candidate_142.py) completes
the exact polynomial encoding of that five-node candidate. Its 125 spanning
trees and 50 separating forests produce 13 coefficient equations of degree
at most four. Direct symbolic determinants give the same polynomials. A
positive solution has not been found or excluded; the global six-reactive
question remains open.

`review.md` records the mathematical audit and exact limits. `pick-source.json`
identifies the primary classical interpolation theorem checked for the note.
The computation manifests bind their inputs before and after execution.
