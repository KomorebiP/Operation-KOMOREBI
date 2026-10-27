import MachineTheory.RecipientExamples

/-! Independent source-facing restatements of Core4.2. In particular, quantification
runs over every case in an attained sender fibre, and both minimizations are attained.
The fixed-recipient execution specialization preserves the decoder and its limits. -/
open Komorebi.MachineTheory
open Recipient RecipientExecution
noncomputable section
variable {X H C : Type*} (α : X → H) (ok : X → C → Prop)

example :
    (∃ f : Attained α → C, ∀ x, ok x (f ⟨α x, x, rfl⟩)) ↔
    ∀ h : {h : H // ∃ x, α x = h}, ∃ c : C, ∀ x, α x = h.val → ok x c :=
  encoder_exists_iff α ok

example [Fintype X] (k : ℕ) :
    (∃ f : Attained α → C,
      (∀ x, ok x (f (record α x))) ∧ (Recipient.image α f).card ≤ k) ↔
    ∃ S : Finset C,
      (∀ h : Attained α, ∃ c ∈ S, ∀ x, α x = h.val → ok x c) ∧ S.card ≤ k :=
  cardinality_budget_iff α ok k

example [Fintype X] [Fintype C]
    (h : ∃ f : Attained α → C, ∀ x, ok x (f (record α x))) :
    ∃ f : Attained α → C,
      (∀ x, ok x (f (record α x))) ∧
      (∀ g : Attained α → C, (∀ x, ok x (g (record α x))) →
        (Recipient.image α f).card ≤ (Recipient.image α g).card) ∧
      (∀ S : Finset C, (∀ a : Attained α, ∃ c ∈ S, ∀ x, α x = a.val → ok x c) →
        (Recipient.image α f).card ≤ S.card) := by
  obtain ⟨f, S, hf, _, he, _, hmin, hcover⟩ := minimum_common_artifact h
  refine ⟨f, hf, ?_, ?_⟩
  · intro g hg
    rw [he]
    exact hmin g hg
  · intro T ht
    rw [he]
    exact hcover T ht

example [Fintype X] [Fintype C] (h : Feasible α ok) :
    minImageSize h = minCoverSize h := minimum_image_eq_cover h

example {I : Type*} {B Y : I → Type*} (R : Audience X C I B Y) :
    (∃ f : Attained α → C, ∀ x i, R.permitted i x (f (record α x)) ∧
      ∃ r, R.run i (R.background i x) (f (record α x)) = .completed r ∧
        r.output = R.target i x ∧ r.work ≤ R.workLimit i x ∧
        r.peakSpace ≤ R.spaceLimit i x) ↔
    ∀ h : Attained α, ∃ c, ∀ x, α x = h.val → ∀ i,
      R.permitted i x c ∧ ∃ r, R.run i (R.background i x) c = .completed r ∧
        r.output = R.target i x ∧ r.work ≤ R.workLimit i x ∧
        r.peakSpace ≤ R.spaceLimit i x := R.common_artifact_iff α

example : minCoverSize RecipientExamples.xor_feasible = 2 :=
  RecipientExamples.xor_minimum_codebook
example : minCoverSize RecipientExamples.pair_feasible = 4 :=
  RecipientExamples.pair_minimum_codebook
example : minCoverSize RecipientExamples.triple_feasible = 2 :=
  RecipientExamples.triple_minimum_codebook
example : minCoverSize RecipientExamples.empty_problem_feasible = 0 :=
  RecipientExamples.empty_minimum_zero
example : ¬ ∃ d : Attained RecipientExamples.display → Bool,
    ∀ x : RecipientExamples.Sensor, d (record RecipientExamples.display x) = x.1 :=
  RecipientExamples.xor_sender_does_not_know_target
end
