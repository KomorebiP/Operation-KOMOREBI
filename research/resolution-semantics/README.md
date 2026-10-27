# Komorebi Resolution Semantics 0.1.0

Author: Komorebi P.  
Date: September 26, 2026.

The PDF develops the proposal that mathematical worlds can be treated as
related resolutions, while distinguishing a common encoding from an explanatory
transformation structure. It supplies explicit mathematical proofs, counterexamples,
and exact finite verification.

## Main results

- A Boolean-valued presentation of any supplied set-indexed family of first-order models.
- A typed transport differential, its twisted product rule, and its composition law.
- A Boolean invariant subalgebra with an **additive**, not Boolean, residual quotient.
- The exact relationship between definable coherent observables and a diagram limit.
- Finite graph integration and reconstruction, including exact cycle obstructions.
- A classification of all Boolean retractions onto a finite component-constant algebra.
- Canonical lower and upper envelopes of all such retractions.
- A two-world obstruction to a symmetry-preserving Boolean or additive projector.
- Weighted real multiresolution and a finite all-path stabilization criterion.

These are structural results, not a proof of a new ZFC existence axiom or a solution
to a set-theoretic independence problem. Standard predecessors are acknowledged
in the PDF, including Boolean-valued models, modal forcing, graph cohomology,
rough-set approximation, and nested orthogonal projections. Novelty of the
combined research framework has not been established by this release.

## Reproduce

```bash
python checks/verify_krs.py
pdflatex -interaction=nonstopmode -halt-on-error Komorebi_Resolution_Semantics.tex
pdflatex -interaction=nonstopmode -halt-on-error Komorebi_Resolution_Semantics.tex
```

Python uses only the standard library, exact integers, and Boolean polynomial
normal forms. No random input, floating arithmetic, GPU, or external solver is used.
The checker recreates `results/VERIFICATION.json`.

## Lean boundary

`formal/KRS_Core.lean` is **uncompiled**. It is a limited two-valued source
scaffold, not verification of the note. No Lean or Lake binary was located.
A pinned Lean release download failed because the runtime could not resolve
`github.com`; the external download path was restricted as well.
A local reproduction target is `lean formal/KRS_Core.lean`.

No prior Komorebi Lean checkpoint was imported or modified. No executable compiler,
font file, or third-party source paper is distributed.

## Contents

`Komorebi_Resolution_Semantics.pdf`: typeset mathematical note.  
`Komorebi_Resolution_Semantics.tex`: editable source.  
`checks/verify_krs.py`: exact computation and finite enumeration.  
`results/VERIFICATION.json`: machine-readable result and source hash.  
`results/verification_stdout.txt`: retained raw checker output.  
`formal/KRS_Core.lean`: explicitly uncompiled source scaffold.  
`PROOF_BOUNDARY.md`: what is proved, checked, conditional, or unverified.  
`results/DEVELOPMENT_FAILURES.md`: failed steps and their resolution.  
`SHA256SUMS.txt`: file integrity hashes.
