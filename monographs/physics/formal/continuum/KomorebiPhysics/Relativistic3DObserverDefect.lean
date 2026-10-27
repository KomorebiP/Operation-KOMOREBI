module

public import KomorebiPhysics.Relativistic3DMovingFrequency

/-!
Observer-shell Lorentz defect for the exact three-dimensional lattice walk.
The transformed lattice four-momentum is compared with the exact lattice shell
at its moving transformed spatial momentum.  The moving-argument contribution
is retained and cancels against the transformed source correction, leaving the
closed coefficient `(Q(k') - Q(k)) / (6 E')`.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DObserverDefect

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit
open KomorebiPhysics.Relativistic3DLorentzKinematics
open KomorebiPhysics.Relativistic3DDiscreteBoost
open KomorebiPhysics.Relativistic3DMovingFrequency

/-- Difference between the boosted exact lattice energy and the exact lattice
frequency evaluated at the boosted exact spatial momentum. -/
def observerDefect (m : ℝ) (k v : Vec3) (ε : ℝ) : ℝ :=
  discreteBoostEnergy m k v ε -
    frequencyVec m (discreteBoostMomentum m k v ε) ε

/-- Contribution of the moving transformed momentum to the continuum energy. -/
def movingEnergyCoeff (m : ℝ) (k v : Vec3) : ℝ :=
  (-gamma v * correctionVec m k) *
    dot v (continuumBoostMomentum m k v) /
      continuumBoostEnergy m k v

/-- Coefficient obtained before the Lorentz cancellation is simplified. -/
def observerOperationalCoeff (m : ℝ) (k v : Vec3) : ℝ :=
  gamma v * correctionVec m k -
    (movingEnergyCoeff m k v +
      correctionVec m (continuumBoostMomentum m k v))

/-- Closed leading observer-shell defect coefficient. -/
def observerDefectCoeff (m : ℝ) (k v : Vec3) : ℝ :=
  (anisotropyVec m (continuumBoostMomentum m k v) -
      anisotropyVec m k) /
    (6 * continuumBoostEnergy m k v)

/-- Pure scalar cancellation underlying the observer defect. -/
theorem coefficient_cancellation
    {E Ep d g c cp Q Qp : ℝ}
    (hE : E ≠ 0) (hEp : Ep ≠ 0) (hg : g ≠ 0)
    (hinv : Ep + d = E / g)
    (hc : c = -Q / (6 * E))
    (hcp : cp = -Qp / (6 * Ep)) :
    g*c - ((-g*c)*d/Ep + cp) = (Qp-Q)/(6*Ep) := by
  calc
    g*c - ((-g*c)*d/Ep + cp) = g*c*(Ep+d)/Ep - cp := by
      field_simp [hEp]
      ring
    _ = g*c*(E/g)/Ep - cp := by rw [hinv]
    _ = c*E/Ep - cp := by
      field_simp [hg]
    _ = (Qp-Q)/(6*Ep) := by
      rw [hc, hcp]
      field_simp [hE, hEp]
      ring

