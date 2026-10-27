import MachineTheory

/-! These independently restated types are checked against the exported theorems.
They supplement, and do not replace, the source-to-statement review. -/
open Komorebi.MachineTheory
open scoped BigOperators
noncomputable section

section Evidence
variable {X A Y H : Type*} (F : A → X → X) (q : X → Y) (r : X → H)
example : (∃ d : Attained r → Y, ∀ x, d (record r x) = q x) ↔
    (∀ x y, r x = r y → q x = q y) := decoder_exists_iff r q
example : Nonempty (Predictor F q r (BehavioralState F q)) ↔
    (∀ x y, r x = r y → ∀ w, q (run F w x) = q (run F w y)) :=
  evidence_initialized_predictor_iff F q r
example [Fintype X] {Z : Type*} (p : Predictor F q r Z) :
    Fintype.card (BehavioralState F q) ≤
      Fintype.card (Attained (fun x => p.initState (record r x))) :=
  p.minimal_initialized_card
end Evidence

section Packet
variable {𝕜 V Z : Type*} [Field 𝕜] [AddCommGroup V] [Module 𝕜 V]
  [AddCommGroup Z] [Module 𝕜 Z]
example (C : V →ₗ[𝕜] Z) (R : Z →ₗ[𝕜] V) (T U : V →ₗ[𝕜] V) :
    C.comp ((T.comp U).comp R) - (C.comp (T.comp R)).comp (C.comp (U.comp R)) =
      C.comp (T.comp ((LinearMap.id - R.comp C).comp (U.comp R))) :=
  hidden_return_identity C R T U
end Packet

section Transport
example {X Y A B : Type*} (D : Set X) (F : A → X → X) (G : B → Y → Y)
    (T : X → Y) (τ : A → B) (hi : ∀ a x, x ∈ D → F a x ∈ D)
    (hc : ∀ a x, x ∈ D → T (F a x) = G (τ a) (T x))
    (w : List A) (x : X) (hx : x ∈ D) :
    T (run F w x) = run G (w.map τ) (T x) :=
  invariant_forward_transport D F G T τ hi hc w x hx
end Transport

section Memory
variable {Ω Y : Type*} (E : EvidenceAlgebra Ω) (t : Ω → Y)
example (events : List E.Event) (V : Set Ω) :
    E.read t (run (E.update t) events (E.remember t V)) =
      t '' (run E.filter events V) := E.memory_readout_continuation t events V
example [Fintype Ω] {M : Type*} (r : Set Ω → M) (q : M → Set Y)
    (step : E.Event → M → M) (hq : ∀ V, q (r V) = t '' V)
    (hs : ∀ e V, step e (r V) = r (E.filter e V)) :
    Fintype.card (E.Memory t) ≤ Fintype.card (Attained r) :=
  E.memory_minimal_card t r q step hq hs
end Memory

