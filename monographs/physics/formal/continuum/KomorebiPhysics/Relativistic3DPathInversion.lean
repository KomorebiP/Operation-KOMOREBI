module

public import KomorebiPhysics.Relativistic3DContinuumLimit
public import Mathlib.Analysis.Asymptotics.Ring

/-!
A parameterized branch-safe inversion theorem.  Any real shell path with a
sixth-order expansion

  S(ε) = 1 - E² ε²/2 + B ε⁴ + O(ε⁶),  E > 0,

has principal positive frequency

  arccos(S(ε))/ε = E + (E³/24 - B/E) ε² + O(ε⁴).

This isolates the inverse-trigonometric analysis from the moving-momentum shell.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DPathInversion

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Relativistic1DContinuumLimit

/-- Fourth-order shell approximant for a general positive-energy path. -/
def pathShellPoly4 (E B ε : ℝ) : ℝ :=
  1 - E^2 * ε^2 / 2 + B * ε^4

/-- Quartic coefficient in the square of the general shell approximant. -/
def pathShellSqQuartic (E B : ℝ) : ℝ := E^4 / 4 + 2 * B

/-- Fourth-order approximant to the squared shell. -/
def pathShellSqPoly4 (E B ε : ℝ) : ℝ :=
  1 - E^2 * ε^2 + pathShellSqQuartic E B * ε^4

/-- Normalized principal-sine square, continuously filled at zero. -/
def pathSinQ (S : ℝ → ℝ) (E ε : ℝ) : ℝ :=
  if ε = 0 then E^2 else (1 - S ε ^ 2) / ε^2

/-- Quadratic approximation to the normalized principal-sine square. -/
def pathSinQPoly2 (E B ε : ℝ) : ℝ :=
  E^2 - pathShellSqQuartic E B * ε^2

/-- Positive radial factor of the principal sine. -/
def pathRadial (S : ℝ → ℝ) (E ε : ℝ) : ℝ :=
  Real.sqrt (pathSinQ S E ε)

/-- Quadratic coefficient in the radial factor. -/
def pathRadialCoeff (E B : ℝ) : ℝ :=
  -pathShellSqQuartic E B / (2 * E)

/-- Quadratic radial approximant. -/
def pathRadialPoly2 (E B ε : ℝ) : ℝ :=
  E + pathRadialCoeff E B * ε^2

/-- Exact arcsine input. -/
def pathPhaseInput (S : ℝ → ℝ) (E ε : ℝ) : ℝ :=
  ε * pathRadial S E ε

/-- Cubic approximation to the arcsine input. -/
def pathPhaseInputPoly3 (E B ε : ℝ) : ℝ :=
  E * ε + pathRadialCoeff E B * ε^3

/-- Principal phase of a general real shell. -/
def pathPhase (S : ℝ → ℝ) (ε : ℝ) : ℝ := Real.arccos (S ε)

/-- Positive-frequency quotient, continuously filled at zero. -/
def pathPositiveFrequency (S : ℝ → ℝ) (E ε : ℝ) : ℝ :=
  if ε = 0 then E else pathPhase S ε / ε

/-- Quadratic coefficient after branch-safe phase inversion. -/
def pathCorrection (E B : ℝ) : ℝ := E^3 / 24 - B / E

/-- Second-order frequency approximant. -/
def pathFrequencyPoly2 (E B ε : ℝ) : ℝ :=
  E + pathCorrection E B * ε^2

@[simp] theorem pathSinQ_zero (S : ℝ → ℝ) (E : ℝ) :
    pathSinQ S E 0 = E^2 := by simp [pathSinQ]

@[simp] theorem pathPositiveFrequency_zero (S : ℝ → ℝ) (E : ℝ) :
    pathPositiveFrequency S E 0 = E := by simp [pathPositiveFrequency]

theorem pathSinQ_of_pos (S : ℝ → ℝ) (E ε : ℝ) (hε : 0 < ε) :
    pathSinQ S E ε = (1 - S ε ^ 2) / ε^2 := by
  simp [pathSinQ, ne_of_gt hε]

