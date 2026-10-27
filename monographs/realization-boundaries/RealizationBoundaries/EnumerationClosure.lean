import RealizationBoundaries.ListingSearchEquivalence
import RealizationBoundaries.OracleEnumerationNormalForm

/-! # Equivalent native enumeration contracts and the exact spectrum criterion -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

theorem oracleEnumerable_iff_searchEnumeration (X : ℕ → Bool) (A : Set ℕ) :
    OracleEnumerable X A ↔ Nonempty (OracleSearchEnumeration X A) := by
  constructor
  · intro h
    obtain ⟨test, hc, hs⟩ := oracleEnumerable_has_total_search X A h
    exact ⟨⟨test, hc, hs⟩⟩
  · rintro ⟨E⟩
    exact E.toOracleEnumerable

theorem oracleEnumerable_iff_stageListing (X : ℕ → Bool) (A : Set ℕ) :
    OracleEnumerable X A ↔ Nonempty (OracleStageListing X A) :=
  (oracleEnumerable_iff_searchEnumeration X A).trans
    (oracle_searchEnumeration_iff_stageListing X A)

/-- Monograph 3.3, also in the native partial-recursive-domain formulation. -/
theorem oracle_spectrum_copy_iff_enumerable (X : ℕ → Bool) (B : Set Prime) :
    HasOracleGroupCopy X (spectrumSubgroup B) ↔
      OracleEnumerable X {n | primeAt n ∈ B} :=
  (oracle_spectrum_copy_iff_searchEnumeration X B).trans
    (oracleEnumerable_iff_searchEnumeration X {n | primeAt n ∈ B}).symm

end RealizationBoundaries
