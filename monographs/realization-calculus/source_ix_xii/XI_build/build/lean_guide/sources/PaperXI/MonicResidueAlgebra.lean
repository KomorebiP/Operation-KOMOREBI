import Mathlib.RingTheory.AdjoinRoot
import Mathlib.Algebra.Polynomial.Eval.Irreducible
import Mathlib.RingTheory.LocalRing.Quotient
import Mathlib.RingTheory.Ideal.GoingUp
import Mathlib.Tactic

/-! Monic lifts with irreducible residue polynomial give finite free local
algebras with their literal special fiber. No ambient field is supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonicResidueAlgebra
open Polynomial IsLocalRing
variable {R : Type*} [CommRing R] [IsLocalRing R]
variable (f : R[X]) [hm : Fact f.Monic]
variable [hi : Fact (Irreducible (f.map (residue R)))]

abbrev specialIdeal : Ideal (AdjoinRoot f) :=
  (maximalIdeal R).map (algebraMap R (AdjoinRoot f))

instance finite : Module.Finite R (AdjoinRoot f) := hm.out.finite_adjoinRoot
instance free : Module.Free R (AdjoinRoot f) := hm.out.free_adjoinRoot

/-- The base special fiber is the actual residue polynomial algebra. -/
def specialFiberEquiv :
    (AdjoinRoot f ⧸ specialIdeal f) ≃ₐ[R] AdjoinRoot (f.map (residue R)) :=
  AdjoinRoot.quotEquivQuotMap f (maximalIdeal R)

omit hm in
theorem specialIdeal_maximal : (specialIdeal f).IsMaximal := by
  apply Ideal.Quotient.maximal_of_isField
  exact (specialFiberEquiv f).toRingEquiv.toMulEquiv.isField (Field.toIsField _)

/-- All maximal ideals lie above the base maximal ideal; the special fiber is a field. -/
instance localRing : IsLocalRing (AdjoinRoot f) := by
  let := AdjoinRoot.isIntegral_of_monic hm.out
  apply IsLocalRing.of_unique_max_ideal
  refine ⟨specialIdeal f, specialIdeal_maximal f, ?_⟩
  intro M hM
  let : M.IsMaximal := hM
  have hcomap : M.comap (algebraMap R (AdjoinRoot f)) = maximalIdeal R :=
    IsLocalRing.eq_maximalIdeal (Ideal.isMaximal_comap_of_isIntegral_of_isMaximal M)
  have hle : specialIdeal f ≤ M := by
    rw [specialIdeal, Ideal.map_le_iff_le_comap, hcomap]
  exact ((specialIdeal_maximal f).eq_of_le hM.ne_top hle).symm

theorem maximalIdeal_eq : maximalIdeal (AdjoinRoot f) = specialIdeal f :=
  (IsLocalRing.eq_maximalIdeal (specialIdeal_maximal f)).symm

def residueEquiv : ResidueField (AdjoinRoot f) ≃+* AdjoinRoot (f.map (residue R)) :=
  (Ideal.quotEquivOfEq (maximalIdeal_eq f)).trans (specialFiberEquiv f).toRingEquiv

omit hi in
theorem rank : Module.finrank R (AdjoinRoot f) = f.natDegree := by
  simpa using Module.finrank_eq_card_basis (AdjoinRoot.powerBasis' hm.out).basis

theorem degree_pos : 0 < f.degree := by
  rw [← hm.out.degree_map (residue R)]
  exact Polynomial.degree_pos_of_irreducible hi.out

instance localHom : IsLocalHom (algebraMap R (AdjoinRoot f)) :=
  AdjoinRoot.isLocalHom_of_monic_of_degree_pos hm.out (degree_pos f)

theorem residueEquiv_mk (p : R[X]) :
    residueEquiv f (residue (AdjoinRoot f) (AdjoinRoot.mk f p)) =
      AdjoinRoot.mk (f.map (residue R)) (p.map (residue R)) := by
  change (specialFiberEquiv f).toRingEquiv
    ((Ideal.quotEquivOfEq (maximalIdeal_eq f))
      (Ideal.Quotient.mk _ (AdjoinRoot.mk f p))) = _
  rw [Ideal.quotEquivOfEq_mk]
  exact AdjoinRoot.quotEquivQuotMap_apply_mk f p (maximalIdeal R)

def residueAlgebraEquiv :
    ResidueField (AdjoinRoot f) ≃ₐ[ResidueField R] AdjoinRoot (f.map (residue R)) :=
  { residueEquiv f with
    commutes' := fun a => by
      obtain ⟨r, rfl⟩ := residue_surjective a
      change residueEquiv f (residue (AdjoinRoot f) (AdjoinRoot.mk f (C r))) = _
      rw [residueEquiv_mk, Polynomial.map_C]
      rfl }

theorem residue_rank :
    Module.finrank (ResidueField R) (ResidueField (AdjoinRoot f)) = f.natDegree := by
  rw [(residueAlgebraEquiv f).toLinearEquiv.finrank_eq]
  simpa [hm.out.natDegree_map] using
    Module.finrank_eq_card_basis (AdjoinRoot.powerBasis' (hm.out.map (residue R))).basis

end PaperXI.MonicResidueAlgebra
