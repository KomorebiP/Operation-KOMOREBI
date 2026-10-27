/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Algebra.Order.Floor.Div
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.List.OfFn

/-!
# Paper II: weighted transfer and finite-precision inversion

Author: Komorebi P.

This module isolates the algebraic content of weighted transfer inversion.  It proves a finite
noncommutative geometric-inverse identity, transports that identity through quotient maps, expands
powers as finite sums of ordered words, and packages multiplicative-filtration certificates which
justify pruning every word whose cumulative weight reaches the requested precision.

Positive edge weights turn a precision cutoff into an explicit nilpotence certificate in the
quotient, so the resulting inverse is a finite sum.  A separate analytic specialization proves the
usual infinite geometric formula in a complete normed ring under the explicit hypothesis
`‖Dinv * K‖ < 1`.

There is deliberately no theorem asserting unrestricted adic convergence: filtered results below
are exact statements at a fixed finite precision, while the sole convergent infinite series uses a
norm strictly smaller than one.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.WeightedTransfer

open scoped BigOperators

universe u v w

/-! ## Finite noncommutative geometric inversion -/

/-- `y` is simultaneously a left and right inverse of `x`.

Keeping both equations in the certificate is important in the noncommutative setting.
-/
structure TwoSidedInverse {R : Type u} [Mul R] [One R] (x y : R) : Prop where
  left_inv : y * x = 1
  right_inv : x * y = 1

namespace TwoSidedInverse

/-- A ring homomorphism transports a two-sided inverse certificate. -/
theorem map {R : Type u} {S : Type v} [Semiring R] [Semiring S]
    {x y : R} (h : TwoSidedInverse x y) (q : R →+* S) :
    TwoSidedInverse (q x) (q y) := by
  constructor
  · simpa only [map_mul, map_one] using congrArg q h.left_inv
  · simpa only [map_mul, map_one] using congrArg q h.right_inv

end TwoSidedInverse

/-- The finite geometric candidate for the inverse of `1 + a`.

No commutativity is assumed: this is the ordered sum `1 - a + a² - ⋯` through degree `N - 1`.
-/
def finiteGeometricInverse {R : Type u} [Ring R] (a : R) (N : ℕ) : R :=
  ∑ n ∈ Finset.range N, (-a) ^ n

/-- If `a ^ N = 0`, the finite geometric candidate is a genuine two-sided inverse of `1 + a`. -/
theorem finiteGeometricInverse_spec_of_pow_eq_zero {R : Type u} [Ring R]
    (a : R) (N : ℕ) (hN : a ^ N = 0) :
    TwoSidedInverse (1 + a) (finiteGeometricInverse a N) := by
  have hneg : (-a) ^ N = 0 := by
    rw [neg_pow, hN, mul_zero]
  constructor
  · simpa [finiteGeometricInverse, hneg] using geom_sum_mul_neg (-a) N
  · simpa [finiteGeometricInverse, hneg] using mul_neg_geom_sum (-a) N

/-- Data certifying a concrete nilpotence cutoff for `a`. -/
structure NilpotenceCertificate {R : Type u} [Ring R] (a : R) where
  cutoff : ℕ
  pow_eq_zero : a ^ cutoff = 0

/-- The finite inverse selected by a nilpotence certificate. -/
def inverseFromCertificate {R : Type u} [Ring R] (a : R)
    (certificate : NilpotenceCertificate a) : R :=
  finiteGeometricInverse a certificate.cutoff

/-- A nilpotence certificate produces a verified two-sided inverse. -/
theorem inverseFromCertificate_spec {R : Type u} [Ring R] (a : R)
    (certificate : NilpotenceCertificate a) :
    TwoSidedInverse (1 + a) (inverseFromCertificate a certificate) := by
  exact finiteGeometricInverse_spec_of_pow_eq_zero
    a certificate.cutoff certificate.pow_eq_zero

