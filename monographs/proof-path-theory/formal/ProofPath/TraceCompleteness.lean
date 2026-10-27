import ProofPath.Trace

/-!
Causal witnesses can be reused under stronger known information. Because each
rule has finitely many premises, every inductive derivation has a finite replay
trace. This is completeness of witness certificates, not verification of the
Python search procedure or a bound on shortest proofs.
-/
namespace ProofPath.Trace

theorem enabled_mono (r : Rule) {a b : List Nat}
    (hab : ∀ v, v ∈ a → v ∈ b) (h : enabled r a = true) :
    enabled r b = true :=
  (enabled_iff r b).mpr (fun v hv => hab v ((enabled_iff r a).mp h v hv))

/-- Nonstrict traces remain valid if more nodes are already known. -/
theorem replay_weaken (p : Problem) {a b trace out : List Nat}
    (hab : ∀ v, v ∈ a → v ∈ b) (h : replay p false a trace = some out) :
    ∃ result, replay p false b trace = some result ∧
      ∀ v, v ∈ out → v ∈ result := by
  induction trace generalizing a b with
  | nil =>
    have he : a = out := Option.some.inj h
    exact ⟨b, rfl, fun v hv => hab v (he.symm ▸ hv)⟩
  | cons j js ih =>
    cases hj : lookup p.rules j with
    | none => simp [replay, hj] at h
    | some r =>
      simp only [replay, hj] at h
      split at h
      next ha =>
        have he : enabled r a = true := by simpa using ha
        have he' := enabled_mono r hab he
        have hab' : ∀ v, v ∈ r.conclusion :: a → v ∈ r.conclusion :: b := by
          intro v hv
          rcases List.mem_cons.mp hv with hv | hv
          · exact List.mem_cons.mpr (Or.inl hv)
          · exact List.mem_cons.mpr (Or.inr (hab v hv))
        obtain ⟨result, hr, hc⟩ := ih hab' h
        exact ⟨result, by simp [replay, hj, he', hr], hc⟩
      next => simp at h

/-- A strict execution is also a valid causal-witness execution. -/
theorem strict_replay_is_causal (p : Problem) {known trace out : List Nat}
    (h : replay p true known trace = some out) :
    replay p false known trace = some out := by
  induction trace generalizing known with
  | nil => exact h
  | cons j js ih =>
    cases hj : lookup p.rules j with
    | none => simp [replay, hj] at h
    | some r =>
      simp only [replay, hj] at h
      split at h
      next ha =>
        have he := (Bool.and_eq_true_iff.mp ha).1
        simpa [replay, hj, he] using ih h
      next => simp at h

/-- Concatenate finitely many existing causal traces, retaining all targets. -/
theorem gather_traces (p : Problem) (targets : List Nat)
    (hw : ∀ v, v ∈ targets → ∃ tr out,
      replay p false p.initial tr = some out ∧ v ∈ out)
    {known : List Nat} (hk : ∀ v, v ∈ p.initial → v ∈ known) :
    ∃ tr out, replay p false known tr = some out ∧
      ∀ v, v ∈ targets → v ∈ out := by
  induction targets generalizing known with
  | nil => exact ⟨[], known, rfl, by simp⟩
  | cons v vs ih =>
    obtain ⟨first, out, hf, hv⟩ := hw v (by simp)
    obtain ⟨middle, hm, hsub⟩ := replay_weaken p hk hf
    have hnext : ∀ w, w ∈ p.initial → w ∈ middle := by
      intro w hw
      exact replay_extensive p false hm w (hk w hw)
    obtain ⟨rest, last, hr, hvs⟩ := ih
      (fun w hwv => hw w (List.mem_cons_of_mem _ hwv)) hnext
    refine ⟨first ++ rest, last, ?_, ?_⟩
    · simp [replay_append, hm, hr]
    · intro w hmem
      rcases List.mem_cons.mp hmem with hmem | hmem
      · subst w
        exact replay_extensive p false hr v (hsub v hv)
      · exact hvs w hmem

/-- Finite rule premises make every inductive derivation serially replayable. -/
theorem derivation_has_trace (p : Problem) {v : Nat} (hv : v ∈ p.exactClosure) :
    ∃ tr out, replay p false p.initial tr = some out ∧ v ∈ out := by
  induction hv with
  | leaf hv =>
    refine ⟨[], p.initial, rfl, ?_⟩
    rcases hv with hv | hv
    · exact List.mem_append_left _ hv
    · exact List.mem_append_right _ hv
  | step j hj _ ih =>
    cases he : lookup p.rules j with
    | none => simp [Problem.field, Field.seeded, he] at hj
    | some r =>
      have targets : ∀ w, w ∈ r.premises → ∃ tr out,
          replay p false p.initial tr = some out ∧ w ∈ out := by
        intro w hw
        apply ih w
        simpa [Problem.field, Field.seeded, he] using hw
      obtain ⟨tr, out, ht, hp⟩ := gather_traces p r.premises targets (fun _ h => h)
      have hen : enabled r out = true := (enabled_iff r out).mpr hp
      refine ⟨tr ++ [j], r.conclusion :: out, ?_, ?_⟩
      · simp [replay_append, ht, replay, he, hen]
      · simp [Problem.field, Field.seeded, he]

/-- An obstruction always has some finite causal witness in this declared field. -/
theorem witness_complete (p : Problem) {v : Nat}
    (hn : v ∈ p.forbidden) (hv : v ∈ p.exactClosure) :
    ∃ w, w.target = v ∧ checkWitness p w = true := by
  obtain ⟨tr, out, ht, hvout⟩ := derivation_has_trace p hv
  exact ⟨⟨v, tr⟩, rfl, by simpa [checkWitness, ht, hvout, Problem.forbidden] using hn⟩

theorem witness_exists_iff_infeasible (p : Problem) :
    (∃ w, checkWitness p w = true) ↔
      ¬ ∃ x, p.field.Extends p.seeds p.forbidden x := by
  constructor
  · rintro ⟨w, hw⟩
    exact checkWitness_refutes p w hw
  · intro h
    obtain ⟨v, hn, hv⟩ :=
      (p.field.infeasible_iff_forbidden_derivation p.seeds p.forbidden).mp h
    obtain ⟨w, _, hw⟩ := witness_complete p hn hv
    exact ⟨w, hw⟩

end ProofPath.Trace
