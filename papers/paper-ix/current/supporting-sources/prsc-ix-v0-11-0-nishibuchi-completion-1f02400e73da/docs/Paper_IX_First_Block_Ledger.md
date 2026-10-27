# Paper IX first-block formal coverage ledger

**Author: Komorebi P.**

Release v0.1.0. Status-corrected manuscript, 28 pages, preserved unchanged.

**7 of 24 named manuscript-proved items are checked in the recorded scopes; 17 remain.** Three classical inputs and two conjectures are tracked separately.

Named theorem/lemma/corollary/proposition environments only. Examples and numerical certificates are excluded. Manuscript-to-Lean correspondence is a mathematical review, not an automated semantic-equivalence theorem.

## Recorded items

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

Lemma; manuscript page 10; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 4.2 — Odd-prime Euler reconstruction

Theorem; manuscript page 11; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 4.3 — Uniform odd-prime supercongruence ladder

Corollary; manuscript page 11; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 5.1 — Dyadic integrality of the inverse coefficients

Lemma; manuscript page 14; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 5.2 — Dyadic integrality of the source

Lemma; manuscript page 14; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 5.3 — Exact weighted dyadic Euler coordinate theorem

Theorem; manuscript page 14; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 5.4 — Weighted dyadic supercongruence

Corollary; manuscript page 14; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

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

Theorem; manuscript page 17; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 7.3 — Weighted difference bound

Corollary; manuscript page 18; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

### 7.4 — Unit-mode valuation gain

Theorem; manuscript page 18; **PENDING_LEAN**.

Manuscript proof claim not yet checked in this Paper IX Lean project.

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
