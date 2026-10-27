import AVOC.OpenWorld
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC

universe u v w

/-- Evidence mass can be computed before or after deterministic compression
when the likelihood depends only on the compressed state. -/
theorem evidenceMass_pushforward
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z) (b : RationalBelief Ω) (Lbar : Z → ℚ) :
    evidenceMass (pushforwardBelief φ b) Lbar =
      evidenceMass b (fun ω => Lbar (φ ω)) := by
  unfold evidenceMass
  exact sum_pushforward_mul φ b.prob Lbar

/-- Conditioning commutes with deterministic compression whenever the
likelihood is constant on representation fibers. -/
theorem condition_pushforward_commutes
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z) (b : RationalBelief Ω) (Lbar : Z → ℚ)
    (hLbar : ∀ z, 0 ≤ Lbar z)
    (hpos : 0 < evidenceMass b (fun ω => Lbar (φ ω))) :
    let hL : ∀ ω, 0 ≤ Lbar (φ ω) := fun ω => hLbar (φ ω)
    let hposCoarse : 0 < evidenceMass (pushforwardBelief φ b) Lbar := by
      rw [evidenceMass_pushforward φ b Lbar]
      exact hpos
    pushforwardBelief φ
        (conditionByWeight b (fun ω => Lbar (φ ω)) hL hpos) =
      conditionByWeight (pushforwardBelief φ b) Lbar hLbar hposCoarse := by
  dsimp
  let M := evidenceMass b (fun ω => Lbar (φ ω))
  have hmass : evidenceMass (pushforwardBelief φ b) Lbar = M := by
    exact evidenceMass_pushforward φ b Lbar
  apply RationalBelief.ext
  intro z
  change
    (∑ ω ∈ Finset.univ.filter (fun ω : Ω => φ ω = z),
      (b.prob ω * Lbar (φ ω)) / M) =
      (pushforwardRow φ b.prob z * Lbar z) /
        evidenceMass (pushforwardBelief φ b) Lbar
  rw [hmass]
  simp only [div_eq_mul_inv]
  unfold pushforwardRow
  rw [Finset.sum_mul, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro ω hω
  have hφ : φ ω = z := (Finset.mem_filter.mp hω).2
  rw [hφ]

/-- Predictive probability itself commutes with deterministic compression when
an observation channel factors through the compressed state. -/
theorem predictiveProb_pushforward
    {Ω : Type u} {Z : Type v} {O : Type w}
    [Fintype Ω] [Fintype Z] [Fintype O] [DecidableEq Z]
    (φ : Ω → Z) (b : RationalBelief Ω)
    (E : RationalChannel Ω O) (Ebar : RationalChannel Z O)
    (hfactor : ∀ ω o, E.prob ω o = Ebar.prob (φ ω) o)
    (o : O) :
    predictiveProb b E o =
      predictiveProb (pushforwardBelief φ b) Ebar o := by
  unfold predictiveProb
  calc
    (∑ ω : Ω, b.prob ω * E.prob ω o)
        = ∑ ω : Ω, b.prob ω * Ebar.prob (φ ω) o := by
            apply Finset.sum_congr rfl
            intro ω hω
            rw [hfactor]
    _ = ∑ z : Z, pushforwardRow φ b.prob z * Ebar.prob z o := by
          exact (sum_pushforward_mul φ b.prob (fun z => Ebar.prob z o)).symm
    _ = ∑ z : Z, (pushforwardBelief φ b).prob z * Ebar.prob z o := rfl

/-- Exact Bayes-compression commuting square for a channel that factors through
`φ`. -/
theorem bayesUpdate_pushforward_commutes
    {Ω : Type u} {Z : Type v} {O : Type w}
    [Fintype Ω] [Fintype Z] [Fintype O] [DecidableEq Z]
    (φ : Ω → Z) (b : RationalBelief Ω)
    (E : RationalChannel Ω O) (Ebar : RationalChannel Z O)
    (hfactor : ∀ ω o, E.prob ω o = Ebar.prob (φ ω) o)
    (o : O) (hpos : 0 < predictiveProb b E o) :
    let hposCoarse : 0 < predictiveProb (pushforwardBelief φ b) Ebar o := by
      rw [← predictiveProb_pushforward φ b E Ebar hfactor o]
      exact hpos
    pushforwardBelief φ (bayesUpdate b E o hpos) =
      bayesUpdate (pushforwardBelief φ b) Ebar o hposCoarse := by
  dsimp
  have hmass : predictiveProb b E o =
      predictiveProb (pushforwardBelief φ b) Ebar o :=
    predictiveProb_pushforward φ b E Ebar hfactor o
  apply RationalBelief.ext
  intro z
  change
    (∑ ω ∈ Finset.univ.filter (fun ω : Ω => φ ω = z),
      (b.prob ω * E.prob ω o) / predictiveProb b E o) =
      (pushforwardRow φ b.prob z * Ebar.prob z o) /
        predictiveProb (pushforwardBelief φ b) Ebar o
  rw [← hmass]
  simp only [div_eq_mul_inv]
  unfold pushforwardRow
  rw [Finset.sum_mul, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro ω hω
  have hφ : φ ω = z := (Finset.mem_filter.mp hω).2
  rw [hfactor, hφ]

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v

/-- A likelihood can be represented exactly on compressed state iff it is
constant on every compression fiber. -/
theorem likelihood_factors_iff_fiber_constant
    {Ω : Type u} {Z : Type v}
    (φ : Ω → Z) (L : Ω → ℚ) :
    (∃ Lbar : Z → ℚ, ∀ ω, Lbar (φ ω) = L ω) ↔
      ∀ x y, φ x = φ y → L x = L y := by
  constructor
  · rintro ⟨Lbar, hLbar⟩ x y hxy
    calc
      L x = Lbar (φ x) := (hLbar x).symm
      _ = Lbar (φ y) := congrArg Lbar hxy
      _ = L y := hLbar y
  · intro h
    have hs : TaskSufficient φ L := by
      apply fiber_refinement_implies_sufficient
      intro x y hxy
      exact h x y hxy
    exact hs

/-- One within-fiber likelihood disagreement certifies that no exact coarse
likelihood exists. -/
theorem likelihood_collision_obstructs_factorization
    {Ω : Type u} {Z : Type v}
    (φ : Ω → Z) (L : Ω → ℚ) {x y : Ω}
    (hφ : φ x = φ y) (hL : L x ≠ L y) :
    ¬ ∃ Lbar : Z → ℚ, ∀ ω, Lbar (φ ω) = L ω := by
  intro hfactor
  exact hL ((likelihood_factors_iff_fiber_constant φ L).1 hfactor x y hφ)

end Komorebi.AVOC
