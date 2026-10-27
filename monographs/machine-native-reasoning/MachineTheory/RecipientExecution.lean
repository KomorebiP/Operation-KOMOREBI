import MachineTheory.Recipient

/-!
# Fixed recipient executions

A recipient's run function takes only its own background and the common artifact.
The hidden case indexes required results and limits, not an extra interpreter input.
Outcome flags, returned work and peak-space counters belong to a stipulated finite
execution contract. This is not a universal semantics for arbitrary host software.
-/
namespace Komorebi.MachineTheory.RecipientExecution

structure Result (Y : Type*) where
  output : Y
  work : ℕ
  peakSpace : ℕ
  deriving DecidableEq

inductive Outcome (Y : Type*) where
  | completed (r : Result Y)
  | timeout
  | malformed
  deriving DecidableEq

structure Audience (X C I : Type*) (B Y : I → Type*) where
  background : ∀ i, X → B i
  target : ∀ i, X → Y i
  run : ∀ i, B i → C → Outcome (Y i)
  permitted : I → X → C → Prop
  workLimit : I → X → ℕ
  spaceLimit : I → X → ℕ

namespace Audience
variable {X C I : Type*} {B Y : I → Type*}

/-- Each recipient must succeed on the SAME artifact with its INSTALLED interpreter. -/
def Accepts (R : Audience X C I B Y) (x : X) (c : C) : Prop :=
  ∀ i, R.permitted i x c ∧ ∃ v,
    R.run i (R.background i x) c = Outcome.completed v ∧
    v.output = R.target i x ∧ v.work ≤ R.workLimit i x ∧
    v.peakSpace ≤ R.spaceLimit i x

theorem accepts_result (R : Audience X C I B Y) {x : X} {c : C}
    (h : R.Accepts x c) (i : I) : ∃ v,
    R.run i (R.background i x) c = Outcome.completed v ∧
    v.output = R.target i x ∧ v.work ≤ R.workLimit i x ∧
    v.peakSpace ≤ R.spaceLimit i x := (h i).2

theorem no_timeout (R : Audience X C I B Y) {x : X} {c : C}
    (i : I) (h : R.run i (R.background i x) c = Outcome.timeout) : ¬ R.Accepts x c := by
  intro ha
  obtain ⟨v, hv, _⟩ := R.accepts_result ha i
  rw [h] at hv
  cases hv

theorem no_malformed (R : Audience X C I B Y) {x : X} {c : C}
    (i : I) (h : R.run i (R.background i x) c = Outcome.malformed) : ¬ R.Accepts x c := by
  intro ha
  obtain ⟨v, hv, _⟩ := R.accepts_result ha i
  rw [h] at hv
  cases hv

theorem no_work_overrun (R : Audience X C I B Y) {x : X} {c : C}
    (i : I) (v : Result (Y i))
    (hr : R.run i (R.background i x) c = Outcome.completed v)
    (hcost : R.workLimit i x < v.work) : ¬ R.Accepts x c := by
  intro ha
  obtain ⟨w, hw, _, hc, _⟩ := R.accepts_result ha i
  have he : w = v := Outcome.completed.inj (hw.symm.trans hr)
  subst w
  exact Nat.not_le_of_gt hcost hc

theorem no_space_overrun (R : Audience X C I B Y) {x : X} {c : C}
    (i : I) (v : Result (Y i))
    (hr : R.run i (R.background i x) c = Outcome.completed v)
    (hcost : R.spaceLimit i x < v.peakSpace) : ¬ R.Accepts x c := by
  intro ha
  obtain ⟨w, hw, _, _, hc⟩ := R.accepts_result ha i
  have he : w = v := Outcome.completed.inj (hw.symm.trans hr)
  subst w
  exact Nat.not_le_of_gt hcost hc

theorem no_permission (R : Audience X C I B Y) {x : X} {c : C}
    (i : I) (h : ¬ R.permitted i x c) : ¬ R.Accepts x c :=
  fun ha => h (ha i).1

/-- The source theorem instantiated at output, permission and budget success. -/
theorem common_artifact_iff (R : Audience X C I B Y) {H : Type*} (α : X → H) :
    (∃ f : Attained α → C, ∀ x, R.Accepts x (f (record α x))) ↔
      ∀ h : Attained α, ∃ c, ∀ x, α x = h.val → R.Accepts x c :=
  Recipient.encoder_exists_iff α R.Accepts

/-- Minimum image and minimum meeting codebook coincide for actual fixed recipients. -/
theorem minimum_codebook [Fintype X] (R : Audience X C I B Y) {H : Type*} {α : X → H}
    (h : Recipient.Feasible α R.Accepts) :
    Recipient.minImageSize h = Recipient.minCoverSize h :=
  Recipient.minimum_image_eq_cover h

/-- Tightening a requirement can preserve or reduce feasibility, never create it. -/
theorem acceptance_monotone {H : Type*} (α : X → H) (ok₁ ok₂ : X → C → Prop)
    (stronger : ∀ x c, ok₂ x c → ok₁ x c) :
    Recipient.Feasible α ok₂ → Recipient.Feasible α ok₁ := by
  rintro ⟨f, hf⟩
  exact ⟨f, fun x => stronger x _ (hf x)⟩

theorem minimum_monotone [Fintype X] {H : Type*} {α : X → H} {ok₁ ok₂ : X → C → Prop}
    (stronger : ∀ x c, ok₂ x c → ok₁ x c)
    (h₁ : Recipient.Feasible α ok₁) (h₂ : Recipient.Feasible α ok₂) :
    Recipient.minImageSize h₁ ≤ Recipient.minImageSize h₂ := by
  obtain ⟨f, hf, he⟩ := Recipient.minImage_attained h₂
  exact (Recipient.minImage_le h₁ f (fun x => stronger x _ (hf x))).trans_eq he

end Audience
end Komorebi.MachineTheory.RecipientExecution
