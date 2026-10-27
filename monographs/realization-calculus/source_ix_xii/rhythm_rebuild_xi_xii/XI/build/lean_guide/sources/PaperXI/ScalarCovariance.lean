import PaperXI.MonodromyChain

/-! Paper XI, Proposition 2.4. F = diag(1,q,...,q^(m-1)) as an actual
linear automorphism. q is a unit. The covariance factor is q⁻¹. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ScalarCovariance
open PaperXI.MonodromyChain

variable {K W : Type*} [Field K] [AddCommGroup W] [Module K W]
variable {m : ℕ}

def frobenius (q : Kˣ) : (Fin m → W) ≃ₗ[K] (Fin m → W) where
  toFun x i := (q : K) ^ i.val • x i
  invFun x i := ((q⁻¹ : Kˣ) : K) ^ i.val • x i
  left_inv x := by
    funext i
    simp [smul_smul]
  right_inv x := by
    funext i
    simp [smul_smul]
  map_add' x y := by funext i; exact smul_add _ _ _
  map_smul' c x := by funext i; simp [smul_smul, mul_comm]

@[simp] theorem frobenius_apply (q : Kˣ) (x : Fin m → W) (i : Fin m) :
    frobenius q x i = (q : K) ^ i.val • x i := rfl

/-- The pointwise covariance holds even for arbitrary linear transfers. -/
theorem covariance (q : Kˣ) (A : ℕ → Module.End K W) (x : Fin m → W) :
    frobenius q (shift A x) = ((q⁻¹ : Kˣ) : K) • shift A (frobenius q x) := by
  funext i
  simp only [frobenius_apply, shift_apply, Pi.smul_apply]
  split
  · rename_i h
    simp only [map_smul, smul_smul]
    congr 1
    simp [pow_succ, mul_comm]
  · simp

/-- Proposition 2.4, with F⁻¹ implemented by the inverse linear equivalence. -/
theorem conjugation (q : Kˣ) (A : ℕ → Module.End K W) :
    (frobenius (m := m) q).conj (shift A) = ((q⁻¹ : Kˣ) : K) • shift A := by
  apply LinearMap.ext
  intro x
  simpa using covariance q A ((frobenius q).symm x)

/-- The printed scalar model is the case in which every transfer is the identity. -/
theorem scalar_model (q : Kˣ) :
    (frobenius (W := K) (m := m) q).conj (shift fun _ => 1) =
      ((q⁻¹ : Kˣ) : K) • (shift fun _ => 1) := conjugation q _

end PaperXI.ScalarCovariance
