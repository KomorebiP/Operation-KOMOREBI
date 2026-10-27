import AVOC.ExactRateDistortion
import Mathlib.Data.Finset.Max
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC

universe u v w

/-- A compressed decision signature is `η`-accurate when every action-wise
Q-coordinate is reconstructed within `η`. -/
def QSignatureApproximation
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ) : Prop :=
  ∀ s a, |Q s a - Qbar (φ s) a| ≤ η

/-- Exact finite-horizon stochastic-control specialization of Q-signature
approximation. -/
def HorizonQSignatureApproximation
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type w}
    (sys : FiniteStochasticControlSystem S A)
    (φ : S → Z) (Qbar : Z → A → ℚ) (n : ℕ) (η : ℚ) : Prop :=
  QSignatureApproximation φ (fun s a => stochasticQValue sys n s a) Qbar η

/-- A context fiber is decision-signature feasible when every action coordinate
has diameter at most `2η` inside the fiber. -/
def QFiberDiameterBound
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (η : ℚ) : Prop :=
  ∀ s t, φ s = φ t → ∀ a, |Q s a - Q t a| ≤ 2 * η

/-- Every action-wise accurate decoder necessarily has Q-diameter at most
`2η` on each context fiber. -/
theorem qSignatureApproximation_implies_fiberDiameter
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (h : QSignatureApproximation φ Q Qbar η) :
    QFiberDiameterBound φ Q η := by
  intro s t hst a
  have hs := h s a
  have ht := h t a
  have htri : |Q s a - Q t a| ≤
      |Q s a - Qbar (φ s) a| + |Qbar (φ t) a - Q t a| := by
    calc
      |Q s a - Q t a|
          = |(Q s a - Qbar (φ s) a) + (Qbar (φ t) a - Q t a)| := by
              rw [hst]
              ring_nf
      _ ≤ |Q s a - Qbar (φ s) a| + |Qbar (φ t) a - Q t a| := abs_add_le _ _
  have ht' : |Qbar (φ t) a - Q t a| ≤ η := by
    rw [abs_sub_comm]
    exact ht
  linarith

/-- The set of action-`a` Q-values appearing in a finite context fiber. -/
def qFiberValues
    {S : Type u} [Fintype S]
    {A : Type v} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (z : Z) (a : A) : Finset ℚ :=
  (valueFiberStates φ z).image (fun s => Q s a)

/-- Every state's action-value appears in the corresponding Q-fiber value set. -/
theorem mem_qFiberValues_self
    {S : Type u} [Fintype S]
    {A : Type v} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (s : S) (a : A) :
    Q s a ∈ qFiberValues φ Q (φ s) a := by
  apply Finset.mem_image.mpr
  refine ⟨s, ?_, rfl⟩
  simp [valueFiberStates]

/-- Coordinate-wise midpoint decoder for a finite Q-signature fiber. -/
noncomputable def midpointQDecoder
    {S : Type u} [Fintype S]
    {A : Type v} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (z : Z) (a : A) : ℚ :=
  if h : (qFiberValues φ Q z a).Nonempty then
    ((qFiberValues φ Q z a).min' h + (qFiberValues φ Q z a).max' h) / 2
  else 0