theorem pathPositiveFrequency_of_pos (S : ℝ → ℝ) (E ε : ℝ) (hε : 0 < ε) :
    pathPositiveFrequency S E ε = pathPhase S ε / ε := by
  simp [pathPositiveFrequency, ne_of_gt hε]

/-- The squared polynomial contributes only sixth- and eighth-order residuals. -/
theorem pathShellPoly_sq_error_isBigO (E B : ℝ) :
    (fun ε => pathShellPoly4 E B ε ^ 2 - pathShellSqPoly4 E B ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^6) := by
  have h6 : (fun ε : ℝ => ε^6) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
    isBigO_refl _ _
  have h8 : (fun ε : ℝ => ε^8) =O[𝓝[>] 0] (fun ε : ℝ => ε^6) :=
    pow8_isBigO_pow6_positive
  have hsum := (h6.const_mul_left (-(E^2 * B))).add
    (h8.const_mul_left (B^2))
  exact hsum.congr_left (by
    intro ε
    simp only [pathShellPoly4, pathShellSqPoly4, pathShellSqQuartic]
    ring)

/-- The assumed shell expansion implies convergence to one. -/
theorem tendsto_pathShell {S : ℝ → ℝ} {E B : ℝ}
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    Tendsto S (𝓝[>] 0) (𝓝 1) := by
  have herr := hS.trans_tendsto (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 6)
  have hpoly : Tendsto (pathShellPoly4 E B) (𝓝[>] 0) (𝓝 1) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε => 1 - E^2 * ε^2 / 2 + B * ε^4)
      (𝓝[>] 0) (𝓝 1)
    convert (tendsto_const_nhds.sub
      ((tendsto_const_nhds.mul (hid.pow 2)).div_const 2)).add
        (tendsto_const_nhds.mul (hid.pow 4)) using 1
    all_goals ring
  have hsum := herr.add hpoly
  simpa using Tendsto.congr'
    (Filter.Eventually.of_forall (fun ε => by ring)) hsum

/-- Squaring preserves the shell expansion through quartic order. -/
theorem pathShell_sq_expansion_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => S ε ^ 2 - pathShellSqPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6) := by
  have hST := tendsto_pathShell hS
  have hpoly : Tendsto (pathShellPoly4 E B) (𝓝[>] 0) (𝓝 1) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε => 1 - E^2 * ε^2 / 2 + B * ε^4)
      (𝓝[>] 0) (𝓝 1)
    convert (tendsto_const_nhds.sub
      ((tendsto_const_nhds.mul (hid.pow 2)).div_const 2)).add
        (tendsto_const_nhds.mul (hid.pow 4)) using 1
    all_goals ring
  have hbounded : (fun ε => S ε + pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun _ : ℝ => (1 : ℝ)) := (hST.add hpoly).isBigO_one ℝ
  have hprod := hS.mul hbounded
  have hprod6 :
      (fun ε => (S ε - pathShellPoly4 E B ε) *
        (S ε + pathShellPoly4 E B ε)) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^6) := by
    exact hprod.congr_right (by intro ε; simp)
  have hpolyerr := pathShellPoly_sq_error_isBigO E B
  exact (hprod6.add hpolyerr).congr_left (by intro ε; ring)

/-- Normalized sine-square expansion. -/
theorem pathSinQ_expansion_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathSinQ S E ε - pathSinQPoly2 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) := by
  have hdiv := div_sq_isBigO_positive (pathShell_sq_expansion_isBigO hS)
  have hneg := hdiv.const_mul_left (-1 : ℝ)
  apply hneg.congr'
  · filter_upwards [self_mem_nhdsWithin] with ε hε
    have hne : ε ≠ 0 := ne_of_gt hε
    rw [pathSinQ_of_pos S E ε hε]
    simp only [pathSinQPoly2, pathShellSqPoly4]
    field_simp [hne]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The normalized sine square converges to `E²`. -/
