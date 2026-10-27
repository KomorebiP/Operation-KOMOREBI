# Paper IX finite completion ledger

**Author: Komorebi P.**

Release **v0.10.0**. All **24 of 24 named manuscript-proved entries** are covered in their stated scopes. Three classical inputs and two conjectures are tracked separately.

Cumulative inventory: 753 named theorem declarations and 148 explicit definitions across 70 modules. The successful clean build and 901 transitive-axiom reports are recorded in `verification/tenth_clean/verification.json`. Supporting lemmas and examples are included in the declaration count; no discovery count is inferred.

The original status-corrected manuscript remains unchanged. Earlier amendments, including the finite sample/stencil condition and the factorial normalization correction, remain applicable. Manuscript correspondence is mathematical review, not automated semantic equivalence.

## 1.2 — Exact arithmetic packet reconstruction

**Theorem · LEAN_CHECKED** · manuscript page 4

Coefficient selectors over finite residue classes, idempotence, orthogonality, exact reconstruction and divisor refinement. Formal power-series versions use actual coefficients. Labels range over standard residues; modulus is positive for reconstruction. No new analytic convergence assertion.

Principal targets: `KomorebiPaperIX.ResiduePackets.packet_reconstruction`, `KomorebiPaperIX.ResiduePackets.packet_refinement`, `KomorebiPaperIX.ResiduePackets.series_packet_reconstruction`, `KomorebiPaperIX.ResiduePackets.series_packet_refinement`.

## 2.1 — Unit EGF coordinate change

**Theorem · LEAN_CHECKED** · manuscript page 6

Actual exponential-series encode/decode over a characteristic-zero field. The inverse power series is constructed from constant coefficient one. Binomial convolution, inverse identities and conjugated packet laws are proved. The statement is formal/coefficientwise, not a separate analytic convergence theorem.

Principal targets: `KomorebiPaperIX.EGF.coordinateEquiv`, `KomorebiPaperIX.EGF.coordinate_forward`, `KomorebiPaperIX.EGF.coordinate_inverse`, `KomorebiPaperIX.EGF.transported_reconstruction`, `KomorebiPaperIX.EGF.transported_idempotent`, `KomorebiPaperIX.EGF.transported_orthogonal`, `KomorebiPaperIX.EGF.matrix_diagonal`, `KomorebiPaperIX.EGF.matrix_above_diagonal`.

## 2.2 — Filtered triangular reconstruction

**Theorem · LEAN_CHECKED** · manuscript page 7

Finite coefficient-row divisibility over an arbitrary commutative ring, specialized to actual p-adic integers. Weights are natural numbers or infinity, with infinity denoting a zero coefficient. This proves the omitted-tail assertion. Weight growth is not needed for an individual finite row; no infinite-limit convergence theorem is claimed.

Principal targets: `KomorebiPaperIX.Filtered.filtered_triangular_reconstruction`, `KomorebiPaperIX.Filtered.padic_filtered_reconstruction`.

## 3.2 — Triangular congruential inverse

**Theorem · LEAN_CHECKED** · manuscript page 7

Rational coefficients constructed by well-founded forward substitution, nonzero binomial diagonal proved, unique solution proved. The reciprocal-series identity and actual original exponential-section product are proved using power-series expansion. For the original source formula, N>0 and 0<=j<N are explicit.

Principal targets: `KomorebiPaperIX.Congruential.triangular_inverse`, `KomorebiPaperIX.Congruential.coefficient_recurrence`, `KomorebiPaperIX.Congruential.coefficient_unique`, `KomorebiPaperIX.Congruential.packet_is_actual_inverse`, `KomorebiPaperIX.ExponentialSection.original_section_inverse_identity`.

## 3.3 — Universal denominator clearing

**Proposition · LEAN_CHECKED** · manuscript page 8

The product of the binomial diagonal entries clears every constructed rational coefficient. The proof derives denominator divisibility through a general integer triangular system; it does not assume integral packet coefficients.

Principal targets: `KomorebiPaperIX.Congruential.clearing_product`, `KomorebiPaperIX.Congruential.universal_denominator_clearing`.

## 4.1 — Odd-power generating function

**Lemma · LEAN_CHECKED** · manuscript page 10

Actual rational formal exponential series and the literal integer alternating odd-power sum. Proves the full generating-function identity and its even-part identity for every odd positive length, including composite lengths and length one. Formal/coefficientwise scope, not a separate analytic convergence theorem.

