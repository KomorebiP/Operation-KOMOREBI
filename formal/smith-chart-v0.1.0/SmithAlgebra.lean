import Mathlib.Data.Nat.ModEq
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.Ring

/-! Coefficient projectors, coprime factorization and nonlinear support. -/

open scoped BigOperators

namespace SmithAlgebra

def project (N j : ℕ) (a : ℕ → ℂ) (m : ℕ) : ℂ :=
  if m % N = j % N then a m else 0

theorem project_idempotent (N j : ℕ) (a : ℕ → ℂ) :
    project N j (project N j a) = project N j a := by
  funext m
  by_cases h : m % N = j % N <;> simp [project, h]

theorem project_orthogonal (N j k : ℕ) (a : ℕ → ℂ)
    (hjk : j % N ≠ k % N) : project N j (project N k a) = 0 := by
  funext m
  by_cases hj : m % N = j % N
  · simp [project, hj, hjk]
  · simp [project, hj]

theorem coprime_residue_iff (d o m j : ℕ) (h : d.Coprime o) :
    m % (d * o) = j % (d * o) ↔ m % d = j % d ∧ m % o = j % o := by
  simpa only [Nat.ModEq] using (Nat.modEq_and_modEq_iff_modEq_mul h).symm

/-- A coprime product projector is the intersection of the two residue lanes. -/
theorem crt_projector (d o j : ℕ) (h : d.Coprime o) (a : ℕ → ℂ) :
    project (d * o) j a = project d j (project o j a) := by
  funext m
  simp only [project, coprime_residue_iff d o m j h]
  by_cases hd : m % d = j % d <;> by_cases ho : m % o = j % o <;> simp [hd, ho]

def convolution (a b : ℕ → ℂ) (n : ℕ) : ℂ :=
  ∑ m ∈ Finset.range (n + 1), a m * b (n - m)

/-- Products of lanes r and s are supported only in lane r+s. -/
theorem convolution_off_target (N r s n : ℕ) (a b : ℕ → ℂ)
    (h : n % N ≠ (r + s) % N) :
    convolution (project N r a) (project N s b) n = 0 := by
  apply Finset.sum_eq_zero
  intro m hm
  by_cases ha : m % N = r % N
  · by_cases hb : (n - m) % N = s % N
    · have hmle : m ≤ n := Nat.le_of_lt_succ (Finset.mem_range.mp hm)
      have he : n % N = (r + s) % N := by
        calc
          n % N = (m + (n - m)) % N := by rw [Nat.add_sub_of_le hmle]
          _ = (m % N + (n - m) % N) % N := Nat.add_mod _ _ _
          _ = (r % N + s % N) % N := by rw [ha, hb]
          _ = (r + s) % N := (Nat.add_mod _ _ _).symm
      exact False.elim (h he)
    · simp [project, hb]
  · simp [project, ha]

end SmithAlgebra
