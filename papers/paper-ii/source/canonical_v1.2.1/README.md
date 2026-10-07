# Projector-Resolved Seed Calculus II

**Polyphase Refinement, Weighted Transfer, and Dyadic-Odd Resolution**  
**Komorebi P. — Paper version 1.2.1 (September 3, 2026)**

This release develops the refinement layer of the projector-resolved seed
calculus: coherent nested packet coordinates, residue/Fourier selectors,
dyadic–odd CRT coordinates, explicit pruned weighted inverses, automatically
rational finite-graph walk series, evaluated Bézout separators, concrete
finite Smith-coordinate fibres, and typed linear refinement defects.

The revision freezes a 25-item formal contract: 21 numbered main-text
definitions/results, the Smith-phase identity, and three algorithms. Every
item is mapped to one or more Lean declarations. “Lean-complete” here means
complete relative to the scopes and hypotheses in that revised contract.
Several formerly certificate-only branches are now constructive at their
stated finite scope: a finite Fourier table extends by periodicity, the
enumerated walk series receives its determinant/adjugate denominator, and the
one-coordinate Smith count is proved over `ZMod (p^L)`. The counted Smith
theorem is exactly this concrete result with residue cardinality `p`; the
arbitrary-DVR, residue-size-`q` extension is classical/certificate-explicit.
This does not assert
novelty, priority, universal generality beyond the stated hypotheses, or
external peer review.

## Contents

- `paper/`: PDF, LaTeX source, and generated figure pairs.
- `formalization/lean/`: Lean 4/Mathlib source, kernel audit, exact theorem map,
  and verification report. The component version is 1.1.1.
- `code/python/`: Python 1.2.1 package, test suite, pinned environment,
  generated-data pipeline, and installable wheel.
- `results/`: machine-readable certificates and captured verification logs.
- `provenance/`: baseline, claim-boundary, contract, render, and audit records.

## Verify

On Unix-like systems:

```sh
./Run_All.sh
```

On Windows PowerShell:

```powershell
.\Run_All.ps1
```

The scripts create a local verification environment, install the exact Python
lock, regenerate results and figures, run all Python tests, rebuild the wheel,
check every theorem-map declaration, build the Lean target, run the fail-closed
kernel audit, and compile the paper. The exact lock requires Python 3.11+,
plus `lake` and `latexmk` on `PATH`; the pinned Lean toolchain is read
from `formalization/lean/lean-toolchain`.

See `REPRODUCIBILITY.md` for individual commands and scope. No license has
been selected; see `LICENSE_STATUS.md`.
