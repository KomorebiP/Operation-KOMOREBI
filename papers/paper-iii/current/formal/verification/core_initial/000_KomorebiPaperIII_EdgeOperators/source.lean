/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Data.Matrix.Basic

/-!
# Typed packet-supported edge operators

An edge `e : E` is oriented from `source e` to `target e`.  Its elementary
packet operator has its only potentially nonzero matrix coefficient in row
`target e`, column `source e`.  Consequently matrix multiplication follows
execution order from right to left: `edgeOp f * edgeOp e` means first traverse
`e`, then traverse `f`.
-/

set_option autoImplicit false

namespace Komorebi.PaperIII.EdgeOperators

open scoped BigOperators

universe u v w

/-- A finite directed multigraph; distinct edge values may have equal endpoints. -/
structure PacketGraph (V : Type u) (E : Type v) where
  source : E → V
  target : E → V

namespace PacketGraph

variable {V : Type u} {E : Type v} {R : Type w}

/-- The matrix unit supported from packet `source` to packet `target`. -/
def packetMatrix [Zero R] [DecidableEq V]
    (source target : V) (coefficient : R) : Matrix V V R :=
  fun row column ↦ if row = target ∧ column = source then coefficient else 0

@[simp] theorem packetMatrix_apply [Zero R] [DecidableEq V]
    (source target row column : V) (coefficient : R) :
    packetMatrix source target coefficient row column =
      if row = target ∧ column = source then coefficient else 0 :=
  rfl

/-- An edge coefficient system on a packet graph. -/
structure EdgeSystem (G : PacketGraph V E) (R : Type w) where
  coefficient : E → R

namespace EdgeSystem

variable (G : PacketGraph V E) (S : EdgeSystem G R)

/-- The elementary operator carried by one directed edge. -/
def edgeOp [Zero R] [DecidableEq V] (e : E) : Matrix V V R :=
  packetMatrix (G.source e) (G.target e) (S.coefficient e)

@[simp] theorem edgeOp_apply [Zero R] [DecidableEq V]
    (e : E) (row column : V) :
    edgeOp G S e row column =
      if row = G.target e ∧ column = G.source e then S.coefficient e else 0 :=
  rfl

/-- Edge operators are supported only on their declared target-source block. -/
theorem edgeOp_eq_zero_off_support [Zero R] [DecidableEq V]
    (e : E) (row column : V)
    (h : ¬ (row = G.target e ∧ column = G.source e)) :
    edgeOp G S e row column = 0 := by
  simp [edgeOp, packetMatrix, h]

/--
Noncomposable edge products vanish.  In `edgeOp f * edgeOp e`, `e` acts first;
the product is zero when the target of `e` is not the source of `f`.
-/
theorem edgeOp_mul_edgeOp_eq_zero
    [Fintype V] [DecidableEq V] [Semiring R]
    (e f : E) (h : G.target e ≠ G.source f) :
    edgeOp G S f * edgeOp G S e = 0 := by
  ext row column
  rw [Matrix.mul_apply]
  apply Finset.sum_eq_zero
  intro middle _
  by_cases htarget : middle = G.target e
  · subst middle
    simp [edgeOp, packetMatrix, h]
  · simp [edgeOp, packetMatrix, htarget]

/--
A composable two-edge word collapses to the endpoint block, with coefficients
multiplied in operator order.
-/
theorem edgeOp_mul_edgeOp_of_composable
    [Fintype V] [DecidableEq V] [Semiring R]
    (e f : E) (h : G.target e = G.source f) :
    edgeOp G S f * edgeOp G S e =
      packetMatrix (G.source e) (G.target f)
        (S.coefficient f * S.coefficient e) := by
  ext row column
  by_cases hrow : row = G.target f
  · by_cases hcolumn : column = G.source e
    · simp [edgeOp, packetMatrix, Matrix.mul_apply, h, hrow, hcolumn]
    · simp [edgeOp, packetMatrix, Matrix.mul_apply, h, hcolumn]
  · simp [edgeOp, packetMatrix, Matrix.mul_apply, hrow]

/-- A list is composable in its written, left-to-right execution order. -/
def Composable (G : PacketGraph V E) : List E → Prop
  | [] => True
  | [_] => True
  | e :: f :: rest => G.target e = G.source f ∧ Composable G (f :: rest)

/-- Evaluate a word in execution order; the first listed edge acts first. -/
def wordOp [Fintype V] [DecidableEq V] [Semiring R]
    (G : PacketGraph V E) (S : EdgeSystem G R) : List E → Matrix V V R
  | [] => 1
  | e :: rest => wordOp G S rest * edgeOp G S e

@[simp] theorem wordOp_nil [Fintype V] [DecidableEq V] [Semiring R] :
    wordOp G S [] = 1 :=
  rfl

@[simp] theorem wordOp_singleton [Fintype V] [DecidableEq V] [Semiring R]
    (e : E) : wordOp G S [e] = edgeOp G S e := by
  simp [wordOp]

/-- Concatenating execution words reverses at the level of operator products. -/
theorem wordOp_append [Fintype V] [DecidableEq V] [Semiring R]
    (first second : List E) :
    wordOp G S (first ++ second) = wordOp G S second * wordOp G S first := by
  induction first with
  | nil => simp
  | cons e rest ih =>
      simp [wordOp, ih, Matrix.mul_assoc]

/-- Prefixing a noncomposable edge pair makes the entire word operator zero. -/
theorem wordOp_eq_zero_of_first_break
    [Fintype V] [DecidableEq V] [Semiring R]
    (e f : E) (rest : List E) (h : G.target e ≠ G.source f) :
    wordOp G S (e :: f :: rest) = 0 := by
  change (wordOp G S rest * edgeOp G S f) * edgeOp G S e = 0
  rw [Matrix.mul_assoc, edgeOp_mul_edgeOp_eq_zero G S e f h]
  simp

