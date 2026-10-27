module

public import Triangular
public import Mathlib.NumberTheory.Padics.RingHoms

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.UnitTriangular

/-- Forward substitution in a ring, with actual unit diagonal inverses. -/
def solve {R : Type*} [CommRing R] (T : ℕ → ℕ → R) (b : ℕ → R)
    (d : ℕ → Rˣ) (n : ℕ) : R :=
  ↑(d n)⁻¹ * (b n - ∑ k : Fin n, T n k * solve T b d k)
termination_by n

theorem solve_step {R : Type*} [CommRing R] (T : ℕ → ℕ → R) (b : ℕ → R)
    (d : ℕ → Rˣ) (n : ℕ) :
    solve T b d n = ↑(d n)⁻¹ * (b n - ∑ k : Fin n, T n k * solve T b d k) := by
  rw [solve]

theorem solve_row {R : Type*} [CommRing R] (T : ℕ → ℕ → R) (b : ℕ → R)
    (d : ℕ → Rˣ) (hd : ∀ n, (d n : R) = T n n) (n : ℕ) :
    (∑ k : Fin n, T n k * solve T b d k) + T n n * solve T b d n = b n := by
  rw [solve_step T b d n, ← hd n, ← mul_assoc]
  simp only [Units.mul_inv, one_mul]
  ring

theorem solve_unique {R : Type*} [CommRing R] (T : ℕ → ℕ → R) (b a : ℕ → R)
    (d : ℕ → Rˣ) (hd : ∀ n, (d n : R) = T n n)
    (ha : ∀ n, (∑ k : Fin n, T n k * a k) + T n n * a n = b n) :
    a = solve T b d := by
  funext n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    have hs : (∑ k : Fin n, T n k * a k) = ∑ k : Fin n, T n k * solve T b d k := by
      apply Finset.sum_congr rfl
      intro k _
      rw [ih k k.isLt]
    have hr := ha n
    rw [hs] at hr
    have he := solve_row T b d hd n
    have hh := add_left_cancel (hr.trans he.symm)
    rw [← hd n] at hh
    exact (Units.mul_right_inj (d n)).mp hh

/-- The original field-based solver commutes with a genuine field homomorphism. -/
theorem field_solve_map {F G : Type*} [Field F] [Field G]
    (f : F →+* G) (T : ℕ → ℕ → F) (b : ℕ → F) (n : ℕ) :
    f (Triangular.solve T b n) =
      Triangular.solve (fun i j => f (T i j)) (fun i => f (b i)) n := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    rw [Triangular.solve_step, Triangular.solve_step]
    simp only [map_div₀, map_sub, map_sum, map_mul]
    congr 2
    apply Finset.sum_congr rfl
    intro k _
    rw [ih k k.isLt]

/-- A ring solution with unit pivots maps to the ordinary field solution. -/
theorem solve_map_to_field {R F : Type*} [CommRing R] [Field F]
    (f : R →+* F) (T : ℕ → ℕ → R) (b : ℕ → R)
    (d : ℕ → Rˣ) (hd : ∀ n, (d n : R) = T n n) :
    (fun n => f (solve T b d n)) =
      Triangular.solve (fun i j => f (T i j)) (fun i => f (b i)) := by
  apply Triangular.solve_unique
  · intro n
    rw [← hd n]
    exact ((d n).isUnit.map f).ne_zero
  · intro n
    have h := congrArg f (solve_row T b d hd n)
    simpa only [map_add, map_sum, map_mul] using h

end KomorebiPaperIX.UnitTriangular
