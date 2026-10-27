module

public import KomorebiPhysics.Relativistic3DShellAsymptotics
public import KomorebiPhysics.Relativistic1DContinuumLimit
public import Mathlib.Analysis.Asymptotics.Ring

/-!
Positive-spacing continuum inversion for the exact three-dimensional shell.

The branch discipline follows the already-checked one-dimensional construction:
first normalize the principal sine, then take its positive square root, rewrite
the principal phase as an arcsine near positive zero, and only then divide by
the spacing.  This proves the three-dimensional correction rather than assuming
an inverse-cosine series.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DContinuumLimit

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.DiracWalk3D
open KomorebiPhysics.Dispersion3D
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic1DContinuumLimit

/-- Quartic coefficient in the square of the exact 3D shell. -/
def shellSqQuartic3 (m kx ky kz : ℝ) : ℝ :=
  (energy3 m kx ky kz ^ 4 + anisotropyQ m kx ky kz) / 3

/-- Fourth-order polynomial for the square of the exact 3D shell. -/
def shellSqPoly4_3 (m kx ky kz ε : ℝ) : ℝ :=
  1 - energy3 m kx ky kz ^ 2 * ε^2 +
    shellSqQuartic3 m kx ky kz * ε^4

/-- The squared quartic approximant has only sixth- and eighth-order residuals. -/
theorem shell3_poly_sq_error_isBigO (m kx ky kz : ℝ) :
    (fun ε => shellPoly4_3 m kx ky kz ε ^ 2 -
      shellSqPoly4_3 m kx ky kz ε) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^6) := by
  let E := energy3 m kx ky kz
  let B := shellQuarticCoeffSource3 m kx ky kz
  have h6 : (fun ε : ℝ => ε^6) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
    isBigO_refl _ _
  have h8 : (fun ε : ℝ => ε^8) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
    pow8_isBigO_pow6_positive
  have hsum := (h6.const_mul_left (-(E^2 * B))).add
    (h8.const_mul_left (B^2))
  exact hsum.congr_left (by
    intro ε
    dsimp [E, B, shellPoly4_3, shellSqPoly4_3, shellSqQuartic3,
      shellQuarticCoeffSource3]
    ring)

