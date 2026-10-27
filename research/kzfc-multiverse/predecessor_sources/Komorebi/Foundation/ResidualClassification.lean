import Komorebi.Foundation.ConeFilter
import Komorebi.Foundation.ResidualAudit

/-!
# Classification of the fixed-domain residual schema

These are schemas over a fixed, independently specified semantic constraint class,
not over arbitrary predicates retrospectively chosen to make reflection true.
Their equivalence with complete filter extension is a theorem; the existence of
an uncountable cardinal satisfying either schema is not asserted.
-/

universe u

namespace Komorebi.CompactnessClassification

open Set Filter
open FineUltrafilterCompactness

/-- Depth-zero KRR for all constraint systems with small value domain and small scopes. -/
def FixedDomainKRR0 (κ : Cardinal.{u}) : Prop :=
  ∀ (I V A : Type u), Cardinal.mk A < κ →
    ∀ (scope : I → Set V), (∀ i, Cardinal.mk (scope i) < κ) →
    ∀ (satisfies : I → (V → A) → Prop),
    (∀ i a b, (∀ v ∈ scope i, a v = b v) → satisfies i a → satisfies i b) →
    (residualSystem κ satisfies).KRR0At κ

/-- The finite-depth schema for the same class and the same residual encoding.
Only depth zero carries obstructions in this particular class. -/
def FixedDomainKRR (κ : Cardinal.{u}) : Prop :=
  ∀ (I V A : Type u), Cardinal.mk A < κ →
    ∀ (scope : I → Set V), (∀ i, Cardinal.mk (scope i) < κ) →
    ∀ (satisfies : I → (V → A) → Prop),
    (∀ i a b, (∀ v ∈ scope i, a v = b v) → satisfies i a → satisfies i b) →
    (residualSystem κ satisfies).KRRAt κ

/-- The residual predicates in this semantic encoding are sound without compactness. -/
theorem constraint_residual_sound {I V A : Type u} (κ : Cardinal.{u})
    (satisfies : I → (V → A) → Prop) :
    ((residualSystem κ satisfies).atScale κ).Sound := by
  intro q J _ ho hg
  obtain ⟨a, ha⟩ := hg
  exact ho.2 ⟨a, fun i _ => ha i⟩

/-- Contraposition, with no change of value domain or support bound. -/
theorem krr0_iff_fixedDomain (κ : Cardinal.{u}) :
    FixedDomainKRR0 κ ↔ FixedDomainCompactness κ := by
  constructor
  · intro hk I V A hA scope hscope satisfies locality hlocal
    by_contra hbad
    obtain ⟨J, _, _, ho⟩ := hk I V A hA scope hscope satisfies locality hbad
    exact ho (hlocal J)
  · intro hc I V A hA scope hscope satisfies locality hbad
    by_contra hn
    have hlocal : ∀ J : SmallPieces κ I, ∃ a : V → A, ∀ i ∈ J.val, satisfies i a := by
      intro J
      by_contra hj
      exact hn ⟨J, J.property, rfl, hj⟩
    exact hbad (hc I V A hA scope hscope satisfies locality hlocal)

/-- In this declared class, adding degree labels does not change the assertion. -/
theorem krr_iff_krr0 (κ : Cardinal.{u}) : FixedDomainKRR κ ↔ FixedDomainKRR0 κ := by
  constructor
  · intro hk I V A hA scope hscope satisfies locality hbad
    obtain ⟨q, J, hJ, _, ho⟩ := hk I V A hA scope hscope satisfies locality hbad
    exact ⟨J, hJ, rfl, ho⟩
  · intro hk I V A hA scope hscope satisfies locality
    exact SizedResidualSystem.krrAt_of_krr0At (hk I V A hA scope hscope satisfies locality)

/-- Main residual classification: the specified KRR0 schema is equivalent to the
complete-filter extension property, not merely a consequence of it. -/
theorem krr0_iff_extension (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    FixedDomainKRR0 κ ↔ CompleteFilterExtension κ :=
  (krr0_iff_fixedDomain κ).trans (fixedDomain_iff_extension κ hκ)

/-- The same classification for the original finite-depth witness interface. -/
theorem krr_iff_extension (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    FixedDomainKRR κ ↔ CompleteFilterExtension κ :=
  (krr_iff_krr0 κ).trans (krr0_iff_extension κ hκ)

theorem krr_iff_fine (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    FixedDomainKRR κ ↔ FineUltrafilterPrinciple κ :=
  ((krr_iff_krr0 κ).trans (krr0_iff_fixedDomain κ)).trans (fixedDomain_iff_fine κ hκ)

/-- This proposition is the candidate existence assertion in residual language.
It is defined, not assumed and not proved to hold. -/
def ResidualExistence : Prop :=
  ∃ κ : Cardinal.{u}, κ.IsRegular ∧ Cardinal.aleph0 < κ ∧ FixedDomainKRR κ

/-- Independently specified existence assertion in complete-filter language.
At regular uncountable kappa this is the standard strong-compactness form. -/
def FilterExtensionExistence : Prop :=
  ∃ κ : Cardinal.{u}, κ.IsRegular ∧ Cardinal.aleph0 < κ ∧ CompleteFilterExtension κ

/-- Equivalence of candidate existence assertions, not a proof of either assertion. -/
theorem residualExistence_iff_filterExtensionExistence :
    ResidualExistence.{u} ↔ FilterExtensionExistence.{u} := by
  constructor
  · rintro ⟨κ, hreg, hunc, hk⟩
    exact ⟨κ, hreg, hunc, (krr_iff_extension κ hreg).mp hk⟩
  · rintro ⟨κ, hreg, hunc, hf⟩
    exact ⟨κ, hreg, hunc, (krr_iff_extension κ hreg).mpr hf⟩

/-- Finite-domain, finite-scope compactness is a theorem of the ordinary baseline. -/
theorem krr_aleph0 : FixedDomainKRR Cardinal.aleph0.{u} :=
  (krr_iff_extension _ Cardinal.isRegular_aleph0).mpr extension_aleph0

end Komorebi.CompactnessClassification
