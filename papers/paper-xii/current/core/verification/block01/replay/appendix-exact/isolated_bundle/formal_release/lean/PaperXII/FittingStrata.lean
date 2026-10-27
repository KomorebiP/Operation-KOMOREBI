import PaperXII.FittingBoundaryChecks
import Mathlib.RingTheory.LocalRing.Module

/-! Intrinsic Fitting support and all higher residue-fiber strata. -/
noncomputable section
namespace PaperXII
open TensorProduct

/-- Over a field, all intrinsic Fitting ideals are determined by actual vector-space dimension. -/
theorem fittingIdeal_field {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    [Module.FinitePresentation K V] (j : ℕ) :
    fittingIdeal K V j = if Module.finrank K V ≤ j then ⊤ else ⊥ := by
  calc
    fittingIdeal K V j = fittingIdeal K (Fin (Module.finrank K V) → K) j :=
      fittingIdeal_linearEquiv (Module.finBasis K V).equivFun j
    _ = _ := fittingIdeal_free _ _

variable {R M : Type*} [CommRing R] [AddCommGroup M] [Module R M]

/-- Ideal containment at a prime is exactly the strict residue-fiber dimension condition. -/
theorem fittingIdeal_le_prime_iff [Module.FinitePresentation R M]
    (p : PrimeSpectrum R) (j : ℕ) :
    fittingIdeal R M j ≤ p.asIdeal ↔
      j < Module.finrank p.asIdeal.ResidueField (p.asIdeal.ResidueField ⊗[R] M) := by
  have hmap : Ideal.map (algebraMap R p.asIdeal.ResidueField) (fittingIdeal R M j) = ⊥ ↔
      fittingIdeal R M j ≤ p.asIdeal := by
    rw [Ideal.map_eq_bot_iff_le_ker,Ideal.ker_algebraMap_residueField]
  rw [← hmap, ← fittingIdeal_baseChange, fittingIdeal_field]
  by_cases h : Module.finrank p.asIdeal.ResidueField (p.asIdeal.ResidueField ⊗[R] M) ≤ j
  · simp [h,not_lt_of_ge h]
  · simp [h,Nat.lt_of_not_ge h]

/-- Paper XII, Claim 6.3: intrinsic zeroth Fitting ideals cut out actual module support. -/
theorem support_eq_zeroLocus_fittingIdeal [Module.FinitePresentation R M] :
    Module.support R M = PrimeSpectrum.zeroLocus (fittingIdeal R M 0 : Set R) := by
  ext p
  change p ∈ Module.support R M ↔ fittingIdeal R M 0 ≤ p.asIdeal
  rw [fittingIdeal_le_prime_iff,
    Module.mem_support_iff_nontrivial_residueField_tensorProduct,
    Module.finrank_pos_iff]

/-- Paper XII, Claim 6.4: all higher Fitting strata, including r above every generator bound. -/
theorem higherFittingStrata [Module.FinitePresentation R M] (r : ℕ) (hr : 1 ≤ r) :
    {p : PrimeSpectrum R |
      r ≤ Module.finrank p.asIdeal.ResidueField (p.asIdeal.ResidueField ⊗[R] M)} =
      PrimeSpectrum.zeroLocus (fittingIdeal R M (r-1) : Set R) := by
  ext p
  change r ≤ Module.finrank p.asIdeal.ResidueField (p.asIdeal.ResidueField ⊗[R] M) ↔
    fittingIdeal R M (r-1) ≤ p.asIdeal
  rw [fittingIdeal_le_prime_iff]
  omega

/-- Claims 6.3 and 6.4 under exactly the manuscript's finite-Noetherian hypotheses. -/
theorem fitting_support_and_strata_noetherian [IsNoetherianRing R] [Module.Finite R M] :
    let _ : Module.FinitePresentation R M := Module.finitePresentation_of_finite R M
    Module.support R M = PrimeSpectrum.zeroLocus (fittingIdeal R M 0 : Set R) ∧
    ∀ r : ℕ, 1 ≤ r →
      {p : PrimeSpectrum R |
        r ≤ Module.finrank p.asIdeal.ResidueField (p.asIdeal.ResidueField ⊗[R] M)} =
        PrimeSpectrum.zeroLocus (fittingIdeal R M (r-1) : Set R) := by
  let : Module.FinitePresentation R M := Module.finitePresentation_of_finite R M
  exact ⟨support_eq_zeroLocus_fittingIdeal, higherFittingStrata⟩

end PaperXII