/-- The exact squared shell has the checked fourth-order expansion. -/
theorem shell3_sq_expansion_isBigO (m kx ky kz : ℝ) :
    (fun ε => shell m kx ky kz ε ^ 2 - shellSqPoly4_3 m kx ky kz ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
  let p : ℝ → ℝ := fun ε => shellPoly4_3 m kx ky kz ε
  have hr : (fun ε => shell m kx ky kz ε - p ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
    exact (shell3_expansion_isBigO m kx ky kz).mono nhdsWithin_le_nhds
  have hshell : Tendsto (fun ε => shell m kx ky kz ε) (𝓝[>] 0) (𝓝 1) := by
    have hm : Continuous (fun ε : ℝ => Real.cos (m * ε)) :=
      Real.continuous_cos.comp (continuous_const.mul continuous_id)
    have hx : Continuous (fun ε : ℝ => Real.cos (kx * ε)) :=
      Real.continuous_cos.comp (continuous_const.mul continuous_id)
    have hy : Continuous (fun ε : ℝ => Real.cos (ky * ε)) :=
      Real.continuous_cos.comp (continuous_const.mul continuous_id)
    have hz : Continuous (fun ε : ℝ => Real.cos (kz * ε)) :=
      Real.continuous_cos.comp (continuous_const.mul continuous_id)
    have hfull : Tendsto (fun ε => shell m kx ky kz ε) (𝓝 0) (𝓝 1) := by
      change Tendsto
        ((((fun ε : ℝ => Real.cos (m * ε)) *
          (fun ε : ℝ => Real.cos (kx * ε))) *
          (fun ε : ℝ => Real.cos (ky * ε))) *
          (fun ε : ℝ => Real.cos (kz * ε))) (𝓝 0) (𝓝 1)
      simpa using (((hm.mul hx).mul hy).mul hz).tendsto 0
    exact hfull.mono_left nhdsWithin_le_nhds
  have hp : Tendsto p (𝓝[>] 0) (𝓝 1) := by
    dsimp [p, shellPoly4_3]
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    convert (tendsto_const_nhds.sub
      ((tendsto_const_nhds.mul (hid.pow 2)).div_const 2)).add
        (tendsto_const_nhds.mul (hid.pow 4)) using 1
    all_goals ring
  have hbounded : (fun ε => shell m kx ky kz ε + p ε) =O[𝓝[>] 0]
      (fun _ : ℝ => (1 : ℝ)) := (hshell.add hp).isBigO_one ℝ
  have hprod := hr.mul hbounded
  have hprod6 :
      (fun ε => (shell m kx ky kz ε - p ε) *
        (shell m kx ky kz ε + p ε)) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^6) := by
    exact hprod.congr_right (by intro ε; simp)
  have hpoly := shell3_poly_sq_error_isBigO m kx ky kz
  exact (hprod6.add hpoly).congr_left (by
    intro ε
    dsimp [p]
    ring)

/-- Normalized square of the exact principal sine. -/
def sinQ3 (m kx ky kz ε : ℝ) : ℝ :=
  if ε = 0 then energy3 m kx ky kz ^ 2
  else (1 - shell m kx ky kz ε ^ 2) / ε^2

/-- Second-order normalized sine-square approximant. -/
def sinQPoly2_3 (m kx ky kz ε : ℝ) : ℝ :=
  energy3 m kx ky kz ^ 2 - shellSqQuartic3 m kx ky kz * ε^2

@[simp] theorem sinQ3_zero (m kx ky kz : ℝ) :
    sinQ3 m kx ky kz 0 = energy3 m kx ky kz ^ 2 := by
  simp [sinQ3]

theorem sinQ3_of_pos (m kx ky kz ε : ℝ) (hε : 0 < ε) :
    sinQ3 m kx ky kz ε = (1 - shell m kx ky kz ε ^ 2) / ε^2 := by
  simp [sinQ3, ne_of_gt hε]

/-- Dividing by the positive squared spacing gives the normalized `O(ε⁴)` remainder. -/
theorem sinQ3_expansion_isBigO (m kx ky kz : ℝ) :
    (fun ε => sinQ3 m kx ky kz ε - sinQPoly2_3 m kx ky kz ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have hdiv := div_sq_isBigO_positive (shell3_sq_expansion_isBigO m kx ky kz)
  have hneg := hdiv.const_mul_left (-1 : ℝ)
  apply hneg.congr'
  · filter_upwards [self_mem_nhdsWithin] with ε hε
    have hne : ε ≠ 0 := ne_of_gt hε
    rw [sinQ3_of_pos m kx ky kz ε hε]
    dsimp [sinQPoly2_3, shellSqPoly4_3]
    field_simp [hne]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The normalized sine square converges to the continuum energy squared. -/
theorem tendsto_sinQ3 (m kx ky kz : ℝ) :
    Tendsto (sinQ3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (energy3 m kx ky kz ^ 2)) := by
  have herr := (sinQ3_expansion_isBigO m kx ky kz).trans_tendsto (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 4)
  have hpoly : Tendsto (sinQPoly2_3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (energy3 m kx ky kz ^ 2)) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε : ℝ => energy3 m kx ky kz ^ 2 -
      shellSqQuartic3 m kx ky kz * ε^2) (𝓝[>] 0)
        (𝓝 (energy3 m kx ky kz ^ 2))
    convert tendsto_const_nhds.sub (tendsto_const_nhds.mul (hid.pow 2)) using 1
    all_goals ring
  have hsum := herr.add hpoly
  simpa using Tendsto.congr' (Filter.Eventually.of_forall (fun ε => by ring)) hsum

/-- Exact factorization of `1-shell²` on positive spacings. -/
theorem one_sub_shell3_sq_eq (m kx ky kz ε : ℝ) (hε : 0 < ε) :
    1 - shell m kx ky kz ε ^ 2 = ε^2 * sinQ3 m kx ky kz ε := by
  rw [sinQ3_of_pos m kx ky kz ε hε]
  field_simp [ne_of_gt hε]

/-- Nonzero continuum energy makes the normalized sine square eventually positive. -/
theorem eventually_sinQ3_pos {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0, 0 < sinQ3 m kx ky kz ε := by
  have hE2 : 0 < energy3 m kx ky kz ^ 2 := sq_pos_of_ne_zero hE
  have hmem : Set.Ioi (energy3 m kx ky kz ^ 2 / 2) ∈
      𝓝 (energy3 m kx ky kz ^ 2) := by
    exact Ioi_mem_nhds (by linarith)
  filter_upwards [(tendsto_sinQ3 m kx ky kz) hmem] with ε hε
  exact lt_trans (by positivity : 0 < energy3 m kx ky kz ^ 2 / 2) hε

/-- Positive square-root factor in the exact principal sine. -/
def radial3 (m kx ky kz ε : ℝ) : ℝ := Real.sqrt (sinQ3 m kx ky kz ε)

/-- The exact 3D shell tends to one on the positive-spacing filter. -/
theorem tendsto_shell3_positive (m kx ky kz : ℝ) :
    Tendsto (fun ε => shell m kx ky kz ε) (𝓝[>] 0) (𝓝 1) := by
  have hm : Continuous (fun ε : ℝ => Real.cos (m * ε)) :=
    Real.continuous_cos.comp (continuous_const.mul continuous_id)
  have hx : Continuous (fun ε : ℝ => Real.cos (kx * ε)) :=
    Real.continuous_cos.comp (continuous_const.mul continuous_id)
  have hy : Continuous (fun ε : ℝ => Real.cos (ky * ε)) :=
    Real.continuous_cos.comp (continuous_const.mul continuous_id)
  have hz : Continuous (fun ε : ℝ => Real.cos (kz * ε)) :=
    Real.continuous_cos.comp (continuous_const.mul continuous_id)
  have hfull : Tendsto (fun ε => shell m kx ky kz ε) (𝓝 0) (𝓝 1) := by
    change Tendsto
      ((((fun ε : ℝ => Real.cos (m * ε)) *
        (fun ε : ℝ => Real.cos (kx * ε))) *
        (fun ε : ℝ => Real.cos (ky * ε))) *
        (fun ε : ℝ => Real.cos (kz * ε))) (𝓝 0) (𝓝 1)
    simpa using (((hm.mul hx).mul hy).mul hz).tendsto 0
  exact hfull.mono_left nhdsWithin_le_nhds

/-- Near positive zero the shell is on the positive half of the principal branch. -/
theorem eventually_shell3_pos (m kx ky kz : ℝ) :
    ∀ᶠ ε in 𝓝[>] 0, 0 < shell m kx ky kz ε := by
  exact (tendsto_shell3_positive m kx ky kz)
    (Ioi_mem_nhds (by norm_num : (0 : ℝ) < 1))

/-- The principal sine is spacing times the positive radial factor. -/
theorem sin_phase3_eq_spacing_radial (m kx ky kz ε : ℝ) (hε : 0 < ε) :
    Real.sin (phase m kx ky kz ε) = ε * radial3 m kx ky kz ε := by
  rw [phase, Real.sin_arccos]
  rw [one_sub_shell3_sq_eq m kx ky kz ε hε]
  rw [Real.sqrt_mul (sq_nonneg ε)]
  rw [Real.sqrt_sq hε.le]
  rfl

/-- On the positive-shell branch the principal phase is an ordinary arcsine. -/
theorem phase3_eq_arcsin_spacing_radial {m kx ky kz ε : ℝ}
    (hε : 0 < ε) (hs : 0 < shell m kx ky kz ε) :
    phase m kx ky kz ε = Real.arcsin (ε * radial3 m kx ky kz ε) := by
  have hlo : -(Real.pi / 2) ≤ phase m kx ky kz ε := by
    have hp := phase_nonneg m kx ky kz ε
    have hpi : 0 < Real.pi := Real.pi_pos
    linarith
  have hhi : phase m kx ky kz ε ≤ Real.pi / 2 :=
    Real.arccos_le_pi_div_two.mpr hs.le
  calc
    phase m kx ky kz ε = Real.arcsin (Real.sin (phase m kx ky kz ε)) :=
      (Real.arcsin_sin hlo hhi).symm
    _ = Real.arcsin (ε * radial3 m kx ky kz ε) := by
      rw [sin_phase3_eq_spacing_radial m kx ky kz ε hε]

/-- Total positive-branch frequency, continuously filled at zero. -/
def positiveFrequency3 (m kx ky kz ε : ℝ) : ℝ :=
  if ε = 0 then energy3 m kx ky kz else frequency m kx ky kz ε

@[simp] theorem positiveFrequency3_zero (m kx ky kz : ℝ) :
    positiveFrequency3 m kx ky kz 0 = energy3 m kx ky kz := by
  simp [positiveFrequency3]

theorem positiveFrequency3_of_pos (m kx ky kz ε : ℝ) (hε : 0 < ε) :
    positiveFrequency3 m kx ky kz ε = frequency m kx ky kz ε := by
  simp [positiveFrequency3, ne_of_gt hε]

/-- Eventually the exact frequency is the arcsine quotient of the radial factor. -/
theorem eventually_positiveFrequency3_eq_arcsin_div (m kx ky kz : ℝ) :
    ∀ᶠ ε in 𝓝[>] 0,
      positiveFrequency3 m kx ky kz ε =
        Real.arcsin (ε * radial3 m kx ky kz ε) / ε := by
  filter_upwards [self_mem_nhdsWithin, eventually_shell3_pos m kx ky kz]
    with ε hε hs
  rw [positiveFrequency3_of_pos m kx ky kz ε hε, frequency]
  rw [phase3_eq_arcsin_spacing_radial hε hs]

/-- Quadratic radial coefficient. -/
def radialCoeff3 (m kx ky kz : ℝ) : ℝ :=
  -(shellSqQuartic3 m kx ky kz) / (2 * energy3 m kx ky kz)

/-- Quadratic radial approximant. -/
def radialPoly2_3 (m kx ky kz ε : ℝ) : ℝ :=
  energy3 m kx ky kz + radialCoeff3 m kx ky kz * ε^2

/-- Exact arcsine input. -/
def phaseInput3 (m kx ky kz ε : ℝ) : ℝ :=
  ε * radial3 m kx ky kz ε

/-- Cubic approximation to the arcsine input. -/
def phaseInputPoly3_3 (m kx ky kz ε : ℝ) : ℝ :=
  energy3 m kx ky kz * ε + radialCoeff3 m kx ky kz * ε^3

/-- The radial factor tends to the continuum energy. -/
theorem tendsto_radial3 (m kx ky kz : ℝ) :
    Tendsto (radial3 m kx ky kz) (𝓝[>] 0) (𝓝 (energy3 m kx ky kz)) := by
  have h := (tendsto_sinQ3 m kx ky kz).sqrt
  change Tendsto (fun ε => Real.sqrt (sinQ3 m kx ky kz ε)) (𝓝[>] 0)
    (𝓝 (energy3 m kx ky kz))
  simpa [Real.sqrt_sq (energy3_nonneg m kx ky kz)] using h

/-- The normalized sine square differs from `E²` by `O(ε²)`. -/
theorem sinQ3_sub_energy_sq_isBigO (m kx ky kz : ℝ) :
    (fun ε => sinQ3 m kx ky kz ε - energy3 m kx ky kz ^ 2)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  have hrem4 := sinQ3_expansion_isBigO m kx ky kz
  have hrem2 :
      (fun ε => sinQ3 m kx ky kz ε - sinQPoly2_3 m kx ky kz ε)
        =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    hrem4.trans ((isLittleO_pow_pow (by omega : 2 < 4)).isBigO.mono
      nhdsWithin_le_nhds)
  have hquad := (isBigO_refl (fun ε : ℝ => ε^2) (𝓝[>] 0)).const_mul_left
    (-shellSqQuartic3 m kx ky kz)
  exact (hrem2.add hquad).congr_left (by
    intro ε
    dsimp [sinQPoly2_3]
    ring)

/-- The rationalizing denominator is bounded below by the positive energy. -/
theorem eventually_radial3_add_energy_abs_ge {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      energy3 m kx ky kz ≤
        |radial3 m kx ky kz ε + energy3 m kx ky kz| := by
  have hEp : 0 < energy3 m kx ky kz :=
    lt_of_le_of_ne (energy3_nonneg m kx ky kz) (Ne.symm hE)
  filter_upwards with ε
  change energy3 m kx ky kz ≤
    |Real.sqrt (sinQ3 m kx ky kz ε) + energy3 m kx ky kz|
  rw [abs_of_nonneg (add_nonneg (Real.sqrt_nonneg _) hEp.le)]
  linarith [Real.sqrt_nonneg (sinQ3 m kx ky kz ε)]

/-- Exact rationalization of the radial error. -/
theorem eventually_radial3_rationalization {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      radial3 m kx ky kz ε - energy3 m kx ky kz =
        (sinQ3 m kx ky kz ε - energy3 m kx ky kz ^ 2) /
          (radial3 m kx ky kz ε + energy3 m kx ky kz) := by
  filter_upwards [eventually_sinQ3_pos hE] with ε hq
  have hEp : 0 < energy3 m kx ky kz :=
    lt_of_le_of_ne (energy3_nonneg m kx ky kz) (Ne.symm hE)
  have hden : radial3 m kx ky kz ε + energy3 m kx ky kz ≠ 0 :=
    ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hEp)
  rw [eq_div_iff hden]
  have hrad_sq : radial3 m kx ky kz ε ^ 2 = sinQ3 m kx ky kz ε := by
    dsimp [radial3]
    rw [Real.sq_sqrt hq.le]
  nlinarith

/-- The radial factor first differs from the continuum energy by `O(ε²)`. -/
theorem radial3_sub_energy_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => radial3 m kx ky kz ε - energy3 m kx ky kz)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  have hdiv := div_isBigO_of_eventually_abs_ge
    (sinQ3_sub_energy_sq_isBigO m kx ky kz)
    (lt_of_le_of_ne (energy3_nonneg m kx ky kz) (Ne.symm hE))
    (eventually_radial3_add_energy_abs_ge hE)
  apply hdiv.congr'
  · filter_upwards [eventually_radial3_rationalization hE] with ε hε
    exact hε.symm
  · exact Filter.Eventually.of_forall (fun _ => rfl)

/-- The exact square root has the required quadratic expansion. -/
theorem radial3_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => radial3 m kx ky kz ε - radialPoly2_3 m kx ky kz ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  let E := energy3 m kx ky kz
  let D := shellSqQuartic3 m kx ky kz
  let d : ℝ → ℝ := fun ε => radial3 m kx ky kz ε + E
  let R : ℝ → ℝ := fun ε => sinQ3 m kx ky kz ε - (E^2 - D*ε^2)
  have hEp : 0 < E :=
    lt_of_le_of_ne (energy3_nonneg m kx ky kz) (Ne.symm hE)
  have hR : R =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    simpa [R, E, D, sinQPoly2_3] using sinQ3_expansion_isBigO m kx ky kz
  have hd : ∀ᶠ ε in 𝓝[>] 0, E ≤ |d ε| := by
    simpa [d, E] using eventually_radial3_add_energy_abs_ge hE
  have hfirst : (fun ε => R ε / d ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) :=
    div_isBigO_of_eventually_abs_ge hR hEp hd
  have hr2 : (fun ε => radial3 m kx ky kz ε - E) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
    simpa [E] using radial3_sub_energy_isBigO hE
  have hp2 : (fun ε : ℝ => ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    isBigO_refl _ _
  have hnum := (hp2.mul hr2).const_mul_left (D / (2*E))
  have hsecond :
      (fun ε => (D / (2*E) *
        (ε^2 * (radial3 m kx ky kz ε - E))) / d ε) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^4) := by
    have hnum4 :
        (fun ε => D / (2*E) * (ε^2 * (radial3 m kx ky kz ε - E)))
          =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
      exact hnum.congr_right (by intro ε; ring)
    exact div_isBigO_of_eventually_abs_ge hnum4 hEp hd
  have hsum := hfirst.add hsecond
  apply hsum.congr'
  · filter_upwards [eventually_sinQ3_pos hE] with ε hq
    have hden : d ε ≠ 0 := by
      dsimp [d, E]
      exact ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hEp)
    have h2E : 2*E ≠ 0 := mul_ne_zero (by norm_num) (ne_of_gt hEp)
    have hbase : radial3 m kx ky kz ε - E =
        (sinQ3 m kx ky kz ε - E^2) / d ε := by
      have hden' : radial3 m kx ky kz ε + energy3 m kx ky kz ≠ 0 := by
        exact ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hEp)
      simpa [d, E] using (show
        radial3 m kx ky kz ε - energy3 m kx ky kz =
          (sinQ3 m kx ky kz ε - energy3 m kx ky kz ^ 2) /
            (radial3 m kx ky kz ε + energy3 m kx ky kz) from by
          rw [eq_div_iff hden']
          have hrad_sq : radial3 m kx ky kz ε ^ 2 =
              sinQ3 m kx ky kz ε := by
            dsimp [radial3]
            rw [Real.sq_sqrt hq.le]
          nlinarith)
    have hqdiff : sinQ3 m kx ky kz ε - E^2 =
        (radial3 m kx ky kz ε - E) * d ε := by
      exact ((eq_div_iff hden).mp hbase).symm
    change R ε / d ε +
      (D / (2*E) * (ε^2 * (radial3 m kx ky kz ε - E))) / d ε =
        radial3 m kx ky kz ε - (E + (-(D) / (2*E)) * ε^2)
    rw [← add_div]
    rw [div_eq_iff hden]
    have hRpoint : R ε =
        (radial3 m kx ky kz ε - E) * d ε + D*ε^2 := by
      dsimp [R]
      calc
        sinQ3 m kx ky kz ε - (E^2 - D*ε^2) =
            (sinQ3 m kx ky kz ε - E^2) + D*ε^2 := by ring
        _ = (radial3 m kx ky kz ε - E) * d ε + D*ε^2 := by rw [hqdiff]
    rw [hRpoint]
    field_simp [h2E]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The exact arcsine input has the expected cubic expansion. -/
theorem phaseInput3_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => phaseInput3 m kx ky kz ε - phaseInputPoly3_3 m kx ky kz ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
  have hr := radial3_expansion_isBigO hE
  have he : (fun ε : ℝ => ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
    isBigO_refl _ _
  have h := he.mul hr
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by
      dsimp [phaseInput3, phaseInputPoly3_3, radialPoly2_3]
      ring))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- The exact arcsine input tends to zero. -/