/-- Multiplying a perturbation inverse by `Dinv` gives an inverse of `D + K`. -/
private theorem diagonal_inverse_of_perturbation_inverse {R : Type u} [Ring R]
    (D Dinv K S : R) (hD : TwoSidedInverse D Dinv)
    (hS : TwoSidedInverse (1 + Dinv * K) S) :
    TwoSidedInverse (D + K) (S * Dinv) := by
  constructor
  · calc
      (S * Dinv) * (D + K) = S * (Dinv * D + Dinv * K) := by
        simp only [mul_add, mul_assoc]
      _ = S * (1 + Dinv * K) := by rw [hD.left_inv]
      _ = 1 := hS.left_inv
  · have hfactor : D + K = D * (1 + Dinv * K) := by
      symm
      rw [mul_add, mul_one, ← mul_assoc, hD.right_inv, one_mul]
    rw [hfactor]
    calc
      (D * (1 + Dinv * K)) * (S * Dinv) =
          D * (((1 + Dinv * K) * S) * Dinv) := by
            simp only [mul_assoc]
      _ = D * (1 * Dinv) := by rw [hS.right_inv]
      _ = 1 := by simpa only [one_mul] using hD.right_inv

/-- The exact finite candidate for `(D + K)⁻¹` when `Dinv * K` is nilpotent. -/
def diagonalTransferInverse {R : Type u} [Ring R]
    (Dinv K : R) (N : ℕ) : R :=
  finiteGeometricInverse (Dinv * K) N * Dinv

/-- Exact `D + K` inversion in a possibly noncommutative ring, under an explicit nilpotence
certificate for `Dinv * K`. -/
theorem diagonalTransferInverse_spec {R : Type u} [Ring R]
    (D Dinv K : R) (N : ℕ) (hD : TwoSidedInverse D Dinv)
    (hNil : (Dinv * K) ^ N = 0) :
    TwoSidedInverse (D + K) (diagonalTransferInverse Dinv K N) := by
  apply diagonal_inverse_of_perturbation_inverse D Dinv K
  · exact hD
  · exact finiteGeometricInverse_spec_of_pow_eq_zero (Dinv * K) N hNil

/-! ## Exact inversion after passage to finite precision -/

/-- If a ring homomorphism kills `a ^ L`, the mapped finite geometric sum is an exact inverse of
the mapped `1 + a`.  A quotient map is the primary application, but injectivity or surjectivity is
not needed. -/
theorem finitePrecisionInverse {R : Type u} {S : Type v} [Ring R] [Ring S]
    (q : R →+* S) (a : R) (L : ℕ) (hPrecision : q (a ^ L) = 0) :
    TwoSidedInverse (q (1 + a)) (q (finiteGeometricInverse a L)) := by
  have hpow : (q a) ^ L = 0 := by
    simpa only [map_pow] using hPrecision
  have hmap : q (finiteGeometricInverse a L) = finiteGeometricInverse (q a) L := by
    simp [finiteGeometricInverse]
  simpa only [map_add, map_one, hmap] using
    (finiteGeometricInverse_spec_of_pow_eq_zero (q a) L hpow)

/-! ## Analytic specialization -/

/-- The analytic geometric inverse.  Its specification below requires `‖a‖ < 1`. -/
noncomputable def analyticGeometricInverse {R : Type u} [NormedRing R]
    (a : R) : R :=
  ∑' n : ℕ, (-a) ^ n

/-- In a complete normed ring, the geometric series is a two-sided inverse when `‖a‖ < 1`. -/
theorem analyticGeometricInverse_spec {R : Type u} [NormedRing R] [CompleteSpace R]
    (a : R) (ha : ‖a‖ < 1) :
    TwoSidedInverse (1 + a) (analyticGeometricInverse a) := by
  have hneg : ‖-a‖ < 1 := by simpa only [norm_neg] using ha
  have hs : Summable (fun n : ℕ ↦ (-a) ^ n) :=
    summable_geometric_of_norm_lt_one hneg
  constructor
  · simpa [analyticGeometricInverse] using hs.tsum_pow_mul_one_sub
  · simpa [analyticGeometricInverse] using hs.one_sub_mul_tsum_pow

