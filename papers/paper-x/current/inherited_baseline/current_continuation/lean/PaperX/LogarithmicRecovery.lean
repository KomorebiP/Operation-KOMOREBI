import PaperX.NilpotentLogarithm
import PaperX.NilpotentExponential

/-! General logarithmic extraction from an actual unipotent sample.
The coefficient field has characteristic zero. Nilpotence may have any finite
order, and the underlying vector spaces need not be finite dimensional. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.LogarithmicRecovery

open PaperX.FiniteLogarithm PaperX.NilpotentLogarithm
open PaperX.NilpotentExponential

variable {K V W : Type*} [Field K] [CharZero K]
  [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

local instance : Algebra ℚ (Module.End K V) :=
  Algebra.compHom (Module.End K V) (algebraMap ℚ K)

/-- Normalize the finite logarithm by the supplied nonzero sample parameter. -/
def recoverN (t : K) (U : Module.End K V) : Module.End K V := t⁻¹ • log U

theorem recoverN_expN {N : Module.End K V} (hN : IsNilpotent N)
    {t : K} (ht : t ≠ 0) : recoverN t (expN N t) = N := by
  rw [recoverN, expN, log_exp (hN.smul t)]
  simp [smul_smul, ht]

/-- The logarithm is a finite polynomial over the original coefficient field. -/
theorem log_polynomial {U : Module.End K V} {d : ℕ} (hU : (U - 1) ^ d = 0) :
    log U = ∑ j ∈ Finset.range d, ((-1 : K) ^ (j + 1) / (j : K)) • (U - 1) ^ j := by
  rw [log_eq_sum hU]
  apply Finset.sum_congr rfl
  intro j hj
  change ((algebraMap ℚ K) ((-1 : ℚ) ^ (j + 1) / (j : ℚ))) • (U - 1) ^ j = _
  simp only [map_div₀, map_pow, map_neg, map_one, map_natCast]

/-- A linear map intertwining unipotent operators also intertwines their
finite logarithms, even when their nilpotence orders differ. -/
theorem log_intertwines (U : Module.End K V) (Z : Module.End K W)
    (hU : IsNilpotent (U - 1)) (hZ : IsNilpotent (Z - 1))
    (f : V →ₗ[K] W) (h : Z ∘ₗ f = f ∘ₗ U) :
    log Z ∘ₗ f = f ∘ₗ log U := by
  obtain ⟨a, ha⟩ := hU
  obtain ⟨b, hb⟩ := hZ
  have h₁ : (Z - 1) ∘ₗ f = f ∘ₗ (U - 1) := by
    simp only [LinearMap.sub_comp, LinearMap.comp_sub, Module.End.one_eq_id,
      LinearMap.id_comp, LinearMap.comp_id, h]
  rw [log_polynomial (pow_eq_zero_of_le (Nat.le_max_right a b) hb),
    log_polynomial (pow_eq_zero_of_le (Nat.le_max_left a b) ha)]
  ext x
  simp only [LinearMap.comp_apply, LinearMap.sum_apply, LinearMap.smul_apply,
    map_sum, map_smul]
  apply Finset.sum_congr rfl
  intro j hj
  exact congrArg (fun y => ((-1 : K) ^ (j + 1) / (j : K)) • y)
    (LinearMap.congr_fun (Module.End.commute_pow_left_of_commute h₁ j) x)

/-- A single nonzero-parameter exponential sample determines an arbitrary
nilpotent monodromy operator. -/
theorem expN_injective {N M : Module.End K V} (hN : IsNilpotent N)
    (hM : IsNilpotent M) {t : K} (ht : t ≠ 0)
    (h : expN N t = expN M t) : N = M := by
  have he := congrArg (recoverN t) h
  simpa only [recoverN_expN hN ht, recoverN_expN hM ht] using he

/-- Intertwining one common nonzero unipotent sample is equivalent to
intertwining the underlying nilpotent operators. -/
theorem expN_intertwines_iff {N : Module.End K V} {M : Module.End K W}
    (hN : IsNilpotent N) (hM : IsNilpotent M) (f : V →ₗ[K] W)
    {t : K} (ht : t ≠ 0) :
    expN M t ∘ₗ f = f ∘ₗ expN N t ↔ M ∘ₗ f = f ∘ₗ N := by
  constructor
  · intro h
    have hl := log_intertwines (expN N t) (expN M t)
      (IsNilpotent.isNilpotent_exp_sub_one (hN.smul t))
      (IsNilpotent.isNilpotent_exp_sub_one (hM.smul t)) f h
    rw [expN, expN, log_exp (hM.smul t), log_exp (hN.smul t)] at hl
    ext x
    have hx := LinearMap.congr_fun hl x
    apply smul_right_injective W ht
    simpa using hx
  · exact fun h => expN_intertwines hN hM f h t

theorem recoverN_nilpotent {U : Module.End K V} (hU : IsNilpotent (U - 1)) (t : K) :
    IsNilpotent (recoverN t U) := (isNilpotent_log hU).smul _

theorem expN_recoverN {U : Module.End K V} (hU : IsNilpotent (U - 1))
    {t : K} (ht : t ≠ 0) : expN (recoverN t U) t = U := by
  unfold expN recoverN
  simpa [smul_smul, ht] using exp_log hU

/-- Fixed vectors of a unipotent operator are killed by its finite logarithm. -/
theorem log_kills_fixed {U : Module.End K V} (hU : IsNilpotent (U - 1))
    {x : V} (hx : U x = x) : log U x = 0 := by
  obtain ⟨d, hd⟩ := hU
  rw [log_polynomial hd]
  simp only [LinearMap.sum_apply, LinearMap.smul_apply]
  apply Finset.sum_eq_zero
  intro j hj
  by_cases hzero : j = 0
  · simp [hzero]
  · obtain ⟨i, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hzero
    have hz : (U - 1) x = 0 := by simp [hx]
    rw [pow_succ (U - 1), Module.End.mul_apply, hz, map_zero, smul_zero]

/-- One nonzero exponential sample has exactly the monodromy kernel as
its fixed space, for arbitrary finite nilpotence order. -/
theorem expN_fixed_iff {N : Module.End K V} (hN : IsNilpotent N)
    {t : K} (ht : t ≠ 0) (x : V) : expN N t x = x ↔ N x = 0 := by
  constructor
  · intro hx
    have hl := log_kills_fixed
      (IsNilpotent.isNilpotent_exp_sub_one (hN.smul t)) hx
    rw [log_exp (hN.smul t)] at hl
    exact (smul_eq_zero.mp hl).resolve_left ht
  · exact expN_identity_on_kernel hN t

theorem kernel_expN_sub_one {N : Module.End K V} (hN : IsNilpotent N)
    {t : K} (ht : t ≠ 0) : LinearMap.ker (expN N t - 1) = LinearMap.ker N := by
  ext x
  simp only [LinearMap.mem_ker, LinearMap.sub_apply, Module.End.one_apply, sub_eq_zero]
  exact expN_fixed_iff hN ht x

end PaperX.LogarithmicRecovery
