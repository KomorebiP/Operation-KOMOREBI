import AVOC.Stochastic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

universe u v w z

/-- A finite rational stochastic channel. -/
structure RationalChannel (X : Type u) (Y : Type v) [Fintype Y] where
  prob : X → Y → ℚ
  nonneg : ∀ x y, 0 ≤ prob x y
  sum_one : ∀ x, ∑ y, prob x y = 1

@[ext] theorem RationalChannel.ext
    {X : Type u} {Y : Type v} [Fintype Y]
    (E F : RationalChannel X Y)
    (h : ∀ x y, E.prob x y = F.prob x y) : E = F := by
  cases E with
  | mk ep en es =>
    cases F with
    | mk fp fn fs =>
      have hp : ep = fp := by
        funext x y
        exact h x y
      cases hp
      rfl

/-- Composition of finite rational channels. -/
def composeChannel
    {X : Type u} {Y : Type v} {Z : Type w}
    [Fintype Y] [Fintype Z]
    (E : RationalChannel X Y) (K : RationalChannel Y Z) :
    RationalChannel X Z where
  prob x z := ∑ y, E.prob x y * K.prob y z
  nonneg := by
    intro x z
    apply Finset.sum_nonneg
    intro y hy
    exact mul_nonneg (E.nonneg x y) (K.nonneg y z)
  sum_one := by
    intro x
    calc
      (∑ z, ∑ y, E.prob x y * K.prob y z)
          = ∑ y, ∑ z, E.prob x y * K.prob y z := by rw [Finset.sum_comm]
      _ = ∑ y, E.prob x y := by
        apply Finset.sum_congr rfl
        intro y hy
        rw [← Finset.mul_sum, K.sum_one]
        simp
      _ = 1 := E.sum_one x

/-- Contribution/value of taking action `a` after receiving signal `x`, before
normalizing by the probability of that signal. -/
def signalActionScore
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w}
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (x : O) (a : A) : ℚ :=
  ∑ ω, prior ω * E.prob ω x * utility ω a

/-- Finite decision value after a stochastic observation channel, expressed as
sum of unnormalized posterior action scores. -/
def stochasticDecisionValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w}
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (policy : O → A) : ℚ :=
  ∑ o, signalActionScore prior utility E o (policy o)

/-- Signal score after a garbling is the garbling-weighted sum of fine-signal
scores. -/
theorem signalActionScore_compose
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z}
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse)
    (y : Coarse) (a : A) :
    signalActionScore prior utility (composeChannel E K) y a =
      ∑ x, K.prob x y * signalActionScore prior utility E x a := by
  unfold signalActionScore
  change (∑ ω, prior ω * (∑ x, E.prob ω x * K.prob x y) * utility ω a) =
    ∑ x, K.prob x y * ∑ ω, prior ω * E.prob ω x * utility ω a
  calc
    (∑ ω, prior ω * (∑ x, E.prob ω x * K.prob x y) * utility ω a)
        = ∑ ω, ∑ x, (prior ω * (E.prob ω x * K.prob x y)) * utility ω a := by
          apply Finset.sum_congr rfl
          intro ω hω
          rw [Finset.mul_sum, Finset.sum_mul]
    _ = ∑ x, ∑ ω, (prior ω * (E.prob ω x * K.prob x y)) * utility ω a := by
          rw [Finset.sum_comm]
    _ = ∑ x, K.prob x y * ∑ ω, prior ω * E.prob ω x * utility ω a := by
          apply Finset.sum_congr rfl
          intro x hx
          rw [Finset.mul_sum]
          apply Finset.sum_congr rfl
          intro ω hω
          ring

