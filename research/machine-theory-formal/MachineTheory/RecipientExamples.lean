import MachineTheory.RecipientExecution
import Mathlib.Data.Fintype.Prod

/-! Exact fixed-interpreter examples for Core 4.2, with no host execution or learned-decoder claim. -/
namespace Komorebi.MachineTheory.RecipientExamples
open Recipient RecipientExecution

abbrev Sensor := Bool × Bool × Bool

def display (x : Sensor) : Bool := xor x.1 x.2.1

/-- Recipient false knows the convention; recipient true knows the target bit. -/
def xorAudience : Audience Sensor Bool Bool (fun _ => Bool) (fun _ => Bool) where
  background i x := if i then x.1 else x.2.1
  target i x := if i then x.2.1 else x.1
  run _ b c := .completed ⟨xor c b, 1, 1⟩
  permitted _ _ _ := True
  workLimit _ _ := 1
  spaceLimit _ _ := 1

theorem xor_accepts_iff (x : Sensor) (c : Bool) :
    xorAudience.Accepts x c ↔ c = display x := by
  rcases x with ⟨b, s, n⟩
  cases b <;> cases s <;> cases n <;> cases c <;>
    simp [Audience.Accepts, xorAudience, display]

theorem xor_sender_valid : Valid display xorAudience.Accepts (fun h => h.val) := by
  intro x
  exact (xor_accepts_iff x _).mpr rfl

theorem xor_feasible : Feasible display xorAudience.Accepts :=
  ⟨fun h => h.val, xor_sender_valid⟩

theorem xor_sender_does_not_know_target :
    ¬ ∃ d : Attained display → Bool, ∀ x : Sensor, d (record display x) = x.1 := by
  exact no_decoder_of_collision (r := display) (t := fun x : Sensor => x.1)
    (false, false, false) (true, true, false) rfl (by decide)

theorem xor_image_for_every_valid_sender (f : Attained display → Bool)
    (hf : Valid display xorAudience.Accepts f) : image display f = Finset.univ := by
  have hforced : Valid display (fun x c => c = display x) f :=
    fun x => (xor_accepts_iff x _).mp (hf x)
  rw [forced_image display display f hforced]
  decide

theorem xor_minimum_codebook : minCoverSize xor_feasible = 2 := by
  rw [← minimum_image_eq_cover xor_feasible]
  obtain ⟨f, hf, he⟩ := minImage_attained xor_feasible
  rw [← he, xor_image_for_every_valid_sender f hf]
  decide

theorem xor_one_artifact_impossible :
    ¬ ∃ f : Attained display → Bool,
      Valid display xorAudience.Accepts f ∧ (image display f).card ≤ 1 := by
  rintro ⟨f, hf, hc⟩
  have h := minCover_le xor_feasible _ (image_hits display xorAudience.Accepts f hf)
  rw [xor_minimum_codebook] at h
  omega

/-- Return the background while ignoring the transmitted artifact. -/
def ignoresMessage : Audience Sensor Bool Bool (fun _ => Bool) (fun _ => Bool) :=
  { xorAudience with run := fun _ b _ => .completed ⟨b, 1, 1⟩ }

theorem ignored_message_fails (c : Bool) :
    ¬ ignoresMessage.Accepts (true, false, false) c := by
  cases c <;> simp [Audience.Accepts, ignoresMessage, xorAudience]

theorem fixed_ignoring_decoder_has_no_encoder : ¬ Feasible display ignoresMessage.Accepts := by
  rintro ⟨f, hf⟩
  exact ignored_message_fails _ (hf (true, false, false))

/-- Correct output with a two-unit run cannot use the unchanged one-unit contract. -/
def tooSlow : Audience Sensor Bool Bool (fun _ => Bool) (fun _ => Bool) :=
  { xorAudience with run := fun _ b c => .completed ⟨xor c b, 2, 1⟩ }

theorem correct_output_still_over_budget (x : Sensor) (c : Bool) : ¬ tooSlow.Accepts x c := by
  apply tooSlow.no_work_overrun false ⟨xor c x.2.1, 2, 1⟩ rfl
  change 1 < 2
  decide

