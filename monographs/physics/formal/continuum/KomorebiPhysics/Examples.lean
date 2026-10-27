module
public import KomorebiPhysics.Refinement

/-! Exact, nonzero realizations and hypothesis-sensitivity checks.
These are kernel proofs, not floating point experiments. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.Examples
open scoped BigOperators

/-- Coordinate projectors give an actual atlas in every finite dimension. -/
def coordinateMap {I : Type*} [Fintype I] [DecidableEq I] (i : I) :
    EuclideanSpace ℂ I →L[ℂ] EuclideanSpace ℂ I :=
  (EuclideanSpace.proj i).smulRight (PiLp.single 2 i 1)

theorem coordinateMap_apply {I : Type*} [Fintype I] [DecidableEq I]
    (i j : I) (v : EuclideanSpace ℂ I) :
    coordinateMap i v j = if j = i then v i else 0 := by
  simp [coordinateMap, PiLp.single_apply, mul_ite]

def coordinateAtlas (I : Type*) [Fintype I] [DecidableEq I] :
    Atlas (EuclideanSpace ℂ I) I where
  proj := coordinateMap
  mul_proj := by
    intro i j
    ext v k
    simp only [mul_apply_eq_comp, coordinateMap_apply]
    split_ifs <;> simp_all [coordinateMap_apply]
  sum_proj := by
    ext v k
    simp [sum_apply, coordinateMap_apply]
  selfAdjoint := by
    intro i x y
    simp [EuclideanSpace.inner_eq_star_dotProduct, dotProduct,
      coordinateMap_apply, apply_ite]

/-- Nonzero state with two orthogonal, populated sectors. -/
def state2 : EuclideanSpace ℂ (Fin 2) :=
  PiLp.single 2 0 1 + PiLp.single 2 1 1

/-- The real skew matrix [[0,-1],[1,0]] acting on complex two-vectors. -/
def rotation2 : EuclideanSpace ℂ (Fin 2) →L[ℂ] EuclideanSpace ℂ (Fin 2) :=
  (EuclideanSpace.proj 0).smulRight (PiLp.single 2 1 1) -
  (EuclideanSpace.proj 1).smulRight (PiLp.single 2 0 1)

theorem rotation2_skew : IsSkew rotation2 := by
  intro x y
  simp [rotation2, EuclideanSpace.inner_eq_star_dotProduct, dotProduct,
    Fin.sum_univ_two, PiLp.single_apply]

/-- Current is genuinely nonzero, with the correct orientation and sign. -/
theorem exact_two_sector_current :
    (coordinateAtlas (Fin 2)).current rotation2 state2 0 1 = -2 ∧
    (coordinateAtlas (Fin 2)).current rotation2 state2 1 0 = 2 := by
  constructor <;>
    norm_num [Atlas.current, Atlas.packet, pairCurrent, coordinateAtlas,
      coordinateMap, rotation2, state2, EuclideanSpace.inner_eq_star_dotProduct,
      dotProduct, Fin.sum_univ_two, PiLp.single_apply]

/-- Removing skew-adjointness invalidates diagonal-current cancellation:
the identity generator has a strictly nonzero self-current. -/
theorem identity_current_nonzero :
    pairCurrent (1 : ℂ →L[ℂ] ℂ) 1 1 = 2 := by
  norm_num [pairCurrent]

/-- Explicit refutation of the overstrong no-hypothesis conservation claim. -/
theorem identity_not_skew : ¬ IsSkew (1 : ℂ →L[ℂ] ℂ) := by
  intro h
  have hz := pairCurrent_self (1 : ℂ →L[ℂ] ℂ) h 1
  rw [identity_current_nonzero] at hz
  norm_num at hz

end KomorebiPhysics.Examples
