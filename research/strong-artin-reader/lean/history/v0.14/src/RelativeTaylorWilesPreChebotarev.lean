import RelativeCyclotomicDepthSurvival
import TransverseQuotientProjectorProbes
import PreChebotarevSelector

namespace Komorebi.StrongArtin.RelativeTaylorWilesPreChebotarev

open Komorebi.StrongArtin.PreChebotarevSelector
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.TransverseAdjointRepresentation
open Komorebi.StrongArtin.TransverseQuotientProjectorProbes
open Komorebi.StrongArtin.RelativeCyclotomicDepthSurvival

noncomputable section

universe u i c

variable {k Γ G W : Type u} {ι : Type i} {C : Type c}
  [Field k] [IsAlgClosed k]
  [Group Γ] [Fintype Γ] [Group G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction Γ ι] [Monoid C]

/-- **Relative Taylor--Wiles pre-Chebotarev capstone.** In the clean finite
residual-image regime, assume a deeper subgroup `T` is central modulo the
residual-kernel subgroup `S`. A nonzero transverse `H¹` class then supplies a
nonzero value on `T`; the relative spectral projector family detects that
value. For any prescribed element `g` with trivial cyclotomic label, there is a
candidate `γ` with:

* exactly the same residual-image element as `g`;
* trivial cyclotomic label;
* nonzero evaluation under an actual centered projector trace.

This closes the algebraic and finite-cohomological part of one-prime auxiliary
selection. It does not assert that `γ` is a Frobenius element, nor identify the
projector functional with a local Tate-duality quotient. -/
theorem exists_deep_label_preserving_projector_detected_element
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
      (Rep.res res (transverseAdjointRep ρ)) f ≠ 0)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (cyc : G →* C)
    (hcycT : ∀ t : T, cyc t = 1)
    (g : G) (hcycg : cyc g = 1) :
    ∃ i : ι, ∃ γ : G,
      res γ = res g ∧
      cyc γ = 1 ∧
      transverseProjectorProbe ρ P i0 href i (f γ) ≠ 0 := by
  obtain ⟨t, ht⟩ := exists_deep_transverse_cocycle_value
    ρ hΓcard res hresSurj S T hquot hTS hresS hcentral f hclass
  obtain ⟨i, hi⟩ := exists_transverseProjectorProbe_ne_zero
    ρ P i0 href hP hoff (f t) ht
  have hrest : res t = 1 := hresS ⟨t, hTS t.property⟩
  have hactt : (Rep.res res (transverseAdjointRep ρ)).ρ t = 1 := by
    change (transverseAdjointRep ρ).ρ (res t) = 1
    rw [hrest]
    exact map_one _
  obtain ⟨γ, _hchoice, hresγ, hcycγ, hdetect⟩ :=
    exists_label_preserving_detected_element
      (A := Rep.res res (transverseAdjointRep ρ))
      f (transverseProjectorProbe ρ P i0 href i)
      res cyc t g hactt hrest (hcycT t) hcycg hi
  exact ⟨i, γ, hresγ, hcycγ, hdetect⟩

end
end Komorebi.StrongArtin.RelativeTaylorWilesPreChebotarev

#print axioms Komorebi.StrongArtin.RelativeTaylorWilesPreChebotarev.exists_deep_label_preserving_projector_detected_element
