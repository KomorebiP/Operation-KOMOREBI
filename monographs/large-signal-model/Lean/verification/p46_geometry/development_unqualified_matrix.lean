import KomorebiLSM.RotationDensity
import KomorebiLSM.LorentzBaseNorm
import KomorebiLSM.PositiveLiftTopology
import KomorebiLSM.RotationRank
import Mathlib.Analysis.Convex.Strict.Extreme
import Mathlib.Analysis.InnerProductSpace.Convex
import Mathlib.Analysis.Normed.Module.Convex

set_option autoImplicit false
namespace Komorebi.LSM.RotationConeGeometry
open Set Metric
open RotationDensity

/-- Distinct forward times give distinct actual rational rotations. -/
theorem rotation_power_injective : Function.Injective (fun n : ℕ => rotation ^ n) := by
  apply injective_pow_iff_not_isOfFinOrder.mpr
  intro h
  obtain ⟨n, hn, he⟩ := h.exists_pow_eq_one
  exact rotation_pow_ne_one n hn he

/-- The unit disk cannot be the convex hull of finitely many complex points. -/
theorem disk_not_finite_convex_hull (s : Finset ℂ) :
    convexHull ℝ (s : Set ℂ) ≠ closedBall 0 1 := by
  intro he
  have hi : Function.Injective (fun n : ℕ => ((rotation ^ n : Circle) : ℂ)) :=
    Subtype.val_injective.comp rotation_power_injective
  have hinf := Set.infinite_range_of_injective hi
  have hsub : Set.range (fun n : ℕ => ((rotation ^ n : Circle) : ℂ)) ⊆ (s : Set ℂ) := by
    rintro x ⟨n, rfl⟩
    apply (extremePoints_convexHull_subset (𝕜 := ℝ) (A := (s : Set ℂ)))
    rw [he, StrictConvexSpace.extremePoints_closedBall_eq_sphere]
    simp
  exact hinf (s.finite_toSet.subset hsub)

/-- Dense forward rotated observations detect the full Euclidean radius. -/
theorem norm_le_of_rotated_re_le (w : ℂ) (t : ℝ)
    (h : ∀ n : ℕ, (((rotation ^ n : Circle) : ℂ) * w).re ≤ t) : ‖w‖ ≤ t := by
  have hall : ∀ u : Circle, ((u : ℂ) * w).re ≤ t := by
    intro u
    exact rotation_forward_dense.induction_on (p := fun u : Circle => ((u : ℂ) * w).re ≤ t) u
      (isClosed_le (by fun_prop) continuous_const) h
  by_cases hw : w = 0
  · simpa [hw] using hall 1
  · have hn : 0 < ‖w‖ := norm_pos_iff.mpr hw
    let u : Circle := ⟨(star w) / (‖w‖ : ℂ), by
      apply mem_sphere_zero_iff_norm.mpr
      simp [ne_of_gt hn]⟩
    have he : ((u : ℂ) * w).re = ‖w‖ := by
      change (((star w) / (‖w‖ : ℂ)) * w).re = ‖w‖
      simp only [Complex.mul_re, Complex.div_ofReal_re, Complex.div_ofReal_im,
        Complex.star_def, Complex.conj_re, Complex.conj_im]
      have hsq := Complex.normSq_eq_norm_sq w
      rw [Complex.normSq_apply] at hsq
      field_simp
      nlinarith
    simpa [he] using hall u



open RotationModel FiniteInstruments
open LorentzBaseNorm (spatial point)

/-- Complex multiplication is precisely the displayed rational spatial rotation. -/
theorem spatial_rotate (z : RotationModel.State) :
    spatial (rotate z) = (rotation : ℂ) * spatial z := by
  apply Complex.ext <;> simp [Complex.mul_re, Complex.mul_im]
  ring

/-- The chronological word consisting of n forward rotate branches. -/
def rotationWord (n : ℕ) : List (Bool × Bool) := List.replicate n (false,false)

@[simp] theorem rotationWord_zero : rotationWord 0 = [] := rfl
@[simp] theorem rotationWord_succ (n : ℕ) :
    rotationWord (n+1) = (false,false)::rotationWord n := rfl

