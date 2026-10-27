import ProofPath.TraceWire
import ProofPath.TraceCompleteness

namespace ProofPath.Trace.Examples
open Wire

def chain : Problem := ⟨4, [0], [⟨[0], 1⟩, ⟨[1], 2⟩], [], [3]⟩
def chainCertificate : Certificate := ⟨true, [0, 1, 2], [0, 1], none⟩
def blocked : Problem := { chain with negative := [2] }
def blockedCertificate : Certificate :=
  ⟨false, [0, 1, 2], [0, 1], some ⟨2, [0, 1]⟩⟩

theorem chain_accepted : accept chain chainCertificate = true := by decide

theorem chain_has_protected_model :
    chain.field.Extends chain.seeds chain.forbidden (fun v => v ∈ chainCertificate.closure) :=
  certificate_positive _ _ (by decide) rfl

theorem blocked_accepted : accept blocked blockedCertificate = true := by decide

theorem blocked_has_no_model :
    ¬ ∃ x, blocked.field.Extends blocked.seeds blocked.forbidden x :=
  certificate_negative blocked blockedCertificate (by decide) rfl

theorem accepted_json_has_checked_answer :
    acceptJson (encodeProblem chain) (encodeCertificate chainCertificate) = true := by
  rw [encoded_acceptance]
  exact chain_accepted

/-- Closedness by itself is not a least-model certificate. -/
theorem forged_closed_superset_is_rejected :
    closed chain [0, 1, 2, 3] = true ∧
      checkClosure chain [] [0, 1, 2, 3] = false := by decide

/-- Derivability of every listed node does not establish saturation. -/
theorem partial_replay_is_not_complete :
    replay chain true chain.initial [0] = some [1, 0] ∧
      checkClosure chain [0] [0, 1] = false := by decide

theorem wrong_order_rejected :
    replay chain false chain.initial [1, 0] = none := by decide

theorem unknown_rule_rejected :
    replay chain false chain.initial [9] = none := by decide

theorem repeated_rule_causal_not_strict :
    checkWitness blocked ⟨2, [0, 0, 1]⟩ = true ∧
      replay blocked true blocked.initial [0, 0, 1] = none := by decide

theorem context_substitution_rejected :
    accept blocked chainCertificate = false := by decide

theorem witness_target_must_be_forbidden :
    checkWitness chain ⟨2, [0, 1]⟩ = false := by decide

theorem direct_observation_conflict :
    checkWitness ({ chain with positive := [3] } : Problem) ⟨3, []⟩ = true := by decide

def cycle : Problem := ⟨2, [], [⟨[0], 1⟩, ⟨[1], 0⟩], [], [1]⟩

theorem unseeded_cycle_is_not_self_justifying :
    accept cycle ⟨true, [], [], none⟩ = true ∧
      checkWitness cycle ⟨1, [0, 1]⟩ = false := by decide

theorem seeded_cycle_saturates :
    accept { cycle with positive := [0] }
      ⟨false, [0, 1], [0], some ⟨1, [0]⟩⟩ = true := by decide

theorem empty_problem_accepted :
    accept ⟨0, [], [], [], []⟩ ⟨true, [], [], none⟩ = true := by decide

theorem empty_address_space_rejects_rule :
    problemValid ⟨0, [], [⟨[], 0⟩], [], []⟩ = false := by decide

theorem duplicate_rows_retain_distinct_addresses :
    let p : Problem := ⟨2, [0], [⟨[0], 1⟩, ⟨[0], 1⟩], [], []⟩
    accept p ⟨true, [0, 1], [0], none⟩ = true ∧
    accept p ⟨true, [0, 1], [1], none⟩ = true := by decide

theorem booleans_are_not_node_indices : decodeNat (.bool true) = none := rfl

theorem strings_are_not_verdicts : decodeBool (.str "false") = none := rfl

theorem extra_certificate_fields_rejected :
    decodeCertificate (.arr #[.str "proof-path/certificate/1", .bool true,
      .arr #[], .arr #[], .null, .null]) = none := rfl

theorem wrong_version_rejected :
    decodeCertificate (.arr #[.str "proof-path/certificate/2", .bool true,
      .arr #[], .arr #[], .null]) = none := by decide

end ProofPath.Trace.Examples
