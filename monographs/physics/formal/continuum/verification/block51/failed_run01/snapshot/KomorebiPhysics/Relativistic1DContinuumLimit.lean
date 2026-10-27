module

public import KomorebiPhysics.Relativistic1DAsymptoticExamples
public import Mathlib.Analysis.Asymptotics.Ring

@[expose] public section

open Filter Asymptotics
open scoped Topology

set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DContinuumLimit

theorem div_sq_isBigO_positive {f : ℝ → ℝ}
    (h : f =O[𝓝[>] (0 : ℝ)] (fun ε : ℝ => ε^6)) :
    (fun ε => f ε / ε^2) =O[𝓝[>] (0 : ℝ)] (fun ε : ℝ => ε^4) := by
  rcases h.exists_pos with ⟨c, hc, hbc⟩
  apply (IsBigOWith.of_bound (c := c) ?_).isBigO
  rw [IsBigOWith_def] at hbc
  filter_upwards [hbc, self_mem_nhdsWithin] with ε hε hpos
  rw [Real.norm_eq_abs, Real.norm_eq_abs] at hε ⊢
  have hne : ε ≠ 0 := ne_of_gt hpos
  have habspos : 0 < |ε| := abs_pos.mpr hne
  have hp2 : |ε ^ 2| = |ε|^2 := abs_pow ε 2
  have hp4 : |ε ^ 4| = |ε|^4 := abs_pow ε 4
  have hp6 : |ε ^ 6| = |ε|^6 := abs_pow ε 6
  rw [abs_div, hp2, hp4]
  rw [hp6] at hε
  rw [div_le_iff₀ (pow_pos habspos 2)]
  convert hε using 1
  · rfl
  · ring

end KomorebiPhysics.Relativistic1DContinuumLimit

namespace KomorebiPhysics.Relativistic1DContinuumLimit

noncomputable section

open KomorebiPhysics.Dispersion1D
open KomorebiPhysics.Relativistic1DShellAsymptotics
open KomorebiPhysics.Relativistic1DAsymptoticAlgebra


theorem div_isBigO_of_eventually_abs_ge {f g d : ℝ → ℝ} {l : Filter ℝ} {c : ℝ}
    (hf : f =O[l] g) (hc : 0 < c) (hd : ∀ᶠ x in l, c ≤ |d x|) :
    (fun x => f x / d x) =O[l] g := by
  rcases hf.exists_pos with ⟨C, hC, hbound⟩
  apply (IsBigOWith.of_bound (c := C / c) ?_).isBigO
  rw [IsBigOWith_def] at hbound
  filter_upwards [hbound, hd] with x hfx hdx
  rw [Real.norm_eq_abs, Real.norm_eq_abs] at hfx ⊢
  rw [abs_div]
  have hdpos : 0 < |d x| := lt_of_lt_of_le hc hdx
  calc
    |f x| / |d x| ≤ (C * |g x|) / |d x| :=
      div_le_div_of_nonneg_right hfx (abs_nonneg _)
    _ ≤ (C * |g x|) / c := by
      exact div_le_div_of_nonneg_left (mul_nonneg hC.le (abs_nonneg _)) hc hdx
    _ = (C / c) * |g x| := by ring


theorem div_linear_isBigO_positive {f : ℝ → ℝ}
    (h : f =O[𝓝[>] (0 : ℝ)] (fun ε : ℝ => ε^5)) :
    (fun ε => f ε / ε) =O[𝓝[>] (0 : ℝ)] (fun ε : ℝ => ε^4) := by
  rcases h.exists_pos with ⟨c, hc, hbc⟩
  apply (IsBigOWith.of_bound (c := c) ?_).isBigO
  rw [IsBigOWith_def] at hbc
  filter_upwards [hbc, self_mem_nhdsWithin] with ε hε hpos
  rw [Real.norm_eq_abs, Real.norm_eq_abs] at hε ⊢
  have habspos : 0 < |ε| := abs_pos.mpr (ne_of_gt hpos)
  have habse : |ε| = ε := abs_of_pos hpos
  rw [abs_div, habse, abs_pow]
  rw [abs_pow] at hε
  rw [div_le_iff₀ hpos]
  convert hε using 1
  · rfl
  · rw [habse]
    ring


theorem div_cube_isBigO_square_positive {f : ℝ → ℝ}
    (h : f =O[𝓝[>] (0 : ℝ)] (fun ε : ℝ => ε^3)) :
    (fun ε => f ε / ε) =O[𝓝[>] (0 : ℝ)] (fun ε : ℝ => ε^2) := by
  rcases h.exists_pos with ⟨c, hc, hbc⟩
  apply (IsBigOWith.of_bound (c := c) ?_).isBigO
  rw [IsBigOWith_def] at hbc
  filter_upwards [hbc, self_mem_nhdsWithin] with ε hε hpos
  rw [Real.norm_eq_abs, Real.norm_eq_abs] at hε ⊢
  have habse : |ε| = ε := abs_of_pos hpos
  rw [abs_div, habse, abs_pow]
  rw [abs_pow] at hε
  rw [div_le_iff₀ hpos]
  convert hε using 1
  · rfl
  · rw [habse]
    ring

/-- Quartic coefficient in `shell^2`. -/
def shellSqQuartic (m k : ℝ) : ℝ := (energy m k ^ 4 + m^2*k^2) / 3

def shellSqPoly4 (m k ε : ℝ) : ℝ :=
  1 - energy m k ^ 2 * ε^2 + shellSqQuartic m k * ε^4

theorem pow8_isBigO_pow6_positive :
    (fun ε : ℝ => ε^8) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
  exact (isLittleO_pow_pow (by omega : 6 < 8)).isBigO.mono nhdsWithin_le_nhds

