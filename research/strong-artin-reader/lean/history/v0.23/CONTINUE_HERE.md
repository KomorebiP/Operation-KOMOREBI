# Continue Strong Artin from v0.23

## Restore point

Use this directory as the canonical additive checkpoint above the exact bases:

```text
Strong_Artin_Lean_v0.22.0_Presentation_Cotangent_Obstruction_Checked.zip
Strong_Artin_Lean_v0.15.0_Adaptive_Auxiliary_Set_Checked.zip
```

Preserve the base hashes recorded in `README.md`.  Do not replace intrinsic
cotangent `H1` by a redundant transpose-Jacobian kernel.

## Strongest checked endpoint

```text
one-prime detection on intrinsic Selmer / cotangent H1
  → exactly intrinsic-rank many admissible labels
  → raw selected kernel = relation syzygies
  → surjective raw evaluation to selected coordinates
  → cardinality-minimal exact syzygy-corrected sequence.
```

The same intrinsic selected set works for distinct presentations of the same
Selmer obstruction.

## Next internal theorem

Let `J : U → W` be the presentation Jacobian and let `Syz ≤ ker Jᵛ` be the
relation-syzygy space.  After auxiliary selection, the dual kernel is exactly
`Syz`.  Define the compatible target

```text
W_compat = { w : W | φ w = 0 for every φ ∈ Syz }.
```

Prove in finite dimension that

```text
range J_aug = W_compat.
```

Then formulate a nonlinear lifting theorem for an equation map whose defects,
derivatives, and Taylor remainders land in `W_compat`.  This is the correct
syzygy-aware replacement for demanding surjectivity onto a redundant equation
space.

A valid alternative is to construct a conormally independent reduced
first-jet presentation and prove it defines the same intrinsic deformation
problem.

## Arithmetic theorem still required

Construct the domain-specific equivalence

```text
intrinsic cotangent H1 ≃ transverse dual Selmer
```

and the actual one-prime Taylor--Wiles interface.  Continuous local Galois
cohomology, Tate pairing, Chebotarev realization, and the automorphic carrier
remain external/open.

## Verification

```bash
python3 verify.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --max-modules 8
python3 verify.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --resume
```
