import Mathlib.RingTheory.Nilpotent.Exp

set_option autoImplicit false

/-!
# A finite logarithm for unipotent elements

The logarithm is evaluated as a finite rational polynomial in `u - 1`.
Its values away from unipotent elements are not assigned an interpretation.
-/

namespace PaperX.FiniteLogarithm

open Finset

variable {A : Type*} [Ring A] [Algebra ℚ A]

/-- The finite logarithm, with the zero coefficient at exponent zero included. -/
noncomputable def log (u : A) : A :=
  ∑ j ∈ range (nilpotencyClass (u - 1)),
    ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) • (u - 1) ^ j

/-- Any annihilating exponent gives the same finite logarithm. -/
theorem log_eq_sum {u : A} {d : ℕ} (hu : (u - 1) ^ d = 0) :
    log u = ∑ j ∈ range d, ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) • (u - 1) ^ j := by
  have h₁ : (∑ j ∈ range d, ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) • (u - 1) ^ j) =
      (∑ j ∈ range (nilpotencyClass (u - 1)),
        ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) • (u - 1) ^ j) +
      ∑ j ∈ Ico (nilpotencyClass (u - 1)) d,
        ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) • (u - 1) ^ j :=
    (sum_range_add_sum_Ico _ (csInf_le' hu)).symm
  have h₂ : (∑ j ∈ Ico (nilpotencyClass (u - 1)) d,
      ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) • (u - 1) ^ j) = 0 := by
    exact sum_eq_zero fun _ hj => by
      rw [pow_eq_zero_of_le (mem_Ico.1 hj).1 (pow_nilpotencyClass ⟨d, hu⟩), smul_zero]
  dsimp [log]
  rw [h₁, h₂, add_zero]

@[simp]
theorem log_one : log (1 : A) = 0 := by
  rw [log_eq_sum (d := 1) (by simp)]
  simp

/-- The finite logarithm of a unipotent element is nilpotent. -/
theorem isNilpotent_log {u : A} (hu : IsNilpotent (u - 1)) : IsNilpotent (log u) := by
  rw [log]
  apply Commute.isNilpotent_sum
  · intro j _
    by_cases hj : j = 0
    · simp [hj]
    · exact (IsNilpotent.pow_of_pos hu hj).smul _
  · intro i j _ _
    exact ((Commute.refl (u - 1)).pow_pow i j).smul_left _ |>.smul_right _

/-- Ring maps preserve the finite logarithm on unipotent elements. -/
theorem map_log {B : Type*} [Ring B] [Algebra ℚ B] {u : A}
    (hu : IsNilpotent (u - 1)) (f : A →+* B) : f (log u) = log (f u) := by
  obtain ⟨d, hd⟩ := hu
  have hd' : (f u - 1) ^ d = 0 := by
    simpa only [map_pow, map_sub, map_one, map_zero] using congrArg f hd
  simp [log_eq_sum hd, log_eq_sum hd', map_rat_smul]

end PaperX.FiniteLogarithm
