import PaperX.MonodromyData

set_option autoImplicit false
noncomputable section
namespace PaperX.MonodromyKernels
open scoped BigOperators
open PaperX.CarrierSummands PaperX.CarrierPolynomials PaperX.MonodromyData

variable {K : Type*} [Field K] {q : Kˣ}
variable {I : Type*} [Fintype I] {W : I → Type*}
variable [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]

/-- An independently defined kernel is exactly the product of constituent kernels. -/
def kernelCopiesEquiv (D : ∀ i, Datum q (W i)) (m : I → ℕ) :
    LinearMap.ker (copiesDatum D m).N ≃ₗ[K]
      Copies (fun i => LinearMap.ker (D i).N) m where
  toFun x i k := ⟨x.val i k, congrFun (congrFun x.property i) k⟩
  invFun x := ⟨fun i k => (x i k).val, by
    funext i k
    exact (x i k).property⟩
  left_inv x := by apply Subtype.ext; rfl
  right_inv x := rfl
  map_add' x y := rfl
  map_smul' a x := rfl

theorem kernel_equivariant (D : ∀ i, Datum q (W i)) (m : I → ℕ)
    (x : LinearMap.ker (copiesDatum D m).N) :
    kernelCopiesEquiv D m (kernelF (copiesDatum D m) x) =
      (LinearEquiv.piCongrRight (fun i => LinearEquiv.piCongrRight
        (fun _ : Fin (m i) => kernelF (D i)))) (kernelCopiesEquiv D m x) := rfl

theorem kernel_conjugate (D : ∀ i, Datum q (W i)) (m : I → ℕ) :
    (kernelCopiesEquiv D m).conj (kernelF (copiesDatum D m)).toLinearMap =
      piEnd (fun i => piEnd (fun _ : Fin (m i) => (kernelF (D i)).toLinearMap)) := by
  apply LinearMap.ext
  intro x
  rfl

variable [∀ i, FiniteDimensional K (W i)]

theorem kernel_charpoly_product (D : ∀ i, Datum q (W i)) (m : I → ℕ) :
    kernelCharpoly (copiesDatum D m) = ∏ i, kernelCharpoly (D i) ^ m i := by
  unfold kernelCharpoly
  rw [← LinearEquiv.charpoly_conj (kernelCopiesEquiv D m), kernel_conjugate,
    charpoly_piEnd]
  apply Finset.prod_congr rfl
  intro i _
  rw [charpoly_piEnd]
  simp

theorem kernel_dimension_sum (D : ∀ i, Datum q (W i)) (m : I → ℕ) :
    Module.finrank K (LinearMap.ker (copiesDatum D m).N) =
      ∑ i, m i * Module.finrank K (LinearMap.ker (D i).N) := by
  rw [(kernelCopiesEquiv D m).finrank_eq, copies_finrank]

theorem kernel_trace_sum (D : ∀ i, Datum q (W i)) (m : I → ℕ) :
    LinearMap.trace K _ (kernelF (copiesDatum D m)).toLinearMap =
      ∑ i, (m i : K) * LinearMap.trace K _ (kernelF (D i)).toLinearMap := by
  rw [← LinearMap.trace_conj' _ (kernelCopiesEquiv D m), kernel_conjugate,
    trace_piEnd]
  apply Finset.sum_congr rfl
  intro i _
  rw [trace_piEnd]
  simp

/-- Coefficient comparison concerns the actual kernel polynomial here. -/
theorem common_kernel_polynomial {E : Type*} [CommRing E] (σ : E →+* K)
    (D : ∀ i, Datum q (W i)) (m : I → ℕ) (P : I → Polynomial E)
    (hP : ∀ i, kernelCharpoly (D i) = (P i).map σ) :
    kernelCharpoly (copiesDatum D m) = (∏ i, P i ^ m i).map σ := by
  rw [kernel_charpoly_product]
  simp [hP, Polynomial.map_prod]

end PaperX.MonodromyKernels
