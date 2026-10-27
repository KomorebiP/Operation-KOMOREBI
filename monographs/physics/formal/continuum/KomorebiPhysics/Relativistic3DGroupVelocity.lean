module

public import KomorebiPhysics.Relativistic3DContinuumLimit
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.InverseDeriv

/-!
Exact component derivatives and continuum group-velocity limits for the
three-dimensional principal dispersion branch.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DGroupVelocity

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.DiracWalk3D
open KomorebiPhysics.Dispersion3D
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit
open KomorebiPhysics.Relativistic1DContinuumLimit

/-- Interior shell values are exactly the nonsingular points for arccos differentiation. -/
theorem shell3_ne_endpoints_of_abs_lt_one {m kx ky kz ε : ℝ}
    (h : |shell m kx ky kz ε| < 1) :
    shell m kx ky kz ε ≠ -1 ∧ shell m kx ky kz ε ≠ 1 := by
  constructor <;> intro heq <;> rw [heq] at h <;> norm_num at h

/-- Exact derivative of the 3D shell in the x-momentum component. -/
theorem hasDerivAt_shell_kx (m kx ky kz ε : ℝ) :
    HasDerivAt (fun q => shell m q ky kz ε)
      (-(Real.cos (m*ε) * Real.sin (kx*ε) *
        Real.cos (ky*ε) * Real.cos (kz*ε) * ε)) kx := by
  let A : ℝ := Real.cos (m*ε) * Real.cos (ky*ε) * Real.cos (kz*ε)
  have hlin : HasDerivAt (fun q : ℝ => q * ε) ε kx :=
    hasDerivAt_mul_const ε
  have hcos : HasDerivAt (fun q : ℝ => Real.cos (q * ε))
      (-Real.sin (kx * ε) * ε) kx := hlin.cos
  have hprod : HasDerivAt (fun q : ℝ => A * Real.cos (q * ε))
      (A * (-Real.sin (kx * ε) * ε)) kx := hcos.const_mul A
  have hfun :
      (fun q : ℝ => shell m q ky kz ε) =
        (fun q : ℝ => A * Real.cos (q * ε)) := by
    funext q
    dsimp [A, shell]
    ring
  rw [hfun]
  exact hprod.congr_deriv (by dsimp [A]; ring)


/-- The square-root denominator is the positive principal-branch sine. -/
theorem sqrt_one_sub_shell3_sq (m kx ky kz ε : ℝ) :
    Real.sqrt (1 - shell m kx ky kz ε ^ 2) =
      Real.sin (phase m kx ky kz ε) := by
  rw [← cos_phase m kx ky kz ε]
  symm
  exact Real.sin_eq_sqrt_one_sub_cos_sq
    (phase_nonneg m kx ky kz ε) (phase_le_pi m kx ky kz ε)

/-- Principal-frequency phase cancellation at nonzero spacing. -/
theorem frequency3_mul_spacing (m kx ky kz ε : ℝ) (hε : ε ≠ 0) :
    frequency m kx ky kz ε * ε = phase m kx ky kz ε := by
  rw [frequency]
  exact div_mul_cancel₀ _ hε

