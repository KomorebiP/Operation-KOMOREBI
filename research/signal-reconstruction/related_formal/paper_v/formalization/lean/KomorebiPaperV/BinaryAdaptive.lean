import Mathlib.Basic.Real.Basic
import Mathlib.Tactic

/-!
Author: Komorebi P.
Checked source. Finite, possibly unbalanced BINARY trees.
Cuts are defined recursively. The bridge to set-valued antichains of arbitrary
finite arity is not included. Parent conservation is an explicit hypothesis.
-/

namespace KomorebiPaperV.Binary

inductive Tree (A : Type*) where
  | leaf : A → Tree A
  | branch : A → Tree A → Tree A → Tree A

variable {A E : Type*}

def label : Tree A → A
  | .leaf a => a
  | .branch a _ _ => a

inductive Cut : Tree A → Type _ where
  | stop (t : Tree A) : Cut t
  | split {a : A} {l r : Tree A} : Cut l → Cut r → Cut (.branch a l r)

def cutSum [Add E] (p : A → E) : {t : Tree A} → Cut t → E
  | t, .stop _ => p (label t)
  | _, .split l r => cutSum p l + cutSum p r

def conserves [Add E] (p : A → E) : Tree A → Prop
  | .leaf _ => True
  | .branch a l r =>
      p a = p (label l) + p (label r) ∧ conserves p l ∧ conserves p r

theorem cutSum_eq_root [Add E] (p : A → E) {t : Tree A} (q : Cut t) :
    conserves p t → cutSum p q = p (label t) := by
  induction q with
  | stop t =>
    intro _
    rfl
  | split ql qr ihl ihr =>
    intro h
    rcases h with ⟨hp, hl, hr⟩
    change cutSum p ql + cutSum p qr = _
    rw [ihl hl, ihr hr]
    exact hp.symm

noncomputable def value (c : A → ℝ) : Tree A → ℝ
  | .leaf a => c a
  | .branch a l r => min (c a) (value c l + value c r)

noncomputable def best (c : A → ℝ) : (t : Tree A) → Cut t
  | .leaf a => .stop (.leaf a)
  | .branch a l r =>
      if c a ≤ value c l + value c r then .stop (.branch a l r)
      else .split (best c l) (best c r)

theorem value_le_cost (c : A → ℝ) {t : Tree A} (q : Cut t) :
    value c t ≤ cutSum c q := by
  induction q with
  | stop t =>
    cases t with
    | leaf a => exact le_rfl
    | branch a l r => exact min_le_left _ _
  | split ql qr ihl ihr =>
    exact le_trans (min_le_right _ _) (add_le_add ihl ihr)

theorem best_cost (c : A → ℝ) (t : Tree A) :
    cutSum c (best c t) = value c t := by
  induction t with
  | leaf a => rfl
  | branch a l r ihl ihr =>
    by_cases h : c a ≤ value c l + value c r
    · simp [best, h, cutSum, label, value]
    · have h' : value c l + value c r ≤ c a := by linarith
      simp [best, h, cutSum, ihl, ihr, value, min_eq_right h']

theorem best_is_global_minimum (c : A → ℝ) {t : Tree A} (q : Cut t) :
    cutSum c (best c t) ≤ cutSum c q := by
  rw [best_cost]
  exact value_le_cost c q

noncomputable def envelope (e : A → ℝ) : Tree A → ℝ
  | .leaf a => e a
  | .branch a l r => max (e a) (envelope e l + envelope e r)

theorem root_le_envelope (e : A → ℝ) (t : Tree A) :
    e (label t) ≤ envelope e t := by
  cases t with
  | leaf a => exact le_rfl
  | branch a l r => exact le_max_left _ _

theorem cut_perturbation (c d e : A → ℝ)
    (h : ∀ a, |d a - c a| ≤ e a) {t : Tree A} (q : Cut t) :
    |cutSum d q - cutSum c q| ≤ envelope e t := by
  induction q with
  | stop t =>
    exact le_trans (h (label t)) (root_le_envelope e t)
  | @split a l r ql qr ihl ihr =>
    change |(cutSum d ql + cutSum d qr) - (cutSum c ql + cutSum c qr)| ≤ _
    calc
      |(cutSum d ql + cutSum d qr) - (cutSum c ql + cutSum c qr)| =
          |(cutSum d ql - cutSum c ql) + (cutSum d qr - cutSum c qr)| := by
            congr 1
            ring
      _ ≤ |cutSum d ql - cutSum c ql| + |cutSum d qr - cutSum c qr| := abs_add_le _ _
      _ ≤ envelope e l + envelope e r := add_le_add ihl ihr
      _ ≤ envelope e (.branch a l r) := le_max_right _ _

end KomorebiPaperV.Binary