/-- Coordinate-wise midpoint reconstruction is Q-signature accurate whenever
all context fibers have action-wise diameter at most `2η`. -/
theorem midpointQDecoder_accurate
    {S : Type u} [Fintype S]
    {A : Type v} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (η : ℚ)
    (hdiam : QFiberDiameterBound φ Q η) :
    QSignatureApproximation φ Q (midpointQDecoder φ Q) η := by
  intro s a
  let vals := qFiberValues φ Q (φ s) a
  have hsval : Q s a ∈ vals := by
    simpa [vals] using mem_qFiberValues_self φ Q s a
  have hne : vals.Nonempty := ⟨Q s a, hsval⟩
  let mn : ℚ := vals.min' hne
  let mx : ℚ := vals.max' hne
  have hmnmem : mn ∈ vals := by
    simpa [mn] using vals.min'_mem hne
  have hmxmem : mx ∈ vals := by
    simpa [mx] using vals.max'_mem hne
  have hmns : mn ≤ Q s a := by
    simpa [mn] using Finset.min'_le vals (Q s a) hsval
  have hsmx : Q s a ≤ mx := by
    simpa [mx] using Finset.le_max' vals (Q s a) hsval
  rcases Finset.mem_image.mp hmnmem with ⟨smin, hsminFiber, hsminVal⟩
  rcases Finset.mem_image.mp hmxmem with ⟨smax, hsmaxFiber, hsmaxVal⟩
  have hsminCode : φ smin = φ s := (Finset.mem_filter.mp hsminFiber).2
  have hsmaxCode : φ smax = φ s := (Finset.mem_filter.mp hsmaxFiber).2
  have hsminmaxCode : φ smin = φ smax := hsminCode.trans hsmaxCode.symm
  have hdiam' := hdiam smin smax hsminmaxCode a
  have hmnmx : mn ≤ mx := le_trans hmns hsmx
  have hspan : mx - mn ≤ 2 * η := by
    have habs : |mn - mx| ≤ 2 * η := by
      simpa [hsminVal, hsmaxVal] using hdiam'
    rw [abs_of_nonpos (sub_nonpos.mpr hmnmx)] at habs
    linarith
  have hmid : |Q s a - (mn + mx) / 2| ≤ η := by
    rw [abs_le]
    constructor <;> linarith
  simpa [midpointQDecoder, vals, hne, mn, mx] using hmid

/-- Exact finite Q-vector rate-distortion characterization for a fixed context
partition: an action-wise `η`-accurate decoder exists iff every context fiber
has coordinate diameter at most `2η`. -/
theorem exists_qSignatureApproximation_iff_fiberDiameter
    {S : Type u} [Fintype S]
    {A : Type v} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (η : ℚ) :
    (∃ Qbar : Z → A → ℚ, QSignatureApproximation φ Q Qbar η) ↔
      QFiberDiameterBound φ Q η := by
  constructor
  · rintro ⟨Qbar, h⟩
    exact qSignatureApproximation_implies_fiberDiameter φ Q Qbar η h
  · intro hdiam
    exact ⟨midpointQDecoder φ Q, midpointQDecoder_accurate φ Q η hdiam⟩

/-- At zero distortion, exact Q-signature decoding is exactly action-wise
constancy of Q on each context fiber. -/
theorem exists_exact_q_decoder_iff_fiber_constant
    {S : Type u} [Fintype S]
    {A : Type v} {Z : Type w} [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) :
    (∃ Qbar : Z → A → ℚ, QSignatureApproximation φ Q Qbar 0) ↔
      ∀ s t, φ s = φ t → ∀ a, Q s a = Q t a := by
  rw [exists_qSignatureApproximation_iff_fiberDiameter φ Q 0]
  constructor
  · intro h s t hst a
    have hh := h s t hst a
    simp only [mul_zero, abs_nonpos_iff] at hh
    linarith
  · intro h s t hst a
    have := h s t hst a
    simp [this]

/-- If one action coordinate differs by more than `2η`, every `η`-accurate
Q-signature representation must distinguish the two states. -/
theorem q_coordinate_gap_forces_distinction
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (happrox : QSignatureApproximation φ Q Qbar η)
    {s t : S} {a : A}
    (hgap : 2 * η < |Q s a - Q t a|) :
    φ s ≠ φ t := by
  intro hst
  have hdiam := qSignatureApproximation_implies_fiberDiameter φ Q Qbar η happrox
  exact (not_le_of_gt hgap) (hdiam s t hst a)

/-- Pairwise action-signature separation on a finite witness set. -/
def PairwiseQSeparated
    {S : Type u} [DecidableEq S]
    {A : Type v}
    (Q : S → A → ℚ) (η : ℚ) (K : Finset S) : Prop :=
  ∀ s ∈ K, ∀ t ∈ K, s ≠ t → ∃ a, 2 * η < |Q s a - Q t a|

