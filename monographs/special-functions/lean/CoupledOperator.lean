import CoupledScalarReduction
import Mathlib.Order.Filter.Germ.Basic
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-! # Autonomous linear projections of the coupled functional field -/

set_option autoImplicit false
set_option maxHeartbeats 2000000

noncomputable section
open Filter Set
open scoped Topology Matrix

namespace Komorebi.SpecialFunctions.Coupled.Scales

structure EntireInput where
  u : ℂ → ℂ
  v : ℂ → ℂ
  hu : Differentiable ℂ u
  hv : Differentiable ℂ v
  u_zero : u 0 = 0
  v_zero : v 0 = 0

structure LocalInput where
  u : ℂ → ℂ
  v : ℂ → ℂ
  hu : AnalyticAt ℂ u 0
  hv : AnalyticAt ℂ v 0
  u_zero : u 0 = 0
  v_zero : v 0 = 0

def EntireInput.toLocal (X : EntireInput) : LocalInput :=
  ⟨X.u, X.v, X.hu.analyticAt 0, X.hv.analyticAt 0, X.u_zero, X.v_zero⟩

def rowProjection (c : Fin 2 → ℂ) (u v : ℂ → ℂ) (z : ℂ) : ℂ :=
  c 0 * u z + c 1 * v z

def rowField (s : Scales) (c : Fin 2 → ℂ) (u v : ℂ → ℂ) (z : ℂ) : ℂ :=
  c 0 * (1 + u ((s.q : ℂ) * z) * v ((s.r : ℂ) * z)) +
    c 1 * (1 + u ((s.a : ℂ) * z) * v ((s.b : ℂ) * z))

def entireProjection (c : Fin 2 → ℂ) (X : EntireInput) : ℂ → ℂ :=
  rowProjection c X.u X.v

def entireField (s : Scales) (c : Fin 2 → ℂ) (X : EntireInput) : ℂ → ℂ :=
  s.rowField c X.u X.v

def Autonomous (s : Scales) (c : Fin 2 → ℂ) : Prop :=
  Function.FactorsThrough (s.entireField c) (entireProjection c)

theorem autonomous_iff_scalar_functional (s : Scales) (c : Fin 2 → ℂ) :
    s.Autonomous c ↔ ∃ H : (ℂ → ℂ) → (ℂ → ℂ),
      ∀ X : EntireInput, s.entireField c X = H (entireProjection c X) := by
  rw [Autonomous, Function.factorsThrough_iff]
  constructor
  · rintro ⟨H, hH⟩
    exact ⟨H, fun X => congrFun hH X⟩
  · rintro ⟨H, hH⟩
    exact ⟨H, funext hH⟩

def scaledInput (f : ℂ → ℂ) (hf : Differentiable ℂ f) (hzero : f 0 = 0)
    (x y : ℂ) : EntireInput :=
  ⟨fun z => x * f z, fun z => y * f z, hf.const_mul x, hf.const_mul y,
    by simp [hzero], by simp [hzero]⟩

def nodePolynomial (s : Scales) (z : ℂ) : ℂ :=
  1 - (1 - z / (s.q : ℂ)) * (1 - z / (s.r : ℂ)) *
    (1 - z / (s.a : ℂ)) * (1 - z / (s.b : ℂ))

theorem nodePolynomial_differentiable (s : Scales) :
    Differentiable ℂ s.nodePolynomial := by unfold nodePolynomial; fun_prop

theorem nodePolynomial_zero (s : Scales) : s.nodePolynomial 0 = 0 := by
  simp [nodePolynomial]