/-- A deterministic action can be selected signal-by-signal to maximize the
unnormalized posterior action score. -/
theorem signalwise_max_policy_exists
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) :
    ∃ policy : O → A,
      ∀ x a, signalActionScore prior utility E x a ≤
        signalActionScore prior utility E x (policy x) := by
  classical
  have hpoint : ∀ x : O, ∃ a : A, ∀ b : A,
      signalActionScore prior utility E x b ≤ signalActionScore prior utility E x a := by
    intro x
    obtain ⟨a, ha, hmax⟩ := Finset.exists_max_image
      (Finset.univ : Finset A) (signalActionScore prior utility E x)
      (Finset.univ_nonempty)
    exact ⟨a, fun b => hmax b (Finset.mem_univ b)⟩
  choose policy hpolicy using hpoint
  exact ⟨policy, hpolicy⟩

/-- A stochastic garbling followed by any coarse policy is bounded, signal by
signal, by a suitable deterministic policy acting directly on the fine signal. -/
theorem garbled_policy_score_le_fine_policy
    {Fine : Type u} [Fintype Fine]
    {Coarse : Type v} [Fintype Coarse]
    {A : Type w} [Fintype A] [Nonempty A]
    (K : RationalChannel Fine Coarse)
    (score : Fine → A → ℚ) (coarsePolicy : Coarse → A) :
    ∃ finePolicy : Fine → A,
      (∑ x, ∑ y, K.prob x y * score x (coarsePolicy y)) ≤
        ∑ x, score x (finePolicy x) := by
  classical
  have hpoint : ∀ x : Fine, ∃ a : A, ∀ b : A, score x b ≤ score x a := by
    intro x
    obtain ⟨a, ha, hmax⟩ := Finset.exists_max_image
      (Finset.univ : Finset A) (score x) (Finset.univ_nonempty)
    exact ⟨a, fun b => hmax b (Finset.mem_univ b)⟩
  choose finePolicy hmax using hpoint
  refine ⟨finePolicy, ?_⟩
  apply Finset.sum_le_sum
  intro x hx
  calc
    (∑ y, K.prob x y * score x (coarsePolicy y))
        ≤ ∑ y, K.prob x y * score x (finePolicy x) := by
          apply Finset.sum_le_sum
          intro y hy
          exact mul_le_mul_of_nonneg_left (hmax x (coarsePolicy y)) (K.nonneg x y)
    _ = score x (finePolicy x) := by
      rw [← Finset.sum_mul, K.sum_one]
      simp

/-- Decision value after channel composition equals the garbling-weighted sum of
fine-signal action scores. -/
theorem stochasticDecisionValue_compose_eq_garbled_scores
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z}
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse)
    (policy : Coarse → A) :
    stochasticDecisionValue prior utility (composeChannel E K) policy =
      ∑ x, ∑ y, K.prob x y * signalActionScore prior utility E x (policy y) := by
  unfold stochasticDecisionValue
  simp_rw [signalActionScore_compose prior utility E K]
  rw [Finset.sum_comm]

/-- Stochastic Blackwell theorem in finite rational form: every deterministic
policy on a garbled channel is weakly dominated by some deterministic policy
on the original fine channel. -/
theorem stochastic_blackwell_policy_dominance
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse)
    (coarsePolicy : Coarse → A) :
    ∃ finePolicy : Fine → A,
      stochasticDecisionValue prior utility (composeChannel E K) coarsePolicy ≤
        stochasticDecisionValue prior utility E finePolicy := by
  obtain ⟨finePolicy, hscore⟩ := garbled_policy_score_le_fine_policy K
    (signalActionScore prior utility E) coarsePolicy
  refine ⟨finePolicy, ?_⟩
  rw [stochasticDecisionValue_compose_eq_garbled_scores prior utility E K coarsePolicy]
  exact hscore

/-- Best deterministic decision value for a stochastic finite channel. -/
noncomputable def bestStochasticDecisionValue
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) : ℚ := by
  classical
  let vals : Finset ℚ := (Finset.univ : Finset (O → A)).image
    (stochasticDecisionValue prior utility E)
  have hne : vals.Nonempty := by
    let a0 : A := Classical.choice (inferInstance : Nonempty A)
    let p0 : O → A := fun _ => a0
    exact ⟨stochasticDecisionValue prior utility E p0,
      Finset.mem_image.mpr ⟨p0, Finset.mem_univ _, rfl⟩⟩
  exact vals.max' hne

