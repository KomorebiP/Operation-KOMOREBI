module

public import FibonacciPackets

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.RecurrenceExamples

open Matrix FibonacciPackets

/-- Lucas anchors follow from the independent recurrence. -/
theorem lucas_anchor_values : lucas 0 = 2 ∧ lucas 1 = 1 ∧ lucas 2 = 3 ∧
    lucas 3 = 4 ∧ lucas 4 = 7 ∧ lucas 5 = 11 := by norm_num [lucas]

/-- The exact sequence displayed in manuscript Example 9.3. -/
theorem manuscript_sequence :
    ([0,1,2,3,4,5].map (fun k => Nat.fib (3*k+2))) = [1,5,21,89,377,1597] := by
  norm_num

/-- The step-three recurrence is universal in the offset and packet index. -/
theorem manuscript_step_three (j k : ℕ) :
    (Nat.fib (3*(k+2)+j):ℤ) =
      4*(Nat.fib (3*(k+1)+j):ℤ) + (Nat.fib (3*k+j):ℤ) := by
  simpa only [lucas_anchor_values.2.2.2.1] using
    fibonacci_odd_step 3 j k (by decide)

/-- The contrasting even step has the subtractive sign. -/
theorem step_two (j k : ℕ) :
    (Nat.fib (2*(k+2)+j):ℤ) =
      3*(Nat.fib (2*(k+1)+j):ℤ) - (Nat.fib (2*k+j):ℤ) := by
  simpa only [lucas_anchor_values.2.2.1] using
    fibonacci_even_step 2 j k (by decide)

/-- The simplest attempted sign reversal gives a false equation. -/
theorem even_step_wrong_sign :
    (Nat.fib 5:ℤ) ≠ 3*(Nat.fib 3:ℤ) + (Nat.fib 1:ℤ) := by norm_num

/-- The ordinary N=1 recurrence is recovered with no sign ambiguity. -/
theorem step_one (j k : ℕ) :
    (Nat.fib (k+2+j):ℤ) = (Nat.fib (k+1+j):ℤ) + (Nat.fib (k+j):ℤ) := by
  simpa [lucas] using fibonacci_odd_step 1 j k (by decide)

/-- Zero step is allowed algebraically, but is not a positive-modulus residue split. -/
theorem zero_step (j k : ℕ) :
    (Nat.fib (0*(k+2)+j):ℤ) =
      lucas 0 * (Nat.fib (0*(k+1)+j):ℤ) - (-1:ℤ)^0 * (Nat.fib (0*k+j):ℤ) := by
  exact fibonacci_packet_recurrence 0 j k

/-- A singular nilpotent system is a legitimate input to the general theorem. -/
def nilpotent : Matrix (Fin 2) (Fin 2) ℤ := !![0,1;0,0]

theorem nilpotent_square : nilpotent^2 = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [nilpotent, pow_two, Matrix.mul_apply, Fin.sum_univ_two]

theorem nilpotent_charpoly : nilpotent.charpoly = (Polynomial.X:Polynomial ℤ)^2 := by
  rw [Matrix.charpoly_fin_two]
  norm_num [nilpotent, Matrix.trace, Fin.sum_univ_two, Matrix.det_fin_two]

theorem nilpotent_packet_zero (v : Fin 2 → ℤ) (j k : ℕ) :
    Companion.packet nilpotent v 2 j (k+1) = 0 := by
  rw [Companion.packet_step, nilpotent_square, Matrix.zero_mulVec]

/-- Dimension two does not force minimal recurrence order two. -/
theorem identity_packet_constant (v : Fin 2 → ℤ) (N j k : ℕ) :
    Companion.packet (1:Matrix (Fin 2) (Fin 2) ℤ) v N j k = v := by
  simp [Companion.packet, Companion.orbit]

theorem identity_packet_first_order (v : Fin 2 → ℤ) (N j k : ℕ) :
    Companion.packet (1:Matrix (Fin 2) (Fin 2) ℤ) v N j (k+1) =
      Companion.packet (1:Matrix (Fin 2) (Fin 2) ℤ) v N j k := by
  rw [identity_packet_constant, identity_packet_constant]

/-- The time step N belongs in C^N; using C again changes the sampled state. -/
theorem wrong_jump_matrix :
    Companion.packet companion initial 2 0 1 ≠ companion *ᵥ initial := by
  intro h
  have h1 := congrFun h 0
  norm_num [Companion.packet, Companion.orbit, companion, initial, pow_two,
    Matrix.mul_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two] at h1

/-- The zero-dimensional theorem remains meaningful on its unique empty state. -/
theorem empty_state_recurrence (C : Matrix (Fin 0) (Fin 0) ℤ) (v : Fin 0 → ℤ) (N j k : ℕ) :
    Companion.packet C v N j k = 0 := by
  ext i
  exact Fin.elim0 i

end KomorebiPaperIX.RecurrenceExamples
