# Research boundary after Strong Artin Lean v0.23

## Strongest closed theorem

Let `P` be a presentation and suppose an explicit arithmetic datum identifies
its intrinsic cotangent `H1` with a finite-dimensional Selmer obstruction space
`H`.  If a one-prime interface detects every nonzero class of `H`, then Lean
constructs an admissible finite set `Q` satisfying

```text
Q.card = finrank S P.toExtension.H1Cotangent;
ker (rawEvaluationMap D I Q) = relationSyzygies P;
rawEvaluationMap D I Q is surjective;
relationSyzygies P → raw obstruction → (Q → S) is exact.
```

The family is cardinality-minimal among scalar families with this kernel
property.

## Presentation independence

The selected set lives on the intrinsic Selmer space.  Therefore the same `Q`
works for any two compared presentations, reducing each raw kernel to its own
relation-syzygy module.  Redundant equations alter only the invisible syzygy
kernel; they do not alter the intrinsic auxiliary count.

Under conormal independence, the syzygy kernels vanish and the two raw
obstruction spaces are linearly equivalent through the common selected
coordinate space.  This equivalence preserves all selected evaluations.

## Corrected Taylor--Wiles endpoint

The valid presentation-level conclusion is

```text
selected arithmetic auxiliaries reduce the raw dual kernel to relation syzygies,
```

not

```text
selected arithmetic auxiliaries make every redundant raw kernel zero.
```

The latter is false when relation syzygies are nonzero, because every genuine
arithmetic functional factors through the intrinsic obstruction quotient.

## First open technical implication

The next internal bridge is

```text
kernel of augmented transpose Jacobian = relation syzygies
  → image of augmented Jacobian = compatible equation subspace
  → nonlinear lifting inside that compatible target.
```

This should either produce a syzygy-compatible Hensel theorem or justify a
conormally independent reduced first-jet presentation before invoking the
existing nonlinear lifting pipeline.

## First open arithmetic implication

The comparison datum

```text
P.toExtension.H1Cotangent ≃ transverse dual Selmer
```

is still an arithmetic input.  v0.23 proves all selection, exactness,
minimality, and presentation-independence consequences after that datum and an
arithmetic one-prime interface are supplied; it does not construct either one.

## Global boundary

The dominant independent gap remains construction of a nonzero patchable,
determinant-bearing automorphic carrier for the finite-Satake descent.  v0.23
does not prove local Tate comparison, Chebotarev instantiation, relative
patching, ramified attachment, solvable-image Strong Artin, or unrestricted
Strong Artin.