/-- Every policy is bounded by the best stochastic-channel decision value. -/
theorem stochasticDecisionValue_le_best
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (policy : O → A) :
    stochasticDecisionValue prior utility E policy ≤
      bestStochasticDecisionValue prior utility E := by
  classical
  unfold bestStochasticDecisionValue
  let vals : Finset ℚ := (Finset.univ : Finset (O → A)).image
    (stochasticDecisionValue prior utility E)
  have hne : vals.Nonempty := by
    let a0 : A := Classical.choice (inferInstance : Nonempty A)
    let p0 : O → A := fun _ => a0
    exact ⟨stochasticDecisionValue prior utility E p0,
      Finset.mem_image.mpr ⟨p0, Finset.mem_univ _, rfl⟩⟩
  exact Finset.le_max' vals _
    (Finset.mem_image.mpr ⟨policy, Finset.mem_univ _, rfl⟩)

/-- A best policy exists for every finite stochastic observation channel. -/
theorem best_stochastic_policy_exists
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) :
    ∃ policy : O → A,
      stochasticDecisionValue prior utility E policy =
        bestStochasticDecisionValue prior utility E := by
  classical
  let vals : Finset ℚ := (Finset.univ : Finset (O → A)).image
    (stochasticDecisionValue prior utility E)
  have hne : vals.Nonempty := by
    let a0 : A := Classical.choice (inferInstance : Nonempty A)
    let p0 : O → A := fun _ => a0
    exact ⟨stochasticDecisionValue prior utility E p0,
      Finset.mem_image.mpr ⟨p0, Finset.mem_univ _, rfl⟩⟩
  have hm : vals.max' hne ∈ vals := Finset.max'_mem vals hne
  rcases Finset.mem_image.mp hm with ⟨policy, hp, hv⟩
  refine ⟨policy, ?_⟩
  unfold bestStochasticDecisionValue
  change stochasticDecisionValue prior utility E policy = vals.max' hne
  exact hv

/-- Full finite rational Blackwell monotonicity under stochastic garbling. -/
theorem stochastic_blackwell_monotonicity
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse) :
    bestStochasticDecisionValue prior utility (composeChannel E K) ≤
      bestStochasticDecisionValue prior utility E := by
  obtain ⟨coarsePolicy, hcoarse⟩ :=
    best_stochastic_policy_exists prior utility (composeChannel E K)
  obtain ⟨finePolicy, hdom⟩ :=
    stochastic_blackwell_policy_dominance prior utility E K coarsePolicy
  rw [← hcoarse]
  exact hdom.trans (stochasticDecisionValue_le_best prior utility E finePolicy)

/-- Blackwell-plus-cost pruning rule for stochastic experiments. -/
theorem stochastic_blackwell_cost_dominance
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse)
    {fineCost coarseCost : ℚ} (hcost : fineCost ≤ coarseCost) :
    netExperimentValue
        (bestStochasticDecisionValue prior utility (composeChannel E K)) coarseCost ≤
      netExperimentValue (bestStochasticDecisionValue prior utility E) fineCost := by
  unfold netExperimentValue
  have hv := stochastic_blackwell_monotonicity prior utility E K
  linarith



/-- Identity observation channel. -/
def identityChannel (X : Type u) [Fintype X] [DecidableEq X] : RationalChannel X X where
  prob x y := if x = y then 1 else 0
  nonneg := by
    intro x y
    split <;> norm_num
  sum_one := by
    intro x
    simp

