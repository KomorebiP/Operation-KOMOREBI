import CoupledGermInverse

/-! # Component rescaling for the canonical coupled functions

Complex rescalings are allowed in the obstruction direction. The converse
uses the positive real square root and a normalized scalar entire solution.
-/

set_option autoImplicit false
set_option maxHeartbeats 1500000

noncomputable section

open Filter
open scoped Topology

namespace Komorebi.SpecialFunctions.Coupled.Scales

def denseOddComplex (c : ℕ → ℂ) (k : ℕ) : ℂ :=
  if k % 2 = 1 then c (k / 2) else 0

theorem denseOddComplex_odd (c : ℕ → ℂ) (n : ℕ) :
    denseOddComplex c (2 * n + 1) = c n := by
  have hm : (2 * n + 1) % 2 = 1 := by omega
  have hd : (2 * n + 1) / 2 = n := by omega
  simp [denseOddComplex, hm, hd]

theorem complex_odd_series_hasFPowerSeriesAt {c : ℕ → ℂ} {f : ℂ → ℂ}
    (h : ∀ᶠ z in 𝓝 (0 : ℂ), HasSum (fun n => c n * z ^ (2 * n + 1)) (f z)) :
    HasFPowerSeriesAt f (FormalMultilinearSeries.ofScalars ℂ (denseOddComplex c)) 0 := by
  apply hasFPowerSeriesAt_iff.mpr
  filter_upwards [h] with z hz
  have hi : Function.Injective (fun n : ℕ => 2 * n + 1) := by
    intro a b hab
    change 2 * a + 1 = 2 * b + 1 at hab
    omega
  have hsum : HasSum (fun k => denseOddComplex c k * z ^ k) (f z) := by
    apply (hi.hasSum_iff (f := fun k => denseOddComplex c k * z ^ k) ?_).mp
    · simpa only [Function.comp_def, denseOddComplex_odd] using hz
    · intro k hk
      have hm : k % 2 ≠ 1 := by
        intro hm
        apply hk
        refine ⟨k / 2, ?_⟩
        change 2 * (k / 2) + 1 = k
        omega
      simp [denseOddComplex, hm]
  simpa only [FormalMultilinearSeries.coeff_ofScalars, zero_add, smul_eq_mul,
    mul_comm] using hsum

theorem complex_odd_coefficients_eq {c d : ℕ → ℂ} {f g : ℂ → ℂ}
    (hc : ∀ᶠ z in 𝓝 (0 : ℂ), HasSum (fun n => c n * z ^ (2 * n + 1)) (f z))
    (hd : ∀ᶠ z in 𝓝 (0 : ℂ), HasSum (fun n => d n * z ^ (2 * n + 1)) (g z))
    (he : f =ᶠ[𝓝 0] g) : c = d := by
  have hp := (complex_odd_series_hasFPowerSeriesAt hc).eq_formalMultilinearSeries_of_eventually
    (complex_odd_series_hasFPowerSeriesAt hd) he
  funext n
  simpa only [FormalMultilinearSeries.coeff_ofScalars, denseOddComplex_odd] using
    congrArg (fun p : FormalMultilinearSeries ℂ ℂ ℂ => p.coeff (2 * n + 1)) hp

