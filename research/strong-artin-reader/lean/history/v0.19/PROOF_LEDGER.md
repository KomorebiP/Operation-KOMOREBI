# Proof ledger — Strong Artin Lean v0.19

## Evidence label

Every item below is **Lean-checked as written** in the pinned environment. These are algebraic nonlinear-lifting theorems over nilpotent coefficient thickenings. Their application to the actual Strong Artin deformation and Hecke equations remains conditional on the explicit arithmetic hypotheses listed in `RESEARCH_BOUNDARY.md`.

## `PowerDivisibility.lean`

Definition:

- `PowDivisible pi n x`: there exists `y` with `pi^n • y = x`.

Checked theorems:

1. `powDivisible_zero`
2. `powDivisible_zero_elem`
3. `PowDivisible.add`
4. `PowDivisible.neg`
5. `PowDivisible.sub`
6. `PowDivisible.map`
7. `PowDivisible.smul`
8. `PowDivisible.of_succ`
9. `PowDivisible.mono`
10. `eq_zero_of_pow_eq_zero`

## `NilpotentRightInverse.lean`

Checked theorems:

11. `isNilpotent_smul_end`
12. `exists_exact_rightInverse_of_nilpotent_error`
13. `exists_exact_rightInverse_of_scalar_nilpotent_error`
14. `surjective_of_scalar_nilpotent_approx_rightInverse`

### Mechanism

If

```text
A = J.comp R₀ - id
```

is nilpotent, then `1 + A = J.comp R₀` is a unit in `Module.End R W`. Composing `R₀` with its inverse produces an exact right inverse of `J`.

## `NonlinearHenselStep.lean`

Definitions:

- `remainder F J x delta`
- `RemainderRaisesOne pi F J`

Checked theorems:

15. `correction_is_powDivisible`
16. `rightInverse_correction_cancels`
17. `exists_next_approximation`
18. `next_approximation_congruent`

### Mechanism

For error `F x`, choose

```text
delta = -rightInv (F x).
```

The exact right inverse cancels the linear term. The remaining defect is exactly the nonlinear Taylor remainder, which gains one power by hypothesis.

## `NonlinearHenselTower.lean`

Checked theorems:

19. `exists_approximation_tower`
20. `exists_approximation_at_depth`
21. `exists_exact_solution_of_pow_eq_zero`

The tower satisfies

```text
F (x n) ∈ pi^(n+1) W
x (n+1) - x n ∈ pi^(n+1) X.
```

## `RelativeNonlinearHenselCapstone.lean`

Checked theorems:

22. `exists_nonlinear_tower_of_nilpotent_approx_rightInverse`
23. `exists_exact_solution_of_nilpotent_approx_rightInverse`
24. `exists_exact_solution_of_finite_thickness`

These combine nilpotent correction of the approximate right inverse with the nonlinear Hensel tower.

## `VariableJacobianHensel.lean`

Definitions:

- `SameResidual pi base x`
- `variableRemainder F D x delta`
- `VariableRemainderRaisesOne pi F D`

Checked theorems:

25. `sameResidual_self`
26. `sameResidual_of_sameResidual_of_powDivisible_sub`
27. `exists_next_variable_approximation`
28. `exists_variable_approximation_tower`
29. `exists_exact_solution_variableJacobian`

### Mechanism

At each point of the residual fibre, the current Jacobian has an approximate right inverse with nilpotent error. It is corrected to an exact right inverse at that stage. Positive-depth corrections preserve the residual fibre, so the hypothesis can be reused recursively.

## `QuadraticRemainderGain.lean`

Definitions:

- `quadraticMap`
- `quadraticDerivative`

Checked theorems:

30. `quadratic_variableRemainder`
31. `quadratic_remainder_raises_one`
32. `exists_exact_quadratic_solution`

The exact identity is

```text
remainder = bilinear delta delta.
```

Thus quadratic systems satisfy the one-power gain automatically.

## Declaration and axiom audit

New v0.19 source contains:

- theorem declarations: **32**
- definitions: **8**
- lemmas: **0**
- abbreviations: **0**
- structures: **0**
- instances: **0**
- `sorry`: **0**
- `admit`: **0**
- custom `axiom`: **0**
- custom `opaque`: **0**

The displayed capstones depend only on ordinary Lean/Mathlib foundations:

- `propext`
- `Classical.choice`
- `Quot.sound`
