import Mathlib.RingTheory.Nilpotent.Exp
import Mathlib.Algebra.Algebra.Rat

/-! Finite nilpotent exponential algebra in characteristic zero. The rational
scalar action is derived from the original coefficient field, with no additional
scalar-compatibility hypothesis. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NilpotentExponential
variable {K V W : Type*} [Field K] [CharZero K]
  [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

local instance : Module ℚ (Module.End K V) :=
  Module.compHom (Module.End K V) (algebraMap ℚ K)

def expN (N : Module.End K V) (t : K) : Module.End K V :=
  IsNilpotent.exp (t • N)

@[simp] theorem expN_zero (N : Module.End K V) : expN N 0 = 1 := by
  simp [expN]

theorem expN_add {N : Module.End K V} (hN : IsNilpotent N) (s t : K) :
    expN N (s + t) = expN N s * expN N t := by
  unfold expN
  rw [add_smul]
  apply IsNilpotent.exp_add_of_commute
  · exact (Commute.refl N).smul_left s |>.smul_right t
  · exact hN.smul s
  · exact hN.smul t

theorem expN_sum {N : Module.End K V} {d : ℕ} (hN : N ^ d = 0) (t : K) :
    expN N t = ∑ j ∈ Finset.range d, (j.factorial : ℚ)⁻¹ • (t • N) ^ j := by
  apply IsNilpotent.exp_eq_sum
  simp [smul_pow, hN]

theorem expN_intertwines {N : Module.End K V} {M : Module.End K W}
    (hN : IsNilpotent N) (hM : IsNilpotent M)
    (f : V →ₗ[K] W) (h : M ∘ₗ f = f ∘ₗ N) (t : K) :
    expN M t ∘ₗ f = f ∘ₗ expN N t := by
  let : Module ℚ V := Module.compHom V (algebraMap ℚ K)
  let : Module ℚ W := Module.compHom W (algebraMap ℚ K)
  apply Module.End.commute_exp_left_of_commute (hN.smul t) (hM.smul t)
  ext x
  simpa using congrArg (fun z => t • z) (LinearMap.congr_fun h x)

@[simp] theorem expN_smul (N : Module.End K V) (a t : K) :
    expN (a • N) t = expN N (t * a) := by
  simp [expN, smul_smul]

theorem expN_mul_neg {N : Module.End K V} (hN : IsNilpotent N) (t : K) :
    expN N t * expN N (-t) = 1 := by
  rw [← expN_add hN, add_neg_cancel, expN_zero]

theorem expN_neg_mul {N : Module.End K V} (hN : IsNilpotent N) (t : K) :
    expN N (-t) * expN N t = 1 := by
  rw [← expN_add hN, neg_add_cancel, expN_zero]

def expEquiv {N : Module.End K V} (hN : IsNilpotent N) (t : K) : V ≃ₗ[K] V where
  toFun := expN N t
  invFun := expN N (-t)
  left_inv x := LinearMap.congr_fun (expN_neg_mul hN t) x
  right_inv x := LinearMap.congr_fun (expN_mul_neg hN t) x
  map_add' := (expN N t).map_add
  map_smul' := (expN N t).map_smul

theorem expN_identity_on_kernel {N : Module.End K V} (hN : IsNilpotent N)
    (t : K) {x : V} (hx : N x = 0) : expN N t x = x := by
  let : Module ℚ V := Module.compHom V (algebraMap ℚ K)
  have hx' : ((t • N) ^ 1) • x = 0 := by simp [Module.End.smul_def, hx]
  have h := IsNilpotent.exp_smul_eq_sum hx' (hN.smul t)
  simpa [expN, Module.End.smul_def] using h

/-- The construction is a finite polynomial over the original coefficient field. -/
theorem expN_polynomial {N : Module.End K V} {d : ℕ} (hN : N ^ d = 0) (t : K) :
    expN N t = ∑ j ∈ Finset.range d, (t ^ j / (j.factorial : K)) • N ^ j := by
  rw [expN_sum hN]
  apply Finset.sum_congr rfl
  intro j hj
  change ((algebraMap ℚ K) ((j.factorial : ℚ)⁻¹)) • (t • N) ^ j = _
  simp [smul_pow, smul_smul, div_eq_mul_inv, mul_comm]

/-- Covariance with a scalar twist, in the order needed for reconstructing group actions. -/
theorem expN_covariance {N : Module.End K V} {M : Module.End K W}
    (hN : IsNilpotent N) (hM : IsNilpotent M) (f : V →ₗ[K] W) (c : K)
    (h : f ∘ₗ N = (c • M) ∘ₗ f) (t : K) :
    f ∘ₗ expN N t = expN M (c * t) ∘ₗ f := by
  have he := expN_intertwines hN (hM.smul c) f h.symm t
  simpa [expN_smul, mul_comm] using he.symm

end PaperX.NilpotentExponential
