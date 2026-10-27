import PaperXII.OrdinaryPatching
import Mathlib.RingTheory.Spectrum.Prime.Topology

/-! Amended Paper XII 6.12: each component is contained in the support.
The original reversed containment is not claimed as proved. -/
set_option autoImplicit false
namespace PaperXII.CorrectedOccupancy
open ModuleSupport

/-- Full support after patching contains every entire irreducible component. -/
theorem componentwise_occupancy
    {A R P M : Type*} [CommRing A] [CommRing R] [Algebra A R]
    [AddCommGroup P] [Module A P] [Module.Finite A P]
    [AddCommGroup M] [Module A M] [Module R M] [IsScalarTower A R M]
    (I : Ideal A) (hf : Function.Surjective (algebraMap A R))
    (hker : RingHom.ker (algebraMap A R) = I)
    (e : (P ⧸ (I • ⊤ : Submodule A P)) ≃ₗ[A] M) (h : FullSupport A P) :
    ∀ Z ∈ irreducibleComponents (PrimeSpectrum R), Z ⊆ Module.support R M := by
  have hs := OrdinaryPatching.fullSupport_descends I hf hker e h
  intro Z _
  rw [show Module.support R M = Set.univ from hs]
  exact Set.subset_univ Z

end PaperXII.CorrectedOccupancy
