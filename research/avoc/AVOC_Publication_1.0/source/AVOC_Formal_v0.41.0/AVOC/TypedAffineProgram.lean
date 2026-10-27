import AVOC.AffineSignature
import Lean.Elab.Tactic.Omega

namespace Komorebi.AVOC.Affine

/-- Different dimensional types cannot be silently connected. -/
inductive Program (Atom : Nat → Nat → Type) : Nat → Nat → Type where
  | atom {n m} : Atom n m → Program Atom n m
  | ident {n} : Program Atom n n
  | seq {n m k} : Program Atom n m → Program Atom m k → Program Atom n k
  | plus {n m} : Program Atom n m → Program Atom n m → Program Atom n m

variable {R : Type} [Ring R] {Atom : Nat → Nat → Type}

/-- Coefficient semantics normalize all compositions, without enumerating R^n. -/
def normalize (a : ∀ {n m}, Atom n m → Signature R n m) :
    {n m : Nat} → Program Atom n m → Signature R n m
  | _, _, .atom f => a f
  | _, _, .ident => identity _
  | _, _, .seq f g => compose (normalize a g) (normalize a f)
  | _, _, .plus f g => add (normalize a f) (normalize a g)

/-- Independent compositional execution semantics. -/
def run (a : ∀ {n m}, Atom n m → Signature R n m) :
    {n m : Nat} → Program Atom n m → (Fin n → R) → (Fin m → R)
  | _, _, .atom f, x => eval (a f) x
  | _, _, .ident, x => x
  | _, _, .seq f g, x => run a g (run a f x)
  | _, _, .plus f g, x => run a f x + run a g x

@[simp] theorem normalize_correct (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m} (p : Program Atom n m) (x : Fin n → R) :
    eval (normalize a p) x = run a p x := by
  induction p with
  | atom f => rfl
  | ident => simp [normalize, run]
  | seq f g ihf ihg => simp [normalize, run, ihf, ihg]
  | plus f g ihf ihg => simp [normalize, run, ihf, ihg]

def Equivalent (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m} (p q : Program Atom n m) : Prop := ∀ x, run a p x = run a q x

theorem normalized_iff_equivalent (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m} (p q : Program Atom n m) : normalize a p = normalize a q ↔ Equivalent a p q := by
  rw [eq_iff_eval]
  simp only [normalize_correct, Equivalent]

def checkProgram [DecidableEq R] (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m} (p q : Program Atom n m) : Bool := check (normalize a p) (normalize a q)

theorem checkProgram_iff [DecidableEq R] (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m} (p q : Program Atom n m) : checkProgram a p q = true ↔ Equivalent a p q := by
  rw [checkProgram, check_iff]
  simp only [normalize_correct, Equivalent]

theorem finite_probe_complete (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m} (p q : Program Atom n m)
    (h0 : run a p 0 = run a q 0)
    (hb : ∀ j : Fin n, run a p (basis j) = run a q (basis j)) : Equivalent a p q := by
  apply (normalized_iff_equivalent a p q).1
  apply eq_of_zero_basis
  · simpa only [normalize_correct] using h0
  · intro j; simpa only [normalize_correct] using hb j

theorem seq_congr (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m k} {p p' : Program Atom n m} {q q' : Program Atom m k}
    (hp : Equivalent a p p') (hq : Equivalent a q q') :
    Equivalent a (.seq p q) (.seq p' q') := by
  intro x
  simp only [run, hp x]
  exact hq _

theorem plus_congr (a : ∀ {n m}, Atom n m → Signature R n m)
    {n m} {p p' q q' : Program Atom n m}
    (hp : Equivalent a p p') (hq : Equivalent a q q') :
    Equivalent a (.plus p q) (.plus p' q') := by
  intro x; simp only [run, hp x, hq x]

/-- Typed one-hole contexts support safe replacements at any nesting depth. -/
inductive Context (Atom : Nat → Nat → Type) (i o : Nat) : Nat → Nat → Type where
  | hole : Context Atom i o i o
  | before {n m k} : Program Atom n m → Context Atom i o m k → Context Atom i o n k
  | after {n m k} : Context Atom i o n m → Program Atom m k → Context Atom i o n k
  | sumLeft {n m} : Context Atom i o n m → Program Atom n m → Context Atom i o n m
  | sumRight {n m} : Program Atom n m → Context Atom i o n m → Context Atom i o n m

