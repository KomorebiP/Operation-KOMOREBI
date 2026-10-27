import GoodAuxiliarySelection

namespace Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet

open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.GoodAuxiliarySelection

noncomputable section

/-- Exact interface between the arithmetic one-prime theorem and finite
Taylor--Wiles selection.  `admissible` packages all fixed arithmetic conditions
at a chosen depth (unramifiedness, avoidance of the bad set, cyclotomic
congruence, and the required residual spectral condition). -/
structure OnePrimeSelectionInterface
    (k H Aux : Type*) [Field k] [AddCommGroup H] [Module k H] where
  admissible : Aux → Prop
  localFunctional : Aux → Module.Dual k H
  detects : ∀ h : H, h ≠ 0 →
    ∃ a : Aux, admissible a ∧ localFunctional a h ≠ 0

variable {k H Aux : Type*} [Field k]
  [AddCommGroup H] [Module k H]

/-- Continue from any already chosen admissible auxiliary set.  At most the
current active dimension many new labels are required. -/
theorem extend_to_relative_TaylorWiles_set
    [DecidableEq Aux] [FiniteDimensional k H]
    (I : OnePrimeSelectionInterface k H Aux)
    (Q₀ : Finset Aux)
    (hQ₀ : ∀ a ∈ Q₀, I.admissible a) :
    ∃ Q : Finset Aux,
      Q₀ ⊆ Q ∧
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card ≤ Q₀.card +
        Module.finrank k (selectedKernel I.localFunctional Q₀) ∧
      selectedKernel I.localFunctional Q = ⊥ := by
  exact exists_finite_good_auxiliary_superset
    I.localFunctional I.admissible I.detects Q₀ hQ₀

/-- **Abstract finite relative Taylor--Wiles set theorem.** Once the arithmetic
one-prime theorem supplies an admissible scalar local functional detecting every
nonzero transverse dual-Selmer class, exactly `dim H` admissible auxiliary
labels can be selected; their local restriction/evaluation map is injective and
the resulting transverse Selmer kernel is zero. -/
theorem exists_relative_TaylorWiles_set_exact
    [DecidableEq Aux] [FiniteDimensional k H]
    (I : OnePrimeSelectionInterface k H Aux) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank k H ∧
      selectedKernel I.localFunctional Q = ⊥ ∧
      Function.Injective (evaluationMap I.localFunctional Q) := by
  obtain ⟨Q, hgood, hcard, hinj⟩ :=
    exists_finite_good_auxiliary_set_exact
      I.localFunctional I.admissible I.detects
  have hker : selectedKernel I.localFunctional Q = ⊥ := by
    rw [← ker_evaluationMap, LinearMap.ker_eq_bot]
    exact hinj
  exact ⟨Q, hgood, hcard, hker, hinj⟩

end
end Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet

#print axioms Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet.extend_to_relative_TaylorWiles_set
#print axioms Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet.exists_relative_TaylorWiles_set_exact
