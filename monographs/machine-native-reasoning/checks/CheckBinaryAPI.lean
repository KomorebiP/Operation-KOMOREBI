import MachineTheory.BinaryExamples
open Komorebi.MachineTheory HardInquiry BinaryDiagnosis
open Finset

/-- Independent restatement exposes the source premises instead of assuming leaf counts. -/
example {X E C : Type} [DecidableEq X] (M : Model X E Bool C Unit)
    (hi : ∀ e x, M.next e x = x)
    (hs : ∀ c x y, M.accept x c = true → M.accept y c = true → x=y)
    (hq : ∀ e, M.stepCost e ()=1)
    (hc : ∀ c V, V.Nonempty → M.terminalCost c V ()=1)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (hv : M.Valid h V t) :
    1 + Nat.clog 2 V.card ≤ (M.profile h V t).1 () ∧
      2*V.card-1 ≤ (M.profile h V t).2 :=
  (binary_lower_bounds M ⟨hi,hs,hq,hc⟩ h V t hv).2

example {X E C : Type} [DecidableEq X] [Fintype E] [Fintype C]
    (M : Model X E Bool C Unit) (s : Scope M) (h : ℕ) (V : Finset X)
    (t : Tree E Bool C h) (hv : M.Valid h V t)
    (hw : (M.profile h V t).1 ()=1+Nat.clog 2 V.card)
    (hm : (M.profile h V t).2=2*V.card-1) :
    M.solve h V = {(fun _ => 1+Nat.clog 2 V.card,2*V.card-1)} :=
  checked_candidate_closes_frontier M s h V t hv hw hm

example {X E C : Type} [Fintype X] [DecidableEq X] [Fintype E] [Fintype C]
    (M : Model X E Bool C Unit) (h : ℕ) (V : Finset X) (t : Tree E Bool C h)
    (ha : admissionCheck M h V t = true) :
    M.compute h V = {(fun _ => 1+Nat.clog 2 V.card,2*V.card-1)} :=
  admitted_frontier M h V t ha

example {X E C : Type} [DecidableEq X] (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (hv : M.Valid h V t) :
    (M.profile h V t).2 = 2*V.card-1+unary h t := records_exact M s h V t hv

example (n : ℕ) : BinaryExamples.eight.solve (3+n) univ = {(fun _ => 4,15)} :=
  BinaryExamples.eight_frontier_all n

