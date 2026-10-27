import CyclotomicDepthSurvival
import TransverseAdjointPullbackNoFixed

namespace Komorebi.StrongArtin.RelativeCyclotomicDepthSurvival

open Komorebi.StrongArtin.CyclotomicDepthSurvival
open Komorebi.StrongArtin.TransverseAdjointRepresentation
open Komorebi.StrongArtin.TransverseAdjointPullbackNoFixed

noncomputable section

universe u

variable {k Γ G W : Type u}
  [Field k] [IsAlgClosed k]
  [Group Γ] [Fintype Γ] [Group G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]

/-- **Relative cyclotomic-depth survival.** Let a global group `G` act on the
transverse adjoint module through a finite residual quotient `Γ`. Assume:

* the residual representation of `Γ` is irreducible;
* `|Γ|` is nonzero in the coefficient field;
* `res : G → Γ` is surjective;
* a normal subgroup `S` lies in the residual kernel and `G/S` has order
  nonzero in the coefficient field;
* `T ≤ S` is deep enough that conjugation by `G` is trivial on `S/T`.

Then every nonzero transverse `H¹` class has a cocycle value nonzero already on
`T`. This is the exact abstract survival statement needed before imposing a
deeper cyclotomic congruence. The arithmetic task of proving the centrality
condition for the concrete cyclotomic tower remains separate. -/
theorem exists_deep_transverse_cocycle_value
    (ρ : Representation k Γ W) [Representation.IsIrreducible ρ]
    (hΓcard : (Fintype.card Γ : k) ≠ 0)
    (res : G →* Γ) (hresSurj : Function.Surjective res)
    (S T : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (hquot : (Fintype.card (G ⧸ S) : k) ≠ 0)
    (hTS : T ≤ S)
    (hresS : ∀ s : S, res s = 1)
    (hcentral : ∀ g : G, ∀ s : S,
      g * (s : G) * g⁻¹ * (s : G)⁻¹ ∈ T)
    (f : groupCohomology.cocycles₁
      (Rep.res res (transverseAdjointRep ρ)))
    (hclass : groupCohomology.H1π
      (Rep.res res (transverseAdjointRep ρ)) f ≠ 0) :
    ∃ t : T, f t ≠ 0 := by
  apply exists_deeper_nonzero_value_from_nonzero_H1
    (Rep.res res (transverseAdjointRep ρ)) f S T hquot hclass hTS
  · intro s
    change (transverseAdjointRep ρ).ρ (res s) = 1
    rw [hresS s]
    exact map_one _
  · exact hcentral
  · intro q hq
    exact pullback_transverseAdjoint_fixed_eq_zero
      ρ hΓcard res hresSurj q hq

end
end Komorebi.StrongArtin.RelativeCyclotomicDepthSurvival

#print axioms Komorebi.StrongArtin.RelativeCyclotomicDepthSurvival.exists_deep_transverse_cocycle_value
