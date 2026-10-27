import H1RestrictionInjective
import TransverseQuotientProjectorProbes
import PreChebotarevSelector

namespace Komorebi.StrongArtin.TransverseCohomologicalPreChebotarev

open Komorebi.StrongArtin.H1RestrictionInjective
open Komorebi.StrongArtin.PreChebotarevSelector
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.TransverseAdjointRepresentation
open Komorebi.StrongArtin.TransverseQuotientProjectorProbes

noncomputable section

universe u i c

variable {k G W : Type u} {ι : Type i} {C : Type c}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction G ι] [Monoid C]

/-- **Transverse cohomological pre-Chebotarev capstone.** Work directly in the
quotient adjoint representation `End(W) / k·1`. A nonzero `H¹` class remains
nonzero on a normal subgroup whose quotient order is nonzero in `k`; some
subgroup element therefore has a nonzero transverse cocycle value. Relative
spectral detection chooses an actual centered projector detecting that value,
and the two-point selector modifies a prescribed residual Frobenius candidate
without changing either its residual matrix or its cyclotomic label.

Unlike the ambient-adjoint version, this theorem has no separate hypothesis
asserting that nonzero cocycle values are nonscalar: scalar values have already
been quotiented out in the coefficient representation. No Chebotarev theorem
or local Tate-duality identification is asserted. -/
theorem exists_detected_label_preserving_element_from_transverse_H1
    (ρ : Representation k G W)
    (S : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (f : groupCohomology.cocycles₁ (transverseAdjointRep ρ))
    (P : ι → Module.End k W) (i0 : ι)
    (cyc : G →* C)
    (g : G)
    (hquot : (Fintype.card (G ⧸ S) : k) ≠ 0)
    (hclass : groupCohomology.H1π (transverseAdjointRep ρ) f ≠ 0)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (hresKernel : ∀ s : S, ρ s = (1 : Module.End k W))
    (hcycKernel : ∀ s : S, cyc s = 1)
    (hcycg : cyc g = 1) :
    ∃ i : ι, ∃ γ : G,
      ρ γ = ρ g ∧
      cyc γ = 1 ∧
      transverseProjectorProbe ρ P i0 href i (f γ) ≠ 0 := by
  obtain ⟨s, hs⟩ :=
    exists_subgroup_element_with_nonzero_cocycle_value
      (transverseAdjointRep ρ) S hquot f hclass
  obtain ⟨i, hi⟩ :=
    exists_transverseProjectorProbe_ne_zero
      ρ P i0 href hP hoff (f s) hs
  obtain ⟨γ, _hchoice, hres, hcyc, hdetect⟩ :=
    exists_label_preserving_detected_element
      (A := transverseAdjointRep ρ)
      f (transverseProjectorProbe ρ P i0 href i) ρ cyc s g
      (transverseAdjoint_action_eq_one_of_residual_eq_one ρ s (hresKernel s))
      (hresKernel s) (hcycKernel s) hcycg hi
  exact ⟨i, γ, hres, hcyc, hdetect⟩

end
end Komorebi.StrongArtin.TransverseCohomologicalPreChebotarev

#print axioms Komorebi.StrongArtin.TransverseCohomologicalPreChebotarev.exists_detected_label_preserving_element_from_transverse_H1
