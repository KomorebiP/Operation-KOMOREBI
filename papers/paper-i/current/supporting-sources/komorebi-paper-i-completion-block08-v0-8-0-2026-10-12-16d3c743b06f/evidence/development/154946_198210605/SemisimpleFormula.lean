import PaperICompletion8.RegularMultiplicity
import PaperICompletion7.ModuleTop
import Mathlib.RingTheory.SimpleModule.WedderburnArtin
import Mathlib.RingTheory.Artinian.Module

/-! The manuscript's semisimple formula, with genuine nonsplit ring and
module decompositions. Abstract ring and simple-module decomposition
existence is explicitly integrated from the proved upstream theorems.
The radical-top formula uses the existing canonical quotient and rank. -/
set_option autoImplicit false
set_option linter.unusedSectionVars false

namespace Komorebi.PaperICompletion8.SemisimpleFormula

open scoped DirectSum
open Komorebi.SeedRankBasics Komorebi.SeedRankOperations
open Komorebi.PaperICompletion8.DivisionProduct
open Komorebi.PaperICompletion8.RegularMultiplicity
open Komorebi.PaperICompletion7.ModuleTop

universe u v
attribute [local instance] RingHomInvPair.of_ringEquiv

section AbstractExistence
variable (R M : Type u) [Ring R] [AddCommGroup M] [Module R M]

/-- Actual Wedderburn-Artin existence over arbitrary division rings. -/
theorem exists_wedderburn_decomposition [IsSemisimpleRing R] :
    ∃ (q : ℕ) (D : Fin q → Type u) (d : Fin q → ℕ) (_ : ∀ i, DivisionRing (D i)),
      (∀ i, NeZero (d i)) ∧
      Nonempty (R ≃+* ∀ i, Matrix (Fin (d i)) (Fin (d i)) (D i)) :=
  IsSemisimpleRing.exists_ringEquiv_pi_matrix_divisionRing R

/-- Every finitely generated module over a semisimple ring really decomposes into simple modules. -/
theorem exists_finite_simple_decomposition [IsSemisimpleRing R] [Module.Finite R M] :
    ∃ (n : ℕ) (S : Fin n → Submodule R M),
      Nonempty (M ≃ₗ[R] ⨁ i : Fin n, S i) ∧ ∀ i, IsSimpleModule R (S i) := by
  obtain ⟨n, S, e, hS⟩ := IsSemisimpleModule.exists_linearEquiv_fin_dfinsupp R M
  exact ⟨n, S, ⟨e⟩, hS⟩

/-- A finite-dimensional algebra has an actually semisimple radical quotient. -/
theorem finiteAlgebra_radicalQuotient_isSemisimple
    (k : Type u) [Field k] [Algebra k R] [Module.Finite k R] :
    IsSemisimpleRing (R ⧸ Ring.jacobson R) := by
  let : IsArtinianRing R := isArtinian_of_tower k inferInstance
  infer_instance

/-- The decomposition of a finite algebra's radical quotient is constructed, not assumed. -/
theorem finiteAlgebra_radicalQuotient_decomposition
    (k : Type u) [Field k] [Algebra k R] [Module.Finite k R] :
    ∃ (q : ℕ) (D : Fin q → Type u) (d : Fin q → ℕ) (_ : ∀ i, DivisionRing (D i)),
      (∀ i, NeZero (d i)) ∧
      Nonempty ((R ⧸ Ring.jacobson R) ≃+* ∀ i, Matrix (Fin (d i)) (Fin (d i)) (D i)) := by
  let := finiteAlgebra_radicalQuotient_isSemisimple R k
  exact exists_wedderburn_decomposition (R ⧸ Ring.jacobson R)

end AbstractExistence

section Formula
variable {I : Type v} [Fintype I] [DecidableEq I]
variable {D : I → Type u} [∀ i, DivisionRing (D i)]
variable (d m : I → ℕ)
variable {R M : Type (max u v)} [Ring R] [AddCommGroup M] [Module R M]

/-- The printed nonsplit formula for the actual displayed ring and module equivalences. -/
theorem semisimple_seedRank_of_decompositions
    (eR : R ≃+* DivisionProductAlgebra (D := D) d)
    (eM : M ≃ₛₗ[(RingHomClass.toRingHom eR)] (⨁ i : I, (Fin (m i) → Simple (D := D) d i)))
    (hd : ∀ i, 0 < d i) : seedRank R M = (maxCeilDiv d m : Cardinal) := by
  let : RingHomSurjective (RingHomClass.toRingHom eR) := ⟨eR.surjective⟩
  exact (seedRank_eq_of_bijective_semilinear eM.toLinearMap eM.bijective).trans
    (directSum_seedRank d m hd)

