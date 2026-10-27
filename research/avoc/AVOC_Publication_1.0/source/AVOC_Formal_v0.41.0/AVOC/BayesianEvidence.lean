import AVOC.BayesianControl
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC

universe u v w

/-- Evidence normalizer for an arbitrary nonnegative likelihood weight. -/
def evidenceMass
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (L : Ω → ℚ) : ℚ :=
  ∑ ω, b.prob ω * L ω

/-- Nonnegative likelihoods have nonnegative evidence mass. -/
theorem evidenceMass_nonneg
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (L : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω) :
    0 ≤ evidenceMass b L := by
  unfold evidenceMass
  apply Finset.sum_nonneg
  intro ω hω
  exact mul_nonneg (b.nonneg ω) (hL ω)

/-- Conditioning by an arbitrary nonnegative likelihood weight. -/
def conditionByWeight
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (L : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω)
    (hpos : 0 < evidenceMass b L) : RationalBelief Ω where
  prob ω := b.prob ω * L ω / evidenceMass b L
  nonneg := by
    intro ω
    exact div_nonneg (mul_nonneg (b.nonneg ω) (hL ω)) (le_of_lt hpos)
  sum_one := by
    unfold evidenceMass
    change (∑ ω, (b.prob ω * L ω) * (∑ ω, b.prob ω * L ω)⁻¹) = 1
    rw [← Finset.sum_mul]
    exact mul_inv_cancel₀ (ne_of_gt hpos)

/-- Pointwise conditioning identity. -/
theorem conditionByWeight_mul_evidence
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (L : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω)
    (hpos : 0 < evidenceMass b L) (ω : Ω) :
    (conditionByWeight b L hL hpos).prob ω * evidenceMass b L =
      b.prob ω * L ω := by
  change (b.prob ω * L ω / evidenceMass b L) * evidenceMass b L =
    b.prob ω * L ω
  exact div_mul_cancel₀ _ (ne_of_gt hpos)

/-- Ordinary Bayes update is conditioning by the observation likelihood. -/
theorem bayesUpdate_eq_conditionByWeight
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    (b : RationalBelief Ω) (E : RationalChannel Ω O) (o : O)
    (hpos : 0 < predictiveProb b E o) :
    bayesUpdate b E o hpos =
      conditionByWeight b (fun ω => E.prob ω o)
        (fun ω => E.nonneg ω o) hpos := by
  apply RationalBelief.ext
  intro ω
  rfl

/-- Sequential evidence normalizers multiply to the normalizer of the product
likelihood. -/
theorem evidenceMass_condition_compose
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    (L₁ L₂ : Ω → ℚ)
    (hL₁ : ∀ ω, 0 ≤ L₁ ω)
    (_hL₂ : ∀ ω, 0 ≤ L₂ ω)
    (h₁ : 0 < evidenceMass b L₁) :
    evidenceMass b L₁ *
        evidenceMass (conditionByWeight b L₁ hL₁ h₁) L₂ =
      evidenceMass b (fun ω => L₁ ω * L₂ ω) := by
  unfold evidenceMass
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro ω hω
  have hc := conditionByWeight_mul_evidence b L₁ hL₁ h₁ ω
  calc
    (∑ x, b.prob x * L₁ x) *
        ((conditionByWeight b L₁ hL₁ h₁).prob ω * L₂ ω)
        = ((conditionByWeight b L₁ hL₁ h₁).prob ω *
            (∑ x, b.prob x * L₁ x)) * L₂ ω := by ring
    _ = (b.prob ω * L₁ ω) * L₂ ω := by
      have hh := congrArg (fun x : ℚ => x * L₂ ω) hc
      simpa [evidenceMass] using hh
    _ = b.prob ω * (L₁ ω * L₂ ω) := by rw [mul_assoc]

