module
public import DworkAlgebra
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.CubicDworkAlgebra
open DworkAlgebra
variable {K A : Type*} [Field K] [CommRing A] [Algebra K A] [CharZero K]
/-- The larger defect uses the actual p^3 and p^2 derivatives. At p=2 these are 8 and 4. -/
def B (D : Derivation K A A) (p : ℕ) : A →ₗ[K] A :=
  (p:K)⁻¹ • (deriv D (p^3) - deriv D (p^2))
/-- Neither derivative power is treated as a derivation: all middle terms are retained. -/
theorem B_mul (D : Derivation K A A) (p : ℕ) (hp : p.Prime) (f g : A) :
    B D p (f*g) = B D p f*g + f*B D p g +
      middle D p (p^3) f g - middle D p (p^2) f g := by
  have h0 : (p:K) ≠ 0 := Nat.cast_ne_zero.mpr hp.ne_zero
  have h2 := prime_power_leibniz D p 2 hp f g
  have h3 := prime_power_leibniz D p 3 hp f g
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply]
  rw [h3,h2]
  have hc := congrArg (algebraMap K A) (inv_mul_cancel₀ h0)
  simp only [map_mul,map_natCast,map_one] at hc
  simp only [Algebra.smul_def]
  linear_combination (middle D p (p^3) f g - middle D p (p^2) f g)*hc
end KomorebiPaperIX.CubicDworkAlgebra