theorem tendsto_pathSinQ {S : ℝ → ℝ} {E B : ℝ}
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    Tendsto (pathSinQ S E) (𝓝[>] 0) (𝓝 (E^2)) := by
  have herr := (pathSinQ_expansion_isBigO hS).trans_tendsto (by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 4)
  have hpoly : Tendsto (pathSinQPoly2 E B) (𝓝[>] 0) (𝓝 (E^2)) := by
    have hid : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    change Tendsto (fun ε => E^2 - pathShellSqQuartic E B * ε^2)
      (𝓝[>] 0) (𝓝 (E^2))
    convert tendsto_const_nhds.sub (tendsto_const_nhds.mul (hid.pow 2)) using 1
    all_goals ring
  have hsum := herr.add hpoly
  simpa using Tendsto.congr'
    (Filter.Eventually.of_forall (fun ε => by ring)) hsum

/-- Exact positive-spacing factorization of `1-S²`. -/
theorem one_sub_pathShell_sq_eq (S : ℝ → ℝ) (E ε : ℝ) (hε : 0 < ε) :
    1 - S ε ^ 2 = ε^2 * pathSinQ S E ε := by
  rw [pathSinQ_of_pos S E ε hε]
  field_simp [ne_of_gt hε]

/-- Positive energy makes the normalized principal-sine square eventually positive. -/
theorem eventually_pathSinQ_pos {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    ∀ᶠ ε in 𝓝[>] 0, 0 < pathSinQ S E ε := by
  have hE2 : 0 < E^2 := sq_pos_of_pos hE
  have hmem : Set.Ioi (E^2 / 2) ∈ 𝓝 (E^2) :=
    Ioi_mem_nhds (by linarith)
  filter_upwards [(tendsto_pathSinQ hS) hmem] with ε hε
  exact lt_trans (by positivity : 0 < E^2 / 2) hε

/-- The shell path is eventually positive. -/
theorem eventually_pathShell_pos {S : ℝ → ℝ} {E B : ℝ}
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    ∀ᶠ ε in 𝓝[>] 0, 0 < S ε := by
  exact (tendsto_pathShell hS) (Ioi_mem_nhds (by norm_num : (0 : ℝ) < 1))

/-- The principal sine is spacing times the positive radial factor. -/
theorem sin_pathPhase_eq_spacing_radial
    (S : ℝ → ℝ) (E ε : ℝ) (hε : 0 < ε) :
    Real.sin (pathPhase S ε) = ε * pathRadial S E ε := by
  rw [pathPhase, Real.sin_arccos]
  rw [one_sub_pathShell_sq_eq S E ε hε]
  rw [Real.sqrt_mul (sq_nonneg ε)]
  rw [Real.sqrt_sq hε.le]
  rfl

/-- On the positive-shell branch, the principal phase is an ordinary arcsine. -/
theorem pathPhase_eq_arcsin_spacing_radial
    {S : ℝ → ℝ} {E ε : ℝ} (hε : 0 < ε) (hs : 0 < S ε) :
    pathPhase S ε = Real.arcsin (ε * pathRadial S E ε) := by
  have hlo : -(Real.pi / 2) ≤ pathPhase S ε := by
    have hp : 0 ≤ pathPhase S ε := Real.arccos_nonneg _
    have hpi : 0 < Real.pi := Real.pi_pos
    linarith
  have hhi : pathPhase S ε ≤ Real.pi / 2 :=
    Real.arccos_le_pi_div_two.mpr hs.le
  calc
    pathPhase S ε = Real.arcsin (Real.sin (pathPhase S ε)) :=
      (Real.arcsin_sin hlo hhi).symm
    _ = Real.arcsin (ε * pathRadial S E ε) := by
      rw [sin_pathPhase_eq_spacing_radial S E ε hε]

/-- The radial factor converges to the positive energy. -/
theorem tendsto_pathRadial {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    Tendsto (pathRadial S E) (𝓝[>] 0) (𝓝 E) := by
  have h := (tendsto_pathSinQ hS).sqrt
  change Tendsto (fun ε => Real.sqrt (pathSinQ S E ε)) (𝓝[>] 0) (𝓝 E)
  simpa [Real.sqrt_sq hE.le] using h

/-- Removing `E²` from the normalized sine square leaves `O(ε²)`. -/
theorem pathSinQ_sub_energy_sq_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathSinQ S E ε - E^2) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have hrem4 := pathSinQ_expansion_isBigO hS
  have hrem2 := hrem4.trans
    ((isLittleO_pow_pow (by omega : 2 < 4)).isBigO.mono nhdsWithin_le_nhds)
  have hquad := (isBigO_refl (fun ε : ℝ => ε^2) (𝓝[>] 0)).const_mul_left
    (-pathShellSqQuartic E B)
  exact (hrem2.add hquad).congr_left (by
    intro ε
    simp only [pathSinQPoly2]
    ring)

/-- The rationalizing denominator is globally bounded below by `E`. -/
theorem eventually_pathRadial_add_energy_abs_ge {S : ℝ → ℝ} {E : ℝ}
    (hE : 0 < E) :
    ∀ᶠ ε in 𝓝[>] 0, E ≤ |pathRadial S E ε + E| := by
  filter_upwards with ε
  change E ≤ |Real.sqrt (pathSinQ S E ε) + E|
  rw [abs_of_nonneg (add_nonneg (Real.sqrt_nonneg _) hE.le)]
  linarith [Real.sqrt_nonneg (pathSinQ S E ε)]

/-- Exact rationalization of the radial error. -/
theorem eventually_pathRadial_rationalization
    {S : ℝ → ℝ} {E B : ℝ} (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    ∀ᶠ ε in 𝓝[>] 0,
      pathRadial S E ε - E =
        (pathSinQ S E ε - E^2) / (pathRadial S E ε + E) := by
  filter_upwards [eventually_pathSinQ_pos hE hS] with ε hq
  have hden : pathRadial S E ε + E ≠ 0 :=
    ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hE)
  rw [eq_div_iff hden]
  have hrad_sq : pathRadial S E ε ^ 2 = pathSinQ S E ε := by
    dsimp [pathRadial]
    rw [Real.sq_sqrt hq.le]
  nlinarith

/-- The radial factor first differs from `E` by `O(ε²)`. -/
theorem pathRadial_sub_energy_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathRadial S E ε - E) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have hdiv := div_isBigO_of_eventually_abs_ge
    (pathSinQ_sub_energy_sq_isBigO hS) hE
    (eventually_pathRadial_add_energy_abs_ge (S := S) hE)
  apply hdiv.congr'
  · filter_upwards [eventually_pathRadial_rationalization hE hS] with ε hε
    exact hε.symm
  · exact Filter.Eventually.of_forall (fun _ => rfl)