theorem shell_poly_sq_error_isBigO (m k : ℝ) :
    (fun ε =>
      (1 - energy m k ^ 2 * ε^2 / 2 + shellQuarticCoeffSource m k * ε^4)^2 -
        shellSqPoly4 m k ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
  let E := energy m k
  let B := shellQuarticCoeffSource m k
  have h6 : (fun ε : ℝ => ε^6) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
    isBigO_refl _ _
  have h8 : (fun ε : ℝ => ε^8) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
    pow8_isBigO_pow6_positive
  have hsum := (h6.const_mul_left (-(E^2 * B))).add (h8.const_mul_left (B^2))
  exact hsum.congr_left (by
    intro ε
    dsimp [E, B, shellSqPoly4, shellSqQuartic, shellQuarticCoeffSource]
    ring)

theorem shell_sq_expansion_isBigO (m k : ℝ) :
    (fun ε => shell m k ε ^ 2 - shellSqPoly4 m k ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
  let p : ℝ → ℝ := fun ε =>
    1 - energy m k ^ 2 * ε^2 / 2 + shellQuarticCoeffSource m k * ε^4
  have hr : (fun ε => shell m k ε - p ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
    exact (shell_expansion_source_form_isBigO m k).mono nhdsWithin_le_nhds
  have hshell : Tendsto (fun ε => shell m k ε) (𝓝[>] 0) (𝓝 1) := by
    have hfull : Tendsto (fun ε => shell m k ε) (𝓝 0) (𝓝 1) := by
      have hm : Continuous (fun ε : ℝ => Real.cos (m * ε)) :=
        Real.continuous_cos.comp (continuous_const.mul continuous_id)
      have hk : Continuous (fun ε : ℝ => Real.cos (k * ε)) :=
        Real.continuous_cos.comp (continuous_const.mul continuous_id)
      change Tendsto ((fun ε : ℝ => Real.cos (m * ε)) *
        (fun ε : ℝ => Real.cos (k * ε))) (𝓝 0) (𝓝 1)
      simpa using (hm.mul hk).tendsto 0
    exact hfull.mono_left nhdsWithin_le_nhds
  have hp : Tendsto p (𝓝[>] 0) (𝓝 1) := by
    dsimp [p]
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    convert (tendsto_const_nhds.sub
      ((tendsto_const_nhds.mul (hid.pow 2)).div_const 2)).add
        (tendsto_const_nhds.mul (hid.pow 4)) using 1
    all_goals ring
  have hbounded : (fun ε => shell m k ε + p ε) =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) :=
    (hshell.add hp).isBigO_one ℝ
  have hprod := hr.mul hbounded
  have hprod6 :
      (fun ε => (shell m k ε - p ε) * (shell m k ε + p ε)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
    exact hprod.congr_right (by intro ε; simp)
  have hpoly := shell_poly_sq_error_isBigO m k
  exact (hprod6.add hpoly).congr_left (by
    intro ε
    dsimp [p]
    ring)


/-- Normalized square of the exact principal sine. -/
def sinQ (m k ε : ℝ) : ℝ :=
  if ε = 0 then energy m k ^ 2 else (1 - shell m k ε ^ 2) / ε^2

/-- Second-order normalized sine-square approximation. -/
def sinQPoly2 (m k ε : ℝ) : ℝ :=
  energy m k ^ 2 - shellSqQuartic m k * ε^2

@[simp] theorem sinQ_zero (m k : ℝ) : sinQ m k 0 = energy m k ^ 2 := by
  simp [sinQ]

theorem sinQ_of_pos (m k ε : ℝ) (hε : 0 < ε) :
    sinQ m k ε = (1 - shell m k ε ^ 2) / ε^2 := by
  simp [sinQ, ne_of_gt hε]

/-- Dividing the sine-square shell by the positive squared spacing gives an `O(ε⁴)` remainder. -/
theorem sinQ_expansion_isBigO (m k : ℝ) :
    (fun ε => sinQ m k ε - sinQPoly2 m k ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) := by
  have hdiv := div_sq_isBigO_positive (shell_sq_expansion_isBigO m k)
  have hneg := hdiv.const_mul_left (-1 : ℝ)
  apply hneg.congr'
  · filter_upwards [self_mem_nhdsWithin] with ε hε
    have hne : ε ≠ 0 := ne_of_gt hε
    rw [sinQ_of_pos m k ε hε]
    dsimp [sinQPoly2, shellSqPoly4]
    field_simp [hne]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The normalized sine square converges to the continuum energy squared. -/
theorem tendsto_sinQ (m k : ℝ) :
    Tendsto (sinQ m k) (𝓝[>] 0) (𝓝 (energy m k ^ 2)) := by
  have herr := (sinQ_expansion_isBigO m k).trans_tendsto (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 4)
  have hpoly : Tendsto (sinQPoly2 m k) (𝓝[>] 0) (𝓝 (energy m k ^ 2)) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε : ℝ => energy m k ^ 2 - shellSqQuartic m k * ε^2)
      (𝓝[>] 0) (𝓝 (energy m k ^ 2))
    convert tendsto_const_nhds.sub (tendsto_const_nhds.mul (hid.pow 2)) using 1
    all_goals ring
  have hsum := herr.add hpoly
  simpa using Tendsto.congr' (Filter.Eventually.of_forall (fun ε => by ring)) hsum

/-- Exact factorization of `1-shell²` on positive spacings. -/
theorem one_sub_shell_sq_eq (m k ε : ℝ) (hε : 0 < ε) :
    1 - shell m k ε ^ 2 = ε^2 * sinQ m k ε := by
  rw [sinQ_of_pos m k ε hε]
  field_simp [ne_of_gt hε]

/-- For nonzero continuum energy the normalized sine square is eventually positive. -/
theorem eventually_sinQ_pos {m k : ℝ} (hE : energy m k ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0, 0 < sinQ m k ε := by
  have hE2 : 0 < energy m k ^ 2 := sq_pos_of_ne_zero hE
  have hmem : Set.Ioi (energy m k ^ 2 / 2) ∈ 𝓝 (energy m k ^ 2) := by
    exact Ioi_mem_nhds (by linarith)
  filter_upwards [(tendsto_sinQ m k) hmem] with ε hε
  exact lt_trans (by positivity : 0 < energy m k ^ 2 / 2) hε



/-- Positive square-root factor in the principal sine. -/
def radial (m k ε : ℝ) : ℝ := Real.sqrt (sinQ m k ε)

/-- The exact shell tends to one on the physical positive-spacing filter. -/
theorem tendsto_shell_positive (m k : ℝ) :
    Tendsto (fun ε => shell m k ε) (𝓝[>] 0) (𝓝 1) := by
  have hm : Continuous (fun ε : ℝ => Real.cos (m * ε)) :=
    Real.continuous_cos.comp (continuous_const.mul continuous_id)
  have hk : Continuous (fun ε : ℝ => Real.cos (k * ε)) :=
    Real.continuous_cos.comp (continuous_const.mul continuous_id)
  have hfull : Tendsto (fun ε => shell m k ε) (𝓝 0) (𝓝 1) := by
    change Tendsto ((fun ε : ℝ => Real.cos (m * ε)) *
      (fun ε : ℝ => Real.cos (k * ε))) (𝓝 0) (𝓝 1)
    simpa using (hm.mul hk).tendsto 0
  exact hfull.mono_left nhdsWithin_le_nhds

/-- Near positive zero the exact shell lies in the positive half of the principal branch. -/
theorem eventually_shell_pos (m k : ℝ) :
    ∀ᶠ ε in 𝓝[>] 0, 0 < shell m k ε := by
  exact (tendsto_shell_positive m k) (Ioi_mem_nhds (by norm_num : (0:ℝ) < 1))

/-- The principal sine factors as spacing times the positive radial factor. -/
theorem sin_principalPhase_eq_spacing_radial (m k ε : ℝ) (hε : 0 < ε) :
    Real.sin (principalPhase m k ε) = ε * radial m k ε := by
  rw [principalPhase, Real.sin_arccos]
  rw [one_sub_shell_sq_eq m k ε hε]
  rw [Real.sqrt_mul (sq_nonneg ε)]
  rw [Real.sqrt_sq hε.le]
  rfl

/-- On the positive-shell branch the principal phase is an ordinary arcsine. -/
theorem principalPhase_eq_arcsin_spacing_radial {m k ε : ℝ}
    (hε : 0 < ε) (hs : 0 < shell m k ε) :
    principalPhase m k ε = Real.arcsin (ε * radial m k ε) := by
  have hlo : -(Real.pi / 2) ≤ principalPhase m k ε := by
    have hp := principalPhase_nonneg m k ε
    have hpi : 0 < Real.pi := Real.pi_pos
    linarith
  have hhi : principalPhase m k ε ≤ Real.pi / 2 :=
    Real.arccos_le_pi_div_two.mpr hs.le
  calc
    principalPhase m k ε = Real.arcsin (Real.sin (principalPhase m k ε)) :=
      (Real.arcsin_sin hlo hhi).symm
    _ = Real.arcsin (ε * radial m k ε) := by
      rw [sin_principalPhase_eq_spacing_radial m k ε hε]

/-- A total positive-branch frequency extension. Its value at zero is chosen as the continuum energy. -/
def positiveFrequency (m k ε : ℝ) : ℝ :=
  if hε : ε = 0 then energy m k else principalFrequency m k ε hε

@[simp] theorem positiveFrequency_zero (m k : ℝ) :
    positiveFrequency m k 0 = energy m k := by simp [positiveFrequency]

/-- On positive spacing, the total extension is the checked principal frequency. -/
theorem positiveFrequency_of_pos (m k ε : ℝ) (hε : 0 < ε) :
    positiveFrequency m k ε = principalFrequency m k ε (ne_of_gt hε) := by
  simp [positiveFrequency, ne_of_gt hε]

/-- Eventually the exact positive frequency is the arcsine quotient of the radial factor. -/
theorem eventually_positiveFrequency_eq_arcsin_div (m k : ℝ) :
    ∀ᶠ ε in 𝓝[>] 0,
      positiveFrequency m k ε = Real.arcsin (ε * radial m k ε) / ε := by
  filter_upwards [self_mem_nhdsWithin, eventually_shell_pos m k] with ε hε hs
  rw [positiveFrequency_of_pos m k ε hε, principalFrequency]
  rw [principalPhase_eq_arcsin_spacing_radial hε hs]

/-- Cubic Taylor approximant for sine. -/
def sinPoly3 (x : ℝ) : ℝ := x - x^3/6

theorem taylor5_sin_closed (x : ℝ) :
    taylorWithinEval Real.sin 5 Set.univ 0 x = sinPoly3 x + x^5/120 := by
  simp only [taylorWithinEval_succ, taylor_within_zero_eval, iteratedDerivWithin_univ]
  norm_num [Real.iteratedDeriv_even_sin, Real.iteratedDeriv_odd_sin, sinPoly3]
  ring

/-- Genuine fifth-order sine remainder. -/
theorem sin_cubic_expansion_isBigO :
    (fun x : ℝ => Real.sin x - sinPoly3 x) =O[𝓝 0] (fun x : ℝ => x^5) := by
  have hsmall := (taylor_isLittleO_univ (x₀ := (0 : ℝ)) (n := 5) Real.contDiff_sin).isBigO
  have hsmall' : (fun x : ℝ => Real.sin x - taylorWithinEval Real.sin 5 Set.univ 0 x)
      =O[𝓝 0] (fun x : ℝ => x^5) := hsmall.congr_right (by intro x; ring)
  have hpoly : (fun x : ℝ => taylorWithinEval Real.sin 5 Set.univ 0 x - sinPoly3 x)
      =O[𝓝 0] (fun x : ℝ => x^5) := by
    have h := (isBigO_refl (fun x : ℝ => x^5) (𝓝 0)).const_mul_left (1/120 : ℝ)
    exact h.congr_left (by intro x; rw [taylor5_sin_closed]; ring)
  exact (hsmall'.add hpoly).congr_left (by intro x; ring)

theorem arcsin_sub_id_isLittleO :
    (fun x : ℝ => Real.arcsin x - x) =o[𝓝 0] (fun x : ℝ => x) := by
  have hd : HasDerivAt Real.arcsin 1 0 := by
    convert Real.hasDerivAt_arcsin (by norm_num : (0:ℝ) ≠ -1)
      (by norm_num : (0:ℝ) ≠ 1) using 1
    all_goals norm_num
  simpa using hd.isLittleO

theorem arcsin_isBigO_id :
    Real.arcsin =O[𝓝 0] (fun x : ℝ => x) := by
  have hdiff := arcsin_sub_id_isLittleO.isBigO
  have hid := isBigO_refl (fun x : ℝ => x) (𝓝 0)
  exact (hdiff.add hid).congr_left (by intro x; ring)

/-- Cubic arcsine expansion obtained by inverting the checked sine expansion. -/
theorem arcsin_cubic_expansion_isBigO :
    (fun x : ℝ => Real.arcsin x - x - x^3/6) =O[𝓝 0] (fun x : ℝ => x^5) := by
  let y : ℝ → ℝ := Real.arcsin
  let r : ℝ → ℝ := fun x => x - y x + y x ^ 3 / 6
  have hyT : Tendsto y (𝓝 0) (𝓝 0) := by
    dsimp [y]
    simpa using Real.continuous_arcsin.tendsto 0
  have hyO : y =O[𝓝 0] (fun x : ℝ => x) := by
    simpa [y] using arcsin_isBigO_id
  have hcomp := sin_cubic_expansion_isBigO.comp_tendsto hyT
  have hcomp5 :
      (fun x => Real.sin (y x) - sinPoly3 (y x)) =O[𝓝 0] (fun x : ℝ => x^5) :=
    hcomp.trans (hyO.pow 5)
  have hr : r =O[𝓝 0] (fun x : ℝ => x^5) := by
    apply hcomp5.congr'
    · filter_upwards [Icc_mem_nhds (by norm_num : (-1:ℝ) < 0)
        (by norm_num : (0:ℝ) < 1)] with x hx
      dsimp [r, y, sinPoly3]
      rw [Real.sin_arcsin hx.1 hx.2]
      ring
    · exact Filter.Eventually.of_forall (fun _ => rfl)
  have h5to3 : (fun x : ℝ => x^5) =O[𝓝 0] (fun x : ℝ => x^3) :=
    (isLittleO_pow_pow (by omega : 3 < 5)).isBigO
  have hy3 : (fun x => y x ^ 3 / 6) =O[𝓝 0] (fun x : ℝ => x^3) := by
    have h := (hyO.pow 3).const_mul_left (1/6 : ℝ)
    exact h.congr_left (by intro x; ring)
  have hr3 : r =O[𝓝 0] (fun x : ℝ => x^3) := hr.trans h5to3
  have hy_sub_x : (fun x => y x - x) =O[𝓝 0] (fun x : ℝ => x^3) := by
    have h := hy3.sub hr3
    exact h.congr_left (by intro x; dsimp [r]; ring)
  have hy2 : (fun x => y x ^ 2) =O[𝓝 0] (fun x : ℝ => x^2) := hyO.pow 2
  have hyx : (fun x => y x * x) =O[𝓝 0] (fun x : ℝ => x^2) := by
    have h := hyO.mul (isBigO_refl (fun x : ℝ => x) (𝓝 0))
    exact h.congr_right (by intro x; ring)
  have hx2 : (fun x : ℝ => x^2) =O[𝓝 0] (fun x : ℝ => x^2) := isBigO_refl _ _
  have hfactor : (fun x => y x ^ 2 + y x * x + x^2) =O[𝓝 0] (fun x : ℝ => x^2) :=
    (hy2.add hyx).add hx2
  have hcubes : (fun x => y x ^ 3 - x^3) =O[𝓝 0] (fun x : ℝ => x^5) := by
    have h := hy_sub_x.mul hfactor
    exact h.congr' (Filter.Eventually.of_forall (fun x => by ring))
      (Filter.Eventually.of_forall (fun x => by ring))
  have hcubes6 : (fun x => (y x ^ 3 - x^3) / 6) =O[𝓝 0] (fun x : ℝ => x^5) := by
    have h := hcubes.const_mul_left (1/6 : ℝ)
    exact h.congr_left (by intro x; ring)
  have hfinal := hcubes6.sub hr
  exact hfinal.congr_left (by intro x; dsimp [r, y]; ring)

/-- Quadratic radial coefficient. -/
def radialCoeff (m k : ℝ) : ℝ :=
  -(shellSqQuartic m k) / (2 * energy m k)

/-- Quadratic radial approximant. -/
def radialPoly2 (m k ε : ℝ) : ℝ :=
  energy m k + radialCoeff m k * ε^2


/-- Exact arcsine input. -/
def phaseInput (m k ε : ℝ) : ℝ := ε * radial m k ε

/-- Cubic approximation of the arcsine input. -/
def phaseInputPoly3 (m k ε : ℝ) : ℝ :=
  energy m k * ε + radialCoeff m k * ε^3

theorem tendsto_radial (m k : ℝ) :
    Tendsto (radial m k) (𝓝[>] 0) (𝓝 (energy m k)) := by
  have h := (tendsto_sinQ m k).sqrt
  change Tendsto (fun ε => Real.sqrt (sinQ m k ε)) (𝓝[>] 0) (𝓝 (energy m k))
  simpa [Real.sqrt_sq (energy_nonneg m k)] using h

/-- The normalized sine square differs from `E²` by `O(ε²)`. -/
theorem sinQ_sub_energy_sq_isBigO (m k : ℝ) :
    (fun ε => sinQ m k ε - energy m k ^ 2) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have hrem4 := sinQ_expansion_isBigO m k
  have hrem2 : (fun ε => sinQ m k ε - sinQPoly2 m k ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) :=
    hrem4.trans ((isLittleO_pow_pow (by omega : 2 < 4)).isBigO.mono nhdsWithin_le_nhds)
  have hquad := (isBigO_refl (fun ε : ℝ => ε^2) (𝓝[>] 0)).const_mul_left
    (-shellSqQuartic m k)
  exact (hrem2.add hquad).congr_left (by
    intro ε
    dsimp [sinQPoly2]
    ring)

/-- The rationalizing denominator is uniformly bounded below by the positive continuum energy. -/
theorem eventually_radial_add_energy_abs_ge {m k : ℝ} (hE : energy m k ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0, energy m k ≤ |radial m k ε + energy m k| := by
  have hEp : 0 < energy m k := lt_of_le_of_ne (energy_nonneg m k) (Ne.symm hE)
  filter_upwards with ε
  change energy m k ≤ |Real.sqrt (sinQ m k ε) + energy m k|
  rw [abs_of_nonneg (add_nonneg (Real.sqrt_nonneg _) hEp.le)]
  linarith [Real.sqrt_nonneg (sinQ m k ε)]

/-- Exact rationalization of the radial error near positive spacing. -/
theorem eventually_radial_rationalization {m k : ℝ} (hE : energy m k ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      radial m k ε - energy m k =
        (sinQ m k ε - energy m k ^ 2) /
          (radial m k ε + energy m k) := by
  filter_upwards [eventually_sinQ_pos hE] with ε hq
  have hEp : 0 < energy m k := lt_of_le_of_ne (energy_nonneg m k) (Ne.symm hE)
  have hden : radial m k ε + energy m k ≠ 0 :=
    ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hEp)
  rw [eq_div_iff hden]
  have hrad_sq : radial m k ε ^ 2 = sinQ m k ε := by
    dsimp [radial]
    rw [Real.sq_sqrt hq.le]
  nlinarith

/-- The radial factor first differs from the continuum energy by `O(ε²)`. -/
theorem radial_sub_energy_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => radial m k ε - energy m k) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have hdiv := div_isBigO_of_eventually_abs_ge
    (sinQ_sub_energy_sq_isBigO m k)
    (lt_of_le_of_ne (energy_nonneg m k) (Ne.symm hE))
    (eventually_radial_add_energy_abs_ge hE)
  apply hdiv.congr'
  · filter_upwards [eventually_radial_rationalization hE] with ε hε
    exact hε.symm
  · exact Filter.Eventually.of_forall (fun _ => rfl)

/-- The exact square root has the required quadratic expansion. -/
theorem radial_expansion_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => radial m k ε - radialPoly2 m k ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) := by
  let E := energy m k
  let D := shellSqQuartic m k
  let d : ℝ → ℝ := fun ε => radial m k ε + E
  let R : ℝ → ℝ := fun ε => sinQ m k ε - (E^2 - D*ε^2)
  have hEp : 0 < E := lt_of_le_of_ne (energy_nonneg m k) (Ne.symm hE)
  have hR : R =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    simpa [R, E, D, sinQPoly2] using sinQ_expansion_isBigO m k
  have hd : ∀ᶠ ε in 𝓝[>] 0, E ≤ |d ε| := by
    simpa [d, E] using eventually_radial_add_energy_abs_ge hE
  have hfirst : (fun ε => R ε / d ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) :=
    div_isBigO_of_eventually_abs_ge hR hEp hd
  have hr2 : (fun ε => radial m k ε - E) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    simpa [E] using radial_sub_energy_isBigO hE
  have hp2 : (fun ε : ℝ => ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := isBigO_refl _ _
  have hnum := (hp2.mul hr2).const_mul_left (D / (2*E))
  have hsecond :
      (fun ε => (D / (2*E) * (ε^2 * (radial m k ε - E))) / d ε) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^4) := by
    have hnum4 :
        (fun ε => D / (2*E) * (ε^2 * (radial m k ε - E))) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^4) := by
      exact hnum.congr_right (by intro ε; ring)
    exact div_isBigO_of_eventually_abs_ge hnum4 hEp hd
  have hsum := hfirst.add hsecond
  apply hsum.congr'
  · filter_upwards [eventually_sinQ_pos hE] with ε hq
    have hden : d ε ≠ 0 := by
      dsimp [d, E]
      exact ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hEp)
    have h2E : 2*E ≠ 0 := mul_ne_zero (by norm_num) (ne_of_gt hEp)
    -- Re-establish the pointwise rationalization directly to avoid proof-term dependence.
    have hbase : radial m k ε - E = (sinQ m k ε - E^2) / d ε := by
      have hden' : radial m k ε + energy m k ≠ 0 := by
        exact ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hEp)
      simpa [d, E] using (show radial m k ε - energy m k =
        (sinQ m k ε - energy m k ^ 2) /
          (radial m k ε + energy m k) from by
            rw [eq_div_iff hden']
            have hrad_sq : radial m k ε ^ 2 = sinQ m k ε := by
              dsimp [radial]
              rw [Real.sq_sqrt hq.le]
            nlinarith)
    have hqdiff : sinQ m k ε - E^2 = (radial m k ε - E) * d ε := by
      exact ((eq_div_iff hden).mp hbase).symm
    change R ε / d ε +
      (D / (2*E) * (ε^2 * (radial m k ε - E))) / d ε =
        radial m k ε - (E + (-(D) / (2*E)) * ε^2)
    rw [← add_div]
    rw [div_eq_iff hden]
    have hRpoint : R ε = (radial m k ε - E) * d ε + D*ε^2 := by
      dsimp [R]
      calc
        sinQ m k ε - (E^2 - D*ε^2) = (sinQ m k ε - E^2) + D*ε^2 := by ring
        _ = (radial m k ε - E) * d ε + D*ε^2 := by rw [hqdiff]
    rw [hRpoint]
    field_simp [h2E]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)


