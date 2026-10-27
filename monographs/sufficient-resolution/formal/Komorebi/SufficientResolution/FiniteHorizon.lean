import Komorebi.SufficientResolution.Behavioral
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.Tactic.Push

/-!
# Finite observation horizon and exact stabilization

`visibleKernel n` consists of states invisible along every chronological word
of length at most n.  A plateau is exact, not heuristic.  If X is finite
 dimensional, stabilization occurs by dim(ker O), even for an infinite alphabet.
Finiteness of the alphabet is required only by the separate enumeration module.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.FiniteHorizon

open Behavioral Module

universe uK uX uY uI
variable {K : Type uK} [Field K]
variable {X : Type uX} [AddCommGroup X] [Module K X]
variable {Y : Type uY} [AddCommGroup Y] [Module K Y]
variable {I : Type uI}
variable (T : I → X →ₗ[K] X) (O : X →ₗ[K] Y)

/-- States invisible through a specified word length, including the empty word. -/
def visibleKernel (n : ℕ) : Submodule K X where
  carrier := {x | ∀ w : List I, w.length ≤ n → O (wordOp T w x) = 0}
  zero_mem' := by simp
  add_mem' := by
    intro x y hx hy w hw
    simp only [map_add, hx w hw, hy w hw, add_zero]
  smul_mem' := by
    intro a x hx w hw
    simp only [map_smul, hx w hw, smul_zero]

 theorem mem_visibleKernel_iff (n : ℕ) (x : X) :
    x ∈ visibleKernel T O n ↔ ∀ w : List I, w.length ≤ n → O (wordOp T w x) = 0 :=
  Iff.rfl

 theorem visibleKernel_zero : visibleKernel T O 0 = LinearMap.ker O := by
  ext x
  constructor
  · intro hx
    simpa using hx [] (by simp)
  · intro hx w hw
    have he : w = [] := List.length_eq_zero_iff.mp (Nat.eq_zero_of_le_zero hw)
    subst w
    simpa using hx

 theorem visibleKernel_antitone : Antitone (visibleKernel T O) := by
  intro m n h x hx w hw
  exact hx w (hw.trans h)

 theorem visibleKernel_succ_le (n : ℕ) :
    visibleKernel T O (n + 1) ≤ visibleKernel T O n :=
  visibleKernel_antitone T O (Nat.le_succ n)

 theorem invisible_le_visibleKernel (n : ℕ) :
    invisible T O ≤ visibleKernel T O n := by
  intro x hx w _
  exact hx w

 theorem visibleKernel_le_ker (n : ℕ) :
    visibleKernel T O n ≤ LinearMap.ker O := by
  rw [← visibleKernel_zero T O]
  exact visibleKernel_antitone T O (Nat.zero_le n)

 theorem mem_visibleKernel_succ_iff (n : ℕ) (x : X) :
    x ∈ visibleKernel T O (n + 1) ↔
      O x = 0 ∧ ∀ i : I, T i x ∈ visibleKernel T O n := by
  constructor
  · intro hx
    constructor
    · simpa using hx [] (by simp)
    · intro i w hw
      have h := hx (i :: w) (by simp only [List.length_cons]; omega)
      exact h
  · rintro ⟨hx, hnext⟩ w hw
    cases w with
    | nil => simpa using hx
    | cons i w =>
      exact hnext i w (by simp only [List.length_cons] at hw; omega)

/-- The recursion is a finite intersection when the operation alphabet is finite. -/
 theorem visibleKernel_succ (n : ℕ) :
    visibleKernel T O (n + 1) =
      LinearMap.ker O ⊓ ⨅ i : I, (visibleKernel T O n).comap (T i) := by
  ext x
  simp only [mem_visibleKernel_succ_iff, Submodule.mem_inf, LinearMap.mem_ker,
    Submodule.mem_iInf, Submodule.mem_comap]

/-- A single equality of successive subspaces certifies all-future sufficiency. -/
 theorem visibleKernel_eq_invisible_of_plateau (n : ℕ)
    (h : visibleKernel T O (n + 1) = visibleKernel T O n) :
    visibleKernel T O n = invisible T O := by
  apply le_antisymm
  · apply invariant_submodule_le_invisible T O _ (visibleKernel_le_ker T O n)
    intro i x hx
    have hs : x ∈ visibleKernel T O (n + 1) := by rw [h]; exact hx
    exact ((mem_visibleKernel_succ_iff T O n x).mp hs).2 i
  · exact invisible_le_visibleKernel T O n

 theorem visibleKernel_eq_invisible_of_eq_finrank (n : ℕ)
    [FiniteDimensional K (visibleKernel T O n)]
    (h : finrank K (visibleKernel T O (n + 1)) = finrank K (visibleKernel T O n)) :
    visibleKernel T O n = invisible T O := by
  exact visibleKernel_eq_invisible_of_plateau T O n
    (Submodule.eq_of_le_of_finrank_eq (visibleKernel_succ_le T O n) h)

 theorem visibleKernel_eq_invisible_of_le {m n : ℕ} (hmn : m ≤ n)
    (hm : visibleKernel T O m = invisible T O) :
    visibleKernel T O n = invisible T O := by
  apply le_antisymm
  · rw [← hm]
    exact visibleKernel_antitone T O hmn
  · exact invisible_le_visibleKernel T O n

