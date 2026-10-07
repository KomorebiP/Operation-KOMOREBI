/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib

/-!
# Komorebi verification smoke theorems

These declarations verify that Lean, Lake, and Mathlib can elaborate and check
small proofs in the project environment.
-/

namespace KomorebiVerification

/--
A small end-to-end check that the project can elaborate a theorem over the
reals and invoke a Mathlib normalization tactic.
-/
theorem binomialSquare (x y : ℝ) :
    (x + y) ^ 2 = x ^ 2 + 2 * x * y + y ^ 2 := by
  ring

/-- A second check exercising finite sums and arithmetic normalization. -/
theorem sumFirstOddNumbers (n : ℕ) :
    ∑ k ∈ Finset.range n, (2 * k + 1) = n ^ 2 := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Finset.sum_range_succ, ih]
      ring

end KomorebiVerification
