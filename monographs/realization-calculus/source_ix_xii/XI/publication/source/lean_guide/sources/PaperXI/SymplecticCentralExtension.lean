import PaperXI.CentralExtensionStructure
import Mathlib.Algebra.Group.AddChar
import Mathlib.LinearAlgebra.BilinearForm.Basic
import Mathlib.LinearAlgebra.SesquilinearForm.Basic

/-! A nontrivial additive character detects every nonzero vector through a
left-nondegenerate field-valued bilinear commutator. This supplies scalar
nondegeneracy for actual symplectic central extensions in every characteristic. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SymplecticCentralExtension
open PaperXI.CentralExtension PaperXI.CocycleCommutator
variable {K V H : Type*} [Field K] [AddCommGroup V] [Module K V] [Group H]

/-- An additive character is an honest unit-valued character of the
multiplicatively tagged scalar group. -/
def scalarCharacter (ψ : AddChar K ℂ) : Multiplicative K →* ℂˣ :=
  ψ.toMonoidHom.toHomUnits

@[simp] theorem scalarCharacter_apply (ψ : AddChar K ℂ) (z : Multiplicative K) :
    (scalarCharacter ψ z : ℂ) = ψ z.toAdd := rfl

@[simp] theorem scalarCharacter_ofAdd (ψ : AddChar K ℂ) (z : K) :
    (scalarCharacter ψ (Multiplicative.ofAdd z) : ℂ) = ψ z := rfl

/-- A merely nontrivial character suffices because every nonzero field-linear
functional takes every scalar value. Faithfulness of the character is not assumed. -/
theorem character_separating_left (b : LinearMap.BilinForm K V) (hb : b.SeparatingLeft)
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (v : V)
    (hv : ∀ w : V, ψ (b v w) = 1) : v = 0 := by
  apply hb v
  intro w
  by_contra hw
  obtain ⟨t, ht⟩ := AddChar.ne_one_iff.mp hψ
  have hscale : b v ((t / b v w) • w) = t := by
    simp only [map_smul, smul_eq_mul]
    exact div_mul_cancel₀ t hw
  apply ht
  rw [← hscale]
  exact hv ((t / b v w) • w)

/-- Actual symplectic commutators and a nontrivial additive character force
the scalar cocycle radical to vanish. No division by two or finite-dimensionality
assumption occurs; the quotient map is the actual surjective map in the datum. -/
theorem radical_eq_bot
    (D : Datum (Multiplicative K) H (Multiplicative V))
    (b : LinearMap.BilinForm K V) (hb : b.SeparatingLeft)
    (hcomm : ∀ h k : H, centralCommutator D h k =
      Multiplicative.ofAdd (b (D.q h).toAdd (D.q k).toAdd))
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1)
    (ζ : Multiplicative K →* ℂˣ)
    (hζ : ∀ t : K, (ζ (Multiplicative.ofAdd t) : ℂ) = ψ t) :
    radical (scalarCocycle D ζ) = ⊥ := by
  apply (radical_scalarCocycle_eq_bot_iff D ζ).2
  intro h hh
  have hv : (D.q h).toAdd = 0 := by
    apply character_separating_left b hb ψ hψ
    intro w
    obtain ⟨k, hk⟩ := D.q_surjective (Multiplicative.ofAdd w)
    have hscalar := congrArg (fun z : ℂˣ => (z : ℂ)) (hh k)
    rw [hcomm, hζ, hk] at hscalar
    exact hscalar
  exact congrArg Multiplicative.ofAdd hv

/-- Canonical unit-valued character formulation of scalar nondegeneracy. -/
theorem radical_eq_bot_scalarCharacter
    (D : Datum (Multiplicative K) H (Multiplicative V))
    (b : LinearMap.BilinForm K V) (hb : b.SeparatingLeft)
    (hcomm : ∀ h k : H, centralCommutator D h k =
      Multiplicative.ofAdd (b (D.q h).toAdd (D.q k).toAdd))
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) :
    radical (scalarCocycle D (scalarCharacter ψ)) = ⊥ :=
  radical_eq_bot D b hb hcomm ψ hψ (scalarCharacter ψ) (scalarCharacter_ofAdd ψ)

end PaperXI.SymplecticCentralExtension