/-- Exact x-component derivative with the arccos square-root denominator. -/
theorem hasDerivAt_frequency_kx_sqrt (m kx ky kz ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m kx ky kz ε| < 1) :
    HasDerivAt (fun q => frequency m q ky kz ε)
      (Real.cos (m*ε) * Real.sin (kx*ε) *
        Real.cos (ky*ε) * Real.cos (kz*ε) /
          Real.sqrt (1 - shell m kx ky kz ε ^ 2)) kx := by
  obtain ⟨hnegn, hone⟩ := shell3_ne_endpoints_of_abs_lt_one hint
  have hsquare : shell m kx ky kz ε ^ 2 < 1 :=
    (sq_lt_one_iff_abs_lt_one (shell m kx ky kz ε)).2 hint
  have hsqrt : Real.sqrt (1 - shell m kx ky kz ε ^ 2) ≠ 0 := by
    exact ne_of_gt (Real.sqrt_pos.2 (by linarith))
  have hs := hasDerivAt_shell_kx m kx ky kz ε
  have ha := (Real.hasDerivAt_arccos hnegn hone).comp kx hs
  have hd := ha.div_const ε
  have hd' : HasDerivAt
      (fun q => Real.arccos (shell m q ky kz ε) / ε)
      (-(1 / Real.sqrt (1 - shell m kx ky kz ε ^ 2)) *
        (-(Real.cos (m*ε) * Real.sin (kx*ε) *
          Real.cos (ky*ε) * Real.cos (kz*ε) * ε)) / ε) kx := by
    simpa only [Function.comp_apply] using hd
  have hcoeff :
      (-(1 / Real.sqrt (1 - shell m kx ky kz ε ^ 2)) *
        (-(Real.cos (m*ε) * Real.sin (kx*ε) *
          Real.cos (ky*ε) * Real.cos (kz*ε) * ε)) / ε) =
      (Real.cos (m*ε) * Real.sin (kx*ε) *
        Real.cos (ky*ε) * Real.cos (kz*ε) /
          Real.sqrt (1 - shell m kx ky kz ε ^ 2)) := by
    field_simp [hε, hsqrt]
  simpa [frequency, phase] using hd'.congr_deriv hcoeff

/-- Equation (8.34), x component, on the nonsingular principal branch. -/
theorem hasDerivAt_frequency_kx (m kx ky kz ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m kx ky kz ε| < 1) :
    HasDerivAt (fun q => frequency m q ky kz ε)
      (Real.cos (m*ε) * Real.sin (kx*ε) *
        Real.cos (ky*ε) * Real.cos (kz*ε) /
          Real.sin (phase m kx ky kz ε)) kx := by
  have h := hasDerivAt_frequency_kx_sqrt m kx ky kz ε hε hint
  rw [sqrt_one_sub_shell3_sq] at h
  exact h


/-- Exact derivative of the 3D shell in the y-momentum component. -/
theorem hasDerivAt_shell_ky (m kx ky kz ε : ℝ) :
    HasDerivAt (fun q => shell m kx q kz ε)
      (-(Real.cos (m*ε) * Real.cos (kx*ε) * Real.sin (ky*ε) *
        Real.cos (kz*ε) * ε)) ky := by
  let A : ℝ := Real.cos (m*ε) * Real.cos (kx*ε)
  let B : ℝ := Real.cos (kz*ε)
  have hlin : HasDerivAt (fun q : ℝ => q * ε) ε ky :=
    hasDerivAt_mul_const ε
  have hcos : HasDerivAt (fun q : ℝ => Real.cos (q * ε))
      (-Real.sin (ky * ε) * ε) ky := hlin.cos
  have hprod : HasDerivAt (fun q : ℝ => (A * Real.cos (q * ε)) * B)
      ((A * (-Real.sin (ky * ε) * ε)) * B) ky :=
    (hcos.const_mul A).mul_const B
  have hfun :
      (fun q : ℝ => shell m kx q kz ε) =
        (fun q : ℝ => (A * Real.cos (q * ε)) * B) := by
    funext q
    dsimp [A, B, shell]
  rw [hfun]
  exact hprod.congr_deriv (by dsimp [A, B]; ring)

/-- Exact derivative of the 3D shell in the z-momentum component. -/
theorem hasDerivAt_shell_kz (m kx ky kz ε : ℝ) :
    HasDerivAt (fun q => shell m kx ky q ε)
      (-(Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε) *
        Real.sin (kz*ε) * ε)) kz := by
  let A : ℝ := Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε)
  have hlin : HasDerivAt (fun q : ℝ => q * ε) ε kz :=
    hasDerivAt_mul_const ε
  have hcos : HasDerivAt (fun q : ℝ => Real.cos (q * ε))
      (-Real.sin (kz * ε) * ε) kz := hlin.cos
  have hprod : HasDerivAt (fun q : ℝ => A * Real.cos (q * ε))
      (A * (-Real.sin (kz * ε) * ε)) kz := hcos.const_mul A
  have hfun :
      (fun q : ℝ => shell m kx ky q ε) =
        (fun q : ℝ => A * Real.cos (q * ε)) := by
    funext q
    dsimp [A, shell]
  rw [hfun]
  exact hprod.congr_deriv (by dsimp [A]; ring)