theorem tendsto_phaseInput3 (m kx ky kz : ℝ) :
    Tendsto (phaseInput3 m kx ky kz) (𝓝[>] 0) (𝓝 0) := by
  have he : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
    tendsto_id.mono_left nhdsWithin_le_nhds
  change Tendsto (fun ε : ℝ => ε * radial3 m kx ky kz ε) (𝓝[>] 0) (𝓝 0)
  simpa using he.mul (tendsto_radial3 m kx ky kz)

/-- The exact arcsine input is `O(ε)`. -/
theorem phaseInput3_isBigO (m kx ky kz : ℝ) :
    phaseInput3 m kx ky kz =O[𝓝[>] 0] (fun ε : ℝ => ε) := by
  have hr : radial3 m kx ky kz =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) :=
    (tendsto_radial3 m kx ky kz).isBigO_one ℝ
  have he : (fun ε : ℝ => ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
    isBigO_refl _ _
  have h := he.mul hr
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by simp [phaseInput3]))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- Removing the linear term leaves `O(ε³)`. -/
theorem phaseInput3_sub_linear_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => phaseInput3 m kx ky kz ε - energy3 m kx ky kz * ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^3) := by
  have hrem5 := phaseInput3_expansion_isBigO hE
  have hrem3 :
      (fun ε => phaseInput3 m kx ky kz ε - phaseInputPoly3_3 m kx ky kz ε)
        =O[𝓝[>] 0] (fun ε : ℝ => ε^3) :=
    hrem5.trans ((isLittleO_pow_pow (by omega : 3 < 5)).isBigO.mono
      nhdsWithin_le_nhds)
  have hcubic := (isBigO_refl (fun ε : ℝ => ε^3) (𝓝[>] 0)).const_mul_left
    (radialCoeff3 m kx ky kz)
  exact (hrem3.add hcubic).congr_left (by
    intro ε
    dsimp [phaseInputPoly3_3]
    ring)