theorem rotationWord_mass (n : ℕ) (z : RotationModel.State) :
    RotationModel.mass (wordAction operator (rotationWord n) z) = z 0 := by
  induction n generalizing z with
  | zero => simp [rotationWord]
  | succ n ih =>
    simp only [rotationWord_succ,wordAction_cons,LinearMap.comp_apply,operator_rotate0]
    rw [ih,rotate_zero]

theorem rotationWord_spatial (n : ℕ) (z : RotationModel.State) :
    spatial (wordAction operator (rotationWord n) z) = ((rotation^n : Circle) : ℂ) * spatial z := by
  induction n generalizing z with
  | zero => simp [rotationWord]
  | succ n ih =>
    simp only [rotationWord_succ,wordAction_cons,LinearMap.comp_apply,operator_rotate0]
    rw [ih,spatial_rotate]
    simp only [pow_succ,Circle.coe_mul]
    ring

theorem rotationWord_initial (n : ℕ) :
    wordAction operator (rotationWord n) initial = point 1 ((rotation^n : Circle) : ℂ) := by
  rw [← LorentzBaseNorm.point_mass_spatial (wordAction operator (rotationWord n) initial)]
  have hm := rotationWord_mass n initial
  have hs := rotationWord_spatial n initial
  change (wordAction operator (rotationWord n) initial) 0 = 1 at hm
  rw [hm,hs]
  have hi : spatial initial = (1 : ℂ) := rfl
  rw [hi,mul_one]

/-- Every all-test nonnegative state satisfies all rotated probe effects. -/
theorem allTests_rotated_probe_bound {z : RotationModel.State}
    (hz : z ∈ TestDomains.allTests operator RotationModel.mass) (n : ℕ) :
    (((rotation^n : Circle) : ℂ) * spatial z).re ≤ z 0 := by
  have hp := hz (rotationWord n ++ [(true,true)])
  change 0 ≤ RotationModel.mass (wordAction operator (rotationWord n ++ [(true,true)]) z) at hp
  simp only [wordAction_append,LinearMap.comp_apply,wordAction_cons,wordAction_nil,
    LinearMap.id_comp,operator_probe1] at hp
  rw [probe1_apply,map_smul,initial_mass,smul_eq_mul,mul_one] at hp
  have hm := rotationWord_mass n z
  change (wordAction operator (rotationWord n) z) 0 = z 0 at hm
  have hs := congrArg Complex.re (rotationWord_spatial n z)
  simp only [LorentzBaseNorm.spatial_apply_re] at hs
  rw [← hs]
  linarith

/-- The exact model's canonical all-future-test cone is the Lorentz cone. -/
theorem canonical_cone_eq : TestDomains.allTests operator RotationModel.mass = RotationModel.cone := by
  apply Set.Subset.antisymm
  · intro z hz
    apply (LorentzBaseNorm.cone_iff_norm z).mpr
    exact norm_le_of_rotated_re_le (spatial z) (z 0) (allTests_rotated_probe_bound hz)
  · intro z hz w
    exact all_word_mass_nonneg w hz

/-- A fixed unit-mass slice is affine in its complex spatial coordinate. -/
theorem point_one_convex {C : Set RotationModel.State} (hc : Convex ℝ C) :
    Convex ℝ {w : ℂ | point 1 w ∈ C} := by
  intro w hw v hv a b ha hb hab
  change point 1 (a • w + b • v) ∈ C
  have he : point 1 (a • w + b • v) = a • point 1 w + b • point 1 v := by
    funext i
    fin_cases i <;> simp [LorentzBaseNorm.point,smul_eq_mul,hab]
  rw [he]
  exact hc hw hv ha hb hab

