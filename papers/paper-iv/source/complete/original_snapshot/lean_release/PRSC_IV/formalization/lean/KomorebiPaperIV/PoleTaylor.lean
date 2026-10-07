/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.PoleRemoval
import KomorebiPaperIV.CompanionCompletion

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology Classical

theorem analyticTaylorSeries_sub {f g : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0) :
    analyticTaylorSeries (fun z => f z - g z) = analyticTaylorSeries f - analyticTaylorSeries g := by
  simp only [sub_eq_add_neg]
  rw [analyticTaylorSeries_add (g := fun z => -g z) hf (by fun_prop), analyticTaylorSeries_neg]

theorem analyticTaylorSeries_finsetSum {ι : Type*} (S : Finset ι) {f : ι → ℂ → ℂ}
    (hf : ∀ i ∈ S, AnalyticAt ℂ (f i) 0) :
    analyticTaylorSeries (fun z => ∑ i ∈ S, f i z) = ∑ i ∈ S, analyticTaylorSeries (f i) := by
  induction S using Finset.induction_on with
  | empty => simp
  | @insert i S hi ih =>
    simp only [Finset.sum_insert hi]
    rw [analyticTaylorSeries_add (hf i (Finset.mem_insert_self i S))
      (Finset.analyticAt_fun_sum _ (fun k hk => hf k (Finset.mem_insert_of_mem hk))),
      ih (fun k hk => hf k (Finset.mem_insert_of_mem hk))]

theorem analyticTaylorSeries_id : analyticTaylorSeries (fun z : ℂ => z) = PowerSeries.X := by
  ext n
  cases n with
  | zero => simp [analyticTaylorCoefficient]
  | succ n =>
    simp [analyticTaylorCoefficient, iteratedDeriv_fun_id, PowerSeries.coeff_X]
    split_ifs <;> simp_all

theorem analyticTaylorSeries_poleTerm (ρ : ℂ) (ℓ : ℕ) :
    analyticTaylorSeries (poleTerm ρ ℓ) = principalPartSeries ρ ℓ := by
  have hb : AnalyticAt ℂ (fun z : ℂ => 1 - z / ρ) 0 := by fun_prop
  have he : analyticTaylorSeries (fun z : ℂ => 1 - z / ρ) = 1 - PowerSeries.C ρ⁻¹ * PowerSeries.X := by
    simp_rw [div_eq_mul_inv, mul_comm _ ρ⁻¹]
    rw [analyticTaylorSeries_sub (g := fun z => ρ⁻¹ * z) analyticAt_const (by fun_prop),
      analyticTaylorSeries_mul (f := fun _ => ρ⁻¹) (g := fun z => z) analyticAt_const analyticAt_id, analyticTaylorSeries_const,
      analyticTaylorSeries_const, analyticTaylorSeries_id]
    simp
  have hi := analyticTaylorSeries_inverse_product (f := fun z => (1 - z / ρ) ^ ℓ)
    (hb.pow ℓ) (by simp)
  rw [analyticTaylorSeries_pow hb, he] at hi
  have hu : IsUnit ((1 - PowerSeries.C ρ⁻¹ * PowerSeries.X) ^ ℓ) :=
    PowerSeries.isUnit_iff_constantCoeff.mpr (by simp)
  apply hu.mul_left_cancel
  exact hi.trans (by rw [mul_comm]; exact (principalPartSeries_inverse ρ ℓ).symm)