/-- An accurate Q-signature context is injective on every finite pairwise
Q-separated witness set. -/
theorem qSignatureApproximation_injectiveOn_separated
    {S : Type u} [DecidableEq S]
    {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (K : Finset S)
    (happrox : QSignatureApproximation φ Q Qbar η)
    (hsep : PairwiseQSeparated Q η K) :
    Set.InjOn φ (↑K : Set S) := by
  intro s hs t ht heq
  by_contra hst
  obtain ⟨a, hgap⟩ := hsep s hs t ht hst
  exact (q_coordinate_gap_forces_distinction φ Q Qbar η happrox hgap) heq

/-- Pairwise Q-separated states give a lower bound on finite context-cardinality. -/
theorem q_separated_card_le_code_card
    {S : Type u} [DecidableEq S]
    {A : Type v} {Z : Type w} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (K : Finset S)
    (happrox : QSignatureApproximation φ Q Qbar η)
    (hsep : PairwiseQSeparated Q η K) :
    K.card ≤ Fintype.card Z := by
  have hinj := qSignatureApproximation_injectiveOn_separated
    φ Q Qbar η K happrox hsep
  have hcard : (K.image φ).card = K.card := Finset.card_image_iff.mpr hinj
  rw [← hcard]
  simpa using (Finset.card_le_card (Finset.subset_univ (K.image φ)))

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v w

/-- An action is Q-optimal at a raw state. -/
def QOptimalAt
    {S : Type u} {A : Type v}
    (Q : S → A → ℚ) (s : S) (a : A) : Prop :=
  ∀ b, Q s b ≤ Q s a

/-- An action is optimal in the decoded Q-signature at a context code. -/
def AbstractQOptimalAt
    {A : Type v} {Z : Type w}
    (Qbar : Z → A → ℚ) (z : Z) (a : A) : Prop :=
  ∀ b, Qbar z b ≤ Qbar z a

/-- An action optimal in an `η`-accurate decoded Q-signature is at most `2η`
suboptimal against every raw action. -/
theorem abstract_q_optimal_raw_regret_bound
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (happrox : QSignatureApproximation φ Q Qbar η)
    {s : S} {aStar : A}
    (hopt : AbstractQOptimalAt Qbar (φ s) aStar) :
    ∀ a, Q s a - Q s aStar ≤ 2 * η := by
  intro a
  have ha := happrox s a
  have hs := happrox s aStar
  have hbar := hopt a
  rw [abs_le] at ha hs
  linarith

/-- Consequently, if a raw Q-optimal action exists, the decoded optimal action
has raw regret at most `2η` relative to that optimum. -/
theorem abstract_q_optimal_regret_vs_raw_optimum
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (happrox : QSignatureApproximation φ Q Qbar η)
    {s : S} {aRaw aAbs : A}
    (hraw : QOptimalAt Q s aRaw)
    (habs : AbstractQOptimalAt Qbar (φ s) aAbs) :
    0 ≤ Q s aRaw - Q s aAbs ∧ Q s aRaw - Q s aAbs ≤ 2 * η := by
  constructor
  · exact sub_nonneg.mpr (hraw aAbs)
  · exact abstract_q_optimal_raw_regret_bound φ Q Qbar η happrox habs aRaw

/-- If a raw action has margin strictly larger than `2η` over every competitor,
then every `η`-accurate decoded signature preserves that action as strictly
optimal. -/
theorem q_margin_preserves_unique_optimum
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (happrox : QSignatureApproximation φ Q Qbar η)
    {s : S} {aStar : A}
    (hmargin : ∀ a, a ≠ aStar → 2 * η < Q s aStar - Q s a) :
    ∀ a, a ≠ aStar → Qbar (φ s) a < Qbar (φ s) aStar := by
  intro a hne
  have ha := happrox s a
  have hs := happrox s aStar
  have hm := hmargin a hne
  rw [abs_le] at ha hs
  linarith

/-- At zero Q-distortion, decoded optimality and raw optimality agree exactly. -/
theorem exact_q_signature_optimality_iff
    {S : Type u} {A : Type v} {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ)
    (happrox : QSignatureApproximation φ Q Qbar 0)
    (s : S) (a : A) :
    AbstractQOptimalAt Qbar (φ s) a ↔ QOptimalAt Q s a := by
  have hcoord : ∀ b, Q s b = Qbar (φ s) b := by
    intro b
    have hb0 : |Q s b - Qbar (φ s) b| ≤ 0 := by
      simpa using happrox s b
    have hsub : Q s b - Qbar (φ s) b = 0 := abs_nonpos_iff.mp hb0
    exact sub_eq_zero.mp hsub
  constructor
  · intro h b
    simpa [hcoord b, hcoord a] using h b
  · intro h b
    simpa [hcoord b, hcoord a] using h b

end Komorebi.AVOC
