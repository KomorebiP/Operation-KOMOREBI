import PaperXI.HeisenbergGroup
import PaperXI.SchrodingerOperator
import PaperXI.SchrodingerIrreducible

/-! The actual finite Schrödinger representation of the Heisenberg group,
its invertible operators, central character, and irreducibility. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.Heisenberg

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

/-- The manuscript operator formula is a representation of the actual group. -/
def representation (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0) :
    Representation ℂ (Element K X) (X → ℂ) where
  toFun a := Schrodinger.operator ψ a.position a.frequency a.central
  map_one' := Schrodinger.operator_one ψ
  map_mul' a b := (Schrodinger.operator_mul ψ h2 a.position b.position
    a.frequency b.frequency a.central b.central).symm

@[simp] theorem representation_apply (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (a : Element K X) (f : X → ℂ) (u : X) :
    representation ψ h2 a f u =
      ψ (a.central + a.frequency u + (2 : K)⁻¹ * a.frequency a.position) *
        f (u + a.position) := rfl

/-- The same representation with its values bundled in the general linear group. -/
def representationGL (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0) :
    Element K X →* Units (Module.End ℂ (X → ℂ)) :=
  (representation ψ h2).asGroupHom

@[simp] theorem representationGL_coe (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (a : Element K X) :
    (representationGL ψ h2 a : Module.End ℂ (X → ℂ)) = representation ψ h2 a :=
  Representation.asGroupHom_apply _ a

/-- Every Schrödinger operator is invertible. -/
theorem representation_isUnit (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (a : Element K X) : IsUnit (representation ψ h2 a) := by
  rw [← representationGL_coe ψ h2 a]
  exact (representationGL ψ h2 a).isUnit

theorem central_action (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0) (z : K) :
    representation ψ h2 (centralElement (X := X) z) = ψ z • LinearMap.id :=
  Schrodinger.operator_central ψ z

theorem translation_action (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0) (x : X) :
    representation ψ h2 (translationElement (K := K) x) = Schrodinger.translation x :=
  Schrodinger.operator_translation ψ x

theorem modulation_action (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (ξ : Module.Dual K X) :
    representation ψ h2 (modulationElement ξ) = Schrodinger.modulation ψ ξ :=
  Schrodinger.operator_modulation ψ ξ

/-- The representation is irreducible for every nontrivial central character,
including the one-dimensional function space when `X` is zero-dimensional. -/
theorem irreducible [Fintype X] (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
    (h2 : (2 : K) ≠ 0) : Representation.IsIrreducible (representation (X := X) ψ h2) := by
  apply SchrodingerIrreducible.irreducible_of_actions ψ hψ
  · intro x
    refine ⟨translationElement (K := K) x, ?_⟩
    intro f u
    rw [translation_action]
    rfl
  · intro ξ
    refine ⟨modulationElement ξ, ?_⟩
    intro f u
    rw [modulation_action]
    rfl

end PaperXI.Heisenberg
