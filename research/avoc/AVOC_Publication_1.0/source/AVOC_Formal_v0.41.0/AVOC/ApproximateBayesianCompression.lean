import AVOC.ApproximateBayesian
import AVOC.BayesianCompression
import AVOC.ApproximateComposition

namespace Komorebi.AVOC

universe u v

/-- Deterministic belief pushforward is L1-contractive. -/
theorem beliefL1_pushforward_contract
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z) (b c : RationalBelief Ω) :
    beliefL1Distance (pushforwardBelief φ b) (pushforwardBelief φ c) ≤
      beliefL1Distance b c := by
  simpa [beliefL1Distance, l1RowDistance] using l1_pushforward_contract φ b.prob c.prob

/-- Approximate Bayes/compression commuting square.  If the fine likelihood is
pointwise `β`-close to a likelihood representable on compressed state and both
evidence masses stay above `ζ`, then the pushed fine posterior is within
`2β/ζ` in L1 of the posterior computed directly on compressed state. -/
theorem condition_pushforward_approximately_commutes
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z) (b : RationalBelief Ω)
    (L : Ω → ℚ) (Lbar : Z → ℚ)
    (hL : ∀ ω, 0 ≤ L ω) (hLbar : ∀ z, 0 ≤ Lbar z)
    (β ζ : ℚ) (hβ : 0 ≤ β)
    (hclose : ∀ ω, |L ω - Lbar (φ ω)| ≤ β)
    (hζ : 0 < ζ)
    (hfine : ζ ≤ evidenceMass b L)
    (hcoarse : ζ ≤ evidenceMass (pushforwardBelief φ b) Lbar) :
    beliefL1Distance
      (pushforwardBelief φ
        (conditionByWeight b L hL (lt_of_lt_of_le hζ hfine)))
      (conditionByWeight (pushforwardBelief φ b) Lbar hLbar
        (lt_of_lt_of_le hζ hcoarse))
      ≤ 2 * β / ζ := by
  let M : Ω → ℚ := fun ω => Lbar (φ ω)
  have hM : ∀ ω, 0 ≤ M ω := fun ω => hLbar (φ ω)
  have hMmass : evidenceMass b M =
      evidenceMass (pushforwardBelief φ b) Lbar := by
    exact (evidenceMass_pushforward φ b Lbar).symm
  have hMlower : ζ ≤ evidenceMass b M := by
    rw [hMmass]
    exact hcoarse
  let bL := conditionByWeight b L hL (lt_of_lt_of_le hζ hfine)
  let bM := conditionByWeight b M hM (lt_of_lt_of_le hζ hMlower)
  have hstable : beliefL1Distance bL bM ≤ 2 * β / ζ := by
    simpa [bL, bM, M] using
      conditionByWeight_l1_stability_likelihood b L M hL hM β ζ hβ hclose
        hζ hfine hMlower
  have hpush : beliefL1Distance (pushforwardBelief φ bL)
      (pushforwardBelief φ bM) ≤ 2 * β / ζ :=
    le_trans (beliefL1_pushforward_contract φ bL bM) hstable
  have hcomm := condition_pushforward_commutes φ b Lbar hLbar
    (lt_of_lt_of_le hζ hMlower)
  dsimp [M] at hcomm
  have hcoarsePos : 0 < evidenceMass (pushforwardBelief φ b) Lbar :=
    lt_of_lt_of_le hζ hcoarse
  have hEq : pushforwardBelief φ bM =
      conditionByWeight (pushforwardBelief φ b) Lbar hLbar hcoarsePos := by
    simpa [bM, M] using hcomm
  rw [hEq] at hpush
  exact hpush

end Komorebi.AVOC