/-- Exact y-component derivative with the arccos square-root denominator. -/
theorem hasDerivAt_frequency_ky_sqrt (m kx ky kz ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m kx ky kz ε| < 1) :
    HasDerivAt (fun q => frequency m kx q kz ε)
      (Real.cos (m*ε) * Real.cos (kx*ε) * Real.sin (ky*ε) *
        Real.cos (kz*ε) /
          Real.sqrt (1 - shell m kx ky kz ε ^ 2)) ky := by
  obtain ⟨hnegn, hone⟩ := shell3_ne_endpoints_of_abs_lt_one hint
  have hsquare : shell m kx ky kz ε ^ 2 < 1 :=
    (sq_lt_one_iff_abs_lt_one (shell m kx ky kz ε)).2 hint
  have hsqrt : Real.sqrt (1 - shell m kx ky kz ε ^ 2) ≠ 0 := by
    exact ne_of_gt (Real.sqrt_pos.2 (by linarith))
  have hs := hasDerivAt_shell_ky m kx ky kz ε
  have ha := (Real.hasDerivAt_arccos hnegn hone).comp ky hs
  have hd := ha.div_const ε
  have hd' : HasDerivAt
      (fun q => Real.arccos (shell m kx q kz ε) / ε)
      (-(1 / Real.sqrt (1 - shell m kx ky kz ε ^ 2)) *
        (-(Real.cos (m*ε) * Real.cos (kx*ε) * Real.sin (ky*ε) *
          Real.cos (kz*ε) * ε)) / ε) ky := by
    simpa only [Function.comp_apply] using hd
  have hcoeff :
      (-(1 / Real.sqrt (1 - shell m kx ky kz ε ^ 2)) *
        (-(Real.cos (m*ε) * Real.cos (kx*ε) * Real.sin (ky*ε) *
          Real.cos (kz*ε) * ε)) / ε) =
      (Real.cos (m*ε) * Real.cos (kx*ε) * Real.sin (ky*ε) *
        Real.cos (kz*ε) /
          Real.sqrt (1 - shell m kx ky kz ε ^ 2)) := by
    field_simp [hε, hsqrt]
  simpa [frequency, phase] using hd'.congr_deriv hcoeff

/-- Equation (8.34), y component, on the nonsingular principal branch. -/
theorem hasDerivAt_frequency_ky (m kx ky kz ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m kx ky kz ε| < 1) :
    HasDerivAt (fun q => frequency m kx q kz ε)
      (Real.cos (m*ε) * Real.cos (kx*ε) * Real.sin (ky*ε) *
        Real.cos (kz*ε) / Real.sin (phase m kx ky kz ε)) ky := by
  have h := hasDerivAt_frequency_ky_sqrt m kx ky kz ε hε hint
  rw [sqrt_one_sub_shell3_sq] at h
  exact h

/-- Exact z-component derivative with the arccos square-root denominator. -/
theorem hasDerivAt_frequency_kz_sqrt (m kx ky kz ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m kx ky kz ε| < 1) :
    HasDerivAt (fun q => frequency m kx ky q ε)
      (Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε) *
        Real.sin (kz*ε) /
          Real.sqrt (1 - shell m kx ky kz ε ^ 2)) kz := by
  obtain ⟨hnegn, hone⟩ := shell3_ne_endpoints_of_abs_lt_one hint
  have hsquare : shell m kx ky kz ε ^ 2 < 1 :=
    (sq_lt_one_iff_abs_lt_one (shell m kx ky kz ε)).2 hint
  have hsqrt : Real.sqrt (1 - shell m kx ky kz ε ^ 2) ≠ 0 := by
    exact ne_of_gt (Real.sqrt_pos.2 (by linarith))
  have hs := hasDerivAt_shell_kz m kx ky kz ε
  have ha := (Real.hasDerivAt_arccos hnegn hone).comp kz hs
  have hd := ha.div_const ε
  have hd' : HasDerivAt
      (fun q => Real.arccos (shell m kx ky q ε) / ε)
      (-(1 / Real.sqrt (1 - shell m kx ky kz ε ^ 2)) *
        (-(Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε) *
          Real.sin (kz*ε) * ε)) / ε) kz := by
    simpa only [Function.comp_apply] using hd
  have hcoeff :
      (-(1 / Real.sqrt (1 - shell m kx ky kz ε ^ 2)) *
        (-(Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε) *
          Real.sin (kz*ε) * ε)) / ε) =
      (Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε) *
        Real.sin (kz*ε) /
          Real.sqrt (1 - shell m kx ky kz ε ^ 2)) := by
    field_simp [hε, hsqrt]
  simpa [frequency, phase] using hd'.congr_deriv hcoeff

