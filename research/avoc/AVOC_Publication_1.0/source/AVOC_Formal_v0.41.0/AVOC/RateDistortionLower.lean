import AVOC.ApproximateStochastic
import Mathlib.Data.Finset.Card
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC

universe u v

/-- A compressed value representation is `η`-accurate when every raw state is
within `η` of the value assigned to its code. -/
def ValueApproximation
    {S : Type u} {Z : Type v}
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ) : Prop :=
  ∀ s, |V s - Vbar (φ s)| ≤ η

/-- Any two states whose values differ by more than `2η` must remain distinct
under every `η`-accurate value representation. -/
theorem value_gap_forces_distinction
    {S : Type u} {Z : Type v}
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ)
    (happrox : ValueApproximation φ V Vbar η)
    {s t : S}
    (hgap : 2 * η < |V s - V t|) :
    φ s ≠ φ t := by
  intro heq
  have hs := happrox s
  have ht := happrox t
  have htri : |V s - V t| ≤
      |V s - Vbar (φ s)| + |Vbar (φ t) - V t| := by
    calc
      |V s - V t|
          = |(V s - Vbar (φ s)) + (Vbar (φ t) - V t)| := by
              rw [heq]
              ring_nf
      _ ≤ |V s - Vbar (φ s)| + |Vbar (φ t) - V t| := abs_add_le _ _
  have ht' : |Vbar (φ t) - V t| ≤ η := by
    rw [abs_sub_comm]
    exact ht
  have : |V s - V t| ≤ 2 * η := by
    linarith
  linarith

/-- A finite set is pairwise value-separated at tolerance `η`. -/
def PairwiseValueSeparated
    {S : Type u} [DecidableEq S]
    (V : S → ℚ) (η : ℚ) (K : Finset S) : Prop :=
  ∀ s ∈ K, ∀ t ∈ K, s ≠ t → 2 * η < |V s - V t|

/-- An `η`-accurate representation is injective on every pairwise
`2η`-separated finite set. -/
theorem valueApproximation_injectiveOn_separated
    {S : Type u} [DecidableEq S]
    {Z : Type v}
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ)
    (K : Finset S)
    (happrox : ValueApproximation φ V Vbar η)
    (hsep : PairwiseValueSeparated V η K) :
    Set.InjOn φ (↑K : Set S) := by
  intro s hs t ht heq
  by_contra hst
  have hgap := hsep s hs t ht hst
  exact (value_gap_forces_distinction φ V Vbar η happrox hgap) heq

/-- Every `η`-accurate code space needs at least as many codes as any finite
pairwise `2η`-separated subset of states. -/
theorem separated_card_le_code_card
    {S : Type u} [DecidableEq S]
    {Z : Type v} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ) (η : ℚ)
    (K : Finset S)
    (happrox : ValueApproximation φ V Vbar η)
    (hsep : PairwiseValueSeparated V η K) :
    K.card ≤ Fintype.card Z := by
  have hinj := valueApproximation_injectiveOn_separated
    φ V Vbar η K happrox hsep
  have hcard : (K.image φ).card = K.card :=
    Finset.card_image_iff.mpr hinj
  rw [← hcard]
  simpa using (Finset.card_le_card (Finset.subset_univ (K.image φ)))

/-- A horizon-value approximation specializes the generic rate-distortion
notion to finite stochastic control. -/
def HorizonValueApproximation
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type*}
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (Vbar : Z → ℚ) (n : ℕ) (η : ℚ) : Prop :=
  ValueApproximation φ (stochasticHorizonValue sys n) Vbar η

/-- Large finite-horizon optimal-value gaps force distinct context codes. -/
theorem horizon_value_gap_forces_context_distinction
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type*}
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (Vbar : Z → ℚ) (n : ℕ) (η : ℚ)
    (happrox : HorizonValueApproximation sys φ Vbar n η)
    {s t : S}
    (hgap : 2 * η <
      |stochasticHorizonValue sys n s - stochasticHorizonValue sys n t|) :
    φ s ≠ φ t :=
  value_gap_forces_distinction φ (stochasticHorizonValue sys n) Vbar η happrox hgap

/-- At zero distortion, any two states with different values must remain
separate. -/
theorem exact_value_representation_separates_unequal
    {S : Type u} {Z : Type v}
    (φ : S → Z) (V : S → ℚ) (Vbar : Z → ℚ)
    (happrox : ValueApproximation φ V Vbar 0)
    {s t : S} (hne : V s ≠ V t) :
    φ s ≠ φ t := by
  apply value_gap_forces_distinction φ V Vbar 0 happrox
  simp
  exact sub_ne_zero.mpr hne

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v w

/-- The v0.5 upper bound has a converse necessary-distinction consequence:
raw states farther apart than twice the certified approximation budget cannot
be merged by that abstraction. -/
theorem approximate_abstraction_large_gap_forces_distinction
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (n : ℕ) {s t : S}
    (hgap : 2 * approxBudget ε δ R n <
      |stochasticHorizonValue raw n s - stochasticHorizonValue raw n t|) :
    φ s ≠ φ t := by
  apply value_gap_forces_distinction φ
    (stochasticHorizonValue raw n)
    (stochasticHorizonValue absSys n)
    (approxBudget ε δ R n)
  · intro x
    exact approximate_stochastic_horizon_value_bound raw absSys φ ε δ R h n x
  · exact hgap

/-- Any pairwise value-separated witness set gives a certified lower bound on
the number of abstract context states required by an approximate abstraction. -/
theorem approximate_abstraction_separated_card_lower_bound
    {S : Type u} {A : Type v} {Z : Type w}
    [Fintype S] [DecidableEq S] [Fintype Z] [DecidableEq Z] [DecidableEq A]
    (raw : FiniteStochasticControlSystem S A)
    (absSys : FiniteStochasticControlSystem Z A)
    (φ : S → Z) (ε δ R : ℚ)
    (h : ApproximateStochasticAbstraction raw absSys φ ε δ R)
    (n : ℕ) (K : Finset S)
    (hsep : PairwiseValueSeparated
      (stochasticHorizonValue raw n) (approxBudget ε δ R n) K) :
    K.card ≤ Fintype.card Z := by
  apply separated_card_le_code_card φ
    (stochasticHorizonValue raw n)
    (stochasticHorizonValue absSys n)
    (approxBudget ε δ R n) K
  · intro x
    exact approximate_stochastic_horizon_value_bound raw absSys φ ε δ R h n x
  · exact hsep

end Komorebi.AVOC
