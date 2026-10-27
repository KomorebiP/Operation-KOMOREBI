import RealizationBoundaries.SubgroupSpectrum

/-! # Coherent finite prime observations reconstruct exactly one selector -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Each finite observation is supported on its finite domain, and restricting
a larger observation gives exactly the smaller one. -/
structure CompatibleSpectrumPatterns where
  pattern : Finset Prime → Set Prime
  supported : ∀ F, pattern F ⊆ (F : Set Prime)
  compatible : ∀ F G, F ⊆ G → pattern F = pattern G ∩ (F : Set Prime)

/-- A full compatible family reads each selector bit from its singleton pattern. -/
def CompatibleSpectrumPatterns.selector (P : CompatibleSpectrumPatterns) : Set Prime :=
  {p | p ∈ P.pattern {p}}

/-- Compatibility is sufficient for existence of the global selector. -/
theorem CompatibleSpectrumPatterns.pattern_eq_restriction (P : CompatibleSpectrumPatterns)
    (F : Finset Prime) : P.pattern F = P.selector ∩ (F : Set Prime) := by
  classical
  ext p
  constructor
  · intro hp
    have hpF : p ∈ F := P.supported F hp
    refine ⟨?_, hpF⟩
    change p ∈ P.pattern {p}
    rw [P.compatible {p} F (Finset.singleton_subset_iff.mpr hpF)]
    exact ⟨hp, Finset.mem_singleton_self p⟩
  · rintro ⟨hp, hpF⟩
    change p ∈ P.pattern {p} at hp
    rw [P.compatible {p} F (Finset.singleton_subset_iff.mpr hpF)] at hp
    exact hp.1

/-- Every full compatible collection of finite membership patterns determines
one and only one prime selector, including existence rather than uniqueness alone. -/
theorem compatible_spectrum_patterns_exists_unique (P : CompatibleSpectrumPatterns) :
    ∃! B : Set Prime, ∀ F : Finset Prime, P.pattern F = B ∩ (F : Set Prime) := by
  classical
  refine ⟨P.selector, P.pattern_eq_restriction, ?_⟩
  intro B hB
  ext p
  have he := hB {p}
  have hp : p ∈ P.pattern {p} ↔ p ∈ B := by
    rw [he]
    simp
  exact hp.symm

/-- Coherent finite data therefore determine one actual subgroup of D. -/
theorem compatible_spectrum_patterns_group_unique (P : CompatibleSpectrumPatterns)
    (B C : Set Prime)
    (hB : ∀ F : Finset Prime, P.pattern F = B ∩ (F : Set Prime))
    (hC : ∀ F : Finset Prime, P.pattern F = C ∩ (F : Set Prime)) :
    spectrumSubgroup B = spectrumSubgroup C := by
  have h := compatible_spectrum_patterns_exists_unique P
  exact congrArg spectrumSubgroup (h.unique hB hC)

end RealizationBoundaries