Principal targets: `KomorebiPaperIX.OddPower.source_as_exponentials`, `KomorebiPaperIX.OddPower.odd_source_egf`, `KomorebiPaperIX.OddPower.odd_source_even_egf`, `KomorebiPaperIX.OddPower.evenPart_coeff`.

## 4.2 — Odd-prime Euler reconstruction

**Theorem · LEAN_CHECKED** · manuscript page 11

Constructs integral signed Euler coefficients from the same C_(2,0) triangular recurrence and proves their sech generating function. Inverse coefficients are an integer binomial convolution, with their signed odd-zigzag identity proved through actual formal sine/cosine and derivative of tan. Proves exact reconstruction in every even row for any odd length and the unit triangular row properties. No Euler reconstruction or zigzag coefficient expansion is assumed.

Principal targets: `KomorebiPaperIX.EulerCoefficients.euler_egf`, `KomorebiPaperIX.Zigzag.inverse_is_signed_zigzag`, `KomorebiPaperIX.OddEuler.odd_euler_reconstruction`, `KomorebiPaperIX.OddEuler.odd_euler_reconstruction_zigzag`, `KomorebiPaperIX.OddEuler.row_diagonal`, `KomorebiPaperIX.OddEuler.row_above_diagonal`, `KomorebiPaperIX.OddEuler.row_action`.

## 4.3 — Uniform odd-prime supercongruence ladder

**Corollary · LEAN_CHECKED** · manuscript page 11

Actual integer divisibility by p^(2M+2), derived from the proved reconstruction and integral inverse coefficients, with min(M,n/2) truncation. All even rows, all depths, and odd-prime specialization included. In fact valid for every odd positive integer length. Complete retention is exact. Example 4.4 is separately kernel-checked and proves the guaranteed modulus is attained; it does not imply a stronger uniform modulus.

Principal targets: `KomorebiPaperIX.OddEuler.odd_euler_supercongruence`, `KomorebiPaperIX.OddEuler.odd_prime_supercongruence`, `KomorebiPaperIX.OddEuler.full_depth_exact`, `KomorebiPaperIX.OddEulerExamples.manuscript_error_sharp`.

## 5.1 — Dyadic integrality of the inverse coefficients

**Lemma · LEAN_CHECKED** · manuscript page 14

Actual rational ordinary coefficients of the unit reciprocal kernel. Legendre factorial valuation bound proves integral kernel coefficients; strong induction proves the actual reciprocal has integral coefficients. The cleared formal-series identity B(z)sinh(z)^2=z^2 connects beta to the manuscript germ without inverting a zero-constant series. Actual Z_2 coefficient witnesses are constructed. The unnumbered Bernoulli closed formula is not independently formalized.

Principal targets: `KomorebiPaperIX.Dyadic.kernel_coefficient_integral`, `KomorebiPaperIX.Dyadic.beta_integral`, `KomorebiPaperIX.DyadicSeries.beta_original_generating_function`.

## 5.2 — Dyadic integrality of the source

**Lemma · LEAN_CHECKED** · manuscript page 14

The actual rational source R_(2n)=(3^(2n+2)-1)/(4(2n+1)(2n+2)). The pinned LTE theorem proves equal numerator and denominator 2-adic valuations. Source nonzeroness and valuation exactly zero are established; the coefficient embeds as a genuine unit of Z_2, for all n including zero.

Principal targets: `KomorebiPaperIX.Dyadic.source_valuation`, `KomorebiPaperIX.Dyadic.source_integral`, `KomorebiPaperIX.Dyadic.sourcePadic_isUnit`.

## 5.3 — Exact weighted dyadic Euler coordinate theorem

**Theorem · LEAN_CHECKED** · manuscript page 14

The independently defined dyadic source and actual reciprocal beta series multiply after rescaling by two to the previously identified Euler sech series. Exact coefficient extraction derives the complete finite rational row with actual descending factorials. Both degree 2n and arbitrary even-degree statements are checked. Rational equalities are transported to Z_2 using proved integrality, not assumed valuations. Formal series only; no additional analytic convergence claim.

Principal targets: `KomorebiPaperIX.DyadicSeries.source_shift_identity`, `KomorebiPaperIX.DyadicSeries.dyadic_reconstruction_series`, `KomorebiPaperIX.DyadicReconstruction.dyadic_reconstruction`, `KomorebiPaperIX.DyadicReconstruction.dyadic_reconstruction_even_degree`, `KomorebiPaperIX.DyadicReconstruction.falling_factorial_fraction`, `KomorebiPaperIX.DyadicReconstruction.dyadic_reconstruction_padic`.

## 5.4 — Weighted dyadic supercongruence

