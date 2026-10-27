# Strong Artin Lean v0.23.0 — Intrinsic Syzygy-Corrected Auxiliary Selection — Checked

**Author:** Komorebi P.  
**Primary base:** `Strong_Artin_Lean_v0.22.0_Presentation_Cotangent_Obstruction_Checked.zip`  
**Primary base SHA-256:** `b45ed0b2aaffed5ec8fcb2d553766323efb241ce8ceef0295f514bf9d29c8228`  
**Auxiliary-selection base:** `Strong_Artin_Lean_v0.15.0_Adaptive_Auxiliary_Set_Checked.zip`  
**Auxiliary-selection base SHA-256:** `77b0988d26f5a61d02028339697942e3863457074a1682124c7a4b538817ab4e`  
**Status:** additive Lean checkpoint; resumable fresh replay PASS.

## Purpose

v0.22 proved that a raw presentation-dependent transpose-Jacobian kernel is
not generally the intrinsic obstruction space.  There is a canonical exact
sequence

```text
relation syzygies → raw presentation obstruction → intrinsic cotangent H1,
```

and genuine arithmetic functionals vanish on the relation-syzygy kernel.
Consequently, Taylor--Wiles selection cannot legitimately be run by demanding
that arithmetic probes kill the entire raw kernel when the displayed relation
system is redundant.

v0.23 corrects the auxiliary-selection pipeline.  Selection is performed on
the intrinsic cotangent-H1 / Selmer obstruction space.  Pulling the selected
functionals back to any presentation cuts its raw obstruction kernel down
**exactly** to relation syzygies.

## Main theorem

Assume:

1. `P` is a presentation;
2. `D : SelmerPresentationComparison.Datum P H` identifies intrinsic
   cotangent `H1` with a finite-dimensional Selmer obstruction space `H`;
3. `I : OnePrimeSelectionInterface S H Aux` detects every nonzero intrinsic
   obstruction by an admissible scalar auxiliary functional.

Then Lean constructs a finite set `Q` such that:

```text
all labels in Q are admissible;
Q.card = finrank S P.toExtension.H1Cotangent;
ker (rawEvaluationMap D I Q) = relationSyzygies P;
rawEvaluationMap D I Q is surjective;
relationSyzygies P → raw obstruction → (Q → S) is exact;
Q is cardinality-minimal among scalar families with that same kernel property.
```

The capstone is:

```text
Komorebi.StrongArtin.IntrinsicSyzygyCorrectedCapstone.
  exists_intrinsic_minimal_exact_auxiliary_set
```

## Exact syzygy-corrected sequence

The selected raw evaluation map is

```text
rawEvaluationMap D I Q : presentationObstructionDual P →ₗ[S] (Q → S).
```

Lean proves

```text
ker (rawEvaluationMap D I Q) = relationSyzygies P
```

and surjectivity.  Together with the injective subtype inclusion this gives the
operational short exact sequence

```text
0 → relationSyzygies P
  → presentationObstructionDual P
  → (Q → S)
  → 0.
```

Thus genuine auxiliary primes remove every **intrinsic** obstruction while
leaving precisely the presentation redundancy that arithmetic functionals are
forced to ignore.

## Intrinsic auxiliary count

The selected cardinality is

```text
Q.card = finrank S P.toExtension.H1Cotangent,
```

not the dimension of the potentially inflated raw transpose-Jacobian kernel.
When the raw obstruction space is finite-dimensional, Lean proves

```text
Q.card + finrank S (relationSyzygies P)
  = finrank S (presentationObstructionDual P).
```

This separates arithmetic obstruction rank from presentation redundancy.

## Minimality

Any scalar auxiliary family whose pulled-back evaluations have kernel exactly
`relationSyzygies P` has at least `finrank S H` members.  The set selected from
the one-prime interface attains this lower bound.  It is therefore
cardinality-minimal at the intrinsic obstruction level.

## Presentation independence

If two presentations `P₁` and `P₂` are both compared with the same intrinsic
Selmer space `H`, one and the same selected set `Q` satisfies

```text
ker rawEvaluation₁ = relationSyzygies P₁,
ker rawEvaluation₂ = relationSyzygies P₂,
```

and both raw evaluation maps are surjective.

If both relation systems are conormally independent, their syzygy modules
vanish and the two raw obstruction spaces are linearly equivalent through the
common auxiliary-coordinate space.  Lean proves that this comparison preserves
every selected auxiliary coordinate.

## Correct interpretation

v0.23 does **not** prove that auxiliary primes make a redundant displayed
Jacobian surjective onto its entire equation space.  That would contradict the
syzygy directions identified in v0.22.  The correct conclusion is:

```text
arithmetic probes kill the intrinsic obstruction quotient;
the residual raw kernel is exactly relation redundancy.
```

The next technical problem is a syzygy-compatible lifting theorem: identify the
compatible equation subspace annihilated by relation syzygies, prove the
augmented Jacobian is onto that intrinsic target, and run nonlinear lifting
there—or construct a conormally independent presentation.

## Verification

Pinned environment:

```text
Lean 4.34.0-rc2
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
-DwarningAsError=true
```

The verifier stages exact source from the preserved v0.15 and v0.22 archives,
adds all five v0.23 modules, and replays the resulting fourteen-module closure.
The replay was deliberately split into resumable batches after a one-shot
wrapper hit its external execution ceiling.

Final result:

- 3 replayed v0.15 dependency modules;
- 6 replayed v0.22 dependency modules;
- 5 new v0.23 modules;
- 14 total modules with observed compiler return code `0`;
- 18 new theorem declarations;
- 4 new definitions;
- 583 new source lines;
- 0 `sorry`;
- 0 `admit`;
- 0 custom `axiom` declarations;
- 0 custom `opaque` declarations;
- no `sorryAx` in compiler output.

Representative axiom reports contain only ordinary Lean/Mathlib foundations:

```text
propext
Classical.choice
Quot.sound
```

## Replay

```bash
python3 verify.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --max-modules 8

python3 verify.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --resume
```
