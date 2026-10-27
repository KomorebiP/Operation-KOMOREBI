import PaperX.AbsoluteGaloisRestriction
import Mathlib.FieldTheory.Galois.IsGaloisGroup
import Mathlib.FieldTheory.Galois.Profinite
import Mathlib.RingTheory.Invariant.Profinite
import Mathlib.RingTheory.Localization.Integral
import Mathlib.FieldTheory.Perfect
import Mathlib.Topology.Algebra.MulAction

set_option autoImplicit false
noncomputable section
namespace Probe
abbrev Ω := AlgebraicClosure ℚ
abbrev G := Gal(Ω/ℚ)
abbrev B := integralClosure ℤ Ω

instance : Algebra.IsAlgebraic ℤ Ω :=
  IsFractionRing.comap_isAlgebraic_iff.mpr (inferInstance : Algebra.IsAlgebraic ℚ Ω)

instance : IsFractionRing B Ω :=
  integralClosure.isFractionRing_of_algebraic (A := ℤ)
    (fun _ hx => (FaithfulSMul.algebraMap_injective ℤ Ω) (hx.trans (map_zero _).symm))

instance : IsGaloisGroup G ℤ B := IsGaloisGroup.of_isFractionRing G ℤ B ℚ Ω

example : Algebra.IsInvariant ℤ B G := inferInstance
example : CompactSpace G := inferInstance
example : TotallyDisconnectedSpace G := inferInstance

local instance : TopologicalSpace B := ⊥
local instance : DiscreteTopology B := ⟨rfl⟩

instance : ContinuousSMul G B := by
  apply continuousSMul_iff_stabilizer_isOpen.mpr
  intro x
  convert stabilizer_isOpen_of_isIntegral (K := ℚ) (x : Ω) using 1
  ext σ
  simp only [SetLike.mem_coe, MulAction.mem_stabilizer_iff, Subtype.ext_iff]
  rfl

end Probe
