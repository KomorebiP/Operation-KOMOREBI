import MachineTheory.Synthesis

/-!
# Sound ordered semantic compression

Reviewed Core 6.2. The quotient keeps the first ORIGINAL syntax value at each key.
Keys are an external checked interface. A soundness premise is not replaced by
finite probe agreement. The same scan, teacher, target and retained-example order
are used on both sides. Preparation, key comparisons, index storage and dispatch
are not included in the retained-example comparison counter.
-/

namespace Komorebi.MachineTheory.Synthesis

universe u v w z
variable {P : Type u} {D : Type v} {Y : Type w} {K : Type z}
variable [DecidableEq Y] [DecidableEq K]

/-- Only one direction of semantic identification is required. -/
def KeySound (T : Task P D Y) (key : P → K) : Prop :=
  ∀ p q, key p = key q → ∀ x, T.eval p x = T.eval q x

/-- Prefix keys have already been refuted by persistent available evidence. -/
def KeysRefuted (T : Task P D Y) (key : P → K) (seen : List K) (E : List D) : Prop :=
  ∀ p, key p ∈ seen → Refuted T E p

/-- Keep the first original AST at each key, never its normalized replacement. -/
def representatives (key : P → K) : List K → List P → List P
  | _, [] => []
  | seen, p :: ps =>
    if key p ∈ seen then representatives key seen ps
    else p :: representatives key (key p :: seen) ps

omit [DecidableEq Y] in
theorem refuted_cons (T : Task P D Y) {E : List D} {p : P}
    (h : Refuted T E p) (x : D) : Refuted T (x :: E) p := by
  rcases h with ⟨y, hy, hdiff⟩
  exact ⟨y, List.mem_cons_of_mem x hy, hdiff⟩

omit [DecidableEq Y] [DecidableEq K] in
theorem keysRefuted_cons_evidence (T : Task P D Y) (key : P → K)
    {seen : List K} {E : List D} (h : KeysRefuted T key seen E) (x : D) :
    KeysRefuted T key seen (x :: E) := by
  intro p hp
  exact refuted_cons T (h p hp) x

omit [DecidableEq Y] [DecidableEq K] in
theorem keysRefuted_add_key (T : Task P D Y) (key : P → K)
    (hs : KeySound T key) {seen : List K} {E : List D}
    (h : KeysRefuted T key seen E) {p : P} (hp : Refuted T E p) :
    KeysRefuted T key (key p :: seen) E := by
  intro q hq
  rcases List.mem_cons.mp hq with hqp | hq
  · rcases hp with ⟨x, hx, hdiff⟩
    refine ⟨x, hx, ?_⟩
    rw [hs q p hqp x]
    exact hdiff
  · exact h q hq

theorem representatives_sublist (key : P → K) (seen : List K) (G : List P) :
    (representatives key seen G).Sublist G := by
  induction G generalizing seen with
  | nil => exact List.Sublist.refl []
  | cons p ps ih =>
    by_cases hk : key p ∈ seen
    · simpa [representatives, hk] using (ih seen).cons p
    · simpa [representatives, hk] using (ih (key p :: seen)).cons_cons p

