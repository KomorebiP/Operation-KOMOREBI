# Paper IX fourth-block formal coverage ledger

**Author: Komorebi P.**

Release **v0.4.0**. The 28-page status-corrected manuscript remains unchanged.

**17 of 24 named manuscript-proved items are checked in their recorded scopes; seven remain pending.** Three classical inputs and two conjectures remain separate.

This block covers items 7.2, 7.3 and 7.4. The cumulative project has **272 explicit theorem declarations and 60 explicit definitions across 21 modules**. The four new modules add 53 theorems and seven definitions, including supporting lemmas and examples. These are not counts of independent discoveries.

The finite-data qualification for 7.2 is explicit: a forward difference at n of order s requires data through n+s. The unrestricted formula applies to the full sequence or the constructed interpolant, not an unspecified continuation from a finite sample. The valuation in 7.3 and 7.4 is extended to infinity at zero. See `Paper_IX_Fourth_Block_Amendments.md`.

Manuscript-to-Lean correspondence is a mathematical review, not an automated semantic-equivalence theorem. Infinite Mahler expansion and the global Euler finite-difference theorem are not promoted by this block.

## Registered items

### 1.2 — Exact arithmetic packet reconstruction

Theorem; manuscript page 4; **LEAN_CHECKED**.

Coefficient selectors over finite residue classes, idempotence, orthogonality, exact reconstruction and divisor refinement. Formal power-series versions use actual coefficients. Labels range over standard residues; modulus is positive for reconstruction. No new analytic convergence assertion.

Principal targets: `KomorebiPaperIX.ResiduePackets.packet_reconstruction`, `KomorebiPaperIX.ResiduePackets.packet_refinement`, `KomorebiPaperIX.ResiduePackets.series_packet_reconstruction`, `KomorebiPaperIX.ResiduePackets.series_packet_refinement`.

### 2.1 — Unit EGF coordinate change

Theorem; manuscript page 6; **LEAN_CHECKED**.

Actual exponential-series encode/decode over a characteristic-zero field. The inverse power series is constructed from constant coefficient one. Binomial convolution, inverse identities and conjugated packet laws are proved. The statement is formal/coefficientwise, not a separate analytic convergence theorem.

Principal targets: `KomorebiPaperIX.EGF.coordinateEquiv`, `KomorebiPaperIX.EGF.coordinate_forward`, `KomorebiPaperIX.EGF.coordinate_inverse`, `KomorebiPaperIX.EGF.transported_reconstruction`, `KomorebiPaperIX.EGF.transported_idempotent`, `KomorebiPaperIX.EGF.transported_orthogonal`, `KomorebiPaperIX.EGF.matrix_diagonal`, `KomorebiPaperIX.EGF.matrix_above_diagonal`.

### 2.2 — Filtered triangular reconstruction

Theorem; manuscript page 7; **LEAN_CHECKED**.

Finite coefficient-row divisibility over an arbitrary commutative ring, specialized to actual p-adic integers. Weights are natural numbers or infinity, with infinity denoting a zero coefficient. This proves the omitted-tail assertion. Weight growth is not needed for an individual finite row; no infinite-limit convergence theorem is claimed.

Principal targets: `KomorebiPaperIX.Filtered.filtered_triangular_reconstruction`, `KomorebiPaperIX.Filtered.padic_filtered_reconstruction`.

### 3.2 — Triangular congruential inverse

Theorem; manuscript page 7; **LEAN_CHECKED**.

Rational coefficients constructed by well-founded forward substitution, nonzero binomial diagonal proved, unique solution proved. The reciprocal-series identity and actual original exponential-section product are proved using power-series expansion. For the original source formula, N>0 and 0<=j<N are explicit.

Principal targets: `KomorebiPaperIX.Congruential.triangular_inverse`, `KomorebiPaperIX.Congruential.coefficient_recurrence`, `KomorebiPaperIX.Congruential.coefficient_unique`, `KomorebiPaperIX.Congruential.packet_is_actual_inverse`, `KomorebiPaperIX.ExponentialSection.original_section_inverse_identity`.

