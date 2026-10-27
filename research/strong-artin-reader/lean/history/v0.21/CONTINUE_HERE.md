# Continue Strong Artin from v0.21

## Restore point

Use this directory as the canonical additive checkpoint above:

```text
Strong_Artin_Lean_v0.20.0_Polynomial_Presentation_Hensel_Checked.zip
```

Preserve the exact base SHA-256 and every arithmetic boundary.

## Strongest checked endpoint

```text
finite completed formal-power-series presentation
  + principal nilpotent residue ideal
  + residual vanishing of constants
  + surjective reduced linear coefficient matrix
  -> exact nilpotent solution of the original untruncated equations
  -> algebra point of the completed presentation quotient.
```

Capstones:

```text
Komorebi.StrongArtin.CompletedPresentationHenselCapstone.
  exists_exact_solution_of_residual_zero_and_surjective_linear_part

Komorebi.StrongArtin.FormalPresentationPoint.
  exists_algebra_point_of_surjective_linearCoefficientMatrix
```

## First open technical theorem

Connect the arithmetic deformation problem to the formal capstone:

1. select the finite-level relative deformation or localized Hecke algebra;
2. prove a finite formal presentation
   ```text
   R[[X_1,...,X_r]] / (f_1,...,f_s);
   ```
3. identify the formal coordinates with ordinary and Taylor--Wiles deformation variables;
4. identify the reduced linear coefficient matrix `(coeff_{X_i} f_j mod pi)` with the augmented arithmetic Jacobian completed in v0.17;
5. derive its surjectivity from the global Selmer--Jacobian comparison;
6. apply the v0.21 algebra-point theorem at the explicit finite attachment depth `m₀`.

## Independent priorities

The next local arithmetic target remains the continuous local `H¹`/finite-cyclic comparison and local Tate-pairing identity up to a unit. The dominant global target remains construction of the nonzero patchable determinant-bearing finite-Satake automorphic packet.

## Verification

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Use `--resume` if an external execution wrapper ends after some module results have already been recorded.
