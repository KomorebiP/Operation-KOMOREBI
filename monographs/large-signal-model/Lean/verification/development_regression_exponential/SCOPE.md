P81 exponential-process and probability-mixture helper

The fixed-direction process is the literal finite product of the normalized
factors from ConditionalRandomMultiplier. The coefficient at step i is the
predictable scalar projection (q·φᵢ)/σ. Coordinate measurability of φᵢ at Fᵢ,
measurability of ξᵢ at Fᵢ₊₁, and the actual ConditionalSubgaussian hypothesis at
Fᵢ imply adaptedness, integrability and the conditional event inequalities.
The fixed-q Supermartingale conclusion is derived from those properties.
Neither a design bound nor independence is required.

For σ≠0 the product is proved equal to

 exp(q·responseVector(φ,ξ,n)/σ − q·(designGram(φ,n)q)/2).

The response vector and design Gram are the literal sums from RegressionGeometry;
the exponential identity is not supplied as a premise.

The generic probability-mixture theorem first derives joint integrability from
joint measurability, nonnegativity, the individual supermartingale expectation
budgets, and the initial value one. The product-integrability criterion uses
Tonelli's norm integral. Fubini on each conditioning event then proves the
mixture's supermartingale inequalities. It does not assume mixture integrability
or mixture supermartingale status.

The actual regression family is separately proved jointly measurable in q and
history at Fₙ. Its probability mixture is the literal Bochner integral over q.
The module proves its supermartingale property, pointwise nonnegativity, initial
value one, almost-everywhere integrability of the mixing fiber, and its exact
integrand identity with the Gaussian score/Gram formula. A generic probability
mixture is interpreted as the Bochner-integral version on exceptional fibers;
the derived fiber-integrability theorem supplies the actual a.e. statement.
The consuming Gaussian calculation proves its own fiber integrability directly.

The semantic controls reject actual False: an after-response design gives a
first-step normalized expectation exp(1/2)>1 despite genuine deterministic
conditional noise bounds, and a mixing measure of mass two gives initial value
two instead of one.

Gaussian normalization/determinant identities, the ridge confidence capstone,
and Ville's time-uniform crossing theorem are separate consuming modules. This
receipt establishes the exponential and mixture helpers, not full P81 alone.