/-- The exact arcsine input has the expected cubic expansion. -/
theorem phaseInput_expansion_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => phaseInput m k ε - phaseInputPoly3 m k ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^5) := by
  have hr := radial_expansion_isBigO hE
  have he : (fun ε : ℝ => ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) := isBigO_refl _ _
  have h := he.mul hr
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by
      dsimp [phaseInput, phaseInputPoly3, radialPoly2]
      ring))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- The exact arcsine input tends to zero. -/
theorem tendsto_phaseInput (m k : ℝ) :
    Tendsto (phaseInput m k) (𝓝[>] 0) (𝓝 0) := by
  have he : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
    tendsto_id.mono_left nhdsWithin_le_nhds
  change Tendsto (fun ε : ℝ => ε * radial m k ε) (𝓝[>] 0) (𝓝 0)
  simpa using he.mul (tendsto_radial m k)

/-- The exact arcsine input is `O(ε)`. -/
theorem phaseInput_isBigO (m k : ℝ) :
    phaseInput m k =O[𝓝[>] 0] (fun ε : ℝ => ε) := by
  have hr : radial m k =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) :=
    (tendsto_radial m k).isBigO_one ℝ
  have he : (fun ε : ℝ => ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) := isBigO_refl _ _
  have h := he.mul hr
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by simp [phaseInput]))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- Removing only the linear continuum term leaves `O(ε³)`. -/
theorem phaseInput_sub_linear_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => phaseInput m k ε - energy m k * ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^3) := by
  have hrem5 := phaseInput_expansion_isBigO hE
  have hrem3 :
      (fun ε => phaseInput m k ε - phaseInputPoly3 m k ε) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^3) :=
    hrem5.trans ((isLittleO_pow_pow (by omega : 3 < 5)).isBigO.mono nhdsWithin_le_nhds)
  have hcubic := (isBigO_refl (fun ε : ℝ => ε^3) (𝓝[>] 0)).const_mul_left
    (radialCoeff m k)
  exact (hrem3.add hcubic).congr_left (by
    intro ε
    dsimp [phaseInputPoly3]
    ring)

