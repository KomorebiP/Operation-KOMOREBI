# Joint motion construction

Author: Komorebi P.

`PolynomialJointMotion.lean` adds two theorems.

- `exists_joint_root_certificate` constructs the actual full point from the original solved block's two integral inverse identities. It returns exact perturbed equations, exact prescribed parameters, full displacement and uniqueness-ball divisibility, full-point uniqueness at those parameters, and the integral corrected error.
- `exists_joint_root_motion` derives that certificate from the actual original solved Jacobian's written rational inverse bound. It converts the solved error into the first-order formula with force `H(a) + K v` and exponent `2 * M - 3 * s`.

The proof uses the actual appended polynomial equations. The negative parameter perturbation produces `T = T(a) + p^M v`. The negative off-diagonal certificate produces the plus sign in `H(a) + K v`. No perturbed Jacobian hypothesis, assumed root, or assumed augmented inverse appears in the public hypotheses.

The first narrow compile failed in two routine elaboration places: the selective namespace opening omitted `join_solved`, and the polymorphic `solvedPart a` needed an explicit integral type before coercion to the fraction field. Both were repaired without changing the mathematical statement. The second narrow compile passed with warnings treated as errors using the pinned portable runtime and unchanged default heartbeat limit.

This narrow compile is development evidence. The separate fresh release gate and raw proof audit remain the release authority.

Source SHA-256 at the passing narrow compile:
`946ca8e3e4f17c71e66db136a1ab70b1012c60dbc1f87ded33f2d7defb1b84e4`.
