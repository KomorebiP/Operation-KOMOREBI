import TransitiveGenericBranchSupport
import Mathlib.Algebra.BigOperators.Pi

/-!
# Generic branch support over a split product ring

After the cyclic defect algebra is split in the generic fibre, its coefficient
ring is a finite product of fields.  The coordinate idempotents sum to one.  A
nonzero module therefore has a nonzero component, and a transitive equivariant
automorphism propagates nonvanishing to every branch.

This module proves that product-ring support statement.  It does not construct
the generic splitting of the arithmetic Hecke algebra or its twist action.
-/

namespace Komorebi.StrongArtin.ProductRingBranchSupport

open Komorebi.StrongArtin.TransitiveGenericBranchSupport

noncomputable section

variable {K M ι : Type*} [Field K]
  [Fintype ι] [DecidableEq ι]
  [AddCommGroup M] [Module (ι → K) M]

/-- The primitive coordinate idempotent of the `i`th factor. -/
def branchIdempotent (i : ι) : ι → K :=
  Pi.single i 1

omit [Fintype ι] in
@[simp]
theorem branchIdempotent_apply_same (i : ι) :
    branchIdempotent (K := K) i i = 1 := by
  simp [branchIdempotent]

omit [Fintype ι] in
@[simp]
theorem branchIdempotent_apply_ne {i j : ι} (hij : i ≠ j) :
    branchIdempotent (K := K) i j = 0 := by
  simp [branchIdempotent, hij]

/-- The primitive branch idempotents decompose the identity of the product ring. -/
theorem sum_branchIdempotent :
    ∑ i : ι, branchIdempotent (K := K) i = 1 := by
  ext j
  simp [branchIdempotent]

/-- Every nonzero module over a finite product ring has at least one nonzero
coordinate component. -/
theorem exists_supported_branch [Nontrivial M] :
    ∃ i : ι,
      ComponentSupported (M := M) (branchIdempotent (K := K)) i := by
  exact exists_componentSupported
    (M := M) (branchIdempotent (K := K))
    (sum_branchIdempotent (K := K) (ι := ι))


omit [Fintype ι] in
/-- A faithful module over a split product ring supports every coordinate
branch, without needing a separate transitivity argument. -/
theorem all_branches_supported_of_faithful
    [FaithfulSMul (ι → K) M] :
    ∀ i : ι,
      ComponentSupported (M := M) (branchIdempotent (K := K)) i := by
  intro i
  by_contra hnone
  have hall : ∀ m : M, branchIdempotent (K := K) i • m = 0 := by
    intro m
    by_contra hm
    exact hnone ⟨m, hm⟩
  have heq : branchIdempotent (K := K) i = (0 : ι → K) :=
    @FaithfulSMul.eq_of_smul_eq_smul (ι → K) M _ _
      (branchIdempotent (K := K) i) 0 (fun m => by simpa using hall m)
  have hcoord := congrArg (fun f : ι → K => f i) heq
  have honezero : (1 : K) = 0 := calc
    (1 : K) = branchIdempotent (K := K) i i :=
      (branchIdempotent_apply_same (K := K) i).symm
    _ = (0 : ι → K) i := hcoord
    _ = 0 := rfl
  exact one_ne_zero honezero

/--
**Split generic support capstone.** If a module over `K^ι` is nonzero and a
linear automorphism transports coordinate components through a transitive
successor action on `ι`, then every generic coordinate branch is supported.
-/
theorem all_branches_supported_of_transitive [Nontrivial M]
    (next : ι → ι) (T : M ≃ₗ[(ι → K)] M)
    (htransport : ∀ i m,
      T (branchIdempotent (K := K) i • m) =
        branchIdempotent (K := K) (next i) • T m)
    (htransitive : ∀ i j : ι,
      ∃ n : ℕ, iterateNext next n i = j) :
    ∀ j : ι,
      ComponentSupported (M := M) (branchIdempotent (K := K)) j := by
  exact all_components_supported_of_transitive
    (M := M)
    (branchIdempotent (K := K))
    (sum_branchIdempotent (K := K) (ι := ι))
    next T htransport htransitive

end

end Komorebi.StrongArtin.ProductRingBranchSupport

#print axioms Komorebi.StrongArtin.ProductRingBranchSupport.sum_branchIdempotent
#print axioms Komorebi.StrongArtin.ProductRingBranchSupport.exists_supported_branch
#print axioms Komorebi.StrongArtin.ProductRingBranchSupport.all_branches_supported_of_faithful
#print axioms Komorebi.StrongArtin.ProductRingBranchSupport.all_branches_supported_of_transitive