/-- The cube of the exact input differs from the continuum cube by `O(ε⁵)`. -/
theorem phaseInput_cube_expansion_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => phaseInput m k ε ^ 3 - (energy m k * ε)^3) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^5) := by
  have hdiff := phaseInput_sub_linear_isBigO hE
  have hx := phaseInput_isBigO m k
  have hlin : (fun ε : ℝ => energy m k * ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
    (isBigO_refl (fun ε : ℝ => ε) (𝓝[>] 0)).const_mul_left (energy m k)
  have hx2 := hx.pow 2
  have hxlin0 := hx.mul hlin
  have hxlin : (fun ε => phaseInput m k ε * (energy m k * ε)) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := hxlin0.congr_right (by intro ε; ring)
  have hlin2 := hlin.pow 2
  have hfactor :
      (fun ε => phaseInput m k ε ^ 2 + phaseInput m k ε * (energy m k * ε) +
        (energy m k * ε)^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    have hsum := (hx2.add hxlin).add hlin2
    exact hsum.congr_right (by intro ε; ring)
  have h := hdiff.mul hfactor
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- The cubic phase coefficient simplifies to the manuscript correction. -/
theorem radialCoeff_add_energy_cube {m k : ℝ} (hE : energy m k ≠ 0) :
    radialCoeff m k + energy m k ^ 3 / 6 = correction m k := by
  rw [radialCoeff, shellSqQuartic, correction]
  field_simp [hE]
  ring

/-- The exact principal phase has the manuscript's cubic expansion. -/
theorem principalPhase_expansion_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => principalPhase m k ε -
      (energy m k * ε + correction m k * ε^3)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^5) := by
  have harc0 := arcsin_cubic_expansion_isBigO.comp_tendsto (tendsto_phaseInput m k)
  have harc :
      (fun ε => Real.arcsin (phaseInput m k ε) - phaseInput m k ε -
        phaseInput m k ε ^ 3 / 6) =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
    have hp := (phaseInput_isBigO m k).pow 5
    exact harc0.trans hp
  have hin := phaseInput_expansion_isBigO hE
  have hcube := phaseInput_cube_expansion_isBigO hE
  have hcube6 :
      (fun ε => (phaseInput m k ε ^ 3 - (energy m k * ε)^3) / 6) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^5) := by
    have h := hcube.const_mul_left (1/6 : ℝ)
    exact h.congr_left (by intro ε; ring)
  have hsum := (harc.add hin).add hcube6
  have hphaseArcsin : ∀ᶠ ε in 𝓝[>] 0,
      principalPhase m k ε = Real.arcsin (phaseInput m k ε) := by
    filter_upwards [self_mem_nhdsWithin, eventually_shell_pos m k] with ε hε hs
    simpa [phaseInput] using principalPhase_eq_arcsin_spacing_radial hε hs
  apply hsum.congr'
  · filter_upwards [hphaseArcsin] with ε heq
    rw [heq]
    rw [← radialCoeff_add_energy_cube hE]
    dsimp [phaseInputPoly3]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)


