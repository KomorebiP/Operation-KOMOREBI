# Sharp dyadic Euler tower: recovered and formalized

The earlier manuscript's sharp dyadic tower is now proved in Lean for the actual coefficients used by the existing Euler reconstruction. No coefficient valuation or Bernoulli identity is assumed as a hypothesis.

The source proves the formal power series bridge

`inverseSeries = cothNormalized - X * derivative Q cothNormalized`,

where `cothNormalized = rescale 2 (bernoulliPowerSeries Q) + X`. It then extracts, for m>0,

`beta_m = -2^(2m) (2m-1) B_(2m)/(2m)!`.

The weighted coefficients `kappa_m = beta_m * 2^(2m) * (2m)!` have exact valuation `4m-1`, using the imported and proved theorem `Bernoulli.padicValRat_bernoulli`.

The actual completed-ring error satisfies

`2^(4M+3) | EulerEven(n) - truncationPadic(n,M)` in Z_2,

for every natural n,M. At n=M+1, its rational valuation is exactly 4M+3. Thus this uniform exponent is optimal. The prior checked bound was 2M+2.

For 0<m<=n, the exact summand valuation is

`4m-1 + v2(choose(2n,2m))`.

The general row theorem accepts any numerical lower bound on all omitted weights and proves the corresponding completed-ring tail divisibility. It does not claim that a sum's valuation equals the minimum term valuation: cancellation can improve the sum.

Lean n denotes half the Euler degree, so the first omitted row n=M+1 has full Euler degree 2M+2. The case n<=M is handled automatically as exact zero tail. Positive-depth and nonzero binomial hypotheses are included wherever rational exact valuation is asserted.

Verification: one Lean compiler thread; warningAsError enabled; full source compiles with no warnings or errors. All 27 declarations pass axiom audits with only propext, Classical.choice, and Quot.sound. Two malformed valuation controls are rejected. See tower_verification.json and the logs. The module contains 24 theorems and 3 definitions.

The native unrestricted conjectures 13.2/13.3 are not resolved by these dyadic Euler theorems. The N=4 Nishibuchi addresses are separate coefficient families and should not be conflated with this Euler tower.