/-- The norm-convergent diagonal-plus-transfer candidate. -/
noncomputable def analyticDiagonalTransferInverse {R : Type u} [NormedRing R]
    (Dinv K : R) : R :=
  analyticGeometricInverse (Dinv * K) * Dinv

/-- Analytic `D + K` inversion under the explicit Neumann-series condition
`‖Dinv * K‖ < 1`. -/
theorem analyticDiagonalTransferInverse_spec {R : Type u}
    [NormedRing R] [CompleteSpace R] (D Dinv K : R)
    (hD : TwoSidedInverse D Dinv) (hNorm : ‖Dinv * K‖ < 1) :
    TwoSidedInverse (D + K) (analyticDiagonalTransferInverse Dinv K) := by
  apply diagonal_inverse_of_perturbation_inverse D Dinv K
  · exact hD
  · exact analyticGeometricInverse_spec (Dinv * K) hNorm

/-! ## Finite ordered-word expansion -/

/-- Cumulative weight of an ordered transfer word. -/
def wordWeight {E : Type u} (weight : E → ℕ) (word : List E) : ℕ :=
  (word.map weight).sum

/-- Ordered, hence generally noncommutative, product attached to a transfer word. -/
def wordProduct {E : Type u} {R : Type v} [Monoid R]
    (edge : E → R) (word : List E) : R :=
  (word.map edge).prod

@[simp] theorem wordWeight_nil {E : Type u} (weight : E → ℕ) :
    wordWeight weight [] = 0 := rfl

@[simp] theorem wordWeight_cons {E : Type u} (weight : E → ℕ)
    (e : E) (word : List E) :
    wordWeight weight (e :: word) = weight e + wordWeight weight word := rfl

@[simp] theorem wordProduct_nil {E : Type u} {R : Type v} [Monoid R]
    (edge : E → R) :
    wordProduct edge [] = 1 := rfl

@[simp] theorem wordProduct_cons {E : Type u} {R : Type v} [Monoid R]
    (edge : E → R) (e : E) (word : List E) :
    wordProduct edge (e :: word) = edge e * wordProduct edge word := rfl

