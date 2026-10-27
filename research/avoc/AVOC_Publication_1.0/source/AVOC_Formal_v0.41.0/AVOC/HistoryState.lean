import AVOC.BayesianControl
import Mathlib.Data.Finset.Max
import Mathlib.Algebra.Order.BigOperators.Group.Finset

namespace Komorebi.AVOC

universe u v w z

/-- A raw finite action-observation history, represented in chronological snoc form. -/
inductive ResearchHistory (A : Type v) (O : Type w) where
  | root : ResearchHistory A O
  | snoc : ResearchHistory A O → A → O → ResearchHistory A O
  deriving Repr

/-- The compiled research state keeps the Bayesian belief and a separate typed
certification/artifact coordinate.  The second coordinate is intentionally
abstract: later AVOC layers may instantiate it with a proof ledger, artifact
store, frontier state, or their product. -/
structure CertifiedResearchState
    (Ω : Type u) [Fintype Ω] (Cert : Type z) where
  belief : RationalBelief Ω
  cert : Cert

@[ext] theorem CertifiedResearchState.ext
    {Ω : Type u} [Fintype Ω] {Cert : Type z}
    (s t : CertifiedResearchState Ω Cert)
    (hb : s.belief = t.belief) (hc : s.cert = t.cert) : s = t := by
  cases s
  cases t
  simp_all

/-- A finite Bayesian research controller with an additional certified-state
coordinate updated after each action-observation pair. -/
structure CertifiedBayesianResearchSystem
    (Ω : Type u) (A : Type v) (O : Type w) (Cert : Type z)
    [Fintype Ω] [Fintype O] [DecidableEq A] where
  actions : Finset A
  actions_nonempty : actions.Nonempty
  experiment : A → RationalChannel Ω O
  reward : CertifiedResearchState Ω Cert → A → ℚ
  certStep : Cert → A → O → Cert

/-- One Markov update of the compiled Bayesian/certification research state. -/
noncomputable def stepResearchState
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (s : CertifiedResearchState Ω Cert) (a : A) (o : O) :
    CertifiedResearchState Ω Cert where
  belief := bayesUpdateTotal s.belief (sys.experiment a) o
  cert := sys.certStep s.cert a o

/-- Compile a raw research history into the sufficient Bayesian/certified state. -/
noncomputable def compileHistory
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert) : ResearchHistory A O →
      CertifiedResearchState Ω Cert
  | .root => init
  | .snoc h a o => stepResearchState sys (compileHistory sys init h) a o

@[simp] theorem compileHistory_root
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert) :
    compileHistory sys init (.root : ResearchHistory A O) = init := by
  rfl

@[simp] theorem compileHistory_snoc
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert)
    (h : ResearchHistory A O) (a : A) (o : O) :
    compileHistory sys init (.snoc h a o) =
      stepResearchState sys (compileHistory sys init h) a o := by
  rfl

/-- Expected continuation value from a compiled research state. -/
noncomputable def certifiedExpectedContinuation
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (V : CertifiedResearchState Ω Cert → ℚ)
    (s : CertifiedResearchState Ω Cert) (a : A) : ℚ :=
  ∑ o, predictiveProb s.belief (sys.experiment a) o *
    V (stepResearchState sys s a o)

/-- Bellman value on the compiled Bayesian/certification state. -/
noncomputable def certifiedHorizonValue
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert) :
    ℕ → CertifiedResearchState Ω Cert → ℚ
  | 0, _ => 0
  | n + 1, s =>
      let vals := sys.actions.image (fun a =>
        sys.reward s a +
          certifiedExpectedContinuation sys (certifiedHorizonValue sys n) s a)
      vals.max' (sys.actions_nonempty.image _)

/-- Compiled-state Bellman action value. -/
noncomputable def certifiedQValue
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (n : ℕ) (s : CertifiedResearchState Ω Cert) (a : A) : ℚ :=
  sys.reward s a +
    certifiedExpectedContinuation sys (certifiedHorizonValue sys n) s a

/-- Raw-history Bellman value: this recursion is defined on the full transcript,
not by fiat through `compileHistory`. -/
noncomputable def historyHorizonValue
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert) :
    ℕ → ResearchHistory A O → ℚ
  | 0, _ => 0
  | n + 1, h =>
      let vals := sys.actions.image (fun a =>
        sys.reward (compileHistory sys init h) a +
          ∑ o, predictiveProb (compileHistory sys init h).belief
              (sys.experiment a) o *
            historyHorizonValue sys init n (.snoc h a o))
      vals.max' (sys.actions_nonempty.image _)

/-- Raw-history action value. -/
noncomputable def historyQValue
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert)
    (n : ℕ) (h : ResearchHistory A O) (a : A) : ℚ :=
  sys.reward (compileHistory sys init h) a +
    ∑ o, predictiveProb (compileHistory sys init h).belief (sys.experiment a) o *
      historyHorizonValue sys init n (.snoc h a o)

