import Mathlib.RepresentationTheory.Irreducible
import QuotientFixedVectorAveraging
import TransverseAdjointRepresentation

namespace Komorebi.StrongArtin.TransverseAdjointNoFixed

open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.TransverseAdjointRepresentation
open Komorebi.StrongArtin.QuotientFixedVectorAveraging

noncomputable section

universe u

variable {k G W : Type u}
  [Field k] [IsAlgClosed k] [Group G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]

/-- Schur's lemma in conjugation form: for an irreducible representation over
an algebraically closed field, every endomorphism fixed by conjugation is
scalar. -/
theorem conjugation_fixed_mem_scalarLine_of_irreducible
    (ρ : Representation k G W) [Representation.IsIrreducible ρ]
    (X : Module.End k W)
    (hX : ∀ g : G, conjugationRepresentation ρ g X = X) :
    X ∈ scalarLine (k := k) (W := W) := by
  let F : Representation.IntertwiningMap ρ ρ :=
    LinearMap.intertwiningMap_of_isIntertwiningMap ρ ρ X (by
      intro g v
      have hv := LinearMap.congr_fun (hX g) (ρ g v)
      simpa [conjugationRepresentation_apply,
        Representation.inv_self_apply] using hv.symm)
  have hbij :=
    Representation.IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed
      (ρ := ρ)
  obtain ⟨a, ha⟩ := hbij.2 F
  have hscalar : F.toLinearMap = a • LinearMap.id := by
    apply LinearMap.ext
    intro v
    have hv := LinearMap.congr_fun
      (congrArg Representation.IntertwiningMap.toLinearMap ha) v
    simpa [F] using hv.symm
  rw [Submodule.mem_span_singleton]
  refine ⟨a, ?_⟩
  calc
    a • (1 : Module.End k W) = a • LinearMap.id := rfl
    _ = F.toLinearMap := hscalar.symm
    _ = X := rfl

/-- In the prime-to-characteristic finite-image regime, the transverse adjoint
quotient has no nonzero fixed vector. This combines Schur's lemma with exact
finite-group averaging; it does not require semisimplicity as a separate
hypothesis. -/
theorem transverseAdjoint_fixed_eq_zero_of_irreducible
    [Fintype G]
    (ρ : Representation k G W) [Representation.IsIrreducible ρ]
    (hcard : (Fintype.card G : k) ≠ 0)
    (q : transverseAdjointRep ρ)
    (hq : ∀ g : G, (transverseAdjointRep ρ).ρ g q = q) :
    q = 0 := by
  apply quotient_fixed_eq_zero_of_card_ne_zero
    (Rep.of (conjugationRepresentation ρ))
    (scalarLine (k := k) (W := W))
    (scalarLine_invariant ρ) hcard
  · intro X hfixed
    exact conjugation_fixed_mem_scalarLine_of_irreducible ρ X hfixed
  · exact hq

end
end Komorebi.StrongArtin.TransverseAdjointNoFixed

#print axioms Komorebi.StrongArtin.TransverseAdjointNoFixed.conjugation_fixed_mem_scalarLine_of_irreducible
#print axioms Komorebi.StrongArtin.TransverseAdjointNoFixed.transverseAdjoint_fixed_eq_zero_of_irreducible
