# Self-review and coverage map

## Claim and dependency boundaries

**Primary verdict:** the Lean statements in this companion are proved under
their displayed hypotheses when the accompanying replay succeeds. This is a
self-review of their mapping to the public demonstration, not an independent
review or a certification of the entire Smith chart project.

The analytic claim starts with a positive natural order `N`, a canonical
index `j < N`, and a complex input `‖t‖ < 1`. Its dependencies are:

1. The geometric series converges and gives each residue lane's actual sum
   (`SmithChart.residue_hasSum`, `packet_zero`, `packet_nonzero`).
2. The canonical exponential has exact order `N`
   (`SmithCanonicalRoot.omega_unit_order`, using the pinned Mathlib theorem
   `Complex.exp_two_pi_mul_I_mul_div_eq_one_iff`).
3. Exact-order characters select residues in a finite polynomial
   (`SmithFourier.phase_average_finite`).
4. A finite geometric identity transfers that selection to the rational
   impedance on the open disk (`SmithAnalyticFourier.average_eq_packet`),
   and the canonical-root specialization connects it to the chart's phase.
5. Character orthogonality gives finite Parseval for arbitrary sampled complex
   vectors and its impedance-orbit specialization (`SmithParseval`); the
   canonical root meets its exact-order hypothesis.

`SmithChart.packet_reconstruction`, `packet_dyadic_refinement`, and the
admittance theorems establish further identities. The zero coefficient is one,
while all positive impedance coefficients are two; the zero lane therefore
has a different definition from the other lanes. Admittance is obtained by
substituting `-t`, giving one sign per lane only when `N` is even. For odd
`N`, the sign alternates within the lane and the denominator changes.

## Adversarial checks

| Obligation | Result and boundary |
| --- | --- |
| Smallest order and zero input | `N=1` is admitted; the open-disk theorems include `t=0`. The browser only offers orders at least two. |
| Reflection denominator | The open and closed converses explicitly exclude `z+1=0`. At `z=-1`, Lean's totalized division makes reflection zero despite negative real part; `omitted_denominator_can_fake_passivity` records the counterexample. |
| Ideal open | At `t=1` Lean computes a totalized value, not the physical infinite impedance; `pole_is_totalized_in_lean` makes this visible. The earlier Paper V projective action is bound as source context but not imported or replayed here. |
| Passivity of packets | The zero packet is positive real throughout the open disk. The `N=2`, `j=1` packet at `t=-1/2` is negative real (`-4/3`); an isolated nonzero lane is not generally a passive network. |
| Odd/even duality | At `N=3`, `j=1`, `t=1/2`, the admittance packet is `-8/9`, while the even-order sign formula would give `-8/7`. The Lean fixture proves inequality. |
| Character order | An order-one root used at nominal order two fails to separate residues. The general filter therefore requires exact order, and the canonical root is separately proved to meet it. |
| Nonlinear products | For `F=1+t`, the degree-two coefficient of the even lane of `F²` is one, whereas squaring only the even lane gives zero. The Lean fixture proves the off-diagonal contribution is necessary. |
| Coprime factorization | `crt_projector` uses coprimality explicitly; it does not assert the formula for arbitrary noncoprime factors. |
| Sampling optimality | The formal lower bound concerns the largest interval mass. An equal-density-mass partition is now proved to exist; neither result establishes a general interpolation or estimation optimum. |
| Angular energy | The angular-integral theorems apply for `0 ≤ ρ < 1` and distinguish the zero and nonzero lanes. They do not establish a finite boundary H² norm. |

## Not covered

- A Lean proof of divergence as the radius tends to one or of any finite
  boundary H² norm. The finite-radius angular integrals are proved separately
  from finite phase-orbit Parseval; their scope and self-review are in
  [ENERGY_INTEGRAL_AUDIT.md](ENERGY_INTEGRAL_AUDIT.md).
- A Lean proof that the explicit branch-aware inverse-CDF formula or the
  browser implementation equals the integral-defined CDF. A self-reviewed
  derivation is in [SAMPLING_DERIVATION.md](SAMPLING_DERIVATION.md). The
  density normalization and equal-mass existence are formalized and reviewed
  separately in [SAMPLING_INTEGRAL_AUDIT.md](SAMPLING_INTEGRAL_AUDIT.md).
- Correspondence between the Lean model and the JavaScript, including
  finite precision, UI state, coordinate entry, or exported sessions.
- Hardware validation, a measured-data comparison, or a novelty assessment.
- The contents and status of the later ChatGPT-only continuation.

The source is identified by [source-bindings.json](source-bindings.json).
The compiler accepts only the statements actually present in the Lean files;
the source-to-formal mapping and the checks in this report are self-review.
See the replay receipt for the exact compiler, input hashes, direct cache
hashes, accepted axioms, and execution result.

The bounded JavaScript calculation is separate evidence: it executes the
unchanged pure-math prefix of the pinned script and compares its packet values
to independently calculated phase averages. Its own CDF and inverse are also
compared against one another, which does not establish the integral identity.
See the computation contract and manifest for its finite domain, tolerances,
counts, and provenance. The standalone computation directory has no Git
commit of its own; its copied input is authenticated against the bound Git
object's SHA-256. Independent 45- and 75-digit quadrature also checked 44
quantiles against the stated density. The baseline browser snapped a tiny
neighborhood around the half-turn: at radius `0.97`, probability inputs
`0.5 ± 10⁻¹³` both returned the same angle as `0.5`. Its measured maximum
mass discrepancy in that finite run was about `1.01 × 10⁻¹³`. A local patch
removes the explicit snapping; the same 44-case check on the final patched
source observed about `3.27 × 10⁻¹⁵` at worst. These are not error bounds for
all inputs. The patched source is not the pinned baseline Git object.