theorem analyticTaylorCoefficient_principalPart {ρ : ℂ} (hρ : ρ ≠ 0)
    (a : ℂ → ℕ → ℂ) (r m : ℕ) :
    analyticTaylorCoefficient (polePrincipalPart a r ρ) m =
      ∑ k ∈ Finset.range r, a ρ (k + 1) * ((m + k).choose k : ℂ) * ρ⁻¹ ^ m := by
  have ha (k : ℕ) : AnalyticAt ℂ (poleTerm ρ (k+1)) 0 := poleTerm_analyticAt hρ hρ.symm (k+1)
  rw [← analyticTaylorSeries_coeff (polePrincipalPart a r ρ) m]
  change PowerSeries.coeff m (analyticTaylorSeries (fun z => ∑ k ∈ Finset.range r,
    a ρ (k+1) * poleTerm ρ (k+1) z)) = _
  rw [analyticTaylorSeries_finsetSum _ (fun k _ => analyticAt_const.fun_mul (ha k)), map_sum]
  apply Finset.sum_congr rfl
  intro k _
  rw [analyticTaylorSeries_mul analyticAt_const (ha k), analyticTaylorSeries_const,
    analyticTaylorSeries_poleTerm, PowerSeries.coeff_C_mul,
    principalPartSeries_coefficient ρ (Nat.succ_pos k)]
  simp only [Nat.succ_sub_one, Nat.add_succ_sub_one, mul_assoc]

theorem analyticTaylorSeries_canonicalSignedDenominator {N : ℕ} (hN : 0 < N) :
    analyticTaylorSeries (canonicalSignedDenominator N) = signedSection (R := ℂ) N 0 := by
  ext n
  rw [analyticTaylorSeries_coeff, analyticTaylorCoefficient]
  rw [iteratedDeriv_eq_iterate]
  unfold canonicalSignedDenominator
  rw [entireSigned_derivative_at_zero hN hN (canonicalPrimitiveRoot_isPrimitive hN) (canonicalSignedRoot_pow hN)]
  simp [Nat.factorial_ne_zero]

theorem reciprocalSeries_nat (N r : ℕ) : reciprocalSeries (R := ℂ) N (r : ℂ) = reciprocalSeries N 1 ^ r := by
  induction r with
  | zero => simp [reciprocalSeries_zero]
  | succ r ih => rw [Nat.cast_add, Nat.cast_one, ← reciprocalSeries_add, ih, pow_succ]

theorem analyticTaylorSeries_reciprocal_signed {N : ℕ} (hN : 0 < N) (r : ℕ) :
    analyticTaylorSeries (fun z => (canonicalSignedDenominator N z ^ r)⁻¹) =
      PowerSeries.expand N hN.ne' (reciprocalSeries N (r : ℂ)) := by
  have hf : AnalyticAt ℂ (canonicalSignedDenominator N) 0 := analyticAt_entireSigned ..
  have hi := analyticTaylorSeries_inverse_product (f := fun z => canonicalSignedDenominator N z ^ r)
    (hf.pow r) (by rw [canonicalSignedDenominator_zero hN]; simp)
  rw [analyticTaylorSeries_pow hf, analyticTaylorSeries_canonicalSignedDenominator hN,
    signedSection_zero_eq_expand_reducedDenominator hN] at hi
  have he : PowerSeries.expand N hN.ne' (reciprocalSeries N (r : ℂ)) *
      (PowerSeries.expand N hN.ne' (reducedDenominator N)) ^ r = 1 := by
    rw [reciprocalSeries_nat, ← map_pow, ← map_mul, ← mul_pow,
      ← reciprocalSeries_neg_one (R := ℂ) N, reciprocalSeries_add]
    simp [reciprocalSeries_zero]
  have hu : IsUnit ((PowerSeries.expand N hN.ne' (reducedDenominator (R := ℂ) N)) ^ r) :=
    PowerSeries.isUnit_iff_constantCoeff.mpr (by simp)
  exact hu.mul_left_cancel (hi.trans (by rw [mul_comm]; exact he.symm))

/-- The actual analytic reciprocal has the manuscript's exact factorial-scaled coefficients. -/
theorem reciprocalCoeff_analyticTaylor {N : ℕ} (hN : 0 < N) (n r : ℕ) :
    reciprocalCoeff N n (r : ℂ) = ((N*n).factorial : ℂ) *
      analyticTaylorCoefficient (fun z => (canonicalSignedDenominator N z ^ r)⁻¹) (N*n) := by
  rw [← analyticTaylorSeries_coeff]
  rw [analyticTaylorSeries_reciprocal_signed hN, PowerSeries.coeff_expand_mul]
  rfl

end
end Komorebi.PaperIV
