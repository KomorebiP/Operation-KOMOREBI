import MachineTheory.SynthesisQuotient

/-!
# The scan is the stated restart-earliest protocol

The operational relation searches the entire original grammar again at each
teacher call. Its proof from `scan` shows that omitting already refuted prefixes
changes neither submissions nor retained evidence. Repeated syntax entries in a
list cannot cause repeated submission after rejection.
-/

namespace Komorebi.MachineTheory.Synthesis

universe u v w
variable {P : Type u} {D : Type v} {Y : Type w} [DecidableEq Y]

def select (T : Task P D Y) (G : List P) (E : List D) : Option P :=
  G.find? (fun p => ((inspect T p E).1).isNone)

theorem select_some_consistent (T : Task P D Y) (G : List P) (E : List D)
    {p : P} (h : select T G E = some p) : Consistent T E p := by
  have hh := List.find?_some h
  exact (inspect_none_iff T p E).mp (Option.isNone_iff_eq_none.mp hh)

omit [DecidableEq Y] in
theorem refuted_not_consistent (T : Task P D Y) {E : List D} {p : P}
    (h : Refuted T E p) : ¬ Consistent T E p := by
  rcases h with ⟨x, hx, hdiff⟩
  exact fun hc => hdiff (hc x hx)

theorem select_refuted_prefix (T : Task P D Y) (B G : List P) (E : List D)
    (hb : ∀ p ∈ B, Refuted T E p) : select T (B ++ G) E = select T G E := by
  induction B with
  | nil => rfl
  | cons p ps ih =>
    have hn := (refuted_iff_inspect_ne_none T E p).mp (hb p List.mem_cons_self)
    have ht : ∀ q ∈ ps, Refuted T E q := fun q hq => hb q (List.mem_cons_of_mem p hq)
    cases hc : (inspect T p E).1 with
    | none => exact False.elim (hn hc)
    | some x => simpa [select, hc] using ih ht

/-- Genuine earliest-consistent interaction on the WHOLE supplied grammar. -/
inductive Protocol (T : Task P D Y) (G : List P) :
    List D → List (P × Option D) → Option P → Prop
  | exhausted (E) (h : select T G E = none) : Protocol T G E [] none
  | accepted (E p) (hs : select T G E = some p) (ht : teacher T p = none) :
      Protocol T G E [(p, none)] (some p)
  | rejected (E p x tr ans) (hs : select T G E = some p) (ht : teacher T p = some x)
      (rest : Protocol T G (x :: E) tr ans) :
      Protocol T G E ((p, some x) :: tr) ans

