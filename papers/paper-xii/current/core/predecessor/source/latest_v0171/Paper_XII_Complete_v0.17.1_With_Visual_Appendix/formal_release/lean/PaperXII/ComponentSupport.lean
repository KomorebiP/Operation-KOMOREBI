import PaperXII.ModuleSupport
import Mathlib.RingTheory.Spectrum.Prime.Topology

/-! Paper XII, Corollary 6.8, including actual irreducible components and generic points. -/
namespace PaperXII.ComponentSupport

open ModuleSupport

/-- Every irreducible component has a generic point with nonzero localized module. -/
theorem exists_genericPoint_nontrivial_localization
    {R M : Type*} [CommRing R] [IsNoetherianRing R]
    [AddCommGroup M] [Module R M] [Module.Finite R M]
    (h : NearlyFaithful R M) (Z : Set (PrimeSpectrum R))
    (hZ : Z ∈ irreducibleComponents (PrimeSpectrum R)) :
    ∃ p : PrimeSpectrum R, IsGenericPoint p Z ∧
      Nontrivial (LocalizedModule p.asIdeal.primeCompl M) := by
  obtain ⟨p, hp⟩ := QuasiSober.sober hZ.1
    (isClosed_of_mem_irreducibleComponents Z hZ)
  exact ⟨p, hp, nontrivial_localization_of_nearlyFaithful R M h p⟩

end PaperXII.ComponentSupport