variable [FiniteDimensional K X]

/-- Before reaching the exact invisible space, each new horizon lowers dimension. -/
 theorem visibleKernel_finrank_strict (n : ℕ)
    (h : visibleKernel T O (n + 1) ≠ invisible T O) :
    finrank K (visibleKernel T O (n + 1)) < finrank K (visibleKernel T O n) := by
  by_contra hn
  have he := Submodule.eq_of_le_of_finrank_le (visibleKernel_succ_le T O n)
    (Nat.le_of_not_gt hn)
  apply h
  rw [he]
  exact visibleKernel_eq_invisible_of_plateau T O n he

/-- The number of strict rounds is paid for by a loss of state dimension. -/
 theorem visibleKernel_finrank_budget (n : ℕ)
    (h : visibleKernel T O n ≠ invisible T O) :
    finrank K (visibleKernel T O n) + n ≤ finrank K (LinearMap.ker O) := by
  induction n with
  | zero => rw [visibleKernel_zero T O]; omega
  | succ n ih =>
    have hn : visibleKernel T O n ≠ invisible T O := by
      intro he
      exact h (visibleKernel_eq_invisible_of_le T O (Nat.le_succ n) he)
    have hb := ih hn
    have hs := visibleKernel_finrank_strict T O n h
    omega

/-- A priori termination bound: dim ker(O) rounds suffice. -/
 theorem visibleKernel_stabilizes :
    visibleKernel T O (finrank K (LinearMap.ker O)) = invisible T O := by
  by_contra h
  have hb := visibleKernel_finrank_budget T O (finrank K (LinearMap.ker O)) h
  have hz : finrank K (visibleKernel T O (finrank K (LinearMap.ker O))) = 0 := by omega
  have hbot := Submodule.finrank_eq_zero.mp hz
  apply h
  apply le_antisymm
  · rw [hbot]
    exact bot_le
  · exact invisible_le_visibleKernel T O _

 theorem visibleKernel_stabilizes_at_ambient_dimension :
    visibleKernel T O (finrank K X) = invisible T O := by
  exact visibleKernel_eq_invisible_of_le T O (LinearMap.ker O).finrank_le
    (visibleKernel_stabilizes T O)

 theorem invisible_iff_bounded_observations (x : X) :
    x ∈ invisible T O ↔
      ∀ w : List I, w.length ≤ finrank K (LinearMap.ker O) → O (wordOp T w x) = 0 := by
  rw [← visibleKernel_stabilizes T O]
  rfl

/-- Equality of a finite horizon of whole observations determines every future. -/
 theorem same_future_iff_bounded (x y : X) :
    (∀ w : List I, O (wordOp T w x) = O (wordOp T w y)) ↔
    (∀ w : List I, w.length ≤ finrank K (LinearMap.ker O) →
      O (wordOp T w x) = O (wordOp T w y)) := by
  have h := invisible_iff_bounded_observations T O (x - y)
  simpa only [mem_invisible_iff, map_sub, sub_eq_zero] using h

 theorem quotient_eq_iff_bounded (x y : X) :
    quotientMap T O x = quotientMap T O y ↔
    (∀ w : List I, w.length ≤ finrank K (LinearMap.ker O) →
      O (wordOp T w x) = O (wordOp T w y)) := by
  rw [quotient_eq_iff_same_future, same_future_iff_bounded]

/-- Inequivalent states have an explicitly bounded distinguishing word. -/
 theorem exists_bounded_distinguishing_word (x y : X)
    (h : quotientMap T O x ≠ quotientMap T O y) :
    ∃ w : List I, w.length ≤ finrank K (LinearMap.ker O) ∧
      O (wordOp T w x) ≠ O (wordOp T w y) := by
  classical
  by_contra hn
  push Not at hn
  exact h ((quotient_eq_iff_bounded T O x y).mpr hn)

end Komorebi.SufficientResolution.FiniteHorizon
