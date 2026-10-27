import Mathlib.RingTheory.LocalRing.Etale
import Mathlib.RingTheory.LocalRing.Quotient
import Mathlib.RingTheory.Smooth.Fiber
import Mathlib.RingTheory.RamificationInertia.Ramification
import Mathlib.RingTheory.Unramified.LocalRing

/-! An equal-rank residue fiber criterion for actual finite etale local algebras. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LocalResidueRank
open IsLocalRing
variable (R S : Type*) [CommRing R] [CommRing S] [Algebra R S]
variable [IsLocalRing R] [IsLocalRing S] [IsLocalHom (algebraMap R S)]
variable [Module.Finite R S] [Module.Free R S]

set_option backward.inferInstanceAs.wrap.data false in
/-- When the finite free rank is already exhausted by the residue degree,
no nilpotent thickness remains in the special fiber. -/
theorem map_maximal_of_rank
    (h : Module.finrank R S = Module.finrank (ResidueField R) (ResidueField S)) :
    (maximalIdeal R).map (algebraMap R S) = maximalIdeal S := by
  let J := (maximalIdeal R).map (algebraMap R S)
  have hJ : J ≤ maximalIdeal S :=
    ((local_hom_TFAE (algebraMap R S)).out 1 3 rfl rfl).mp inferInstance
  let : Algebra (ResidueField R) (S ⧸ J) :=
    (inferInstanceAs <| Algebra (R ⧸ maximalIdeal R) _)
  let : IsScalarTower R (ResidueField R) (S ⧸ J) :=
    (inferInstanceAs <| IsScalarTower R (R ⧸ maximalIdeal R) _)
  let f : S ⧸ J →ₐ[ResidueField R] ResidueField S :=
    { Ideal.Quotient.factor hJ with
      commutes' := fun r => by
        obtain ⟨r, rfl⟩ := residue_surjective r
        rfl }
  have hf : Function.Surjective f := Ideal.Quotient.factor_surjective hJ
  have : Module.Finite (ResidueField R) (S ⧸ J) :=
    Module.Finite.of_restrictScalars_finite R _ _
  have heq : Module.finrank (ResidueField R) (S ⧸ J) =
      Module.finrank (ResidueField R) (ResidueField S) := by
    exact (IsLocalRing.finrank_quotient_map (R := R) (S := S)).trans h
  have hi : Function.Injective f :=
    (LinearMap.injective_iff_surjective_of_finrank_eq_finrank
      (f := f.toLinearMap) heq).mpr hf
  apply le_antisymm hJ
  intro x hx
  have hzero : f (Ideal.Quotient.mk J x) = f 0 := by
    change residue S x = 0
    simpa only [residue_eq_zero_iff] using hx
  exact Ideal.Quotient.eq_zero_iff_mem.mp (hi hzero)

/-- This is Mathlib's formal-unramified predicate, not a substitute definition. -/
theorem formallyUnramified [Algebra.IsSeparable (ResidueField R) (ResidueField S)]
    (h : Module.finrank R S = Module.finrank (ResidueField R) (ResidueField S)) :
    Algebra.FormallyUnramified R S := by
  exact Algebra.FormallyUnramified.of_map_maximalIdeal (map_maximal_of_rank R S h)

/-- Finite presentation and flatness yield the actual etale predicate. -/
theorem etale [Algebra.FinitePresentation R S]
    [Algebra.IsSeparable (ResidueField R) (ResidueField S)]
    (h : Module.finrank R S = Module.finrank (ResidueField R) (ResidueField S)) :
    Algebra.Etale R S := by
  let := formallyUnramified R S h
  exact Algebra.Etale.of_formallyUnramified_of_flat

/-- The criterion is an equivalence for finite free local algebras with
separable residue extension. -/
theorem etale_iff_rank_residue [Algebra.FinitePresentation R S]
    [Algebra.IsSeparable (ResidueField R) (ResidueField S)] :
    Algebra.Etale R S ↔
      Module.finrank R S = Module.finrank (ResidueField R) (ResidueField S) := by
  constructor
  · intro h
    let := h
    exact IsLocalRing.finrank_eq_finrank_residueField
  · exact etale R S

/-- In particular the library's ramification index is one. -/
theorem ramificationIdx_one [Algebra.IsSeparable (ResidueField R) (ResidueField S)]
    (h : Module.finrank R S = Module.finrank (ResidueField R) (ResidueField S)) :
    (maximalIdeal S).ramificationIdx R = 1 := by
  let := formallyUnramified R S h
  exact Ideal.ramificationIdx_eq_one _ _

end PaperXI.LocalResidueRank
