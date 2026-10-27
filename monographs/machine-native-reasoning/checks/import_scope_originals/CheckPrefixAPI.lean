import MachineTheory
open Komorebi.MachineTheory HardInquiry OrderedCompiler BinaryDiagnosis

/-- The integer capacity-completion theorem has the source's actual quantifiers. -/
example (m C a b : ℤ) (hC : 1≤C) (hm : 2≤m) (hsize : m≤2*C)
    (ha : 0≤a) (hb : 0≤b) (hr : a+b≤m) :
    (∃ u v : ℤ, 0≤u ∧ 0≤v ∧ u+v=m-a-b ∧ a+u≤C ∧ b+v≤C) ↔ max a b≤C :=
  PrefixScan.integer_completion_iff m C a b hC hm hsize ha hb hr

variable {X E C : Type} [DecidableEq X]

/-- A retained prefix excludes ALL valid completions of that actual root. -/
example (M : Model X E Bool C Unit) (s : Scope M) (h : ℕ)
    (V P : Finset X) (hp : P⊆V) (e : E) (o : Bool)
    (hc : 2^h < (P.filter (fun x => M.observe e x=o)).card) :
    ¬ ∃ k : Bool → Option (Tree E Bool C h), M.Valid (h+1) V (.inr (e,k)) :=
  prefix_exclusion M s h V P hp e o hc

omit [DecidableEq X] in
/-- Exact ordered syntax is preserved, rather than just existence of some solution. -/
example (M : Model X E Bool C Unit) (es : List E) (cs : List C) (h : ℕ) (xs : List X) :
    (search streamScanner M es cs h xs).answer=(search fullScanner M es cs h xs).answer ∧
    (search streamScanner M es cs h xs).reads≤(search fullScanner M es cs h xs).reads :=
  streaming_preserves_search M es cs h xs

example (M : Model X E Bool C Unit) (s : Scope M) (es : List E) (cs : List C)
    (he : ∀ e,e∈es) (hc : ∀ c,c∈cs) (h : ℕ) (xs : List X) (hn : xs.Nodup) :
    (∀ t, (search streamScanner M es cs h xs).answer=some t → M.Valid h xs.toFinset t) ∧
    ((search streamScanner M es cs h xs).answer=none ↔
      ¬ ∃ t : Tree E Bool C h,M.Valid h xs.toFinset t) :=
  streaming_sound_complete M s es cs he hc h xs hn

variable [Fintype X] [Fintype E] [DecidableEq E] [Fintype C] [DecidableEq C]

example (M : Model X E Bool C Unit) (es : List E) (cs : List C) (h : ℕ) (xs : List X)
    (r : Run (Tree E Bool C h)) (hr : checkedSearch M es cs h xs=some r) :
    (∀ t,r.answer=some t → M.Valid h xs.toFinset t) ∧
    (r.answer=none ↔ ¬ ∃ t : Tree E Bool C h,M.Valid h xs.toFinset t) :=
  admitted_search_sound_complete M es cs h xs r hr
