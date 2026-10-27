# Joint motion controls development

Author: Komorebi P.

The positive control module is `controls/PolynomialJointMotionControls.lean`.
It uses actual polynomials over the 2-adic integers and the existing checked
scalar sharpness theorem. It does not use `native_decide`, a placeholder proof,
or a custom axiom.

## Checks implemented

- `linearSystem(Y,T) = Y + T`, `linearPerturbation(Y,T) = 1` have exact base
  root zero and both actual partial Jacobians equal to one.
- For exponent M = 1 and parameter digit v = 1, the prescribed parameter is
  2, the exact solved root is -4, and the first-order error is zero. The root
  is unique for the prescribed parameter, even without a ball restriction.
- For exponent M = 2, the new actual augmented polynomial construction has
  the exact point (Y,T) = (-8,4) as a root.
- At M = 2 the claimed error ideal is 16 Z_2. Omitting K v leaves error -4,
  and reversing its sign leaves error -8. Both nondivisibility statements
  are proved through the checked integer/p-adic divisibility equivalence.
- The parameter-only polynomial Y + Y^2 + T, with T = 2, has an actual even
  root whose error Y + 2 is divisible by 4 and not by 8. Existence is obtained
  from the inherited checked scalar root-motion theorem. This proves that an
  extra error digit cannot hold uniformly for parameter-only motion.

## Development outcomes

Four development compilation calls were made using the pinned portable kit,
one thread, default heartbeat limit, and the existing low-memory runner.

1. Failed on six local simplification goals: derivative cross terms and
   appended-coordinate evaluation did not normalize the Fin indices.
2. Failed again on those local Fin normalization goals after adding
   `Pi.single_apply` and unfolding the join definition.
3. Failed on one remaining goal in `linear_joint_unique`: the tactic treated
   two definitionally equal zero Fin indices as different ring atoms.
4. Passed after normalizing the target with `change y 0 = -4`.

The first two failures were fixed with explicit two-coordinate join lemmas
and `Fin.ext_iff` in derivative simplification. These were elaboration and
tactic-normalization failures; no theorem hypothesis or mathematical target
was weakened. Raw failed logs were returned by the execution tool and were
not saved to standalone files. This note records their outcomes rather than
reconstructing raw logs.

The independent auditor noticed that at p = 2, M = 1 a reversed K v sign
would differ from the correct center by 4, already in the allowed error
ideal. The stronger M = 2 control was therefore added before completion.
The M = 1 check is retained only as an exact positive identity.