/-- Every noncomposable edge word evaluates to the zero packet operator. -/
theorem wordOp_eq_zero_of_not_composable
    [Fintype V] [DecidableEq V] [Semiring R]
    (word : List E) (h : ¬ Composable G word) :
    wordOp G S word = 0 := by
  induction word with
  | nil => simp [Composable] at h
  | cons e rest ih =>
      cases rest with
      | nil => simp [Composable] at h
      | cons f tail =>
          simp only [Composable, not_and_or] at h
          rcases h with hbreak | htail
          · exact wordOp_eq_zero_of_first_break G S e f tail hbreak
          · change wordOp G S (f :: tail) * edgeOp G S e = 0
            rw [ih htail]
            simp

/-- The transfer operator is the finite sum of all elementary edge operators. -/
def transferOp [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (G : PacketGraph V E) (S : EdgeSystem G R) : Matrix V V R :=
  ∑ e : E, edgeOp G S e

/--
Recursive finite expansion of length-`n` edge words.  Each successor step
chooses the next (left-multiplying) edge after the already executed word.
-/
def wordExpansion [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (G : PacketGraph V E) (S : EdgeSystem G R) :
    ℕ → Matrix V V R
  | 0 => 1
  | n + 1 => transferOp G S * wordExpansion G S n

/-- Evaluate a finite edge tuple as its left-to-right execution word. -/
def tupleWordOp [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) (word : Fin n → E) : Matrix V V R :=
  wordOp G S (List.ofFn word)

/-- An actual finite sum over every edge word of length `n`. -/
def explicitWordExpansion [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) : Matrix V V R :=
  ∑ word : Fin n → E, tupleWordOp G S n word

/--
The finite word sum with every non-walk term removed.  `Composable` is exactly
the adjacent endpoint condition, so these are the typed graph walks.
-/
noncomputable def walkExpansion
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (G : PacketGraph V E) (S : EdgeSystem G R) (n : ℕ) : Matrix V V R := by
  classical
  exact ∑ word : Fin n → E,
    if Composable G (List.ofFn word) then tupleWordOp G S n word else 0

/-- Appending one final edge left-multiplies the operator of the prefix. -/
theorem tupleWordOp_snoc
    [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) (final : E) (prior : Fin n → E) :
    tupleWordOp G S (n + 1) (Fin.snoc prior final) =
      edgeOp G S final * tupleWordOp G S n prior := by
  unfold tupleWordOp
  rw [List.ofFn_succ']
  simp only [Fin.snoc_castSucc, Fin.snoc_last]
  rw [List.concat_eq_append, wordOp_append]
  simp

/-- The explicit tuple sum grows by appending one final edge. -/
theorem explicitWordExpansion_succ
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) :
    explicitWordExpansion G S (n + 1) =
      transferOp G S * explicitWordExpansion G S n := by
  unfold explicitWordExpansion
  rw [← (Fin.snocEquiv (fun _ : Fin (n + 1) ↦ E)).sum_comp]
  rw [Fintype.sum_prod_type]
  change (∑ final : E, ∑ prior : Fin n → E,
    tupleWordOp G S (n + 1) (Fin.snoc prior final)) = _
  simp only [tupleWordOp_snoc]
  unfold transferOp
  rw [Finset.sum_mul]
  simp_rw [Finset.mul_sum]

/-- The recursive word expansion is exactly the explicit finite tuple sum. -/
theorem wordExpansion_eq_explicitWordExpansion
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) :
    wordExpansion G S n = explicitWordExpansion G S n := by
  induction n with
  | zero =>
      simp [wordExpansion, explicitWordExpansion, tupleWordOp]
  | succ n ih =>
      rw [wordExpansion, ih, explicitWordExpansion_succ G S n]

/-- Removing noncomposable words does not change the finite operator sum. -/
theorem explicitWordExpansion_eq_walkExpansion
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) :
    explicitWordExpansion G S n = walkExpansion G S n := by
  classical
  unfold explicitWordExpansion walkExpansion
  apply Finset.sum_congr rfl
  intro word _
  by_cases hwalk : Composable G (List.ofFn word)
  · simp [hwalk]
  · have hzero : tupleWordOp G S n word = 0 :=
      wordOp_eq_zero_of_not_composable G S (List.ofFn word) hwalk
    simp [hwalk, hzero]

/-- Every finite transfer power equals the recursively enumerated word expansion. -/
theorem transferOp_pow_eq_wordExpansion
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) :
    transferOp G S ^ n = wordExpansion G S n := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [pow_succ', ih]
      rfl

/-- Finite walk expansion: a transfer power is the sum of all length-`n` words. -/
theorem transferOp_pow_eq_explicitWordExpansion
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) :
    transferOp G S ^ n = explicitWordExpansion G S n := by
  rw [transferOp_pow_eq_wordExpansion G S n,
    wordExpansion_eq_explicitWordExpansion G S n]

/--
Finite walk expansion: `T^n` is exactly the sum over composable typed edge
words of length `n`; every non-walk word has vanished by packet support.
-/
theorem transferOp_pow_eq_walkExpansion
    [Fintype E] [Fintype V] [DecidableEq V] [Semiring R]
    (n : ℕ) :
    transferOp G S ^ n = walkExpansion G S n := by
  rw [transferOp_pow_eq_explicitWordExpansion G S n,
    explicitWordExpansion_eq_walkExpansion G S n]

end EdgeSystem
end PacketGraph
end Komorebi.PaperIII.EdgeOperators
