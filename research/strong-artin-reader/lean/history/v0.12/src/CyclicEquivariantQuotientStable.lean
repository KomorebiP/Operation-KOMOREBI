import CyclicQuotientSupportStable

namespace Komorebi.StrongArtin.CyclicEquivariantQuotient

open Komorebi.StrongArtin.CyclicDefect
open Komorebi.StrongArtin.CyclicBranchSupport
open Komorebi.StrongArtin.CyclicQuotientSupport

noncomputable section

variable (p : ℕ) [Fact p.Prime]

omit [Fact p.Prime] in
/-- Equivariance of a quotient map automatically makes its kernel stable under
the cyclic defect twist. No support hypothesis is used here. -/
theorem ker_twist_stable_of_equivariant {K B : Type*} [Field K] [CommRing B]
    [Algebra K B]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p)
    (q : GenericFiber p K →ₐ[K] B)
    (β : B →ₐ[K] B)
    (heq : β.comp q = q.comp (twistHom p ζ hζ)) :
    TwistStableIdeal p ζ hζ (RingHom.ker q.toRingHom) := by
  intro a ha
  change q a = 0 at ha
  change q (twistHom p ζ hζ a) = 0
  have hpoint := DFunLike.congr_fun heq a
  change β (q a) = q (twistHom p ζ hζ a) at hpoint
  rw [ha, map_zero] at hpoint
  exact hpoint.symm

/-- Patching-facing cyclic support theorem. Let `q` be a surjective algebra map
from the exact cyclic-defect algebra to a quotient algebra `B`. If `q` is
equivariant for the quotient-character twist and one generic branch factors
through `q`, then every generic branch factors through `q`.

This reduces the finite cyclic support problem to two global inputs: a nonzero
supported branch and an equivariant quotient map. -/
theorem all_branches_factor_through_equivariant_surjection
    {K B : Type*} [Field K] [CommRing B] [Algebra K B]
    (ζ : K) (hζ : IsPrimitiveRoot ζ p)
    (q : GenericFiber p K →ₐ[K] B)
    (hq : Function.Surjective q)
    (β : B →ₐ[K] B)
    (heq : β.comp q = q.comp (twistHom p ζ hζ))
    (hne : ∃ x : ZMod p, ∃ ψ : B →ₐ[K] K,
      ψ.comp q = branchAtLabel p ζ hζ x) :
    ∀ x : ZMod p, ∃ ψ : B →ₐ[K] K,
      ψ.comp q = branchAtLabel p ζ hζ x := by
  have hI : TwistStableIdeal p ζ hζ (RingHom.ker q.toRingHom) :=
    ker_twist_stable_of_equivariant p ζ hζ q β heq
  have hone : ∃ x : ZMod p,
      RingHom.ker q.toRingHom ≤
        RingHom.ker (branchAtLabel p ζ hζ x).toRingHom := by
    rcases hne with ⟨x, ψ, hψ⟩
    refine ⟨x, ?_⟩
    intro a ha
    change q a = 0 at ha
    change branchAtLabel p ζ hζ x a = 0
    rw [← hψ]
    simp [ha]
  have hall := ideal_killed_by_all_branches_of_one p ζ hζ
    (RingHom.ker q.toRingHom) hI hone
  intro x
  let ψ : B →ₐ[K] K :=
    AlgHom.liftOfSurjective q hq (branchAtLabel p ζ hζ x) (hall x)
  refine ⟨ψ, ?_⟩
  exact AlgHom.liftOfSurjective_comp q hq (branchAtLabel p ζ hζ x) (hall x)

end
end Komorebi.StrongArtin.CyclicEquivariantQuotient

#print axioms Komorebi.StrongArtin.CyclicEquivariantQuotient.ker_twist_stable_of_equivariant
#print axioms Komorebi.StrongArtin.CyclicEquivariantQuotient.all_branches_factor_through_equivariant_surjection
