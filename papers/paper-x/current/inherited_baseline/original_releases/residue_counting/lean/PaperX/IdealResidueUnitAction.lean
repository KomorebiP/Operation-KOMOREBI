import PaperX.NormResidueLatticeMap

/-! Multiplication by a residue-ring unit permutes the actual ideal residue set.
No surjectivity from ideal residues to the ambient residue ring is used. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.IdealResidueUnitAction
open Ideal NumberField
open PaperX.IdealClassQuantitative PaperX.ResidueLattice PaperX.NormResidue
open PaperX.NormResidueLattice
open scoped nonZeroDivisors

variable (K : Type*) [Field K] [NumberField K]

/-- Every ideal-lattice residue has a representative in the actual integral ideal. -/
theorem residue_mk_surjective (M J : (Ideal (𝓞 K))⁰) :
    Function.Surjective (fun x : (J : Ideal (𝓞 K)) =>
      (Submodule.Quotient.mk (idealPointEquiv K J x) : IdealResidues K M J)) := by
  intro c
  induction c using Quotient.inductionOn with
  | h x =>
    refine ⟨(idealPointEquiv K J).symm x, ?_⟩
    simp only [Equiv.apply_symm_apply]
    rfl

/-- Multiplication by an algebraic integer descends to the actual ideal residues. -/
def mulResidue (M J : (Ideal (𝓞 K))⁰) (a : 𝓞 K) :
    IdealResidues K M J → IdealResidues K M J :=
  Quotient.lift (fun x : idealEuclideanLattice K J =>
    Submodule.Quotient.mk (idealPointEquiv K J
      ⟨a * integerRepresentative K J x,
        (J : Ideal (𝓞 K)).mul_mem_left a ((idealPointEquiv K J).symm x).property⟩)) (by
    intro x y hxy
    apply (idealPoint_residue_eq_iff K M J _ _).mpr
    have hrep : integerRepresentative K J x - integerRepresentative K J y ∈
        (M : Ideal (𝓞 K)) := by
      rw [← integerPoint_mem_iff K M, integerPoint_sub,
        integerRepresentative_point, integerRepresentative_point]
      exact (Submodule.Quotient.eq
        ((idealEuclideanLattice K M).comap (idealEuclideanLattice K J).subtype)).mp
          (Quotient.sound hxy)
    change a * integerRepresentative K J x - a * integerRepresentative K J y ∈ _
    rw [← mul_sub]
    exact (M : Ideal (𝓞 K)).mul_mem_left a hrep)

theorem mulResidue_mk (M J : (Ideal (𝓞 K))⁰) (a : 𝓞 K)
    (x : (J : Ideal (𝓞 K))) :
    mulResidue K M J a (Submodule.Quotient.mk (idealPointEquiv K J x)) =
      Submodule.Quotient.mk (idealPointEquiv K J
        ⟨a * x.1, (J : Ideal (𝓞 K)).mul_mem_left a x.2⟩) := by
  change Submodule.Quotient.mk (idealPointEquiv K J
    ⟨a * integerRepresentative K J (idealPointEquiv K J x), _⟩) = _
  simp only [integerRepresentative_equiv]

/-- An inverse modulo m acts as a genuine inverse on ideal residues when mJ≤M. -/
theorem mulResidue_inverse (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hprod : modulusIdeal (𝓞 K) m * (J : Ideal (𝓞 K)) ≤ M)
    (a b : 𝓞 K) (hab : a * b - 1 ∈ modulusIdeal (𝓞 K) m)
    (c : IdealResidues K M J) :
    mulResidue K M J a (mulResidue K M J b c) = c := by
  obtain ⟨x, rfl⟩ := residue_mk_surjective K M J c
  rw [mulResidue_mk, mulResidue_mk]
  apply (idealPoint_residue_eq_iff K M J _ _).mpr
  change a * (b * x.1) - x.1 ∈ (M : Ideal (𝓞 K))
  have h := hprod (Ideal.mul_mem_mul hab x.2)
  convert h using 1
  ring

/-- The actual permutation induced by a unit of the ring-of-integers residue ring. -/
def unitPerm (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hprod : modulusIdeal (𝓞 K) m * (J : Ideal (𝓞 K)) ≤ M)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ) :
    Equiv.Perm (IdealResidues K M J) where
  toFun := mulResidue K M J (Quotient.out (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m))
  invFun := mulResidue K M J (Quotient.out ((u⁻¹ :
    (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ) : 𝓞 K ⧸ modulusIdeal (𝓞 K) m))
  left_inv := by
    apply mulResidue_inverse K M J m hprod
    apply Ideal.Quotient.eq.mp
    simp [map_mul, Ideal.Quotient.mk_out]
  right_inv := by
    apply mulResidue_inverse K M J m hprod
    apply Ideal.Quotient.eq.mp
    simp [map_mul, Ideal.Quotient.mk_out]

/-- Multiplication has the expected effect on the actual residue norm. -/
theorem residueNorm_mulResidue (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m) (a : 𝓞 K)
    (c : IdealResidues K M J) :
    residueNorm K M J m hM (mulResidue K M J a c) =
      (Algebra.norm ℤ a : ZMod m) * residueNorm K M J m hM c := by
  obtain ⟨x, rfl⟩ := residue_mk_surjective K M J c
  rw [mulResidue_mk, residueNorm_mk, residueNorm_mk, map_mul, Int.cast_mul]

/-- The permutation scales the norm by the actual norm of the residue-ring unit. -/
theorem residueNorm_unitPerm (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hprod : modulusIdeal (𝓞 K) m * (J : Ideal (𝓞 K)) ≤ M)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ) (c : IdealResidues K M J) :
    residueNorm K M J m hM (unitPerm K M J m hprod u c) =
      integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m) *
        residueNorm K M J m hM c := by
  change residueNorm K M J m hM (mulResidue K M J _ c) = _
  rw [residueNorm_mulResidue, ← integerQuotientNorm_mk, Ideal.Quotient.mk_out]

end PaperX.IdealResidueUnitAction
