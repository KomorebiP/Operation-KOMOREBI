import GenericFiberSurvival
import ProductRingBranchSupport

/-!
# Residual occurrence to all generic branches

A nonzero special fibre makes the integral module nonzero.  If that module
injects into a split generic module, the generic module is nonzero.  A
transitive equivariant action on the split product-ring branches then forces
all branches to be supported.

The theorem is an abstract support pipeline.  It does not construct the
injective comparison map, the generic product decomposition, or the arithmetic
twist action.
-/

namespace Komorebi.StrongArtin.ResidualOccurrenceToGenericSupport

open Komorebi.StrongArtin.GenericFiberSurvival
open Komorebi.StrongArtin.TransitiveGenericBranchSupport
open Komorebi.StrongArtin.ProductRingBranchSupport

noncomputable section

variable {R M N K ι : Type*}
  [CommRing R]
  [AddCommGroup M] [Module R M]
  [AddCommGroup N] [Module R N]
  [Field K] [Fintype ι] [DecidableEq ι]
  [Module (ι → K) N]

/-- A nonzero special fibre and an injective comparison map force the target
module to be nonzero. -/
theorem target_nontrivial_of_specialFiber
    (π : R) [Nontrivial (specialFiber R M π)]
    (loc : M →ₗ[R] N) (hloc : Function.Injective loc) :
    Nontrivial N := by
  have hM : Nontrivial M := module_nontrivial_of_specialFiber R M π
  exact @Function.Injective.nontrivial M N hM loc hloc

/--
**Residual-to-generic branch-support capstone.** A nonzero special fibre, an
injective integral-to-generic comparison, a split product coefficient ring, and
a transitive equivariant twist action imply support on every generic branch.
-/
theorem all_generic_branches_supported
    (π : R) [Nontrivial (specialFiber R M π)]
    (loc : M →ₗ[R] N) (hloc : Function.Injective loc)
    (next : ι → ι) (T : N ≃ₗ[(ι → K)] N)
    (htransport : ∀ i m,
      T (branchIdempotent (K := K) i • m) =
        branchIdempotent (K := K) (next i) • T m)
    (htransitive : ∀ i j : ι,
      ∃ n : ℕ, iterateNext next n i = j) :
    ∀ j : ι,
      ComponentSupported (M := N) (branchIdempotent (K := K)) j := by
  have hN : Nontrivial N :=
    target_nontrivial_of_specialFiber π loc hloc
  exact @all_branches_supported_of_transitive K N ι
    _ _ _ _ _ hN next T htransport htransitive

end

end Komorebi.StrongArtin.ResidualOccurrenceToGenericSupport

#print axioms Komorebi.StrongArtin.ResidualOccurrenceToGenericSupport.target_nontrivial_of_specialFiber
#print axioms Komorebi.StrongArtin.ResidualOccurrenceToGenericSupport.all_generic_branches_supported
