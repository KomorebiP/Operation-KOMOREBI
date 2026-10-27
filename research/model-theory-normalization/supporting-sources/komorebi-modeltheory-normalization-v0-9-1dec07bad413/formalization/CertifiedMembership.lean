module
public import DiscoveryTrace

@[expose] public section
namespace Komorebi.Discovery.Certified
open scoped BigOperators
open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix

/-- Untrusted finite data: either coefficients in the old rows or a separating
state difference. A malformed witness has no mathematical meaning until checked. -/
inductive Evidence (R : Type) (d : Nat) where
  | combination : List R → Evidence R d
  | separation : (Fin d → R) → Evidence R d

variable {R : Type} [CommRing R] [DecidableEq R] {d k o : Nat}

def memberCondition (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (ts : List (Test k o)) (v : Fin d → R)
    (c : List R) : Prop :=
  c.length = ts.length ∧
    (∑ i : Fin ts.length, c[i.val]?.getD 0 • testValue A O ts[i]) = v

def separationCondition (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (ts : List (Test k o)) (v : Fin d → R)
    (delta : Fin d → R) : Prop :=
  (∀ i : Fin ts.length, dot (testValue A O ts[i]) delta = 0) ∧ dot v delta ≠ 0

/-- None means invalid evidence, not nonmembership. No coefficient enumeration,
Smith elimination, division or source-state enumeration is performed here. -/
def checkMembership (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (ts : List (Test k o)) (v : Fin d → R) :
    Evidence R d → Option Bool
  | .combination c =>
      if c.length = ts.length ∧
          (∑ i : Fin ts.length, c[i.val]?.getD 0 • testValue A O ts[i]) = v
      then some true else none
  | .separation delta =>
      if (∀ i : Fin ts.length, dot (testValue A O ts[i]) delta = 0) ∧ dot v delta ≠ 0
      then some false else none

theorem checked_member (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (ts : List (Test k o)) (v : Fin d → R)
    (e : Evidence R d) (h : checkMembership A O ts v e = some true) :
    v ∈ testSpan A O ts := by
  cases e with
  | combination c =>
    simp only [checkMembership] at h
    split at h
    · rename_i hc
      exact span_member_from_coefficients A O ts v (fun i => c[i.val]?.getD 0) hc.2
    · cases h
  | separation delta =>
    simp only [checkMembership] at h
    split at h <;> simp_all

theorem checked_nonmember (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (ts : List (Test k o)) (v : Fin d → R)
    (e : Evidence R d) (h : checkMembership A O ts v e = some false) :
    v ∉ testSpan A O ts := by
  cases e with
  | combination c =>
    simp only [checkMembership] at h
    split at h <;> simp_all
  | separation delta =>
    simp only [checkMembership] at h
    split at h
    · rename_i hd
      exact span_nonmember_from_indexed_functional A O ts v (rowEvaluate delta) hd.1 hd.2
    · cases h

theorem checked_decision (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (ts : List (Test k o)) (v : Fin d → R)
    (e : Evidence R d) (b : Bool) (h : checkMembership A O ts v e = some b) :
    (b = true ↔ v ∈ testSpan A O ts) := by
  cases b with
  | true => exact ⟨fun _ => checked_member A O ts v e h, fun _ => rfl⟩
  | false =>
    constructor
    · intro hf; cases hf
    · intro hv; exact False.elim (checked_nonmember A O ts v e h hv)

/-- Valid evidence cannot certify opposing decisions for the same row. -/
theorem accepted_decisions_unique (A : Fin k → (Fin d → R) →ₗ[R] (Fin d → R))
    (O : Fin o → (Fin d → R)) (ts : List (Test k o)) (v : Fin d → R)
    (e f : Evidence R d) (b c : Bool)
    (he : checkMembership A O ts v e = some b)
    (hf : checkMembership A O ts v f = some c) : b = c := by
  apply Bool.eq_iff_iff.mpr
  exact (checked_decision A O ts v e b he).trans (checked_decision A O ts v f c hf).symm

end Komorebi.Discovery.Certified