def tooLarge : Audience Sensor Bool Bool (fun _ => Bool) (fun _ => Bool) :=
  { xorAudience with run := fun _ b c => .completed ⟨xor c b, 1, 2⟩ }

theorem correct_output_still_over_space (x : Sensor) (c : Bool) : ¬ tooLarge.Accepts x c := by
  apply tooLarge.no_space_overrun false ⟨xor c x.2.1, 1, 2⟩ rfl
  change 1 < 2
  decide

def timedOut : Audience Sensor Bool Bool (fun _ => Bool) (fun _ => Bool) :=
  { xorAudience with run := fun _ _ _ => .timeout }

theorem timeout_is_not_success (x : Sensor) (c : Bool) : ¬ timedOut.Accepts x c :=
  timedOut.no_timeout false rfl

def malformed : Audience Sensor Bool Bool (fun _ => Bool) (fun _ => Bool) :=
  { xorAudience with run := fun _ _ _ => .malformed }

theorem malformed_is_not_success (x : Sensor) (c : Bool) : ¬ malformed.Accepts x c :=
  malformed.no_malformed false rfl

def forbidden : Audience Sensor Bool Bool (fun _ => Bool) (fun _ => Bool) :=
  { xorAudience with permitted := fun _ _ _ => False }

theorem correct_output_still_forbidden (x : Sensor) (c : Bool) : ¬ forbidden.Accepts x c :=
  forbidden.no_permission false id

/-- Manuscript Counterexample 4.3: each case is soluble, but not from this record. -/
def blindRecord (_ : Bool) : Unit := ()

theorem individual_cases_have_artifacts : ∀ x : Bool, ∃ c : Bool, c = x :=
  fun x => ⟨x, rfl⟩

theorem individually_possible_not_common :
    ¬ Feasible blindRecord (fun x c : Bool => c = x) := by
  apply no_encoder_of_disjoint blindRecord (fun x c : Bool => c = x) false true rfl
  intro c h
  have he : false = true := h.1.symm.trans h.2
  cases he

/-- A separate artifact for each recipient does not supply one common artifact. -/
theorem separate_recipient_artifacts_exist : ∀ i : Bool, ∃ c : Bool, c = i :=
  fun i => ⟨i, rfl⟩

theorem no_one_artifact_for_opposed_recipients : ¬ ∃ c : Bool, ∀ i : Bool, c = i := by
  rintro ⟨c, hc⟩
  have he : false = true := (hc false).symm.trans (hc true)
  cases he

/-- Recipient false reads the first component, recipient true the second. -/
def pairAudience : Audience (Bool × Bool) (Bool × Bool) Bool (fun _ => Unit) (fun _ => Bool) where
  background _ _ := ()
  target i x := if i then x.2 else x.1
  run i _ c := .completed ⟨if i then c.2 else c.1, 1, 1⟩
  permitted _ _ _ := True
  workLimit _ _ := 1
  spaceLimit _ _ := 1

theorem pair_accepts_iff (x c : Bool × Bool) : pairAudience.Accepts x c ↔ c = x := by
  rcases x with ⟨x₀, x₁⟩
  rcases c with ⟨c₀, c₁⟩
  cases x₀ <;> cases x₁ <;> cases c₀ <;> cases c₁ <;>
    simp [Audience.Accepts, pairAudience, Bool.forall_bool]

def pairRecord (x : Bool × Bool) : Bool × Bool := x

theorem pair_feasible : Feasible pairRecord pairAudience.Accepts := by
  refine ⟨fun h => h.val, ?_⟩
  intro x
  exact (pair_accepts_iff x x).mpr rfl

theorem pair_minimum_codebook : minCoverSize pair_feasible = 4 := by
  rw [← minimum_image_eq_cover pair_feasible]
  obtain ⟨f, hf, he⟩ := minImage_attained pair_feasible
  have hforced : Valid pairRecord (fun x c => c = x) f :=
    fun x => (pair_accepts_iff x _).mp (hf x)
  rw [← he, forced_image pairRecord id f hforced]
  decide

theorem pair_single_binary_message_impossible (send : Attained pairRecord → Bool)
    (decode : Bool → Bool × Bool) :
    ¬ Valid pairRecord pairAudience.Accepts (decode ∘ send) := by
  intro hv
  have h := decoded_alphabet_bound pair_feasible send decode hv
  rw [pair_minimum_codebook] at h
  have hc : Fintype.card Bool = 2 := rfl
  omega