/-- The cube of the exact input differs from the continuum cube by `O(ε⁵)`. -/
theorem phaseInput3_cube_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => phaseInput3 m kx ky kz ε ^ 3 -
      (energy3 m kx ky kz * ε)^3) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^5) := by
  have hdiff := phaseInput3_sub_linear_isBigO hE
  have hx := phaseInput3_isBigO m kx ky kz
  have hlin : (fun ε : ℝ => energy3 m kx ky kz * ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε) :=
    (isBigO_refl (fun ε : ℝ => ε) (𝓝[>] 0)).const_mul_left
      (energy3 m kx ky kz)
  have hx2 := hx.pow 2
  have hxlin0 := hx.mul hlin
  have hxlin :
      (fun ε => phaseInput3 m kx ky kz ε * (energy3 m kx ky kz * ε))
        =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    hxlin0.congr_right (by intro ε; ring)
  have hlin2 := hlin.pow 2
  have hfactor :
      (fun ε => phaseInput3 m kx ky kz ε ^ 2 +
        phaseInput3 m kx ky kz ε * (energy3 m kx ky kz * ε) +
        (energy3 m kx ky kz * ε)^2) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^2) := by
    have hsum := (hx2.add hxlin).add hlin2
    exact hsum.congr_right (by intro ε; ring)
  have h := hdiff.mul hfactor
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- The three-dimensional quadratic frequency correction. -/
def correction3 (m kx ky kz : ℝ) : ℝ :=
  -anisotropyQ m kx ky kz / (6 * energy3 m kx ky kz)

