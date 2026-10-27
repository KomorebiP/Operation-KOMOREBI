import KomorebiVerification.PaperII.NestedRefinement

/-! Exact manuscript endpoints for block support and coordinate conjugacy. -/
set_option autoImplicit false
namespace Komorebi.PaperII.NestedRefinement
open Komorebi.Foundation Komorebi.Foundation.LinearProjectorFamily
universe u v w x y z
variable {R : Type u} [Semiring R]
variable {M : Type v} {N : Type w}
variable [AddCommMonoid M] [Module R M] [AddCommMonoid N] [Module R N]
variable {ι : Type x} {κ : Type y} {ι' : Type z} {κ' : Type*}
variable [Fintype ι] [Fintype κ] [Fintype ι'] [Fintype κ']

/-- Fine blocks are obtained by projecting the corresponding coarse block on both sides. -/
theorem transferBlock_descendant
    {P : LinearProjectorFamily R M ι} {Q : LinearProjectorFamily R M κ}
    {S : LinearProjectorFamily R N ι'} {V : LinearProjectorFamily R N κ'}
    {p : κ → ι} {q : κ' → ι'} (hp : Refines P Q p) (hq : Refines S V q)
    (T : M →ₗ[R] N) (β : κ') (α : κ) :
    (V.proj β).comp ((transferBlock P S T (q β) (p α)).comp (Q.proj α)) =
      transferBlock Q V T β α := by
  ext x
  simp only [transferBlock, LinearMap.comp_apply]
  rw [hp.coarse_fine_apply_eq_self, hq.fine_coarse_apply_eq_self]

/-- A coarse block vanishes exactly when every descendant fine block vanishes. -/
theorem transferBlock_eq_zero_iff_descendants
    {P : LinearProjectorFamily R M ι} {Q : LinearProjectorFamily R M κ}
    {S : LinearProjectorFamily R N ι'} {V : LinearProjectorFamily R N κ'}
    {p : κ → ι} {q : κ' → ι'} (hp : Refines P Q p) (hq : Refines S V q)
    (T : M →ₗ[R] N) (b : ι') (a : ι) :
    transferBlock P S T b a = 0 ↔
      ∀ β ∈ children q b, ∀ α ∈ children p a, transferBlock Q V T β α = 0 := by
  classical
  constructor
  · intro hz β hβ α hα
    have hb := (mem_children q b β).mp hβ
    have ha := (mem_children p a α).mp hα
    have h := transferBlock_descendant hp hq T β α
    rw [hb, ha, hz, LinearMap.zero_comp, LinearMap.comp_zero] at h
    exact h.symm
  · intro h
    rw [transferBlock_refinement_between hp hq]
    apply Finset.sum_eq_zero
    intro β hβ
    apply Finset.sum_eq_zero
    intro α hα
    exact h β hβ α hα

/-- Exact operator coordinates transform by synthesis/analysis conjugacy. -/
theorem coordinateOperator_conjugation
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (S : LinearProjectorFamily R N ι') (V : LinearProjectorFamily R N κ')
    (T : M →ₗ[R] N) :
    (coarsenCoordinates S V).comp
        ((coordinateOperator Q V T).comp (refineCoordinates P Q)) =
      coordinateOperator P S T := by
  ext packets
  simp [coordinateOperator, coarsenCoordinates, refineCoordinates]

end Komorebi.PaperII.NestedRefinement

#print axioms Komorebi.PaperII.NestedRefinement.transferBlock_eq_zero_iff_descendants
#print axioms Komorebi.PaperII.NestedRefinement.coordinateOperator_conjugation