/-- The deletion invariant proves full trace equality, not merely equal outputs. -/
theorem compression_invariant (T : Task P D Y) (key : P → K) (hs : KeySound T key)
    (G : List P) (seen : List K) (E : List D)
    (hseen : KeysRefuted T key seen E) :
    SameEvidence (scan T (representatives key seen G) E) (scan T G E) ∧
    (scan T (representatives key seen G) E).comparisons ≤ (scan T G E).comparisons ∧
    (scan T (representatives key seen G) E).visits ≤ (scan T G E).visits := by
  induction G generalizing seen E with
  | nil => simp [scan, representatives, SameEvidence]
  | cons p ps ih =>
    by_cases hk : key p ∈ seen
    · have hr := (refuted_iff_inspect_ne_none T E p).mp (hseen p hk)
      cases hc : (inspect T p E).1 with
      | none => exact False.elim (hr hc)
      | some x =>
        obtain ⟨⟨ha, ht, he⟩, hcost, hvis⟩ := ih seen E hseen
        simp only [representatives, hk, ↓reduceIte, scan, hc, SameEvidence]
        exact ⟨⟨ha, ht, he⟩, by omega, by omega⟩
    · cases hc : (inspect T p E).1 with
      | some x =>
        have hp : Refuted T E p := ⟨x, (inspect_some T p E x hc).1,
          (inspect_some T p E x hc).2⟩
        have hn := keysRefuted_add_key T key hs hseen hp
        obtain ⟨⟨ha, ht, he⟩, hcost, hvis⟩ := ih (key p :: seen) E hn
        simp only [representatives, hk, ↓reduceIte, scan, hc, SameEvidence]
        exact ⟨⟨ha, ht, he⟩, Nat.add_le_add_left hcost _, Nat.add_le_add_left hvis _⟩
      | none =>
        cases ht : teacher T p with
        | none => simp [representatives, hk, scan, hc, ht, SameEvidence]
        | some x =>
          have hp : Refuted T (x :: E) p :=
            ⟨x, List.mem_cons_self, teacher_refutes T ht⟩
          have hn := keysRefuted_add_key T key hs
            (keysRefuted_cons_evidence T key hseen x) hp
          obtain ⟨⟨ha, htr, he⟩, hcost, hvis⟩ := ih (key p :: seen) (x :: E) hn
          simp only [representatives, hk, ↓reduceIte, scan, hc, ht, SameEvidence]
          exact ⟨⟨ha, congrArg ((p, some x) :: ·) htr, he⟩,
            Nat.add_le_add_left hcost _, Nat.add_le_add_left hvis _⟩

/-- Core 6.2: exact AST/reply/evidence preservation and nonincreasing search checks. -/
theorem ordered_compression (T : Task P D Y) (key : P → K) (hs : KeySound T key)
    (G : List P) (E : List D) :
    SameEvidence (scan T (representatives key [] G) E) (scan T G E) ∧
    (scan T (representatives key [] G) E).comparisons ≤ (scan T G E).comparisons ∧
    (scan T (representatives key [] G) E).visits ≤ (scan T G E).visits :=
  compression_invariant T key hs G [] E (by simp [KeysRefuted])

/-- Both front ends invoke the very same finite-context teacher on the same ASTs. -/
def teacherComparisons (T : Task P D Y) (r : Result P D) : Nat :=
  (r.transcript.map (fun e => (inspect T e.1 T.contexts).2)).sum

theorem teacher_work_preserved (T : Task P D Y) (key : P → K) (hs : KeySound T key)
    (G : List P) (E : List D) :
    teacherComparisons T (scan T (representatives key [] G) E) =
      teacherComparisons T (scan T G E) := by
  unfold teacherComparisons
  rw [(ordered_compression T key hs G E).1.2.1]

/-- Only admissible-domain soundness is used; no semantic completeness is needed. -/
theorem representative_search_complete (T : Task P D Y) (key : P → K)
    (hs : KeySound T key) (G : List P) (E : List D) :
    (scan T (representatives key [] G) E).answer = none ↔
      ∀ p ∈ G, ¬ Correct T p := by
  rw [(ordered_compression T key hs G E).1.1]
  exact exhaustion_iff T G E


/-- Actual key-comparison work of the simple list-backed representative index. -/
def lookupKey (k : K) : List K → Bool × Nat
  | [] => (false, 0)
  | q :: qs => if k = q then (true, 1) else
      let r := lookupKey k qs
      (r.1, 1 + r.2)

@[simp] theorem lookupKey_value (k : K) (seen : List K) :
    (lookupKey k seen).1 = decide (k ∈ seen) := by
  induction seen with
  | nil => simp [lookupKey]
  | cons q qs ih =>
    by_cases h : k = q
    · simp [lookupKey, h]
    · simp [lookupKey, h, ih]

/-- Only equality comparisons are metered here; key computation and storage are separate. -/
def prepare (key : P → K) : List K → List P → List P × Nat
  | _, [] => ([], 0)
  | seen, p :: ps =>
    let q := lookupKey (key p) seen
    if q.1 then
      let r := prepare key seen ps
      (r.1, q.2 + r.2)
    else
      let r := prepare key (key p :: seen) ps
      (p :: r.1, q.2 + r.2)

theorem prepare_value (key : P → K) (seen : List K) (G : List P) :
    (prepare key seen G).1 = representatives key seen G := by
  induction G generalizing seen with
  | nil => rfl
  | cons p ps ih =>
    by_cases h : key p ∈ seen
    · simp [prepare, representatives, h, ih]
    · simp [prepare, representatives, h, ih]

end Komorebi.MachineTheory.Synthesis
