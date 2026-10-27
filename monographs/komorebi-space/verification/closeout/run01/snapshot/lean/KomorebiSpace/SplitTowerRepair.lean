import KomorebiSpace.BanachTowerExactification

set_option autoImplicit false

/-!
# A constructed right inverse for the tower differential

The target bonding maps have uniformly bounded right inverses. A strict bound
on forward propagation makes the causal correction uniformly bounded. No
correction operator, exact candidate, or limiting repair is postulated.
-/
universe u v
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace BanachTower
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)

/-- Chosen bounded splittings of the target bonding maps. -/
structure Splitting (Y : BanachTower.{u,v} 𝕜) where
  up : ∀ n, Y.Obj n →L[𝕜] Y.Obj (n+1)
  down_up : ∀ n, (Y.down n).comp (up n) = ContinuousLinearMap.id 𝕜 (Y.Obj n)
  bound : ℝ≥0
  up_bound : ∀ n, ‖up n‖ ≤ (bound : ℝ)

namespace Splitting
variable {Y}
variable (L : Splitting Y)

@[simp] theorem down_up_apply (n : ℕ) (y : Y.Obj n) :
    Y.down n (L.up n y) = y :=
  congrArg (fun T : Y.Obj n →L[𝕜] Y.Obj n => T y) (L.down_up n)

def gain : ℝ := (L.bound : ℝ) / (1 - (L.bound : ℝ) * X.bound)

variable (hgap : (L.bound : ℝ) * X.bound < 1)

include hgap in
theorem gain_nonneg : 0 ≤ L.gain X := by
  unfold gain
  exact div_nonneg (NNReal.coe_nonneg _) (le_of_lt (sub_pos.mpr hgap))

include hgap in
theorem gain_balance :
    (L.bound : ℝ) * (1 + L.gain X * X.bound) = L.gain X := by
  have hn : (1 - (L.bound : ℝ) * X.bound) ≠ 0 := ne_of_gt (sub_pos.mpr hgap)
  unfold gain
  field_simp [hn]
  ring

/-- The causal recurrence solving `d a = r` with `a 0 = 0`. -/
def rawCorrection (r : Residuals X Y) : ∀ n, X.Obj n →L[𝕜] Y.Obj n
  | 0 => 0
  | n+1 => (L.up n).comp (r n + (rawCorrection r n).comp (X.down n))

@[simp] theorem rawCorrection_zero (r : Residuals X Y) : L.rawCorrection X r 0 = 0 := rfl

@[simp] theorem rawCorrection_succ (r : Residuals X Y) (n : ℕ) :
    L.rawCorrection X r (n+1) =
      (L.up n).comp (r n + (L.rawCorrection X r n).comp (X.down n)) := rfl

include hgap in
theorem rawCorrection_bound (r : Residuals X Y) (n : ℕ) :
    ‖L.rawCorrection X r n‖ ≤ L.gain X * ‖r‖ := by
  induction n with
  | zero => simpa using mul_nonneg (L.gain_nonneg X hgap) (norm_nonneg r)
  | succ n ih =>
    have hr := lp.norm_apply_le_norm ENNReal.top_ne_zero r n
    have ha : ‖(L.rawCorrection X r n).comp (X.down n)‖ ≤
        (L.gain X * ‖r‖) * (X.bound : ℝ) :=
      ((L.rawCorrection X r n).opNorm_comp_le _).trans
        (mul_le_mul ih (X.down_bound n) (norm_nonneg _) (mul_nonneg
          (L.gain_nonneg X hgap) (norm_nonneg r)))
    calc
      ‖L.rawCorrection X r (n+1)‖ ≤ ‖L.up n‖ *
          ‖r n + (L.rawCorrection X r n).comp (X.down n)‖ :=
        (L.up n).opNorm_comp_le _
      _ ≤ (L.bound : ℝ) * ‖r n + (L.rawCorrection X r n).comp (X.down n)‖ :=
        mul_le_mul_of_nonneg_right (L.up_bound n) (norm_nonneg _)
      _ ≤ (L.bound : ℝ) * (‖r n‖ + ‖(L.rawCorrection X r n).comp (X.down n)‖) :=
        mul_le_mul_of_nonneg_left (norm_add_le _ _) (NNReal.coe_nonneg _)
      _ ≤ (L.bound : ℝ) * (‖r‖ + (L.gain X * ‖r‖) * (X.bound : ℝ)) :=
        mul_le_mul_of_nonneg_left (add_le_add hr ha) (NNReal.coe_nonneg _)
      _ = ((L.bound : ℝ) * (1 + L.gain X * X.bound)) * ‖r‖ := by ring
      _ = L.gain X * ‖r‖ := by rw [L.gain_balance X hgap]

theorem rawCorrection_add (r t : Residuals X Y) (n : ℕ) :
    L.rawCorrection X (r+t) n = L.rawCorrection X r n + L.rawCorrection X t n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [rawCorrection_succ, rawCorrection_succ, rawCorrection_succ, ih]
    ext x
    simp only [ContinuousLinearMap.comp_apply, add_apply,
      lp.coeFn_add, Pi.add_apply, map_add]
    abel

theorem rawCorrection_smul (c : 𝕜) (r : Residuals X Y) (n : ℕ) :
    L.rawCorrection X (c • r) n = c • L.rawCorrection X r n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [rawCorrection_succ, rawCorrection_succ, ih]
    ext x
    simp [smul_add]

