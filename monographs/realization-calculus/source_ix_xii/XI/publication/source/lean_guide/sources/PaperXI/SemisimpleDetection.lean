import Mathlib.RepresentationTheory.Maschke
import PaperXI.CharacterProjector

/-! Maschke separation: literal elements of C[G] are detected on simple modules.
No choice of a complete irreducible character table is assumed. -/
set_option autoImplicit false
noncomputable section
open scoped MonoidAlgebra BigOperators
namespace PaperXI.SemisimpleDetection
universe u
variable {G : Type u} [Group G] [Fintype G]

/-- Vanishing on all simple left ideals forces an element to be zero. -/
theorem eq_zero_of_simple_actions (a : MonoidAlgebra ℂ G)
    (h : ∀ S : Submodule (MonoidAlgebra ℂ G) (MonoidAlgebra ℂ G),
      IsSimpleModule (MonoidAlgebra ℂ G) S →
      (Representation.ofModule (k := ℂ) (G := G) S).asAlgebraHom a = 0) : a = 0 := by
  let A := MonoidAlgebra ℂ G
  have : NeZero (Nat.card G : ℂ) := ⟨by exact_mod_cast (Nat.card_pos (α := G)).ne'⟩
  have htop : (⊤ : Submodule ℂ A) ≤ (LinearMap.mulLeft ℂ a).ker := by
    calc
      ⊤ = (sSup {S : Submodule A A | IsSimpleModule A S}).restrictScalars ℂ := by
        rw [IsSemisimpleModule.sSup_simples_eq_top, Submodule.restrictScalars_top]
      _ = sSup (Submodule.restrictScalars ℂ '' {S : Submodule A A | IsSimpleModule A S}) :=
        Submodule.restrictScalars_sSup ℂ _
      _ ≤ (LinearMap.mulLeft ℂ a).ker := by
        apply sSup_le
        rintro T ⟨S, hS, rfl⟩ x hx
        have hz := LinearMap.congr_fun (h S hS)
          ((RestrictScalars.addEquiv ℂ A S).symm ⟨x, hx⟩)
        rw [Representation.ofModule_asAlgebraHom_apply_apply] at hz
        have hv := congrArg (fun z : RestrictScalars ℂ A S =>
          ((RestrictScalars.addEquiv ℂ A S) z).val) hz
        change a * x = 0 at hv
        exact hv
  have ha := htop (show (1 : A) ∈ (⊤ : Submodule ℂ A) from trivial)
  simpa using ha

set_option backward.isDefEq.respectTransparency false in
/-- It suffices to test actual finite-dimensional irreducible representations. -/
theorem eq_zero_of_irreducible_actions (a : MonoidAlgebra ℂ G)
    (h : ∀ (W : Type u) [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
      (σ : Representation ℂ G W) [Representation.IsIrreducible σ],
      σ.asAlgebraHom a = 0) : a = 0 := by
  apply eq_zero_of_simple_actions a
  intro S hS
  have : Representation.IsIrreducible (Representation.ofModule (k := ℂ) (G := G) S) :=
    (Representation.isSimpleModule_iff_irreducible_ofModule (k := ℂ) (G := G) S).mp hS
  let e : RestrictScalars ℂ (MonoidAlgebra ℂ G) S ≃ₗ[ℂ] S :=
    { toAddEquiv := RestrictScalars.addEquiv ℂ (MonoidAlgebra ℂ G) S
      map_smul' := by
        intro c x
        exact (RestrictScalars.addEquiv_map_smul ℂ (MonoidAlgebra ℂ G) S c x).trans
          (IsScalarTower.algebraMap_smul (MonoidAlgebra ℂ G) c _) }
  have : FiniteDimensional ℂ S :=
    Module.Finite.of_injective (S.subtype.restrictScalars ℂ) S.subtype_injective
  have : FiniteDimensional ℂ (RestrictScalars ℂ (MonoidAlgebra ℂ G) S) :=
    Module.Finite.equiv e.symm
  exact h _ (Representation.ofModule (k := ℂ) (G := G) S)

/-- Equality of group-algebra elements can be checked on irreducibles. -/
theorem eq_of_irreducible_actions (a b : MonoidAlgebra ℂ G)
    (h : ∀ (W : Type u) [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
      (σ : Representation ℂ G W) [Representation.IsIrreducible σ],
      σ.asAlgebraHom a = σ.asAlgebraHom b) : a = b := by
  apply sub_eq_zero.mp
  apply eq_zero_of_irreducible_actions
  intro W _ _ _ σ _
  rw [map_sub, h W σ, sub_self]

end PaperXI.SemisimpleDetection
