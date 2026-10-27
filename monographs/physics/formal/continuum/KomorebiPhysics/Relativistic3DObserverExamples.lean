module

public import KomorebiPhysics.Relativistic3DObserverDefect

/-!
Exact witnesses for the three-dimensional observer-shell defect.  The first
checks exact covariance for a stationary observer.  The second gives a fully
rational nonzero coefficient at `m=3`, `k=(4,0,0)`, and `v=(3/5,0,0)`.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DObserverExamples

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Relativistic3DLorentzKinematics
open KomorebiPhysics.Relativistic3DDiscreteBoost
open KomorebiPhysics.Relativistic3DObserverDefect

/-- Source momentum for the rational observer witness. -/
def observerExampleK : Vec3 := ⟨4, 0, 0⟩

/-- Subluminal velocity for the rational observer witness. -/
def observerExampleV : Vec3 := ⟨3/5, 0, 0⟩

/-- The witness velocity is subluminal. -/
theorem observerExample_subluminal : normSq observerExampleV < 1 := by
  norm_num [observerExampleV, normSq, dot]

/-- The source continuum energy is exactly five. -/
theorem observerExample_energy : energyVec 3 observerExampleK = 5 := by
  have hs : Real.sqrt (25 : ℝ) = 5 := by
    have h5 : (0 : ℝ) ≤ 5 := by norm_num
    rw [← Real.sqrt_sq h5]
    norm_num
  norm_num [observerExampleK, energyVec,
    KomorebiPhysics.Relativistic3DShellAsymptotics.energy3, hs]

/-- The witness Lorentz factor is `5/4`. -/
theorem observerExample_gamma : gamma observerExampleV = 5/4 := by
  have hs : Real.sqrt (16/25 : ℝ) = 4/5 := by
    apply (Real.sqrt_eq_iff_eq_sq (by norm_num) (by norm_num)).2
    norm_num
  rw [gamma]
  norm_num [observerExampleV, normSq, dot, hs]

/-- The transformed continuum energy is exactly `13/4`. -/
theorem observerExample_boostEnergy :
    continuumBoostEnergy 3 observerExampleK observerExampleV = 13/4 := by
  rw [continuumBoostEnergy, boostEnergy, observerExample_gamma,
    observerExample_energy]
  norm_num [observerExampleK, observerExampleV, dot]

/-- The transformed continuum momentum is `(5/4,0,0)`. -/
theorem observerExample_boostMomentum :
    continuumBoostMomentum 3 observerExampleK observerExampleV =
      (⟨5/4, 0, 0⟩ : Vec3) := by
  have hg : gamma observerExampleV = 5/4 := observerExample_gamma
  have hE : energyVec 3 observerExampleK = 5 := observerExample_energy
  rw [continuumBoostMomentum, boostMomentum, boostCoeff, boostAlpha, hg, hE]
  apply Vec3.ext <;>
    norm_num [observerExampleK, observerExampleV, dot, add, scale]

/-- Source anisotropy polynomial for the witness. -/
theorem observerExample_sourceAnisotropy :
    anisotropyVec 3 observerExampleK = 144 := by
  norm_num [anisotropyVec, observerExampleK,
    KomorebiPhysics.Relativistic3DShellAsymptotics.anisotropyQ]

/-- Transformed anisotropy polynomial for the witness. -/
theorem observerExample_transformedAnisotropy :
    anisotropyVec 3
      (continuumBoostMomentum 3 observerExampleK observerExampleV) = 225/16 := by
  rw [observerExample_boostMomentum]
  norm_num [anisotropyVec,
    KomorebiPhysics.Relativistic3DShellAsymptotics.anisotropyQ]

/-- Exact nonzero leading observer-shell coefficient. -/
theorem observerExample_defectCoeff :
    observerDefectCoeff 3 observerExampleK observerExampleV = -693/104 := by
  rw [observerDefectCoeff, observerExample_boostEnergy,
    observerExample_sourceAnisotropy, observerExample_transformedAnisotropy]
  norm_num

/-- The rational example certifies a genuine quadratic Lorentz defect. -/
theorem observerExample_defectCoeff_ne_zero :
    observerDefectCoeff 3 observerExampleK observerExampleV ≠ 0 := by
  rw [observerExample_defectCoeff]
  norm_num

/-- Checked asymptotic defect for the rational witness. -/
theorem observerExample_expansion_isBigO :
    (fun ε => observerDefect 3 observerExampleK observerExampleV ε -
      (-693/104) * ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  rw [← observerExample_defectCoeff]
  exact observerDefect_expansion_isBigO observerExample_subluminal
    (by rw [observerExample_energy]; norm_num)

/-- A stationary observer has identically zero defect, not merely zero leading coefficient. -/
theorem observerStationary_exact (m : ℝ) (k : Vec3) :
    (fun ε => observerDefect m k zero ε) = fun _ => 0 := by
  funext ε
  exact observerDefect_zero_velocity m k ε

end KomorebiPhysics.Relativistic3DObserverExamples
