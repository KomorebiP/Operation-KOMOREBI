module
public import Euler.SourceScalars
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- The actual dyadic inverse coefficient, including its correct zero-depth value. -/
def eulerKappaRat (m : ℕ) : ℚ :=
  -(2:ℚ)^(4*m) * (2*(m:ℚ)-1) * bernoulli (2*m)

@[simp] lemma eulerKappaRat_zero : eulerKappaRat 0=1 := by
  norm_num [eulerKappaRat, bernoulli_zero]

lemma eulerOddFactor_ne_zero (m : ℕ) : 2*(m:ℚ)-1≠0 := by
  exact_mod_cast (show 2*(m:ℤ)-1≠0 by omega)

lemma eulerOddFactor_val (m : ℕ) : padicValRat 2 (2*(m:ℚ)-1)=0 := by
  have hc : (2*(m:ℚ)-1) = ((2*(m:ℤ)-1:ℤ):ℚ) := by push_cast; rfl
  rw [hc,padicValRat.of_int]
  have hz : padicValInt 2 (2*(m:ℤ)-1)=0 := padicValInt.eq_zero_of_not_dvd (by omega)
  rw [hz]
  rfl

lemma eulerBernoulli_val (m : ℕ) (hm : 0<m) :
    padicValRat 2 (bernoulli (2*m)) = -1 := by
  exact Bernoulli.padicValRat_bernoulli hm (by simp)

lemma eulerBernoulli_ne_zero (m : ℕ) (hm : 0<m) : bernoulli (2*m)≠0 := by
  intro hz
  have h := eulerBernoulli_val m hm
  rw [hz] at h
  norm_num at h

lemma eulerKappaRat_ne_zero (m : ℕ) : eulerKappaRat m≠0 := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp
  · exact mul_ne_zero (mul_ne_zero (neg_ne_zero.mpr (pow_ne_zero _ (by norm_num)))
      (eulerOddFactor_ne_zero m)) (eulerBernoulli_ne_zero m hm)

/-- The four-bit slope is now proved from the actual Bernoulli definition. -/
theorem eulerKappaRat_val (m : ℕ) (hm : 0<m) :
    padicValRat 2 (eulerKappaRat m)=4*(m:ℤ)-1 := by
  rw [eulerKappaRat,
    padicValRat.mul (mul_ne_zero (neg_ne_zero.mpr (pow_ne_zero _ (by norm_num)))
      (eulerOddFactor_ne_zero m)) (eulerBernoulli_ne_zero m hm),
    padicValRat.mul (neg_ne_zero.mpr (pow_ne_zero _ (by norm_num)))
      (eulerOddFactor_ne_zero m), padicValRat.neg, padicValRat.pow,
    eulerOddFactor_val, eulerBernoulli_val m hm]
  have hp : padicValRat 2 (2:ℚ)=1 := padicValRat.self (by norm_num)
  rw [hp]
  push_cast
  ring

lemma eulerKappaRat_val_nonneg (m : ℕ) : 0≤padicValRat 2 (eulerKappaRat m) := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp
  · rw [eulerKappaRat_val m hm]
    omega

/-- The actual rational inverse coefficient embedded in the dyadic integers. -/
def eulerKappa (m : ℕ) : D :=
  ⟨(eulerKappaRat m:ℚ_[2]), (Padic.norm_le_one_iff_val_nonneg _).mpr
    (by simpa only [Padic.valuation_ratCast] using eulerKappaRat_val_nonneg m)⟩

@[simp] lemma eulerKappa_coe (m : ℕ) :
    (eulerKappa m:ℚ_[2])=(eulerKappaRat m:ℚ_[2]) := rfl

@[simp] lemma eulerKappa_zero : eulerKappa 0=1 := by
  apply Subtype.ext
  simp

lemma eulerKappa_ne_zero (m : ℕ) : eulerKappa m≠0 := by
  intro h
  have hc := congrArg (fun x:D => (x:ℚ_[2])) h
  simp only [eulerKappa_coe,PadicInt.coe_zero] at hc
  exact eulerKappaRat_ne_zero m (by exact_mod_cast hc)

/-- The same sharp valuation in the actual dyadic field. -/
theorem eulerKappa_valuation (m : ℕ) (hm : 0<m) :
    Padic.valuation (eulerKappa m:ℚ_[2])=4*(m:ℤ)-1 := by
  rw [eulerKappa_coe,Padic.valuation_ratCast,eulerKappaRat_val m hm]

/-- Exact kernel norm, including the strict first omitted-layer size. -/
theorem eulerKappa_norm (m : ℕ) (hm : 0<m) :
    ‖eulerKappa m‖=(2:ℝ)^(-(4*(m:ℤ)-1)) := by
  change ‖(eulerKappa m:ℚ_[2])‖=_
  rw [Padic.norm_eq_zpow_neg_valuation (by
    exact (PadicInt.coe_eq_zero).not.mpr (eulerKappa_ne_zero m)),eulerKappa_valuation m hm]
  norm_num

end Komorebi.Euler
