import ProofPath.Protected
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.ToLin

namespace ProofPath
open Matrix

variable {K : Type*} [Field K] {m n : ℕ}

def dualRow (l : (Fin m → K) →ₗ[K] K) (i : Fin m) : K :=
  l (Pi.single i 1)

theorem dual_row_eval (l : (Fin m → K) →ₗ[K] K) (y : Fin m → K) :
    dotProduct (dualRow l) y = l y := by
  have h : (∑ i : Fin m, y i • Pi.single i (1 : K)) = y := by
    ext j
    simp [Finset.sum_apply, Pi.single_apply, Pi.smul_apply]
  calc
    dotProduct (dualRow l) y = l (∑ i : Fin m, y i • Pi.single i (1 : K)) := by
      simp [dotProduct, dualRow, map_sum, map_smul, smul_eq_mul, mul_comm]
    _ = l y := congrArg l h

theorem row_witness_sound (M : Matrix (Fin m) (Fin n) K)
    (b l : Fin m → K) (hz : vecMul l M = 0) (h1 : dotProduct l b = 1) :
    ¬ ∃ y, M.mulVec y = b := by
  rintro ⟨y, hy⟩
  have h := dotProduct_mulVec l M y
  rw [hy, hz, zero_dotProduct, h1] at h
  exact one_ne_zero h

theorem row_alternative (M : Matrix (Fin m) (Fin n) K) (b : Fin m → K) :
    (¬ ∃ y, M.mulVec y = b) ↔
      ∃ l, vecMul l M = 0 ∧ dotProduct l b = 1 := by
  constructor
  · intro hn
    have hb : b ∉ M.mulVecLin.range := by
      rintro ⟨y, hy⟩
      exact hn ⟨y, hy⟩
    obtain ⟨l, hl, hz⟩ := Submodule.exists_dual_map_eq_bot_of_notMem hb inferInstance
    let f := (l b)⁻¹ • l
    have hf : f b = 1 := by simp [f, hl]
    have hzero : ∀ y, f (M.mulVec y) = 0 := by
      intro y
      have hm : l (M.mulVec y) ∈ M.mulVecLin.range.map l :=
        ⟨M.mulVec y, ⟨y, rfl⟩, rfl⟩
      have h : l (M.mulVec y) = 0 := by simpa [hz] using hm
      simp [f, h]
    refine ⟨dualRow f, ?_, by rw [dual_row_eval]; exact hf⟩
    ext j
    have h := hzero (Pi.single j 1)
    rw [← dual_row_eval f, dotProduct_mulVec] at h
    simpa [dotProduct, Pi.single_apply, mul_ite] using h
  · rintro ⟨l, hz, h1⟩
    exact row_witness_sound M b l hz h1

theorem binary_fiber_card {R : Type*} [AddCommGroup R] [Module (ZMod 2) R]
    (T : (Fin n → ZMod 2) →ₗ[ZMod 2] R) (x₀ : Fin n → ZMod 2) :
    Nat.card {y // T y = T x₀} = 2 ^ Module.finrank (ZMod 2) T.ker := by
  simpa using fiber_card T x₀

end ProofPath