/-- Equation (8.34), z component, on the nonsingular principal branch. -/
theorem hasDerivAt_frequency_kz (m kx ky kz ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m kx ky kz ε| < 1) :
    HasDerivAt (fun q => frequency m kx ky q ε)
      (Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε) *
        Real.sin (kz*ε) / Real.sin (phase m kx ky kz ε)) kz := by
  have h := hasDerivAt_frequency_kz_sqrt m kx ky kz ε hε hint
  rw [sqrt_one_sub_shell3_sq] at h
  exact h


/-- A scaled cosine is bounded on the positive-spacing filter. -/
theorem scaledCos_isBigO_one (a : ℝ) :
    (fun ε : ℝ => Real.cos (a*ε)) =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) := by
  have hc : Continuous (fun ε : ℝ => Real.cos (a*ε)) :=
    Real.continuous_cos.comp (continuous_const.mul continuous_id)
  exact ((hc.tendsto 0).mono_left nhdsWithin_le_nhds).isBigO_one ℝ

/-- Product of the three cosine factors transverse to one momentum component. -/
def cosTriple (a b c ε : ℝ) : ℝ :=
  Real.cos (a*ε) * Real.cos (b*ε) * Real.cos (c*ε)

/-- The transverse cosine product is bounded near positive zero. -/
theorem cosTriple_isBigO_one (a b c : ℝ) :
    cosTriple a b c =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) := by
  have h := ((scaledCos_isBigO_one a).mul (scaledCos_isBigO_one b)).mul
    (scaledCos_isBigO_one c)
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by simp [cosTriple]))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- The transverse cosine product differs from one only quadratically. -/
theorem cosTriple_sub_one_isBigO (a b c : ℝ) :
    (fun ε => cosTriple a b c ε - 1) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have ha := scaled_cos_sub_one_isBigO a
  have hb := scaled_cos_sub_one_isBigO b
  have hc := scaled_cos_sub_one_isBigO c
  have hbo := scaledCos_isBigO_one b
  have hco := scaledCos_isBigO_one c
  have h1raw := (ha.mul hbo).mul hco
  have h1 :
      (fun ε => (Real.cos (a*ε) - 1) * Real.cos (b*ε) * Real.cos (c*ε))
        =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    h1raw.congr' (Filter.Eventually.of_forall (fun _ => rfl))
      (Filter.Eventually.of_forall (fun ε => by ring))
  have h2raw := hb.mul hco
  have h2 :
      (fun ε => (Real.cos (b*ε) - 1) * Real.cos (c*ε))
        =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    h2raw.congr' (Filter.Eventually.of_forall (fun _ => rfl))
      (Filter.Eventually.of_forall (fun ε => by ring))
  exact ((h1.add h2).add hc).congr_left (by
    intro ε
    dsimp [cosTriple]
    ring)

/-- Normalized exact numerator for one component of the 3D group velocity. -/
def normalizedVelocityNumerator3 (a b c k ε : ℝ) : ℝ :=
  cosTriple a b c ε * sinQuot k ε

/-- Every component numerator approaches its continuum momentum with quadratic error. -/
theorem normalizedVelocityNumerator3_expansion_isBigO (a b c k : ℝ) :
    (fun ε => normalizedVelocityNumerator3 a b c k ε - k)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  have hfirstRaw := (cosTriple_isBigO_one a b c).mul
    (sinQuot_expansion_isBigO k)
  have hfirst :
      (fun ε => cosTriple a b c ε * (sinQuot k ε - k))
        =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    hfirstRaw.congr' (Filter.Eventually.of_forall (fun _ => rfl))
      (Filter.Eventually.of_forall (fun ε => by ring))
  have hsecond := (cosTriple_sub_one_isBigO a b c).const_mul_left k
  exact (hfirst.add hsecond).congr_left (by
    intro ε
    dsimp [normalizedVelocityNumerator3]
    ring)

