import Mathlib.RingTheory.Support
import Mathlib.RingTheory.Noetherian.Nilpotent

/-! Paper XII, claims 6.2, 6.7 and 6.8.
Support is Mathlib's actual localized-module support. -/
namespace PaperXII.ModuleSupport

variable (R M : Type*) [CommRing R] [AddCommGroup M] [Module R M]

/-- Every localization at a prime is nontrivial. -/
def FullSupport : Prop := Module.support R M = Set.univ

/-- The annihilator ideal has a zero power. -/
def NearlyFaithful : Prop := IsNilpotent (Module.annihilator R M)

/-- Manuscript 6.2. Finite generation suffices; no Noetherian assumption. -/
theorem support_eq_zeroLocus_annihilator [Module.Finite R M] :
    Module.support R M = PrimeSpectrum.zeroLocus (Module.annihilator R M) :=
  Module.support_eq_zeroLocus

/-- The localization meaning of full support, without a finiteness assumption. -/
theorem fullSupport_iff_localizations :
    FullSupport R M ↔ ∀ p : PrimeSpectrum R,
      Nontrivial (LocalizedModule p.asIdeal.primeCompl M) := by
  simp only [FullSupport, Set.eq_univ_iff_forall, Module.mem_support_iff]

/-- Manuscript 6.7, conditions (2) and (3). -/
theorem fullSupport_iff_annihilator_le_nilradical [Module.Finite R M] :
    FullSupport R M ↔ Module.annihilator R M ≤ nilradical R := by
  rw [FullSupport, Module.support_eq_zeroLocus, PrimeSpectrum.zeroLocus_eq_univ_iff]
  rfl

/-- Manuscript 6.7, conditions (1) and (3). -/
theorem nearlyFaithful_iff_annihilator_le_nilradical [IsNoetherianRing R] :
    NearlyFaithful R M ↔ Module.annihilator R M ≤ nilradical R :=
  Ideal.FG.isNilpotent_iff_le_nilradical (IsNoetherian.noetherian _)

/-- Manuscript 6.7, conditions (1) and (2). -/
theorem nearlyFaithful_iff_fullSupport [IsNoetherianRing R] [Module.Finite R M] :
    NearlyFaithful R M ↔ FullSupport R M :=
  (nearlyFaithful_iff_annihilator_le_nilradical R M).trans
    (fullSupport_iff_annihilator_le_nilradical R M).symm

/-- Manuscript 6.8, strengthened to every prime, hence every component generic point. -/
theorem nontrivial_localization_of_nearlyFaithful [IsNoetherianRing R]
    [Module.Finite R M] (h : NearlyFaithful R M) (p : PrimeSpectrum R) :
    Nontrivial (LocalizedModule p.asIdeal.primeCompl M) :=
  (fullSupport_iff_localizations R M).mp
    ((nearlyFaithful_iff_fullSupport R M).mp h) p

/-- Manuscript 6.7, reduced-ring refinement. -/
theorem nearlyFaithful_iff_faithful_of_reduced [IsNoetherianRing R] [IsReduced R] :
    NearlyFaithful R M ↔ FaithfulSMul R M := by
  rw [nearlyFaithful_iff_annihilator_le_nilradical, nilradical_eq_zero,
    Ideal.zero_eq_bot, le_bot_iff, Module.annihilator_eq_bot]

/-- Full support detects faithfulness over a reduced ring for finite modules. -/
theorem fullSupport_iff_faithful_of_reduced [Module.Finite R M] [IsReduced R] :
    FullSupport R M ↔ FaithfulSMul R M := by
  rw [fullSupport_iff_annihilator_le_nilradical, nilradical_eq_zero,
    Ideal.zero_eq_bot, le_bot_iff, Module.annihilator_eq_bot]

end PaperXII.ModuleSupport