/-- Second-order continuum frequency approximant. -/
def frequencyPoly2_3 (m kx ky kz ε : ℝ) : ℝ :=
  energy3 m kx ky kz + correction3 m kx ky kz * ε^2

/-- The cubic phase coefficient simplifies exactly to `-Q/(6E)`. -/
theorem radialCoeff3_add_energy_cube {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    radialCoeff3 m kx ky kz + energy3 m kx ky kz ^ 3 / 6 =
      correction3 m kx ky kz := by
  rw [radialCoeff3, shellSqQuartic3, correction3]
  field_simp [hE]
  ring

/-- The principal 3D phase has the checked cubic expansion. -/
theorem phase3_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => phase m kx ky kz ε -
      (energy3 m kx ky kz * ε + correction3 m kx ky kz * ε^3))
        =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
  have harc0 := arcsin_cubic_expansion_isBigO.comp_tendsto
    (tendsto_phaseInput3 m kx ky kz)
  have harc :
      (fun ε => Real.arcsin (phaseInput3 m kx ky kz ε) -
        phaseInput3 m kx ky kz ε - phaseInput3 m kx ky kz ε ^ 3 / 6)
          =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
    have hp := (phaseInput3_isBigO m kx ky kz).pow 5
    exact harc0.trans hp
  have hin := phaseInput3_expansion_isBigO hE
  have hcube := phaseInput3_cube_expansion_isBigO hE
  have hcube6 :
      (fun ε => (phaseInput3 m kx ky kz ε ^ 3 -
        (energy3 m kx ky kz * ε)^3) / 6) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^5) := by
    have h := hcube.const_mul_left (1/6 : ℝ)
    exact h.congr_left (by intro ε; ring)
  have hsum := (harc.add hin).add hcube6
  have hphaseArcsin : ∀ᶠ ε in 𝓝[>] 0,
      phase m kx ky kz ε = Real.arcsin (phaseInput3 m kx ky kz ε) := by
    filter_upwards [self_mem_nhdsWithin, eventually_shell3_pos m kx ky kz]
      with ε hε hs
    simpa [phaseInput3] using phase3_eq_arcsin_spacing_radial hε hs
  apply hsum.congr'
  · filter_upwards [hphaseArcsin] with ε heq
    rw [heq]
    rw [← radialCoeff3_add_energy_cube hE]
    dsimp [phaseInputPoly3_3]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- Equation (8.33): the exact positive-branch 3D frequency has fourth-order remainder. -/
