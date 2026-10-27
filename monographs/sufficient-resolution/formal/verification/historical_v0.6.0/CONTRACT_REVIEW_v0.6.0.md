# Contract review — v0.6.0

The sources use standard Mathlib continuous-linear-map composition, Banach-algebra
exponentials, real operator norms, interval integrals and derivatives. No custom
notation redefines these operations. All proof hypotheses are printed in the
principal-signatures log. No production source changes the kernel or declares axioms.

* Duhamel: backward derivative plus actual FTC; no assumed desired integral identity.
* CompleteSpace X and Z: explicit real Banach-space generators. Output target Y
  only needs normed linear structure. q has no injection/surjection assumption.
* Bounds: complete operator norms, not values on selected states. Arbitrary
  envelope theorem uses [0,t], with t>=0. Exponential corollaries assume all s>=0.
* The nonnegative amplitude assumptions in norm_evolution_le_response are retained
  in the interface but unused by that base proof; later monotonicity proofs use
  them explicitly. They do not encode the conclusion or a hidden stability theorem.
* Rates may be of either sign. Equal-rate formula is separately proved, avoiding
  division by zero. Stable corollaries require rate>0 and supplied flow decay.
* Initialization: state-level model allowance is multiplied by ||x||, and an
  arbitrary z has a separate propagated ||qx-z|| term. No prepared-state claim is
  promoted to all-state closure.
* Scalar sharpness: actual flow identified via homogeneous ODE uniqueness;
  unboundedness quantified over every positive epsilon and every real bound.
* Composition: both stage errors retained with map-norm amplification.
* Finite rational tests: only coefficients through the recorded degree. The
  antiderivative expansion is independent of the factorial closed form. They
  do not independently prove real exponentials or infer semigroup growth.

The claims are new formal additions to this project, not a certificate of historical
novelty. Classical Duhamel/semigroup reasoning remains classical mathematics.
