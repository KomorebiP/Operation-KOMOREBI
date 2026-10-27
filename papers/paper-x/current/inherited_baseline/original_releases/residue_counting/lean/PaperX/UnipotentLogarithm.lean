import PaperX.NilpotentExponential
import Mathlib.Tactic.NormNum

/-! Finite logarithmic recovery for nilpotence order at most three.
The exponential is Mathlib's actual nilpotent exponential. The logarithm
here is deliberately quadratic, and every inverse theorem states its
cubic nilpotence hypothesis explicitly. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.UnipotentLogarithm

variable {A : Type*} [Ring A] [Module ℚ A]

/-- Quadratic logarithm, meaningful as a complete logarithm when `(u-1)^3=0`. -/
def log₂ (u : A) : A := (u - 1) - (1 / 2 : ℚ) • (u - 1) ^ 2

theorem exp_of_cube_zero {a : A} (ha : a ^ 3 = 0) :
    IsNilpotent.exp a = 1 + a + (1 / 2 : ℚ) • a ^ 2 := by
  rw [IsNilpotent.exp_eq_sum ha]
  norm_num [Finset.sum_range_succ]

theorem quadratic_square {a : A} (ha : a ^ 3 = 0) (c : ℚ) :
    (a + c • a ^ 2) ^ 2 = a ^ 2 := by
  have h₃ : a * a * a = 0 := by simpa only [pow_succ, pow_two, pow_zero, one_mul] using ha
  have h₄ : (a * a) * (a * a) = 0 := by rw [← mul_assoc, h₃, zero_mul]
  simp only [pow_two, add_mul, mul_add, smul_mul_assoc, mul_smul_comm]
  rw [← mul_assoc a a a, h₃, h₄]
  simp

theorem quadratic_cube_zero {a : A} (ha : a ^ 3 = 0) (c : ℚ) :
    (a + c • a ^ 2) ^ 3 = 0 := by
  rw [pow_succ, quadratic_square ha]
  have h₄ : a ^ 2 * a ^ 2 = 0 := by
    rw [← pow_add]
    exact pow_eq_zero_of_le (by decide) ha
  rw [mul_add, ← pow_succ, ha, mul_smul_comm, h₄, smul_zero, zero_add]

theorem exp_sub_one_cube_zero {a : A} (ha : a ^ 3 = 0) :
    (IsNilpotent.exp a - 1) ^ 3 = 0 := by
  rw [exp_of_cube_zero ha]
  have h : 1 + a + (1 / 2 : ℚ) • a ^ 2 - 1 = a + (1 / 2 : ℚ) • a ^ 2 := by abel
  rw [h]
  exact quadratic_cube_zero ha _

theorem log_exp {a : A} (ha : a ^ 3 = 0) : log₂ (IsNilpotent.exp a) = a := by
  rw [log₂, exp_of_cube_zero ha]
  have h : 1 + a + (1 / 2 : ℚ) • a ^ 2 - 1 = a + (1 / 2 : ℚ) • a ^ 2 := by abel
  rw [h, quadratic_square ha]
  exact add_sub_cancel_right _ _

theorem log_cube_zero {u : A} (hu : (u - 1) ^ 3 = 0) : (log₂ u) ^ 3 = 0 := by
  simpa only [log₂, sub_eq_add_neg, neg_smul] using quadratic_cube_zero hu (- (1 / 2 : ℚ))

theorem exp_log {u : A} (hu : (u - 1) ^ 3 = 0) : IsNilpotent.exp (log₂ u) = u := by
  rw [exp_of_cube_zero (log_cube_zero hu)]
  have hs : (log₂ u) ^ 2 = (u - 1) ^ 2 := by
    simpa only [log₂, sub_eq_add_neg, neg_smul] using quadratic_square hu (- (1 / 2 : ℚ))
  rw [hs, log₂]
  abel