section Probability
open Instrument
variable {X Z A O : Type*} [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
  [DecidableEq Z] (π : X → Z) (hπ : Function.Surjective π) (K : Law X A O)
example : (∃ L : Law Z A O, ∀ a o p,
    push π (applyKernel (K.kernel a o) p) = applyKernel (L.kernel a o) (push π p)) ↔
      (∀ a o z x y, π x = π y →
        (∑ u, if π u = z then K.kernel a o u x else 0) =
          (∑ u, if π u = z then K.kernel a o u y else 0)) :=
  quotient_exists_iff π hπ K
example (hc : FiberCriterion π K.kernel) (g : Policy A O) (p : X → ℝ)
    (events : History A O) :
    let L := coarseLaw π hπ K
    mass (evolve K.kernel g.probability [] events p) =
      mass (evolve L.kernel g.probability [] events (push π p)) ∧
    Option.map (push π) (posterior? (evolve K.kernel g.probability [] events p)) =
      posterior? (evolve L.kernel g.probability [] events (push π p)) :=
  quotient_feedback_law π hπ K hc g p events
example (g : Policy A O) (p : X → ℝ) (hp : IsDist p) (n : Nat) :
    totalHistoryMass K g n [] p = 1 := by rw [totalHistoryMass_eq, hp.2]
end Probability

#check decoder_exists_iff
#check evidence_initialized_predictor_iff
#check Predictor.minimal_initialized_card
#check canonical_initialized_card
#check split_encoding_comp
#check hidden_return_identity
#check invariant_forward_output
#check EvidenceAlgebra.memory_minimal_card
#check Instrument.quotient_exists_iff
#check Instrument.quotient_unique
#check Instrument.instrument_iff_reports_and_posteriors
#check Instrument.quotient_feedback_law
#check Instrument.stoppedAndSurvivingMass_eq

section Reporting
open Instrument Bayes Bayes.ReportingModel
variable {M O Z : Type*} [Fintype M] [Fintype O] [Fintype Z]
  [Nonempty M] [Nonempty O] (E : ReportingModel M O Z)
-- The reconstruction must factor the actual joint likelihood, not just its marginals.
example :
    (∀ p : M → ℝ, IsDist p → ∀ o z,
      0 < evidence p (E.joint o z) → update p (E.raw o) = update p (E.report z)) ↔
    ∃ ρ : Z → O → ℝ, (∀ z o, 0 ≤ ρ z o) ∧ (∀ z, ∑ o, ρ z o = 1) ∧
      (∀ m o z, E.likelihood m o * E.channel o z =
        (∑ o', E.likelihood m o' * E.channel o' z) * ρ z o) :=
  E.all_iff_reconstruction
example (p : M → ℝ) (hp : IsDist p) (hfull : ∀ m, 0 < p m) :
    E.PreservesAll ↔ E.PreservesAt p := E.all_iff_full_support_prior p hp hfull
end Reporting

section SeparateCorrection
open Instrument Bayes BayesianLumping
variable {X Z : Type*} [Fintype X] [Fintype Z] [DecidableEq X] [DecidableEq Z]
example (π : X → Z) (hπ : Function.Surjective π) (l : X → ℝ)
    (hl : ∀ x, 0 < l x) (hn : ∃ x y, π x ≠ π y) :
    (∃ g : Z → ℝ, (∀ z, 0 < g z) ∧
      ∀ p, IsDist p → push π (update p l) = update (push π p) g) ↔
    (∀ x y, π x = π y → l x = l y) := fixed_positive_coarse_iff π hπ l hl hn
end SeparateCorrection

section LeastRefinement
open Instrument Bayes Refinement
variable {X A O : Type*} [Fintype X]
example (K : Law X A Unit) (l : O → X → ℝ) (P₀ : Setoid X)
    (hl : ∀ o x, 0 < l o x) (hn : ∃ x y, ¬ P₀ x y) :
    let I := initial P₀ l
    let n := stopIndex (transition K) I
    let P := Refinement.sequence (transition K) I n
    n ≤ Fintype.card X - Nat.card (Quotient I) ∧
      (P ≤ P₀ ∧ PredictionExists K P ∧ CorrectionsExist l P) ∧
      (∀ Q, Q ≤ P₀ → PredictionExists K Q → CorrectionsExist l Q → Q ≤ P) := by
  have h := least_prediction_correction_refinement K l P₀ hl hn
  exact ⟨h.1, h.2.1, fun Q hq hp hc => h.2.2.1 Q ⟨hq,hp,hc⟩⟩
example (K : A → X → X → ℝ) (I : Setoid X) :
    ∃ n ≤ Fintype.card X - Nat.card (Quotient I),
      step K (Refinement.sequence K I n) = Refinement.sequence K I n := bounded_stabilization K I
end LeastRefinement

#check Bayes.ReportingModel.all_iff_exists_full_support
#check Bayes.ReportingModel.reconstruction_factor
#check Refinement.admissible_iff
#check Refinement.least_prediction_correction_refinement
#check Block02Examples.discrete_is_only_admissible
#check Block02Examples.one_block_still_corrects
#check Block02Examples.likelihood_split_cannot_be_omitted

section PlanningBlock03
open Instrument Planning BeliefPlanning
variable {X Z A O D : Type*} [Fintype X] [Fintype Z] [Fintype O] [DecidableEq Z]
variable (K : Law X A O) (L : Law Z A O) (π : X → Z)
variable (hk : ∀ a o p, push π (applyKernel (K.kernel a o) p) =
    applyKernel (L.kernel a o) (push π p)) (C : Contract Z A D)
example (h : Nat) (p : X → ℝ) (hp : IsDist p) :
    value (fineModel K π C) h ⟨p,hp⟩ =
      value (coarseModel L C) h ⟨push π p, push_dist π p hp⟩ :=
  (instrumentMap K L π hk C).value_eq h ⟨p,hp⟩
example (h : Nat) (p : Belief X) (a : A) :
    backup (fineModel K π C) (value (fineModel K π C) h) p a =
      backup (coarseModel L C) (value (coarseModel L C) h) (aggregate π p) a :=
  (instrumentMap K L π hk C).firstValue_eq h p (Sum.inr a)
example (h : Nat) (p : Belief X) (d : D) :
    OptimalFirst (fineModel K π C) h p (Sum.inl d) ↔
      OptimalFirst (coarseModel L C) h (aggregate π p) (Sum.inl d) :=
  (instrumentMap K L π hk C).optimalFirst_iff h p (Sum.inl d)
example (h : Nat) (q : Belief Z) :
    ∃ P : Tree A O D, P.Bounded h ∧ Feasible (coarseModel L C) h q P ∧
      evaluate (coarseModel L C) P q = value (coarseModel L C) h q ∧
      ∀ p : Belief X, aggregate π p = q → Feasible (fineModel K π C) h p P ∧
        evaluate (fineModel K π C) P p = value (fineModel K π C) h p :=
  common_optimal_inquiry K L π hk C h q
example (h : Nat) (p : Belief X) (P : Tree A O D)
    (hp : Feasible (fineModel K π C) h p P) :
    value (fineModel K π C) h p ≤ evaluate (fineModel K π C) P p :=
  value_le_tree _ h p P hp
end PlanningBlock03

#check Planning.minimizing_tree_exists
#check Planning.randomized_tree_lower_bound
#check BeliefPlanning.constructed_quotient_planning
#check PlanningSensor.countMap
#check PlanningSensor.eight_world_adaptive_optimal
#check PlanningSensor.source_sensor_optimum
#check PlanningControls.no_common_permission_quotient
#check PlanningControls.unchanged_filter_different_value
example : Planning.value PlanningSensor.countModel 3 (0,0) = (11 : ℝ)/40 :=
  PlanningSensor.sensor_value_table.2.2.2

section TerminalBlock03
open Planning
variable {S T A O D : Type*} [Fintype O]
example (M : Model S A O D) (N : Model T A O D) (f : S → T)
    (H : ExactMap M N f) (s : S) (d : D) :
    (d ∈ M.decisions s ∧ M.loss s d = value M 0 s) ↔
      (d ∈ N.decisions (f s) ∧ N.loss (f s) d = value N 0 (f s)) :=
  H.optimalStop_iff 0 s d
end TerminalBlock03