**Corollary · LEAN_CHECKED** · manuscript page 14

The actual min(M,n)-truncation has error divisible by 2^(2M+2) in Z_2 for every row and depth. A separate theorem proves that the rational normalized error belongs to the 2-adically integral subring of Q. Zero row and complete retention are included. This is not divisibility in the field Q_2 and does not use the finite valuation default at zero.

Principal targets: `KomorebiPaperIX.DyadicReconstruction.dyadic_supercongruence`, `KomorebiPaperIX.DyadicReconstruction.normalized_error_integral`, `KomorebiPaperIX.DyadicReconstruction.full_depth_exact`, `KomorebiPaperIX.DyadicReconstruction.full_depth_exact_padic`.

## 6.1 — Unit-group decomposition

**Classical Input · CLASSICAL_INPUT** · manuscript page 15

Not independently formalized in this release.

## 6.2 — Finite unit decomposition certificates

**Proposition · LEAN_CHECKED** · manuscript page 17

Actual units of ZMod(p^(L+1)), with explicit omega=a^(p^L) and principal=a/omega. The Euler totient exponent and finite-field Frobenius give the root and residue laws; ideal power lifting proves uniqueness. Root and principal coordinates are multiplicative and compatible under loss of precision; the principal factor has p-power order. This finite construction works for every prime; the odd-prime statement is its specialization. The separate dyadic branch at precision L+2 constructs the sign from reduction mod 4 and proves unique sign/principal reconstruction, including distinction mod 4 and invisibility mod 2. No infinite p-adic decomposition, analytic logarithm, or Hensel algorithm runtime is claimed.

Principal targets: `KomorebiPaperIX.FiniteUnits.finite_unit_decomposition`, `KomorebiPaperIX.FiniteUnits.omega_unique`, `KomorebiPaperIX.FiniteUnits.decomposition_unique`, `KomorebiPaperIX.DyadicUnits.dyadic_unit_decomposition`, `KomorebiPaperIX.DyadicUnits.decomposition_unique`, `KomorebiPaperIX.UnitRefinement.omega_compatible`, `KomorebiPaperIX.UnitRefinement.principal_compatible`.

## 7.1 — Mahler coordinate system

**Classical Input · CLASSICAL_INPUT** · manuscript page 17

Not independently formalized in this release.

## 7.2 — Finite Mahler reconstruction

**Theorem · LEAN_CHECKED** · manuscript page 17

Actual iterated forward differences and independently defined finite binomial interpolants over a commutative ring. Newton reconstruction and coefficient shifts reuse the pinned Mathlib ForwardDiff theorems. Uniqueness, truncation beyond the degree, and prefix/stencil dependence are proved. Finite data determine differences only when n+s<=N; arbitrary orders are identities for the interpolant or a full sequence. No infinite p-adic interpolation or convergence claim.

Principal targets: `KomorebiPaperIX.Mahler.finite_mahler_reconstruction`, `KomorebiPaperIX.Mahler.difference_from_coefficients`, `KomorebiPaperIX.Mahler.interpolant_reproduces`, `KomorebiPaperIX.Mahler.coefficient_interpolant`, `KomorebiPaperIX.Mahler.interpolant_difference`, `KomorebiPaperIX.Mahler.finite_sample_difference`, `KomorebiPaperIX.Mahler.interpolant_coefficients_unique`.

## 7.3 — Weighted difference bound

**Corollary · LEAN_CHECKED** · manuscript page 18

Actual Z_p-valued sequences, their derived Mahler coefficients, and natural evaluation arguments. The minimum runs over r=s,...,s+n, exactly the nonzero binomial support. Includes w(r) in Nat union infinity, the actual binomial p-adic valuation, all-zero/cancelled cases, and a separate ideal-divisibility equivalence. Extended order assigns infinity to zero; the library finite valuation default is not used at zero. The infinite Mahler convergence input remains separately tracked.

Principal targets: `KomorebiPaperIX.PadicBounds.nat_le_order_iff`, `KomorebiPaperIX.PadicBounds.weighted_difference_bound`, `KomorebiPaperIX.PadicBounds.weighted_difference_divisibility`, `KomorebiPaperIX.PadicBounds.coefficient_tail_bound`, `KomorebiPaperIX.PadicBounds.interpolant_weighted_bound`.

## 7.4 — Unit-mode valuation gain

**Theorem · LEAN_CHECKED** · manuscript page 18

