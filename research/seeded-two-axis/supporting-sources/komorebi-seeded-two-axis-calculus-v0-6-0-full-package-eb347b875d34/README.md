# Komorebi Seeded Two-Axis Calculus v0.6.0

Author: Komorebi P.

This is a corrected and extended continuation of v0.5.0, not a replacement by a short summary. The standalone LaTeX file builds the complete 45-page manuscript. The accompanying PDF is that build.

## Main mathematical changes

- A coherent diamond refutes general ordered residual-filtration independence. An explicit two-axis functor system realizes the counterexample.
- The semantic diamond criterion gives equality of normalization comparison maps in the homotopy category, hence equivalence of total cofibers.
- In the pure identity-preserving adjacent-swap grammar, reachable words are order ideals of a finite exchange-event poset. Histories are linear extensions.
- A supplied homotopy-coherent event diagram yields an ideal-indexed residual diagram. Its chain restrictions retain different histories while its total residual is fixed.
- An ordinary thick obstruction kernel need not be constructor-invariant. The invariant saturation gives a universal constructor-compatible quotient, with a concrete collapse counterexample.
- Directed common postcomposition makes operational killability both thick and constructor-invariant.
- An exact equivariant detector certifies noncollapse. Exact residual functors can be tested on the operation orbit of the seeds.

## Build

Use a standard TeX installation with the packages named in the preamble. No external figures or bibliography files are needed.

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error Komorebi_Seeded_Two_Axis_Calculus_v0.6.0.tex
```

Alternatively run `pdflatex` repeatedly until the cross-references stabilize.

## Reproduce the finite tests

Python 3.10 or later, standard library only. Do not run in optimized (`-O`) mode because the checks use assertions.

```sh
python checks/check_models.py --max-length 10 --output checks/reproduced_results.json
```

The recorded run was on Python 3.13.5. It covers all 2,047 two-sort words through length 10, 82,499 reachable states and 168,454 rewrite edges, plus exact integer/rational counterexample checks. Runtime is not a benchmark. There is no random sampling or floating-point tolerance.

## Evidence boundary

The theorems have written proofs and authoring-session self-review. The finite tests are regression evidence, not universal proofs. No Lean checking was performed. Arithmetic globalization, unrestricted Langlands reciprocity, nonadditive universal completion, and a universal new axiom of set theory are not established.

Read `audit/AUDIT.md` for restrictions, mathematical corrections, source verification, and recorded execution failures. Read `STATUS.md` for the current next obligations. The previous v0.5.0 source and PDF are retained in `previous/`, and the textual changes are recorded in `audit/v0.5.0_to_v0.6.0.diff`.

`CHECKSUMS.json` gives SHA-256 hashes of the release files. No font files or externally downloaded source papers are bundled.