/-- The radial factor has the required quadratic expansion. -/
theorem pathRadial_expansion_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathRadial S E ε - pathRadialPoly2 E B ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  let D := pathShellSqQuartic E B
  let d : ℝ → ℝ := fun ε => pathRadial S E ε + E
  let R : ℝ → ℝ := fun ε => pathSinQ S E ε - (E^2 - D*ε^2)
  have hR : R =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    simpa [R, D, pathSinQPoly2] using pathSinQ_expansion_isBigO hS
  have hd : ∀ᶠ ε in 𝓝[>] 0, E ≤ |d ε| := by
    simpa [d] using eventually_pathRadial_add_energy_abs_ge (S := S) hE
  have hfirst : (fun ε => R ε / d ε) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) :=
    div_isBigO_of_eventually_abs_ge hR hE hd
  have hr2 : (fun ε => pathRadial S E ε - E) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := pathRadial_sub_energy_isBigO hE hS
  have hp2 : (fun ε : ℝ => ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
    isBigO_refl _ _
  have hnum := (hp2.mul hr2).const_mul_left (D / (2*E))
  have hsecond :
      (fun ε => (D / (2*E) * (ε^2 * (pathRadial S E ε - E))) / d ε)
        =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    have hnum4 :
        (fun ε => D / (2*E) * (ε^2 * (pathRadial S E ε - E)))
          =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
      exact hnum.congr_right (by intro ε; ring)
    exact div_isBigO_of_eventually_abs_ge hnum4 hE hd
  have hsum := hfirst.add hsecond
  apply hsum.congr'
  · filter_upwards [eventually_pathSinQ_pos hE hS] with ε hq
    have hden : d ε ≠ 0 := by
      dsimp [d]
      exact ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hE)
    have h2E : 2*E ≠ 0 := mul_ne_zero (by norm_num) (ne_of_gt hE)
    have hbase : pathRadial S E ε - E =
        (pathSinQ S E ε - E^2) / d ε := by
      have hden' : pathRadial S E ε + E ≠ 0 := by
        exact ne_of_gt (add_pos_of_nonneg_of_pos (Real.sqrt_nonneg _) hE)
      rw [eq_div_iff hden']
      have hrad_sq : pathRadial S E ε ^ 2 = pathSinQ S E ε := by
        dsimp [pathRadial]
        rw [Real.sq_sqrt hq.le]
      nlinarith
    have hqdiff : pathSinQ S E ε - E^2 =
        (pathRadial S E ε - E) * d ε := by
      exact ((eq_div_iff hden).mp hbase).symm
    change R ε / d ε +
      (D / (2*E) * (ε^2 * (pathRadial S E ε - E))) / d ε =
        pathRadial S E ε - (E + (-D / (2*E)) * ε^2)
    rw [← add_div]
    rw [div_eq_iff hden]
    have hRpoint : R ε =
        (pathRadial S E ε - E) * d ε + D*ε^2 := by
      dsimp [R]
      calc
        pathSinQ S E ε - (E^2 - D*ε^2) =
            (pathSinQ S E ε - E^2) + D*ε^2 := by ring
        _ = (pathRadial S E ε - E) * d ε + D*ε^2 := by rw [hqdiff]
    rw [hRpoint]
    field_simp [h2E]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The exact arcsine input has its cubic expansion. -/
theorem pathPhaseInput_expansion_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathPhaseInput S E ε - pathPhaseInputPoly3 E B ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
  have hr := pathRadial_expansion_isBigO hE hS
  have he : (fun ε : ℝ => ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
    isBigO_refl _ _
  have h := he.mul hr
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by
      simp only [pathPhaseInput, pathPhaseInputPoly3, pathRadialPoly2]
      ring)) (Filter.Eventually.of_forall (fun ε => by ring))