/-- Exact x-component group velocity, continuously filled at zero. -/
def positiveGroupVelocityX3 (m kx ky kz ε : ℝ) : ℝ :=
  if ε = 0 then kx / energy3 m kx ky kz else
    Real.cos (m*ε) * Real.sin (kx*ε) * Real.cos (ky*ε) *
      Real.cos (kz*ε) / Real.sin (phase m kx ky kz ε)

/-- Exact y-component group velocity, continuously filled at zero. -/
def positiveGroupVelocityY3 (m kx ky kz ε : ℝ) : ℝ :=
  if ε = 0 then ky / energy3 m kx ky kz else
    Real.cos (m*ε) * Real.cos (kx*ε) * Real.sin (ky*ε) *
      Real.cos (kz*ε) / Real.sin (phase m kx ky kz ε)

/-- Exact z-component group velocity, continuously filled at zero. -/
def positiveGroupVelocityZ3 (m kx ky kz ε : ℝ) : ℝ :=
  if ε = 0 then kz / energy3 m kx ky kz else
    Real.cos (m*ε) * Real.cos (kx*ε) * Real.cos (ky*ε) *
      Real.sin (kz*ε) / Real.sin (phase m kx ky kz ε)

@[simp] theorem positiveGroupVelocityX3_zero (m kx ky kz : ℝ) :
    positiveGroupVelocityX3 m kx ky kz 0 = kx / energy3 m kx ky kz := by
  simp [positiveGroupVelocityX3]

@[simp] theorem positiveGroupVelocityY3_zero (m kx ky kz : ℝ) :
    positiveGroupVelocityY3 m kx ky kz 0 = ky / energy3 m kx ky kz := by
  simp [positiveGroupVelocityY3]

@[simp] theorem positiveGroupVelocityZ3_zero (m kx ky kz : ℝ) :
    positiveGroupVelocityZ3 m kx ky kz 0 = kz / energy3 m kx ky kz := by
  simp [positiveGroupVelocityZ3]

