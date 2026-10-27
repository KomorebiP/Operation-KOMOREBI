# Komorebi Beal research — Block 52, v5.2.0

## What this package contains

The complete original Block51 archive is preserved in `predecessor/`.
It contains the earlier recovered Blocks49--50, their original archives,
and all earlier bundled materials. The new Block52 work is in `work52/`.
Nothing in the frozen predecessor has been edited or reconstructed.

This block establishes, under the inherited arithmetic contract:

- actual depth n>=2 forces29*43|C, and the reducible branch forces71|C;
- good13 makes the actual twisted Frobenius scalar and forces a_phi=0;
- compatible local Kummer forms constrain the real depth-one support and
  exclude the old nonliftable ray realization on the good13 subcase.

It does NOT solve Beal, the complete(3,5,7) signature, or the full remaining
reducible branch. No new Lean certificate is claimed.

Start with `work52/REPORT.md`, then `work52/TARGET_CONTRACT.md` and
`work52/PROOF_BOUNDARY.md`. Complete mathematical proofs are in `work52/notes/`.
The next bounded objective is in `CONTINUE_HERE.md`.

## Reproduce

Python3.10 or later, standard library only. No package installation required.
From this extracted directory run:

```text
python verify.py --replay-predecessors
```

The verifier first checks all package hashes and the original ZIP hash/CRC.
It then extracts the predecessor in a temporary directory, runs its Block51
check plus its six selected historical replays, and runs the three new
Block52 scripts in an isolated copy. Every new JSON is compared with its
pinned reference. Inputs are hashed again afterward.

By default the report is written NEXT TO this package directory, not inside
it. `--report PATH` must also point outside the package. `--timeout-seconds`
applies to each new job; the nested predecessor receives a separate bounded
wrapper allowance. A timeout is inconclusive, not a mathematical result.

Without `--replay-predecessors`, the three new Block52 scripts and archive
integrity are checked, but the earlier computations are not rerun. Neither
mode certifies universal prose proofs or external source theorems by itself.

The finite checks cover164 weighted orbits, all1240 admissible pairs counted
independently,2500 exact integral matrices, finite Kummer symbols, and the
stated negative controls. See `work52/VERIFICATION.md` for the exact boundary.

The package's SHA256 manifest excludes only itself. The original archive is
nested rather than flattened so that its exact historical manifest and
provenance remain usable.
