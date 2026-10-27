/- Algebraic consequences of explicitly supplied finite theta norm identities.
No elliptic, gamma, algebraicity, or special-value assertion is postulated. -/
module
public import Mathlib.Tactic.Ring.Basic
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public section
namespace H12.NormAlgebra
variable {K : Type*} [Field K]

theorem four_sheet_kernel_norm
    (a b c d u v : K) (hu : u ≠ 0) (hv : v ≠ 0) (h : a*b*c*d=u) :
    (a^2/(u*v))*(b^2/(u*v))*(c^2/(u*v))*(d^2/(u*v))=1/(u^2*v^4) := by
  calc
    _ = (a*b*c*d)^2/(u*v)^4 := by field_simp
    _ = u^2/(u*v)^4 := by rw [h]
    _ = _ := by field_simp

theorem even_norm_boundary (u v : K) (hu : u ≠ 0) (hv : v ≠ 0) :
    1/(u^2*v^4)=(1/u^6)*(u/v)^4 := by
  field_simp

theorem norm_one_doubling_factor
    (a b c d u : K) (hu : u ≠ 0) (h : a*b*c*d=u) :
    (a^4/u)*(b^4/u)*(c^4/u)*(d^4/u)=1 := by
  calc
    _ = (a*b*c*d)^4/u^4 := by field_simp
    _ = u^4/u^4 := by rw [h]
    _ = 1 := div_self (pow_ne_zero _ hu)

theorem kernel_factorization (u v w : K)
    (hu : u ≠ 0) (hv : v ≠ 0) (hw : w ≠ 0) :
    u^2/(v*w)=((u^4/v)^2/u^6)*(v/w) := by
  field_simp

theorem odd_norm_boundary (a b c d : K) (hc : c ≠ 0) :
    a^2/(b*d)=(a^2/(b*c))*(c/d) := by
  simp only [div_eq_mul_inv, mul_inv_rev]
  calc
    a^2*(d⁻¹*b⁻¹) = (a^2*b⁻¹*d⁻¹)*(c⁻¹*c) := by rw [inv_mul_cancel₀ hc]; ring1
    _ = a^2*(c⁻¹*b⁻¹)*(c*d⁻¹) := by ring1

theorem finite_boundary_product (q : ℕ → K) (hq : ∀ i, q i ≠ 0) (m : ℕ) :
    (∏ j ∈ Finset.range m, q j / q (j+1))=q 0/q m := by
  induction m with
  | zero => simp [hq]
  | succ m ih =>
    rw [Finset.prod_range_succ, ih]
    field_simp [hq m, hq (m+1)]

theorem pointwise_phase_comparison
    (u v epsilon limitValue : K) (hu : u ≠ 0) (hv : v ≠ 0)
    (he : epsilon ≠ 0)
    (han : limitValue=epsilon^6/u^3)
    (har : limitValue=epsilon^6/v^3) : u^3=v^3 := by
  have h : epsilon^6/u^3=epsilon^6/v^3 := han.symm.trans har
  have hcross := (div_eq_div_iff (pow_ne_zero _ hu) (pow_ne_zero _ hv)).mp h
  exact (mul_left_cancel₀ (pow_ne_zero 6 he) hcross).symm
theorem three_walsh_channels_recover_norm_one_factor
    (a b c d : K) (ha : a≠0) (hb : b≠0) (hc : c≠0) (hd : d≠0) :
    (a*b/(c*d))*(a*c/(b*d))*(a*d/(b*c))=a^4/(a*b*c*d) := by
  field_simp

theorem walsh_fourth_power_reconstruction
    (a b c d : K) (ha : a≠0) (hb : b≠0) (hc : c≠0) (hd : d≠0) :
    (a*b*c*d)*(a*b/(c*d))*(a*c/(b*d))*(a*d/(b*c))=a^4 := by
  field_simp

theorem walsh_translation_inversion
    (a b c d : K) (ha : a≠0) (hb : b≠0) (hc : c≠0) (hd : d≠0) :
    c*d/(a*b)=(a*b/(c*d))⁻¹ := by
  field_simp
end H12.NormAlgebra
