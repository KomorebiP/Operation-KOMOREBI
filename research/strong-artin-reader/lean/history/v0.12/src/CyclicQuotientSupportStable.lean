import CyclicBranchSupportStable

namespace Komorebi.StrongArtin.CyclicQuotientSupport

open Komorebi.StrongArtin.CyclicDefect
open Komorebi.StrongArtin.CyclicBranchSupport

noncomputable section

variable (p : ℕ) [Fact p.Prime]

/-- A quotient ideal is forward-stable under the canonical quotient-character
 twist. This is the exact algebraic invariance condition needed to propagate
 generic branch support. -/
def TwistStableIdeal {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p)
    (I : Ideal (GenericFiber p K)) : Prop :=
  ∀ a, a ∈ I → twistHom p ζ hζ a ∈ I

/-- If a twist-stable quotient ideal vanishes on one generic cyclic branch,
then it vanishes on every branch. Thus a quotient of the cyclic defect algebra
cannot retain only a proper nonempty subset of the p branches while respecting
the quotient-character symmetry. -/
theorem ideal_killed_by_all_branches_of_one {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p)
    (I : Ideal (GenericFiber p K))
    (hI : TwistStableIdeal p ζ hζ I)
    (hne : ∃ x : ZMod p,
      I ≤ RingHom.ker (branchAtLabel p ζ hζ x).toRingHom) :
    ∀ x : ZMod p,
      I ≤ RingHom.ker (branchAtLabel p ζ hζ x).toRingHom := by
  apply all_branches_of_nonempty_twist_stable p ζ hζ
    (fun φ => I ≤ RingHom.ker φ.toRingHom)
  · exact hne
  · intro x hx a ha
    have hta : twistHom p ζ hζ a ∈ I := hI a ha
    have hzero : branchAtLabel p ζ hζ x (twistHom p ζ hζ a) = 0 := hx hta
    change ((branchAtLabel p ζ hζ x).comp (twistHom p ζ hζ)) a = 0
    exact hzero

/-- Under the same hypotheses, every generic branch factors through the
quotient algebra. This is the point-valued support formulation of the previous
theorem. -/
theorem every_branch_factors_through_quotient {K : Type*} [Field K]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p)
    (I : Ideal (GenericFiber p K))
    (hI : TwistStableIdeal p ζ hζ I)
    (hne : ∃ x : ZMod p,
      I ≤ RingHom.ker (branchAtLabel p ζ hζ x).toRingHom) :
    ∀ x : ZMod p, ∃ φ : (GenericFiber p K ⧸ I) →ₐ[K] K,
      φ.comp (Ideal.Quotient.mkₐ K I) = branchAtLabel p ζ hζ x := by
  have hall := ideal_killed_by_all_branches_of_one p ζ hζ I hI hne
  intro x
  have hk : ∀ a ∈ I, branchAtLabel p ζ hζ x a = 0 := by
    intro a ha
    exact hall x ha
  let φ : (GenericFiber p K ⧸ I) →ₐ[K] K :=
    Ideal.Quotient.liftₐ I (branchAtLabel p ζ hζ x) hk
  refine ⟨φ, ?_⟩
  exact Ideal.Quotient.liftₐ_comp I (branchAtLabel p ζ hζ x) hk

end
end Komorebi.StrongArtin.CyclicQuotientSupport

#print axioms Komorebi.StrongArtin.CyclicQuotientSupport.ideal_killed_by_all_branches_of_one
#print axioms Komorebi.StrongArtin.CyclicQuotientSupport.every_branch_factors_through_quotient
