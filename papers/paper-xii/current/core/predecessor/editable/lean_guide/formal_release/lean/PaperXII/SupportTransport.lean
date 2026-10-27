import PaperXII.QuotientSupport
import Mathlib.RingTheory.Spectrum.Prime.Topology

/-! Paper XII, support portion of 7.1 and complete Corollary 7.2.
The Fitting-ideal assertion in 7.1 is not claimed by this module. -/
namespace PaperXII.SupportTransport

open ModuleSupport

variable {R S M : Type*} [CommRing R] [CommRing S] [Algebra R S]
    [AddCommGroup M] [Module R M] [Module S M] [IsScalarTower R S M]

/-- Under a surjective scalar map, localization support agrees at corresponding primes.
No finite generation is needed for this change of scalars. -/
theorem mem_support_comap_iff (hf : Function.Surjective (algebraMap R S))
    (q : PrimeSpectrum S) :
    PrimeSpectrum.comap (algebraMap R S) q ∈ Module.support R M ↔
      q ∈ Module.support S M := by
  simp only [Module.mem_support_iff', PrimeSpectrum.comap_asIdeal, Ideal.mem_comap]
  constructor
  · rintro ⟨m, hm⟩
    refine ⟨m, fun s hs ↦ ?_⟩
    obtain ⟨r, rfl⟩ := hf s
    simpa only [IsScalarTower.algebraMap_smul] using hm r hs
  · rintro ⟨m, hm⟩
    refine ⟨m, fun r hr ↦ ?_⟩
    simpa only [IsScalarTower.algebraMap_smul] using hm (algebraMap R S r) hr

/-- A ring isomorphism induces the actual homeomorphism of spectra. -/
theorem spectrum_isHomeomorph (hf : Function.Bijective (algebraMap R S)) :
    IsHomeomorph (PrimeSpectrum.comap (algebraMap R S)) :=
  PrimeSpectrum.isHomeomorph_comap_of_bijective hf

/-- Support assertion in 7.1, using the actual spectral map. -/
theorem image_support (hf : Function.Bijective (algebraMap R S)) :
    PrimeSpectrum.comap (algebraMap R S) '' Module.support S M = Module.support R M := by
  ext p
  constructor
  · rintro ⟨q, hq, rfl⟩
    exact (mem_support_comap_iff hf.surjective q).mpr hq
  · intro hp
    obtain ⟨q, rfl⟩ := (spectrum_isHomeomorph hf).surjective p
    exact ⟨q, (mem_support_comap_iff hf.surjective q).mp hp, rfl⟩

/-- Corollary 7.2: full support is invariant under the ring identification. -/
theorem fullSupport_iff (hf : Function.Bijective (algebraMap R S)) :
    FullSupport R M ↔ FullSupport S M := by
  constructor
  · intro h
    apply (fullSupport_iff_localizations S M).mpr
    intro q
    exact (mem_support_comap_iff hf.surjective q).mp
      ((fullSupport_iff_localizations R M).mp h _)
  · intro h
    unfold FullSupport at h ⊢
    rw [← image_support hf, h, Set.image_univ,
      Set.range_eq_univ.mpr (spectrum_isHomeomorph hf).surjective]

end PaperXII.SupportTransport
