import KomorebiSpace.SplitTowerRepair

set_option autoImplicit false

/-!
# Protected seed and innovation coordinates

A target splitting distinguishes inherited output from the new output kernel.
The full observable protects the initial operator and every innovation row.
Unlike evaluation at level zero alone, this observable separates exact maps.
All canonicity statements remain relative to the specified splitting.
-/
universe u v
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace BanachTower
namespace Splitting
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X : BanachTower.{u,v} 𝕜) {Y : BanachTower.{u,v} 𝕜}
variable (L : Splitting Y)

/-- The output component not inherited through the chosen target section. -/
def innovation (f : Candidates X Y) (n : ℕ) : X.Obj (n+1) →L[𝕜] Y.Obj (n+1) :=
  f (n+1) - (L.up n).comp ((Y.down n).comp (f (n+1)))

theorem innovation_bound (f : Candidates X Y) (n : ℕ) :
    ‖L.innovation X f n‖ ≤ (1 + (L.bound : ℝ) * Y.bound) * ‖f‖ := by
  have hf := lp.norm_apply_le_norm ENNReal.top_ne_zero f (n+1)
  have hd : ‖(Y.down n).comp (f (n+1))‖ ≤ (Y.bound : ℝ) * ‖f‖ :=
    ((Y.down n).opNorm_comp_le _).trans
      (mul_le_mul (Y.down_bound n) hf (norm_nonneg _) (NNReal.coe_nonneg _))
  have hu : ‖(L.up n).comp ((Y.down n).comp (f (n+1)))‖ ≤
      (L.bound : ℝ) * ((Y.bound : ℝ) * ‖f‖) :=
    ((L.up n).opNorm_comp_le _).trans
      (mul_le_mul (L.up_bound n) hd (norm_nonneg _) (NNReal.coe_nonneg _))
  calc
    ‖L.innovation X f n‖ ≤ ‖f (n+1)‖ +
        ‖(L.up n).comp ((Y.down n).comp (f (n+1)))‖ := norm_sub_le _ _
    _ ≤ ‖f‖ + (L.bound : ℝ) * ((Y.bound : ℝ) * ‖f‖) := add_le_add hf hu
    _ = (1 + (L.bound : ℝ) * Y.bound) * ‖f‖ := by ring

def rawObservable (f : Candidates X Y) : ∀ n, X.Obj n →L[𝕜] Y.Obj n
  | 0 => f 0
  | n+1 => L.innovation X f n

theorem rawObservable_bound (f : Candidates X Y) (n : ℕ) :
    ‖L.rawObservable X f n‖ ≤ (1 + (L.bound : ℝ) * Y.bound) * ‖f‖ := by
  cases n with
  | zero =>
    have hf := lp.norm_apply_le_norm ENNReal.top_ne_zero f 0
    have ht : 0 ≤ (L.bound : ℝ) * (Y.bound : ℝ) :=
      mul_nonneg (NNReal.coe_nonneg _) (NNReal.coe_nonneg _)
    change ‖f 0‖ ≤ _
    nlinarith [norm_nonneg f]
  | succ n => exact L.innovation_bound X f n

def observableLinear : Candidates X Y →ₗ[𝕜] Candidates X Y where
  toFun f := ⟨L.rawObservable X f, memℓp_infty ⟨(1 + (L.bound : ℝ) * Y.bound) * ‖f‖,
    by rintro _ ⟨n, rfl⟩; exact L.rawObservable_bound X f n⟩⟩
  map_add' f g := by
    apply lp.ext
    funext n
    cases n with
    | zero => rfl
    | succ n =>
      ext x
      simp only [rawObservable, innovation, lp.coeFn_add, Pi.add_apply,
        ContinuousLinearMap.comp_apply, add_apply, sub_apply, map_add]
      abel
  map_smul' c f := by
    apply lp.ext
    funext n
    cases n with
    | zero => rfl
    | succ n =>
      ext x
      simp [rawObservable, innovation, smul_sub]

theorem observableLinear_bound (f : Candidates X Y) :
    ‖L.observableLinear X f‖ ≤ (1 + (L.bound : ℝ) * Y.bound) * ‖f‖ := by
  apply lp.norm_le_of_forall_le (by positivity)
  exact L.rawObservable_bound X f

/-- A bounded observable retaining all fresh output information, not only the seed. -/
def observable : Candidates X Y →L[𝕜] Candidates X Y :=
  (L.observableLinear X).mkContinuous (1 + (L.bound : ℝ) * Y.bound)
    (L.observableLinear_bound X)

@[simp] theorem observable_zero (f : Candidates X Y) : L.observable X f 0 = f 0 := rfl

@[simp] theorem observable_succ (f : Candidates X Y) (n : ℕ) :
    L.observable X f (n+1) = L.innovation X f n := rfl

theorem observable_bound (f : Candidates X Y) :
    ‖L.observable X f‖ ≤ (1 + (L.bound : ℝ) * Y.bound) * ‖f‖ :=
  L.observableLinear_bound X f

theorem observable_opNorm : ‖L.observable X‖ ≤ 1 + (L.bound : ℝ) * Y.bound :=
  ContinuousLinearMap.opNorm_le_bound _ (by positivity) (L.observable_bound X)

/-- Innovations really take values in the kernel of the target coarse-graining map. -/
@[simp] theorem innovation_down (f : Candidates X Y) (n : ℕ) :
    (Y.down n).comp (L.innovation X f n) = 0 := by
  ext x
  simp [innovation]

