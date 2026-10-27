import PaperXII.ModuleSupport
import Mathlib.Algebra.Module.Torsion.Basic
import Mathlib.RingTheory.Spectrum.Prime.RingHom

/-! Paper XII, claim 6.9. Quotient rings and quotient modules are actual quotients. -/
namespace PaperXII.QuotientSupport

variable {R S M : Type*} [CommRing R] [CommRing S]
    [AddCommGroup M] [Module R M]

/-- Support under a surjective change of scalars. -/
theorem mem_support_restrictScalars_iff [Algebra R S] [Module S M]
    [IsScalarTower R S M] [Module.Finite R M]
    (hf : Function.Surjective (algebraMap R S)) (q : PrimeSpectrum S) :
    PrimeSpectrum.comap (algebraMap R S) q ∈ Module.support R M ↔
      q ∈ Module.support S M := by
  let : Module.Finite S M := Module.Finite.of_restrictScalars_finite R S M
  rw [Module.mem_support_iff_of_finite, Module.mem_support_iff_of_finite,
    ← Module.comap_annihilator (R := S) (R₀ := R)]
  exact Ideal.comap_le_comap_iff_of_surjective (algebraMap R S) hf _ _

/-- The ambient-spectrum quotient identity, from actual localization and Nakayama. -/
theorem support_quotient_over_base [Module.Finite R M] (I : Ideal R) :
    Module.support R (M ⧸ (I • ⊤ : Submodule R M)) =
      Module.support R M ∩ PrimeSpectrum.zeroLocus I :=
  Module.support_quotient I

/-- Manuscript 6.9, with its two spectra explicitly distinguished. -/
theorem support_quotient_iff [Module.Finite R M] (I : Ideal R)
    (q : PrimeSpectrum (R ⧸ I)) :
    q ∈ Module.support (R ⧸ I) (M ⧸ (I • ⊤ : Submodule R M)) ↔
      PrimeSpectrum.comap (Ideal.Quotient.mk I) q ∈ Module.support R M := by
  rw [← mem_support_restrictScalars_iff (R := R)
    (S := R ⧸ I) (Ideal.Quotient.mk_surjective) q,
    support_quotient_over_base]
  have hI : PrimeSpectrum.comap (Ideal.Quotient.mk I) q ∈
      PrimeSpectrum.zeroLocus I := by
    intro x hx
    change Ideal.Quotient.mk I x ∈ q.asIdeal
    rw [Ideal.Quotient.eq_zero_iff_mem.mpr hx]
    exact q.asIdeal.zero_mem
  exact and_iff_left hI

/-- Set form of 6.9: inverse image along Spec(R/I) → Spec R. -/
theorem support_quotient_eq_preimage [Module.Finite R M] (I : Ideal R) :
    Module.support (R ⧸ I) (M ⧸ (I • ⊤ : Submodule R M)) =
      PrimeSpectrum.comap (Ideal.Quotient.mk I) ⁻¹' Module.support R M := by
  ext q
  exact support_quotient_iff I q

/-- Manuscript 6.9, literal image form under the canonical spectrum identification. -/
theorem image_support_quotient [Module.Finite R M] (I : Ideal R) :
    PrimeSpectrum.comap (Ideal.Quotient.mk I) ''
      Module.support (R ⧸ I) (M ⧸ (I • ⊤ : Submodule R M)) =
      Module.support R M ∩ PrimeSpectrum.zeroLocus I := by
  rw [support_quotient_eq_preimage, Set.image_preimage_eq_inter_range,
    range_comap_of_surjective (R ⧸ I) (Ideal.Quotient.mk I)
      Ideal.Quotient.mk_surjective, Ideal.mk_ker]

end PaperXII.QuotientSupport
