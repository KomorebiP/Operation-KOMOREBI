module

public import PaperX.IdealSeriesContinuation
public import CebotarevDensity.ForMathlib.IdealCongruenceCount

/-!
# Actual ideal-norm residue characters: cancellation and boundary limits

The residue group is constructed as the subgroup of unit residues realized by
norms of actual nonzero integral ideals. Its realization premise is discharged
by definition. The inherited geometry-of-numbers count and its Fourier-decay
producer then give a sublinear bound for each nontrivial character, which is
fed to the proved Mellin continuation. No Frobenius-density theorem is used.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter Asymptotics
open scoped Topology nonZeroDivisors
open PaperX.IdealSeriesContinuation
namespace PaperX.NormResidueBoundary

/-- The actual image subgroup of coprime ideal norms, not all unit residues. -/
def realizedResidues (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m] :
    Subgroup (ZMod m)ˣ where
  carrier := {a : (ZMod m)ˣ | ∃ I : (Ideal (𝓞 K))⁰,
    ((Ideal.absNorm (I : Ideal (𝓞 K)) : ZMod m)) = (a : ZMod m)}
  one_mem' := ⟨1, by
    rw [Submonoid.coe_one, Ideal.one_eq_top, Ideal.absNorm_top, Nat.cast_one, Units.val_one]⟩
  mul_mem' := by
    rintro a b ⟨I, hI⟩ ⟨J, hJ⟩
    exact ⟨I * J, by rw [Submonoid.coe_mul, map_mul, Nat.cast_mul, hI, hJ, Units.val_mul]⟩
  inv_mem' := by
    rintro a ⟨I, hI⟩
    refine ⟨I ^ (orderOf a - 1), ?_⟩
    have hi : a⁻¹ = a ^ (orderOf a - 1) := inv_eq_of_mul_eq_one_right
      (by rw [← pow_succ', Nat.sub_add_cancel (orderOf_pos a), pow_orderOf_eq_one])
    rw [SubmonoidClass.coe_pow, map_pow, Nat.cast_pow, hI, hi, Units.val_pow_eq_pow_val]

instance realizedFintype (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m] :
    Fintype (realizedResidues K m) := Fintype.ofFinite _

def count (K : Type*) [Field K] [NumberField K] (m : ℕ) (a : ZMod m) (N : ℕ) : ℕ :=
  Nat.card {I : NonzeroIdeal K // Ideal.absNorm I.1 ≤ N ∧
    ((Ideal.absNorm I.1 : ZMod m)) = a}

private theorem count_eq (K : Type*) [Field K] [NumberField K]
    (m : ℕ) (a : ZMod m) (N : ℕ) :
    count K m a N = Nat.card {I : (Ideal (𝓞 K))⁰ //
      Ideal.absNorm (I : Ideal (𝓞 K)) ≤ N ∧
      ((Ideal.absNorm (I : Ideal (𝓞 K)) : ZMod m)) = a} := by
  apply Nat.card_congr
  exact
    { toFun := fun I ↦ ⟨⟨I.1.1, mem_nonZeroDivisors_of_ne_zero I.1.2⟩, I.2⟩
      invFun := fun I ↦ ⟨⟨I.1, by simpa using nonZeroDivisors.coe_ne_zero I.1⟩, I.2⟩
      left_inv := fun _ ↦ rfl
      right_inv := fun _ ↦ rfl }

/-- The uniform count has no supplied realization or Fourier-decay premise. -/
theorem actual_uniform_count (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m] :
    ∃ κ C : ℝ, ∀ a : realizedResidues K m, ∀ N : ℕ, 1 ≤ N →
      |(count K m ((a : (ZMod m)ˣ) : ZMod m) N : ℝ) - κ * N| ≤
        C * (N : ℝ) ^ (1 - (Module.finrank ℚ K : ℝ)⁻¹) := by
  obtain ⟨κ, C, h⟩ := exists_card_norm_le_norm_residue_eq_sub_mul_rpow_le_uniform K m
    (realizedResidues K m) (fun χ hχ ↦
      tendsto_sum_char_mul_cardNormLeResidue_div_of_realized K m (realizedResidues K m)
        (fun _ h ↦ h) χ hχ)
  exact ⟨κ, C, fun a N hN ↦ by rw [count_eq]; exact h a.1 a.2 N hN⟩

open Classical in
/-- Zero off the realized unit subgroup, the character value on that subgroup. -/
def value {K : Type*} [Field K] [NumberField K] {m : ℕ} [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (a : ZMod m) : ℂ :=
  ∑ u : realizedResidues K m,
    if ((u : (ZMod m)ˣ) : ZMod m) = a then (χ u : ℂ) else 0

private theorem residue_injective {K : Type*} [Field K] [NumberField K] {m : ℕ} [NeZero m] :
    Function.Injective (fun u : realizedResidues K m ↦ ((u : (ZMod m)ˣ) : ZMod m)) :=
  fun _ _ h ↦ Subtype.ext (Units.ext h)

theorem value_apply {K : Type*} [Field K] [NumberField K] {m : ℕ} [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (u : realizedResidues K m) :
    value χ ((u : (ZMod m)ˣ) : ZMod m) = (χ u : ℂ) := by
  classical
  simp only [value, residue_injective.eq_iff]
  simp

theorem norm_value_le_one {K : Type*} [Field K] [NumberField K] {m : ℕ} [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (a : ZMod m) : ‖value χ a‖ ≤ 1 := by
  classical
  by_cases h : ∃ u : realizedResidues K m, ((u : (ZMod m)ˣ) : ZMod m) = a
  · obtain ⟨u, rfl⟩ := h
    rw [value_apply]
    exact (((Units.coeHom ℂ).comp χ).isOfFinOrder (isOfFinOrder_of_finite u)).norm_eq_one.le
  · have hz : value χ a = 0 := by
      apply Finset.sum_eq_zero
      intro u _
      exact ite_eq_right (fun hu ↦ h ⟨u, hu⟩)
    rw [hz, norm_zero]
    exact zero_le_one

/-- The coefficient at an actual nonzero ideal is its norm-residue character. -/
def weight {K : Type*} [Field K] [NumberField K] {m : ℕ} [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (I : NonzeroIdeal K) : ℂ :=
  value χ (Ideal.absNorm I.1 : ZMod m)

private theorem bounded_fibre_count (K : Type*) [Field K] [NumberField K]
    (m : ℕ) (a : ZMod m) (N : ℕ) :
    Nat.card {I : BoundedIdeal K N // a = ((Ideal.absNorm I.1.1 : ZMod m))} =
      count K m a N := by
  apply Nat.card_congr
  exact
    { toFun := fun I ↦ ⟨I.1.1, I.1.2, I.2.symm⟩
      invFun := fun I ↦ ⟨⟨I.1, I.2.1⟩, I.2.2.symm⟩
      left_inv := fun _ ↦ rfl
      right_inv := fun _ ↦ rfl }

/-- Exact finite Fourier regrouping of the norm-bounded ideal sum. -/
theorem sum_weight_eq (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (N : ℕ) :
    (∑' I : BoundedIdeal K N, weight χ I.1) =
      ∑ u : realizedResidues K m, (χ u : ℂ) *
        (count K m ((u : (ZMod m)ˣ) : ZMod m) N : ℂ) := by
  classical
  let : Fintype (BoundedIdeal K N) := Fintype.ofFinite _
  rw [tsum_fintype]
  simp only [weight, value]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun u _ ↦ ?_
  rw [← Finset.sum_filter, Finset.sum_const, nsmul_eq_mul, mul_comm]
  congr 1
  rw [← Fintype.card_subtype, ← Nat.card_eq_fintype_card,
    bounded_fibre_count K m ((u : (ZMod m)ˣ) : ZMod m) N]

/-- Sublinear cancellation for every actual nontrivial norm-residue character. -/
theorem partial_sum_bound (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (hχ : χ ≠ 1) :
    ∃ C : ℝ, ∀ N : ℕ, 1 ≤ N →
      ‖∑' I : BoundedIdeal K N, weight χ I.1‖ ≤
        C * (N : ℝ) ^ (1 - (Module.finrank ℚ K : ℝ)⁻¹) := by
  classical
  obtain ⟨κ, C, hcount⟩ := actual_uniform_count K m
  refine ⟨(Fintype.card (realizedResidues K m) : ℝ) * |C|, fun N hN ↦ ?_⟩
  have hz : ∑ u : realizedResidues K m, (χ u : ℂ) = 0 := sum_char_self_eq_zero_of_ne_one hχ
  rw [sum_weight_eq]
  have hsub : (∑ u : realizedResidues K m, (χ u : ℂ) *
      (count K m ((u : (ZMod m)ˣ) : ZMod m) N : ℂ)) =
      ∑ u : realizedResidues K m, (χ u : ℂ) *
        (((count K m ((u : (ZMod m)ˣ) : ZMod m) N : ℝ) - κ * N : ℝ) : ℂ) := by
    push_cast
    simp_rw [mul_sub]
    rw [Finset.sum_sub_distrib, ← Finset.sum_mul, hz, zero_mul, sub_zero]
  rw [hsub]
  calc ‖∑ u : realizedResidues K m, (χ u : ℂ) *
        (((count K m ((u : (ZMod m)ˣ) : ZMod m) N : ℝ) - κ * N : ℝ) : ℂ)‖
      ≤ ∑ u : realizedResidues K m, ‖(χ u : ℂ) *
        (((count K m ((u : (ZMod m)ˣ) : ZMod m) N : ℝ) - κ * N : ℝ) : ℂ)‖ := norm_sum_le _ _
    _ ≤ ∑ _u : realizedResidues K m, |C| * (N : ℝ) ^ (1 - (Module.finrank ℚ K : ℝ)⁻¹) := by
      refine Finset.sum_le_sum fun u _ ↦ ?_
      have hn : ‖(χ u : ℂ)‖ = 1 :=
        (((Units.coeHom ℂ).comp χ).isOfFinOrder (isOfFinOrder_of_finite u)).norm_eq_one
      rw [norm_mul, hn, one_mul, Complex.norm_real, Real.norm_eq_abs]
      exact (hcount u N hN).trans (mul_le_mul_of_nonneg_right (le_abs_self C)
        (Real.rpow_nonneg (Nat.cast_nonneg N) _))
    _ = _ := by rw [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]; ring

theorem partial_sum_bigO (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (hχ : χ ≠ 1) :
    (fun N : ℕ ↦ ∑' I : BoundedIdeal K N, weight χ I.1)
      =O[atTop] (fun N : ℕ ↦ (N : ℝ) ^ (1 - (Module.finrank ℚ K : ℝ)⁻¹)) := by
  obtain ⟨C, hC⟩ := partial_sum_bound K m χ hχ
  refine isBigO_iff.mpr ⟨C, ?_⟩
  filter_upwards [eventually_ge_atTop 1] with N hN
  rw [Real.norm_of_nonneg (Real.rpow_nonneg (Nat.cast_nonneg N) _)]
  exact hC N hN

/-- Finite limits for actual norm-residue ideal series. Cancellation is proved,
not supplied; nonvanishing is deliberately not asserted by this theorem. -/
theorem actual_boundary_limit (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (χ : realizedResidues K m →* ℂˣ) (hχ : χ ≠ 1) :
    ∃ v : ℂ, Tendsto (fun s : ℝ ↦ ∑' I : NonzeroIdeal K,
      weight χ I * (Ideal.absNorm I.1 : ℂ) ^ (-(s : ℂ))) (𝓝[>] 1) (𝓝 v) := by
  have hd : (1 : ℝ) ≤ (Module.finrank ℚ K : ℝ) := by exact_mod_cast Module.finrank_pos
  have hi : (Module.finrank ℚ K : ℝ)⁻¹ ≤ 1 := by simpa using inv_anti₀ zero_lt_one hd
  have hp : 0 < (Module.finrank ℚ K : ℝ)⁻¹ := inv_pos.mpr (zero_lt_one.trans_le hd)
  exact exists_boundary_limit K (weight χ) (fun I ↦ norm_value_le_one χ _)
    (sub_nonneg.mpr hi) (by linarith) (partial_sum_bigO K m χ hχ)

end PaperX.NormResidueBoundary