/-- The operational coefficient equals the closed anisotropy difference. -/
theorem observerOperationalCoeff_eq_closed
    {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    observerOperationalCoeff m k v = observerDefectCoeff m k v := by
  let E := energyVec m k
  let q := continuumBoostMomentum m k v
  let Ep := continuumBoostEnergy m k v
  let d := dot v q
  have hEpPos : 0 < Ep := by
    dsimp [Ep, continuumBoostEnergy]
    exact boostEnergy_pos hv hE
  have hEp : Ep ≠ 0 := ne_of_gt hEpPos
  have hg : gamma v ≠ 0 := gamma_ne_zero hv
  have hqE : energyVec m q = Ep := by
    dsimp [q, Ep, continuumBoostMomentum, continuumBoostEnergy]
    exact energyVec_boostMomentum hv hE
  have hinv : Ep + d = E / gamma v := by
    dsimp [Ep, d, q, E, continuumBoostEnergy, continuumBoostMomentum]
    exact boostEnergy_add_dot_boostMomentum hv k (energyVec m k)
  have hc : correctionVec m k = -anisotropyVec m k / (6 * E) := by
    rfl
  have hcp : correctionVec m q = -anisotropyVec m q / (6 * Ep) := by
    change -anisotropyQ m q.x q.y q.z / (6 * energy3 m q.x q.y q.z) =
      -anisotropyQ m q.x q.y q.z / (6 * Ep)
    rw [show energy3 m q.x q.y q.z = Ep by simpa [energyVec] using hqE]
  have hcancel := coefficient_cancellation
    (E := E) (Ep := Ep) (d := d) (g := gamma v)
    (c := correctionVec m k) (cp := correctionVec m q)
    (Q := anisotropyVec m k) (Qp := anisotropyVec m q)
    hE hEp hg hinv hc hcp
  simpa [observerOperationalCoeff, movingEnergyCoeff, observerDefectCoeff,
    E, Ep, q, d] using hcancel

/-- The unsimplified observer defect has its checked quadratic jet. -/
theorem observerDefect_operational_expansion_isBigO
    {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    (fun ε => observerDefect m k v ε -
      observerOperationalCoeff m k v * ε^2)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have henergy := discreteBoostEnergy_expansion_isBigO
    (m := m) (k := k) (v := v) hE
  have hmovingEnergy := boostedMovingEnergy_expansion_isBigO
    (m := m) (k := k) (v := v) hv hE
  have hmovingFrequency := boostedMovingFrequency_expansion_isBigO
    (m := m) (k := k) (v := v) hv hE
  have hfrequency := hmovingFrequency.add hmovingEnergy
  have h := henergy.sub hfrequency
  exact h.congr_left (by
    intro ε
    simp only [observerDefect, observerOperationalCoeff, movingEnergyCoeff]
    ring)

/-- Main Block-22 observer-shell theorem.

The exact lattice observer defect has leading coefficient
`(Q(k') - Q(k)) / (6 E')`, including the contribution from the moving
transformed momentum.
-/
theorem observerDefect_expansion_isBigO
    {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    (fun ε => observerDefect m k v ε -
      observerDefectCoeff m k v * ε^2)
      =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  rw [← observerOperationalCoeff_eq_closed hv hE]
  exact observerDefect_operational_expansion_isBigO hv hE

/-- The zero observer velocity gives exact covariance at every spacing. -/
@[simp] theorem observerDefect_zero_velocity
    (m : ℝ) (k : Vec3) (ε : ℝ) :
    observerDefect m k zero ε = 0 := by
  simp [observerDefect, discreteBoostEnergy, discreteBoostMomentum]

/-- The closed leading coefficient also vanishes at zero velocity. -/
@[simp] theorem observerDefectCoeff_zero_velocity
    (m : ℝ) (k : Vec3) :
    observerDefectCoeff m k zero = 0 := by
  simp [observerDefectCoeff, continuumBoostMomentum, continuumBoostEnergy]

/-- A nonzero closed coefficient certifies a genuine leading quadratic defect. -/
theorem observerDefectCoeff_ne_zero_iff
    {m : ℝ} {k v : Vec3}
    (hv : normSq v < 1) (hE : energyVec m k ≠ 0) :
    observerDefectCoeff m k v ≠ 0 ↔
      anisotropyVec m (continuumBoostMomentum m k v) ≠ anisotropyVec m k := by
  have hden : 6 * continuumBoostEnergy m k v ≠ 0 := by
    have hp : 0 < continuumBoostEnergy m k v := by
      dsimp [continuumBoostEnergy]
      exact boostEnergy_pos hv hE
    positivity
  rw [observerDefectCoeff, div_ne_zero_iff, and_iff_left hden, sub_ne_zero]

end KomorebiPhysics.Relativistic3DObserverDefect
