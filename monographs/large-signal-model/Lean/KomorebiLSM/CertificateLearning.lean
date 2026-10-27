import KomorebiLSM.BaseNormModels
import KomorebiLSM.PolicyComparison
import KomorebiLSM.Conditioning
import KomorebiLSM.ConditionalStochasticCompletion
import Mathlib.MeasureTheory.Measure.Real

/-! P49: observable models with finite, checked probability-domain witnesses.
Statistical coverage is an explicit event, while stochastic validity follows
from the actual nonnegative coefficient matrices and normalized initial lift. -/
set_option autoImplicit false
namespace Komorebi.LSM.CertificateLearning
open scoped BigOperators
open FiniteInstruments FiniteBayes PositiveLift BaseNorm ObservationTree

variable {E A O J : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [Fintype A] [Fintype O] [Fintype J] [DecidableEq J]

/-- A stationary finite-dimensional model is its symbol family and initial state. -/
abbrev Model (E A O : Type*) [AddCommGroup E] [Module ℝ E] :=
  (A × O → E →ₗ[ℝ] E) × E

/-- A finite witness consists of literal nonnegative matrices and a prior.
It assumes no probability-law conclusion. -/
structure Witness (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ) (m : Model E A O) where
  matrix : A × O → Matrix J J ℝ
  coefficients : J → ℝ
  entries_nonnegative : ∀ s i j, 0 ≤ matrix s i j
  prior : IsPrior coefficients
  intertwines : ∀ s, (m.1 s).comp V=V.comp (matrix s).mulVecLin
  mass_law : ∀ a x, ∑ o, l (m.1 (a,o) x)=l x
  initial : m.2=V coefficients

variable (V : (J → ℝ) →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
variable (hn : l.comp V=FiniteInstruments.mass) (hs : Function.Surjective V)

omit [FiniteDimensional ℝ E] [Fintype A] in
/-- Checked lift equalities imply invariance, rather than assuming validity. -/
theorem witness_valid_family {m : Model E A O} (w : Witness V l m) :
    RobustDomains.ValidFamily (hull V) l m.1 := by
  refine ⟨?_,w.mass_law⟩
  intro s
  exact (positive_lift_iff V (m.1 s)).mpr ⟨w.matrix s,w.entries_nonnegative s,w.intertwines s⟩

omit [FiniteDimensional ℝ E] [Fintype A] [DecidableEq J] in
include hn in
theorem witness_initial {m : Model E A O} (w : Witness V l m) :
    m.2∈normalizedHull V l := by
  rw [w.initial]
  refine ⟨⟨w.coefficients,w.prior.1,rfl⟩,?_⟩
  simpa only [normalized_mass V l hn] using w.prior.2

omit [FiniteDimensional ℝ E] [Fintype A] in
include hn in
/-- The matrix/prior witness is equivalent to finite-cone validity and initial
coverage; the reverse direction constructs its nonnegative columns. -/
theorem witness_exists_iff (m : Model E A O) :
    Nonempty (Witness V l m) ↔
      RobustDomains.ValidFamily (hull V) l m.1 ∧ m.2∈normalizedHull V l := by
  classical
  constructor
  · rintro ⟨w⟩
    exact ⟨witness_valid_family V l w,witness_initial V l hn w⟩
  · rintro ⟨hv,hi⟩
    have hmat := fun s => (positive_lift_iff V (m.1 s)).mp (hv.1 s)
    choose M hp he using hmat
    rw [normalizedHull_eq_prior_image V l hn] at hi
    obtain ⟨a,ha,heq⟩ := hi
    exact ⟨⟨M,a,hp,ha,he,hv.2,heq.symm⟩⟩

omit [FiniteDimensional ℝ E] [Fintype A] in
include hn in
/-- Finite robust vertex checks cover every operator family in the actual
uncertainty hull; initial-state coverage remains a separate required check. -/
theorem robust_vertex_witness {I : Type*}
    (families : I → A × O → E →ₗ[ℝ] E) (M : I → A × O → Matrix J J ℝ)
    (hp : ∀ i s j k, 0≤M i s j k)
    (he : ∀ i s, (families i s).comp V=V.comp (M i s).mulVecLin)
    (hm : ∀ i a x, ∑ o, l (families i (a,o) x)=l x)
    (U : Set (Model E A O))
    (hU : ∀ m∈U, m.1∈convexHull ℝ (Set.range families) ∧ m.2∈normalizedHull V l) :
    ∀ m∈U, Nonempty (Witness V l m) := by
  intro m hmem
  obtain ⟨hB,hinit⟩ := hU m hmem
  exact (witness_exists_iff V l hn m).mpr
    ⟨RobustDomains.robust_positive_lift V l families M hp he hm m.1 hB,hinit⟩

omit [FiniteDimensional ℝ E] [Fintype A] in
include hn in
/-- Every future experiment probability is an actual probability of the
constructed finite nonnegative instrument, for all word lengths. -/
theorem certified_all_words {m : Model E A O} (w : Witness V l m) :
    (∀ word, 0≤l (wordAction m.1 word m.2) ∧ l (wordAction m.1 word m.2)≤1) := by
  intro word
  rw [w.initial]
  exact (finite_positive_lift_certificate m.1 V l hn w.mass_law w.matrix
    w.intertwines w.entries_nonnegative w.coefficients w.prior).2.2 word

omit [FiniteDimensional ℝ E] [Fintype A] [DecidableEq J] in
/-- In a reachable realization an invariant lift containing the initial state
already spans the entire observable space. -/
theorem witness_surjective_of_reachable {f : List (A × O) → ℝ}
    (r : Behavior.Realization f E) (hr : r.IsReachable)
    (w : Witness V l (r.operator,r.initial)) : Function.Surjective V := by
  apply LinearMap.range_eq_top.mp
  apply top_unique
  rw [← hr]
  apply Submodule.span_le.mpr
  rintro _ ⟨word,rfl⟩
  refine ⟨wordAction (fun s => (w.matrix s).mulVecLin) word w.coefficients,?_⟩
  change V (wordAction (fun s => (w.matrix s).mulVecLin) word w.coefficients)=
    wordAction r.operator word r.initial
  have hi : r.initial=V w.coefficients := w.initial
  exact (PositiveLift.lifted_word r.operator V w.matrix w.intertwines word w.coefficients).symm.trans
    (congrArg (wordAction r.operator word) hi.symm)

omit [Fintype A] in
/-- The actual finite witness constructs a full instrument on the common base norm cone. -/
theorem certified_instrument {m : Model E A O} (w : Witness V l m) (a : A) :
    (finiteCone V l hn hs).Instrument (fun o => m.1 (a,o)) := by
  have hv := witness_valid_family V l w
  exact ⟨fun o x hx => hv.1 (a,o) x hx,hv.2 a⟩

omit [Fintype A] in
theorem certified_initial {m : Model E A O} (w : Witness V l m) :
    m.2∈(finiteCone V l hn hs).base := witness_initial V l hn w

/-- Full joint action/observation record law under one common history policy. -/
noncomputable def modelLaw (π : List (A × O) → A → ℝ) (n : ℕ)
    (m : Model E A O) : Record (A × O) n → ℝ :=
  recordLaw (finiteCone V l hn hs) (policyBranches π (fun _ => m.1)) n [] m.2

noncomputable def observedLaw (π : List (A × O) → A → ℝ) (n : ℕ)
    (m : Model E A O) : Record O n → ℝ :=
  observationLaw (finiteCone V l hn hs) π (fun _ => m.1) n m.2

noncomputable def budget (e₀ : ℝ) (ε : ℕ → ℝ) (n : ℕ) : ℝ :=
  min 1 ((e₀+∑ t∈Finset.range n, ε t)/2)

theorem modelLaw_prior {m : Model E A O} (w : Witness V l m)
    (π : List (A × O) → A → ℝ) (hπ : ∀ h,IsPrior (π h)) (n : ℕ) :
    IsPrior (modelLaw V l hn hs π n m) := by
  apply record_prior (finiteCone V l hn hs)
    (policyBranches π (fun _ => m.1))
    (policy_instrument (finiteCone V l hn hs) π hπ (fun _ => m.1)
      (fun _ a => certified_instrument V l hn hs w a)) n [] m.2
  exact certified_initial V l hn hs w

theorem observedLaw_prior {m : Model E A O} (w : Witness V l m)
    (π : List (A × O) → A → ℝ) (hπ : ∀ h,IsPrior (π h)) (n : ℕ) :
    IsPrior (observedLaw V l hn hs π n m) := by
  classical
  exact aggregate_prior (recordMap Prod.snd) _ (modelLaw_prior V l hn hs w π hπ n)

/-- P49's common-policy bound uses the actual finite-cone infimum and actual
record laws. Initial and one-step errors remain explicit numerical budgets. -/
theorem certified_policy_bounds {truth fitted : Model E A O}
    (wt : Witness V l truth) (wf : Witness V l fitted) (ε : ℕ → ℝ) (e₀ : ℝ)
    (herr : ∀ t a z, z∈(finiteCone V l hn hs).base →
      (finiteCone V l hn hs).discrepancy (fun o => truth.1 (a,o))
        (fun o => fitted.1 (a,o)) z≤ε t)
    (hinit : (finiteCone V l hn hs).value (truth.2-fitted.2)≤e₀)
    (π : List (A × O) → A → ℝ) (hπ : ∀ h,IsPrior (π h)) (n : ℕ) :
    FiniteTV.distance (modelLaw V l hn hs π n truth) (modelLaw V l hn hs π n fitted)≤budget e₀ ε n ∧
    FiniteTV.distance (observedLaw V l hn hs π n truth) (observedLaw V l hn hs π n fitted)≤budget e₀ ε n := by
  have hb := shared_randomized_policy_tv_bound (finiteCone V l hn hs) π hπ
    (fun _ => truth.1) (fun _ => fitted.1)
    (fun _ a => certified_instrument V l hn hs wt a)
    (fun _ a => certified_instrument V l hn hs wf a) ε
    (fun h a z hz => herr h.length a z hz) n truth.2 fitted.2
    (certified_initial V l hn hs wt) (certified_initial V l hn hs wf)
  have ho := shared_policy_observation_tv_bound (finiteCone V l hn hs) π hπ
    (fun _ => truth.1) (fun _ => fitted.1)
    (fun _ a => certified_instrument V l hn hs wt a)
    (fun _ a => certified_instrument V l hn hs wf a) ε
    (fun h a z hz => herr h.length a z hz) n truth.2 fitted.2
    (certified_initial V l hn hs wt) (certified_initial V l hn hs wf)
  have hbudget : min 1 ((finiteCone V l hn hs).value (truth.2-fitted.2)/2+
      (∑ t∈Finset.range n, ε t)/2)≤budget e₀ ε n := by
    apply min_le_min le_rfl
    linarith
  exact ⟨hb.trans hbudget,ho.trans hbudget⟩

/-- Conditioning applies to those same record laws, with the positive-event
premises from P44 rather than an unconditional posterior stability claim. -/
theorem certified_conditioning {truth fitted : Model E A O}
    (wt : Witness V l truth) (wf : Witness V l fitted) (ε : ℕ → ℝ) (e₀ : ℝ)
    (herr : ∀ t a z, z∈(finiteCone V l hn hs).base →
      (finiteCone V l hn hs).discrepancy (fun o => truth.1 (a,o))
        (fun o => fitted.1 (a,o)) z≤ε t)
    (hinit : (finiteCone V l hn hs).value (truth.2-fitted.2)≤e₀)
    (π : List (A × O) → A → ℝ) (hπ : ∀ h,IsPrior (π h)) (n : ℕ)
    [DecidableEq (Record (A × O) n)] (H : Finset (Record (A × O) n))
    (ht : 0<FiniteTV.eventMass (modelLaw V l hn hs π n truth) H)
    (hf : 0<FiniteTV.eventMass (modelLaw V l hn hs π n fitted) H) :
    FiniteTV.distance (FiniteTV.conditional (modelLaw V l hn hs π n truth) H)
      (FiniteTV.conditional (modelLaw V l hn hs π n fitted) H)≤
        min 1 (budget e₀ ε n/FiniteTV.eventMass (modelLaw V l hn hs π n truth) H) :=
  FiniteTV.conditioning_tv_bound _ _ (modelLaw_prior V l hn hs wt π hπ n)
    (modelLaw_prior V l hn hs wf π hπ n) H (budget e₀ ε n)
    (certified_policy_bounds V l hn hs wt wf ε e₀ herr hinit π hπ n).1 ht hf

/-- P44 also conditions the actual observation-only record laws, with both
positive-event denominator hypotheses retained. -/
theorem certified_observation_conditioning {truth fitted : Model E A O}
    (wt : Witness V l truth) (wf : Witness V l fitted) (ε : ℕ → ℝ) (e₀ : ℝ)
    (herr : ∀ t a z,z∈(finiteCone V l hn hs).base →
      (finiteCone V l hn hs).discrepancy (fun o => truth.1 (a,o))
        (fun o => fitted.1 (a,o)) z≤ε t)
    (hinit : (finiteCone V l hn hs).value (truth.2-fitted.2)≤e₀)
    (π : List (A × O) → A → ℝ) (hπ : ∀ h,IsPrior (π h)) (n : ℕ)
    [DecidableEq (Record O n)] (H : Finset (Record O n))
    (ht : 0<FiniteTV.eventMass (observedLaw V l hn hs π n truth) H)
    (hf : 0<FiniteTV.eventMass (observedLaw V l hn hs π n fitted) H) :
    FiniteTV.distance (FiniteTV.conditional (observedLaw V l hn hs π n truth) H)
      (FiniteTV.conditional (observedLaw V l hn hs π n fitted) H)≤
        min 1 (budget e₀ ε n/FiniteTV.eventMass (observedLaw V l hn hs π n truth) H) :=
  FiniteTV.conditioning_tv_bound _ _ (observedLaw_prior V l hn hs wt π hπ n)
    (observedLaw_prior V l hn hs wf π hπ n) H (budget e₀ ε n)
    (certified_policy_bounds V l hn hs wt wf ε e₀ herr hinit π hπ n).2 ht hf

section Confidence
open MeasureTheory
variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

omit [IsProbabilityMeasure μ] in
/-- P49's confidence event is supplied by the justified observation protocol.
On it actual robust coefficient certificates make the true and fitted models
valid on one common domain, with the common-policy error bounds. -/
theorem conditional_learning
    (truth fitted : Ω → Model E A O) (U : Ω → Set (Model E A O))
    (wf : ∀ ω,Witness V l (fitted ω))
    (robust : ∀ ω m, m∈U ω → Nonempty (Witness V l m))
    (event : Set Ω) (hmeas : MeasurableSet event) (δ : ℝ)
    (hprob : 1-δ≤μ.real event) (hcover : ∀ ω∈event,truth ω∈U ω)
    (ε : Ω → ℕ → ℝ) (e₀ : Ω → ℝ)
    (herr : ∀ ω∈event,∀ t a z,z∈(finiteCone V l hn hs).base →
      (finiteCone V l hn hs).discrepancy (fun o => (truth ω).1 (a,o))
        (fun o => (fitted ω).1 (a,o)) z≤ε ω t)
    (hinit : ∀ ω∈event,(finiteCone V l hn hs).value ((truth ω).2-(fitted ω).2)≤e₀ ω) :
    MeasurableSet event ∧ 1-δ≤μ.real event ∧ ∀ ω∈event,
      (∀ word,0≤l (wordAction (truth ω).1 word (truth ω).2) ∧
        l (wordAction (truth ω).1 word (truth ω).2)≤1) ∧
      (∀ word,0≤l (wordAction (fitted ω).1 word (fitted ω).2) ∧
        l (wordAction (fitted ω).1 word (fitted ω).2)≤1) ∧
      (∀ π,(∀ h,IsPrior (π h)) → ∀ n,
        FiniteTV.distance (modelLaw V l hn hs π n (truth ω)) (modelLaw V l hn hs π n (fitted ω))≤
          budget (e₀ ω) (ε ω) n ∧
        FiniteTV.distance (observedLaw V l hn hs π n (truth ω)) (observedLaw V l hn hs π n (fitted ω))≤
          budget (e₀ ω) (ε ω) n) := by
  refine ⟨hmeas,hprob,?_⟩
  intro ω hω
  obtain ⟨wt⟩ := robust ω (truth ω) (hcover ω hω)
  exact ⟨certified_all_words V l hn wt,certified_all_words V l hn (wf ω),
    fun π hπ n => certified_policy_bounds V l hn hs wt (wf ω) (ε ω) (e₀ ω)
      (herr ω hω) (hinit ω hω) π hπ n⟩

omit [IsProbabilityMeasure μ] in
/-- The learner may select its finite generator set and common domain from the
data. Coverage is still stated on one explicit measurable event. -/
theorem conditional_selected_learning
    {K : Ω → Type*} [∀ ω,Fintype (K ω)] [∀ ω,DecidableEq (K ω)]
    (V₀ : ∀ ω,(K ω → ℝ) →ₗ[ℝ] E)
    (hn₀ : ∀ ω,l.comp (V₀ ω)=FiniteInstruments.mass)
    (hs₀ : ∀ ω,Function.Surjective (V₀ ω))
    (truth fitted : Ω → Model E A O) (U : Ω → Set (Model E A O))
    (wf : ∀ ω,Witness (V₀ ω) l (fitted ω))
    (robust : ∀ ω m,m∈U ω → Nonempty (Witness (V₀ ω) l m))
    (event : Set Ω) (hmeas : MeasurableSet event) (δ : ℝ)
    (hprob : 1-δ≤μ.real event) (hcover : ∀ ω∈event,truth ω∈U ω)
    (ε : Ω → ℕ → ℝ) (e₀ : Ω → ℝ)
    (herr : ∀ ω∈event,∀ t a z,z∈(finiteCone (V₀ ω) l (hn₀ ω) (hs₀ ω)).base →
      (finiteCone (V₀ ω) l (hn₀ ω) (hs₀ ω)).discrepancy
        (fun o => (truth ω).1 (a,o)) (fun o => (fitted ω).1 (a,o)) z≤ε ω t)
    (hinit : ∀ ω∈event,(finiteCone (V₀ ω) l (hn₀ ω) (hs₀ ω)).value
      ((truth ω).2-(fitted ω).2)≤e₀ ω) :
    MeasurableSet event ∧ 1-δ≤μ.real event ∧ ∀ ω∈event,
      (∀ word,0≤l (wordAction (truth ω).1 word (truth ω).2) ∧
        l (wordAction (truth ω).1 word (truth ω).2)≤1) ∧
      (∀ word,0≤l (wordAction (fitted ω).1 word (fitted ω).2) ∧
        l (wordAction (fitted ω).1 word (fitted ω).2)≤1) ∧
      (∀ π,(∀ h,IsPrior (π h)) → ∀ n,
        FiniteTV.distance
          (modelLaw (V₀ ω) l (hn₀ ω) (hs₀ ω) π n (truth ω))
          (modelLaw (V₀ ω) l (hn₀ ω) (hs₀ ω) π n (fitted ω))≤budget (e₀ ω) (ε ω) n ∧
        FiniteTV.distance
          (observedLaw (V₀ ω) l (hn₀ ω) (hs₀ ω) π n (truth ω))
          (observedLaw (V₀ ω) l (hn₀ ω) (hs₀ ω) π n (fitted ω))≤budget (e₀ ω) (ε ω) n) := by
  refine ⟨hmeas,hprob,?_⟩
  intro ω hω
  obtain ⟨wt⟩ := robust ω (truth ω) (hcover ω hω)
  exact ⟨certified_all_words (V₀ ω) l (hn₀ ω) wt,
    certified_all_words (V₀ ω) l (hn₀ ω) (wf ω),
    fun π hπ n => certified_policy_bounds (V₀ ω) l (hn₀ ω) (hs₀ ω)
      wt (wf ω) (ε ω) (e₀ ω) (herr ω hω) (hinit ω hω) π hπ n⟩

end Confidence
section Atlas
open ConditionalStochasticCompletion
variable {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- Exact atlas transport uses one conjugation and the transported mass row. -/
noncomputable def atlasModel (T : E ≃ₗ[ℝ] F) (m : Model E A O) : Model F A O :=
  (atlasOperator T m.1,T m.2)

omit [FiniteDimensional ℝ E] [DecidableEq J] in
include hn in
/-- The same finite coefficient prior stays normalized after coordinate transport. -/
theorem atlas_normalized (T : E ≃ₗ[ℝ] F) :
    (atlasMass T l).comp (T.toLinearMap.comp V)=FiniteInstruments.mass := by
  apply LinearMap.ext
  intro a
  change l (T.symm (T (V a)))=FiniteInstruments.mass a
  rw [T.symm_apply_apply]
  exact congrArg (fun L : (J → ℝ) →ₗ[ℝ] ℝ => L a) hn

omit [FiniteDimensional ℝ E] [Fintype J] [DecidableEq J] in
include hs in
theorem atlas_surjective (T : E ≃ₗ[ℝ] F) : Function.Surjective (T.toLinearMap.comp V) :=
  T.surjective.comp hs

/-- Transport preserves the actual checked nonnegative matrices and initial
prior, rather than searching for another finite certificate. -/
noncomputable def atlasWitness (T : E ≃ₗ[ℝ] F) {m : Model E A O} (w : Witness V l m) :
    Witness (T.toLinearMap.comp V) (atlasMass T l) (atlasModel T m) where
  matrix := w.matrix
  coefficients := w.coefficients
  entries_nonnegative := w.entries_nonnegative
  prior := w.prior
  intertwines := by
    intro s
    apply LinearMap.ext
    intro a
    change T (m.1 s (T.symm (T (V a))))=T (V ((w.matrix s).mulVecLin a))
    rw [T.symm_apply_apply]
    exact congrArg T (congrArg (fun L : (J → ℝ) →ₗ[ℝ] E => L a) (w.intertwines s))
  mass_law := by
    intro a z
    change (∑ o, l (T.symm (T (m.1 (a,o) (T.symm z)))) )=l (T.symm z)
    simp only [T.symm_apply_apply]
    exact w.mass_law a (T.symm z)
  initial := by
    change T m.2=T (V w.coefficients)
    exact congrArg T w.initial

omit [Fintype A] [Fintype O] [Fintype J] [DecidableEq J] [FiniteDimensional ℝ E] in
theorem atlas_word_probability (T : E ≃ₗ[ℝ] F) (m : Model E A O) (word : List (A × O)) :
    atlasMass T l (wordAction (atlasModel T m).1 word (atlasModel T m).2)=
      l (wordAction m.1 word m.2) :=
  atlas_likelihood T m.1 l word m.2

omit [Fintype A] [Fintype O] [Fintype J] [DecidableEq J] [FiniteDimensional ℝ E] in
/-- Full synthesis preserves every future experiment prediction, including
signed packets. The individual packets are not asserted to be probabilities. -/
theorem full_packet_prediction {K : Type*} [Fintype K]
    (P : K → E →ₗ[ℝ] E) (hP : ∑ k,P k=LinearMap.id)
    (m : Model E A O) (word : List (A × O)) (z : E) :
    l (wordAction m.1 word (∑ k,P k z))=l (wordAction m.1 word z) :=
  ConditionalStochasticCompletion.full_packet_prediction P hP m.1 l word z

/-- Probability-mixture interpretation requires positivity of every packet.
That condition is separate from the synthesis identity. -/
theorem positive_packet_interpretation {K : Type*} [Fintype K] [DecidableEq K]
    (P : K → E →ₗ[ℝ] E)
    (hpos : ∀ k z,z∈(finiteCone V l hn hs).carrier → P k z∈(finiteCone V l hn hs).carrier)
    (hP : ∑ k,P k=LinearMap.id) (z : E) (hz : z∈(finiteCone V l hn hs).base) :
    (∑ k,l (P k z)=1) ∧
    (∑ k∈Finset.univ.filter (fun k => 0<l (P k z)),
      l (P k z) • ((l (P k z))⁻¹ • P k z))=z := by
  let C := finiteCone V l hn hs
  exact ⟨PositivePackets.packet_weights_sum l P hP z hz.2,
    PositivePackets.positive_packet_mixture C.carrier l
      (fun x hx hne => C.mass_pos hx hne) P hpos hP z hz.1⟩

/-- An individual normalized packet is a probability state only under its
explicit cone-positivity and positive-mass hypotheses. -/
theorem positive_packet_state (P : E →ₗ[ℝ] E)
    (hpos : ∀ z,z∈(finiteCone V l hn hs).carrier → P z∈(finiteCone V l hn hs).carrier)
    (z : E) (hz : z∈(finiteCone V l hn hs).base) (hp : 0<l (P z)) :
    (l (P z))⁻¹ • P z∈(finiteCone V l hn hs).base := by
  let C := finiteCone V l hn hs
  exact PositivePackets.normalized_packet C.carrier
    (fun a ha x hx => C.smul_mem ha hx) l P hpos z hz.1 hp

end Atlas

section Observable
open Behavior
variable {I : Type*} [Fintype I] [DecidableEq I]
variable (f : List (A × O) → ℝ) [FiniteDimensional ℝ (space f)]
variable (tests histories : I → List (A × O))
variable (hH : IsUnit (core f tests histories).det)
variable (hr : Module.finrank ℝ (space f)≤Fintype.card I) (i₀ : I) (hi : tests i₀=[])

/-- The true operator/initial pair is the actual observable population-table
construction of P37, not an unknown hidden-state model supplied to a learner. -/
noncomputable def observableModel : Model (I → ℝ) A O :=
  ((tableModel f tests histories hH hr i₀ hi).operator,
   (tableModel f tests histories hH hr i₀ hi).initial)

omit [Fintype A] [Fintype O] in
/-- This is the exact full-process likelihood represented by that constructed pair. -/
theorem observable_word_probability (word : List (A × O)) :
    (LinearMap.proj i₀ : (I → ℝ) →ₗ[ℝ] ℝ) (wordAction (observableModel f tests histories hH hr i₀ hi).1 word
      (observableModel f tests histories hH hr i₀ hi).2)=f word :=
  (tableModel f tests histories hH hr i₀ hi).correct word

omit [Fintype A] [Fintype O] in
include hH hr in
/-- The observable state dimension is minimal among actual finite realizations. -/
theorem observable_minimal {F : Type*} [AddCommGroup F] [Module ℝ F]
    [FiniteDimensional ℝ F] (r : Behavior.Realization f F) :
    Fintype.card I≤Module.finrank ℝ F :=
  tableModel_minimal f tests histories hH hr r

omit [Fintype A] in
/-- A finite certificate for the reconstructed observable pair certifies the
actual process word laws, and not merely the table entries used to construct it. -/
theorem observable_certificate_all_words
    {K : Type*} [Fintype K] [DecidableEq K]
    (V₀ : (K → ℝ) →ₗ[ℝ] (I → ℝ))
    (hn₀ : (LinearMap.proj i₀ : (I → ℝ) →ₗ[ℝ] ℝ).comp V₀=FiniteInstruments.mass)
    (w : Witness V₀ (LinearMap.proj i₀ : (I → ℝ) →ₗ[ℝ] ℝ) (observableModel f tests histories hH hr i₀ hi)) :
    ∀ word,0≤f word ∧ f word≤1 := by
  intro word
  have hw := certified_all_words V₀ (LinearMap.proj i₀ : (I → ℝ) →ₗ[ℝ] ℝ) hn₀ w word
  rwa [observable_word_probability f tests histories hH hr i₀ hi] at hw

omit [Fintype A] in
/-- P37 reachability discharges the full-row-rank requirement for every true
observable-model witness. -/
theorem observable_witness_surjective
    {K : Type*} [Fintype K] [DecidableEq K]
    (V₀ : (K → ℝ) →ₗ[ℝ] (I → ℝ))
    (w : Witness V₀ (LinearMap.proj i₀ : (I → ℝ) →ₗ[ℝ] ℝ)
      (observableModel f tests histories hH hr i₀ hi)) : Function.Surjective V₀ :=
  witness_surjective_of_reachable V₀ (LinearMap.proj i₀)
    (tableModel f tests histories hH hr i₀ hi)
    (tableModel_reachable f tests histories hH hr i₀ hi) w

section ObservableConfidence
open MeasureTheory
variable {Ω K : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
variable [Fintype K] [DecidableEq K]

/-- The same confidence-and-certificate implication with the true model fixed
literally to P37's population-table reconstruction. It connects the observable
process law, not merely a generic matrix family, to the all-horizon bound. -/
theorem conditional_observable_learning
    (V₀ : (K → ℝ) →ₗ[ℝ] (I → ℝ))
    (hn₀ : (LinearMap.proj i₀ : (I → ℝ) →ₗ[ℝ] ℝ).comp V₀=FiniteInstruments.mass)
    (hs₀ : Function.Surjective V₀)
    (fitted : Ω → Model (I → ℝ) A O) (U : Ω → Set (Model (I → ℝ) A O))
    (wf : ∀ ω,Witness V₀ (LinearMap.proj i₀) (fitted ω))
    (robust : ∀ ω m,m∈U ω → Nonempty (Witness V₀ (LinearMap.proj i₀) m))
    (event : Set Ω) (hmeas : MeasurableSet event) (δ : ℝ)
    (hprob : 1-δ≤μ.real event)
    (hcover : ∀ ω∈event,observableModel f tests histories hH hr i₀ hi∈U ω)
    (ε : Ω → ℕ → ℝ) (e₀ : Ω → ℝ)
    (herr : ∀ ω∈event,∀ t a z,z∈(finiteCone V₀ (LinearMap.proj i₀) hn₀ hs₀).base →
      (finiteCone V₀ (LinearMap.proj i₀) hn₀ hs₀).discrepancy
        (fun o => (observableModel f tests histories hH hr i₀ hi).1 (a,o))
        (fun o => (fitted ω).1 (a,o)) z≤ε ω t)
    (hinit : ∀ ω∈event,(finiteCone V₀ (LinearMap.proj i₀) hn₀ hs₀).value
      ((observableModel f tests histories hH hr i₀ hi).2-(fitted ω).2)≤e₀ ω) :
    (∀ word,(LinearMap.proj i₀ : (I → ℝ) →ₗ[ℝ] ℝ)
      (wordAction (observableModel f tests histories hH hr i₀ hi).1 word
        (observableModel f tests histories hH hr i₀ hi).2)=f word) ∧
    MeasurableSet event ∧ 1-δ≤μ.real event ∧ ∀ ω∈event,
      (∀ word,0≤f word ∧ f word≤1) ∧
      (∀ π,(∀ h,IsPrior (π h)) → ∀ n,
        FiniteTV.distance (modelLaw V₀ (LinearMap.proj i₀) hn₀ hs₀ π n
          (observableModel f tests histories hH hr i₀ hi))
          (modelLaw V₀ (LinearMap.proj i₀) hn₀ hs₀ π n (fitted ω))≤budget (e₀ ω) (ε ω) n ∧
        FiniteTV.distance (observedLaw V₀ (LinearMap.proj i₀) hn₀ hs₀ π n
          (observableModel f tests histories hH hr i₀ hi))
          (observedLaw V₀ (LinearMap.proj i₀) hn₀ hs₀ π n (fitted ω))≤budget (e₀ ω) (ε ω) n) := by
  refine ⟨observable_word_probability f tests histories hH hr i₀ hi,hmeas,hprob,?_⟩
  intro ω hω
  obtain ⟨wt⟩ := robust ω _ (hcover ω hω)
  refine ⟨observable_certificate_all_words f tests histories hH hr i₀ hi V₀ hn₀ wt,?_⟩
  intro π hπ n
  exact certified_policy_bounds V₀ (LinearMap.proj i₀) hn₀ hs₀ wt (wf ω) (ε ω) (e₀ ω)
    (herr ω hω) (hinit ω hω) π hπ n

end ObservableConfidence

end Observable

end Komorebi.LSM.CertificateLearning