def plug {i o} : {n m : Nat} → Context Atom i o n m → Program Atom i o → Program Atom n m
  | _, _, .hole, p => p
  | _, _, .before f c, p => .seq f (plug c p)
  | _, _, .after c g, p => .seq (plug c p) g
  | _, _, .sumLeft c f, p => .plus (plug c p) f
  | _, _, .sumRight f c, p => .plus f (plug c p)

theorem context_congr (a : ∀ {n m}, Atom n m → Signature R n m)
    {i o n m} (c : Context Atom i o n m) {p q : Program Atom i o}
    (h : Equivalent a p q) : Equivalent a (plug c p) (plug c q) := by
  induction c with
  | hole => exact h
  | before f c ih => exact seq_congr a (fun _ => rfl) ih
  | after c g ih => exact seq_congr a ih (fun _ => rfl)
  | sumLeft c f ih => exact plus_congr a ih (fun _ => rfl)
  | sumRight f c ih => exact plus_congr a (fun _ => rfl) ih

/-- A declared nonnegative primitive tariff and eager pointwise-addition tariff. -/
def cost (w : ∀ {n m}, Atom n m → Nat) : {n m : Nat} → Program Atom n m → Nat
  | _, _, .atom f => w f
  | _, _, .ident => 0
  | _, _, .seq f g => cost w f + cost w g
  | _, m, .plus f g => cost w f + cost w g + m

theorem context_cost_mono (w : ∀ {n m}, Atom n m → Nat)
    {i o n m} (c : Context Atom i o n m) {p q : Program Atom i o}
    (h : cost w p ≤ cost w q) : cost w (plug c p) ≤ cost w (plug c q) := by
  induction c with
  | hole => exact h
  | before f c ih => simp only [plug, cost]; omega
  | after c g ih => simp only [plug, cost]; omega
  | sumLeft c f ih => simp only [plug, cost]; omega
  | sumRight f c ih => simp only [plug, cost]; omega

/-- Cost certificates are dimension-indexed, not Bool3 tables. -/
structure LowerValid (a : ∀ {n m}, Atom n m → Signature R n m)
    (w : ∀ {n m}, Atom n m → Nat)
    (lb : ∀ {n m}, Signature R n m → Nat) : Prop where
  atom : ∀ {n m} (f : Atom n m), lb (a f) ≤ w f
  ident : ∀ n, lb (identity (R:=R) n) ≤ 0
  seq : ∀ {n m k} (f : Signature R n m) (g : Signature R m k),
    lb (compose g f) ≤ lb f + lb g
  plus : ∀ {n m} (f g : Signature R n m), lb (add f g) ≤ lb f + lb g + m

theorem lower_bound (a : ∀ {n m}, Atom n m → Signature R n m)
    (w : ∀ {n m}, Atom n m → Nat) (lb : ∀ {n m}, Signature R n m → Nat)
    (h : LowerValid a w lb) {n m} (p : Program Atom n m) : lb (normalize a p) ≤ cost w p := by
  induction p with
  | atom f => exact h.atom f
  | ident => exact h.ident _
  | seq f g ihf ihg =>
      have hs := h.seq (normalize a f) (normalize a g)
      simp only [normalize, cost]; omega
  | plus f g ihf ihg =>
      have hs := h.plus (normalize a f) (normalize a g)
      simp only [normalize, cost]; omega

theorem attained_global_minimum (a : ∀ {n m}, Atom n m → Signature R n m)
    (w : ∀ {n m}, Atom n m → Nat) (lb : ∀ {n m}, Signature R n m → Nat)
    (h : LowerValid a w lb) {n m} (witness : Program Atom n m)
    (hw : cost w witness = lb (normalize a witness))
    (p : Program Atom n m) (he : Equivalent a p witness) : cost w witness ≤ cost w p := by
  have hh := lower_bound a w lb h p
  rw [(normalized_iff_equivalent a p witness).2 he] at hh
  simpa only [hw] using hh

end Komorebi.AVOC.Affine
