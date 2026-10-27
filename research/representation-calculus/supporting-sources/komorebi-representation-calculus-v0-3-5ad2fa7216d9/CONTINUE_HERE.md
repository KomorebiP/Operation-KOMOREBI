# Continue from Representation Calculus v0.3

This is NOT p-adic Block 16. Use the v0.3 ZIP as the source, verify
FILE_MANIFEST.json first, and preserve history/Komorebi_Representation_Calculus_v0.2.zip.
Read FORMAL_NOTE.md, FORMALIZATION_COVERAGE.md, RESULTS.md and DEVELOPMENT_FAILURES.md.

## Completed target

The universal symbolic matrix adapter is now Lean-checked: from actual row-word
provenance and PA=CP, O=DP, P=WG it constructs the transport and exact observational
quotient. Its image has a checked principal-multiple description. All 202 frozen
matrix instances compile, with growth witnesses. The large 2^128-state source
has a formal 2^30-element exact image and minimum of two residue coordinates.
No state enumeration is used in those symbolic proofs.

## Next missing theorem

For ANY accepted certificate over R=Z/p^rZ with t nonzero Smith factors, formalize
that the least dimension of an all-initial-state FREE LINEAR encoding is t.
The existing state-space injection alone need not imply this count. Preserve
linearity of the competitor's initial encoding and all-word output correctness;
local competitor-state intertwining need not be assumed. Supply or port the
chain-ring submodule-generator bound and the quotient-generator argument.

The p-adic archive contains relevant module-generator proofs, but importing them
requires actual source/toolchain inspection. v0.3 itself uses only Lean/Std.
Do not turn an uncompiled Mathlib import or a written argument into claimed proof.

## Retain these distinctions

Actual image vs free ambient array; all initial states vs single-seed orbit;
state cardinality vs linear-generator count; observed test growth vs final basis;
input JSON vs generated Lean literal specification; proof existence vs executable
extraction. Empty observations/zero coordinates and nonzero torsion are mandatory
regression cases. A cap is unresolved, never nonexistence.

## Reproduction

README.md has commands. Full Lean audit can run in hash-checked synchronous
batches. Only PASS after all sources, axiom checks and negative controls counts.
Run the documented manifest normalization and validation after a fresh audit.
The raw progress-log metadata misclassification and its correction are retained.