### 3.3 — Universal denominator clearing

Proposition; manuscript page 8; **LEAN_CHECKED**.

The product of the binomial diagonal entries clears every constructed rational coefficient. The proof derives denominator divisibility through a general integer triangular system; it does not assume integral packet coefficients.

Principal targets: `KomorebiPaperIX.Congruential.clearing_product`, `KomorebiPaperIX.Congruential.universal_denominator_clearing`.

### 4.1 — Odd-power generating function

Lemma; manuscript page 10; **LEAN_CHECKED**.

Actual rational formal exponential series and the literal integer alternating odd-power sum. Proves the full generating-function identity and its even-part identity for every odd positive length, including composite lengths and length one. Formal/coefficientwise scope, not a separate analytic convergence theorem.

Principal targets: `KomorebiPaperIX.OddPower.source_as_exponentials`, `KomorebiPaperIX.OddPower.odd_source_egf`, `KomorebiPaperIX.OddPower.odd_source_even_egf`, `KomorebiPaperIX.OddPower.evenPart_coeff`.

### 4.2 — Odd-prime Euler reconstruction

Theorem; manuscript page 11; **LEAN_CHECKED**.

Constructs integral signed Euler coefficients from the same C_(2,0) triangular recurrence and proves their sech generating function. Inverse coefficients are an integer binomial convolution, with their signed odd-zigzag identity proved through actual formal sine/cosine and derivative of tan. Proves exact reconstruction in every even row for any odd length and the unit triangular row properties. No Euler reconstruction or zigzag coefficient expansion is assumed.

Principal targets: `KomorebiPaperIX.EulerCoefficients.euler_egf`, `KomorebiPaperIX.Zigzag.inverse_is_signed_zigzag`, `KomorebiPaperIX.OddEuler.odd_euler_reconstruction`, `KomorebiPaperIX.OddEuler.odd_euler_reconstruction_zigzag`, `KomorebiPaperIX.OddEuler.row_diagonal`, `KomorebiPaperIX.OddEuler.row_above_diagonal`, `KomorebiPaperIX.OddEuler.row_action`.

### 4.3 — Uniform odd-prime supercongruence ladder

Corollary; manuscript page 11; **LEAN_CHECKED**.

Actual integer divisibility by p^(2M+2), derived from the proved reconstruction and integral inverse coefficients, with min(M,n/2) truncation. All even rows, all depths, and odd-prime specialization included. In fact valid for every odd positive integer length. Complete retention is exact. Example 4.4 is separately kernel-checked and proves the guaranteed modulus is attained; it does not imply a stronger uniform modulus.

Principal targets: `KomorebiPaperIX.OddEuler.odd_euler_supercongruence`, `KomorebiPaperIX.OddEuler.odd_prime_supercongruence`, `KomorebiPaperIX.OddEuler.full_depth_exact`, `KomorebiPaperIX.OddEulerExamples.manuscript_error_sharp`.

### 5.1 — Dyadic integrality of the inverse coefficients

Lemma; manuscript page 14; **LEAN_CHECKED**.

Actual rational ordinary coefficients of the unit reciprocal kernel. Legendre factorial valuation bound proves integral kernel coefficients; strong induction proves the actual reciprocal has integral coefficients. The cleared formal-series identity B(z)sinh(z)^2=z^2 connects beta to the manuscript germ without inverting a zero-constant series. Actual Z_2 coefficient witnesses are constructed. The unnumbered Bernoulli closed formula is not independently formalized.

Principal targets: `KomorebiPaperIX.Dyadic.kernel_coefficient_integral`, `KomorebiPaperIX.Dyadic.beta_integral`, `KomorebiPaperIX.DyadicSeries.beta_original_generating_function`.

### 5.2 — Dyadic integrality of the source

Lemma; manuscript page 14; **LEAN_CHECKED**.

