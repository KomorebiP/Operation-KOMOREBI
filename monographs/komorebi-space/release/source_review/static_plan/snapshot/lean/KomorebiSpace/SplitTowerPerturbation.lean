import KomorebiSpace.SplitTowerCanonicity

set_option autoImplicit false

/-!
# Quantitative dependence on the target splitting

The source and target towers remain fixed. Uniformly close right inverses of
the target bonding maps yield uniformly close correction operators, with an
explicit two-gap denominator. This is not invariance under changing norms.
-/
universe u v
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace BanachTower
namespace Splitting
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X : BanachTower.{u,v} 𝕜) {Y : BanachTower.{u,v} 𝕜}
variable (L M : Splitting Y)

/-- The denominator records distance to the propagation threshold for both splittings. -/
def perturbationGain (ε : ℝ) : ℝ :=
  ε / ((1 - (L.bound : ℝ) * X.bound) * (1 - (M.bound : ℝ) * X.bound))

variable (hL : (L.bound : ℝ) * X.bound < 1)
variable (hM : (M.bound : ℝ) * X.bound < 1)
variable {ε : ℝ} (hε : 0 ≤ ε)

include hL hM hε in
 theorem perturbationGain_nonneg : 0 ≤ L.perturbationGain X M ε := by
  exact div_nonneg hε (le_of_lt (mul_pos (sub_pos.mpr hL) (sub_pos.mpr hM)))