theorem rescaling_coefficient_identity (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {A B : ℂ} (he : ∀ z, s.V z = A * s.U (B * z)) (n : ℕ) :
    ((s.coefficients n).2 : ℂ) = A * ((s.coefficients n).1 : ℂ) * B ^ (2 * n + 1) := by
  have hc : ∀ᶠ z in 𝓝 (0 : ℂ),
      HasSum (fun n => ((s.coefficients n).2 : ℂ) * z ^ (2 * n + 1)) (s.V z) :=
    Eventually.of_forall fun z => (s.coefficient_series_entire hs hstrict z).2.of_norm.hasSum
  have hd : ∀ᶠ z in 𝓝 (0 : ℂ),
      HasSum (fun n => (A * ((s.coefficients n).1 : ℂ) * B ^ (2 * n + 1)) *
        z ^ (2 * n + 1)) (A * s.U (B * z)) := by
    apply Eventually.of_forall
    intro z
    simpa only [U, oddSum, mul_pow, mul_assoc, mul_left_comm, mul_comm] using
      ((s.coefficient_series_entire hs hstrict (B * z)).1.of_norm.hasSum).mul_left A
  exact congrFun (complex_odd_coefficients_eq hc hd (Eventually.of_forall he)) n

theorem rescaling_forces_defect_zero (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {A B : ℂ} (he : ∀ z, s.V z = A * s.U (B * z)) : s.defect = 0 := by
  have h0 := s.rescaling_coefficient_identity hs hstrict he 0
  have h1 := s.rescaling_coefficient_identity hs hstrict he 1
  have h2 := s.rescaling_coefficient_identity hs hstrict he 2
  simp only [coefficients_zero, Complex.ofReal_one, mul_one] at h0
  have hab : A * B = 1 := by simpa using h0.symm
  simp only [coefficients_one, u1, v1,
    Complex.ofReal_div, Complex.ofReal_ofNat] at h1
  have hkp : (s.k : ℂ) = (s.p : ℂ) * B ^ 2 := by
    linear_combination 3 * h1 + (s.p : ℂ) * B ^ 2 * hab
  simp only [coefficients_two] at h2
  have hvu : (s.v2 : ℂ) = (s.u2 : ℂ) * B ^ 4 := by
    linear_combination h2 + (s.u2 : ℂ) * B ^ 4 * hab
  apply Complex.ofReal_inj.mp
  change (s.defect : ℂ) = (0 : ℂ)
  simp only [defect, Complex.ofReal_sub, Complex.ofReal_mul, Complex.ofReal_pow]
  rw [hkp, hvu]
  ring

def scalarScales (x y : ℝ) : Scales := ⟨x, y, x, y⟩

def scalarT (x y : ℝ) : ℂ → ℂ := (scalarScales x y).U

theorem scalar_components_equal (x y : ℝ) :
    (scalarScales x y).U = (scalarScales x y).V := by
  have hc : ∀ n, ((scalarScales x y).coefficients n).1 =
      ((scalarScales x y).coefficients n).2 := by
    intro n
    cases n with
    | zero => rw [coefficients_zero]
    | succ n => rw [(scalarScales x y).coefficients_solution.2]; rfl
  change oddSum _ = oddSum _
  congr 1
  funext n
  exact hc n

theorem scalarT_solution {x y : ℝ} (hx : 0 < x) (hy : 0 < y)
    (hx1 : x < 1) (hy1 : y < 1) :
    scalarT x y 0 = 0 ∧ ∀ z : ℂ,
      HasDerivAt (scalarT x y) (1 + scalarT x y ((x : ℂ) * z) *
        scalarT x y ((y : ℂ) * z)) z := by
  have hs : (scalarScales x y).positive := ⟨hx, hy, hx, hy⟩
  have hsol := (scalarScales x y).coupled_entire_solution hs ⟨hx1, hy1, hx1, hy1⟩
  refine ⟨hsol.1, ?_⟩
  intro z
  have h := (hsol.2.2 z).1
  rw [← scalar_components_equal x y] at h
  simpa only [scalarT, scalarScales] using h

def reductionScale (s : Scales) : ℝ := Real.sqrt (s.k / s.p)

theorem reductionScale_positive_sq (s : Scales) (hs : s.positive) :
    0 < s.reductionScale ∧ s.reductionScale ^ 2 = s.k / s.p := by
  have hp : 0 < s.p := mul_pos hs.1 hs.2.1
  have hk : 0 < s.k := mul_pos hs.2.2.1 hs.2.2.2
  exact ⟨Real.sqrt_pos.2 (div_pos hk hp), Real.sq_sqrt (div_pos hk hp).le⟩

theorem reductionScale_surface (s : Scales) (hs : s.positive)
    (hred : s.q = s.b ∨ s.q * s.b = s.a * s.r) :
    (s.a = s.reductionScale * s.q ∧ s.b = s.reductionScale * s.r) ∨
    (s.b = s.q ∧ s.a = s.reductionScale ^ 2 * s.r) := by
  have hS := s.reductionScale_positive_sq hs
  have hp : s.p ≠ 0 := ne_of_gt (mul_pos hs.1 hs.2.1)
  have hSq : s.reductionScale ^ 2 * s.p = s.k := (eq_div_iff hp).mp hS.2
  rcases hred with hqb | har
  · right
    refine ⟨hqb.symm, ?_⟩
    apply mul_right_cancel₀ (ne_of_gt hs.1)
    calc
      s.a * s.q = s.a * s.b := by rw [hqb]
      _ = s.reductionScale ^ 2 * s.p := hSq.symm
      _ = (s.reductionScale ^ 2 * s.r) * s.q := by dsimp [p]; ring
  · have hm : s.q * (s.reductionScale * s.r) ^ 2 = s.q * s.b ^ 2 := by
      dsimp [p, k] at hSq
      linear_combination s.r * hSq - s.b * har
    have he : s.reductionScale * s.r = s.b :=
      (sq_eq_sq₀ (mul_pos hS.1 hs.2.1).le hs.2.2.2.le).mp
        (mul_left_cancel₀ (ne_of_gt hs.1) hm)
    left
    refine ⟨?_, he.symm⟩
    apply mul_right_cancel₀ (ne_of_gt hs.2.1)
    calc
      s.a * s.r = s.q * s.b := har.symm
      _ = (s.reductionScale * s.q) * s.r := by rw [← he]; ring

theorem effective_scalar_scales (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hred : s.q = s.b ∨ s.q * s.b = s.a * s.r) :
    0 < s.reductionScale * s.r ∧ s.reductionScale * s.r < 1 := by
  have hS := s.reductionScale_positive_sq hs
  refine ⟨mul_pos hS.1 hs.2.1, ?_⟩
  rcases s.reductionScale_surface hs hred with h | h
  · rw [← h.2]
    exact hstrict.2.2.2
  · have har : s.a * s.r < 1 :=
      lt_trans (mul_lt_mul_of_pos_right hstrict.2.2.1 hs.2.1) (by simpa using hstrict.2.1)
    have he : (s.reductionScale * s.r) ^ 2 = s.a * s.r := by rw [h.2]; ring
    nlinarith [sq_nonneg (s.reductionScale * s.r - 1)]

/-- A scalar solution generates a coupled solution when the two arguments
match in the displayed order or after interchanging the scalar factors. -/
theorem scalar_rescaled_solution (s : Scales) {T : ℂ → ℂ} {c e : ℂ}
    (hc : c ≠ 0) (hzero : T 0 = 0)
    (hT : ∀ z, HasDerivAt T (1 + T ((s.q : ℂ) * z) * T (e * z)) z)
    (he : e = c ^ 2 * (s.r : ℂ))
    (hmatch : ((s.a : ℂ) = c ^ 2 * (s.q : ℂ) ∧ (s.b : ℂ) = e) ∨
      ((s.b : ℂ) = (s.q : ℂ) ∧ (s.a : ℂ) = c ^ 2 * e)) :
    s.IsEntireSolution (fun z => c * T (c⁻¹ * z)) (fun z => c⁻¹ * T (c * z)) := by
  refine ⟨by simp [hzero], by simp [hzero], ?_⟩
  intro z
  have hF := ((hT (c⁻¹ * z)).comp z ((hasDerivAt_id z).const_mul c⁻¹)).const_mul c
  have hG := ((hT (c * z)).comp z ((hasDerivAt_id z).const_mul c)).const_mul c⁻¹
  have harg : e * (c⁻¹ * z) = c * ((s.r : ℂ) * z) := by
    rw [he]
    field_simp [hc]
  constructor
  · apply hF.congr_deriv
    rw [harg]
    field_simp [hc]
  · rcases hmatch with h | h
    · have ha : c⁻¹ * ((s.a : ℂ) * z) = (s.q : ℂ) * (c * z) := by
        rw [h.1]
        field_simp [hc]
      have hb : c * ((s.b : ℂ) * z) = e * (c * z) := by rw [h.2]; ring
      apply hG.congr_deriv
      dsimp only
      rw [ha, hb]
      field_simp [hc]
    · have ha : c⁻¹ * ((s.a : ℂ) * z) = e * (c * z) := by
        rw [h.2]
        field_simp [hc]
      have hb : c * ((s.b : ℂ) * z) = (s.q : ℂ) * (c * z) := by rw [h.1]; ring
      apply hG.congr_deriv
      dsimp only
      rw [ha, hb]
      field_simp [hc]

def reductionRoot (s : Scales) : ℝ := Real.sqrt s.reductionScale

theorem reductionRoot_positive_sq (s : Scales) (hs : s.positive) :
    0 < s.reductionRoot ∧ s.reductionRoot ^ 2 = s.reductionScale :=
  ⟨Real.sqrt_pos.2 (s.reductionScale_positive_sq hs).1,
    Real.sq_sqrt (s.reductionScale_positive_sq hs).1.le⟩

theorem coupled_scalar_representation (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hred : s.q = s.b ∨ s.q * s.b = s.a * s.r) (z : ℂ) :
    s.U z = (s.reductionRoot : ℂ) * scalarT s.q (s.reductionScale * s.r)
      ((s.reductionRoot : ℂ)⁻¹ * z) ∧
    s.V z = (s.reductionRoot : ℂ)⁻¹ * scalarT s.q (s.reductionScale * s.r)
      ((s.reductionRoot : ℂ) * z) := by
  have heff := s.effective_scalar_scales hs hstrict hred
  have hT := scalarT_solution hs.1 heff.1 hstrict.1 heff.2
  have hroot := s.reductionRoot_positive_sq hs
  have hc : (s.reductionRoot : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hroot.1
  have hcsq : (s.reductionRoot : ℂ) ^ 2 = (s.reductionScale : ℂ) := by
    exact_mod_cast hroot.2
  have he : ((s.reductionScale * s.r : ℝ) : ℂ) =
      (s.reductionRoot : ℂ) ^ 2 * (s.r : ℂ) := by rw [hcsq]; push_cast; rfl
  have hm : ((s.a : ℂ) = (s.reductionRoot : ℂ) ^ 2 * (s.q : ℂ) ∧
      (s.b : ℂ) = ((s.reductionScale * s.r : ℝ) : ℂ)) ∨
      ((s.b : ℂ) = (s.q : ℂ) ∧ (s.a : ℂ) =
        (s.reductionRoot : ℂ) ^ 2 * ((s.reductionScale * s.r : ℝ) : ℂ)) := by
    rcases s.reductionScale_surface hs hred with h | h
    · left
      constructor
      · rw [hcsq]
        exact_mod_cast h.1
      · exact_mod_cast h.2
    · right
      refine ⟨by exact_mod_cast h.1, ?_⟩
      calc
        (s.a : ℂ) = ((s.reductionScale ^ 2 * s.r : ℝ) : ℂ) :=
          congrArg (fun x : ℝ => (x : ℂ)) h.2
        _ = (s.reductionRoot : ℂ) ^ 2 * ((s.reductionScale * s.r : ℝ) : ℂ) := by
          push_cast
          rw [hcsq]
          ring
  have hsol := s.scalar_rescaled_solution hc hT.1 hT.2 he hm
  have heq := s.entire_solution_eq hs hstrict hsol
  exact ⟨congrFun heq.1.symm z, congrFun heq.2.symm z⟩

theorem canonical_component_rescaling (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    (hred : s.q = s.b ∨ s.q * s.b = s.a * s.r) (z : ℂ) :
    s.V z = (s.reductionScale : ℂ)⁻¹ * s.U ((s.reductionScale : ℂ) * z) := by
  have hroot := s.reductionRoot_positive_sq hs
  have hc : (s.reductionRoot : ℂ) ≠ 0 := by exact_mod_cast ne_of_gt hroot.1
  have hcsq : (s.reductionRoot : ℂ) ^ 2 = (s.reductionScale : ℂ) := by
    exact_mod_cast hroot.2
  have harg : (s.reductionRoot : ℂ)⁻¹ * ((s.reductionScale : ℂ) * z) =
      (s.reductionRoot : ℂ) * z := by
    rw [← hcsq]
    field_simp [hc]
  rw [(s.coupled_scalar_representation hs hstrict hred z).2,
    (s.coupled_scalar_representation hs hstrict hred ((s.reductionScale : ℂ) * z)).1,
    harg, ← hcsq]
  field_simp [hc]

theorem component_rescaling_iff_defect (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    (∃ A B : ℂ, A ≠ 0 ∧ B ≠ 0 ∧ ∀ z, s.V z = A * s.U (B * z)) ↔
      s.defect = 0 := by
  constructor
  · rintro ⟨A, B, _, _, he⟩
    exact s.rescaling_forces_defect_zero hs hstrict he
  · intro hD
    have hS : (s.reductionScale : ℂ) ≠ 0 := by
      exact_mod_cast ne_of_gt (s.reductionScale_positive_sq hs).1
    exact ⟨(s.reductionScale : ℂ)⁻¹, (s.reductionScale : ℂ), inv_ne_zero hS, hS,
      s.canonical_component_rescaling hs hstrict ((s.defect_eq_zero_iff hs).mp hD)⟩

theorem component_rescaling_iff_surfaces (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    (∃ A B : ℂ, A ≠ 0 ∧ B ≠ 0 ∧ ∀ z, s.V z = A * s.U (B * z)) ↔
      s.q = s.b ∨ s.q * s.b = s.a * s.r := by
  rw [s.component_rescaling_iff_defect hs hstrict, s.defect_eq_zero_iff hs]

theorem scalarT_unique {x y : ℝ} (hx : 0 < x) (hy : 0 < y)
    (hx1 : x < 1) (hy1 : y < 1) {f : ℂ → ℂ} (hzero : f 0 = 0)
    (hf : ∀ z, HasDerivAt f (1 + f ((x : ℂ) * z) * f ((y : ℂ) * z)) z) :
    f = scalarT x y := by
  have hsol : (scalarScales x y).IsEntireSolution f f :=
    ⟨hzero, hzero, fun z => ⟨hf z, hf z⟩⟩
  exact ((scalarScales x y).entire_solution_eq ⟨hx, hy, hx, hy⟩
    ⟨hx1, hy1, hx1, hy1⟩ hsol).1

theorem scalarT_symm {x y : ℝ} (hx : 0 < x) (hy : 0 < y)
    (hx1 : x < 1) (hy1 : y < 1) : scalarT x y = scalarT y x := by
  have hsol := scalarT_solution hx hy hx1 hy1
  apply scalarT_unique hy hx hy1 hx1 hsol.1
  intro z
  simpa only [mul_comm] using hsol.2 z

/-- The earlier finite-jet collision is in fact a collision of the labeled
entire pairs, so the defect guard cannot be dropped from the germ inverse. -/
theorem boundary_entire_collision : boundaryLeft.U = boundaryRight.U ∧
    boundaryLeft.V = boundaryRight.V ∧ boundaryLeft ≠ boundaryRight := by
  have hU : boundaryLeft.U = boundaryRight.U := by
    change scalarT (1 / 4) (1 / 2) = scalarT (1 / 2) (1 / 4)
    exact scalarT_symm (by norm_num) (by norm_num) (by norm_num) (by norm_num)
  have hl : boundaryLeft.U = boundaryLeft.V := scalar_components_equal (1 / 4) (1 / 2)
  have hr : boundaryRight.U = boundaryRight.V := scalar_components_equal (1 / 2) (1 / 4)
  exact ⟨hU, hl.symm.trans (hU.trans hr), boundary_collision.2.2.2.2⟩

end Komorebi.SpecialFunctions.Coupled.Scales
