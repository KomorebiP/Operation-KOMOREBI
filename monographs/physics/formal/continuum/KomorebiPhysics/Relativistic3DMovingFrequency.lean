module

public import KomorebiPhysics.Relativistic3DMovingShell

/-!
Moving-argument transfer for the exact principal lattice frequency.  The theorem
keeps the lattice correction frozen at the limiting transformed momentum while
allowing the exact transformed momentum itself to vary by `O(ε²)`.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DMovingFrequency

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Dispersion3D
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit
open KomorebiPhysics.Relativistic3DLorentzKinematics
open KomorebiPhysics.Relativistic3DDiscreteBoost
open KomorebiPhysics.Relativistic3DPathInversion
open KomorebiPhysics.Relativistic3DMovingShell

/-- Exact lattice frequency along a scalar moving-momentum path. -/
def movingFrequency (m : ℝ) (q v : Vec3) (t : ℝ → ℝ) (ε : ℝ) : ℝ :=
  frequencyVec m (add q (scale (t ε) v)) ε

/-- On positive spacings, the concrete moving frequency is the generic shell quotient. -/
theorem eventually_movingFrequency_eq_path
    (m : ℝ) (q v : Vec3) (t : ℝ → ℝ) :
    ∀ᶠ ε in 𝓝[>] 0,
      movingFrequency m q v t ε =
        pathPositiveFrequency (movingShell m q v t) (energyVec m q) ε := by
  filter_upwards [self_mem_nhdsWithin] with ε hε
  have hne : ε ≠ 0 := ne_of_gt hε
  rw [movingFrequency, frequencyVec]
  rw [positiveFrequency3_of_pos _ _ _ _ _ hε]
  rw [pathPositiveFrequency_of_pos _ _ _ hε]
  simp only [frequency, pathPhase, phase]
  congr 2

/-- Closed form of the correction produced by the transported shell quartic. -/
theorem pathCorrection_movingShellQuartic
    {m a : ℝ} {q v : Vec3} (hE : energyVec m q ≠ 0) :
    pathCorrection (energyVec m q) (movingShellQuartic m a q v) =
      correctionVec m q + a * dot v q / energyVec m q := by
  have hE3 : energy3 m q.x q.y q.z ≠ 0 := by
    simpa [energyVec] using hE
  rw [pathCorrection, movingShellQuartic, correctionVec, correction3,
    shellQuarticCoeffSource3, energyVec]
  field_simp [hE3]
  ring

/-- The generic path inversion written in physical moving-frequency notation. -/
theorem movingFrequency_fixedBase_expansion_isBigO
    {m a : ℝ} {q v : Vec3} {t : ℝ → ℝ}
    (hE : energyVec m q ≠ 0)
    (ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε => movingFrequency m q v t ε -
      (energyVec m q +
        (correctionVec m q + a * dot v q / energyVec m q) * ε^2))
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have hEp : 0 < energyVec m q :=
    lt_of_le_of_ne (energyVec_nonneg m q) (Ne.symm hE)
  have hshell := movingShell_expansion_isBigO (m := m) q v ht
  have hinv := pathPositiveFrequency_expansion_isBigO hEp hshell
  apply hinv.congr'
  · filter_upwards [eventually_movingFrequency_eq_path m q v t] with ε hfreq
    rw [hfreq]
    rw [pathFrequencyPoly2, pathCorrection_movingShellQuartic hE]
  · exact Filter.Eventually.of_forall (fun ε => rfl)

/-- Main moving-argument transfer theorem.

The exact frequency is evaluated at the moving momentum, while the quadratic
lattice coefficient is evaluated at the limiting base momentum.
-/
theorem movingFrequency_expansion_isBigO
    {m a : ℝ} {q v : Vec3} {t : ℝ → ℝ}
    (hE : energyVec m q ≠ 0)
    (ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4)) :
    (fun ε => movingFrequency m q v t ε -
      (energyVec m (add q (scale (t ε) v)) + correctionVec m q * ε^2))
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have hfreq := movingFrequency_fixedBase_expansion_isBigO
    (m := m) (q := q) (v := v) (t := t) (a := a) hE ht
  have henergy := shiftedEnergy_expansion_isBigO
    (m := m) (q := q) (v := v) (a := a) hE ht
  have h := hfreq.sub henergy
  exact h.congr_left (by intro ε; ring)

/-- Block-22 specialization to the Lorentz-transformed discrete momentum. -/
theorem boostedMovingFrequency_expansion_isBigO
    {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    (fun ε => frequencyVec m (discreteBoostMomentum m k v ε) ε -
      (energyVec m (discreteBoostMomentum m k v ε) +
        correctionVec m (continuumBoostMomentum m k v) * ε^2))
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  let q := continuumBoostMomentum m k v
  let t := boostDisplacement m k v
  let a := -gamma v * correctionVec m k
  have hq : energyVec m q ≠ 0 := by
    dsimp [q, continuumBoostMomentum]
    rw [energyVec_boostMomentum hv hE]
    exact ne_of_gt (boostEnergy_pos hv hE)
  have ht : (fun ε => t ε - a*ε^2) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) := by
    simpa [t, a] using
      (boostDisplacement_expansion_isBigO (m := m) (k := k) (v := v) hE)
  have hmove := movingFrequency_expansion_isBigO
    (m := m) (q := q) (v := v) (t := t) (a := a) hq ht
  apply hmove.congr_left
  intro ε
  dsimp [movingFrequency, q, t]
  rw [discreteBoostMomentum_eq_continuum_add]

end KomorebiPhysics.Relativistic3DMovingFrequency