/-- The exact x velocity is normalized numerator divided by the common radial factor. -/
theorem eventually_positiveGroupVelocityX3_eq_normalized_div {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      positiveGroupVelocityX3 m kx ky kz ε =
        normalizedVelocityNumerator3 m ky kz kx ε / radial3 m kx ky kz ε := by
  filter_upwards [self_mem_nhdsWithin, eventually_sinQ3_pos hE] with ε hε hq
  have hne : ε ≠ 0 := ne_of_gt hε
  have hrne : radial3 m kx ky kz ε ≠ 0 := by
    dsimp [radial3]
    exact Real.sqrt_ne_zero'.mpr hq
  simp [positiveGroupVelocityX3, hne]
  rw [sin_phase3_eq_spacing_radial m kx ky kz ε hε]
  simp only [normalizedVelocityNumerator3, cosTriple, sinQuot_of_pos kx ε hε]
  field_simp [hne, hrne]

/-- The exact y velocity is normalized numerator divided by the common radial factor. -/
theorem eventually_positiveGroupVelocityY3_eq_normalized_div {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      positiveGroupVelocityY3 m kx ky kz ε =
        normalizedVelocityNumerator3 m kx kz ky ε / radial3 m kx ky kz ε := by
  filter_upwards [self_mem_nhdsWithin, eventually_sinQ3_pos hE] with ε hε hq
  have hne : ε ≠ 0 := ne_of_gt hε
  have hrne : radial3 m kx ky kz ε ≠ 0 := by
    dsimp [radial3]
    exact Real.sqrt_ne_zero'.mpr hq
  simp [positiveGroupVelocityY3, hne]
  rw [sin_phase3_eq_spacing_radial m kx ky kz ε hε]
  simp only [normalizedVelocityNumerator3, cosTriple, sinQuot_of_pos ky ε hε]
  field_simp [hne, hrne]

/-- The exact z velocity is normalized numerator divided by the common radial factor. -/
theorem eventually_positiveGroupVelocityZ3_eq_normalized_div {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      positiveGroupVelocityZ3 m kx ky kz ε =
        normalizedVelocityNumerator3 m kx ky kz ε / radial3 m kx ky kz ε := by
  filter_upwards [self_mem_nhdsWithin, eventually_sinQ3_pos hE] with ε hε hq
  have hne : ε ≠ 0 := ne_of_gt hε
  have hrne : radial3 m kx ky kz ε ≠ 0 := by
    dsimp [radial3]
    exact Real.sqrt_ne_zero'.mpr hq
  simp [positiveGroupVelocityZ3, hne]
  rw [sin_phase3_eq_spacing_radial m kx ky kz ε hε]
  simp only [normalizedVelocityNumerator3, cosTriple, sinQuot_of_pos kz ε hε]
  field_simp [hne, hrne]


/-- Quotient transfer from a quadratic numerator approximation and the common radial factor. -/
theorem velocityQuotient3_expansion_isBigO
    {m kx ky kz k : ℝ} {N V : ℝ → ℝ}
    (hE : energy3 m kx ky kz ≠ 0)
    (hN : (fun ε => N ε - k) =O[𝓝[>] 0] (fun ε : ℝ => ε^2))
    (hV : ∀ᶠ ε in 𝓝[>] 0,
      V ε = N ε / radial3 m kx ky kz ε) :
    (fun ε => V ε - k / energy3 m kx ky kz) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  let E := energy3 m kx ky kz
  let r := radial3 m kx ky kz
  have hEp : 0 < E :=
    lt_of_le_of_ne (energy3_nonneg m kx ky kz) (Ne.symm hE)
  have hr : (fun ε => r ε - E) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
    simpa [r, E] using radial3_sub_energy_isBigO hE
  have hnum : (fun ε => E*(N ε-k) - k*(r ε-E)) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) :=
    (hN.const_mul_left E).sub (hr.const_mul_left k)
  have hrLower : ∀ᶠ ε in 𝓝[>] 0, E/2 < r ε := by
    have hmem : Set.Ioi (E/2) ∈ 𝓝 E := Ioi_mem_nhds (by linarith)
    have hev := (tendsto_radial3 m kx ky kz).eventually hmem
    simpa [r, E] using hev
  have hden : ∀ᶠ ε in 𝓝[>] 0, E^2/2 ≤ |E*r ε| := by
    filter_upwards [hrLower] with ε hrl
    rw [abs_of_pos (mul_pos hEp (lt_trans (by linarith) hrl))]
    nlinarith
  have hquot := div_isBigO_of_eventually_abs_ge hnum
    (by positivity : 0 < E^2/2) hden
  apply hquot.congr'
  · filter_upwards [hV, hrLower] with ε hv hrl
    rw [hv]
    have hrne : r ε ≠ 0 := ne_of_gt (lt_trans (by linarith) hrl)
    have hE' : E ≠ 0 := by simpa [E] using hE
    change (E * (N ε - k) - k * (r ε - E)) / (E * r ε) =
      N ε / r ε - k / E
    field_simp [hE', hrne]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- Equation (8.35), x component, with a quadratic continuum error. -/
theorem positiveGroupVelocityX3_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => positiveGroupVelocityX3 m kx ky kz ε -
      kx / energy3 m kx ky kz) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := by
  exact velocityQuotient3_expansion_isBigO
    (m := m) (kx := kx) (ky := ky) (kz := kz) (k := kx)
    (N := normalizedVelocityNumerator3 m ky kz kx)
    (V := positiveGroupVelocityX3 m kx ky kz)
    hE (normalizedVelocityNumerator3_expansion_isBigO m ky kz kx)
      (eventually_positiveGroupVelocityX3_eq_normalized_div hE)

/-- Equation (8.35), y component, with a quadratic continuum error. -/
theorem positiveGroupVelocityY3_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => positiveGroupVelocityY3 m kx ky kz ε -
      ky / energy3 m kx ky kz) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := by
  exact velocityQuotient3_expansion_isBigO
    (m := m) (kx := kx) (ky := ky) (kz := kz) (k := ky)
    (N := normalizedVelocityNumerator3 m kx kz ky)
    (V := positiveGroupVelocityY3 m kx ky kz)
    hE (normalizedVelocityNumerator3_expansion_isBigO m kx kz ky)
      (eventually_positiveGroupVelocityY3_eq_normalized_div hE)

/-- Equation (8.35), z component, with a quadratic continuum error. -/
theorem positiveGroupVelocityZ3_expansion_isBigO {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    (fun ε => positiveGroupVelocityZ3 m kx ky kz ε -
      kz / energy3 m kx ky kz) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := by
  exact velocityQuotient3_expansion_isBigO
    (m := m) (kx := kx) (ky := ky) (kz := kz) (k := kz)
    (N := normalizedVelocityNumerator3 m kx ky kz)
    (V := positiveGroupVelocityZ3 m kx ky kz)
    hE (normalizedVelocityNumerator3_expansion_isBigO m kx ky kz)
      (eventually_positiveGroupVelocityZ3_eq_normalized_div hE)

/-- A quadratic asymptotic error implies the corresponding positive-side limit. -/
theorem tendsto_of_sub_isBigO_sq {f : ℝ → ℝ} {c : ℝ}
    (h : (fun ε => f ε - c) =O[𝓝[>] 0] (fun ε : ℝ => ε^2)) :
    Tendsto f (𝓝[>] 0) (𝓝 c) := by
  have herr := h.trans_tendsto (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => c) (𝓝[>] 0) (𝓝 c) := tendsto_const_nhds
  have hsum := herr.add hc
  simpa using Tendsto.congr' (Filter.Eventually.of_forall (fun ε => by ring)) hsum

/-- The x component converges to `kx/E`. -/
theorem tendsto_positiveGroupVelocityX3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    Tendsto (positiveGroupVelocityX3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (kx / energy3 m kx ky kz)) :=
  tendsto_of_sub_isBigO_sq (positiveGroupVelocityX3_expansion_isBigO hE)

/-- The y component converges to `ky/E`. -/
theorem tendsto_positiveGroupVelocityY3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    Tendsto (positiveGroupVelocityY3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (ky / energy3 m kx ky kz)) :=
  tendsto_of_sub_isBigO_sq (positiveGroupVelocityY3_expansion_isBigO hE)

/-- The z component converges to `kz/E`. -/
theorem tendsto_positiveGroupVelocityZ3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    Tendsto (positiveGroupVelocityZ3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (kz / energy3 m kx ky kz)) :=
  tendsto_of_sub_isBigO_sq (positiveGroupVelocityZ3_expansion_isBigO hE)

/-- Nonzero continuum energy places the exact 3D shell strictly inside `(-1,1)` eventually. -/
theorem eventually_abs_shell3_lt_one {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0, |shell m kx ky kz ε| < 1 := by
  filter_upwards [self_mem_nhdsWithin, eventually_sinQ3_pos hE] with ε hε hq
  have hfac := one_sub_shell3_sq_eq m kx ky kz ε hε
  have hpos : 0 < 1 - shell m kx ky kz ε ^ 2 := by
    rw [hfac]
    exact mul_pos (sq_pos_of_pos hε) hq
  exact (sq_lt_one_iff_abs_lt_one (shell m kx ky kz ε)).mp (by linarith)

/-- The exact x velocity expression is the actual momentum derivative eventually. -/
theorem eventually_hasDerivAt_positiveGroupVelocityX3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      HasDerivAt (fun q => positiveFrequency3 m q ky kz ε)
        (positiveGroupVelocityX3 m kx ky kz ε) kx := by
  filter_upwards [self_mem_nhdsWithin, eventually_abs_shell3_lt_one hE]
    with ε hε hint
  have hne : ε ≠ 0 := ne_of_gt hε
  have h := hasDerivAt_frequency_kx m kx ky kz ε hne hint
  have hfreq : (fun q => positiveFrequency3 m q ky kz ε) =
      (fun q => frequency m q ky kz ε) := by
    funext q
    simp [positiveFrequency3, hne]
  rw [hfreq]
  simpa [positiveGroupVelocityX3, hne] using h

/-- The exact y velocity expression is the actual momentum derivative eventually. -/
theorem eventually_hasDerivAt_positiveGroupVelocityY3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      HasDerivAt (fun q => positiveFrequency3 m kx q kz ε)
        (positiveGroupVelocityY3 m kx ky kz ε) ky := by
  filter_upwards [self_mem_nhdsWithin, eventually_abs_shell3_lt_one hE]
    with ε hε hint
  have hne : ε ≠ 0 := ne_of_gt hε
  have h := hasDerivAt_frequency_ky m kx ky kz ε hne hint
  have hfreq : (fun q => positiveFrequency3 m kx q kz ε) =
      (fun q => frequency m kx q kz ε) := by
    funext q
    simp [positiveFrequency3, hne]
  rw [hfreq]
  simpa [positiveGroupVelocityY3, hne] using h

/-- The exact z velocity expression is the actual momentum derivative eventually. -/
theorem eventually_hasDerivAt_positiveGroupVelocityZ3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      HasDerivAt (fun q => positiveFrequency3 m kx ky q ε)
        (positiveGroupVelocityZ3 m kx ky kz ε) kz := by
  filter_upwards [self_mem_nhdsWithin, eventually_abs_shell3_lt_one hE]
    with ε hε hint
  have hne : ε ≠ 0 := ne_of_gt hε
  have h := hasDerivAt_frequency_kz m kx ky kz ε hne hint
  have hfreq : (fun q => positiveFrequency3 m kx ky q ε) =
      (fun q => frequency m kx ky q ε) := by
    funext q
    simp [positiveFrequency3, hne]
  rw [hfreq]
  simpa [positiveGroupVelocityZ3, hne] using h


/-- Exact three-component group velocity. -/
def positiveGroupVelocityVector3 (m kx ky kz ε : ℝ) : ℝ × ℝ × ℝ :=
  (positiveGroupVelocityX3 m kx ky kz ε,
    positiveGroupVelocityY3 m kx ky kz ε,
    positiveGroupVelocityZ3 m kx ky kz ε)

/-- Continuum relativistic velocity `k/E`. -/
def continuumVelocityVector3 (m kx ky kz : ℝ) : ℝ × ℝ × ℝ :=
  (kx / energy3 m kx ky kz,
    ky / energy3 m kx ky kz,
    kz / energy3 m kx ky kz)

/-- Vector form of equation (8.35). -/
theorem tendsto_positiveGroupVelocityVector3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    Tendsto (positiveGroupVelocityVector3 m kx ky kz) (𝓝[>] 0)
      (𝓝 (continuumVelocityVector3 m kx ky kz)) := by
  exact (tendsto_positiveGroupVelocityX3 hE).prodMk_nhds
    ((tendsto_positiveGroupVelocityY3 hE).prodMk_nhds
      (tendsto_positiveGroupVelocityZ3 hE))

/-- All three displayed components are simultaneously actual derivatives eventually. -/
theorem eventually_hasDerivAt_positiveGroupVelocityVector3 {m kx ky kz : ℝ}
    (hE : energy3 m kx ky kz ≠ 0) :
    ∀ᶠ ε in 𝓝[>] 0,
      HasDerivAt (fun q => positiveFrequency3 m q ky kz ε)
          (positiveGroupVelocityX3 m kx ky kz ε) kx ∧
      HasDerivAt (fun q => positiveFrequency3 m kx q kz ε)
          (positiveGroupVelocityY3 m kx ky kz ε) ky ∧
      HasDerivAt (fun q => positiveFrequency3 m kx ky q ε)
          (positiveGroupVelocityZ3 m kx ky kz ε) kz := by
  filter_upwards [eventually_hasDerivAt_positiveGroupVelocityX3 hE,
    eventually_hasDerivAt_positiveGroupVelocityY3 hE,
    eventually_hasDerivAt_positiveGroupVelocityZ3 hE] with ε hx hy hz
  exact ⟨hx, hy, hz⟩

end KomorebiPhysics.Relativistic3DGroupVelocity
