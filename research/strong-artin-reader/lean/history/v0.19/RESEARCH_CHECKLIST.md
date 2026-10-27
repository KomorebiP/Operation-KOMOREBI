# Strong Artin live checklist after v0.19

Status meanings: `[x]` closed at the stated formal boundary; `[~]` active; `[ ]` open; `[E]` external theorem in a declared range.

## Relative nonlinear Hensel lifting — v0.19

- [x] define the `pi`-power filtration on modules;
- [x] prove closure under addition, subtraction, scalar multiplication, and linear maps;
- [x] prove deeper divisibility implies shallower divisibility;
- [x] prove nilpotent scalar error gives a nilpotent endomorphism error;
- [x] correct a nilpotent-error approximate right inverse to an exact right inverse;
- [x] prove one genuine nonlinear Hensel improvement step;
- [x] prove the next state is congruent modulo the previous depth;
- [x] construct a compatible approximation tower through every depth;
- [x] obtain an exact root when the coefficient parameter is nilpotent;
- [x] allow a state-dependent Jacobian throughout the residual fibre;
- [x] prove positive-depth corrections remain in that residual fibre;
- [x] obtain an exact solution for the variable-Jacobian system;
- [x] prove affine-quadratic systems satisfy the Taylor-gain hypothesis automatically;
- [x] obtain an exact quadratic root under the relative Jacobian hypotheses.

## Arithmetic instantiation of v0.19

- [ ] present the actual deformation/Hecke equations as a map `F` over the finite coefficient quotient;
- [ ] identify its state-dependent Jacobian `D`;
- [ ] lift the v0.17 residual augmented-Jacobian right inverse to the coefficient ring;
- [ ] prove the lifted composite is `id + pi • E` throughout the residual fibre;
- [ ] prove the actual Taylor remainder gains one power;
- [ ] apply the v0.19 capstone to reach the explicit finite precision `m₀`.

## Local and global arithmetic comparison

- [~] compare continuous local Galois `H¹` to the finite cyclic model;
- [ ] prove local Tate duality agrees up to a nonzero unit with `trace(PX)`;
- [E] realize the Chebotarev-ready conjugacy class outside the bad set;
- [ ] instantiate the arithmetic one-prime interface and produce `Q_N`;
- [ ] prove the global Selmer--Jacobian equivalence;
- [ ] identify arithmetic local variables with the checked auxiliary columns.

## Dominant carrier and completion block

- [ ] construct a nonzero patchable determinant-bearing residual finite-Satake packet;
- [ ] establish Taylor--Wiles level variation and the Galois determinant/deformation action;
- [ ] construct a flat/MCM relative patched module or a finite-depth carrier;
- [ ] identify generic coefficients with the split cyclic branches;
- [ ] prove quotient-character twist equivariance;
- [ ] prove ramified local attachment;
- [ ] iterate every invariant solvable Clifford step;
- [ ] conclude finite solvable-image Strong Artin;
- [ ] develop a nonabelian-simple-factor mechanism beginning with `A₅`;
- [ ] conclude unrestricted Strong Artin.

## First open theorem

For the nonlinear lane, the first arithmetic theorem is:

```text
v0.17 residual augmented-Jacobian surjectivity
  -> lifted approximate right inverse over O / pi^m
  -> residual-fibre stability and Taylor gain for the actual equations.
```

Once those concrete comparisons are supplied, v0.19 produces the nonlinear finite-depth lift automatically.
