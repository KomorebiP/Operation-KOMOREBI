import MachineTheory.SynthesisTrace

/-!
# Any truthful counterexample choice obeys the finite bound

Core 6.1 does not need a first-counterexample oracle. This relation admits any
truthful reply at each call, including history-dependent choices, and also finite
open prefixes. The fixed complete teacher is used only for the actual reference
implementation and for Core 6.2's exact-trace comparison.
-/

namespace Komorebi.MachineTheory.Synthesis

universe u v w
variable {P : Type u} {D : Type v} {Y : Type w} [DecidableEq Y]

inductive TraceStatus (P : Type u) where
  | pending | exhausted | accepted (p : P)
  deriving Repr, DecidableEq

/-- The last constructor permits a truthful teacher to choose any counterexample. -/
inductive TruthfulProtocol (T : Task P D Y) (G : List P) :
    List D → List (P × Option D) → TraceStatus P → Prop
  | pending (E) : TruthfulProtocol T G E [] .pending
  | exhausted (E) (h : select T G E = none) : TruthfulProtocol T G E [] .exhausted
  | accepted (E p) (hs : select T G E = some p) (hc : Correct T p) :
      TruthfulProtocol T G E [(p,none)] (.accepted p)
  | rejected (E p x tr out) (hs : select T G E = some p)
      (hx : T.eval p x ≠ T.target x) (rest : TruthfulProtocol T G (x :: E) tr out) :
      TruthfulProtocol T G E ((p,some x) :: tr) out

theorem truthful_excludes_refuted (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {out : TraceStatus P}
    (h : TruthfulProtocol T G E tr out) {p : P} (hp : Refuted T E p) :
    p ∉ tr.map Prod.fst := by
  induction h with
  | pending => simp
  | exhausted => simp
  | accepted E q hs hc =>
    have hn : p ≠ q := by
      intro he; subst q
      exact refuted_not_consistent T hp (select_some_consistent T G E hs)
    simpa using hn
  | rejected E q x tr out hs hx rest ih =>
    have hn : p ≠ q := by
      intro he; subst q
      exact refuted_not_consistent T hp (select_some_consistent T G E hs)
    simpa using And.intro hn (ih (refuted_cons T hp x))

theorem truthful_nodup (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {out : TraceStatus P}
    (h : TruthfulProtocol T G E tr out) : (tr.map Prod.fst).Nodup := by
  induction h with
  | pending => simp
  | exhausted => simp
  | accepted => simp
  | rejected E p x tr out hs hx rest ih =>
    have hr : Refuted T (x :: E) p := ⟨x, List.mem_cons_self, hx⟩
    simpa using And.intro (truthful_excludes_refuted T rest hr) ih

theorem truthful_members (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {out : TraceStatus P}
    (h : TruthfulProtocol T G E tr out) : tr.map Prod.fst ⊆ G := by
  induction h with
  | pending => simp
  | exhausted => simp
  | accepted E p hs hc =>
    have hp : p ∈ G := List.mem_of_find?_eq_some hs
    simpa using hp
  | rejected E p x tr out hs hx rest ih =>
    have hp : p ∈ G := List.mem_of_find?_eq_some hs
    simpa using And.intro hp ih

/-- Applies even to open finite prefixes and arbitrary truthful reply choices. -/
theorem truthful_call_bound (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {out : TraceStatus P}
    (h : TruthfulProtocol T G E tr out) : tr.length ≤ G.length := by
  simpa using (truthful_nodup T h).length_le_of_subset (truthful_members T h)

/-- An unbounded sequence of truthful teacher calls would give an impossible prefix. -/
theorem no_unbounded_truthful_calls (T : Task P D Y) (G : List P) (E : List D) :
    ¬ (∀ n : Nat, ∃ tr out, TruthfulProtocol T G E tr out ∧ tr.length = n) := by
  intro h
  obtain ⟨tr, out, hr, hn⟩ := h (G.length + 1)
  have hb := truthful_call_bound T hr
  omega

/-- Current finite exhaustion is an explicit statement about the declared grammar. -/
theorem select_none_excludes_correct (T : Task P D Y) (G : List P) (E : List D)
    (h : select T G E = none) : ∀ p ∈ G, ¬ Correct T p := by
  have hh := List.find?_eq_none.mp h
  intro p hp hc
  have hn := hh p hp
  have hi := inspect_none_of_correct T hc E
  simp [hi] at hn

/-- The earliest consistent correct entry is the earliest globally correct entry. -/
theorem selected_correct_is_first (T : Task P D Y) (G : List P) (E : List D) {p : P}
    (h : select T G E = some p) (hc : Correct T p) :
    G.find? (fun q => (teacher T q).isNone) = some p := by
  have hsplit := List.find?_eq_some_iff_append.mp h
  rcases hsplit with ⟨_, before, after, hG, hbefore⟩
  apply List.find?_eq_some_iff_append.mpr
  refine ⟨Option.isNone_iff_eq_none.mpr ((teacher_accepts_iff T p).mpr hc), before, after, hG, ?_⟩
  intro q hq
  have hbad := hbefore q hq
  have hnot : ¬ Correct T q := by
    intro hgood
    have he := inspect_none_of_correct T hgood E
    simp [he] at hbad
  cases ht : teacher T q with
  | none => exact False.elim (hnot ((teacher_accepts_iff T q).mp ht))
  | some x => rfl

/-- Final answers and grammar exhaustion are sound for ANY truthful protocol. -/
theorem truthful_outcome (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {out : TraceStatus P}
    (h : TruthfulProtocol T G E tr out) :
    (∀ p, out = .accepted p → G.find? (fun q => (teacher T q).isNone) = some p) ∧
    (out = .exhausted → ∀ p ∈ G, ¬ Correct T p) := by
  induction h with
  | pending => simp
  | exhausted E hs =>
    exact ⟨by simp, fun _ => select_none_excludes_correct T G E hs⟩
  | accepted E p hs hc =>
    constructor
    · intro q hq
      cases hq
      exact selected_correct_is_first T G E hs hc
    · simp
  | rejected E p x tr out hs hx rest ih => exact ih

/-- The executable complete teacher is one realization of the general reply contract. -/
theorem protocol_is_truthful (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {ans : Option P} (h : Protocol T G E tr ans) :
    TruthfulProtocol T G E tr (match ans with | none => .exhausted | some p => .accepted p) := by
  induction h with
  | exhausted E hs => exact TruthfulProtocol.exhausted E hs
  | accepted E p hs ht => exact TruthfulProtocol.accepted E p hs ((teacher_accepts_iff T p).mp ht)
  | rejected E p x tr ans hs ht rest ih =>
    cases ans <;> exact TruthfulProtocol.rejected E p x tr _ hs (teacher_refutes T ht) ih

end Komorebi.MachineTheory.Synthesis