include hgap in
theorem rawCorrection_mem (r : Residuals X Y) :
    Memℓp (L.rawCorrection X r) (∞ : ℝ≥0∞) := by
  apply memℓp_infty
  refine ⟨L.gain X * ‖r‖, ?_⟩
  rintro _ ⟨n, rfl⟩
  exact L.rawCorrection_bound X hgap r n

def correctionLinear : Residuals X Y →ₗ[𝕜] Candidates X Y where
  toFun r := ⟨L.rawCorrection X r, L.rawCorrection_mem X hgap r⟩
  map_add' r t := by
    apply lp.ext
    funext n
    exact L.rawCorrection_add X r t n
  map_smul' c r := by
    apply lp.ext
    funext n
    exact L.rawCorrection_smul X c r n

theorem correctionLinear_bound (r : Residuals X Y) :
    ‖L.correctionLinear X hgap r‖ ≤ L.gain X * ‖r‖ := by
  apply lp.norm_le_of_forall_le (mul_nonneg (L.gain_nonneg X hgap) (norm_nonneg r))
  exact L.rawCorrection_bound X hgap r

/-- A bounded right inverse, constructed from the bonding-map splittings. -/
def correction : Residuals X Y →L[𝕜] Candidates X Y :=
  (L.correctionLinear X hgap).mkContinuous (L.gain X)
    (L.correctionLinear_bound X hgap)

@[simp] theorem correction_apply (r : Residuals X Y) (n : ℕ) :
    L.correction X hgap r n = L.rawCorrection X r n := rfl

theorem correction_bound (r : Residuals X Y) :
    ‖L.correction X hgap r‖ ≤ L.gain X * ‖r‖ := L.correctionLinear_bound X hgap r

theorem correction_opNorm : ‖L.correction X hgap‖ ≤ L.gain X :=
  ContinuousLinearMap.opNorm_le_bound _ (L.gain_nonneg X hgap)
    (L.correction_bound X hgap)

theorem rawCorrection_defect (r : Residuals X Y) (n : ℕ) :
    (Y.down n).comp (L.rawCorrection X r (n+1)) -
      (L.rawCorrection X r n).comp (X.down n) = r n := by
  ext x
  simp [rawCorrection_succ]

/-- Exact cancellation on every bounded residual, not only those already in the range. -/
@[simp] theorem differential_correction (r : Residuals X Y) :
    differential X Y (L.correction X hgap r) = r := by
  apply lp.ext
  funext n
  exact L.rawCorrection_defect X r n

@[simp] theorem correction_preserves_zero (r : Residuals X Y) :
    L.correction X hgap r 0 = 0 := rfl

/-- The constructed correction discharges all hypotheses of the existing repair engine. -/
def scheme : RepairDynamics.Scheme (differential X Y) (evaluation X Y 0) where
  correction := L.correction X hgap
  rate := 0
  rate_nonneg := le_rfl
  rate_lt_one := zero_lt_one
  preserve r := rfl
  contract f := by simp

/-- The exactifier has a finite formula, independent of limit packaging. -/
def repair : Candidates X Y →L[𝕜] Candidates X Y :=
  ContinuousLinearMap.id 𝕜 _ - (L.correction X hgap).comp (differential X Y)

@[simp] theorem repair_apply (f : Candidates X Y) :
    L.repair X hgap f = f - L.correction X hgap (differential X Y f) := rfl

@[simp] theorem repair_differential_zero (f : Candidates X Y) :
    differential X Y (L.repair X hgap f) = 0 := by
  simp only [repair_apply, map_sub, differential_correction, sub_self]

theorem repair_exact (f : Candidates X Y) : Exact X Y (L.repair X hgap f) :=
  (exact_iff_differential_zero X Y _).mpr (L.repair_differential_zero X hgap f)

@[simp] theorem repair_preserves_zero (f : Candidates X Y) :
    L.repair X hgap f 0 = f 0 := by
  change f 0 - L.correction X hgap (differential X Y f) 0 = f 0
  simp

@[simp] theorem repair_fixes_exact (f : Candidates X Y) (hf : Exact X Y f) :
    L.repair X hgap f = f := by
  rw [repair_apply, (exact_iff_differential_zero X Y f).mp hf, map_zero, sub_zero]

@[simp] theorem repair_idempotent (f : Candidates X Y) :
    L.repair X hgap (L.repair X hgap f) = L.repair X hgap f :=
  L.repair_fixes_exact X hgap _ (L.repair_exact X hgap f)

theorem repair_error (f : Candidates X Y) :
    ‖f - L.repair X hgap f‖ ≤ L.gain X * ‖differential X Y f‖ := by
  rw [repair_apply, sub_sub_cancel]
  exact L.correction_bound X hgap _

theorem repair_image_iff (g : Candidates X Y) :
    (∃ f, L.repair X hgap f = g) ↔ Exact X Y g := by
  constructor
  · rintro ⟨f, rfl⟩
    exact L.repair_exact X hgap f
  · intro hg
    exact ⟨g, L.repair_fixes_exact X hgap g hg⟩

/-- The abstract limiting projector equals the explicit one-step repair. -/
theorem scheme_projection_eq (f : Candidates X Y) :
    (L.scheme X hgap).projection f = L.repair X hgap f := by
  have h := ((L.scheme X hgap).limit_spec f).2.2.2 1
  have hstep : RepairDynamics.orbit (differential X Y) (L.scheme X hgap).correction f 1 =
      L.repair X hgap f := rfl
  rw [hstep, L.repair_differential_zero X hgap, norm_zero, mul_zero] at h
  exact (dist_le_zero.mp h).symm

end Splitting
end BanachTower
end KomorebiSpace
end