The actual rational source R_(2n)=(3^(2n+2)-1)/(4(2n+1)(2n+2)). The pinned LTE theorem proves equal numerator and denominator 2-adic valuations. Source nonzeroness and valuation exactly zero are established; the coefficient embeds as a genuine unit of Z_2, for all n including zero.

Principal targets: `KomorebiPaperIX.Dyadic.source_valuation`, `KomorebiPaperIX.Dyadic.source_integral`, `KomorebiPaperIX.Dyadic.sourcePadic_isUnit`.

### 5.3 — Exact weighted dyadic Euler coordinate theorem

Theorem; manuscript page 14; **LEAN_CHECKED**.

The independently defined dyadic source and actual reciprocal beta series multiply after rescaling by two to the previously identified Euler sech series. Exact coefficient extraction derives the complete finite rational row with actual descending factorials. Both degree 2n and arbitrary even-degree statements are checked. Rational equalities are transported to Z_2 using proved integrality, not assumed valuations. Formal series only; no additional analytic convergence claim.

Principal targets: `KomorebiPaperIX.DyadicSeries.source_shift_identity`, `KomorebiPaperIX.DyadicSeries.dyadic_reconstruction_series`, `KomorebiPaperIX.DyadicReconstruction.dyadic_reconstruction`, `KomorebiPaperIX.DyadicReconstruction.dyadic_reconstruction_even_degree`, `KomorebiPaperIX.DyadicReconstruction.falling_factorial_fraction`, `KomorebiPaperIX.DyadicReconstruction.dyadic_reconstruction_padic`.

### 5.4 — Weighted dyadic supercongruence

Corollary; manuscript page 14; **LEAN_CHECKED**.

The actual min(M,n)-truncation has error divisible by 2^(2M+2) in Z_2 for every row and depth. A separate theorem proves that the rational normalized error belongs to the 2-adically integral subring of Q. Zero row and complete retention are included. This is not divisibility in the field Q_2 and does not use the finite valuation default at zero.

Principal targets: `KomorebiPaperIX.DyadicReconstruction.dyadic_supercongruence`, `KomorebiPaperIX.DyadicReconstruction.normalized_error_integral`, `KomorebiPaperIX.DyadicReconstruction.full_depth_exact`, `KomorebiPaperIX.DyadicReconstruction.full_depth_exact_padic`.

### 6.1 — Unit-group decomposition

Classical Input; manuscript page 15; **CLASSICAL_INPUT**.

Not independently formalized in this release.

### 6.2 — Finite unit decomposition certificates

Proposition; manuscript page 17; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 7.1 — Mahler coordinate system

Classical Input; manuscript page 17; **CLASSICAL_INPUT**.

Not independently formalized in this release.

### 7.2 — Finite Mahler reconstruction

Theorem; manuscript page 17; **LEAN_CHECKED**.

Actual iterated forward differences and independently defined finite binomial interpolants over a commutative ring. Newton reconstruction and coefficient shifts reuse the pinned Mathlib ForwardDiff theorems. Uniqueness, truncation beyond the degree, and prefix/stencil dependence are proved. Finite data determine differences only when n+s<=N; arbitrary orders are identities for the interpolant or a full sequence. No infinite p-adic interpolation or convergence claim.

Principal targets: `KomorebiPaperIX.Mahler.finite_mahler_reconstruction`, `KomorebiPaperIX.Mahler.difference_from_coefficients`, `KomorebiPaperIX.Mahler.interpolant_reproduces`, `KomorebiPaperIX.Mahler.coefficient_interpolant`, `KomorebiPaperIX.Mahler.interpolant_difference`, `KomorebiPaperIX.Mahler.finite_sample_difference`, `KomorebiPaperIX.Mahler.interpolant_coefficients_unique`.

### 7.3 — Weighted difference bound

Corollary; manuscript page 18; **LEAN_CHECKED**.

