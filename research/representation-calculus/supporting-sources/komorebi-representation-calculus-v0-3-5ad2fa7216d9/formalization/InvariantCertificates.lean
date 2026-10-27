import FiniteCertificates

namespace Komorebi.Representation
universe u v w z
variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z}

-- Predicate certificates for unary dynamics. These statements concern orbit SETS;
-- applying them to module spans additionally requires linear/submodule closure.
theorem invariant_predicate_run (S : System X A O V) (P : X → Prop)
    (hs : ∀ a x, P x → P (S.step a x)) (x : X) (hx : P x) (w : List A) :
    P (run S w x) := by
  induction w generalizing x with
  | nil => exact hx
  | cons a w ih => exact ih (S.step a x) (hs a x hx)

theorem invariant_intersection (S : System X A O V) (P Q : X → Prop)
    (hp : ∀ a x, P x → P (S.step a x))
    (hq : ∀ a x, Q x → Q (S.step a x)) :
    ∀ a x, (P x ∧ Q x) → (P (S.step a x) ∧ Q (S.step a x)) :=
  fun a x h => ⟨hp a x h.1, hq a x h.2⟩

theorem fixed_fiber_invariant (S : System X A O V) (F : A → Y → Y)
    (q : X → Y) (b : Y)
    (hc : ∀ a x, q (S.step a x) = F a (q x))
    (hb : ∀ a, F a b = b) :
    ∀ a x, q x = b → q (S.step a x) = b := by
  intro a x h
  rw [hc, h, hb]

theorem fixed_fiber_excludes_state (S : System X A O V) (F : A → Y → Y)
    (q : X → Y) (b : Y) (x0 z : X)
    (hc : ∀ a x, q (S.step a x) = F a (q x))
    (hb : ∀ a, F a b = b) (h0 : q x0 = b) (hz : q z ≠ b) :
    ¬ ∃ w, run S w x0 = z := by
  intro ⟨w,hw⟩
  apply hz
  rw [← hw]
  exact invariant_predicate_run S (fun x => q x = b)
    (fixed_fiber_invariant S F q b hc hb) x0 h0 w

def Reachable (S : System X A O V) (x0 x : X) : Prop := ∃ w, run S w x0 = x

theorem witnessed_closed_exact (S : System X A O V) (x0 : X) (P : X → Prop)
    (hw : ∀ x, P x → Reachable S x0 x) (h0 : P x0)
    (hc : ∀ a x, P x → P (S.step a x)) :
    ∀ x, P x ↔ Reachable S x0 x := by
  intro x
  constructor
  · exact hw x
  · intro ⟨w,h⟩
    rw [← h]
    exact invariant_predicate_run S P hc x0 h0 w

-- This is the rank argument used by finite refinement. Identifying a concrete
-- rank with row-module length/cardinality is a separate algebraic obligation.
theorem finite_rank_has_plateau (f : Nat → Nat) (B : Nat)
    (hbound : ∀ n, f n ≤ B) (hmono : ∀ n, f n ≤ f (n+1)) :
    ∃ n, n ≤ B ∧ f n = f (n+1) := by
  classical
  apply Classical.byContradiction
  intro hnone
  have strict : ∀ n, n ≤ B → f n < f (n+1) := by
    intro n hn
    have hne : f n ≠ f (n+1) := fun h => hnone ⟨n,hn,h⟩
    have hm := hmono n
    omega
  have grow : ∀ n, n ≤ B+1 → n ≤ f n := by
    intro n
    induction n with
    | zero => intro _; exact Nat.zero_le _
    | succ n ih =>
      intro hn
      have hnb : n ≤ B := by omega
      have hprev := ih (by omega)
      have hnext := strict n hnb
      omega
  have hg := grow (B+1) (Nat.le_refl _)
  have hb := hbound (B+1)
  omega

end Komorebi.Representation