/-- Equation (8.11): the actual positive-branch frequency has the checked fourth-order remainder. -/
theorem positiveFrequency_expansion_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => positiveFrequency m k ε - frequencyPoly2 m k ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) := by
  have hdiv := div_linear_isBigO_positive (principalPhase_expansion_isBigO hE)
  apply hdiv.congr'
  · filter_upwards [self_mem_nhdsWithin] with ε hε
    have hne : ε ≠ 0 := ne_of_gt hε
    rw [positiveFrequency_of_pos m k ε hε, principalFrequency]
    dsimp [frequencyPoly2]
    field_simp [hne]
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The exact positive-branch frequency tends to the continuum energy. -/
theorem tendsto_positiveFrequency {m k : ℝ} (hE : energy m k ≠ 0) :
    Tendsto (positiveFrequency m k) (𝓝[>] 0) (𝓝 (energy m k)) := by
  have herr := (positiveFrequency_expansion_isBigO hE).trans_tendsto (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 4)
  have hpoly : Tendsto (frequencyPoly2 m k) (𝓝[>] 0) (𝓝 (energy m k)) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε => energy m k + correction m k * ε^2)
      (𝓝[>] 0) (𝓝 (energy m k))
    convert tendsto_const_nhds.add (tendsto_const_nhds.mul (hid.pow 2)) using 1
    all_goals ring
  have hsum := herr.add hpoly
  simpa using Tendsto.congr' (Filter.Eventually.of_forall (fun ε => by ring)) hsum

