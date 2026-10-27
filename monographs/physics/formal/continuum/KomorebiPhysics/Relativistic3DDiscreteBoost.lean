module

public import KomorebiPhysics.Relativistic3DLorentzKinematics
public import Mathlib.Analysis.Asymptotics.Ring

/-!
Exact Lorentz transformation of the discrete four-momentum and the continuum
energy response to its moving spatial component.  The transformed momentum is
not frozen: its displacement is exactly proportional to the source lattice
frequency error.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DDiscreteBoost

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit
open KomorebiPhysics.Relativistic1DContinuumLimit
open KomorebiPhysics.Relativistic3DLorentzKinematics

/-- Continuum transformed energy. -/
def continuumBoostEnergy (m : ℝ) (k v : Vec3) : ℝ :=
  boostEnergy v k (energyVec m k)

/-- Continuum transformed spatial momentum. -/
def continuumBoostMomentum (m : ℝ) (k v : Vec3) : Vec3 :=
  boostMomentum v k (energyVec m k)

/-- Energy component obtained by boosting the exact lattice four-momentum. -/
def discreteBoostEnergy (m : ℝ) (k v : Vec3) (ε : ℝ) : ℝ :=
  boostEnergy v k (frequencyVec m k ε)

/-- Spatial component obtained by boosting the exact lattice four-momentum. -/
def discreteBoostMomentum (m : ℝ) (k v : Vec3) (ε : ℝ) : Vec3 :=
  boostMomentum v k (frequencyVec m k ε)

/-- Scalar displacement of the discrete transformed momentum from the continuum one. -/
def boostDisplacement (m : ℝ) (k v : Vec3) (ε : ℝ) : ℝ :=
  -gamma v * (frequencyVec m k ε - energyVec m k)

/-- The source lattice frequency expansion in vector notation. -/
theorem frequencyVec_expansion_isBigO {m : ℝ} {k : Vec3}
    (hE : energyVec m k ≠ 0) :
    (fun ε => frequencyVec m k ε -
      (energyVec m k + correctionVec m k * ε^2)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^4) := by
  simpa [frequencyVec, energyVec, correctionVec, frequencyPoly2_3] using
    (positiveFrequency3_expansion_isBigO
      (m := m) (kx := k.x) (ky := k.y) (kz := k.z) hE)

/-- The transformed-energy error is exactly `γ` times the source-frequency error. -/
theorem discreteBoostEnergy_sub_continuum (m : ℝ) (k v : Vec3) (ε : ℝ) :
    discreteBoostEnergy m k v ε - continuumBoostEnergy m k v =
      gamma v * (frequencyVec m k ε - energyVec m k) := by
  simp [discreteBoostEnergy, continuumBoostEnergy, boostEnergy]
  ring

/-- Exact moving-momentum identity `k'Δ = k' - γ(ωΔ-E)v`. -/
theorem discreteBoostMomentum_eq_continuum_add (m : ℝ) (k v : Vec3) (ε : ℝ) :
    discreteBoostMomentum m k v ε =
      add (continuumBoostMomentum m k v)
        (scale (boostDisplacement m k v ε) v) := by
  apply Vec3.ext <;>
    simp [discreteBoostMomentum, continuumBoostMomentum, boostMomentum,
      boostCoeff, boostDisplacement, add, scale] <;> ring

/-- Coordinate-free exact displacement from the continuum transformed momentum. -/
theorem discreteBoostMomentum_sub_continuum (m : ℝ) (k v : Vec3) (ε : ℝ) :
    sub (discreteBoostMomentum m k v ε) (continuumBoostMomentum m k v) =
      scale (boostDisplacement m k v ε) v := by
  rw [discreteBoostMomentum_eq_continuum_add]
  ext <;> simp [sub, add, scale]

/-- The boosted energy has its inherited quadratic lattice correction. -/
theorem discreteBoostEnergy_expansion_isBigO {m : ℝ} {k v : Vec3}
    (hE : energyVec m k ≠ 0) :
    (fun ε => discreteBoostEnergy m k v ε -
      (continuumBoostEnergy m k v + gamma v * correctionVec m k * ε^2))
        =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have h := (frequencyVec_expansion_isBigO hE).const_mul_left (gamma v)
  exact h.congr_left (by
    intro ε
    simp [discreteBoostEnergy, continuumBoostEnergy, boostEnergy]
    ring)

/-- The scalar transformed-momentum displacement has a checked quadratic jet. -/
theorem boostDisplacement_expansion_isBigO {m : ℝ} {k v : Vec3}
    (hE : energyVec m k ≠ 0) :
    (fun ε => boostDisplacement m k v ε -
      (-gamma v * correctionVec m k) * ε^2) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^4) := by
  have h := (frequencyVec_expansion_isBigO hE).const_mul_left (-gamma v)
  exact h.congr_left (by
    intro ε
    simp only [boostDisplacement]
    ring)

/-- Squared norm of a scalar displacement along a fixed vector. -/
theorem normSq_add_scale (q v : Vec3) (t : ℝ) :
    normSq (add q (scale t v)) =
      normSq q + 2 * t * dot v q + t^2 * normSq v := by
  simp [normSq_eq, add, scale, dot]
  ring

/-- Exact squared-energy formula along a one-dimensional momentum displacement. -/
theorem energyVec_add_scale_sq (m : ℝ) (q v : Vec3) (t : ℝ) :
    energyVec m (add q (scale t v)) ^ 2 =
      energyVec m q ^ 2 + 2 * t * dot v q + t^2 * normSq v := by
  rw [energyVec_sq, energyVec_sq, normSq_add_scale]
  ring

