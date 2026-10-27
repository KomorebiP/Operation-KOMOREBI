import PaperXI.LiftedFullResidue
import PaperXI.FiniteResidueBaseChange

/-! Frobenius lifting and the exact degree quotient with the actual base residue.
The degree-one lift is derived from finite Galois residue surjectivity. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LiftedResidueFrobenius
open IsLocalRing PaperXI.LiftedResidueDegree PaperXI.FiniteResidueBaseChange
open PaperXI.ResidueWeil PaperXI.ResidueDegreeBaseChange
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [Fintype (ResidueField A)]

instance baseFinite : Finite (BaseResidue K A) :=
  Finite.of_injective (ValuationResidueEmbedding.residueMap A (algebraMap K L))
    (ValuationResidueEmbedding.residueMap_injective A (algebraMap K L))
local instance baseFintype : Fintype (BaseResidue K A) := Fintype.ofFinite _

/-- The actual inverse q-power residue automorphism, q=the full base residue size. -/
def frobenius : RingAut (ResidueField A) := geometric (BaseResidue K A) (ResidueField A)

@[simp] theorem frobenius_inverse_power (x : ResidueField A) :
    frobenius K A x ^ Fintype.card (BaseResidue K A) = x :=
  geometric_inverse_power (BaseResidue K A) (ResidueField A) x

variable [FiniteDimensional K L] [IsGalois K L] [HenselianLocalRing A]
variable (stable : ∀ g : L ≃ₐ[K] L, g ∈ A.decompositionSubgroup K)

/-- A lift of geometric residue Frobenius is a theorem, not an extra input. -/
theorem frobenius_in_range :
    frobenius K A ∈ (HenselianGaloisResidue.residueAction K A stable).range := by
  obtain ⟨g, hg⟩ := residueAut_surjective K A stable
    (FiniteField.frobeniusAlgEquivOfAlgebraic (BaseResidue K A) (ResidueField A)).symm
  exact ⟨g, RingEquiv.ext (fun x => AlgEquiv.congr_fun hg x)⟩

include stable in
/-- The same existence statement in the literal valuation decomposition subgroup. -/
theorem decomposition_frobenius_lift :
    frobenius K A ∈
      (MulSemiringAction.toRingAut (A.decompositionSubgroup K) (ResidueField A)).range := by
  obtain ⟨g, hg⟩ := frobenius_in_range K A stable
  exact ⟨HenselianGaloisResidue.decompositionMap K A stable g, hg⟩

/-- No finite-order reduction of the integer degree. -/
theorem full_degree : Function.Surjective
    (degree (HenselianGaloisResidue.residueAction K A stable) (frobenius K A)) :=
  degree_surjective _ _ (frobenius_in_range K A stable)

/-- The quotient is the actual cyclic quotient of the integer-degree pullback. -/
def cyclicQuotient (n : ℕ) :
    Pullback (HenselianGaloisResidue.residueAction K A stable) (frobenius K A) ⧸
      periodSubgroup (HenselianGaloisResidue.residueAction K A stable) (frobenius K A) n
      ≃* Multiplicative (ZMod n) :=
  quotientEquiv _ _ n (frobenius_in_range K A stable)

variable (s : IntermediateField (BaseResidue K A) (ResidueField A))

/-- Its order equals the derived lifted-field degree, with no assumed index equality. -/
theorem quotient_order :
    Nat.card (Pullback (HenselianGaloisResidue.residueAction K A stable) (frobenius K A) ⧸
      periodSubgroup (HenselianGaloisResidue.residueAction K A stable) (frobenius K A)
        (Module.finrank (BaseResidue K A) s)) = Module.finrank K (field K A s) := by
  have hn : NeZero (Module.finrank (BaseResidue K A) s) := ⟨Module.finrank_pos.ne'⟩
  rw [quotient_card _ _ _ (frobenius_in_range K A stable)]
  exact (LiftedResidueDegree.degree K A stable s).symm

end PaperXI.LiftedResidueFrobenius