/-- The same result in natural-valued canonical rank. -/
theorem semisimple_seedFinrank_of_decompositions
    (eR : R ≃+* DivisionProductAlgebra (D := D) d)
    (eM : M ≃ₛₗ[(RingHomClass.toRingHom eR)] (⨁ i : I, (Fin (m i) → Simple (D := D) d i)))
    (hd : ∀ i, 0 < d i) : seedFinrank R M = maxCeilDiv d m := by
  simpa only [Cardinal.toNat_natCast, seedFinrank, seedRank, Submodule.spanFinrank] using
    congrArg Cardinal.toNat (semisimple_seedRank_of_decompositions d m eR eM hd)

/-- Generator rank is computed by the nonsplit decomposition of the ACTUAL module top. -/
theorem radicalTop_seedRank_of_decompositions [Module.Finite R M]
    (eR : (R ⧸ Ring.jacobson R) ≃+* DivisionProductAlgebra (D := D) d)
    (eM : RadicalTop R M ≃ₛₗ[(RingHomClass.toRingHom eR)]
      (⨁ i : I, (Fin (m i) → Simple (D := D) d i)))
    (hd : ∀ i, 0 < d i) : seedRank R M = (maxCeilDiv d m : Cardinal) := by
  rw [seedRank_eq_radicalTop]
  exact semisimple_seedRank_of_decompositions d m eR eM hd

/-- Natural-valued radical-top multiplicity formula. -/
theorem radicalTop_seedFinrank_of_decompositions [Module.Finite R M]
    (eR : (R ⧸ Ring.jacobson R) ≃+* DivisionProductAlgebra (D := D) d)
    (eM : RadicalTop R M ≃ₛₗ[(RingHomClass.toRingHom eR)]
      (⨁ i : I, (Fin (m i) → Simple (D := D) d i)))
    (hd : ∀ i, 0 < d i) : seedFinrank R M = maxCeilDiv d m := by
  simpa only [Cardinal.toNat_natCast, seedFinrank, seedRank, Submodule.spanFinrank] using
    congrArg Cardinal.toNat (radicalTop_seedRank_of_decompositions d m eR eM hd)

end Formula

section SplitSpecialization
variable {I : Type v} [Fintype I] [DecidableEq I]
variable (k : Type u) [Field k] (d m : I → ℕ)
variable {R M : Type (max u v)} [Ring R] [AddCommGroup M] [Module R M] [Module.Finite R M]

/-- The split top formula needs no algebraic closure once the split decomposition is supplied. -/
theorem split_radicalTop_seedRank
    (eR : (R ⧸ Ring.jacobson R) ≃+* DivisionProductAlgebra (D := fun _ : I ↦ k) d)
    (eM : RadicalTop R M ≃ₛₗ[(RingHomClass.toRingHom eR)]
      (⨁ i : I, (Fin (m i) → Simple (D := fun _ : I ↦ k) d i)))
    (hd : ∀ i, 0 < d i) : seedRank R M = (maxCeilDiv d m : Cardinal) :=
  radicalTop_seedRank_of_decompositions d m eR eM hd

/-- The literal module top has the same generator rank even when its action
is viewed over the original ring. Scalar restriction changes no generating set. -/
theorem seedRank_eq_radicalTop_restricted :
    seedRank R M = seedRank R (RadicalTop R M) := by
  let f : RadicalTop R M →ₛₗ[Ideal.Quotient.mk (Ring.jacobson R)] RadicalTop R M :=
    { toFun := id
      map_add' := fun _ _ ↦ rfl
      map_smul' := fun _ _ ↦ rfl }
  have h := seedRank_eq_of_bijective_semilinear f Function.bijective_id
  exact seedRank_eq_radicalTop.trans h.symm

/-- Exact printed split corollary with a decomposition of the original ring
and the original-ring action on its literal module top. Algebraic closure is
unnecessary once the displayed split decomposition is given. -/
theorem split_originalRing_top_seedRank
    (eR : R ≃+* DivisionProductAlgebra (D := fun _ : I ↦ k) d)
    (eM : RadicalTop R M ≃ₛₗ[(RingHomClass.toRingHom eR)]
      (⨁ i : I, (Fin (m i) → Simple (D := fun _ : I ↦ k) d i)))
    (hd : ∀ i, 0 < d i) : seedRank R M = (maxCeilDiv d m : Cardinal) := by
  rw [seedRank_eq_radicalTop_restricted]
  exact semisimple_seedRank_of_decompositions d m eR eM hd

end SplitSpecialization
end Komorebi.PaperICompletion8.SemisimpleFormula
