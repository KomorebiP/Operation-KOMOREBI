import PaperXI.HeisenbergSource
import PaperXI.HeisenbergSelector
import PaperXI.HeisenbergProjector

/-! Source propositions 7.5 and 7.6 for the canonical odd-prime model.
The finite enumeration of each isotropic subspace is constructed here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergSourceProjector
open HeisenbergForm HeisenbergGeometry
open scoped Classical BigOperators

variable {p : ℕ} [Fact p.Prime]
variable {X : Type*} [AddCommGroup X] [Module (ZMod p) X] [Fintype X]
  [FiniteDimensional (ZMod p) X]

def projector (hp : p ≠ 2) (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X))
    (hL : IsIsotropic form L) : Module.End ℂ (X → ℂ) := by
  let : Finite L := Module.finite_of_finite (ZMod p)
  let : Fintype L := Fintype.ofFinite L
  exact HeisenbergProjector.projector (K := ZMod p) ZMod.stdAddChar (HeisenbergPrime.two_ne_zero hp) L hL

omit [Fintype X] in
theorem idempotent (hp : p ≠ 2)
    (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X)) (hL : IsIsotropic form L) :
    (projector hp L hL).comp (projector hp L hL) = projector hp L hL := by
  unfold projector
  let : Finite L := Module.finite_of_finite (ZMod p)
  let : Fintype L := Fintype.ofFinite L
  exact HeisenbergProjector.idempotent (K := ZMod p) (X := X) ZMod.stdAddChar
    (HeisenbergPrime.two_ne_zero hp) L hL

omit [Fintype X] in
theorem range_eq_invariants (hp : p ≠ 2)
    (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X)) (hL : IsIsotropic form L) :
    LinearMap.range (projector hp L hL) =
      Representation.invariants (G := Multiplicative L)
        (HeisenbergProjector.restriction ZMod.stdAddChar
          (HeisenbergPrime.two_ne_zero hp) L hL) := by
  unfold projector
  let : Finite L := Module.finite_of_finite (ZMod p)
  let : Fintype L := Fintype.ofFinite L
  exact HeisenbergProjector.range_eq_invariants (K := ZMod p) (X := X) ZMod.stdAddChar
    (HeisenbergPrime.two_ne_zero hp) L hL

theorem self_adjoint (hp : p ≠ 2)
    (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X)) (hL : IsIsotropic form L)
    (f g : X → ℂ) :
    TranslationAverage.pairing (projector hp L hL f) g =
      TranslationAverage.pairing f (projector hp L hL g) := by
  unfold projector
  let : Finite L := Module.finite_of_finite (ZMod p)
  let : Fintype L := Fintype.ofFinite L
  exact HeisenbergProjector.self_adjoint (K := ZMod p) (X := X) ZMod.stdAddChar
    (HeisenbergPrime.two_ne_zero hp) L hL f g

theorem residual_orthogonal (hp : p ≠ 2)
    (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X)) (hL : IsIsotropic form L)
    (f : X → ℂ) {g : X → ℂ} (hg : g ∈ LinearMap.range (projector hp L hL)) :
    TranslationAverage.pairing (f - projector hp L hL f) g = 0 := by
  unfold projector
  let : Finite L := Module.finite_of_finite (ZMod p)
  let : Fintype L := Fintype.ofFinite L
  exact HeisenbergProjector.residual_orthogonal (K := ZMod p) (X := X) ZMod.stdAddChar
    (HeisenbergPrime.two_ne_zero hp) L hL f hg

omit [Fintype X] [FiniteDimensional (ZMod p) X] in
theorem lift_central_iff_identity (hp : p ≠ 2)
    (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X)) (hL : IsIsotropic form L)
    (a : Multiplicative L) :
    HeisenbergProjector.liftHom L hL a ∈ Subgroup.center (Heisenberg.Element (ZMod p) X) ↔
      a = 1 := by
  rw [HeisenbergCenter.mem_center_iff (HeisenbergPrime.two_ne_zero hp)]
  exact HeisenbergSelector.coordinates_zero_iff L a

theorem position_range (hp : p ≠ 2) :
    LinearMap.range (projector (X := X) hp HeisenbergProjector.positionSpace
      HeisenbergProjector.position_isotropic) = TranslationAverage.constantSubmodule := by
  unfold projector
  dsimp only
  have he : Fintype.ofFinite (HeisenbergProjector.positionSpace (K := ZMod p) (X := X)) =
      HeisenbergProjector.positionFintype := Subsingleton.elim _ _
  rw [he]
  exact HeisenbergProjector.position_range_eq
    (K := ZMod p) (X := X) ZMod.stdAddChar (HeisenbergPrime.two_ne_zero hp)

theorem position_rank_one (hp : p ≠ 2) :
    Module.finrank ℂ (LinearMap.range (projector (X := X) hp HeisenbergProjector.positionSpace
      HeisenbergProjector.position_isotropic)) = 1 := by
  rw [position_range]
  have h := HeisenbergProjector.position_rank_one
    (K := ZMod p) (X := X) ZMod.stdAddChar (HeisenbergPrime.two_ne_zero hp)
  rw [HeisenbergProjector.position_range_eq] at h
  exact h


theorem maximal_rank_one (hp : p ≠ 2)
    (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X))
    (hL : IsMaximalIsotropic form L) :
    Module.finrank ℂ (LinearMap.range (projector hp L hL.1)) = 1 := by
  unfold projector
  let : Finite L := Module.finite_of_finite (ZMod p)
  let : Fintype L := Fintype.ofFinite L
  exact HeisenbergSelector.maximal_rank_one (K := ZMod p) (X := X) HeisenbergPrime.character_nontrivial
    (HeisenbergPrime.two_ne_zero hp) L hL

theorem maximal_fixed_line (hp : p ≠ 2)
    (L : Submodule (ZMod p) (X × Module.Dual (ZMod p) X))
    (hL : IsMaximalIsotropic form L) :
    Module.finrank ℂ (Representation.invariants (G := Multiplicative L)
      (HeisenbergProjector.restriction ZMod.stdAddChar
        (HeisenbergPrime.two_ne_zero hp) L hL.1)) = 1 := by
  let : Finite L := Module.finite_of_finite (ZMod p)
  let : Fintype L := Fintype.ofFinite L
  exact HeisenbergSelector.maximal_fixed_line (K := ZMod p) (X := X) HeisenbergPrime.character_nontrivial
    (HeisenbergPrime.two_ne_zero hp) L hL

end PaperXI.HeisenbergSourceProjector