theorem nodePolynomial_values (s : Scales) (hs : s.positive) :
    s.nodePolynomial s.q = 1 ∧ s.nodePolynomial s.r = 1 ∧
      s.nodePolynomial s.a = 1 ∧ s.nodePolynomial s.b = 1 := by
  have hq : (s.q : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hs.1
  have hr : (s.r : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hs.2.1
  have ha : (s.a : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hs.2.2.1
  have hb : (s.b : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hs.2.2.2
  simp [nodePolynomial, hq, hr, ha, hb]

theorem autonomous_scalar_fibers (s : Scales) (c : Fin 2 → ℂ) (h : s.Autonomous c)
    {f : ℂ → ℂ} (hf : Differentiable ℂ f) (hz : f 0 = 0)
    (hn : f s.q = 1 ∧ f s.r = 1 ∧ f s.a = 1 ∧ f s.b = 1)
    {x y x' y' : ℂ} (he : c 0 * x + c 1 * y = c 0 * x' + c 1 * y') :
    (c 0 + c 1) * x * y = (c 0 + c 1) * x' * y' := by
  have hp : entireProjection c (scaledInput f hf hz x y) =
      entireProjection c (scaledInput f hf hz x' y') := by
    funext z
    dsimp [entireProjection, rowProjection, scaledInput]
    linear_combination f z * he
  have hh := congrFun (h hp) 1
  simp only [entireField, rowField, scaledInput, mul_one, hn.1, hn.2.1,
    hn.2.2.1, hn.2.2.2] at hh
  linear_combination hh

theorem autonomous_row_sum_zero (s : Scales) (hs : s.positive) (c : Fin 2 → ℂ)
    (h : s.Autonomous c) : c 0 + c 1 = 0 := by
  have hh : ∀ {x y x' y' : ℂ}, c 0 * x + c 1 * y = c 0 * x' + c 1 * y' →
      (c 0 + c 1) * x * y = (c 0 + c 1) * x' * y' :=
    s.autonomous_scalar_fibers c h s.nodePolynomial_differentiable
      s.nodePolynomial_zero (s.nodePolynomial_values hs)
  have h0 := hh (x := 0) (y := 0) (x' := c 1) (y' := -c 0) (by ring)
  have h1 := hh (x := 1) (y := 0) (x' := 1 + c 1) (y' := -c 0) (by ring)
  have h2 := hh (x := 0) (y := 1) (x' := c 1) (y' := 1 - c 0) (by ring)
  have hmul0 : (c 0 + c 1) * c 0 = 0 := by linear_combination h1 - h0
  have hmul1 : (c 0 + c 1) * c 1 = 0 := by linear_combination h0 - h2
  by_contra hsum
  have hc0 := (mul_eq_zero.mp hmul0).resolve_left hsum
  have hc1 := (mul_eq_zero.mp hmul1).resolve_left hsum
  exact hsum (by simp [hc0, hc1])

theorem nonzero_row_first_ne_zero {c : Fin 2 → ℂ} (hc : c ≠ 0)
    (hsum : c 0 + c 1 = 0) : c 0 ≠ 0 := by
  intro hz
  apply hc
  have hz1 : c 1 = 0 := by simpa [hz] using hsum
  funext i
  fin_cases i
  · exact hz
  · exact hz1

theorem autonomous_scale_products (s : Scales) (hs : s.positive) (c : Fin 2 → ℂ)
    (hc : c ≠ 0) (h : s.Autonomous c) :
    s.q * s.r = s.a * s.b ∧ s.q ^ 2 * s.r = s.a ^ 2 * s.b := by
  have hsum := s.autonomous_row_sum_zero hs c h
  have hc0 := nonzero_row_first_ne_zero hc hsum
  have hc1 : c 1 = -c 0 := by linear_combination hsum
  let X : EntireInput := ⟨fun z => z, fun z => z, by fun_prop, by fun_prop,
    by simp, by simp⟩
  let Z : EntireInput := ⟨fun _ => 0, fun _ => 0, by fun_prop, by fun_prop,
    by simp, by simp⟩
  have hp : entireProjection c X = entireProjection c Z := by
    funext z; dsimp [entireProjection, rowProjection, X, Z]; rw [hc1]; ring
  have hF := congrFun (h hp) 1
  dsimp [entireField, rowField, X, Z] at hF
  rw [hc1] at hF
  have he : c 0 * ((s.q : ℂ) * s.r - (s.a : ℂ) * s.b) = 0 := by
    linear_combination hF
  have hpC : (s.q : ℂ) * s.r = (s.a : ℂ) * s.b :=
    sub_eq_zero.mp ((mul_eq_zero.mp he).resolve_left hc0)
  have hpR : s.q * s.r = s.a * s.b := by exact_mod_cast hpC
  let Y : EntireInput := ⟨fun z => z ^ 2 + z, fun z => z, by fun_prop, by fun_prop,
    by simp, by simp⟩
  let W : EntireInput := ⟨fun z => z ^ 2, fun _ => 0, by fun_prop, by fun_prop,
    by simp, by simp⟩
  have hp2 : entireProjection c Y = entireProjection c W := by
    funext z; dsimp [entireProjection, rowProjection, Y, W]; rw [hc1]; ring
  have hF2 := congrFun (h hp2) 1
  dsimp [entireField, rowField, Y, W] at hF2
  rw [hc1] at hF2
  have he2 : c 0 * ((s.q : ℂ) ^ 2 * s.r - (s.a : ℂ) ^ 2 * s.b) = 0 := by
    linear_combination hF2 - c 0 * hpC
  have hp2C := sub_eq_zero.mp ((mul_eq_zero.mp he2).resolve_left hc0)
  exact ⟨hpR, by exact_mod_cast hp2C⟩

theorem autonomous_ordered_rows (s : Scales) (hs : s.positive) (c : Fin 2 → ℂ)
    (hc : c ≠ 0) (h : s.Autonomous c) : s.q = s.a ∧ s.r = s.b := by
  have hp := s.autonomous_scale_products hs c hc h
  have hm := congrArg (fun t : ℝ => s.a * t) hp.1
  have he : (s.q - s.a) * (s.q * s.r) = 0 := by nlinarith only [hp.2, hm]
  have hq := sub_eq_zero.mp ((mul_eq_zero.mp he).resolve_right
    (ne_of_gt (mul_pos hs.1 hs.2.1)))
  exact ⟨hq, mul_left_cancel₀ (ne_of_gt hs.1) (by simpa only [← hq] using hp.1)⟩

theorem ordered_rows_field_zero (s : Scales) (c : Fin 2 → ℂ)
    (hq : s.q = s.a) (hr : s.r = s.b) (hc : c 0 + c 1 = 0)
    (u v : ℂ → ℂ) : s.rowField c u v = 0 := by
  funext z
  dsimp [rowField]
  rw [hq, hr]
  calc
    _ = (c 0 + c 1) * (1 + u ((s.a : ℂ) * z) * v ((s.b : ℂ) * z)) := by ring
    _ = 0 := by rw [hc, zero_mul]

theorem ordered_rows_autonomous (s : Scales) (c : Fin 2 → ℂ)
    (hq : s.q = s.a) (hr : s.r = s.b) (hc : c 0 + c 1 = 0) : s.Autonomous c := by
  intro X Y _
  exact (s.ordered_rows_field_zero c hq hr hc X.u X.v).trans
    (s.ordered_rows_field_zero c hq hr hc Y.u Y.v).symm

theorem zero_row_autonomous (s : Scales) : s.Autonomous 0 := by
  intro X Y _
  ext z
  simp [entireField, rowField]

theorem autonomous_iff_zero_or_ordered (s : Scales) (hs : s.positive) (c : Fin 2 → ℂ) :
    s.Autonomous c ↔ c = 0 ∨ (s.q = s.a ∧ s.r = s.b ∧ c 0 + c 1 = 0) := by
  constructor
  · intro h
    by_cases hc : c = 0
    · exact Or.inl hc
    · exact Or.inr ⟨(s.autonomous_ordered_rows hs c hc h).1,
        (s.autonomous_ordered_rows hs c hc h).2, s.autonomous_row_sum_zero hs c h⟩
  · rintro (rfl | ⟨hq, hr, hc⟩)
    · exact s.zero_row_autonomous
    · exact s.ordered_rows_autonomous c hq hr hc

theorem autonomous_nonzero_classification (s : Scales) (hs : s.positive)
    (c : Fin 2 → ℂ) (hc : c ≠ 0) :
    s.Autonomous c ↔ s.q = s.a ∧ s.r = s.b ∧ ∃ γ : ℂ, γ ≠ 0 ∧ c = ![γ, -γ] := by
  constructor
  · intro h
    have hsum := s.autonomous_row_sum_zero hs c h
    have hr := s.autonomous_ordered_rows hs c hc h
    refine ⟨hr.1, hr.2, c 0, nonzero_row_first_ne_zero hc hsum, ?_⟩
    funext i
    fin_cases i
    · rfl
    · change c 1 = -c 0
      linear_combination hsum
  · rintro ⟨hq, hr, γ, _, rfl⟩
    exact s.ordered_rows_autonomous ![γ, -γ] hq hr (by simp)

theorem autonomous_projected_field_zero (s : Scales) (hs : s.positive)
    (c : Fin 2 → ℂ) (h : s.Autonomous c) (u v : ℂ → ℂ) : s.rowField c u v = 0 := by
  rcases (s.autonomous_iff_zero_or_ordered hs c).mp h with rfl | ⟨hq, hr, hc⟩
  · ext z; simp [rowField]
  · exact s.ordered_rows_field_zero c hq hr hc u v

theorem no_nonzero_autonomous_if_rows_differ (s : Scales) (hs : s.positive)
    (hne : ¬(s.q = s.a ∧ s.r = s.b)) (c : Fin 2 → ℂ) (hc : c ≠ 0) :
    ¬s.Autonomous c := fun h => hne (s.autonomous_ordered_rows hs c hc h)

theorem autonomous_matrix_det_zero (s : Scales) (hs : s.positive)
    (P : Matrix (Fin 2) (Fin 2) ℂ) (h : ∀ i, s.Autonomous (P i)) : P.det = 0 := by
  have h0 := s.autonomous_row_sum_zero hs (P 0) (h 0)
  have h1 := s.autonomous_row_sum_zero hs (P 1) (h 1)
  rw [Matrix.det_fin_two]
  linear_combination P 0 0 * h1 - P 1 0 * h0

theorem no_invertible_constant_decoupling (s : Scales) (hs : s.positive)
    (P : Matrix (Fin 2) (Fin 2) ℂ) (hP : IsUnit P) : ¬∀ i, s.Autonomous (P i) := by
  intro h
  exact ((Matrix.isUnit_iff_isUnit_det P).mp hP).ne_zero (s.autonomous_matrix_det_zero hs P h)

abbrev ScalarGerm := Germ (𝓝 (0 : ℂ)) ℂ

def localProjection (c : Fin 2 → ℂ) (X : LocalInput) : ScalarGerm :=
  (rowProjection c X.u X.v : ℂ → ℂ)

def localField (s : Scales) (c : Fin 2 → ℂ) (X : LocalInput) : ScalarGerm :=
  (s.rowField c X.u X.v : ℂ → ℂ)

def GermAutonomous (s : Scales) (c : Fin 2 → ℂ) : Prop :=
  Function.FactorsThrough (s.localField c) (localProjection c)

theorem local_projection_analytic (c : Fin 2 → ℂ) (X : LocalInput) :
    AnalyticAt ℂ (rowProjection c X.u X.v) 0 := by
  exact (analyticAt_const.mul X.hu).add (analyticAt_const.mul X.hv)

theorem local_field_analytic (s : Scales) (c : Fin 2 → ℂ) (X : LocalInput) :
    AnalyticAt ℂ (s.rowField c X.u X.v) 0 := by
  have hq := analytic_scale_at_zero X.hu (s.q : ℂ)
  have hr := analytic_scale_at_zero X.hv (s.r : ℂ)
  have ha := analytic_scale_at_zero X.hu (s.a : ℂ)
  have hb := analytic_scale_at_zero X.hv (s.b : ℂ)
  exact (analyticAt_const.mul (analyticAt_const.add (hq.mul hr))).add
    (analyticAt_const.mul (analyticAt_const.add (ha.mul hb)))

theorem local_field_respects_component_germs (s : Scales) (c : Fin 2 → ℂ)
    (X Y : LocalInput) (hu : X.u =ᶠ[𝓝 (0 : ℂ)] Y.u)
    (hv : X.v =ᶠ[𝓝 (0 : ℂ)] Y.v) : s.localField c X = s.localField c Y := by
  apply Germ.coe_eq.mpr
  have ht (p : ℂ) : Tendsto (fun z : ℂ => p * z) (𝓝 0) (𝓝 0) := by
    have hp : Continuous (fun z : ℂ => p * z) := by fun_prop
    simpa only [mul_zero] using hp.tendsto (0 : ℂ)
  have hq := hu.comp_tendsto (ht (s.q : ℂ))
  have hr := hv.comp_tendsto (ht (s.r : ℂ))
  have ha := hu.comp_tendsto (ht (s.a : ℂ))
  have hb := hv.comp_tendsto (ht (s.b : ℂ))
  filter_upwards [hq, hr, ha, hb] with z hq hr ha hb
  simp only [Function.comp_apply] at hq hr ha hb
  simp only [rowField, hq, hr, ha, hb]

theorem germ_autonomous_iff_scalar_functional (s : Scales) (c : Fin 2 → ℂ) :
    s.GermAutonomous c ↔ ∃ H : ScalarGerm → ScalarGerm,
      ∀ X : LocalInput, s.localField c X = H (localProjection c X) := by
  rw [GermAutonomous, Function.factorsThrough_iff]
  constructor
  · rintro ⟨H, hH⟩
    exact ⟨H, fun X => congrFun hH X⟩
  · rintro ⟨H, hH⟩
    exact ⟨H, funext hH⟩

theorem entire_field_differentiable (s : Scales) (c : Fin 2 → ℂ) (X : EntireInput) :
    Differentiable ℂ (s.entireField c X) := by
  change Differentiable ℂ (fun z =>
    c 0 * (1 + X.u ((s.q : ℂ) * z) * X.v ((s.r : ℂ) * z)) +
    c 1 * (1 + X.u ((s.a : ℂ) * z) * X.v ((s.b : ℂ) * z)))
  have hu := X.hu
  have hv := X.hv
  fun_prop

theorem germ_autonomous_implies_entire (s : Scales) (c : Fin 2 → ℂ)
    (h : s.GermAutonomous c) : s.Autonomous c := by
  intro X Y hp
  have hpG : localProjection c X.toLocal = localProjection c Y.toLocal := by
    exact congrArg (fun f : ℂ → ℂ => (f : ScalarGerm)) hp
  have hG := h hpG
  have he : s.entireField c X =ᶠ[𝓝 (0 : ℂ)] s.entireField c Y := Germ.coe_eq.mp hG
  have hX : AnalyticOnNhd ℂ (s.entireField c X) univ :=
    fun z _ => (s.entire_field_differentiable c X).analyticAt z
  have hY : AnalyticOnNhd ℂ (s.entireField c Y) univ :=
    fun z _ => (s.entire_field_differentiable c Y).analyticAt z
  exact hX.eq_of_eventuallyEq hY he

theorem germ_autonomous_iff_entire (s : Scales) (hs : s.positive) (c : Fin 2 → ℂ) :
    s.GermAutonomous c ↔ s.Autonomous c := by
  refine ⟨s.germ_autonomous_implies_entire c, ?_⟩
  intro h X Y _
  have hX := s.autonomous_projected_field_zero hs c h X.u X.v
  have hY := s.autonomous_projected_field_zero hs c h Y.u Y.v
  exact congrArg (fun f : ℂ → ℂ => (f : ScalarGerm)) (hX.trans hY.symm)

theorem germ_autonomous_nonzero_classification (s : Scales) (hs : s.positive)
    (c : Fin 2 → ℂ) (hc : c ≠ 0) :
    s.GermAutonomous c ↔ s.q = s.a ∧ s.r = s.b ∧ ∃ γ : ℂ, γ ≠ 0 ∧ c = ![γ, -γ] := by
  rw [s.germ_autonomous_iff_entire hs c, s.autonomous_nonzero_classification hs c hc]

theorem no_invertible_constant_germ_decoupling (s : Scales) (hs : s.positive)
    (P : Matrix (Fin 2) (Fin 2) ℂ) (hP : IsUnit P) : ¬∀ i, s.GermAutonomous (P i) := by
  intro h
  exact s.no_invertible_constant_decoupling hs P hP
    (fun i => s.germ_autonomous_implies_entire (P i) (h i))

end Komorebi.SpecialFunctions.Coupled.Scales
