import AVOC.State

namespace Komorebi.AVOC

/-- A verification gate is extensionally sound for `truth` when every claim it
admits satisfies the intended predicate.  This deliberately separates verifier
soundness from specification fidelity. -/
def SoundGate {C : Type*} (gate truth : C → Prop) : Prop :=
  ∀ c, gate c → truth c

/-- If all accepted claims pass a sound gate, every accepted claim is true under
the predicate that gate actually verifies. -/
theorem sound_gate_acceptance
    {C : Type*} {accepted : Finset C} {gate truth : C → Prop}
    (hsound : SoundGate gate truth)
    (hadmit : ∀ c ∈ accepted, gate c) :
    ∀ c ∈ accepted, truth c := by
  intro c hc
  exact hsound c (hadmit c hc)

/-- Under a sound gate, the finite set of admitted false claims is empty. -/
theorem sound_gate_false_filter_empty
    {C : Type*} [DecidableEq C]
    (accepted : Finset C) (gate truth : C → Prop)
    [DecidablePred truth]
    (hsound : SoundGate gate truth)
    (hadmit : ∀ c ∈ accepted, gate c) :
    accepted.filter (fun c => ¬ truth c) = ∅ := by
  rw [Finset.filter_eq_empty_iff]
  intro c hc hfalse
  exact hfalse (sound_gate_acceptance hsound hadmit c hc)

/-- Consequently the exact false-admission count is zero under perfect gate
soundness.  This theorem does not assert that a real verifier is perfectly sound. -/
theorem sound_gate_false_admission_count_zero
    {C : Type*} [DecidableEq C]
    (accepted : Finset C) (gate truth : C → Prop)
    [DecidablePred truth]
    (hsound : SoundGate gate truth)
    (hadmit : ∀ c ∈ accepted, gate c) :
    (accepted.filter (fun c => ¬ truth c)).card = 0 := by
  rw [sound_gate_false_filter_empty accepted gate truth hsound hadmit]
  rfl

end Komorebi.AVOC
