import LocalFrobeniusPerfectPairing
import Mathlib.LinearAlgebra.Dual.Basis
import Mathlib.LinearAlgebra.Dimension.Free

/-!
# Perfect tame local pairing model

For a residual Frobenius matrix `A`, the linearized tame-inertia directions at
Taylor--Wiles level `q_v = 1` are matrices fixed by `Ad(A)`.  Unramified dual
cocycle representatives are matrices modulo `1 - Ad(A)`.  The trace pairing is
perfect between these two spaces.

This is the exact finite-dimensional algebraic model.  It does not identify the
model with arithmetic local Galois cohomology or fix the normalization of local
Tate duality.
-/

namespace Komorebi.StrongArtin.TameLocalPerfectPairing

open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- Linearized tame-inertia directions fixed by residual Frobenius. -/
abbrev tameInertiaTangent (A : (Matrix n n k)ˣ) :=
  frobeniusCentralizer A

/-- Unramified cocycle representatives modulo Frobenius coboundaries. -/
abbrev unramifiedCocycleQuotient (A : (Matrix n n k)ˣ) :=
  Matrix n n k ⧸ frobeniusCoboundaries A

/-- The model local pairing `([P],[X]) ↦ tr(PX)`. -/
def tameLocalPairing (A : (Matrix n n k)ˣ)
    (P : tameInertiaTangent A) :
    Module.Dual k (unramifiedCocycleQuotient A) :=
  centralizerEquivQuotientDual A P

@[simp]
theorem tameLocalPairing_mkQ
    (A : (Matrix n n k)ˣ) (P : tameInertiaTangent A)
    (X : Matrix n n k) :
    tameLocalPairing A P ((frobeniusCoboundaries A).mkQ X) =
      traceProbe P.1 X :=
  centralizerEquivQuotientDual_apply_mkQ A P X

/-- The tame model pairing is perfect: it identifies the tame-inertia tangent
space with the full dual of the unramified cocycle quotient. -/
def tameLocalPairingEquiv (A : (Matrix n n k)ˣ) :
    tameInertiaTangent A ≃ₗ[k]
      Module.Dual k (unramifiedCocycleQuotient A) :=
  centralizerEquivQuotientDual A

/-- Every nonzero tame-inertia direction detects some unramified quotient class. -/
theorem exists_unramified_class_detected
    (A : (Matrix n n k)ˣ) (P : tameInertiaTangent A)
    (hP : P ≠ 0) :
    ∃ x : unramifiedCocycleQuotient A,
      tameLocalPairing A P x ≠ 0 := by
  have hfun : tameLocalPairing A P ≠ 0 := by
    intro hzero
    apply hP
    apply (tameLocalPairingEquiv A).injective
    simpa [tameLocalPairing, tameLocalPairingEquiv] using hzero
  by_contra hnone
  have hall : ∀ x : unramifiedCocycleQuotient A,
      tameLocalPairing A P x = 0 := by
    intro x
    by_contra hx
    exact hnone ⟨x, hx⟩
  apply hfun
  apply LinearMap.ext
  intro x
  exact hall x

/-- Every nonzero unramified quotient class is detected by some tame-inertia
matrix. -/
theorem exists_tame_direction_detecting
    (A : (Matrix n n k)ˣ)
    (x : unramifiedCocycleQuotient A) (hx : x ≠ 0) :
    ∃ P : tameInertiaTangent A,
      tameLocalPairing A P x ≠ 0 := by
  let b := Module.finBasis k (unramifiedCocycleQuotient A)
  have heval : Module.Dual.eval k (unramifiedCocycleQuotient A) x ≠ 0 := by
    intro hzero
    apply hx
    apply (Module.Basis.eval_injective b)
    simpa using hzero
  have hex : ∃ φ : Module.Dual k (unramifiedCocycleQuotient A), φ x ≠ 0 := by
    by_contra hnone
    have hall : ∀ φ : Module.Dual k (unramifiedCocycleQuotient A), φ x = 0 := by
      intro φ
      by_contra hφ
      exact hnone ⟨φ, hφ⟩
    apply heval
    apply LinearMap.ext
    intro φ
    exact hall φ
  obtain ⟨φ, hφ⟩ := hex
  let P : tameInertiaTangent A := (tameLocalPairingEquiv A).symm φ
  refine ⟨P, ?_⟩
  change (tameLocalPairingEquiv A P) x ≠ 0
  simpa [P] using hφ

/-- Bidirectional nondegeneracy of the algebraic tame local pairing. -/
theorem tameLocalPairing_perfect
    (A : (Matrix n n k)ˣ) :
    (∀ P : tameInertiaTangent A, P ≠ 0 →
      ∃ x : unramifiedCocycleQuotient A,
        tameLocalPairing A P x ≠ 0) ∧
    (∀ x : unramifiedCocycleQuotient A, x ≠ 0 →
      ∃ P : tameInertiaTangent A,
        tameLocalPairing A P x ≠ 0) :=
  ⟨exists_unramified_class_detected A,
   exists_tame_direction_detecting A⟩

end

end Komorebi.StrongArtin.TameLocalPerfectPairing

#print axioms Komorebi.StrongArtin.TameLocalPerfectPairing.tameLocalPairingEquiv
#print axioms Komorebi.StrongArtin.TameLocalPerfectPairing.exists_unramified_class_detected
#print axioms Komorebi.StrongArtin.TameLocalPerfectPairing.exists_tame_direction_detecting
#print axioms Komorebi.StrongArtin.TameLocalPerfectPairing.tameLocalPairing_perfect
