import KomorebiVerification.PaperII.ReleaseResultantPolynomial
import KomorebiVerification.PaperII.ReleaseGluingPrecisionBridge

/-! The actual polynomial resultant supplies the normalized DVR clearing bound. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseResultantDVR
open Polynomial ResultantSeparation ReleaseResultantPolynomial ReleaseGluing
open scoped TensorProduct
universe u v w
variable {O : Type u} {K : Type v} {L : Type w}
variable [CommRing O] [IsDomain O] [IsDiscreteValuationRing O]
variable [Field K] [Algebra O K]
variable [AddCommGroup L] [Module O L] [Module.Free O L] [Module.Finite O L]

/-- Construct the projector and its uniformizer-power lattice bound from
the integral characteristic factorization, with no clearing premise. -/
theorem resultant_projector_valuation_bound
    (pi : O) (hpi : Irreducible pi) (A : Module.End O L) (f g : O[X])
    (hf : f.Monic) (hg : g.Monic)
    (hc : IsCoprime (f.map (algebraMap O K)) (g.map (algebraMap O K)))
    (hchar : A.charpoly = f * g) :
    ∃ E : Module.End K (K ⊗[O] L),
      E * E = E ∧
      LinearMap.range E = LinearMap.ker (aeval (A.baseChange K) (f.map (algebraMap O K))) ∧
      LinearMap.ker E = LinearMap.ker (aeval (A.baseChange K) (g.map (algebraMap O K))) ∧
      IsSeparationWeight (algebraMap O K pi) E
        (tensorLattice (K := K) (R := O) (L := L)).toAddSubgroup
        (IsDiscreteValuationRing.addVal O (f.resultant g)).toNat := by
  obtain ⟨u, v, _hbez, cert, hidem, hrange, hker, _hcompl, hclear⟩ :=
    integral_resultant_projector (K := K) A f g hf hg hc hchar
  let E := separator (algebraMap O K (f.resultant g))
    (aeval (A.baseChange K) (v.map (algebraMap O K)))
    (aeval (A.baseChange K) (g.map (algebraMap O K)))
  have hr : f.resultant g ≠ 0 := by
    intro hzero
    have hn := mapped_resultant_nonzero (K := K) f g hf hg hc
    exact hn (by rw [hzero, map_zero])
  refine ⟨E, hidem, hrange, hker, ?_⟩
  apply original_clearing_weight_at_valuation
    (tensorLattice (K := K) (R := O) (L := L)) pi hpi (f.resultant g) hr E
  intro x hx
  simpa only [LinearMap.smul_apply, algebraMap_smul] using hclear x hx

end Komorebi.PaperII.ReleaseResultantDVR
