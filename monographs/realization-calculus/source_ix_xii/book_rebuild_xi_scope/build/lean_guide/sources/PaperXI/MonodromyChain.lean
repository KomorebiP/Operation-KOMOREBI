import Mathlib.LinearAlgebra.Pi
import Mathlib.Algebra.Module.End
import Mathlib.Tactic

/-! Paper XI, Proposition 2.3. Actual operators on a finite chain of copies of W.
The transfers A i are arbitrary linear maps. Nilpotence is a conclusion.
`path` lists all composable transfers in their matrix multiplication order. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonodromyChain
open scoped BigOperators

variable {K W : Type*} [Field K] [AddCommGroup W] [Module K W]
variable {m : ℕ}

def shift (A : ℕ → Module.End K W) : Module.End K (Fin m → W) where
  toFun x i := if h : i.val + 1 < m then A i.val (x ⟨i.val + 1, h⟩) else 0
  map_add' x y := by funext i; by_cases h : i.val + 1 < m <;> simp [h]
  map_smul' c x := by funext i; by_cases h : i.val + 1 < m <;> simp [h]

@[simp] theorem shift_apply (A : ℕ → Module.End K W) (x : Fin m → W) (i : Fin m) :
    shift A x i = if h : i.val + 1 < m then A i.val (x ⟨i.val + 1, h⟩) else 0 := rfl

def path (A : ℕ → Module.End K W) (i : ℕ) : ℕ → Module.End K W
  | 0 => 1
  | r + 1 => path A i r * A (i + r)

@[simp] theorem path_zero (A : ℕ → Module.End K W) (i : ℕ) : path A i 0 = 1 := rfl
@[simp] theorem path_succ (A : ℕ → Module.End K W) (i r : ℕ) :
    path A i (r + 1) = path A i r * A (i + r) := rfl

/-- The complete path formula, including the zero case beyond the chain endpoint. -/
theorem pow_apply (A : ℕ → Module.End K W) (r : ℕ) (x : Fin m → W) (i : Fin m) :
    (shift A ^ r) x i =
      if h : i.val + r < m then path A i.val r (x ⟨i.val + r, h⟩) else 0 := by
  induction r generalizing x with
  | zero => simp [i.isLt]
  | succ r ih =>
      rw [pow_succ, Module.End.mul_apply, ih]
      by_cases hr : i.val + r < m
      · rw [dite_eq_left hr, shift_apply]
        by_cases hs : i.val + (r + 1) < m
        · simp only [Nat.add_assoc] at *
          rw [dite_eq_left hs, dite_eq_left hs, path_succ, Module.End.mul_apply]
        · simp only [Nat.add_assoc] at *
          rw [dite_eq_right hs, dite_eq_right hs, map_zero]
      · have hs : ¬ i.val + (r + 1) < m := by omega
        rw [dite_eq_right hr, dite_eq_right hs]

/-- Proposition 2.3: arbitrary nearest-neighbor transfers have nilpotence bound m. -/
theorem nilpotent_bound (A : ℕ → Module.End K W) :
    (shift A : Module.End K (Fin m → W)) ^ m = 0 := by
  apply LinearMap.ext
  intro x
  funext i
  rw [pow_apply, dite_eq_right (by omega)]
  rfl

def projector (j : Fin m) : Module.End K (Fin m → W) where
  toFun x i := if i = j then x i else 0
  map_add' x y := by funext i; split <;> simp_all
  map_smul' c x := by funext i; split <;> simp_all

@[simp] theorem projector_apply (j : Fin m) (x : Fin m → W) (i : Fin m) :
    projector (K := K) j x i = if i = j then x i else 0 := rfl

theorem projector_idempotent (j : Fin m) :
    (projector (K := K) (W := W) j) ^ 2 = projector j := by
  apply LinearMap.ext
  intro x
  funext i
  by_cases h : i = j <;> simp [pow_two, Module.End.mul_apply, h]

theorem projector_orthogonal {i j : Fin m} (h : i ≠ j) :
    (projector (K := K) (W := W) i) * projector j = 0 := by
  apply LinearMap.ext
  intro x
  funext k
  by_cases hk : k = i
  · subst k; simp [Module.End.mul_apply, h]
  · simp [Module.End.mul_apply, hk]

theorem projector_sum : (∑ j : Fin m, projector (K := K) (W := W) j) = 1 := by
  apply LinearMap.ext
  intro x
  funext i
  simp [LinearMap.sum_apply, Finset.sum_apply]

/-- All matrix blocks outside the nearest-neighbor diagonal vanish. -/
theorem block_vanishes (A : ℕ → Module.End K W) (i j : Fin m)
    (h : i.val + 1 ≠ j.val) :
    projector i * shift A * projector j = 0 := by
  apply LinearMap.ext
  intro x
  funext k
  by_cases hk : k = i
  · subst k
    simp only [Module.End.mul_apply, projector_apply, ite_true, shift_apply]
    split
    · rename_i hi
      have hij : (⟨i.val + 1, hi⟩ : Fin m) ≠ j := by
        intro he; exact h (congrArg Fin.val he)
      simp [hij]
    · rfl
  · simp [Module.End.mul_apply, hk]

/-- Proposition 2.3: the full operator equals the sum of its admissible blocks.
The double sum is the boundary-safe form of Σ_{j=1}^{m-1} P_{j-1} N P_j. -/
theorem block_reconstruction (A : ℕ → Module.End K W) :
    shift A = ∑ i : Fin m, ∑ j : Fin m,
      if i.val + 1 = j.val then projector i * shift A * projector j else 0 := by
  have h : ∀ i j : Fin m,
      (if i.val + 1 = j.val then projector i * shift A * projector j else 0) =
        projector i * shift A * projector j := by
    intro i j
    split
    · rfl
    · rename_i hij; exact (block_vanishes A i j hij).symm
  simp_rw [h]
  simp only [← Finset.mul_sum, projector_sum, mul_one, ← Finset.sum_mul, one_mul]

end PaperXI.MonodromyChain
