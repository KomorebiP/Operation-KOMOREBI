import RealizationBoundaries
set_option autoImplicit false
noncomputable section
open RealizationBoundaries
open CategoryTheory
namespace RealizationBoundariesClosureTests
example : Set Prime ≃o AddSubgroup finiteSupport := subgroupSpectrumOrderIso
example (B C : Set Prime) : Nonempty (spectrumSubgroup B ≃+ spectrumSubgroup C) ↔ B = C :=
  spectrumSubgroup_isomorphic_iff B C
example (H : AddSubgroup finiteSupport) (f : AddMonoid.End finiteSupport)
    (x : finiteSupport) (hx : x ∈ H) : f x ∈ H :=
  finiteSupport_subgroup_fullyInvariant H f hx
example (F : Finset Prime) (B : Set Prime) :
    Cardinal.mk (SpectrumObservationFiber F B) = Cardinal.continuum := spectrumObservationFiber_card F B
example (P : CompatibleSpectrumPatterns) :
    ∃! B : Set Prime, ∀ F : Finset Prime, P.pattern F = B ∩ (F : Set Prime) :=
  compatible_spectrum_patterns_exists_unique P
example (B : Set ℕ) : UnaryGroupRealizable B ↔ UltimatelyPeriodic B := unary_selector_classification B
example (W : Submodule ℚ TailSpace) :
    Countable (preimage W) ↔ Module.rank ℚ W ≤ Cardinal.aleph0 := preimage_countable_iff_rational_rank W
example (a : ℕ → Bool) (L : AddSubgroup (pairedGroup a)) (hL : L.FG) :
    ∃ m : ℕ, 0 < m ∧ Squarefree m ∧
      (Nonempty (L ≃+ ZMod m) ∨ Nonempty (L ≃+ ℤ × ZMod m)) :=
  paired_fg_subgroup_classification a L hL
example : residuallyFiniteCompletion.Faithful := inferInstance
example : ¬ pairedCompletionFunctor.Full := pairedCompletionFunctor_not_full
example : ¬ boundaryCompletionFunctor.ReflectsIsomorphisms := boundaryCompletionFunctor_not_reflects_isomorphisms
example (U V : Submodule ℚ TailSpace) :
    CommonCofinalObservation (allFiniteObservation U) (allFiniteObservation V) := allFiniteObservation_common U V
example (a X : ℕ → Bool) (c : OracleGroupCopy X (pairedGroup a)) : SelectorReducible a X :=
  oracle_unmarked_copy_reduces a X c
example (a : Prime → Bool) (x : selectorGroup {p | a p = true}) :
    ∃ r : ℚ, ∃ d : List ℕ, codedNormalValue a r d = x.val := codedNormalValue_represents a x
example (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) (t : ℚ) (e : List ℕ)
    (h : certifiedRootSolver a r d m = .ok (t,e)) (hm : 0 < m) :
    m • codedNormalValue a t e = codedNormalValue a r d := certifiedRootSolver_ok a r d hm t e h
end RealizationBoundariesClosureTests

example : (ℕ → Bool) ≃ₜ AddSubgroup finiteSupport := natSubgroupCantorHomeomorph
example (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    (countedCertifiedRootSolver a r d m).1.2.length ≤ m + 1 + 2 * rootCorrectionBound r d m :=
  countedCertifiedRootSolver_query_bound a r d m
example (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    (countedCertifiedRootSolver a r d m).2 ≤ m + 1 + rootCorrectionBound r d m :=
  countedCertifiedRootSolver_step_bound a r d m
example {X : ℕ → Bool} {H : Type} [AddGroup H] [Infinite H]
    (c : OracleRawGroupCodes X H) : Nonempty (OracleGroupCopy X H) := c.oracleGroupCopy_of_rawCodes
example {X : ℕ → Bool} {H : Type} [AddGroup H] (c : OracleGroupCopy X H) :
    OracleComputable X c.inverse := c.inverse_computable

example (a X : ℕ → Bool) :
    Nonempty (OracleGroupCopy X (pairedGroup a)) ↔ SelectorReducible a X := paired_oracle_copy_iff a X
example (X : ℕ → Bool) (B : Set Prime) :
    HasOracleGroupCopy X (spectrumSubgroup B) ↔ OracleEnumerable X {n | primeAt n ∈ B} :=
  oracle_spectrum_copy_iff_enumerable X B
example (X : ℕ → Bool) (A : Set ℕ) :
    OracleEnumerable X A ↔ Nonempty (OracleStageListing X A) := oracleEnumerable_iff_stageListing X A
example (a : ℕ → Bool) : HasLeastPresentationDegree (pairedGroup a) (selectorTuringDegree a) :=
  paired_least_presentation_degree a
example (W : Submodule ℚ TailSpace) :
    CommonCofinalObservation (allFiniteObservation W) fixedComputableObservation :=
  allFiniteObservation_fixed_computable W

example (a : ℕ → Bool) :
    TuringEquivalent (selectorOracle (operationGraphOracle (canonicalPairedAddition a))) (selectorOracle a) :=
  canonicalPairedAddition_graph_equivalent a