Exact h-step power-sequence identity over commutative rings. For actual units of Z_p, Fermat divisibility is derived through the residue-field map and its kernel ideal, not assumed. All primes including 2 with h=p-1, all orders and starting indices, finite integral linear combinations, empty mode sets, zero differences and multiples of the Fermat step. Does not represent general congruential Euler packets as finite unit-mode sums or prove Theorem 7.5.

Principal targets: `KomorebiPaperIX.UnitModes.geometric_difference`, `KomorebiPaperIX.UnitModes.unit_fermat_divisibility`, `KomorebiPaperIX.UnitModes.unit_mode_valuation_gain`, `KomorebiPaperIX.UnitModes.finite_unit_modes_valuation_gain`, `KomorebiPaperIX.UnitModes.unit_multiple_step_divisibility`.

## 7.5 — Global odd-prime finite-difference theorem in packet normalization

**Theorem · LEAN_CHECKED** · manuscript page 19

All permitted residues 0<=j<m*p, every prime p, positive m dividing p-1, all natural rows, orders and step multipliers. The original rational unnormalized coefficients j! C_(mp,j) are proved p-integral and satisfy the saturated exponent min(k,m*n). The normalized bound loses exactly v_p(j!), with zero-safe valuation. Genuine divisibility in Z_p and its original-rational coefficient bridge are proved. Singular weightedness is transferred through actual exp/log substitution and normalized Theta-defect stability; the actual Riccati equation, finite-prefix Picard propagation, ratio induction and unnormalized telescoping supply the full family. No higher-difference, weightedness or flatness premise is assumed in the principal final theorem. The statement includes p=2,m=1 and zero step as valid specializations, not a claim about a broader external dyadic conjecture. No novelty or historical-priority theorem is claimed.

Principal targets: `KomorebiPaperIX.Theorem75.global_finite_difference`, `KomorebiPaperIX.AllResidueEuler.global_unnormalized_bound`, `KomorebiPaperIX.AllResidueEuler.global_normalized_precision`, `KomorebiPaperIX.AllResidueEuler.unnormalized_integral`, `KomorebiPaperIX.AllResidueEuler.unnormalizedLift_coe`.

## 8.1 — Lucas theorem

**Classical Input · CLASSICAL_INPUT** · manuscript page 19

Tracked separately. The Lucas input is reused from pinned Mathlib, not independently reconstructed in this release.

## 8.2 — Standard-window row reduction

**Theorem · LEAN_CHECKED** · manuscript page 19

Actual natural binomial coefficients modulo any prime, with 0<=j<p. All-row Lucas reduction and the diagonal p-unit conclusion are proved. Uses the pinned Mathlib Lucas theorem. Residue independence and uniform period are separately covered in 8.3 and 8.5.

Principal targets: `KomorebiPaperIX.StandardWindow.lucas_row_reduction`, `KomorebiPaperIX.StandardWindow.standard_diagonal_not_divisible`, `KomorebiPaperIX.StandardWindow.standard_diagonal_unit`.

## 8.3 — Residue independence in the standard window

**Corollary · LEAN_CHECKED** · manuscript page 20

Actual rational C_(m*p,j)(n) is lifted to Z_p by recursive ring forward substitution using proven unit pivots. Mapping to Q_p is proved to recover the original rational coefficient. The reduced F_p sequence is independently constructed from the Lucas-reduced triangular rows and proved unique. Applying the genuine Z_p residue hom proves independence of all standard-window addresses j<p and ideal congruence of any two lifts. Covers every row and prime; does not assume Theorem 7.5 or prove the uniform period. The nonintegral (p,m,j,n)=(3,2,3,1) case is separately excluded by a checked example.

Principal targets: `KomorebiPaperIX.WindowIndependence.coeffPadic_coe`, `KomorebiPaperIX.WindowIndependence.standard_window_integral`, `KomorebiPaperIX.WindowIndependence.reduced_row`, `KomorebiPaperIX.WindowIndependence.reduced_unique`, `KomorebiPaperIX.WindowIndependence.residue_independence`, `KomorebiPaperIX.WindowIndependence.two_window_addresses_congruent`.

## 8.5 — Uniform standard-window period

**Corollary · LEAN_CHECKED** · manuscript page 21

Independent finite-field proof using the actual binomial/Hurwitz coefficient convolution, constructed reciprocal, characteristic-p higher Leibniz rule, proved support on multiples of m, and identification with the independently defined Lucas-reduced inverse. All primes, m dividing p-1, n>=1, all nonnegative multiples of the period. Actual standard-window p-adic lift differences lie in p Z_p. Neither the global Euler estimate nor a period hypothesis is assumed. No least-period claim; n=0 and m not dividing p-1 have checked counterexamples.

