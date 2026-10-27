# Strong Artin Lean v0.21.0 — Completed Formal Presentation and Algebra Point — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.20.0_Polynomial_Presentation_Hensel_Checked.zip`  
**Base SHA-256:** `9dafcfcd6d23871e5a167b18314083afae3159a74c16e9aa4fa9bc65f4b3770f`  
**Status:** additive Lean checkpoint; complete direct source dependency closure freshly replayed with warnings as errors.

## Purpose

v0.20 proved nonlinear Hensel lifting for finite coordinate polynomial systems over a principal nilpotent thickening. Its first open algebraic bridge was the passage from a completed local presentation by multivariate formal power series to that finite polynomial syntax.

v0.21 closes that bridge. Over a finite nilpotent coefficient ring, canonical substitution into a multivariate formal power series is exactly evaluation of a finite total-degree truncation. The polynomial compiler preserves evaluation and formal partial derivatives. At a centered presentation, every truncation of level at least two has the same residual Jacobian: the matrix of the original untruncated linear coefficients.

The final result produces not merely a zero of the formal equations, but an actual algebra point of the quotient by the relation ideal.

## Main theorem

Let `q : R →+* k` be a surjective homomorphism to a field. Assume

```text
RingHom.ker q = Ideal.span {pi},
pi ^ N = 0,
2 ≤ N.
```

Let `system : κ → MvPowerSeries ι R` be a finite formal-power-series system. Write

```text
constantCoefficientVector system : κ → R
linearCoefficientMatrix system : Matrix κ ι R.
```

If the equations vanish at the origin modulo `pi`, and the reduced linear-coefficient map is surjective,

```text
q ∘ constantCoefficientVector system = 0,
Function.Surjective
  (matrixLinear ((linearCoefficientMatrix system).map q)),
```

Lean proves that there is a point `x : ι → R`, all of whose coordinates lie in `(pi)`, such that canonical Mathlib substitution annihilates the original **untruncated** equations:

```text
∃ x : ι → R,
  (∀ i, PowDivisible pi 1 (x i)) ∧
  formalEvalSystem system x = 0.
```

The capstone is:

```text
Komorebi.StrongArtin.CompletedPresentationHenselCapstone.
  exists_exact_solution_of_residual_zero_and_surjective_linear_part
```

## Algebra-point capstone

Let

```text
relationIdeal system = Ideal.span (Set.range system).
```

The exact formal solution yields an `R`-algebra homomorphism

```text
(MvPowerSeries ι R ⧸ relationIdeal system) →ₐ[R] R
```

whose value on each coordinate variable is the corresponding coordinate of the solution and hence lies in `(pi)`.

The capstone is:

```text
Komorebi.StrongArtin.FormalPresentationPoint.
  exists_algebra_point_of_surjective_linearCoefficientMatrix
```

Symbolically:

```text
centered completed formal presentation
  + principal nilpotent residue ideal
  + surjective reduced linear coefficient matrix
  -> finite total-degree truncation
  -> v0.20 polynomial Hensel lift
  -> exact zero of the original untruncated formal equations
  -> algebra point of the completed presentation quotient.
```

## Canonical substitution equals finite truncation

For coordinates `x i ∈ (pi)` and `pi ^ N = 0`, v0.21 proves

```text
formalEval f x = MvPolynomial.eval x (f.truncTotal N).
```

The left side uses Mathlib's actual `MvPowerSeries.subst`; it is not a newly invented evaluation surrogate. Every monomial of total degree at least `N` vanishes after substitution, so the infinite series becomes exactly finite at the Artin level.

The theorem is:

```text
Komorebi.StrongArtin.MvPowerSeriesNilpotentSubstitution.
  formalEval_eq_artinEval
```

It also proves independence from every later truncation level `M ≥ N`.

## Jacobian identification

For every truncation level `N ≥ 2`, the coordinate Jacobian at the residual origin is exactly the original matrix of linear coefficients:

```text
jacobianMatrix (compileSystemAt N system) 0
  = linearCoefficientMatrix system.
```

After reduction through any coefficient homomorphism `q`, the same equality holds entrywise. Therefore no truncation-dependent Jacobian hypothesis remains.

The capstone is:

```text
Komorebi.StrongArtin.FormalPowerSeriesJacobianAtOrigin.
  map_jacobianMatrix_compileSystemAt_zero
```

## What changed in the Strong Artin pipeline

Before v0.21, the nonlinear lane stopped at:

```text
finite polynomial presentation
  + surjective residual Jacobian
  -> exact finite-level solution.
```

The new endpoint is:

```text
finite completed formal-power-series presentation
  + surjective reduced linear coefficient matrix
  -> exact point of the completed quotient.
```

Thus, once the arithmetic deformation or Hecke ring is exhibited by a finite completed presentation and its linear coefficient matrix is identified with the Taylor--Wiles-completed Jacobian, no separate truncation or formal-series convergence theorem remains at the finite Artin level.

## Boundary

This checkpoint does **not** prove that the actual Strong Artin deformation or Hecke algebra has been supplied with the required finite completed presentation. It does not prove that its reduced linear coefficient matrix is the augmented Jacobian constructed in the earlier projector/Taylor--Wiles work.

Still required:

1. construct the actual patchable determinant-bearing residual finite-Satake automorphic complex;
2. present its relevant finite-level deformation/Hecke algebra by finitely many formal coordinates and relations;
3. prove the global Selmer--Jacobian comparison and identify the arithmetic Taylor--Wiles variables with the formal coordinates;
4. identify the reduced linear coefficient matrix with the already completed arithmetic Jacobian;
5. complete the continuous local Galois cohomology, local Tate-pairing, and Chebotarev instantiation;
6. establish relative patching or a finite-depth carrier, twist equivariance, ramified local attachment, and the solvable recursion.

Strong Artin remains open.

## Verification

Run:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier checks the exact v0.20 archive hash, pinned Lean and mathlib revisions, declaration counts, absence of proof escapes, and fresh compilation of the complete 19-module direct dependency closure with warnings treated as errors. The verifier is resumable with `--resume` after an external wrapper interruption.