/-- Each projection can separately be explained with one binary symbol. -/
theorem individual_projection_codes (x : Bool × Bool) :
    ((x.1, false) : Bool × Bool).1 = x.1 ∧
    ((false, x.2) : Bool × Bool).2 = x.2 := ⟨rfl, rfl⟩

/-- No impossible input needs a default artifact: both source and artifact types can be empty. -/
def emptyRecord (x : Empty) : Bool := nomatch x

theorem empty_problem_feasible : Feasible emptyRecord (fun (_ : Empty) (_ : Empty) => False) := by
  apply (encoder_exists_iff _ _).mpr
  intro h
  obtain ⟨x, _⟩ := h.property
  cases x

theorem empty_codebook_hits : Hits emptyRecord (fun (_ : Empty) (_ : Empty) => False) ∅ := by
  intro h
  obtain ⟨x, _⟩ := h.property
  cases x

theorem empty_minimum_zero : minCoverSize empty_problem_feasible = 0 := by
  have h := minCover_le empty_problem_feasible ∅ empty_codebook_hits
  simpa using Nat.eq_zero_of_le_zero h

theorem requiring_a_total_decoder_would_fail : ¬ Nonempty (Bool → Empty) := by
  rintro ⟨f⟩
  exact Empty.elim (f false)

/-- Three different sender records, with overlapping two-element acceptance sets. -/
def tripleRecord (x : Fin 3) : Fin 3 := x

theorem triple_pairwise_intersections :
    ∀ x y : Fin 3, ∃ c : Fin 3, c ≠ x ∧ c ≠ y := by decide

theorem triple_no_global_intersection : ¬ ∃ c : Fin 3, ∀ x : Fin 3, c ≠ x := by
  rintro ⟨c, hc⟩
  exact hc c rfl

theorem triple_two_codebook_hits :
    Hits tripleRecord (fun x c : Fin 3 => c ≠ x) {0, 1} := by
  intro h
  by_cases hh : h.val = 0
  · refine ⟨1, by simp, ?_⟩
    intro x hx
    have he : x = 0 := hx.trans hh
    rw [he]
    decide
  · refine ⟨0, by simp, ?_⟩
    intro x hx hzero
    exact hh (hx.symm.trans hzero.symm)

theorem triple_feasible : Feasible tripleRecord (fun x c : Fin 3 => c ≠ x) := by
  obtain ⟨f, hf, _⟩ := (encoder_within_iff tripleRecord _ {0, 1}).mpr triple_two_codebook_hits
  exact ⟨f, hf⟩

theorem triple_hitting_needs_two (S : Finset (Fin 3))
    (hs : Hits tripleRecord (fun x c : Fin 3 => c ≠ x) S) : 2 ≤ S.card := by
  by_contra hn
  have hsmall : S.card ≤ 1 := by omega
  have hsub := Finset.card_le_one.mp hsmall
  obtain ⟨c, hc, _⟩ := hs (record tripleRecord 0)
  obtain ⟨d, hd, hdc⟩ := hs (record tripleRecord c)
  exact hdc c rfl (hsub d hd c hc)

theorem triple_minimum_codebook : minCoverSize triple_feasible = 2 := by
  apply le_antisymm
  · have h := minCover_le triple_feasible {0, 1} triple_two_codebook_hits
    exact h.trans_eq (by decide)
  · obtain ⟨S, hs, he⟩ := minCover_attained triple_feasible
    exact (triple_hitting_needs_two S hs).trans_eq he

/-- Pairwise-compatible cases still need a joint intersection when the sender is blind. -/
theorem triple_blind_sender_impossible :
    ¬ Feasible (fun _ : Fin 3 => ()) (fun x c : Fin 3 => c ≠ x) := by
  rintro ⟨f, hf⟩
  let c := f (record (fun _ : Fin 3 => ()) 0)
  have he : record (fun _ : Fin 3 => ()) c = record (fun _ : Fin 3 => ()) 0 :=
    Subtype.ext rfl
  have h := hf c
  rw [he] at h
  exact h rfl

end Komorebi.MachineTheory.RecipientExamples