/-- A quartic error is also a quadratic error near zero. -/
theorem pow4_isBigO_pow2_positive :
    (fun ε : ℝ => ε^4) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  exact (isLittleO_pow_pow (by omega : 2 < 4)).isBigO.mono
    nhdsWithin_le_nhds

/-- An `a ε² + O(ε⁴)` path is itself `O(ε²)`. -/
theorem path_isBigO_sq {t : ℝ → ℝ} {a : ℝ}
    (ht : (fun ε => t ε - a * ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    t =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  have hr := ht.trans pow4_isBigO_pow2_positive
  have hp := (isBigO_refl (fun ε : ℝ => ε^2) (𝓝[>] 0)).const_mul_left a
  exact (hr.add hp).congr_left (by intro ε; ring)

/-- The displaced continuum energy has its exact first moving-momentum correction. -/
theorem shiftedEnergy_expansion_isBigO
    {m a : ℝ} {q v : Vec3} {t : ℝ → ℝ}
    (hE : energyVec m q ≠ 0)
    (ht : (fun ε => t ε - a * ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε => energyVec m (add q (scale (t ε) v)) -
      (energyVec m q + (a * dot v q / energyVec m q) * ε^2))
        =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  let E := energyVec m q
  let d := dot v q
  let s := normSq v
  let Ep : ℝ → ℝ := fun ε => energyVec m (add q (scale (t ε) v))
  let R : ℝ → ℝ := fun ε => Ep ε ^ 2 - (E^2 + 2*a*d*ε^2)
  have hEp : 0 < E := lt_of_le_of_ne (energyVec_nonneg m q) (Ne.symm hE)
  have ht2 : t =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := path_isBigO_sq ht
  have htSq : (fun ε => t ε ^ 2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    exact (ht2.pow 2).congr_right (by intro ε; ring)
  have hR : R =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
    have hsum := (ht.const_mul_left (2*d)).add (htSq.const_mul_left s)
    exact hsum.congr_left (by
      intro ε
      dsimp [R, Ep, E, d, s]
      rw [energyVec_add_scale_sq]
      ring)
  have hsq2 : (fun ε => Ep ε ^ 2 - E^2) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
    have hR2 := hR.trans pow4_isBigO_pow2_positive
    have hp := (isBigO_refl (fun ε : ℝ => ε^2) (𝓝[>] 0)).const_mul_left
      (2*a*d)
    exact (hR2.add hp).congr_left (by
      intro ε
      dsimp [R]
      ring)
  have hden : ∀ᶠ ε in 𝓝[>] 0, E ≤ |Ep ε + E| := by
    filter_upwards with ε
    rw [abs_of_nonneg (add_nonneg (energyVec_nonneg _ _) hEp.le)]
    linarith [energyVec_nonneg m (add q (scale (t ε) v))]
  have hdiff2 : (fun ε => Ep ε - E) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
    have hdiv := div_isBigO_of_eventually_abs_ge hsq2 hEp hden
    apply hdiv.congr'
    · filter_upwards with ε
      have hne : Ep ε + E ≠ 0 := by
        exact ne_of_gt (add_pos_of_nonneg_of_pos
          (energyVec_nonneg m (add q (scale (t ε) v))) hEp)
      rw [div_eq_iff hne]
      ring
    · exact Filter.Eventually.of_forall (fun ε => rfl)
  have hprod :
      (fun ε => (a*d/E) * ε^2 * (Ep ε - E)) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^4) := by
    have he2 : (fun ε : ℝ => ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) :=
      isBigO_refl _ _
    have h := (he2.mul hdiff2).const_mul_left (a*d/E)
    exact h.congr' (Filter.Eventually.of_forall (fun ε => by ring))
      (Filter.Eventually.of_forall (fun ε => by ring))
  have hnum := hR.sub hprod
  have hquot := div_isBigO_of_eventually_abs_ge hnum hEp hden
  apply hquot.congr'
  · filter_upwards with ε
    have hne : Ep ε + E ≠ 0 := by
      exact ne_of_gt (add_pos_of_nonneg_of_pos
        (energyVec_nonneg m (add q (scale (t ε) v))) hEp)
    change (R ε - (a*d/E) * ε^2 * (Ep ε - E)) / (Ep ε + E) =
      Ep ε - (E + (a*d/E) * ε^2)
    rw [div_eq_iff hne]
    dsimp [R]
    field_simp [show E ≠ 0 from ne_of_gt hEp]
    ring
  · exact Filter.Eventually.of_forall (fun ε => by ring)

/-- The moving transformed continuum energy through the first lattice correction. -/
theorem boostedMovingEnergy_expansion_isBigO {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    (fun ε => energyVec m (discreteBoostMomentum m k v ε) -
      (continuumBoostEnergy m k v +
        ((-gamma v * correctionVec m k) *
          dot v (continuumBoostMomentum m k v) /
            continuumBoostEnergy m k v) * ε^2))
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have hE' : energyVec m (continuumBoostMomentum m k v) ≠ 0 := by
    rw [continuumBoostMomentum, energyVec_boostMomentum hv hE]
    exact ne_of_gt (boostEnergy_pos hv hE)
  have ht := boostDisplacement_expansion_isBigO (m := m) (k := k) (v := v) hE
  have hshift := shiftedEnergy_expansion_isBigO
    (m := m) (q := continuumBoostMomentum m k v) (v := v)
    (a := -gamma v * correctionVec m k) hE' ht
  apply hshift.congr_left
  intro ε
  rw [discreteBoostMomentum_eq_continuum_add]
  rw [continuumBoostEnergy, continuumBoostMomentum, energyVec_boostMomentum hv hE]

end KomorebiPhysics.Relativistic3DDiscreteBoost