Principal targets: `KomorebiPaperIX.WindowPeriod.uniform_standard_window_period`, `KomorebiPaperIX.WindowPeriod.multiple_period`, `KomorebiPaperIX.WindowPeriod.standard_window_period_divisibility`, `KomorebiPaperIX.HurwitzInverse.inverse_prime_difference`, `KomorebiPaperIX.WindowPeriod.inverse_on_support`.

## 9.1 — Companion jump theorem

**Theorem · LEAN_CHECKED** · manuscript page 22

Finite square matrices over an arbitrary commutative ring. Constructs the actual power orbit and arithmetic packet, proves the source-sequence and jump formulas, and derives the explicit order-at-most-d vector, coordinate and linear-observable recurrences from the actual characteristic polynomial of C^N using pinned Mathlib Cayley-Hamilton. Includes zero dimension, singular matrices, zero step and unrestricted natural offsets. Does not assert minimal recurrence order d. No eigenvalue or diagonalizability premise.

Principal targets: `KomorebiPaperIX.Companion.source_companion_jump`, `KomorebiPaperIX.Companion.companion_jump`, `KomorebiPaperIX.Companion.packet_charpoly_annihilation`, `KomorebiPaperIX.Companion.packet_charpoly_recurrence`, `KomorebiPaperIX.Companion.source_charpoly_recurrence`, `KomorebiPaperIX.Companion.packet_coordinate_recurrence`, `KomorebiPaperIX.Companion.packet_observable_recurrence`.

## 9.2 — Fibonacci packet recurrence

**Corollary · LEAN_CHECKED** · manuscript page 22

Actual Nat.fib values cast into integers, with the state (F_(n+1),F_n) proved to follow the explicit integer companion matrix. Lucas numbers are independently defined by 2,1 and their recurrence. Trace of C^N equals L_N and determinant equals (-1)^N are proved, then the general characteristic recurrence yields the full scalar/vector formula for all natural N,j,k, including N=0. Also proves parity specializations, uniqueness from the first two packet values, and the exact manuscript example. No Binet/eigenvalue or desired recurrence assumption.

Principal targets: `KomorebiPaperIX.FibonacciPackets.fibonacci_packet_recurrence`, `KomorebiPaperIX.FibonacciPackets.fibonacci_state_packet_recurrence`, `KomorebiPaperIX.FibonacciPackets.trace_power_is_lucas`, `KomorebiPaperIX.FibonacciPackets.det_power`, `KomorebiPaperIX.FibonacciPackets.packet_is_fibonacci`, `KomorebiPaperIX.FibonacciPackets.fibonacci_packet_unique`, `KomorebiPaperIX.RecurrenceExamples.manuscript_sequence`, `KomorebiPaperIX.RecurrenceExamples.manuscript_step_three`.

## 10.1 — Arithmetic CRT packet factorization

**Theorem · LEAN_CHECKED** · manuscript page 22

Actual Chinese remainder ring equivalence for ZMod(2^a*M) with M odd, including a=0 and M=1. The two residue conditions are proved equivalent to the combined condition. The coefficient-sequence selector and actual formal-series selector factor accordingly, with the canonical label r<2^a*M explicit. Does not identify local valuation weights or infer precision from the CRT bijection.

Principal targets: `KomorebiPaperIX.CRTPackets.address_bijective`, `KomorebiPaperIX.CRTPackets.address_components`, `KomorebiPaperIX.CRTPackets.packet_factorization`, `KomorebiPaperIX.CRTPackets.series_packet_factorization`.

## 13.1 — Sharp normalization boundary

**Proposition · LEAN_CHECKED** · manuscript page 25

Exact coefficients from the general recurrence, valid parameter tuple, actual nonzero rational 3-adic valuation, sharp factorial-loss equality and explicit negation of the universal one-step no-loss claim. Also proves the corresponding unnormalized difference has valuation one. The general corrected finite-difference bound is now separately proved in 7.5; the no-loss counterexample remains valid.

Principal targets: `KomorebiPaperIX.Normalization.normalized_difference`, `KomorebiPaperIX.Normalization.difference_valuation`, `KomorebiPaperIX.Normalization.factorial_loss_is_sharp`, `KomorebiPaperIX.Normalization.universal_no_loss_refuted`.

## 13.2 — Canonical arithmetic obstruction packet

**Conjecture · CONJECTURAL** · manuscript page 26

Unproved; outside the manuscript-proved register.

## 13.3 — Prime-independent arithmetic spine

**Conjecture · CONJECTURAL** · manuscript page 26

Unproved; outside the manuscript-proved register.
