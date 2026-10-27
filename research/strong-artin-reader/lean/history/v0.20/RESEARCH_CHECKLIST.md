# Strong Artin live checklist after v0.20

Status meanings: `[x]` closed at the stated boundary; `[~]` active; `[ ]` open; `[E]` external theorem in a declared range.

## Finite polynomial presentation and nonlinear lifting

- [x] define a general finite polynomial-expression syntax;
- [x] define its directional derivative by sum and product rules;
- [x] prove derivative linearity in the correction direction;
- [x] prove polynomial increments preserve filtration depth;
- [x] prove polynomial derivatives vary with the base-point filtration depth;
- [x] prove every polynomial first-order remainder gains one filtration level;
- [x] package finite families as polynomial systems;
- [x] prove every polynomial system satisfies the v0.19 variable remainder condition;
- [x] define the standard-coordinate polynomial Jacobian matrix;
- [x] prove Jacobians are congruent throughout one residual fibre;
- [x] convert entrywise matrix congruence to a `pi`-multiple endomorphism error;
- [x] lift a residual matrix right inverse entrywise;
- [x] construct a matrix right inverse from residual Jacobian surjectivity over a field;
- [x] derive a stable approximate right inverse from one residual right inverse;
- [x] obtain an exact nonlinear solution over a nilpotent principal thickening;
- [x] capstone: surjective residual polynomial Jacobian implies exact lift.

## Arithmetic instantiation

- [ ] present the actual finite-level Strong Artin deformation/Hecke equations as a finite polynomial system;
- [ ] identify its coordinate Jacobian with the arithmetic augmented Jacobian;
- [ ] prove the global Selmer--Jacobian equivalence;
- [ ] identify arithmetic Taylor--Wiles local variables with the checked auxiliary columns;
- [ ] verify the residue homomorphism and principal nilpotent parameter in the chosen finite coefficient quotient;
- [ ] apply the v0.20 capstone through the explicit attachment precision `m₀`.

## Local arithmetic comparison

- [~] compare continuous local Galois `H¹` to the finite cyclic model;
- [ ] prove local Tate duality agrees up to a nonzero unit with `trace(PX)`;
- [E] realize the Chebotarev-ready conjugacy class outside the bad set;
- [ ] instantiate the arithmetic one-prime interface and produce `Q_N`.

## Dominant carrier and completion block

- [ ] construct a nonzero patchable determinant-bearing residual finite-Satake packet;
- [ ] establish Taylor--Wiles level variation and the Galois determinant/deformation action;
- [ ] construct a flat/MCM relative patched module or finite-depth carrier;
- [ ] identify generic coefficients with the split cyclic branches;
- [ ] prove quotient-character twist equivariance;
- [ ] prove ramified local attachment;
- [ ] iterate every invariant solvable Clifford step;
- [ ] conclude finite solvable-image Strong Artin;
- [ ] develop a nonabelian-simple-factor mechanism beginning with `A₅`;
- [ ] conclude unrestricted Strong Artin.

## First open theorem

For the nonlinear lane, the next arithmetic theorem is now:

```text
actual finite deformation/Hecke presentation
  + v0.17 arithmetic Selmer/Jacobian identification
  -> surjectivity of the residual coordinate Jacobian.
```

Once this is established, v0.20 supplies the full nonlinear finite-level lift without a separate Taylor-remainder or right-inverse-stability proof.