@[simp] theorem observable_idempotent (f : Candidates X Y) :
    L.observable X (L.observable X f) = L.observable X f := by
  apply lp.ext
  funext n
  cases n with
  | zero => rfl
  | succ n =>
    change L.innovation X (L.observable X f) n = L.innovation X f n
    ext x
    simp [innovation]

/-- Exact compatibility determines the inherited part at the next level. -/
theorem exact_reconstruction (f : Candidates X Y) (hf : Exact X Y f) (n : ℕ) :
    f (n+1) = (L.up n).comp ((f n).comp (X.down n)) + L.innovation X f n := by
  rw [← hf n]
  unfold innovation
  abel

/-- Seed plus innovations, in contrast to the seed alone, distinguish exact maps. -/
theorem exact_eq_of_observable (f g : Candidates X Y)
    (hf : Exact X Y f) (hg : Exact X Y g)
    (hp : L.observable X f = L.observable X g) : f = g := by
  apply lp.ext
  funext n
  induction n with
  | zero => simpa only [observable_zero] using
      congrArg (fun a : Candidates X Y => a 0) hp
  | succ n ih =>
    have hn : L.innovation X f n = L.innovation X g n :=
      congrArg (fun a : Candidates X Y => a (n+1)) hp
    rw [L.exact_reconstruction X f hf n, L.exact_reconstruction X g hg n, ih, hn]

/-- Residual and observable together are injective coordinates on all candidates. -/
theorem residual_observable_injective (f g : Candidates X Y)
    (hd : differential X Y f = differential X Y g)
    (hp : L.observable X f = L.observable X g) : f = g := by
  have he : Exact X Y (f-g) := (exact_iff_differential_zero X Y _).mpr (by
    simp only [map_sub, hd, sub_self])
  have hz : Exact X Y (0 : Candidates X Y) :=
    (exact_iff_differential_zero X Y _).mpr (map_zero _)
  have hh : L.observable X (f-g) = L.observable X 0 := by
    simp only [map_sub, hp, sub_self, map_zero]
  exact sub_eq_zero.mp (L.exact_eq_of_observable X (f-g) 0 he hz hh)

variable (hgap : (L.bound : ℝ) * X.bound < 1)

@[simp] theorem innovation_correction (r : Residuals X Y) (n : ℕ) :
    L.innovation X (L.correction X hgap r) n = 0 := by
  ext x
  simp [innovation, rawCorrection_succ]

@[simp] theorem observable_correction (r : Residuals X Y) :
    L.observable X (L.correction X hgap r) = 0 := by
  apply lp.ext
  funext n
  cases n with
  | zero => rfl
  | succ n => exact L.innovation_correction X hgap r n

@[simp] theorem repair_preserves_observable (f : Candidates X Y) :
    L.observable X (L.repair X hgap f) = L.observable X f := by
  simp only [repair_apply, map_sub, observable_correction, sub_zero]

/-- All hypotheses, including semantic separation, are now derived from split towers. -/
def fullScheme : RepairDynamics.Scheme (differential X Y) (L.observable X) where
  correction := L.correction X hgap
  rate := 0
  rate_nonneg := le_rfl
  rate_lt_one := zero_lt_one
  preserve := L.observable_correction X hgap
  contract f := by simp

include hgap in
/-- Existence and uniqueness of exact repair with the full innovation profile fixed. -/
theorem unique_exact_repair (f : Candidates X Y) :
    ∃! g : Candidates X Y, Exact X Y g ∧ L.observable X g = L.observable X f := by
  refine ⟨L.repair X hgap f,
    ⟨L.repair_exact X hgap f, L.repair_preserves_observable X hgap f⟩, ?_⟩
  intro g hg
  exact L.exact_eq_of_observable X g (L.repair X hgap f) hg.1
    (L.repair_exact X hgap f)
    (hg.2.trans (L.repair_preserves_observable X hgap f).symm)

/-- Any valid repair engine for this same observable has the explicit projection. -/
theorem any_scheme_projection_eq
    (B : RepairDynamics.Scheme (differential X Y) (L.observable X)) :
    B.projection = L.repair X hgap := by
  apply ContinuousLinearMap.ext
  intro f
  exact L.exact_eq_of_observable X (B.projection f) (L.repair X hgap f)
    ((exact_iff_differential_zero X Y _).mpr (B.limit_exact f))
    (L.repair_exact X hgap f)
    ((B.limit_semantics f).trans (L.repair_preserves_observable X hgap f).symm)

include hgap in
/-- Every admissible semantic coordinate and every bounded residual have one candidate. -/
theorem unique_candidate_of_coordinates (s : Candidates X Y)
    (hs : L.observable X s = s) (r : Residuals X Y) :
    ∃! f : Candidates X Y, differential X Y f = r ∧ L.observable X f = s := by
  refine ⟨L.repair X hgap s + L.correction X hgap r, ?_, ?_⟩
  · constructor
    · simp only [map_add, repair_differential_zero, differential_correction, zero_add]
    · simp only [map_add, repair_preserves_observable, observable_correction, add_zero, hs]
  · intro f hf
    apply L.residual_observable_injective X
    · simpa only [map_add, repair_differential_zero, differential_correction, zero_add] using hf.1
    · simpa only [map_add, repair_preserves_observable, observable_correction, add_zero, hs] using hf.2

end Splitting
end BanachTower
end KomorebiSpace
end
