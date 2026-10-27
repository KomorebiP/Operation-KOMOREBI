# Continue Strong Artin from v0.20

## Restore point

Use this directory as the canonical additive checkpoint above:

```text
Strong_Artin_Lean_v0.19.0_Relative_Nonlinear_Hensel_Checked.zip
```

Preserve the exact base hash and every arithmetic boundary.

## Strongest checked endpoint

```text
surjective residual Jacobian over a residue field
  -> residual matrix right inverse
  -> entrywise coefficient-ring lift
  -> stable approximate inverse throughout the residual fibre
  -> automatic polynomial Taylor gain
  -> exact nonlinear solution over a nilpotent principal thickening.
```

The capstone is:

```text
Komorebi.StrongArtin.SurjectiveResidueHomPolynomialHensel.
  exists_exact_solution_of_surjective_residue_jacobian
```

## Next technical theorem

Connect the arithmetic deformation problem to the capstone:

1. choose a finite-level coordinate presentation of the relative deformation/Hecke ring;
2. express its defining equations as the v0.20 polynomial system;
3. identify the residual coordinate Jacobian with the augmented Jacobian completed by the v0.17 Taylor--Wiles columns;
4. derive residual surjectivity from the Selmer--Jacobian comparison;
5. apply the v0.20 capstone at the finite attachment level `m₀`.

A separate useful algebraic continuation is a truncation theorem showing that a restricted formal-power-series presentation over a fixed Artin quotient is represented by the finite polynomial syntax used here.

## Independent priorities

The continuous local Galois/Tate comparison and the patchable residual automorphic carrier remain independent major priorities.

## Verification

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```