/-- The arcsine input converges to zero. -/
theorem tendsto_pathPhaseInput {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    Tendsto (pathPhaseInput S E) (𝓝[>] 0) (𝓝 0) := by
  have he : Tendsto (fun ε : ℝ => ε) (𝓝[>] 0) (𝓝 0) :=
    tendsto_id.mono_left nhdsWithin_le_nhds
  change Tendsto (fun ε => ε * pathRadial S E ε) (𝓝[>] 0) (𝓝 0)
  simpa using he.mul (tendsto_pathRadial hE hS)

/-- The exact arcsine input is `O(ε)`. -/
theorem pathPhaseInput_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    pathPhaseInput S E =O[𝓝[>] 0] (fun ε : ℝ => ε) := by
  have hr : pathRadial S E =O[𝓝[>] 0] (fun _ : ℝ => (1 : ℝ)) :=
    (tendsto_pathRadial hE hS).isBigO_one ℝ
  have he : (fun ε : ℝ => ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
    isBigO_refl _ _
  have h := he.mul hr
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by
      simp [pathPhaseInput])) (Filter.Eventually.of_forall (fun ε => by ring))

/-- Removing the linear term from the arcsine input leaves `O(ε³)`. -/
theorem pathPhaseInput_sub_linear_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathPhaseInput S E ε - E*ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^3) := by
  have hrem5 := pathPhaseInput_expansion_isBigO hE hS
  have hrem3 := hrem5.trans
    ((isLittleO_pow_pow (by omega : 3 < 5)).isBigO.mono nhdsWithin_le_nhds)
  have hcubic := (isBigO_refl (fun ε : ℝ => ε^3) (𝓝[>] 0)).const_mul_left
    (pathRadialCoeff E B)
  exact (hrem3.add hcubic).congr_left (by
    intro ε
    simp only [pathPhaseInputPoly3]
    ring)