/-- The difference of exact and polynomial frequency squares is `O(ε⁴)`. -/
theorem positiveFrequency_sq_sub_poly_sq_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => positiveFrequency m k ε ^ 2 - frequencyPoly2 m k ε ^ 2) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) := by
  have hdiff := positiveFrequency_expansion_isBigO hE
  have hsumT := (tendsto_positiveFrequency hE).add (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε => energy m k + correction m k * ε^2)
      (𝓝[>] 0) (𝓝 (energy m k))
    convert tendsto_const_nhds.add (tendsto_const_nhds.mul (hid.pow 2)) using 1
    all_goals ring)
  have hsum : (fun ε => positiveFrequency m k ε + frequencyPoly2 m k ε) =O[𝓝[>] 0]
      (fun _ : ℝ => (1 : ℝ)) := hsumT.isBigO_one ℝ
  have h := hdiff.mul hsum
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- Equation (8.12): the exact frequency has the source mass-shell defect. -/
theorem positiveFrequency_mass_shell_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => positiveFrequency m k ε ^ 2 - k^2 - m^2 -
      (-(m^2*k^2)/3 * ε^2)) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have hsq := positiveFrequency_sq_sub_poly_sq_isBigO hE
  have hpoly :
      (fun ε => frequencyPoly2 m k ε ^ 2 - k^2 - m^2 -
        (-(m^2*k^2)/3 * ε^2)) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    have h := (isBigO_refl (fun ε : ℝ => ε^4) (𝓝[>] 0)).const_mul_left
      (correction m k ^ 2)
    exact h.congr_left (by
      intro ε
      rw [frequencyPoly2_sq_mass_shell hE]
      ring)
  exact (hsq.add hpoly).congr_left (by intro ε; ring)