/-- Sequential conditioning equals one-step conditioning by the product
likelihood. -/
theorem conditionByWeight_compose
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    (L₁ L₂ : Ω → ℚ)
    (hL₁ : ∀ ω, 0 ≤ L₁ ω)
    (hL₂ : ∀ ω, 0 ≤ L₂ ω)
    (h₁ : 0 < evidenceMass b L₁)
    (h₂ : 0 < evidenceMass (conditionByWeight b L₁ hL₁ h₁) L₂) :
    let L₁₂ := fun ω => L₁ ω * L₂ ω
    let hL₁₂ : ∀ ω, 0 ≤ L₁₂ ω := fun ω => mul_nonneg (hL₁ ω) (hL₂ ω)
    let h₁₂ : 0 < evidenceMass b L₁₂ := by
      rw [← evidenceMass_condition_compose b L₁ L₂ hL₁ hL₂ h₁]
      exact mul_pos h₁ h₂
    conditionByWeight (conditionByWeight b L₁ hL₁ h₁) L₂ hL₂ h₂ =
      conditionByWeight b L₁₂ hL₁₂ h₁₂ := by
  dsimp
  let b₁ := conditionByWeight b L₁ hL₁ h₁
  let b₂ := conditionByWeight b₁ L₂ hL₂ h₂
  let L₁₂ := fun ω => L₁ ω * L₂ ω
  have hL₁₂ : ∀ ω, 0 ≤ L₁₂ ω := fun ω => mul_nonneg (hL₁ ω) (hL₂ ω)
  have hmass := evidenceMass_condition_compose b L₁ L₂ hL₁ hL₂ h₁
  have h₁₂ : 0 < evidenceMass b L₁₂ := by
    rw [← hmass]
    exact mul_pos h₁ h₂
  let bj := conditionByWeight b L₁₂ hL₁₂ h₁₂
  apply RationalBelief.ext
  intro ω
  apply mul_right_cancel₀ (ne_of_gt h₁₂)
  have hb₂ := conditionByWeight_mul_evidence b₁ L₂ hL₂ h₂ ω
  have hb₁ := conditionByWeight_mul_evidence b L₁ hL₁ h₁ ω
  have hbj := conditionByWeight_mul_evidence b L₁₂ hL₁₂ h₁₂ ω
  change b₂.prob ω * evidenceMass b L₁₂ = bj.prob ω * evidenceMass b L₁₂
  calc
    b₂.prob ω * evidenceMass b L₁₂
        = b₂.prob ω * (evidenceMass b L₁ * evidenceMass b₁ L₂) := by
            rw [hmass]
    _ = (b₂.prob ω * evidenceMass b₁ L₂) * evidenceMass b L₁ := by ring
    _ = (b₁.prob ω * L₂ ω) * evidenceMass b L₁ := by rw [hb₂]
    _ = (b₁.prob ω * evidenceMass b L₁) * L₂ ω := by ring
    _ = (b.prob ω * L₁ ω) * L₂ ω := by rw [hb₁]
    _ = b.prob ω * L₁₂ ω := by
      change (b.prob ω * L₁ ω) * L₂ ω = b.prob ω * (L₁ ω * L₂ ω)
      rw [mul_assoc]
    _ = bj.prob ω * evidenceMass b L₁₂ := by rw [hbj]

/-- Independent evidence order does not matter: conditioning by two likelihood
weights commutes whenever both sequential orders have positive evidence. -/
theorem conditionByWeight_commute
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    (L₁ L₂ : Ω → ℚ)
    (hL₁ : ∀ ω, 0 ≤ L₁ ω)
    (hL₂ : ∀ ω, 0 ≤ L₂ ω)
    (h₁ : 0 < evidenceMass b L₁)
    (h₂_after₁ : 0 < evidenceMass (conditionByWeight b L₁ hL₁ h₁) L₂)
    (h₂ : 0 < evidenceMass b L₂)
    (h₁_after₂ : 0 < evidenceMass (conditionByWeight b L₂ hL₂ h₂) L₁) :
    conditionByWeight (conditionByWeight b L₁ hL₁ h₁) L₂ hL₂ h₂_after₁ =
      conditionByWeight (conditionByWeight b L₂ hL₂ h₂) L₁ hL₁ h₁_after₂ := by
  have hleft := conditionByWeight_compose b L₁ L₂ hL₁ hL₂ h₁ h₂_after₁
  have hright := conditionByWeight_compose b L₂ L₁ hL₂ hL₁ h₂ h₁_after₂
  rw [hleft, hright]
  apply RationalBelief.ext
  intro ω
  simp [conditionByWeight, evidenceMass, mul_comm]

end Komorebi.AVOC