/-- Postcomposing with the identity channel changes no experiment. -/
theorem compose_identityChannel
    {X : Type u} {Y : Type v} [Fintype Y] [DecidableEq Y]
    (E : RationalChannel X Y) :
    composeChannel E (identityChannel Y) = E := by
  apply RationalChannel.ext
  intro x y
  change (∑ y', E.prob x y' * (if y' = y then 1 else 0)) = E.prob x y
  simp

/-- Channel composition is associative. -/
theorem composeChannel_assoc
    {W : Type u} {X : Type v} {Y : Type w} {Z : Type z}
    [Fintype X] [Fintype Y] [Fintype Z]
    (E : RationalChannel W X) (K : RationalChannel X Y)
    (L : RationalChannel Y Z) :
    composeChannel (composeChannel E K) L =
      composeChannel E (composeChannel K L) := by
  apply RationalChannel.ext
  intro w0 z0
  change (∑ y, (∑ x, E.prob w0 x * K.prob x y) * L.prob y z0) =
    ∑ x, E.prob w0 x * (∑ y, K.prob x y * L.prob y z0)
  simp_rw [Finset.sum_mul, Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro x hx
  apply Finset.sum_congr rfl
  intro y hy
  ring

/-- Blackwell refinement/order: `fine` is at least as informative as `coarse`
when `coarse` is obtained by a stochastic garbling of `fine`. -/
def BlackwellRefines
    {Ω : Type u} {Fine : Type v} {Coarse : Type w}
    [Fintype Fine] [Fintype Coarse]
    (fine : RationalChannel Ω Fine) (coarse : RationalChannel Ω Coarse) : Prop :=
  ∃ K : RationalChannel Fine Coarse, composeChannel fine K = coarse

/-- Blackwell refinement is reflexive. -/
theorem blackwellRefines_refl
    {Ω : Type u} {O : Type v} [Fintype O] [DecidableEq O]
    (E : RationalChannel Ω O) : BlackwellRefines E E := by
  exact ⟨identityChannel O, compose_identityChannel E⟩

/-- Blackwell refinement is transitive. -/
theorem blackwellRefines_trans
    {Ω : Type u} {A : Type v} {B : Type w} {C : Type z}
    [Fintype A] [Fintype B] [Fintype C]
    {E : RationalChannel Ω A} {F : RationalChannel Ω B} {G : RationalChannel Ω C}
    (hEF : BlackwellRefines E F) (hFG : BlackwellRefines F G) :
    BlackwellRefines E G := by
  rcases hEF with ⟨K, rfl⟩
  rcases hFG with ⟨L, rfl⟩
  refine ⟨composeChannel K L, ?_⟩
  exact (composeChannel_assoc E K L).symm

/-- Optimal decision value is monotone along the Blackwell information order. -/
theorem bestValue_mono_blackwell
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    {fine : RationalChannel Ω Fine} {coarse : RationalChannel Ω Coarse}
    (h : BlackwellRefines fine coarse) :
    bestStochasticDecisionValue prior utility coarse ≤
      bestStochasticDecisionValue prior utility fine := by
  rcases h with ⟨K, rfl⟩
  exact stochastic_blackwell_monotonicity prior utility fine K

/-- The completely uninformative one-signal experiment. -/
def uninformativeChannel (Ω : Type u) : RationalChannel Ω Unit where
  prob _ _ := 1
  nonneg := by intro; norm_num
  sum_one := by intro; simp

/-- Forget every observation by mapping it stochastically to the unique unit
signal. -/
def forgetChannel (O : Type v) : RationalChannel O Unit where
  prob _ _ := 1
  nonneg := by intro; norm_num
  sum_one := by intro; simp

/-- Forgetting the output of any certified channel yields the uninformative
channel exactly. -/
theorem compose_forget_prob_eq_uninformative
    {Ω : Type u} {O : Type v} [Fintype O]
    (E : RationalChannel Ω O) (ω : Ω) (u0 : Unit) :
    (composeChannel E (forgetChannel O)).prob ω u0 =
      (uninformativeChannel Ω).prob ω u0 := by
  change (∑ o, E.prob ω o * 1) = 1
  simpa using E.sum_one ω


/-- Forgetting any channel gives exactly the uninformative experiment. -/
theorem compose_forget_eq_uninformative
    {Ω : Type u} {O : Type v} [Fintype O]
    (E : RationalChannel Ω O) :
    composeChannel E (forgetChannel O) = uninformativeChannel Ω := by
  apply RationalChannel.ext
  intro ω u0
  exact compose_forget_prob_eq_uninformative E ω u0

/-- The uninformative experiment is a bottom element of the Blackwell order:
every certified observation channel refines it. -/
theorem blackwellRefines_uninformative
    {Ω : Type u} {O : Type v} [Fintype O]
    (E : RationalChannel Ω O) :
    BlackwellRefines E (uninformativeChannel Ω) := by
  exact ⟨forgetChannel O, compose_forget_eq_uninformative E⟩

/-- Every observation channel weakly improves optimal decision value over the
uninformative baseline, because forgetting is a stochastic garbling. -/
theorem information_never_hurts_without_cost
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) :
    bestStochasticDecisionValue prior utility (uninformativeChannel Ω) ≤
      bestStochasticDecisionValue prior utility E := by
  have hblack := stochastic_blackwell_monotonicity prior utility E (forgetChannel O)
  have hchan : composeChannel E (forgetChannel O) = uninformativeChannel Ω :=
    compose_forget_eq_uninformative E
  rw [hchan] at hblack
  exact hblack

/-- Decision-theoretic value of information: optimal value with an experiment
minus optimal value with no informative observation. -/
noncomputable def valueOfInformation
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) : ℚ :=
  bestStochasticDecisionValue prior utility E -
    bestStochasticDecisionValue prior utility (uninformativeChannel Ω)

/-- Information has nonnegative decision value when acquisition is free. -/
theorem valueOfInformation_nonneg
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) :
    0 ≤ valueOfInformation prior utility E := by
  unfold valueOfInformation
  have h := information_never_hurts_without_cost prior utility E
  linarith