/-- The elementary sine residual is cubic. -/
theorem sin_sub_id_isBigO_cube :
    (fun x : ℝ => Real.sin x - x) =O[𝓝 0] (fun x : ℝ => x^3) := by
  have h5to3 : (fun x : ℝ => x^5) =O[𝓝 0] (fun x : ℝ => x^3) :=
    (isLittleO_pow_pow (by omega : 3 < 5)).isBigO
  have hrem := sin_cubic_expansion_isBigO.trans h5to3
  have hcubic := (isBigO_refl (fun x : ℝ => x^3) (𝓝 0)).const_mul_left (-1/6 : ℝ)
  exact (hrem.add hcubic).congr_left (by intro x; dsimp [sinPoly3]; ring)

/-- The elementary cosine residual is quadratic. -/
theorem cos_sub_one_isBigO_sq :
    (fun x : ℝ => Real.cos x - 1) =O[𝓝 0] (fun x : ℝ => x^2) := by
  have hs : Real.sin =O[𝓝 0] (fun x : ℝ => x) := by
    have hd : HasDerivAt Real.sin 1 0 := by simpa using Real.hasDerivAt_sin 0
    have hl : (fun x : ℝ => Real.sin x - x) =O[𝓝 0] (fun x : ℝ => x) := by
      simpa using hd.isLittleO.isBigO
    have hid := isBigO_refl (fun x : ℝ => x) (𝓝 0)
    exact (hl.add hid).congr_left (by intro x; ring)
  have ht : Tendsto (fun x : ℝ => x/2) (𝓝 0) (𝓝 0) := by
    simpa using (continuous_id.div_const 2).tendsto (0 : ℝ)
  have hc := hs.comp_tendsto ht
  have hhalf : (fun x : ℝ => x/2) =O[𝓝 0] (fun x : ℝ => x) := by
    have h := (isBigO_refl (fun x : ℝ => x) (𝓝 0)).const_mul_left (1/2 : ℝ)
    exact h.congr_left (by intro x; ring)
  have hsin : (fun x : ℝ => Real.sin (x/2)) =O[𝓝 0] (fun x : ℝ => x) := by
    exact (hc.congr_left (by intro x; rfl)).trans hhalf
  have hsq := hsin.pow 2
  have h := hsq.const_mul_left (-2 : ℝ)
  exact h.congr' (Filter.Eventually.of_forall (fun x => by
      have hcos := Real.cos_two_mul' (x/2)
      have hx : 2 * (x/2) = x := by ring
      rw [hx] at hcos
      nlinarith [Real.sin_sq (x/2)]))
    (Filter.Eventually.of_forall (fun x => by ring))

/-- The removable sine quotient, normalized at zero. -/
def sinQuot (k ε : ℝ) : ℝ := if ε = 0 then k else Real.sin (k*ε) / ε

@[simp] theorem sinQuot_zero (k : ℝ) : sinQuot k 0 = k := by simp [sinQuot]

theorem sinQuot_of_pos (k ε : ℝ) (hε : 0 < ε) :
    sinQuot k ε = Real.sin (k*ε) / ε := by simp [sinQuot, ne_of_gt hε]