theorem positiveFrequency3_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => positiveFrequency3 m kx ky kz ε -
      frequencyPoly2_3 m kx ky kz ε) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^4) := by
  have hdiv := div_linear_isBigO_positive (phase3_expansion_isBigO hE)
  apply hdiv.congr'
  · filter_upwards [self_mem_nhdsWithin] with ε hε
    have hne : ε ≠ 0 := ne_of_gt hε
    rw [positiveFrequency3_of_pos m kx ky kz ε hε, frequency]
    dsimp [frequencyPoly2_3]
    field_simp [hne]
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The exact positive-branch 3D frequency tends to the continuum energy. -/
theorem tendsto_positiveFrequency3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    Tendsto (positiveFrequency3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (energy3 m kx ky kz)) := by
  have herr := (positiveFrequency3_expansion_isBigO hE).trans_tendsto (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 4)
  have hpoly : Tendsto (frequencyPoly2_3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (energy3 m kx ky kz)) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε => energy3 m kx ky kz +
      correction3 m kx ky kz * ε^2) (𝓝[>] 0)
        (𝓝 (energy3 m kx ky kz))
    convert tendsto_const_nhds.add (tendsto_const_nhds.mul (hid.pow 2)) using 1
    all_goals ring
  have hsum := herr.add hpoly
  simpa using Tendsto.congr' (Filter.Eventually.of_forall (fun ε => by ring)) hsum

end KomorebiPhysics.Relativistic3DContinuumLimit