/-- Value of information is monotone under Blackwell garbling. -/
theorem valueOfInformation_mono_under_garbling
    {Ω : Type u} [Fintype Ω]
    {Fine : Type v} [Fintype Fine]
    {Coarse : Type w} [Fintype Coarse]
    {A : Type z} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω Fine) (K : RationalChannel Fine Coarse) :
    valueOfInformation prior utility (composeChannel E K) ≤
      valueOfInformation prior utility E := by
  unfold valueOfInformation
  have h := stochastic_blackwell_monotonicity prior utility E K
  linarith

/-- Net incremental value of acquiring an experiment at explicit cost. -/
noncomputable def netValueOfInformation
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (cost : ℚ) : ℚ :=
  valueOfInformation prior utility E - cost

/-- Exact acquisition threshold: an experiment has positive net information
value exactly when its decision value of information exceeds its cost. -/
theorem netValueOfInformation_positive_iff
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (cost : ℚ) :
    0 < netValueOfInformation prior utility E cost ↔
      cost < valueOfInformation prior utility E := by
  unfold netValueOfInformation
  constructor <;> intro h <;> linarith

/-- If information value does not exceed acquisition cost, acquiring the
experiment has nonpositive marginal value; the zero-value stop action weakly
dominates acquisition. -/
theorem stop_dominates_acquisition_when_cost_exceeds_voi
    {Ω : Type u} [Fintype Ω]
    {O : Type v} [Fintype O]
    {A : Type w} [Fintype A] [Nonempty A]
    (prior : Ω → ℚ) (utility : Ω → A → ℚ)
    (E : RationalChannel Ω O) (cost : ℚ)
    (h : valueOfInformation prior utility E ≤ cost) :
    netValueOfInformation prior utility E cost ≤ 0 := by
  unfold netValueOfInformation
  linarith

end Komorebi.AVOC