/-- The normalized sine quotient approaches momentum with quadratic error. -/
theorem sinQuot_expansion_isBigO (k : ℝ) :
    (fun ε => sinQuot k ε - k) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  have ht : Tendsto (fun ε : ℝ => k*ε) (𝓝[>] 0) (𝓝 0) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using tendsto_const_nhds.mul hid
  have hcomp := sin_sub_id_isBigO_cube.comp_tendsto ht
  have hkpow : (fun ε : ℝ => (k*ε)^3) =O[𝓝[>] 0] (fun ε : ℝ => ε^3) := by
    have h := (isBigO_refl (fun ε : ℝ => ε^3) (𝓝[>] 0)).const_mul_left (k^3)
    exact h.congr_left (by intro ε; ring)
  have hnum : (fun ε => Real.sin (k*ε) - k*ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^3) :=
    hcomp.trans hkpow
  have hdiv := div_cube_isBigO_square_positive hnum
  apply hdiv.congr'
  · filter_upwards [self_mem_nhdsWithin] with ε hε
    have hne : ε ≠ 0 := ne_of_gt hε
    rw [sinQuot_of_pos k ε hε]
    field_simp [hne]
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The cosine factor differs from one quadratically after scaling. -/
theorem scaled_cos_sub_one_isBigO (m : ℝ) :
    (fun ε => Real.cos (m*ε) - 1) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  have ht : Tendsto (fun ε : ℝ => m*ε) (𝓝[>] 0) (𝓝 0) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using tendsto_const_nhds.mul hid
  have hcomp := cos_sub_one_isBigO_sq.comp_tendsto ht
  have hpow : (fun ε : ℝ => (m*ε)^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    have h := (isBigO_refl (fun ε : ℝ => ε^2) (𝓝[>] 0)).const_mul_left (m^2)
    exact h.congr_left (by intro ε; ring)
  exact hcomp.trans hpow

/-- Momentum numerator normalized by the spacing. -/
def normalizedVelocityNumerator (m k ε : ℝ) : ℝ :=
  Real.cos (m*ε) * sinQuot k ε

/-- The normalized exact numerator differs from `k` by `O(ε²)`. -/
theorem normalizedVelocityNumerator_expansion_isBigO (m k : ℝ) :
    (fun ε => normalizedVelocityNumerator m k ε - k) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have hcosT : Tendsto (fun ε => Real.cos (m*ε)) (𝓝[>] 0) (𝓝 1) := by
    have hc : Continuous (fun ε : ℝ => Real.cos (m*ε)) :=
      Real.continuous_cos.comp (continuous_const.mul continuous_id)
    simpa using (hc.tendsto 0).mono_left nhdsWithin_le_nhds
  have hcosO : (fun ε => Real.cos (m*ε)) =O[𝓝[>] 0] (fun _ : ℝ => (1:ℝ)) :=
    hcosT.isBigO_one ℝ
  have hsq0 := hcosO.mul (sinQuot_expansion_isBigO k)
  have hsq :
      (fun ε => Real.cos (m*ε) * (sinQuot k ε - k)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := by
    exact hsq0.congr_right (by intro ε; ring)
  have hsecond := (scaled_cos_sub_one_isBigO m).const_mul_left k
  exact (hsq.add hsecond).congr_left (by
    intro ε
    dsimp [normalizedVelocityNumerator]
    ring)

/-- Total exact group-velocity expression; the zero value is the continuum limit. -/
def positiveGroupVelocity (m k ε : ℝ) : ℝ :=
  if ε = 0 then k / energy m k else
    Real.cos (m*ε) * Real.sin (k*ε) / Real.sin (principalPhase m k ε)

@[simp] theorem positiveGroupVelocity_zero (m k : ℝ) :
    positiveGroupVelocity m k 0 = k / energy m k := by simp [positiveGroupVelocity]

/-- Eventually the exact group-velocity expression is normalized numerator divided by radial factor. -/
theorem eventually_positiveGroupVelocity_eq_normalized_div {m k : ℝ}
    (hE : energy m k ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      positiveGroupVelocity m k ε = normalizedVelocityNumerator m k ε / radial m k ε := by
  filter_upwards [self_mem_nhdsWithin, eventually_sinQ_pos hE] with ε hε hq
  have hne : ε ≠ 0 := ne_of_gt hε
  have hrne : radial m k ε ≠ 0 := by
    dsimp [radial]
    exact Real.sqrt_ne_zero'.mpr hq
  simp [positiveGroupVelocity, hne]
  rw [sin_principalPhase_eq_spacing_radial m k ε hε]
  simp only [normalizedVelocityNumerator, sinQuot_of_pos k ε hε]
  field_simp [hne, hrne]

/-- Equation (8.14): exact group velocity approaches `k/E` with quadratic error. -/
theorem positiveGroupVelocity_expansion_isBigO {m k : ℝ} (hE : energy m k ≠ 0) :
    (fun ε => positiveGroupVelocity m k ε - k / energy m k) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  let E := energy m k
  let N := normalizedVelocityNumerator m k
  let r := radial m k
  have hEp : 0 < E := lt_of_le_of_ne (energy_nonneg m k) (Ne.symm hE)
  have hN : (fun ε => N ε - k) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    simpa [N] using normalizedVelocityNumerator_expansion_isBigO m k
  have hr : (fun ε => r ε - E) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    simpa [r, E] using radial_sub_energy_isBigO hE
  have hnum : (fun ε => E*(N ε-k) - k*(r ε-E)) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) :=
    (hN.const_mul_left E).sub (hr.const_mul_left k)
  have hrLower : ∀ᶠ ε in 𝓝[>] 0, E/2 < r ε := by
    have hmem : Set.Ioi (E/2) ∈ 𝓝 E := Ioi_mem_nhds (by linarith)
    have hev := (tendsto_radial m k).eventually hmem
    simpa [r, E] using hev
  have hden : ∀ᶠ ε in 𝓝[>] 0, E^2/2 ≤ |E*r ε| := by
    filter_upwards [hrLower] with ε hrl
    rw [abs_of_pos (mul_pos hEp (lt_trans (by linarith) hrl))]
    nlinarith
  have hquot := div_isBigO_of_eventually_abs_ge hnum (by positivity : 0 < E^2/2) hden
  apply hquot.congr'
  · filter_upwards [eventually_positiveGroupVelocity_eq_normalized_div hE, hrLower] with ε hv hrl
    rw [hv]
    have hrne : r ε ≠ 0 := ne_of_gt (lt_trans (by linarith) hrl)
    have hE' : E ≠ 0 := by simpa [E] using hE
    change (E * (N ε - k) - k * (r ε - E)) / (E * r ε) =
      N ε / r ε - k / E
    field_simp [hE', hrne]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)


/-- Nondegenerate continuum energy places the exact shell strictly inside `(-1,1)` eventually. -/
theorem eventually_abs_shell_lt_one {m k : ℝ} (hE : energy m k ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0, |shell m k ε| < 1 := by
  filter_upwards [self_mem_nhdsWithin, eventually_sinQ_pos hE] with ε hε hq
  have hfac := one_sub_shell_sq_eq m k ε hε
  have hpos : 0 < 1 - shell m k ε ^ 2 := by
    rw [hfac]
    exact mul_pos (sq_pos_of_pos hε) hq
  exact (sq_lt_one_iff_abs_lt_one (shell m k ε)).mp (by linarith)

/-- The exact velocity expression is the actual momentum derivative eventually. -/
theorem eventually_hasDerivAt_positiveGroupVelocity {m k : ℝ} (hE : energy m k ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      HasDerivAt (fun q => positiveFrequency m q ε)
        (positiveGroupVelocity m k ε) k := by
  filter_upwards [self_mem_nhdsWithin, eventually_abs_shell_lt_one hE] with ε hε hint
  have hεpos : 0 < ε := hε
  have hne : ε ≠ 0 := ne_of_gt hεpos
  have h := KomorebiPhysics.Relativistic1DGroupVelocity.hasDerivAt_principalFrequency
    m k ε hne hint
  have hfreq : (fun q => positiveFrequency m q ε) =
      (fun q => principalFrequency m q ε hne) := by
    funext q
    simp [positiveFrequency, hne]
  rw [hfreq]
  convert h using 1
  simp [positiveGroupVelocity, hne]
  rw [KomorebiPhysics.Relativistic1DGroupVelocity.principalFrequency_mul_spacing]

end
end KomorebiPhysics.Relativistic1DContinuumLimit
