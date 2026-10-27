import Mathlib.Algebra.Module.BigOperators
import Mathlib.LinearAlgebra.Basis.Basic

/-!
# Nonzero generic module and transitive branch support

A finite family of branch scalars summing to one must support at least one
nonzero component of a nonzero module.  If a linear automorphism transports
successive branch components and the induced action on branch labels is
transitive, every branch is supported.

This is the abstract support theorem needed after generic-fibre nonvanishing.
It does not construct the cyclotomic idempotents or the automorphic twist action.
-/

namespace Komorebi.StrongArtin.TransitiveGenericBranchSupport

noncomputable section

variable {R M ι : Type*} [CommRing R]
  [AddCommGroup M] [Module R M]

/-- A branch scalar supports a nonzero component of the module. -/
def ComponentSupported (e : ι → R) (i : ι) : Prop :=
  ∃ m : M, e i • m ≠ 0

/-- If finitely many branch scalars sum to one, a nonzero module has at least
one supported branch. -/
theorem exists_componentSupported [Fintype ι] [Nontrivial M]
    (e : ι → R) (hsum : ∑ i, e i = 1) :
    ∃ i : ι, ComponentSupported (M := M) e i := by
  obtain ⟨m, hm⟩ : ∃ m : M, m ≠ 0 := exists_ne 0
  by_contra hnone
  have hall : ∀ i : ι, e i • m = 0 := by
    intro i
    by_contra hi
    exact hnone ⟨i, m, hi⟩
  apply hm
  calc
    m = 1 • m := (one_smul R m).symm
    _ = (∑ i, e i) • m := by rw [hsum]
    _ = ∑ i, e i • m := by rw [Finset.sum_smul]
    _ = 0 := by simp [hall]

/-- Equivariant transport by an automorphism propagates support by one branch
step. -/
theorem componentSupported_next
    (e : ι → R) (next : ι → ι) (T : M ≃ₗ[R] M)
    (htransport : ∀ i m, T (e i • m) = e (next i) • T m)
    {i : ι} (hi : ComponentSupported (M := M) e i) :
    ComponentSupported (M := M) e (next i) := by
  obtain ⟨m, hm⟩ := hi
  refine ⟨T m, ?_⟩
  rw [← htransport i m]
  simpa using T.injective.ne hm

/-- Left-recursive iteration of a branch successor. -/
def iterateNext (next : ι → ι) : ℕ → ι → ι
  | 0, i => i
  | n + 1, i => next (iterateNext next n i)

@[simp]
theorem iterateNext_zero (next : ι → ι) (i : ι) :
    iterateNext next 0 i = i := rfl

@[simp]
theorem iterateNext_succ (next : ι → ι) (n : ℕ) (i : ι) :
    iterateNext next (n + 1) i = next (iterateNext next n i) := rfl

/-- Support propagates through every iterate of the branch successor. -/
theorem componentSupported_iterate
    (e : ι → R) (next : ι → ι) (T : M ≃ₗ[R] M)
    (htransport : ∀ i m, T (e i • m) = e (next i) • T m)
    {i : ι} (hi : ComponentSupported (M := M) e i) :
    ∀ n : ℕ, ComponentSupported (M := M) e (iterateNext next n i) := by
  intro n
  induction n with
  | zero => simpa using hi
  | succ n ihn =>
      simpa using componentSupported_next e next T htransport ihn

/--
**Transitive generic support capstone.** A nonzero module, a finite decomposition
of the identity, and a transitive equivariant branch action force every generic
branch to support a nonzero component.
-/
theorem all_components_supported_of_transitive [Fintype ι] [Nontrivial M]
    (e : ι → R) (hsum : ∑ i, e i = 1)
    (next : ι → ι) (T : M ≃ₗ[R] M)
    (htransport : ∀ i m, T (e i • m) = e (next i) • T m)
    (htransitive : ∀ i j : ι, ∃ n : ℕ, iterateNext next n i = j) :
    ∀ j : ι, ComponentSupported (M := M) e j := by
  obtain ⟨i, hi⟩ := exists_componentSupported (M := M) e hsum
  intro j
  obtain ⟨n, hn⟩ := htransitive i j
  rw [← hn]
  exact componentSupported_iterate e next T htransport hi n

end

end Komorebi.StrongArtin.TransitiveGenericBranchSupport

#print axioms Komorebi.StrongArtin.TransitiveGenericBranchSupport.exists_componentSupported
#print axioms Komorebi.StrongArtin.TransitiveGenericBranchSupport.componentSupported_iterate
#print axioms Komorebi.StrongArtin.TransitiveGenericBranchSupport.all_components_supported_of_transitive
