# Complete Euler work


This archive collects the latest stationary-separation checkpoint and every
surviving Euler research file from this workspace, including older Lean
sources, Python code, proofs, figures, papers, stored results, audits, and
historical releases. Original research files and archives are unchanged.

## Latest work

Extract `LATEST/Euler_Stationary_Separation_2026-10-05.zip` first. Read its
`stationary_separation/README.md` and `SYNTHESIS.md`. That self-contained
checkpoint includes its immutable parent archives, exact computations,
independent reviews, and reproduction instructions.

The Euler simplicity goal remains open. The latest checkpoint records
proved reductions and approximation results, with the remaining actual
stationary-discriminant nonvanishing obligation stated explicitly.

## All earlier work

`WORKSPACE/` retains the original layouts of the surviving working files.
It includes earlier Address One and Critical Phases checkpoints, all
recovered releases, the four original input archives, the standalone
recenter package, and stored Lean sources and results. Run historical
scripts from their original working roots. Their stored mathematical and
verification status is unchanged; Lean was not rerun for this packaging.

`PACKAGING/coverage/` explains why the latest checkpoint alone was
insufficient. It identifies the additional historical files by content
hash, and retains the read-only coverage audit and recursive archive index.

## Verify

Run `python3 verify_bundle.py` from this extracted directory. It checks
the saved content hashes. The outer ZIP was also CRC-tested after creation.
The latest checkpoint's own verifier and reproduction instructions remain
inside its unchanged archive.
