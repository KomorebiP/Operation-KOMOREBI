import PaperXI.ProjectorTransport
import Mathlib.Data.ZMod.Basic

/-! The corrected covariance half of Proposition 3.1 under its printed
relation F T(a) F⁻¹ = T(q*a). Idempotence and completeness are not asserted here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FourierCovariance
open scoped BigOperators
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {M : ℕ} [NeZero M]

def mulPermutation (q : (ZMod M)ˣ) : ZMod M ≃ ZMod M where
  toFun a := (q : ZMod M) * a
  invFun a := ((q⁻¹ : (ZMod M)ˣ) : ZMod M) * a
  left_inv a := by simp [← mul_assoc]
  right_inv a := by simp [← mul_assoc]

def fourierOperator (T : ZMod M → Module.End K V) (χ : ZMod M → K)
    (j : ZMod M) : Module.End K V :=
  (M : K)⁻¹ • ∑ a : ZMod M, χ (-j * a) • T a

/-- The inverse exponent is forced by reindexing; no primitive-root assumption
is needed for this transport identity itself. -/
theorem inverse_exponent_covariance (q : (ZMod M)ˣ) (F : V ≃ₗ[K] V)
    (T : ZMod M → Module.End K V) (χ : ZMod M → K) (j : ZMod M)
    (h : ∀ a, F.conj (T a) = T ((q : ZMod M) * a)) :
    F.conj (fourierOperator T χ j) =
      fourierOperator T χ (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j) := by
  unfold fourierOperator
  rw [PaperXI.ProjectorTransport.normalized_sum_conjugation (mulPermutation q) F T _ _ h]
  congr 1
  apply Finset.sum_congr rfl
  intro a _
  congr 2
  change -j * (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * a) =
    -(((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j) * a
  ring

end PaperXI.FourierCovariance