/-- The `n`th power of a finite sum is the sum of the ordered products indexed by all length-`n`
words.  The order recorded by `List.ofFn` is retained, so no commutativity hypothesis appears. -/
theorem sum_fixedWordProduct_eq_pow {E : Type u} {R : Type v}
    [Fintype E] [Ring R] (edge : E → R) (n : ℕ) :
    (∑ word : Fin n → E, wordProduct edge (List.ofFn word)) =
      (∑ e : E, edge e) ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
      let split : E × (Fin n → E) ≃ (Fin (n + 1) → E) :=
        Fin.consEquiv (fun _ : Fin (n + 1) ↦ E)
      calc
        (∑ word : Fin (n + 1) → E, wordProduct edge (List.ofFn word)) =
            ∑ pair : E × (Fin n → E),
              wordProduct edge (List.ofFn (split pair)) := by
                simpa only using (split.sum_comp
                  (fun word : Fin (n + 1) → E ↦ wordProduct edge (List.ofFn word))).symm
        _ = ∑ pair : E × (Fin n → E),
              edge pair.1 * wordProduct edge (List.ofFn pair.2) := by
                apply Finset.sum_congr rfl
                intro pair _
                simp [split, wordProduct]
        _ = (∑ e : E, edge e) *
              (∑ word : Fin n → E, wordProduct edge (List.ofFn word)) := by
                rw [Fintype.sum_prod_type]
                rw [Finset.sum_mul]
                simp only [Finset.mul_sum]
        _ = (∑ e : E, edge e) ^ (n + 1) := by
                rw [ih, pow_succ']

/-! ## Multiplicative filtrations and precision certificates -/

/-- A decreasing additive filtration whose levels multiply by adding indices.

The structure records exactly the closure properties needed for finite-precision transfer words.
It makes no completeness or convergence claim.
-/
structure MultiplicativeFiltration (R : Type u) [Ring R] where
  Mem : ℕ → R → Prop
  zero_mem : ∀ n, Mem n 0
  add_mem : ∀ {n x y}, Mem n x → Mem n y → Mem n (x + y)
  neg_mem : ∀ {n x}, Mem n x → Mem n (-x)
  one_mem : Mem 0 1
  antitone : ∀ {m n x}, m ≤ n → Mem n x → Mem m x
  mul_mem : ∀ {m n x y}, Mem m x → Mem n y → Mem (m + n) (x * y)

namespace MultiplicativeFiltration

variable {R : Type u} [Ring R]

/-- Membership notation-friendly wrapper. -/
def Contains (filtration : MultiplicativeFiltration R) (n : ℕ) (x : R) : Prop :=
  filtration.Mem n x

/-- Products of filtered edge terms lie at the cumulative word weight. -/
theorem wordProduct_mem (filtration : MultiplicativeFiltration R)
    {E : Type v} (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) (word : List E) :
    filtration.Mem (wordWeight weight word) (wordProduct edge word) := by
  induction word with
  | nil => exact filtration.one_mem
  | cons e word ih =>
      exact filtration.mul_mem (hedge e) ih

end MultiplicativeFiltration

/-- A map realizes precision `L` when it kills every element in filtration level `L`. -/
structure PrecisionCertificate {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R) (q : R →+* S) (L : ℕ) : Prop where
  map_eq_zero : ∀ {x : R}, filtration.Mem L x → q x = 0

/-- A transfer word whose cumulative weight reaches `L` vanishes in every realization carrying a
precision-`L` certificate. -/
theorem wordProduct_vanishes_at_precision {R : Type u} {S : Type v}
    [Ring R] [Ring S] (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e))
    (word : List E) (hweight : L ≤ wordWeight weight word) :
    q (wordProduct edge word) = 0 := by
  apply certificate.map_eq_zero
  apply filtration.antitone hweight
  exact filtration.wordProduct_mem weight edge hedge word

/-- Mapping a finite word expansion is unchanged when all words of cumulative weight at least `L`
are pruned. -/
theorem map_eq_pruned_of_wordExpansion {R : Type u} {S : Type v}
    [Ring R] [Ring S] (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [DecidableEq E] (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e))
    (words : Finset (List E)) (x : R)
    (hexpansion : x = ∑ word ∈ words, wordProduct edge word) :
    q x = ∑ word ∈ words.filter (fun word ↦ wordWeight weight word < L),
      q (wordProduct edge word) := by
  rw [hexpansion, map_sum]
  classical
  rw [Finset.sum_filter]
  apply Finset.sum_congr rfl
  intro word hword
  by_cases hlow : wordWeight weight word < L
  · simp [hlow]
  · simp only [hlow, ↓reduceIte]
    exact wordProduct_vanishes_at_precision
      filtration q L certificate weight edge hedge word (Nat.le_of_not_gt hlow)

/-! ## Explicit pruned word inverses -/

/-- The length-`n` part of the word expansion after retaining exactly the words whose cumulative
weight is strictly below precision `L`. -/
def retainedFixedWordSum {E : Type u} {R : Type v} [Fintype E] [Ring R]
    (weight : E → ℕ) (edge : E → R) (L n : ℕ) : R :=
  ∑ word : Fin n → E with wordWeight weight (List.ofFn word) < L,
    wordProduct edge (List.ofFn word)

/-- The explicit signed, weight-pruned word candidate through word length `N - 1`.

Unlike `finiteGeometricInverse`, this expression visibly contains only retained transfer words:
every summand has cumulative weight strictly below `L`.  The independent length cutoff `N` permits
the sharper cutoff obtained from a lower bound on all edge weights. -/
def prunedWordInverse {E : Type u} {R : Type v} [Fintype E] [Ring R]
    (weight : E → ℕ) (edge : E → R) (L N : ℕ) : R :=
  ∑ n ∈ Finset.range N, (-1 : R) ^ n * retainedFixedWordSum weight edge L n