/-- The raw-history action value factors exactly through the compiled state,
provided the previous-horizon value does. -/
theorem historyQValue_eq_certifiedQValue_of_prev
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert)
    (n : ℕ)
    (ih : ∀ h : ResearchHistory A O,
      historyHorizonValue sys init n h =
        certifiedHorizonValue sys n (compileHistory sys init h))
    (h : ResearchHistory A O) (a : A) :
    historyQValue sys init n h a =
      certifiedQValue sys n (compileHistory sys init h) a := by
  unfold historyQValue certifiedQValue certifiedExpectedContinuation
  congr 1
  apply Finset.sum_congr rfl
  intro o ho
  rw [ih (.snoc h a o)]
  rfl

/-- **History-to-state sufficiency theorem.**  Under the declared Markov update,
the full action-observation transcript and its compiled Bayesian/certification
state have exactly the same finite-horizon optimal value. -/
theorem historyHorizonValue_eq_certifiedHorizonValue
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert) :
    ∀ n (h : ResearchHistory A O),
      historyHorizonValue sys init n h =
        certifiedHorizonValue sys n (compileHistory sys init h) := by
  intro n
  induction n with
  | zero =>
      intro h
      rfl
  | succ n ih =>
      intro h
      unfold historyHorizonValue certifiedHorizonValue
      have hq : ∀ a, historyQValue sys init n h a =
          certifiedQValue sys n (compileHistory sys init h) a := by
        intro a
        exact historyQValue_eq_certifiedQValue_of_prev sys init n ih h a
      have himage :
          sys.actions.image (historyQValue sys init n h) =
            sys.actions.image (certifiedQValue sys n (compileHistory sys init h)) := by
        apply Finset.image_congr
        intro a ha
        exact hq a
      change
        (sys.actions.image (historyQValue sys init n h)).max'
            (sys.actions_nonempty.image _) =
          (sys.actions.image
              (certifiedQValue sys n (compileHistory sys init h))).max'
            (sys.actions_nonempty.image _)
      apply le_antisymm
      · apply Finset.max'_le
        intro y hy
        have hy' : y ∈ sys.actions.image
            (certifiedQValue sys n (compileHistory sys init h)) := by
          rw [← himage]
          exact hy
        exact Finset.le_max' _ y hy'
      · apply Finset.max'_le
        intro y hy
        have hy' : y ∈ sys.actions.image (historyQValue sys init n h) := by
          rw [himage]
          exact hy
        exact Finset.le_max' _ y hy'

/-- Equal compiled research states imply equal future value even when the raw
histories themselves are different. -/
theorem equal_compiled_history_implies_equal_value
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert)
    (n : ℕ) (h₁ h₂ : ResearchHistory A O)
    (hc : compileHistory sys init h₁ = compileHistory sys init h₂) :
    historyHorizonValue sys init n h₁ = historyHorizonValue sys init n h₂ := by
  rw [historyHorizonValue_eq_certifiedHorizonValue sys init n h₁]
  rw [historyHorizonValue_eq_certifiedHorizonValue sys init n h₂]
  rw [hc]

/-- History-level and compiled-state action values coincide. -/
theorem historyQValue_eq_certifiedQValue
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert)
    (n : ℕ) (h : ResearchHistory A O) (a : A) :
    historyQValue sys init n h a =
      certifiedQValue sys n (compileHistory sys init h) a := by
  apply historyQValue_eq_certifiedQValue_of_prev sys init n
  intro h'
  exact historyHorizonValue_eq_certifiedHorizonValue sys init n h'

/-- Optimal-action predicates are also history-state sufficient. -/
theorem history_optimal_iff_compiled_optimal
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert)
    (n : ℕ) (h : ResearchHistory A O) (a : A) :
    (a ∈ sys.actions ∧ ∀ c ∈ sys.actions,
      historyQValue sys init n h c ≤ historyQValue sys init n h a) ↔
    (a ∈ sys.actions ∧ ∀ c ∈ sys.actions,
      certifiedQValue sys n (compileHistory sys init h) c ≤
        certifiedQValue sys n (compileHistory sys init h) a) := by
  constructor <;> intro hh
  · rcases hh with ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro c hc
    rw [← historyQValue_eq_certifiedQValue sys init n h c]
    rw [← historyQValue_eq_certifiedQValue sys init n h a]
    exact hmax c hc
  · rcases hh with ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro c hc
    rw [historyQValue_eq_certifiedQValue sys init n h c]
    rw [historyQValue_eq_certifiedQValue sys init n h a]
    exact hmax c hc

end Komorebi.AVOC
