# Research boundary after Strong Artin Lean v0.22

## Strongest new theorem

For an algebra presentation `P`, the relation-differential kernel—the finite-support transpose-Jacobian kernel—fits into a canonical exact sequence

```text
0 → relationSyzygies P
  → presentationObstructionDual P
  → P.toExtension.H1Cotangent
  → 0
```

at the level of the checked injection, exactness, and surjection statements. The final `→ 0` records proved surjectivity; an explicit quotient `LinearEquiv` was not packaged because its nested quotient type did not elaborate reliably.

The canonical map is injective exactly when

```text
Algebra.Presentation.differentials.hom₁ P
```

is injective, i.e. when the chosen relations are independent in the conormal module.

## Arithmetic consequence

Given an external equivalence

```text
P.toExtension.H1Cotangent ≃ₗ[S] transverseSelmerObstruction,
```

the raw presentation kernel surjects onto the Selmer obstruction space with kernel exactly `relationSyzygies P`.

Therefore the arithmetic Selmer–Jacobian comparison cannot in general be stated as

```text
Selmer ≃ ker(raw transpose Jacobian)
```

without an additional conormal-independence hypothesis. The correct general statement is

```text
Selmer ≃ intrinsic cotangent H1
```

or, informally,

```text
Selmer ≃ raw transpose-Jacobian kernel / relation syzygies.
```

## Negative result

If relation syzygies are nonzero, every genuine Selmer functional pulled back to the raw presentation kernel vanishes on them. Thus no arithmetic auxiliary-prime family can completely detect the raw kernel. Presentation redundancy must be removed or quotiented before applying the minimal auxiliary-selection theorem.

## Effect on prior checkpoints

v0.15–v0.21 remain valid as abstract linear-algebra, auxiliary-selection, Jacobian-completion, and nonlinear-lifting theorems. v0.22 corrects their arithmetic instantiation target: the input obstruction space must be intrinsic, or the chosen presentation must be shown conormally independent.

## First open arithmetic implication

```text
actual relative Strong Artin deformation/Hecke problem
  → finite completed presentation P
  → cotangent H1(P) ≃ transverse dual Selmer
  → conormal independence or explicit syzygy quotient
  → arithmetic one-prime interface
  → v0.15–v0.21 lifting pipeline.
```

## Non-claims

v0.22 does not prove the Selmer comparison datum exists, does not prove that the arithmetic presentation is a complete intersection, does not construct a determinant-bearing automorphic carrier, and does not prove Strong Artin.
