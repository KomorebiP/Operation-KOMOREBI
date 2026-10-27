import FlatGenericFiberSurvival
import ProductRingBranchSupport

/-!
# Flat split-generic support capstone

A flat integral module with nonzero special fibre has nonzero generic fibre.
If that generic fibre is identified with a module over a finite split product
ring and a linear automorphism transports the factors transitively, every
factor is supported.

The theorem isolates the exact module-theoretic conclusion sought from relative
patching.  It does not construct the patched module, its flatness, the generic
splitting, or the twist-equivariant automorphism.
-/

namespace Komorebi.StrongArtin.FlatSplitGenericSupportCapstone

open scoped nonZeroDivisors
open Komorebi.StrongArtin.GenericFiberSurvival
open Komorebi.StrongArtin.FlatGenericFiberSurvival
open Komorebi.StrongArtin.TransitiveGenericBranchSupport
open Komorebi.StrongArtin.ProductRingBranchSupport

noncomputable section

variable {R M N K ι : Type*}
  [CommRing R]
  [AddCommGroup M] [Module R M] [Module.Flat R M]
  [AddCommGroup N] [Module R N]
  [Field K] [Fintype ι] [DecidableEq ι]
  [Module (ι → K) N]

/-- A split generic model linearly equivalent to the localization is nonzero. -/
theorem splitGeneric_nontrivial
    {π : R} (hπ : π ∈ R⁰)
    [Nontrivial (specialFiber R M π)]
    (genericComparison : genericFiber R M π ≃ₗ[R] N) :
    Nontrivial N := by
  have hgen : Nontrivial (genericFiber R M π) :=
    genericFiber_nontrivial_of_flat_specialFiber hπ
  exact @Function.Injective.nontrivial
    (genericFiber R M π) N hgen genericComparison
      genericComparison.injective

/--
**Flat split-generic support capstone.** Nonzero residual occurrence plus
flatness, generic splitting, and transitive twist equivariance force every
split generic branch to be nonzero.
-/
theorem all_split_generic_branches_supported
    {π : R} (hπ : π ∈ R⁰)
    [Nontrivial (specialFiber R M π)]
    (genericComparison : genericFiber R M π ≃ₗ[R] N)
    (next : ι → ι) (T : N ≃ₗ[(ι → K)] N)
    (htransport : ∀ i m,
      T (branchIdempotent (K := K) i • m) =
        branchIdempotent (K := K) (next i) • T m)
    (htransitive : ∀ i j : ι,
      ∃ n : ℕ, iterateNext next n i = j) :
    ∀ j : ι,
      ComponentSupported (M := N) (branchIdempotent (K := K)) j := by
  have hN : Nontrivial N := splitGeneric_nontrivial hπ genericComparison
  exact @all_branches_supported_of_transitive K N ι
    _ _ _ _ _ hN next T htransport htransitive

end

end Komorebi.StrongArtin.FlatSplitGenericSupportCapstone

#print axioms Komorebi.StrongArtin.FlatSplitGenericSupportCapstone.splitGeneric_nontrivial
#print axioms Komorebi.StrongArtin.FlatSplitGenericSupportCapstone.all_split_generic_branches_supported
