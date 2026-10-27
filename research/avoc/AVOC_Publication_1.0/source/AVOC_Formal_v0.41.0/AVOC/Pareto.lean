import AVOC.Control
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

/-- `a` weakly dominates `b` when it is no worse on every declared AVOC
metric: gains are larger and burdens/risks are smaller. -/
def WeaklyDominates (a b : ActionMetrics) : Prop :=
  b.verifiedGain ≤ a.verifiedGain ∧
  b.falsificationGain ≤ a.falsificationGain ∧
  b.reuseGain ≤ a.reuseGain ∧
  a.debtAdded ≤ b.debtAdded ∧
  a.cost ≤ b.cost ∧
  a.falseAdmissionRisk ≤ b.falseAdmissionRisk

/-- Strict Pareto dominance: weak dominance plus strict improvement on at least
one declared coordinate. -/
def StrictlyDominates (a b : ActionMetrics) : Prop :=
  WeaklyDominates a b ∧
    (b.verifiedGain < a.verifiedGain ∨
     b.falsificationGain < a.falsificationGain ∨
     b.reuseGain < a.reuseGain ∨
     a.debtAdded < b.debtAdded ∨
     a.cost < b.cost ∨
     a.falseAdmissionRisk < b.falseAdmissionRisk)

/-- Weak dominance is reflexive. -/
@[refl] theorem weaklyDominates_refl (a : ActionMetrics) : WeaklyDominates a a := by
  exact ⟨le_rfl, le_rfl, le_rfl, le_rfl, le_rfl, le_rfl⟩

/-- Weak dominance is transitive. -/
@[trans] theorem weaklyDominates_trans {a b c : ActionMetrics}
    (hab : WeaklyDominates a b) (hbc : WeaklyDominates b c) :
    WeaklyDominates a c := by
  rcases hab with ⟨hv1, hf1, hr1, hd1, hc1, hR1⟩
  rcases hbc with ⟨hv2, hf2, hr2, hd2, hc2, hR2⟩
  exact ⟨le_trans hv2 hv1, le_trans hf2 hf1, le_trans hr2 hr1,
    le_trans hd1 hd2, le_trans hc1 hc2, le_trans hR1 hR2⟩

/-- Every nonnegative AVOC scalarization respects weak Pareto dominance. -/
theorem score_mono_of_weaklyDominates
    (wF wReuse wDebt wCost wRisk : ℝ) (a b : ActionMetrics)
    (hwF : 0 ≤ wF) (hwReuse : 0 ≤ wReuse) (hwDebt : 0 ≤ wDebt)
    (hwCost : 0 ≤ wCost) (hwRisk : 0 ≤ wRisk)
    (hdom : WeaklyDominates a b) :
    actionScore wF wReuse wDebt wCost wRisk b ≤
      actionScore wF wReuse wDebt wCost wRisk a := by
  rcases hdom with ⟨hv, hf, hr, hd, hc, hR⟩
  exact score_mono_of_dominance wF wReuse wDebt wCost wRisk b a
    hwF hwReuse hwDebt hwCost hwRisk hv hf hr hd hc hR

/-- With strictly positive weights on every non-base coordinate, strict Pareto
dominance strictly improves the scalarized score. The base verified-gain
coordinate has coefficient one and is therefore already strictly positive. -/
theorem score_strict_of_strictlyDominates
    (wF wReuse wDebt wCost wRisk : ℝ) (a b : ActionMetrics)
    (hwF : 0 < wF) (hwReuse : 0 < wReuse) (hwDebt : 0 < wDebt)
    (hwCost : 0 < wCost) (hwRisk : 0 < wRisk)
    (hdom : StrictlyDominates a b) :
    actionScore wF wReuse wDebt wCost wRisk b <
      actionScore wF wReuse wDebt wCost wRisk a := by
  rcases hdom with ⟨hweak, hstrict⟩
  rcases hweak with ⟨hv, hf, hr, hd, hc, hR⟩
  unfold actionScore
  rcases hstrict with hv' | hf' | hr' | hd' | hc' | hR'
  · have hF := mul_le_mul_of_nonneg_left hf (le_of_lt hwF)
    have hReuse := mul_le_mul_of_nonneg_left hr (le_of_lt hwReuse)
    have hDebt := mul_le_mul_of_nonneg_left hd (le_of_lt hwDebt)
    have hCost := mul_le_mul_of_nonneg_left hc (le_of_lt hwCost)
    have hRisk := mul_le_mul_of_nonneg_left hR (le_of_lt hwRisk)
    linarith
  · have hF := mul_lt_mul_of_pos_left hf' hwF
    have hReuse := mul_le_mul_of_nonneg_left hr (le_of_lt hwReuse)
    have hDebt := mul_le_mul_of_nonneg_left hd (le_of_lt hwDebt)
    have hCost := mul_le_mul_of_nonneg_left hc (le_of_lt hwCost)
    have hRisk := mul_le_mul_of_nonneg_left hR (le_of_lt hwRisk)
    linarith
  · have hF := mul_le_mul_of_nonneg_left hf (le_of_lt hwF)
    have hReuse := mul_lt_mul_of_pos_left hr' hwReuse
    have hDebt := mul_le_mul_of_nonneg_left hd (le_of_lt hwDebt)
    have hCost := mul_le_mul_of_nonneg_left hc (le_of_lt hwCost)
    have hRisk := mul_le_mul_of_nonneg_left hR (le_of_lt hwRisk)
    linarith
  · have hF := mul_le_mul_of_nonneg_left hf (le_of_lt hwF)
    have hReuse := mul_le_mul_of_nonneg_left hr (le_of_lt hwReuse)
    have hDebt := mul_lt_mul_of_pos_left hd' hwDebt
    have hCost := mul_le_mul_of_nonneg_left hc (le_of_lt hwCost)
    have hRisk := mul_le_mul_of_nonneg_left hR (le_of_lt hwRisk)
    linarith
  · have hF := mul_le_mul_of_nonneg_left hf (le_of_lt hwF)
    have hReuse := mul_le_mul_of_nonneg_left hr (le_of_lt hwReuse)
    have hDebt := mul_le_mul_of_nonneg_left hd (le_of_lt hwDebt)
    have hCost := mul_lt_mul_of_pos_left hc' hwCost
    have hRisk := mul_le_mul_of_nonneg_left hR (le_of_lt hwRisk)
    linarith
  · have hF := mul_le_mul_of_nonneg_left hf (le_of_lt hwF)
    have hReuse := mul_le_mul_of_nonneg_left hr (le_of_lt hwReuse)
    have hDebt := mul_le_mul_of_nonneg_left hd (le_of_lt hwDebt)
    have hCost := mul_le_mul_of_nonneg_left hc (le_of_lt hwCost)
    have hRisk := mul_lt_mul_of_pos_left hR' hwRisk
    linarith

