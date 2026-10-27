import Mathlib.RepresentationTheory.Irreducible
import Mathlib.Algebra.Algebra.Equiv

/-! Construct the central character of the given irreducible finite-dimensional representation. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DerivedCentralCharacter69
open Representation
variable {k H V : Type*} [Field k] [IsAlgClosed k] [Group H]
  [AddCommGroup V] [Module k V] [FiniteDimensional k V]
  (ρ : Representation k H V) [IsIrreducible ρ]
  (Z : Subgroup H) (hZ : ∀ z : Z, ∀ h : H, Commute (z : H) h)

/-- Central representation operators, as actual endomorphism intertwiners. -/
def centralAction : Z →* IntertwiningMap ρ ρ where
  toFun z :=
    { toLinearMap := ρ (z : H)
      isIntertwining' h := by
        change ρ (z : H) * ρ h = ρ h * ρ (z : H)
        rw [← map_mul, ← map_mul, (hZ z h).eq] }
  map_one' := by ext v; simp
  map_mul' z w := by ext v; simp [← map_mul]

/-- Schur's lemma identifies the entire endomorphism-intertwiner algebra with scalars. -/
def scalarEquiv : k ≃ₐ[k] IntertwiningMap ρ ρ :=
  AlgEquiv.ofBijective (Algebra.ofId k (IntertwiningMap ρ ρ))
    (IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed (ρ := ρ))

/-- The central scalar function is a multiplicative character with values in units. -/
def character : Z →* kˣ :=
  MonoidHom.toHomUnits ((scalarEquiv ρ).symm.toMonoidHom.comp (centralAction ρ Z hZ))

/-- The constructed character acts by precisely the given central operators. -/
theorem character_apply (z : Z) (v : V) :
    ρ (z : H) v = (character ρ Z hZ z : k) • v := by
  have he := (scalarEquiv ρ).apply_symm_apply (centralAction ρ Z hZ z)
  have hev := congrArg (fun f : IntertwiningMap ρ ρ => f v) he
  change ((scalarEquiv ρ).symm (centralAction ρ Z hZ z)) • v = ρ (z : H) v at hev
  exact hev.symm

end PaperXI.DerivedCentralCharacter69
