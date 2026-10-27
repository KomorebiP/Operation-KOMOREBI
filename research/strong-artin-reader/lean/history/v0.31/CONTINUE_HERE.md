# Continue from Strong Artin v0.31 — Frobenius norm resonance

Read README.md, RESEARCH_BOUNDARY.md, RESEARCH_CHECKLIST.md and RESULT.json.
The exact parent is v0.30 Unramified Procyclic Lifting, SHA-256
b1daa98ca39e924aa46aa2afa176acb3c947df1e94b96873fbbbbe17af9a0be4.
Do not identify alternate archives with the same version number as one ancestry.

## Current strongest result

The actual norm-localization cokernel for a diagonalized square-zero kernel
has an exact criterion. Noninvariant modes impose local resonance zeros; invariant
modes require one degree-proportional common correction. This is connected to
vanishing of the actual continuous local-gauge obstruction.

For matrix dual numbers with diagonal residual Frobenius, degree p in
characteristic p leaves exactly the full repeated-eigenvalue blocks obstructed.
Do not reduce this to the scalar line or to the total trace.

## Recommended bounded next route

Analyze N_d(T)=1+T+...+T^(d-1) on nonsemisimple/Jordan blocks of the actual kernel
action. In characteristic p, the scalar identity already suggests the operator
polynomial (T-1)^(p-1), but this operator theorem is not claimed in v0.31.
Determine the nilpotent filtration image, validate on actual matrix extensions,
and distinguish one-stage correction from compatible tower lifting.

The general global arithmetic and automorphic problems are still open. A new
comparison structure alone does not discharge them.

## Verification

python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 8
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 8

Repeat bounded resume until PASS. Preserve the immutable parent and record all
source/log/object hashes. Do not count an interrupted wrapper as a completed run.
