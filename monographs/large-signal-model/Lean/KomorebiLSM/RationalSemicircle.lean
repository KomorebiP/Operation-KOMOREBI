import KomorebiLSM.RobustOrientedMargin
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.Normed.Module.Convex

/-! The two literal rational circle charts and the oriented full-disk consequence. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalSemicircle
open LorentzCylinder RobustOrientedMargin
noncomputable section

/-- The strictly positive denominator shared by both semicircles. -/
def denominator (t : ℝ) : ℝ := 1+t^2

theorem denominator_pos (t : ℝ) : 0<denominator t := by
  unfold denominator
  positivity

/-- `false` is the right semicircle and `true` its antipodal left semicircle. -/
def numerator (left : Bool) (t : ℝ) : ℂ :=
  if left then ⟨-(1-t^2),-(2*t)⟩ else ⟨1-t^2,2*t⟩

def chart (left : Bool) (t : ℝ) : ℂ := (denominator t)⁻¹ • numerator left t

def lift (left : Bool) (t : ℝ) : State ℂ := (denominator t,numerator left t)

theorem lift_eq (left : Bool) (t : ℝ) :
    lift left t=denominator t • (1,chart left t) := by
  apply Prod.ext
  · simp [lift]
  · change numerator left t=denominator t • ((denominator t)⁻¹ • numerator left t)
    rw [smul_smul,mul_inv_cancel₀ (denominator_pos t).ne',one_smul]

theorem chart_norm (left : Bool) (t : ℝ) : ‖chart left t‖=1 := by
  have hn : Complex.normSq (numerator left t)=(denominator t)^2 := by
    cases left <;> simp [numerator,Complex.normSq_apply,denominator] <;> ring
  have hsq : ‖chart left t‖^2=1 := by
    rw [chart,norm_smul,Real.norm_eq_abs,abs_of_pos (inv_pos.mpr (denominator_pos t)),
      mul_pow,← Complex.normSq_eq_norm_sq,hn]
    field_simp [(denominator_pos t).ne']
  nlinarith [norm_nonneg (chart left t)]

/-- The inverse stereographic coordinate is bounded on the entire right semicircle. -/
theorem right_chart_surjective (z : ℂ) (hz : ‖z‖=1) (hre : 0≤z.re) :
    ∃ t∈Set.Icc (-1 : ℝ) 1,chart false t=z := by
  have hs : z.re^2+z.im^2=1 := by
    have h := Complex.normSq_eq_norm_sq z
    rw [hz] at h
    simpa [Complex.normSq_apply,pow_two] using h
  have hi : |z.im|≤1 := by
    apply (sq_le_sq₀ (abs_nonneg _) (by norm_num : (0:ℝ)≤1)).mp
    rw [sq_abs]
    nlinarith [sq_nonneg z.re]
  have hd : 0<1+z.re := by linarith
  let t : ℝ := z.im/(1+z.re)
  have ht : t∈Set.Icc (-1 : ℝ) 1 := by
    dsimp [t]
    constructor
    · apply (le_div_iff₀ hd).mpr
      have := neg_abs_le z.im
      linarith
    · apply (div_le_iff₀ hd).mpr
      have := le_abs_self z.im
      linarith
  refine ⟨t,ht,?_⟩
  apply Complex.ext
  · simp [chart,numerator,Complex.real_smul]
    dsimp [t,denominator]
    field_simp
    linear_combination -(1+z.re)*hs
  · simp [chart,numerator,Complex.real_smul]
    dsimp [t,denominator]
    field_simp
    linear_combination -z.im*hs

/-- Both signs, including their endpoints, cover the actual unit circle. -/
theorem charts_cover (z : ℂ) (hz : ‖z‖=1) :
    ∃ left : Bool,∃ t∈Set.Icc (-1 : ℝ) 1,chart left t=z := by
  by_cases h : 0≤z.re
  · obtain ⟨t,ht,he⟩ := right_chart_surjective z hz h
    exact ⟨false,t,ht,he⟩
  · obtain ⟨t,ht,he⟩ := right_chart_surjective (-z) (by simpa using hz) (by simp; linarith)
    refine ⟨true,t,ht,?_⟩
    have heq : chart true t= -chart false t := by
      unfold chart
      rw [← smul_neg]
      congr 1
    rw [heq,he,neg_neg]

/-- Literal polynomial orientation and squared-spatial tests, with no square roots. -/
def orientation (F : State ℂ →L[ℝ] State ℂ) (kappa : ℝ) (left : Bool) (t : ℝ) : ℝ :=
  (F (lift left t)).1-kappa*denominator t

def squareGap (F : State ℂ →L[ℝ] State ℂ) (kappa : ℝ) (left : Bool) (t : ℝ) : ℝ :=
  (orientation F kappa left t)^2-(F (lift left t)).2.re^2-(F (lift left t)).2.im^2

theorem chart_slack (F : State ℂ →L[ℝ] State ℂ) (kappa : ℝ)
    (left : Bool) (t : ℝ) (hf : 0≤orientation F kappa left t)
    (hh : 0≤squareGap F kappa left t) : kappa≤slack (F (1,chart left t)) := by
  have hs : ‖(F (lift left t)).2‖^2≤(orientation F kappa left t)^2 := by
    rw [← Complex.normSq_eq_norm_sq,Complex.normSq_apply]
    unfold squareGap at hh
    linarith
  have hn : ‖(F (lift left t)).2‖≤orientation F kappa left t :=
    (sq_le_sq₀ (norm_nonneg _) hf).mp hs
  unfold orientation at hn
  rw [lift_eq,map_smul] at hn
  change ‖denominator t • (F (1,chart left t)).2‖≤
    (denominator t • F (1,chart left t)).1-kappa*denominator t at hn
  rw [norm_smul,Real.norm_eq_abs,abs_of_pos (denominator_pos t)] at hn
  change kappa≤(F (1,chart left t)).1-‖(F (1,chart left t)).2‖
  change denominator t*‖(F (1,chart left t)).2‖≤
    denominator t*(F (1,chart left t)).1-kappa*denominator t at hn
  nlinarith [denominator_pos t]

/-- The superlevel is convex because output mass is affine and output norm is convex. -/
theorem convex_slack_superlevel (F : State ℂ →L[ℝ] State ℂ) (kappa : ℝ) :
    Convex ℝ {v : ℂ | kappa≤slack (F (1,v))} := by
  intro v hv w hw a b ha hb hab
  have he : ((1 : ℝ),a • v+b • w)=(a : ℝ) • ((1 : ℝ),v)+b • ((1 : ℝ),w) := by
    apply Prod.ext <;> simp [hab]
  change kappa≤slack (F (1,a • v+b • w))
  rw [he,map_add,map_smul,map_smul]
  have hn := norm_add_le (a • (F (1,v)).2) (b • (F (1,w)).2)
  rw [norm_smul,norm_smul,Real.norm_eq_abs,Real.norm_eq_abs,abs_of_nonneg ha,
    abs_of_nonneg hb] at hn
  change kappa≤(a*(F (1,v)).1+b*(F (1,w)).1)-‖a • (F (1,v)).2+b • (F (1,w)).2‖
  dsimp [slack] at hv hw
  have hk : a*kappa+b*kappa=kappa := by rw [← add_mul,hab,one_mul]
  nlinarith [mul_nonneg ha (sub_nonneg.mpr hv),mul_nonneg hb (sub_nonneg.mpr hw)]

/-- The circle inequalities extend to the full closed disk, not a sampled boundary. -/
theorem disk_slack_of_charts (F : State ℂ →L[ℝ] State ℂ) (kappa : ℝ)
    (hf : ∀ left t,t∈Set.Icc (-1 : ℝ) 1 → 0≤orientation F kappa left t)
    (hh : ∀ left t,t∈Set.Icc (-1 : ℝ) 1 → 0≤squareGap F kappa left t)
    (v : ℂ) (hv : ‖v‖≤1) : kappa≤slack (F (1,v)) := by
  have hs : Metric.sphere (0 : ℂ) 1⊆{v : ℂ | kappa≤slack (F (1,v))} := by
    intro z hz
    have hz1 : ‖z‖=1 := by simpa using hz
    obtain ⟨left,t,ht,he⟩ := charts_cover z hz1
    rw [← he]
    exact chart_slack F kappa left t (hf left t ht) (hh left t ht)
  have h := convexHull_min hs (convex_slack_superlevel F kappa)
  rw [convexHull_sphere_eq_closedBall (0 : ℂ) (by norm_num : (0:ℝ)≤1)] at h
  exact h (by simpa using hv)

/-- P75's conclusion uses the actual attained minimum from P71. -/
theorem margin_of_charts (F : State ℂ →L[ℝ] State ℂ) (kappa : ℝ)
    (hf : ∀ left t,t∈Set.Icc (-1 : ℝ) 1 → 0≤orientation F kappa left t)
    (hh : ∀ left t,t∈Set.Icc (-1 : ℝ) 1 → 0≤squareGap F kappa left t) : kappa≤sigma F :=
  (le_sigma_iff F kappa).mpr (disk_slack_of_charts F kappa hf hh)

end
end Komorebi.LSM.RationalSemicircle