/-- The actual exponential and quadratic logarithm give a bijection on the stated loci. -/
def cubeEquiv : {a : A // a ^ 3 = 0} ≃ {u : A // (u - 1) ^ 3 = 0} where
  toFun a := ⟨IsNilpotent.exp a, exp_sub_one_cube_zero a.property⟩
  invFun u := ⟨log₂ u, log_cube_zero u.property⟩
  left_inv a := Subtype.ext (log_exp a.property)
  right_inv u := Subtype.ext (exp_log u.property)

theorem exp_injective_on_cube_zero {a b : A} (ha : a ^ 3 = 0) (hb : b ^ 3 = 0)
    (h : IsNilpotent.exp a = IsNilpotent.exp b) : a = b := by
  have he := congrArg log₂ h
  simpa only [log_exp ha, log_exp hb] using he

section Linear
variable {K V W : Type*} [Field K] [CharZero K]
  [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
local instance : Module ℚ (Module.End K V) :=
  Module.compHom (Module.End K V) (algebraMap ℚ K)
open PaperX.NilpotentExponential

/-- Normalize the logarithm of a unipotent sample at parameter `t`. -/
def recoverN (t : K) (U : Module.End K V) : Module.End K V := t⁻¹ • log₂ U

omit [CharZero K] in
theorem smul_cube_zero {N : Module.End K V} (hN : N ^ 3 = 0) (t : K) :
    (t • N) ^ 3 = 0 := by simp [smul_pow, hN]

theorem recoverN_expN {N : Module.End K V} (hN : N ^ 3 = 0) {t : K} (ht : t ≠ 0) :
    recoverN t (expN N t) = N := by
  rw [recoverN, expN, log_exp (smul_cube_zero hN t)]
  simp [smul_smul, ht]

theorem log₂_field (U : Module.End K V) :
    log₂ U = (U - 1) - (1 / 2 : K) • (U - 1) ^ 2 := by
  change (U - 1) - ((algebraMap ℚ K) (1 / 2)) • (U - 1) ^ 2 = _
  simp

/-- Polynomial logarithms preserve actual linear intertwiners. -/
theorem log_intertwines (U : Module.End K V) (Z : Module.End K W)
    (f : V →ₗ[K] W) (h : Z ∘ₗ f = f ∘ₗ U) :
    log₂ Z ∘ₗ f = f ∘ₗ log₂ U := by
  have h₁ : (Z - 1) ∘ₗ f = f ∘ₗ (U - 1) := by
    simp only [LinearMap.sub_comp, LinearMap.comp_sub, Module.End.one_eq_id,
      LinearMap.id_comp, LinearMap.comp_id, h]
  have h₂ := Module.End.commute_pow_left_of_commute h₁ 2
  simp only [log₂_field, LinearMap.sub_comp, LinearMap.comp_sub,
    LinearMap.smul_comp, LinearMap.comp_smul, h₁, h₂]

/-- One nonzero-parameter unipotent sample determines the monodromy operator
when both operators have nilpotence order at most three. -/
theorem expN_injective {N M : Module.End K V} (hN : N ^ 3 = 0) (hM : M ^ 3 = 0)
    {t : K} (ht : t ≠ 0) (h : expN N t = expN M t) : N = M := by
  have he := congrArg (recoverN t) h
  simpa only [recoverN_expN hN ht, recoverN_expN hM ht] using he

/-- At cubic nilpotence, a map intertwines monodromy exactly when it intertwines
one exponential sample with a nonzero common parameter. -/
theorem expN_intertwines_iff {N : Module.End K V} {M : Module.End K W}
    (hN : N ^ 3 = 0) (hM : M ^ 3 = 0) (f : V →ₗ[K] W) {t : K} (ht : t ≠ 0) :
    expN M t ∘ₗ f = f ∘ₗ expN N t ↔ M ∘ₗ f = f ∘ₗ N := by
  constructor
  · intro h
    have hl := log_intertwines (expN N t) (expN M t) f h
    rw [expN, expN, log_exp (smul_cube_zero hM t),
      log_exp (smul_cube_zero hN t)] at hl
    ext x
    have hx := LinearMap.congr_fun hl x
    apply smul_right_injective W ht
    simpa using hx
  · exact fun h => expN_intertwines ⟨3, hN⟩ ⟨3, hM⟩ f h t

theorem recoverN_cube_zero {U : Module.End K V} (hU : (U - 1) ^ 3 = 0) (t : K) :
    (recoverN t U) ^ 3 = 0 :=
  smul_cube_zero (log_cube_zero hU) t⁻¹

theorem expN_recoverN {U : Module.End K V} (hU : (U - 1) ^ 3 = 0)
    {t : K} (ht : t ≠ 0) : expN (recoverN t U) t = U := by
  unfold expN recoverN
  simpa [smul_smul, ht] using exp_log hU

/-- Fixed vectors of a linear operator are killed by its quadratic logarithm. -/
theorem log_kills_fixed {U : Module.End K V} {x : V} (hx : U x = x) :
    log₂ U x = 0 := by
  rw [log₂_field]
  have h : (U - 1) x = 0 := by simp [hx]
  simp [LinearMap.sub_apply, LinearMap.smul_apply, pow_two, Module.End.mul_apply, h]

/-- For cubic nilpotence, one nonzero exponential sample has exactly the
monodromy kernel as its fixed space. -/
theorem expN_fixed_iff {N : Module.End K V} (hN : N ^ 3 = 0) {t : K} (ht : t ≠ 0)
    (x : V) : expN N t x = x ↔ N x = 0 := by
  constructor
  · intro hx
    have hl := log_kills_fixed hx
    rw [expN, log_exp (smul_cube_zero hN t)] at hl
    exact (smul_eq_zero.mp hl).resolve_left ht
  · exact expN_identity_on_kernel ⟨3, hN⟩ t

theorem kernel_expN_sub_one {N : Module.End K V} (hN : N ^ 3 = 0)
    {t : K} (ht : t ≠ 0) : LinearMap.ker (expN N t - 1) = LinearMap.ker N := by
  ext x
  simp only [LinearMap.mem_ker, LinearMap.sub_apply, Module.End.one_apply, sub_eq_zero]
  exact expN_fixed_iff hN ht x
end Linear

end PaperX.UnipotentLogarithm