/-- At precision `L`, the full length-`n` word expansion maps to its explicitly retained part. -/
theorem map_pow_eq_retainedFixedWordSum {R : Type u} {S : Type v}
    [Ring R] [Ring S] (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) (n : ℕ) :
    q ((∑ e : E, edge e) ^ n) = q (retainedFixedWordSum weight edge L n) := by
  rw [← sum_fixedWordProduct_eq_pow edge n]
  simp only [retainedFixedWordSum, map_sum]
  classical
  rw [Finset.sum_filter]
  apply Finset.sum_congr rfl
  intro word _
  by_cases hlow : wordWeight weight (List.ofFn word) < L
  · simp [hlow]
  · simp only [hlow, ↓reduceIte]
    exact wordProduct_vanishes_at_precision filtration q L certificate weight edge hedge
      (List.ofFn word) (Nat.le_of_not_gt hlow)

/-- The mapped finite geometric inverse is exactly the mapped explicit pruned-word expression.

This is the direct bridge missing from the abstract pruning statement: it derives the expansion
from the finite edge sum, keeps the noncommutative word order, inserts the alternating geometric
sign, and removes every word of weight at least `L`. -/
theorem map_finiteGeometricInverse_eq_prunedWordInverse
    {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L N : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    q (finiteGeometricInverse (∑ e : E, edge e) N) =
      q (prunedWordInverse weight edge L N) := by
  simp only [finiteGeometricInverse, prunedWordInverse, map_sum, map_mul, map_pow, map_neg,
    map_one]
  apply Finset.sum_congr rfl
  intro n _
  rw [neg_pow]
  congr 1
  simpa only [map_pow, map_sum] using
    (map_pow_eq_retainedFixedWordSum filtration q L certificate weight edge hedge n)

/-- If the normalized transfer is nilpotent after mapping, the explicit pruned word sum is a
two-sided inverse.  The precision cutoff `L` and nilpotence/length cutoff `N` are independent. -/
theorem prunedWordInverse_spec_of_pow_eq_zero
    {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L N : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e))
    (hNil : q ((∑ e : E, edge e) ^ N) = 0) :
    TwoSidedInverse
      (q (1 + ∑ e : E, edge e))
      (q (prunedWordInverse weight edge L N)) := by
  have hfull := finitePrecisionInverse q (∑ e : E, edge e) N hNil
  rw [← map_finiteGeometricInverse_eq_prunedWordInverse
    filtration q L N certificate weight edge hedge]
  exact hfull

/-- When each edge has positive weight, word length is bounded by cumulative weight. -/
theorem length_le_wordWeight {E : Type u} (weight : E → ℕ)
    (hpositive : ∀ e, 1 ≤ weight e) (word : List E) :
    word.length ≤ wordWeight weight word := by
  induction word with
  | nil => simp
  | cons e word ih =>
      rw [List.length_cons, wordWeight_cons]
      calc
        word.length + 1 = 1 + word.length := Nat.add_comm _ _
        _ ≤ weight e + wordWeight weight word := Nat.add_le_add (hpositive e) ih

/-- A uniform lower bound `m` on edge weights gives the sharper estimate
`m * word.length ≤ wordWeight weight word`. -/
theorem minWeight_mul_length_le_wordWeight {E : Type u} (weight : E → ℕ) (m : ℕ)
    (hmin : ∀ e, m ≤ weight e) (word : List E) :
    m * word.length ≤ wordWeight weight word := by
  induction word with
  | nil => simp
  | cons e word ih =>
      rw [List.length_cons, wordWeight_cons, Nat.mul_succ, Nat.add_comm (m * word.length) m]
      exact Nat.add_le_add (hmin e) ih

