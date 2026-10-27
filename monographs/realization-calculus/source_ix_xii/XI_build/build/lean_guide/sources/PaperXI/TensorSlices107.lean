import Mathlib.LinearAlgebra.TensorProduct.Basis
import Mathlib.LinearAlgebra.Dual.Lemmas

/-! Slice an actual tensor operator and reconstruct it when all its first-factor
slices belong to one nonzero line. No invertibility of that line's generator,
and no finite-dimensionality of either carrier, is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TensorSlices107
open scoped TensorProduct
variable {k W U : Type*} [Field k] [AddCommGroup W] [Module k W]
  [AddCommGroup U] [Module k U]

def right (φ : Module.Dual k U) : W ⊗[k] U →ₗ[k] W :=
  (TensorProduct.rid k W).toLinearMap.comp (TensorProduct.map LinearMap.id φ)

def left (ℓ : Module.Dual k W) : W ⊗[k] U →ₗ[k] U :=
  (TensorProduct.lid k U).toLinearMap.comp (TensorProduct.map ℓ LinearMap.id)

@[simp] theorem right_tmul (φ : Module.Dual k U) (w : W) (u : U) :
    right φ (w ⊗ₜ[k] u) = φ u • w := by simp [right]

@[simp] theorem left_tmul (ℓ : Module.Dual k W) (w : W) (u : U) :
    left ℓ (w ⊗ₜ[k] u) = ℓ w • u := by simp [left]

theorem right_ext {s t : W ⊗[k] U}
    (h : ∀ φ : Module.Dual k U, right φ s = right φ t) : s = t := by
  classical
  let b := Module.Free.chooseBasis k U
  apply (TensorProduct.equivFinsuppOfBasisRight b).injective
  ext i
  simpa only [TensorProduct.equivFinsuppOfBasisRight_apply,
    LinearMap.lTensor_def, right, LinearMap.comp_apply, LinearEquiv.coe_coe] using h (b.coord i)

theorem contractions_commute (ℓ : Module.Dual k W) (φ : Module.Dual k U)
    (t : W ⊗[k] U) : φ (left ℓ t) = ℓ (right φ t) := by
  induction t using TensorProduct.induction_on with
  | zero => simp
  | add x y hx hy => simp [hx, hy]
  | tmul w u => simp [mul_comm]

theorem right_map (φ : Module.Dual k U) (A : W →ₗ[k] W) (t : W ⊗[k] U) :
    right φ (TensorProduct.map A LinearMap.id t) = A (right φ t) := by
  induction t using TensorProduct.induction_on with
  | zero => simp
  | add x y hx hy => simp [hx, hy]
  | tmul w u => simp

def slice (T : W ⊗[k] U →ₗ[k] W ⊗[k] U) (u : U) (φ : Module.Dual k U) :
    W →ₗ[k] W :=
  (right φ).comp (T.comp ((TensorProduct.mk k W U).flip u))

@[simp] theorem slice_apply (T : W ⊗[k] U →ₗ[k] W ⊗[k] U)
    (u : U) (φ : Module.Dual k U) (w : W) :
    slice T u φ w = right φ (T (w ⊗ₜ[k] u)) := rfl

theorem exists_nonzero_slice (T : W ⊗[k] U →ₗ[k] W ⊗[k] U) (hT : T ≠ 0) :
    ∃ u φ, slice T u φ ≠ 0 := by
  classical
  by_contra h
  push Not at h
  apply hT
  ext w u
  apply right_ext
  intro φ
  have hs := LinearMap.congr_fun (h u φ) w
  simpa using hs

/-- A nonzero first-factor map need not be invertible: one separating functional
on one nonzero value suffices to recover the entire second-factor operator. -/
theorem factor_of_slice_line (T : W ⊗[k] U →ₗ[k] W ⊗[k] U)
    (S : W →ₗ[k] W) (hS : S ≠ 0)
    (hline : ∀ u φ, ∃ c : k, slice T u φ = c • S) :
    ∃ R : U →ₗ[k] U, T = TensorProduct.map S R := by
  classical
  obtain ⟨w₀, hw₀⟩ : ∃ w₀, S w₀ ≠ 0 := by
    by_contra h
    push Not at h
    exact hS (LinearMap.ext h)
  obtain ⟨ℓ, hℓ⟩ := Module.Projective.exists_dual_eq_one k hw₀
  let R := (left ℓ).comp (T.comp (TensorProduct.mk k W U w₀))
  refine ⟨R, ?_⟩
  ext w u
  apply right_ext
  intro φ
  obtain ⟨c, hc⟩ := hline u φ
  have hcw := LinearMap.congr_fun hc w
  have hc₀ := LinearMap.congr_fun hc w₀
  have hR : φ (R u) = c := by
    change φ (left ℓ (T (w₀ ⊗ₜ[k] u))) = c
    rw [contractions_commute]
    change ℓ (slice T u φ w₀) = c
    rw [hc]
    simp [hℓ]
  simpa [hR] using hcw

theorem tmul_left_injective (w : W) (hw : w ≠ 0) :
    Function.Injective (fun u : U => w ⊗ₜ[k] u) := by
  obtain ⟨ℓ, hℓ⟩ := Module.Projective.exists_dual_eq_one k hw
  intro u v h
  have he := congrArg (left ℓ) h
  simpa [hℓ] using he

theorem map_left_injective (S : W →ₗ[k] W) (hS : S ≠ 0) :
    Function.Injective (fun R : U →ₗ[k] U => TensorProduct.map S R) := by
  obtain ⟨w, hw⟩ : ∃ w, S w ≠ 0 := by
    by_contra h
    push Not at h
    exact hS (LinearMap.ext h)
  intro R R' h
  ext u
  apply tmul_left_injective (k := k) (S w) hw
  simpa using LinearMap.congr_fun h (w ⊗ₜ[k] u)

end PaperXI.TensorSlices107