/-- Refuted prefixes stay refuted at every later restart of the protocol. -/
theorem protocol_prefix (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {ans : Option P} (h : Protocol T G E tr ans)
    (B : List P) (hb : ∀ p ∈ B, Refuted T E p) : Protocol T (B ++ G) E tr ans := by
  induction h with
  | exhausted E hs =>
    exact Protocol.exhausted E ((select_refuted_prefix T B G E hb).trans hs)
  | accepted E p hs ht =>
    exact Protocol.accepted E p ((select_refuted_prefix T B G E hb).trans hs) ht
  | rejected E p x tr ans hs ht rest ih =>
    apply Protocol.rejected E p x tr ans
      ((select_refuted_prefix T B G E hb).trans hs) ht
    exact ih (fun q hq => refuted_cons T (hb q hq) x)

/-- A structurally recursive implementation realizes the specified learner exactly. -/
theorem scan_protocol (T : Task P D Y) (G : List P) (E : List D) :
    Protocol T G E (scan T G E).transcript (scan T G E).answer := by
  induction G generalizing E with
  | nil => exact Protocol.exhausted E rfl
  | cons p ps ih =>
    cases hc : (inspect T p E).1 with
    | some x =>
      have hp : Refuted T E p :=
        ⟨x, (inspect_some T p E x hc).1, (inspect_some T p E x hc).2⟩
      have hprefix := protocol_prefix T (ih E) [p] (by simpa using hp)
      simpa [scan, hc] using hprefix
    | none =>
      have hs : select T (p :: ps) E = some p := by simp [select, hc]
      cases ht : teacher T p with
      | none => simpa [scan, hc, ht] using Protocol.accepted (T := T) E p hs ht
      | some x =>
        have hp : Refuted T (x :: E) p :=
          ⟨x, List.mem_cons_self, teacher_refutes T ht⟩
        have hprefix := protocol_prefix T (ih (x :: E)) [p] (by simpa using hp)
        simpa [scan, hc, ht] using Protocol.rejected E p x
          (scan T ps (x :: E)).transcript (scan T ps (x :: E)).answer hs ht hprefix

/-- Rejection is exclusion from every future teacher call, even with duplicate syntax. -/
theorem protocol_excludes_refuted (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {ans : Option P} (h : Protocol T G E tr ans)
    {p : P} (hp : Refuted T E p) : p ∉ tr.map Prod.fst := by
  induction h with
  | exhausted => simp
  | accepted E q hs ht =>
    have hne : p ≠ q := by
      intro he
      subst q
      exact refuted_not_consistent T hp (select_some_consistent T G E hs)
    simpa using hne
  | rejected E q x tr ans hs ht rest ih =>
    have hne : p ≠ q := by
      intro he
      subst q
      exact refuted_not_consistent T hp (select_some_consistent T G E hs)
    have hn := ih (refuted_cons T hp x)
    simpa [List.map_cons] using And.intro hne hn

/-- Distinct calls need no duplicate-free assumption on the original catalogue. -/
theorem protocol_nodup (T : Task P D Y) {G : List P} {E : List D}
    {tr : List (P × Option D)} {ans : Option P} (h : Protocol T G E tr ans) :
    (tr.map Prod.fst).Nodup := by
  induction h with
  | exhausted => simp
  | accepted => simp
  | rejected E p x tr ans hs ht rest ih =>
    have hr : Refuted T (x :: E) p := ⟨x, List.mem_cons_self, teacher_refutes T ht⟩
    have hn := protocol_excludes_refuted T rest hr
    simpa using And.intro hn ih

theorem no_repeated_submission (T : Task P D Y) (G : List P) (E : List D) :
    ((scan T G E).transcript.map Prod.fst).Nodup :=
  protocol_nodup T (scan_protocol T G E)

/-- Every reported counterexample, not just initial evidence, remains in final memory. -/
theorem rejected_evidence_retained (T : Task P D Y) (G : List P) (E : List D) :
    ∀ p x, (p, some x) ∈ (scan T G E).transcript → x ∈ (scan T G E).retained := by
  induction G generalizing E with
  | nil => simp [scan]
  | cons p ps ih =>
    cases hc : (inspect T p E).1 with
    | some x => simpa [scan, hc] using ih E
    | none =>
      cases ht : teacher T p with
      | none => simp [scan, hc, ht]
      | some x =>
        intro q y hy
        simp only [scan, hc, ht, List.mem_cons, Prod.mk.injEq, Option.some.injEq] at hy
        simp only [scan, hc, ht]
        rcases hy with ⟨rfl, rfl⟩ | hy
        · exact retained_persistent T ps (y :: E) y List.mem_cons_self
        · exact ih (x :: E) q y hy

/-- Core 6.1, with the actual restart protocol and unconditional no-repeat property. -/
theorem counterexample_guided_synthesis (T : Task P D Y) (G : List P) :
    Protocol T G [] (scan T G []).transcript (scan T G []).answer ∧
    ((scan T G []).transcript.map Prod.fst).Nodup ∧
    (scan T G []).transcript.length ≤ G.length ∧
    ((scan T G []).answer = none ↔ ∀ p ∈ G, ¬ Correct T p) := by
  exact ⟨scan_protocol T G [], no_repeated_submission T G [],
    teacher_calls_le T G [], exhaustion_iff T G []⟩

end Komorebi.MachineTheory.Synthesis
