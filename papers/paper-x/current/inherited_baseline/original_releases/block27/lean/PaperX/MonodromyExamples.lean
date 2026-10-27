import PaperX.SpecialMonodromy

/-! Exact boundaries for algebraic monodromy pairs. No arithmetic realization is asserted. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.MonodromyExamples
open Polynomial
open PaperX.MonodromyData PaperX.SpecialMonodromy

variable {K : Type*} [Field K] {q : Kˣ}
variable {V : Type*} [AddCommGroup V] [Module K V]

/-- Keep the entire Frobenius automorphism, but set monodromy to zero. -/
def eraseN (D : Datum q V) : Datum q V where
  F := D.F
  N := 0
  nilpotent := ⟨1, by simp⟩
  relation x := by simp

def zeroKernelEquiv (D : Datum q V) : LinearMap.ker (eraseN D).N ≃ₗ[K] V where
  toFun x := x.val
  invFun x := ⟨x, rfl⟩
  left_inv _ :=  rfl
  right_inv _ :=  rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem zero_kernel_conjugate (D : Datum q V) :
    (zeroKernelEquiv D).conj (kernelF (eraseN D)).toLinearMap = D.F.toLinearMap := by
  apply LinearMap.ext
  intro x
  rfl

variable [FiniteDimensional K V]

theorem zero_kernel_charpoly (D : Datum q V) :
    kernelCharpoly (eraseN D) = D.F.toLinearMap.charpoly := by
  unfold kernelCharpoly
  rw [← LinearEquiv.charpoly_conj (zeroKernelEquiv D), zero_kernel_conjugate]

omit [FiniteDimensional K V] in
theorem zero_kernel_dimension (D : Datum q V) :
    Module.finrank K (LinearMap.ker (eraseN D).N) = Module.finrank K V :=
  (zeroKernelEquiv D).finrank_eq

/-- The same whole Frobenius polynomial does not determine the kernel polynomial. -/
theorem same_F_different_kernel (q a : Kˣ) (n : ℕ) (hn : 1 < n) :
    (eraseN (specialDatum q a n)).F = (specialDatum q a n).F ∧
    kernelCharpoly (eraseN (specialDatum q a n)) ≠
      kernelCharpoly (specialDatum q a n) := by
  refine ⟨rfl, ?_⟩
  intro h
  have hd := congrArg Polynomial.natDegree h
  rw [zero_kernel_charpoly, special_kernel_charpoly q a n (by omega),
    LinearMap.charpoly_natDegree, natDegree_X_sub_C] at hd
  simp only [Module.finrank_fin_fun] at hd
  omega

def scaleTwo : ℚˣ := Units.mk0 2 (by norm_num)

theorem length_three_kernel :
    kernelCharpoly (specialDatum scaleTwo 1 3) = X - 1 := by
  rw [special_kernel_charpoly scaleTwo 1 3 (by decide)]
  simp

theorem length_three_dimensions :
    Module.finrank ℚ (LinearMap.ker (specialDatum scaleTwo 1 3).N) = 1 ∧
    Module.finrank ℚ (LinearMap.ker (eraseN (specialDatum scaleTwo 1 3)).N) = 3 := by
  constructor
  · exact special_kernel_dimension scaleTwo 1 3 (by decide)
  · rw [zero_kernel_dimension]
    simp

theorem length_three_boundary :
    (eraseN (specialDatum scaleTwo 1 3)).F.toLinearMap.charpoly =
      (specialDatum scaleTwo 1 3).F.toLinearMap.charpoly ∧
    kernelCharpoly (eraseN (specialDatum scaleTwo 1 3)) ≠
      kernelCharpoly (specialDatum scaleTwo 1 3) :=
  ⟨rfl, (same_F_different_kernel scaleTwo 1 3 (by decide)).2⟩

end PaperX.MonodromyExamples