/-- Closedness extends actual reachable forward powers to every boundary point. -/
theorem unit_boundary_mem {C : Set RotationModel.State}
    (hclosed : IsClosed C) (hinit : initial ∈ C)
    (hinv : ∀ z ∈ C, rotate z ∈ C) (u : Circle) : point 1 (u : ℂ) ∈ C := by
  have horbit : ∀ n, point 1 ((rotation^n : Circle) : ℂ) ∈ C := by
    intro n
    rw [← rotationWord_initial]
    induction n with
    | zero => simpa [rotationWord] using hinit
    | succ n ih =>
      rw [show rotationWord (n+1)=rotationWord n ++ [(false,false)] by
        exact List.replicate_succ']
      simpa only [wordAction_append,wordAction_cons,wordAction_nil,LinearMap.id_comp,
        LinearMap.comp_apply,operator_rotate0] using hinv _ ih
  have hcont : Continuous (fun u : Circle => point 1 (u : ℂ)) := by
    apply continuous_pi
    intro i
    fin_cases i
    · change Continuous (fun _ : Circle => (1 : ℝ)); fun_prop
    · change Continuous (fun u : Circle => (u : ℂ).re); fun_prop
    · change Continuous (fun u : Circle => (u : ℂ).im); fun_prop
  exact rotation_forward_dense.induction_on (p := fun u : Circle => point 1 (u : ℂ) ∈ C)
    u (hclosed.preimage hcont) horbit

/-- Convexity fills the disk once its entire reachable boundary is present. -/
theorem unit_disk_mem {C : Set RotationModel.State}
    (hclosed : IsClosed C) (hconvex : Convex ℝ C) (hinit : initial ∈ C)
    (hinv : ∀ z ∈ C, rotate z ∈ C) (w : ℂ) (hw : ‖w‖ ≤ 1) : point 1 w ∈ C := by
  have hb : sphere (0 : ℂ) 1 ⊆ {w : ℂ | point 1 w ∈ C} := by
    intro v hv
    exact unit_boundary_mem hclosed hinit hinv ⟨v,hv⟩
  have hh := convexHull_min hb (point_one_convex hconvex)
  rw [convexHull_sphere_eq_closedBall (0 : ℂ) (by norm_num : (0 : ℝ) ≤ 1)] at hh
  exact hh (by simpa only [mem_closedBall,dist_zero_right] using hw)

/-- A closed convex conical set containing the exact rotation orbit contains
all Lorentz-positive states, including its zero-mass boundary. -/
theorem lorentz_subset_of_closed_invariant {C : Set RotationModel.State}
    (hclosed : IsClosed C) (hconvex : Convex ℝ C)
    (hscale : ∀ a : ℝ, 0 ≤ a → ∀ z ∈ C, a • z ∈ C)
    (hinit : initial ∈ C) (hinv : ∀ z ∈ C, rotate z ∈ C) : RotationModel.cone ⊆ C := by
  intro z hz
  have hn := (LorentzBaseNorm.cone_iff_norm z).mp hz
  have ht : 0 ≤ z 0 := (norm_nonneg (spatial z)).trans hn
  by_cases hzero : z 0 = 0
  · have hs : spatial z = 0 := norm_eq_zero.mp (le_antisymm (by simpa [hzero] using hn) (norm_nonneg _))
    have he : z = 0 := LorentzBaseNorm.spatial_eq_zero_and_mass_eq_zero hs hzero
    rw [he]
    simpa using hscale 0 (by norm_num) initial hinit
  · have htpos : 0 < z 0 := lt_of_le_of_ne ht (Ne.symm hzero)
    have hw : ‖spatial z / (z 0 : ℂ)‖ ≤ 1 := by
      rw [norm_div,Complex.norm_real,Real.norm_eq_abs,abs_of_pos htpos]
      exact (div_le_one htpos).mpr hn
    have hm := hscale (z 0) ht (point 1 (spatial z / (z 0 : ℂ)))
      (unit_disk_mem hclosed hconvex hinit hinv _ hw)
    have he : (z 0) • point 1 (spatial z / (z 0 : ℂ)) = z := by
      rw [← LorentzBaseNorm.point_mass_spatial z]
      funext i
      fin_cases i <;> simp [LorentzBaseNorm.point,Pi.smul_apply,smul_eq_mul]
      all_goals field_simp [hzero]
    simpa only [he] using hm

/-- Nonnegative mass on every invariant branch forces the reverse inclusion.
Together with reachability and closure the probability cone is unique. -/
theorem invariant_probability_cone_unique {C : Set RotationModel.State}
    (hclosed : IsClosed C) (hconvex : Convex ℝ C)
    (hscale : ∀ a : ℝ, 0 ≤ a → ∀ z ∈ C, a • z ∈ C)
    (hinit : initial ∈ C) (hmass : ∀ z ∈ C, 0 ≤ RotationModel.mass z)
    (hinv : ∀ s z, z ∈ C → operator s z ∈ C) : C = RotationModel.cone := by
  apply Set.Subset.antisymm
  · rw [← canonical_cone_eq]
    exact TestDomains.allTests_greatest operator RotationModel.mass C hmass hinv
  · exact lorentz_subset_of_closed_invariant hclosed hconvex hscale hinit
      (fun z hz => by simpa only [operator_rotate0] using hinv (false,false) z hz)

/-- The normalized base of any such finite synthesis would project to the disk. -/
theorem spatial_normalizedHull_eq_disk {J : Type*} [Fintype J] [DecidableEq J]
    (V : (J → ℝ) →ₗ[ℝ] RotationModel.State)
    (he : PositiveLift.hull V = RotationModel.cone) :
    spatial '' PositiveLift.normalizedHull V RotationModel.mass = closedBall 0 1 := by
  ext w
  constructor
  · rintro ⟨z,⟨hz,hm⟩,rfl⟩
    rw [he] at hz
    have hb := (LorentzBaseNorm.cone_iff_norm z).mp hz
    change z 0 = 1 at hm
    simpa only [mem_closedBall,dist_zero_right,hm] using hb
  · intro hw
    refine ⟨point 1 w,⟨?_,?_⟩,by simp⟩
    · rw [he]
      apply (LorentzBaseNorm.cone_iff_norm _).mpr
      simpa only [LorentzBaseNorm.spatial_point,LorentzBaseNorm.point_zero,
        mem_closedBall,dist_zero_right] using hw
    · simp

/-- No finite normalized positive-generator certificate exists for the exact
rational model. Redundant generators are covered as well. -/
theorem no_finite_normalized_generator_certificate {J : Type*} [Fintype J] [DecidableEq J]
    (V : (J → ℝ) →ₗ[ℝ] RotationModel.State)
    (hn : RotationModel.mass.comp V = FiniteInstruments.mass)
    (hinit : initial ∈ PositiveLift.hull V)
    (hinv : ∀ s z, z ∈ PositiveLift.hull V → operator s z ∈ PositiveLift.hull V) : False := by
  have he := invariant_probability_cone_unique
    (PositiveLift.hull_closed V RotationModel.mass hn) (PositiveLift.hull_convex V)
    (fun a ha z hz => PositiveLift.hull_smul V ha hz) hinit
    (fun z hz => PositiveLift.hull_mass_nonneg V RotationModel.mass hn hz) hinv
  have hb := spatial_normalizedHull_eq_disk V he
  rw [PositiveLift.normalizedHull_eq_convexHull V RotationModel.mass hn,
    spatial.image_convexHull] at hb
  let s : Finset ℂ := Finset.univ.image (fun j => spatial (PositiveLift.generator V j))
  have hs : (s : Set ℂ) = spatial '' Set.range (PositiveLift.generator V) := by
    ext w
    simp [s]
  exact disk_not_finite_convex_hull s (by rw [hs]; exact hb)

/-- Collected P46 conclusions for the actual rational process. The finite
certificate obstruction allows every finite generator type and redundant maps. -/
theorem rational_rank_three_obstruction {J : Type*} [Fintype J] [DecidableEq J] :
    (∀ s, ∃ M : Matrix (Fin 3) (Fin 3) ℚ, M.map (algebraMap ℚ ℝ) = matrix s) ∧
    Behavior.CausalLaw process ∧
    TestDomains.allTests operator RotationModel.mass = RotationModel.cone ∧
    Module.finrank ℝ (Behavior.space process) = 3 ∧
    (∀ C : Set RotationModel.State, IsClosed C → Convex ℝ C →
      (∀ a : ℝ, 0 ≤ a → ∀ z ∈ C, a • z ∈ C) → initial ∈ C →
      (∀ z ∈ C, 0 ≤ RotationModel.mass z) →
      (∀ s z, z ∈ C → operator s z ∈ C) → C = RotationModel.cone) ∧
    ¬ ∃ V : (J → ℝ) →ₗ[ℝ] RotationModel.State,
      RotationModel.mass.comp V = FiniteInstruments.mass ∧
      initial ∈ PositiveLift.hull V ∧
      ∀ s z, z ∈ PositiveLift.hull V → operator s z ∈ PositiveLift.hull V := by
  refine ⟨matrix_is_rational, process_causal, canonical_cone_eq,
    behavior_dimension_three, ?_, ?_⟩
  · intro C hc hv hs hi hm hb
    exact invariant_probability_cone_unique hc hv hs hi hm hb
  · rintro ⟨V,hn,hi,hb⟩
    exact no_finite_normalized_generator_certificate V hn hi hb

end Komorebi.LSM.RotationConeGeometry