include hL hM in
 theorem perturbationGain_balance (ε : ℝ) :
    (L.bound : ℝ) * (L.perturbationGain X M ε * X.bound) +
      ε * (1 + M.gain X * X.bound) = L.perturbationGain X M ε := by
  have hl : 1 - (L.bound : ℝ) * X.bound ≠ 0 := ne_of_gt (sub_pos.mpr hL)
  have hm : 1 - (M.bound : ℝ) * X.bound ≠ 0 := ne_of_gt (sub_pos.mpr hM)
  have hm' : 1 - (X.bound : ℝ) * M.bound ≠ 0 := by simpa only [mul_comm] using hm
  unfold perturbationGain gain
  field_simp [hl, hm, hm']
  ring

/-- Exact perturbation recurrence before any norm estimate. -/
theorem rawCorrection_difference_succ (r : Residuals X Y) (n : ℕ) :
    L.rawCorrection X r (n+1) - M.rawCorrection X r (n+1) =
      (L.up n).comp ((L.rawCorrection X r n - M.rawCorrection X r n).comp (X.down n)) +
      (L.up n - M.up n).comp (r n + (M.rawCorrection X r n).comp (X.down n)) := by
  rw [rawCorrection_succ, rawCorrection_succ]
  ext x
  simp only [ContinuousLinearMap.comp_apply, sub_apply, add_apply, map_add, map_sub]
  abel

include hL hM hε in
 theorem rawCorrection_perturbation (hclose : ∀ n, ‖L.up n - M.up n‖ ≤ ε)
    (r : Residuals X Y) (n : ℕ) :
    ‖L.rawCorrection X r n - M.rawCorrection X r n‖ ≤
      L.perturbationGain X M ε * ‖r‖ := by
  have hc : 0 ≤ L.perturbationGain X M ε := L.perturbationGain_nonneg X M hL hM hε
  induction n with
  | zero => simpa using mul_nonneg hc (norm_nonneg r)
  | succ n ih =>
    have hn := lp.norm_apply_le_norm ENNReal.top_ne_zero r n
    have hx : ‖(L.rawCorrection X r n - M.rawCorrection X r n).comp (X.down n)‖ ≤
        (L.perturbationGain X M ε * ‖r‖) * (X.bound : ℝ) :=
      ((L.rawCorrection X r n - M.rawCorrection X r n).opNorm_comp_le _).trans
        (mul_le_mul ih (X.down_bound n) (norm_nonneg _) (mul_nonneg hc (norm_nonneg r)))
    have hm : ‖(M.rawCorrection X r n).comp (X.down n)‖ ≤
        (M.gain X * ‖r‖) * (X.bound : ℝ) :=
      ((M.rawCorrection X r n).opNorm_comp_le _).trans
        (mul_le_mul (M.rawCorrection_bound X hM r n) (X.down_bound n)
          (norm_nonneg _) (mul_nonneg (M.gain_nonneg X hM) (norm_nonneg r)))
    have ha : ‖(L.up n).comp
        ((L.rawCorrection X r n - M.rawCorrection X r n).comp (X.down n))‖ ≤
        (L.bound : ℝ) * ((L.perturbationGain X M ε * ‖r‖) * (X.bound : ℝ)) :=
      ((L.up n).opNorm_comp_le _).trans
        (mul_le_mul (L.up_bound n) hx (norm_nonneg _) (NNReal.coe_nonneg _))
    have hb : ‖(L.up n - M.up n).comp (r n + (M.rawCorrection X r n).comp (X.down n))‖ ≤
        ε * (‖r‖ + (M.gain X * ‖r‖) * (X.bound : ℝ)) :=
      ((L.up n - M.up n).opNorm_comp_le _).trans
        (mul_le_mul (hclose n) ((norm_add_le _ _).trans (add_le_add hn hm))
          (norm_nonneg _) hε)
    rw [L.rawCorrection_difference_succ X M r n]
    calc
      _ ≤ _ := norm_add_le _ _
      _ ≤ (L.bound : ℝ) * ((L.perturbationGain X M ε * ‖r‖) * (X.bound : ℝ)) +
          ε * (‖r‖ + (M.gain X * ‖r‖) * (X.bound : ℝ)) := add_le_add ha hb
      _ = ((L.bound : ℝ) * (L.perturbationGain X M ε * X.bound) +
          ε * (1 + M.gain X * X.bound)) * ‖r‖ := by ring
      _ = _ := by rw [L.perturbationGain_balance X M hL hM]

include hε in
 theorem correction_perturbation (hclose : ∀ n, ‖L.up n - M.up n‖ ≤ ε)
    (r : Residuals X Y) :
    ‖L.correction X hL r - M.correction X hM r‖ ≤
      L.perturbationGain X M ε * ‖r‖ := by
  apply lp.norm_le_of_forall_le
    (mul_nonneg (L.perturbationGain_nonneg X M hL hM hε) (norm_nonneg r))
  intro n
  exact L.rawCorrection_perturbation X M hL hM hε hclose r n

include hε in
 theorem correction_perturbation_opNorm (hclose : ∀ n, ‖L.up n - M.up n‖ ≤ ε) :
    ‖L.correction X hL - M.correction X hM‖ ≤ L.perturbationGain X M ε := by
  apply ContinuousLinearMap.opNorm_le_bound _ (L.perturbationGain_nonneg X M hL hM hε)
  exact L.correction_perturbation X M hL hM hε hclose

include hε in
 theorem repair_perturbation (hclose : ∀ n, ‖L.up n - M.up n‖ ≤ ε)
    (f : Candidates X Y) :
    ‖M.repair X hM f - L.repair X hL f‖ ≤
      L.perturbationGain X M ε * ‖differential X Y f‖ := by
  rw [L.repair_change X M hL hM f]
  exact L.correction_perturbation X M hL hM hε hclose _

include hε in
 theorem repair_perturbation_opNorm (hclose : ∀ n, ‖L.up n - M.up n‖ ≤ ε) :
    ‖M.repair X hM - L.repair X hL‖ ≤
      L.perturbationGain X M ε * ((X.bound : ℝ) + Y.bound) := by
  have hc := L.perturbationGain_nonneg X M hL hM hε
  apply ContinuousLinearMap.opNorm_le_bound _ (mul_nonneg hc (by positivity))
  intro f
  calc
    _ ≤ L.perturbationGain X M ε * ‖differential X Y f‖ :=
      L.repair_perturbation X M hL hM hε hclose f
    _ ≤ L.perturbationGain X M ε * (((X.bound : ℝ) + Y.bound) * ‖f‖) :=
      mul_le_mul_of_nonneg_left (differential_bound X Y f) hc
    _ = _ := by ring

end Splitting
end BanachTower
end KomorebiSpace
end
