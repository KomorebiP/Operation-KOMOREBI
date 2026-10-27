import TransverseAdjointNoFixed

namespace Komorebi.StrongArtin.TransverseAdjointPullbackNoFixed

open Komorebi.StrongArtin.TransverseAdjointRepresentation
open Komorebi.StrongArtin.TransverseAdjointNoFixed

noncomputable section

universe u

variable {k Γ G W : Type u}
  [Field k] [IsAlgClosed k]
  [Group Γ] [Fintype Γ] [Group G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]

/-- A surjective pullback from a finite residual image cannot create new fixed
vectors in the transverse adjoint quotient. -/
theorem pullback_transverseAdjoint_fixed_eq_zero
    (ρ : Representation k Γ W) [Representation.IsIrreducible ρ]
    (hcard : (Fintype.card Γ : k) ≠ 0)
    (res : G →* Γ) (hres : Function.Surjective res)
    (q : Rep.res res (transverseAdjointRep ρ))
    (hq : ∀ g : G, (Rep.res res (transverseAdjointRep ρ)).ρ g q = q) :
    q = 0 := by
  apply transverseAdjoint_fixed_eq_zero_of_irreducible ρ hcard q
  intro γ
  rcases hres γ with ⟨g, rfl⟩
  exact hq g

end
end Komorebi.StrongArtin.TransverseAdjointPullbackNoFixed

#print axioms Komorebi.StrongArtin.TransverseAdjointPullbackNoFixed.pullback_transverseAdjoint_fixed_eq_zero
