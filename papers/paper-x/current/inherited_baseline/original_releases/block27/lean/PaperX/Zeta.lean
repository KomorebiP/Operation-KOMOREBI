import PaperX.Counting
import Mathlib.RingTheory.PowerSeries.Inverse
import Mathlib.RingTheory.PowerSeries.Trunc

/-!
Formal (not analytic) generating series in Q[[X]]. The finite prefix is an
actual polynomial truncation. Denominators have constant term one. No
floating approximation, numerical fitting, or convergence assumption is used.
-/
set_option autoImplicit false
namespace PaperX.Zeta
open PowerSeries

noncomputable def geometric (a : ℚ) : ℚ⟦X⟧ := mk fun n => a ^ n

theorem geometric_mul_denominator (a : ℚ) :
    geometric a * (1 - C a * X) = 1 := by
  rw [mul_sub, mul_one, ← mul_assoc]
  ext n
  cases n with
  | zero => simp [geometric, coeff_zero_eq_constantCoeff_apply]
  | succ n => simp [geometric, pow_succ]

theorem geometric_eq_inverse (a : ℚ) :
    geometric a = (1 - C a * X)⁻¹ := by
  apply (eq_inv_iff_mul_eq_one (by simp)).mpr
  exact geometric_mul_denominator a

/-- A geometric tail is represented exactly by a rational formal power series. -/
theorem eventually_geometric_formula (a : ℕ → ℚ) (rate : ℚ) (N : ℕ)
    (htail : ∀ n, N ≤ n → a n = a N * rate ^ (n - N)) :
    mk a = (trunc N (mk a) : ℚ⟦X⟧) +
      C (a N) * X ^ N * (1 - C rate * X)⁻¹ := by
  rw [← geometric_eq_inverse]
  have rearrange : C (a N) * X ^ N * geometric rate =
      C (a N) * (geometric rate * X ^ N) := by ring
  rw [rearrange]
  ext n
  simp only [coeff_mk, map_add, Polynomial.coeff_coe, coeff_trunc, coeff_C_mul,
    coeff_mul_X_pow', geometric]
  by_cases hn : n < N
  · simp [hn, show ¬ N ≤ n by omega]
  · simp [hn, show N ≤ n by omega, htail n (by omega)]

noncomputable def weightedCoeff {d : ℕ} (q : ℕ) (w : Fin d → ℕ) (m : ℕ) : ℚ :=
  if m = 0 then 0 else (q : ℚ) ^ (∑ i, (m - w i))

noncomputable def modelZeta {d : ℕ} (q : ℕ) (w : Fin d → ℕ) : ℚ⟦X⟧ :=
  mk (weightedCoeff q w)

/-- Once all coordinates are active, each new digit multiplies the count by q^d. -/
theorem weighted_tail {d : ℕ} (q : ℕ) (w : Fin d → ℕ) (N : ℕ)
    (hN : 0 < N) (bound : ∀ i, w i ≤ N) (n : ℕ) (hn : N ≤ n) :
    weightedCoeff q w n = weightedCoeff q w N * ((q : ℚ) ^ d) ^ (n-N) := by
  have hs : (∑ i, (n - w i)) = (∑ i, (N - w i)) + d * (n-N) := by
    calc
      (∑ i, (n - w i)) = ∑ i, ((N - w i) + (n-N)) := by
        apply Finset.sum_congr rfl
        intro i _
        have := bound i
        omega
      _ = _ := by simp [Finset.sum_add_distrib]
  simp only [weightedCoeff, ite_eq_right (show n ≠ 0 by omega), ite_eq_right (by omega : N ≠ 0)]
  rw [hs, pow_add, pow_mul]

/-- Weighted seed zeta, with any upper bound M on the weights. This includes d=0. -/
theorem weighted_zeta_formula {d : ℕ} (q : ℕ) (w : Fin d → ℕ) (M : ℕ)
    (bound : ∀ i, w i ≤ M) :
    modelZeta q w = (trunc (M+1) (modelZeta q w) : ℚ⟦X⟧) +
      C (weightedCoeff q w (M+1)) * X ^ (M+1) * (1 - C ((q : ℚ)^d) * X)⁻¹ := by
  exact eventually_geometric_formula (weightedCoeff q w) ((q : ℚ)^d) (M+1)
    (weighted_tail q w (M+1) (by omega) (fun i => (bound i).trans (by omega)))

/-- The smooth formula T/(1-q^d T), as an identity of infinite formal series. -/
theorem smooth_zeta_formula (q d : ℕ) :
    modelZeta q (fun _ : Fin d => 1) = X * (1 - C ((q : ℚ)^d) * X)⁻¹ := by
  have h := eventually_geometric_formula
    (weightedCoeff q (fun _ : Fin d => 1)) ((q : ℚ)^d) 1
    (weighted_tail q (fun _ : Fin d => 1) 1 (by omega) (fun _ => le_rfl))
  have ht : trunc 1 (modelZeta q (fun _ : Fin d => 1)) = 0 := by
    ext n
    by_cases hn : n = 0
    · subst n
      simp [modelZeta, weightedCoeff]
    · simp [modelZeta, weightedCoeff]
  change modelZeta q (fun _ : Fin d => 1) = _ at h
  change trunc 1 (mk (weightedCoeff q (fun _ : Fin d => 1))) = 0 at ht
  rw [ht] at h
  simpa [weightedCoeff] using h

/-- Simplify the first tail coefficient to q^(d(M+1)-sum w_i). -/
theorem weighted_first_tail {d : ℕ} (q : ℕ) (w : Fin d → ℕ) (M : ℕ)
    (bound : ∀ i, w i ≤ M) :
    weightedCoeff q w (M+1) = (q : ℚ) ^ (d*(M+1) - ∑ i, w i) := by
  simp only [weightedCoeff, Nat.add_eq_zero_iff, one_ne_zero, and_false, ↓reduceIte]
  congr 1
  rw [Finset.sum_tsub_distrib Finset.univ (fun i _ => (bound i).trans (by omega))]
  simp

variable {O : Type*} [CommRing O] [IsDedekindDomain O]
variable (P : Ideal O) [P.IsPrime] (hP : P ≠ ⊥) [Finite (O ⧸ P)]

/-- Defined using cardinalities of actual ideal-quotient tuples. -/
noncomputable def chartZeta {d : ℕ} (w : Fin d → ℕ) : ℚ⟦X⟧ :=
  mk fun m => if m = 0 then 0 else (Nat.card (PaperX.Counting.WeightedChart P w m) : ℚ)

include hP in
theorem chartZeta_eq_model {d : ℕ} (w : Fin d → ℕ) :
    chartZeta P w = modelZeta (PaperX.Counting.residueCard P) w := by
  ext n
  simp [chartZeta, modelZeta, weightedCoeff, PaperX.Counting.weighted_chart_count P hP]

include hP in
theorem actual_weighted_zeta {d : ℕ} (w : Fin d → ℕ) (M : ℕ)
    (bound : ∀ i, w i ≤ M) :
    chartZeta P w = (trunc (M+1) (chartZeta P w) : ℚ⟦X⟧) +
      C ((PaperX.Counting.residueCard P : ℚ) ^ (d*(M+1) - ∑ i, w i)) *
      X ^ (M+1) * (1 - C ((PaperX.Counting.residueCard P : ℚ)^d) * X)⁻¹ := by
  rw [chartZeta_eq_model P hP]
  rw [← weighted_first_tail _ w M bound]
  exact weighted_zeta_formula _ w M bound

include hP in
theorem actual_smooth_zeta (d : ℕ) :
    chartZeta P (fun _ : Fin d => 1) =
      X * (1 - C ((PaperX.Counting.residueCard P : ℚ)^d) * X)⁻¹ := by
  rw [chartZeta_eq_model P hP]
  exact smooth_zeta_formula _ d

end PaperX.Zeta