/-- Cubing the exact input introduces only `O(ε⁵)` beyond the continuum cube. -/
theorem pathPhaseInput_cube_expansion_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathPhaseInput S E ε ^ 3 - (E*ε)^3) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^5) := by
  have hdiff := pathPhaseInput_sub_linear_isBigO hE hS
  have hx := pathPhaseInput_isBigO hE hS
  have hlin : (fun ε : ℝ => E*ε) =O[𝓝[>] 0] (fun ε : ℝ => ε) :=
    (isBigO_refl (fun ε : ℝ => ε) (𝓝[>] 0)).const_mul_left E
  have hx2 := hx.pow 2
  have hxlin0 := hx.mul hlin
  have hxlin :
      (fun ε => pathPhaseInput S E ε * (E*ε)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^2) := hxlin0.congr_right (by intro ε; ring)
  have hlin2 := hlin.pow 2
  have hfactor :
      (fun ε => pathPhaseInput S E ε ^ 2 +
        pathPhaseInput S E ε * (E*ε) + (E*ε)^2) =O[𝓝[>] 0]
          (fun ε : ℝ => ε^2) := by
    have hsum := (hx2.add hxlin).add hlin2
    exact hsum.congr_right (by intro ε; ring)
  have h := hdiff.mul hfactor
  exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
    (Filter.Eventually.of_forall (fun ε => by ring))

/-- The radial and arcsine cubic coefficients reduce to the closed correction. -/
theorem pathRadialCoeff_add_energy_cube {E B : ℝ} (hE : E ≠ 0) :
    pathRadialCoeff E B + E^3 / 6 = pathCorrection E B := by
  rw [pathRadialCoeff, pathShellSqQuartic, pathCorrection]
  field_simp [hE]
  ring

/-- The principal phase has the checked cubic expansion. -/
theorem pathPhase_expansion_isBigO {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathPhase S ε - (E*ε + pathCorrection E B * ε^3))
      =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
  have harc0 := arcsin_cubic_expansion_isBigO.comp_tendsto
    (tendsto_pathPhaseInput hE hS)
  have harc :
      (fun ε => Real.arcsin (pathPhaseInput S E ε) -
        pathPhaseInput S E ε - pathPhaseInput S E ε ^ 3 / 6)
          =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
    have hp := (pathPhaseInput_isBigO hE hS).pow 5
    exact harc0.trans hp
  have hin := pathPhaseInput_expansion_isBigO hE hS
  have hcube := pathPhaseInput_cube_expansion_isBigO hE hS
  have hcube6 :
      (fun ε => (pathPhaseInput S E ε ^ 3 - (E*ε)^3) / 6)
        =O[𝓝[>] 0] (fun ε : ℝ => ε^5) := by
    have h := hcube.const_mul_left (1/6 : ℝ)
    exact h.congr_left (by intro ε; ring)
  have hsum := (harc.add hin).add hcube6
  have hphaseArcsin : ∀ᶠ ε in 𝓝[>] 0,
      pathPhase S ε = Real.arcsin (pathPhaseInput S E ε) := by
    filter_upwards [self_mem_nhdsWithin, eventually_pathShell_pos hS]
      with ε hε hs
    simpa [pathPhaseInput] using pathPhase_eq_arcsin_spacing_radial
      (S := S) (E := E) hε hs
  apply hsum.congr'
  · filter_upwards [hphaseArcsin] with ε heq
    rw [heq]
    rw [← pathRadialCoeff_add_energy_cube (E := E) (B := B) (ne_of_gt hE)]
    simp only [pathPhaseInputPoly3]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- Generic branch-safe frequency inversion with a fourth-order remainder. -/
theorem pathPositiveFrequency_expansion_isBigO
    {S : ℝ → ℝ} {E B : ℝ}
    (hE : 0 < E)
    (hS : (fun ε => S ε - pathShellPoly4 E B ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^6)) :
    (fun ε => pathPositiveFrequency S E ε - pathFrequencyPoly2 E B ε)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have hdiv := div_linear_isBigO_positive (pathPhase_expansion_isBigO hE hS)
  apply hdiv.congr'
  · filter_upwards [self_mem_nhdsWithin] with ε hε
    have hne : ε ≠ 0 := ne_of_gt hε
    rw [pathPositiveFrequency_of_pos S E ε hε]
    simp only [pathFrequencyPoly2]
    field_simp [hne]
  · exact Filter.Eventually.of_forall (fun ε => by ring)

end KomorebiPhysics.Relativistic3DPathInversion
