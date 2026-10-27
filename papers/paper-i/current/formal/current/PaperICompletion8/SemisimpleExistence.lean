import PaperICompletion8.ProductPresentation

/-! Certificate-free public existence and seed formulas. The ring and
compatible module presentations are constructed inside each theorem.
Classical choice selects proved decompositions, not assumed conclusions. -/
set_option autoImplicit false

namespace Komorebi.PaperICompletion8.SemisimpleExistence

open scoped DirectSum
open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion8.DivisionProduct
open Komorebi.PaperICompletion8.RegularMultiplicity
open Komorebi.PaperICompletion8.SemisimpleFormula
open Komorebi.PaperICompletion8.ProductPresentation
open Komorebi.PaperICompletion7.ModuleTop

universe u v
attribute [local instance] RingHomInvPair.of_ringEquiv

section Transport
variable {I : Type v} [Fintype I] [DecidableEq I]
variable {D : I → Type u} [∀ i, DivisionRing (D i)]
variable (d : I → ℕ)
variable {R M : Type (max u v)} [Ring R] [AddCommGroup M] [Module R M] [Module.Finite R M]

/-- Any actual Wedderburn ring isomorphism admits a compatible natural-factor module decomposition. -/
theorem exists_compatible_presentation
    (eR : R ≃+* DivisionProductAlgebra (D := D) d) (hd : ∀ i, 0 < d i) :
    ∃ m : I → ℕ, Nonempty (M ≃ₛₗ[(RingHomClass.toRingHom eR)]
      (⨁ i : I, (Fin (m i) → Simple (D := D) d i))) := by
  classical
  let A := DivisionProductAlgebra (D := D) d
  let : Module A M := Module.compHom M eR.symm.toRingHom
  let e : M ≃ₛₗ[(RingHomClass.toRingHom eR)] M :=
    { __ := AddEquiv.refl M
      map_smul' a x := by
        change a • x = eR.symm (eR a) • x
        rw [eR.symm_apply_apply] }
  let : RingHomSurjective (RingHomClass.toRingHom eR) := ⟨eR.surjective⟩
  let : Module.Finite A M := Module.Finite.of_surjective e.toLinearMap e.surjective
  obtain ⟨m, ⟨em⟩⟩ := exists_multiplicity_presentation (D := D) d M hd
  exact ⟨m, ⟨(e.trans em).trans (multiplicityDirectSumEquiv (D := D) d m)⟩⟩

end Transport

section Existence
variable (R M : Type u) [Ring R] [AddCommGroup M] [Module R M] [Module.Finite R M]

/-- Full semisimple seed formula with the ring and compatible module decompositions built internally. -/
theorem exists_semisimple_seed_formula [IsSemisimpleRing R] :
    ∃ (q : ℕ) (D : Fin q → Type u) (d m : Fin q → ℕ) (_ : ∀ i, DivisionRing (D i)),
      (∀ i, 0 < d i) ∧
      ∃ eR : R ≃+* DivisionProductAlgebra (D := D) d,
        Nonempty (M ≃ₛₗ[(RingHomClass.toRingHom eR)]
          (⨁ i : Fin q, (Fin (m i) → Simple (D := D) d i))) ∧
        seedRank R M = (maxCeilDiv d m : Cardinal) := by
  classical
  obtain ⟨q, D, d, hD, hd, ⟨eR⟩⟩ := exists_wedderburn_decomposition R
  let := hD
  have hpos : ∀ i, 0 < d i := fun i ↦ Nat.pos_of_ne_zero (hd i).out
  obtain ⟨m, ⟨eM⟩⟩ := exists_compatible_presentation (M := M) (D := D) d eR hpos
  exact ⟨q, D, d, m, hD, hpos, eR, ⟨eM⟩,
    semisimple_seedRank_of_decompositions d m eR eM hpos⟩

/-- The same construction for an Artinian ring uses its literal radical quotient and module top. -/
theorem exists_artinian_radicalTop_seed_formula [IsArtinianRing R] :
    ∃ (q : ℕ) (D : Fin q → Type u) (d m : Fin q → ℕ) (_ : ∀ i, DivisionRing (D i)),
      (∀ i, 0 < d i) ∧
      ∃ eR : (R ⧸ Ring.jacobson R) ≃+* DivisionProductAlgebra (D := D) d,
        Nonempty (RadicalTop R M ≃ₛₗ[(RingHomClass.toRingHom eR)]
          (⨁ i : Fin q, (Fin (m i) → Simple (D := D) d i))) ∧
        seedRank R M = (maxCeilDiv d m : Cardinal) := by
  let : Module.Finite (R ⧸ Ring.jacobson R) (RadicalTop R M) :=
    idealTop_finite (Ring.jacobson R) le_rfl
  obtain ⟨q, D, d, m, hD, hd, eR, heM, hr⟩ :=
    exists_semisimple_seed_formula (R ⧸ Ring.jacobson R) (RadicalTop R M)
  exact ⟨q, D, d, m, hD, hd, eR, heM, seedRank_eq_radicalTop.trans hr⟩

/-- Manuscript-facing finite-dimensional-algebra formula with no caller-supplied decomposition. -/
theorem exists_finiteAlgebra_seed_formula
    (k : Type u) [Field k] [Algebra k R] [Module.Finite k R] :
    ∃ (q : ℕ) (D : Fin q → Type u) (d m : Fin q → ℕ) (_ : ∀ i, DivisionRing (D i)),
      (∀ i, 0 < d i) ∧
      ∃ eR : (R ⧸ Ring.jacobson R) ≃+* DivisionProductAlgebra (D := D) d,
        Nonempty (RadicalTop R M ≃ₛₗ[(RingHomClass.toRingHom eR)]
          (⨁ i : Fin q, (Fin (m i) → Simple (D := D) d i))) ∧
        seedRank R M = (maxCeilDiv d m : Cardinal) := by
  let : IsArtinianRing R := isArtinian_of_tower k inferInstance
  exact exists_artinian_radicalTop_seed_formula R M

end Existence
end Komorebi.PaperICompletion8.SemisimpleExistence
