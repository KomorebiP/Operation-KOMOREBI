import PaperX.ResidueLatticeIdeal

/-! The residue fibers count actual algebraic integers, not just coordinates. -/
set_option autoImplicit false
noncomputable section
open Ideal Module
open scoped nonZeroDivisors Real Classical Pointwise
open NumberField NumberField.mixedEmbedding NumberField.mixedEmbedding.euclidean
namespace PaperX.ResidueLattice
open PaperX.IdealClassQuantitative
variable (K : Type*) [Field K] [NumberField K]

/-- The actual Euclidean embedding of an algebraic integer. -/
def integerPoint (x : 𝓞 K) : euclidean.mixedSpace K :=
  (toMixed K).symm (mixedEmbedding K (x : K))

/-- Integral membership is faithfully represented by membership in the ideal lattice. -/
theorem integerPoint_mem_iff (J : (Ideal (𝓞 K))⁰) (x : 𝓞 K) :
    integerPoint K x ∈ idealEuclideanLattice K J ↔ x ∈ (J : Ideal (𝓞 K)) := by
  change toMixed K (integerPoint K x) ∈ idealLattice K (FractionalIdeal.mk0 K J) ↔ _
  simp only [integerPoint, ContinuousLinearEquiv.apply_symm_apply, mem_idealLattice,
    FractionalIdeal.coe_mk0]
  constructor
  · rintro ⟨y, hy, he⟩
    obtain ⟨z, hz, rfl⟩ := (FractionalIdeal.mem_coeIdeal _).mp hy
    have hez : z = x := by
      apply Subtype.ext
      exact mixedEmbedding_injective K he
    exact hez ▸ hz
  · exact fun hx => ⟨x, FractionalIdeal.mem_coeIdeal_of_mem _ hx, rfl⟩

/-- The embedding preserves the additive congruence difference. -/
theorem integerPoint_sub (x y : 𝓞 K) :
    integerPoint K (x - y) = integerPoint K x - integerPoint K y := by
  simp [integerPoint, map_sub]

/-- Faithfulness of the Euclidean embedding. -/
theorem integerPoint_injective : Function.Injective (integerPoint K) := by
  intro x y h
  apply Subtype.ext
  apply mixedEmbedding_injective K
  exact (toMixed K).symm.injective h

/-- Every point in the actual integral ideal lattice comes from a unique integer of that ideal. -/
def idealPointEquiv (J : (Ideal (𝓞 K))⁰) :
    (J : Ideal (𝓞 K)) ≃ idealEuclideanLattice K J :=
  Equiv.ofBijective (fun x => ⟨integerPoint K x.1, (integerPoint_mem_iff K J x.1).mpr x.2⟩)
    ⟨fun x y h => Subtype.ext (integerPoint_injective K (congrArg Subtype.val h)), by
      intro x
      have hx := x.2
      change toMixed K x.1 ∈ idealLattice K (FractionalIdeal.mk0 K J) at hx
      rw [mem_idealLattice, FractionalIdeal.coe_mk0] at hx
      obtain ⟨y, hy, he⟩ := hx
      obtain ⟨z, hz, rfl⟩ := (FractionalIdeal.mem_coeIdeal _).mp hy
      refine ⟨⟨z, hz⟩, ?_⟩
      apply Subtype.ext
      change (toMixed K).symm (mixedEmbedding K (z : K)) = x.1
      rw [he, ContinuousLinearEquiv.symm_apply_apply]⟩

/-- A residue equality in the lattice is exactly congruence of algebraic integers modulo the ideal. -/
theorem idealPoint_residue_eq_iff (M J : (Ideal (𝓞 K))⁰) (x a : (J : Ideal (𝓞 K))) :
    (Submodule.Quotient.mk (idealPointEquiv K J x) : IdealResidues K M J) =
      Submodule.Quotient.mk (idealPointEquiv K J a) ↔
        (x.1 - a.1) ∈ (M : Ideal (𝓞 K)) := by
  rw [residue_eq_iff]
  change integerPoint K x.1 - integerPoint K a.1 ∈ idealEuclideanLattice K M ↔ _
  rw [← integerPoint_sub, integerPoint_mem_iff]

/-- The fiber count is exactly the count of algebraic integers in a prescribed ideal congruence. -/
theorem idealFiberCount_eq_integer_count (M J : (Ideal (𝓞 K))⁰)
    (a : (J : Ideal (𝓞 K))) (t : ℝ) :
    idealFiberCount K M J (Submodule.Quotient.mk (idealPointEquiv K J a)) t =
      Nat.card {x : (J : Ideal (𝓞 K)) // x.1 - a.1 ∈ (M : Ideal (𝓞 K)) ∧
        integerPoint K x.1 ∈ t • coneRegion K 1} := by
  unfold idealFiberCount fiberCount
  exact Nat.card_congr ((idealPointEquiv K J).subtypeEquiv (fun x => by
    simp only [idealPoint_residue_eq_iff]
    rfl)).symm

end PaperX.ResidueLattice