/-- Positive edge weights force the `L`th power of their sum to vanish in a precision-`L`
realization.  The proof uses the full noncommutative word expansion. -/
theorem map_sum_pow_eq_zero_at_cutoff {R : Type u} {S : Type v}
    [Ring R] [Ring S] (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    q ((∑ e : E, edge e) ^ L) = 0 := by
  rw [← sum_fixedWordProduct_eq_pow edge L, map_sum]
  apply Finset.sum_eq_zero
  intro word _
  apply wordProduct_vanishes_at_precision
    filtration q L certificate weight edge hedge (List.ofFn word)
  simpa only [List.length_ofFn] using
    length_le_wordWeight weight hpositive (List.ofFn word)

/-- A minimum edge weight `m` permits any nilpotence cutoff `N` satisfying `L ≤ m * N`.

For `m > 1`, this can be strictly smaller than the coarse length cutoff `N = L`. -/
theorem map_sum_pow_eq_zero_at_scaled_cutoff {R : Type u} {S : Type v}
    [Ring R] [Ring S] (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L m N : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hmin : ∀ e, m ≤ weight e) (hcutoff : L ≤ m * N)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    q ((∑ e : E, edge e) ^ N) = 0 := by
  rw [← sum_fixedWordProduct_eq_pow edge N, map_sum]
  apply Finset.sum_eq_zero
  intro word _
  apply wordProduct_vanishes_at_precision
    filtration q L certificate weight edge hedge (List.ofFn word)
  calc
    L ≤ m * N := hcutoff
    _ = m * (List.ofFn word).length := by simp only [List.length_ofFn]
    _ ≤ wordWeight weight (List.ofFn word) :=
      minWeight_mul_length_le_wordWeight weight m hmin (List.ofFn word)

/-- The executable ceiling cutoff used in the manuscript satisfies the
scaled cutoff inequality.  Positivity of `m` is essential: ceiling division
by zero is not a valid minimum-weight cutoff. -/
theorem le_mul_ceilDiv (L m : ℕ) (hm : 0 < m) :
    L ≤ m * (L ⌈/⌉ m) := by
  exact (ceilDiv_le_iff_le_mul hm).mp le_rfl

/-- The explicit pruned word expression is a two-sided finite-precision inverse at any scaled
cutoff `N` satisfying `L ≤ m * N`. -/
theorem prunedWordInverse_spec_of_minWeight
    {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L m N : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hmin : ∀ e, m ≤ weight e) (hcutoff : L ≤ m * N)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    TwoSidedInverse
      (q (1 + ∑ e : E, edge e))
      (q (prunedWordInverse weight edge L N)) := by
  apply prunedWordInverse_spec_of_pow_eq_zero
    filtration q L N certificate weight edge hedge
  exact map_sum_pow_eq_zero_at_scaled_cutoff
    filtration q L m N certificate weight edge hmin hcutoff hedge

/-- The common positive-weight specialization uses the coarse but assumption-free cutoff `N=L`. -/
theorem finitePrecisionPrunedInverse_of_weightedEdges
    {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    TwoSidedInverse
      (q (1 + ∑ e : E, edge e))
      (q (prunedWordInverse weight edge L L)) := by
  exact prunedWordInverse_spec_of_minWeight
    filtration q L 1 L certificate weight edge hpositive (by simp) hedge

/-- Weighted finite-precision inversion: positive filtered edge weights provide the nilpotence
cutoff needed by the finite geometric inverse. -/
theorem finitePrecisionInverse_of_weightedEdges {R : Type u} {S : Type v}
    [Ring R] [Ring S] (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    TwoSidedInverse
      (q (1 + ∑ e : E, edge e))
      (q (finiteGeometricInverse (∑ e : E, edge e) L)) := by
  apply finitePrecisionInverse q (∑ e : E, edge e) L
  exact map_sum_pow_eq_zero_at_cutoff
    filtration q L certificate weight edge hpositive hedge

/--
Full mapped diagonal-plus-transfer inversion from positive filtered edge data.

The equality `Dinv * K = ∑ e, edge e` identifies the normalized transfer with
the supplied weighted edge expansion.  Its `L`th power vanishes after `q`, the
inverse certificate for `D` maps to the target ring, and the diagonal
factorization then gives the displayed two-sided inverse of `q (D + K)`.
-/
theorem finitePrecisionDiagonalTransferInverse_of_weightedEdges
    {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    (D Dinv K : R) (hD : TwoSidedInverse D Dinv)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (htransfer : Dinv * K = ∑ e : E, edge e)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    TwoSidedInverse
      (q (D + K))
      (q (finiteGeometricInverse (Dinv * K) L * Dinv)) := by
  have hprecision : q ((Dinv * K) ^ L) = 0 := by
    rw [htransfer]
    exact map_sum_pow_eq_zero_at_cutoff
      filtration q L certificate weight edge hpositive hedge
  have hnil : (q Dinv * q K) ^ L = 0 := by
    simpa only [map_pow, map_mul] using hprecision
  have hmappedD : TwoSidedInverse (q D) (q Dinv) := hD.map q
  have hdiagonal :=
    diagonalTransferInverse_spec (q D) (q Dinv) (q K) L hmappedD hnil
  have hgeometric :
      q (finiteGeometricInverse (Dinv * K) L) =
        finiteGeometricInverse (q Dinv * q K) L := by
    simp [finiteGeometricInverse]
  simpa only [diagonalTransferInverse, map_add, map_mul, hgeometric] using hdiagonal

/-- The explicit weight-pruned diagonal-plus-transfer inverse candidate. -/
def prunedDiagonalTransferInverse {E : Type u} {R : Type v} [Fintype E] [Ring R]
    (weight : E → ℕ) (edge : E → R) (Dinv : R) (L N : ℕ) : R :=
  prunedWordInverse weight edge L N * Dinv

/-- Full mapped diagonal-plus-transfer inversion with an explicit pruned word inverse and the
scaled cutoff supplied by a minimum edge weight. -/
theorem finitePrecisionPrunedDiagonalTransferInverse_of_minWeight
    {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L m N : ℕ) (certificate : PrecisionCertificate filtration q L)
    (D Dinv K : R) (hD : TwoSidedInverse D Dinv)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (htransfer : Dinv * K = ∑ e : E, edge e)
    (hmin : ∀ e, m ≤ weight e) (hcutoff : L ≤ m * N)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    TwoSidedInverse
      (q (D + K))
      (q (prunedDiagonalTransferInverse weight edge Dinv L N)) := by
  have hpruned := prunedWordInverse_spec_of_minWeight
    filtration q L m N certificate weight edge hmin hcutoff hedge
  have htransferMapped : q Dinv * q K = ∑ e : E, q (edge e) := by
    simpa only [map_mul, map_sum] using congrArg q htransfer
  have hnormalized :
      TwoSidedInverse (1 + q Dinv * q K) (q (prunedWordInverse weight edge L N)) := by
    simpa only [map_add, map_one, map_sum, htransferMapped] using hpruned
  have hdiagonal := diagonal_inverse_of_perturbation_inverse
    (q D) (q Dinv) (q K) (q (prunedWordInverse weight edge L N)) (hD.map q) hnormalized
  simpa only [prunedDiagonalTransferInverse, map_add, map_mul] using hdiagonal

/-- Positive edge weights give the explicit pruned diagonal inverse at the standard cutoff
`N = L`. -/
theorem finitePrecisionPrunedDiagonalTransferInverse_of_weightedEdges
    {R : Type u} {S : Type v} [Ring R] [Ring S]
    (filtration : MultiplicativeFiltration R)
    (q : R →+* S) (L : ℕ) (certificate : PrecisionCertificate filtration q L)
    (D Dinv K : R) (hD : TwoSidedInverse D Dinv)
    {E : Type w} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (htransfer : Dinv * K = ∑ e : E, edge e)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, filtration.Mem (weight e) (edge e)) :
    TwoSidedInverse
      (q (D + K))
      (q (prunedDiagonalTransferInverse weight edge Dinv L L)) := by
  exact finitePrecisionPrunedDiagonalTransferInverse_of_minWeight
    filtration q L 1 L certificate D Dinv K hD weight edge htransfer hpositive (by simp) hedge

end Komorebi.PaperII.WeightedTransfer
