import TameInertiaRelation

/-!
# Algebraic tame Taylor--Wiles pairing capstone

At residue-field norm `q_v = 1`, the linearized tame-inertia relation space is
identified with the full dual of unramified Frobenius cocycles modulo
coboundaries.  The pairing is exactly `(P,[X]) ↦ tr(PX)`.

This is the complete finite-dimensional local model.  Arithmetic local Tate
duality and its normalization remain external.
-/

namespace Komorebi.StrongArtin.TameTaylorWilesPairingCapstone

open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing
open Komorebi.StrongArtin.TameLocalPerfectPairing
open Komorebi.StrongArtin.TameInertiaRelation

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- The exact algebraic pairing equivalence for a tame Taylor--Wiles prime. -/
def tameRelationPairingEquiv (A : (Matrix n n k)ˣ) :
    tameInertiaRelationSpace A 1 ≃ₗ[k]
      Module.Dual k (Matrix n n k ⧸ frobeniusCoboundaries A) :=
  (LinearEquiv.ofEq
      (tameInertiaRelationSpace A 1)
      (frobeniusCentralizer A)
      (tameInertiaRelationSpace_one_eq_centralizer A)).trans
    (centralizerEquivQuotientDual A)

/-- On matrix representatives, the tame relation pairing is the projector trace. -/
@[simp]
theorem tameRelationPairingEquiv_apply_mkQ
    (A : (Matrix n n k)ˣ)
    (P : tameInertiaRelationSpace A 1)
    (X : Matrix n n k) :
    tameRelationPairingEquiv A P
        ((frobeniusCoboundaries A).mkQ X) = traceProbe P.1 X := by
  let Pcentral : frobeniusCentralizer A :=
    (LinearEquiv.ofEq
      (tameInertiaRelationSpace A 1)
      (frobeniusCentralizer A)
      (tameInertiaRelationSpace_one_eq_centralizer A)) P
  change centralizerEquivQuotientDual A Pcentral
      ((frobeniusCoboundaries A).mkQ X) = traceProbe P.1 X
  rw [centralizerEquivQuotientDual_apply_mkQ]
  rfl

/-- Every local quotient functional has a unique representative satisfying the
linearized tame relation. -/
theorem exists_unique_tame_relation_representative
    (A : (Matrix n n k)ˣ)
    (φ : Module.Dual k (Matrix n n k ⧸ frobeniusCoboundaries A)) :
    ∃! P : tameInertiaRelationSpace A 1,
      ∀ X : Matrix n n k,
        φ ((frobeniusCoboundaries A).mkQ X) = traceProbe P.1 X := by
  let P := (tameRelationPairingEquiv A).symm φ
  have hP : ∀ X : Matrix n n k,
      φ ((frobeniusCoboundaries A).mkQ X) = traceProbe P.1 X := by
    intro X
    calc
      φ ((frobeniusCoboundaries A).mkQ X) =
          tameRelationPairingEquiv A P
            ((frobeniusCoboundaries A).mkQ X) := by
              rw [show tameRelationPairingEquiv A P = φ by
                exact (tameRelationPairingEquiv A).apply_symm_apply φ]
      _ = traceProbe P.1 X :=
        tameRelationPairingEquiv_apply_mkQ A P X
  refine ⟨P, hP, ?_⟩
  intro Q hQ
  apply (tameRelationPairingEquiv A).injective
  apply Submodule.quot_hom_ext
  intro X
  change tameRelationPairingEquiv A Q
      ((frobeniusCoboundaries A).mkQ X) =
    tameRelationPairingEquiv A P
      ((frobeniusCoboundaries A).mkQ X)
  rw [tameRelationPairingEquiv_apply_mkQ,
    tameRelationPairingEquiv_apply_mkQ]
  exact (hQ X).symm.trans (hP X)

end

end Komorebi.StrongArtin.TameTaylorWilesPairingCapstone

#print axioms Komorebi.StrongArtin.TameTaylorWilesPairingCapstone.tameRelationPairingEquiv
#print axioms Komorebi.StrongArtin.TameTaylorWilesPairingCapstone.tameRelationPairingEquiv_apply_mkQ
#print axioms Komorebi.StrongArtin.TameTaylorWilesPairingCapstone.exists_unique_tame_relation_representative
