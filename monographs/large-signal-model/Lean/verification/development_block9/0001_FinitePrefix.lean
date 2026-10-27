import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.Tactic

/-! P17: explicit rational finite-dimensional nilpotent systems for every horizon. -/
set_option autoImplicit false
namespace Komorebi.LSM.Delay

def shift (n : ℕ) : (Fin n → ℚ) →ₗ[ℚ] (Fin n → ℚ) where
  toFun x i := if h : i.val + 1 < n then x ⟨i.val + 1, h⟩ else 0
  map_add' x y := by ext i; simp only; split <;> rfl
  map_smul' a x := by ext i; simp only; split <;> simp

theorem shift_power (n k : ℕ) (x : Fin n → ℚ) (i : Fin n) :
    (shift n ^ k) x i = if h : i.val + k < n then x ⟨i.val + k, h⟩ else 0 := by
  induction k generalizing i with
  | zero => simp
  | succ k ih =>
    rw [pow_succ', Module.End.mul_apply]
    change (if h : i.val + 1 < n then (shift n ^ k) x ⟨i.val+1,h⟩ else 0) = _
    split_ifs with h h'
    · rw [ih]
      simp only
      split_ifs with h''
      · congr 1; apply Fin.ext; omega
      · omega
    · rw [ih]
      simp only
      split_ifs with h''
      · omega
      · rfl
    · omega
    · rfl

theorem shift_nilpotent (n : ℕ) : shift n ^ n = 0 := by
  ext x i
  rw [shift_power]
  simp only [LinearMap.zero_apply, Pi.zero_apply]
  split_ifs with h
  · omega
  · rfl

def delayedInitial (T : ℕ) : Fin (T+2) → ℚ :=
  fun i => if i.val = T+1 then 1 else 0

def output (T : ℕ) : (Fin (T+2) → ℚ) →ₗ[ℚ] ℚ := LinearMap.proj ⟨0,by omega⟩

theorem delayed_output (T t : ℕ) :
    output T ((shift (T+2) ^ t) (delayedInitial T)) = if t = T+1 then 1 else 0 := by
  change (shift (T+2) ^ t) (delayedInitial T) ⟨0,by omega⟩ = _
  rw [shift_power]
  simp only [Nat.zero_add]
  split_ifs with h h'
  · simp [delayedInitial, h']
  · simp [delayedInitial, h']
  · omega
  · rfl

theorem finite_prefix_indistinguishability (T : ℕ) :
    ∃ (L₀ L₁ : (Fin (T+2) → ℚ) →ₗ[ℚ] (Fin (T+2) → ℚ))
      (C : (Fin (T+2) → ℚ) →ₗ[ℚ] ℚ) (x₀ x₁ : Fin (T+2) → ℚ),
      L₀^(T+2) = 0 ∧ L₁^(T+2) = 0 ∧
      (∀ t ≤ T, C ((L₀^t) x₀) = C ((L₁^t) x₁)) ∧
      C ((L₀^(T+1)) x₀) ≠ C ((L₁^(T+1)) x₁) := by
  refine ⟨0, shift (T+2), output T, 0, delayedInitial T, ?_, shift_nilpotent _, ?_, ?_⟩
  · simp
  · intro t ht
    rw [map_zero, map_zero, delayed_output]
    simp [show t ≠ T+1 by omega]
  · rw [map_zero, map_zero, delayed_output]
    simp
end Komorebi.LSM.Delay
