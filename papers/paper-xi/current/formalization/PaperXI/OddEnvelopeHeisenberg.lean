import PaperXI.BilinearHeisenberg
import PaperXI.HeisenbergPrime

/-! Canonical odd-characteristic extension, constructed directly on the given
alternating space. No polarization, symplectic basis or pre-existing group is input. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OddEnvelopeHeisenberg
open BilinearHeisenberg
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- The half-form factor set is available without choosing coordinates. -/
def factor (b : LinearMap.BilinForm K V) : LinearMap.BilinForm K V := (2 : K)⁻¹ • b

@[simp] theorem factor_apply (b : LinearMap.BilinForm K V) (x y : V) :
    factor b x y = (2 : K)⁻¹ * b x y := rfl

/-- Alternation and invertibility of two give the required commutator exactly. -/
theorem factor_commutator (b : LinearMap.BilinForm K V)
    (ha : b.IsAlt) (h2 : (2 : K) ≠ 0) (x y : V) :
    factor b x y - factor b y x = b x y := by
  have hskew : b x y + b y x = 0 := by
    have h := ha (x + y)
    simpa only [map_add, LinearMap.add_apply, ha x, ha y, zero_add, add_zero, add_comm] using h
  simp only [factor_apply]
  have hi : (2 : K)⁻¹ * 2 = 1 := inv_mul_cancel₀ h2
  calc
    (2 : K)⁻¹ * b x y - (2 : K)⁻¹ * b y x =
        ((2 : K)⁻¹ * 2) * b x y := by linear_combination -(2 : K)⁻¹ * hskew
    _ = _ := by rw [hi, one_mul]

/-- Every isometry lifts by the literal formula (v,z) -> (e(v),z). -/
def isometryEquiv {V' : Type*} [AddCommGroup V'] [Module K V']
    (b : LinearMap.BilinForm K V) (b' : LinearMap.BilinForm K V')
    (e : V ≃ₗ[K] V') (he : ∀ x y, b' (e x) (e y) = b x y) :
    Element (factor b) ≃* Element (factor b') where
  toFun h := ⟨e h.vector, h.central⟩
  invFun h := ⟨e.symm h.vector, h.central⟩
  left_inv h := by ext <;> simp
  right_inv h := by ext <;> simp
  map_mul' h k := by
    ext
    · exact e.map_add _ _
    · simp only [mul_central, factor_apply, he]

@[simp] theorem isometryEquiv_center {V' : Type*} [AddCommGroup V'] [Module K V']
    (b : LinearMap.BilinForm K V) (b' : LinearMap.BilinForm K V')
    (e : V ≃ₗ[K] V') (he : ∀ x y, b' (e x) (e y) = b x y) (z : Multiplicative K) :
    isometryEquiv b b' e he (i (factor b) z) = i (factor b') z := by
  ext <;> simp [isometryEquiv]

end PaperXI.OddEnvelopeHeisenberg