Actual Z_p-valued sequences, their derived Mahler coefficients, and natural evaluation arguments. The minimum runs over r=s,...,s+n, exactly the nonzero binomial support. Includes w(r) in Nat union infinity, the actual binomial p-adic valuation, all-zero/cancelled cases, and a separate ideal-divisibility equivalence. Extended order assigns infinity to zero; the library finite valuation default is not used at zero. The infinite Mahler convergence input remains separately tracked.

Principal targets: `KomorebiPaperIX.PadicBounds.nat_le_order_iff`, `KomorebiPaperIX.PadicBounds.weighted_difference_bound`, `KomorebiPaperIX.PadicBounds.weighted_difference_divisibility`, `KomorebiPaperIX.PadicBounds.coefficient_tail_bound`, `KomorebiPaperIX.PadicBounds.interpolant_weighted_bound`.

### 7.4 — Unit-mode valuation gain

Theorem; manuscript page 18; **LEAN_CHECKED**.

Exact h-step power-sequence identity over commutative rings. For actual units of Z_p, Fermat divisibility is derived through the residue-field map and its kernel ideal, not assumed. All primes including 2 with h=p-1, all orders and starting indices, finite integral linear combinations, empty mode sets, zero differences and multiples of the Fermat step. Does not represent general congruential Euler packets as finite unit-mode sums or prove Theorem 7.5.

Principal targets: `KomorebiPaperIX.UnitModes.geometric_difference`, `KomorebiPaperIX.UnitModes.unit_fermat_divisibility`, `KomorebiPaperIX.UnitModes.unit_mode_valuation_gain`, `KomorebiPaperIX.UnitModes.finite_unit_modes_valuation_gain`, `KomorebiPaperIX.UnitModes.unit_multiple_step_divisibility`.

### 7.5 — Global odd-prime finite-difference theorem in packet normalization

Theorem; manuscript page 19; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 8.1 — Lucas theorem

Classical Input; manuscript page 19; **CLASSICAL_INPUT**.

Tracked separately. The Lucas input is reused from pinned Mathlib, not independently reconstructed in this release.

### 8.2 — Standard-window row reduction

Theorem; manuscript page 19; **LEAN_CHECKED**.

Actual natural binomial coefficients modulo any prime, with 0<=j<p. All-row Lucas reduction and the diagonal p-unit conclusion are proved. Uses the pinned Mathlib Lucas theorem. Residue-independence and uniform period are not yet formalized.

Principal targets: `KomorebiPaperIX.StandardWindow.lucas_row_reduction`, `KomorebiPaperIX.StandardWindow.standard_diagonal_not_divisible`, `KomorebiPaperIX.StandardWindow.standard_diagonal_unit`.

### 8.3 — Residue independence in the standard window

Corollary; manuscript page 20; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 8.5 — Uniform standard-window period

Corollary; manuscript page 21; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 9.1 — Companion jump theorem

Theorem; manuscript page 22; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 9.2 — Fibonacci packet recurrence

Corollary; manuscript page 22; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 10.1 — Arithmetic CRT packet factorization

Theorem; manuscript page 22; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 13.1 — Sharp normalization boundary

Proposition; manuscript page 25; **LEAN_CHECKED**.

Exact coefficients from the general recurrence, valid parameter tuple, actual nonzero rational 3-adic valuation, sharp factorial-loss equality and explicit negation of the universal one-step no-loss claim. Also proves the corresponding unnormalized difference has valuation one. The general corrected finite-difference bound remains pending.

Principal targets: `KomorebiPaperIX.Normalization.normalized_difference`, `KomorebiPaperIX.Normalization.difference_valuation`, `KomorebiPaperIX.Normalization.factorial_loss_is_sharp`, `KomorebiPaperIX.Normalization.universal_no_loss_refuted`.

### 13.2 — Canonical arithmetic obstruction packet

Conjecture; manuscript page 26; **CONJECTURAL**.

Unproved; outside the manuscript-proved register.

### 13.3 — Prime-independent arithmetic spine

Conjecture; manuscript page 26; **CONJECTURAL**.

Unproved; outside the manuscript-proved register.