/-- Pareto-maximality inside a finite action set. -/
def ParetoMaximal {A : Type*}
    (actions : Finset A) (metrics : A → ActionMetrics) (a : A) : Prop :=
  a ∈ actions ∧ ¬ ∃ b ∈ actions, StrictlyDominates (metrics b) (metrics a)

/-- Any optimizer of a strictly positive AVOC scalarization is Pareto maximal.
Thus dominated actions can never be uniquely required by such an optimizer. -/
theorem positive_score_optimizer_is_paretoMaximal
    {A : Type*} [DecidableEq A]
    (actions : Finset A) (metrics : A → ActionMetrics) (chosen : A)
    (wF wReuse wDebt wCost wRisk : ℝ)
    (hwF : 0 < wF) (hwReuse : 0 < wReuse) (hwDebt : 0 < wDebt)
    (hwCost : 0 < wCost) (hwRisk : 0 < wRisk)
    (hopt : OptimalOn actions
      (fun a => actionScore wF wReuse wDebt wCost wRisk (metrics a)) chosen) :
    ParetoMaximal actions metrics chosen := by
  refine ⟨hopt.1, ?_⟩
  rintro ⟨b, hb, hdom⟩
  have hle := hopt.2 b hb
  have hlt := score_strict_of_strictlyDominates
    wF wReuse wDebt wCost wRisk (metrics b) (metrics chosen)
    hwF hwReuse hwDebt hwCost hwRisk hdom
  exact (not_lt_of_ge hle) hlt

/-- Every nonempty finite action family has a Pareto-maximal member.  Proof:
maximize the equal-positive-weight score and use the preceding theorem. -/
theorem finite_pareto_frontier_nonempty
    {A : Type*} [DecidableEq A]
    (actions : Finset A) (metrics : A → ActionMetrics)
    (hne : actions.Nonempty) :
    ∃ a, ParetoMaximal actions metrics a := by
  obtain ⟨chosen, hopt⟩ := finite_epistemic_scheduler_exists actions
    (fun a => actionScore 1 1 1 1 1 (metrics a)) hne
  refine ⟨chosen, positive_score_optimizer_is_paretoMaximal
    actions metrics chosen 1 1 1 1 1 ?_ ?_ ?_ ?_ ?_ hopt⟩ <;> norm_num

/-- Weak Pareto improvement preserves hard feasibility because AVOC dominance
can only lower the cost and false-admission-risk coordinates. -/
theorem weakDominance_preserves_feasibility
    (budget riskCap : ℝ) (better worse : ActionMetrics)
    (hdom : WeaklyDominates better worse)
    (hfeas : FeasibleMetrics budget riskCap worse) :
    FeasibleMetrics budget riskCap better := by
  rcases hdom with ⟨_, _, _, _, hcost, hrisk⟩
  exact ⟨le_trans hcost hfeas.1, le_trans hrisk hfeas.2⟩

/-- A strictly dominated feasible action cannot be optimal for a strictly
positive AVOC scalarization. -/
theorem strictly_dominated_feasible_action_not_optimal
    {A : Type*} [DecidableEq A]
    (actions : Finset A) (metrics : A → ActionMetrics)
    (worse better : A)
    (wF wReuse wDebt wCost wRisk : ℝ)
    (hwF : 0 < wF) (hwReuse : 0 < wReuse) (hwDebt : 0 < wDebt)
    (hwCost : 0 < wCost) (hwRisk : 0 < wRisk)
    (hbetter : better ∈ actions)
    (hdom : StrictlyDominates (metrics better) (metrics worse)) :
    ¬ OptimalOn actions
      (fun a => actionScore wF wReuse wDebt wCost wRisk (metrics a)) worse := by
  intro hopt
  have hle := hopt.2 better hbetter
  have hlt := score_strict_of_strictlyDominates
    wF wReuse wDebt wCost wRisk (metrics better) (metrics worse)
    hwF hwReuse hwDebt hwCost hwRisk hdom
  exact (not_lt_of_ge hle) hlt

end Komorebi.AVOC
