import TameLocalPerfectPairing

/-!
# Linearized tame inertia relation

For tame generators satisfying `φ τ φ⁻¹ = τ^q`, a first-order inertia value
`P` obeys `Ad(A) P = q P`, where `A` is residual Frobenius.  At a
Taylor--Wiles prime `q = 1` in the residue field, this is exactly the Frobenius
centralizer used by the perfect local pairing.

This module proves the linear relation only.  It does not derive it from a
continuous local Galois presentation or normalize local Tate duality.
-/

namespace Komorebi.StrongArtin.TameInertiaRelation

open Komorebi.StrongArtin.FrobeniusCocycleQuotient
open Komorebi.StrongArtin.LocalFrobeniusPerfectPairing

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- The linearized tame relation operator `Ad(A) - q`. -/
def tameRelationMap (A : (Matrix n n k)ˣ) (q : k) :
    Matrix n n k →ₗ[k] Matrix n n k :=
  conjugationLinear A - q • LinearMap.id

@[simp]
theorem tameRelationMap_apply
    (A : (Matrix n n k)ˣ) (q : k) (P : Matrix n n k) :
    tameRelationMap A q P =
      (A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k) - q • P := by
  rfl

/-- First-order tame inertia directions satisfying the Frobenius relation. -/
def tameInertiaRelationSpace (A : (Matrix n n k)ˣ) (q : k) :
    Submodule k (Matrix n n k) :=
  LinearMap.ker (tameRelationMap A q)

@[simp]
theorem mem_tameInertiaRelationSpace_iff
    (A : (Matrix n n k)ˣ) (q : k) (P : Matrix n n k) :
    P ∈ tameInertiaRelationSpace A q ↔
      (A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k) = q • P := by
  rw [tameInertiaRelationSpace, LinearMap.mem_ker]
  change
    (A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k) - q • P = 0 ↔ _
  exact sub_eq_zero

/-- At `q = 1`, the tame relation space is exactly the Frobenius centralizer. -/
theorem tameInertiaRelationSpace_one_eq_centralizer
    (A : (Matrix n n k)ˣ) :
    tameInertiaRelationSpace A 1 = frobeniusCentralizer A := by
  ext P
  rw [mem_tameInertiaRelationSpace_iff,
    mem_frobeniusCentralizer_iff_commute]
  constructor
  · intro h
    show P * (A : Matrix n n k) = (A : Matrix n n k) * P
    have h' : (A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k) = P := by
      simpa using h
    calc
      P * (A : Matrix n n k) =
          ((A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k)) *
            (A : Matrix n n k) := congrArg
              (fun X : Matrix n n k => X * (A : Matrix n n k)) h'.symm
      _ = (A : Matrix n n k) * P := by simp [Matrix.mul_assoc]
  · intro h
    have hEq : (A : Matrix n n k) * P = P * (A : Matrix n n k) := h.eq.symm
    calc
      (A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k) =
          P * (A : Matrix n n k) * (↑A⁻¹ : Matrix n n k) := by
            rw [hEq]
      _ = P := by simp
      _ = (1 : k) • P := by simp

/-- Any scalar congruent to one gives the same relation space. -/
theorem tameInertiaRelationSpace_eq_centralizer_of_eq_one
    (A : (Matrix n n k)ˣ) (q : k) (hq : q = 1) :
    tameInertiaRelationSpace A q = frobeniusCentralizer A := by
  subst q
  exact tameInertiaRelationSpace_one_eq_centralizer A

end

end Komorebi.StrongArtin.TameInertiaRelation

#print axioms Komorebi.StrongArtin.TameInertiaRelation.mem_tameInertiaRelationSpace_iff
#print axioms Komorebi.StrongArtin.TameInertiaRelation.tameInertiaRelationSpace_one_eq_centralizer
#print axioms Komorebi.StrongArtin.TameInertiaRelation.tameInertiaRelationSpace_eq_centralizer_of_eq_one
