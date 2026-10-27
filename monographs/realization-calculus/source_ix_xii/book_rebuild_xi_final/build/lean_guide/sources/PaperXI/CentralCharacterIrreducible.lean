import PaperXI.CentralCharacterAction
import PaperXI.CentralCharacterRepresentation
import PaperXI.AlgebraActionModule
import PaperXI.RepresentationStability

/-! Irreducibility of an actual central-character representation is equivalent
to simplicity of its constructed twisted-algebra module. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralCharacter
open CentralExtension

variable {Z H A W : Type*} [CommGroup Z] [Group H] [CommGroup A] [Fintype A]
variable [AddCommGroup W] [Module ℂ W]

/-- The forward action preserves and reflects irreducibility, including the
nonzero-space condition. -/
theorem irreducible_iff_simple (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    Representation.IsIrreducible σ ↔
      IsSimpleModule (Algebra D ζ)
        (AlgebraActionModule.Space (B := ↥(Algebra D ζ)) (toAlgebraAction D ζ σ hcentral)) := by
  rw [RepresentationStability.irreducible_iff, AlgebraActionModule.simple_iff]
  apply and_congr_right
  intro _
  constructor
  · intro h S hS
    exact h S ((action_stable_iff D ζ σ hcentral S).mp hS)
  · intro h S hS
    exact h S ((action_stable_iff D ζ σ hcentral S).mpr hS)

/-- An actual irreducible representation supplies an actual simple module. -/
theorem simpleModule (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    IsSimpleModule (Algebra D ζ)
      (AlgebraActionModule.Space (B := ↥(Algebra D ζ)) (toAlgebraAction D ζ σ hcentral)) :=
  (irreducible_iff_simple D ζ σ hcentral).mp inferInstance

/-- The reverse action construction preserves and reflects simplicity. -/
theorem ofAlgebraAction_irreducible_iff (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (φ : Algebra D ζ →ₐ[ℂ] Module.End ℂ W) :
    Representation.IsIrreducible (ofAlgebraAction D ζ φ) ↔
      IsSimpleModule (Algebra D ζ) (AlgebraActionModule.Space (B := ↥(Algebra D ζ)) φ) := by
  rw [irreducible_iff_simple D ζ (ofAlgebraAction D ζ φ) (ofAlgebraAction_central D ζ φ),
    to_ofAlgebraAction]

end PaperXI.CentralCharacter
