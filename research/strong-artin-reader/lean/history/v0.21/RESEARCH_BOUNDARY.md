# Research boundary after Strong Artin Lean v0.21

## Strongest closed theorem

Let `q : R →+* k` be a surjective homomorphism to a field, with

```text
RingHom.ker q = Ideal.span {pi},
pi ^ N = 0,
2 ≤ N.
```

Let

```text
system : κ → MvPowerSeries ι R
```

be a finite system in finitely many variables and equations. If its constant coefficient vector vanishes after applying `q`, and its matrix of linear coefficients becomes a surjective standard-coordinate linear map after applying `q`, then Lean proves:

```text
∃ x : ι → R,
  (∀ i, x i ∈ (pi)) ∧
  formalEvalSystem system x = 0.
```

Moreover, canonical evaluation at `x` factors through the relation quotient and produces

```text
(MvPowerSeries ι R ⧸ Ideal.span (Set.range system)) →ₐ[R] R.
```

The equations here are the original untruncated formal power series.

## Why truncation is exact

At a point with every coordinate in `(pi)`, a monomial of total degree `d` lies in `pi^d`. If `pi^N = 0`, every term of total degree at least `N` vanishes. Lean proves that Mathlib's canonical substitution is therefore exactly the evaluation of `truncTotal N`, and every later truncation has the same value.

## Why the Jacobian is intrinsic

At the residual origin, every total-degree truncation of level `N ≥ 2` preserves the constant and linear terms. The compiled polynomial Jacobian is therefore exactly the matrix of singleton-degree-one coefficients of the original formal system. The surjectivity hypothesis is independent of the selected cutoff.

## What changed

The v0.20 boundary said that a fixed Artin-level complete-local presentation was expected to truncate to a finite polynomial system but did not prove this.

v0.21 removes that gap:

```text
completed finite formal presentation
  -> exact finite polynomial truncation at a nilpotent level
  -> v0.20 nonlinear Hensel theorem
  -> exact root of the untruncated equations
  -> algebra point of the completed quotient.
```

Thus the remaining nonlinear-lane problem is no longer analytic convergence or truncation. It is arithmetic identification of the actual presentation and its residual linear coefficient matrix.

## First open arithmetic implication

```text
Taylor--Wiles-completed arithmetic deformation problem
  -> finite formal presentation of the relevant deformation/Hecke algebra
  -> reduced linear coefficient matrix equals the augmented arithmetic Jacobian
  -> residual surjectivity.
```

Once this is proved, v0.21 supplies the finite-level algebra point automatically.

## Dominant independent global gap

The principal existence problem remains:

```text
finite-Satake cyclic descent
  -> nonzero patchable determinant-bearing residual automorphic complex.
```

No formal-presentation or Hensel theorem manufactures this carrier.

## Non-claims

v0.21 does not establish:

1. a finite formal presentation of the actual Strong Artin deformation or Hecke ring;
2. the global Selmer--Jacobian comparison;
3. the arithmetic interpretation of Taylor--Wiles variables as the formal coordinates used here;
4. the continuous local Galois `H¹` and local Tate-pairing comparison;
5. Chebotarev realization of the prepared finite conjugacy data;
6. residual automorphic packet occurrence;
7. relative patching, twist equivariance, ramified local attachment, solvable-image Strong Artin, or unrestricted Strong Artin.
