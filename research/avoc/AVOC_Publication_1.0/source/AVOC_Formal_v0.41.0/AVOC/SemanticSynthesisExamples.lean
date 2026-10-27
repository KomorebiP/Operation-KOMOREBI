import AVOC.SemanticSearchBudget

namespace Komorebi.AVOC.SemanticSynthesis

open Synthesis

def sx : Program := .variable .first
def sy : Program := .variable .second

theorem same_size_not_same_semantics : nodes sx = nodes sy ∧ ¬ Equivalent sx sy := by
  refine ⟨rfl, ?_⟩
  intro h
  have hh := h ⟨true,false,false⟩
  simp [sx, sy, run, Input.get] at hh

theorem one_sample_not_a_signature : run sx ⟨false,false,false⟩ = run (.literal false) ⟨false,false,false⟩ ∧
    ¬ Equivalent sx (.literal false) := by
  refine ⟨rfl, ?_⟩
  intro h
  have hh := h ⟨true,false,false⟩
  simp [sx, run, Input.get] at hh

theorem compact_keeps_smaller_equivalent :
    (codes (compact [.neg (.neg sx),sx])) = [sx] := by decide

theorem arbitrary_equivalent_representative_can_be_worse :
    Equivalent (.neg (.neg sx)) sx ∧ nodes (.neg (.neg sx)) > nodes sx := by
  constructor
  · intro s; simp [run]
  · decide

theorem first_layer_has_seventeen : (representatives 1).length = 17 := by decide

theorem feedback_second_layer_count :
    (expand (codes (representatives 1))).length = 901 := by
  rw [expand_length]
  simp only [codes, List.length_map, first_layer_has_seventeen]

theorem frozen_second_layer_count : (programs 2).length = 21845 := by
  rw [programs_length]
  decide

theorem feedback_emits_strictly_fewer_at_second_layer :
    (expand (codes (representatives 1))).length < (programs 2).length := by
  rw [feedback_second_layer_count, frozen_second_layer_count]
  decide

theorem zero_credit_does_not_search (d : Nat) : paidSearch d 0 = none :=
  unfunded_seed_no_search d 0 (by decide)

end Komorebi.AVOC.SemanticSynthesis
