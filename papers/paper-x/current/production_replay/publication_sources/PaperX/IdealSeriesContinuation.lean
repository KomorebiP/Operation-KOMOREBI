module

public import CebotarevDensity.NumberFieldEulerProduct
public import Mathlib.NumberTheory.LSeries.SumCoeff
public import Mathlib.Analysis.MellinTransform

/-!
# Boundary continuation of a weighted number-field ideal series

The series on the open half-plane is summed over actual nonzero ideals. Its
norm-fibre coefficients are regrouped exactly. Sublinear cancellation of their
partial sums constructs a Mellin continuation across one. No unordered,
conditionally convergent ideal sum at the boundary is asserted.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter Asymptotics MeasureTheory Set
open scoped Topology BigOperators
namespace PaperX.IdealSeriesContinuation

abbrev BoundedIdeal (K : Type*) [Field K] [NumberField K] (N : ℕ) :=
  {I : NonzeroIdeal K // Ideal.absNorm I.1 ≤ N}

instance finiteBoundedIdeal (K : Type*) [Field K] [NumberField K] (N : ℕ) :
    Finite (BoundedIdeal K N) :=
  have : Finite {I : Ideal (𝓞 K) // Ideal.absNorm I ≤ N} :=
    (Ideal.finite_setOfPred_absNorm_le (S := 𝓞 K) N).to_subtype
  Finite.of_injective (fun I : BoundedIdeal K N ↦
    (⟨I.1.1, I.2⟩ : {I : Ideal (𝓞 K) // Ideal.absNorm I ≤ N}))
    (fun _ _ h ↦ Subtype.ext (Subtype.ext (congrArg (fun I : {I : Ideal (𝓞 K) // Ideal.absNorm I ≤ N} ↦ I.1) h)))

instance finiteNormFibre (K : Type*) [Field K] [NumberField K] (n : ℕ) :
    Finite {I : NonzeroIdeal K // Ideal.absNorm I.1 = n} :=
  Finite.of_injective (fun I : {I : NonzeroIdeal K // Ideal.absNorm I.1 = n} ↦
    (⟨I.1, I.2.le⟩ : BoundedIdeal K n)) (fun _ _ h ↦ Subtype.ext (congrArg (fun I : BoundedIdeal K n ↦ I.1) h))

def coeff (K : Type*) [Field K] [NumberField K] (w : NonzeroIdeal K → ℂ) (n : ℕ) : ℂ :=
  ∑' I : {I : NonzeroIdeal K // Ideal.absNorm I.1 = n}, w I.1

theorem coeff_zero (K : Type*) [Field K] [NumberField K] (w : NonzeroIdeal K → ℂ) :
    coeff K w 0 = 0 := by
  have : IsEmpty {I : NonzeroIdeal K // Ideal.absNorm I.1 = 0} :=
    ⟨fun I ↦ I.1.2 (Ideal.absNorm_eq_zero_iff.mp I.2)⟩
  rw [coeff, tsum_empty]

theorem norm_coeff_le (K : Type*) [Field K] [NumberField K]
    (w : NonzeroIdeal K → ℂ) (hw : ∀ I, ‖w I‖ ≤ 1) (n : ℕ) :
    ‖coeff K w n‖ ≤ (idealNormMultiplicity K n : ℝ) := by
  classical
  let : Fintype {I : NonzeroIdeal K // Ideal.absNorm I.1 = n} := Fintype.ofFinite _
  calc ‖coeff K w n‖
      ≤ ∑' I : {I : NonzeroIdeal K // Ideal.absNorm I.1 = n}, ‖w I.1‖ :=
        norm_tsum_le_tsum_norm Summable.of_finite
    _ ≤ ∑' _I : {I : NonzeroIdeal K // Ideal.absNorm I.1 = n}, (1 : ℝ) :=
        Summable.tsum_le_tsum (fun I ↦ hw I.1) Summable.of_finite Summable.of_finite
    _ = (idealNormMultiplicity K n : ℝ) := by
        rw [tsum_fintype, Finset.sum_const, Finset.card_univ, nsmul_eq_mul, mul_one,
          idealNormMultiplicity, Nat.card_eq_fintype_card]

/-- Exact regrouping by the norm, including the bounded-norm domain. -/
theorem sum_coeff_eq (K : Type*) [Field K] [NumberField K]
    (w : NonzeroIdeal K → ℂ) (N : ℕ) :
    ∑ n ∈ Finset.Icc 1 N, coeff K w n = ∑' I : BoundedIdeal K N, w I.1 := by
  classical
  let : Fintype (BoundedIdeal K N) := Fintype.ofFinite _
  rw [tsum_fintype, ← Finset.sum_fiberwise_of_maps_to (t := Finset.Icc 1 N)
    (g := fun I : BoundedIdeal K N ↦ Ideal.absNorm I.1.1)
    (fun I _ ↦ Finset.mem_Icc.mpr
      ⟨Nat.one_le_iff_ne_zero.mpr (mt Ideal.absNorm_eq_zero_iff.mp I.1.2), I.2⟩)
    (fun I ↦ w I.1)]
  refine Finset.sum_congr rfl fun n hn ↦ ?_
  rw [coeff, ← Finset.sum_subtype_eq_sum_filter, Finset.subtype_univ]
  let : Fintype {I : NonzeroIdeal K // Ideal.absNorm I.1 = n} := Fintype.ofFinite _
  rw [tsum_fintype]
  exact Fintype.sum_equiv
    { toFun := fun I ↦ (⟨⟨I.1, I.2.le.trans (Finset.mem_Icc.mp hn).2⟩, I.2⟩ :
        {I : BoundedIdeal K N // Ideal.absNorm I.1.1 = n})
      invFun := fun I ↦ ⟨I.1.1, I.2⟩
      left_inv := fun _ ↦ rfl
      right_inv := fun _ ↦ rfl } _ _ fun _ ↦ rfl

theorem sum_norm_coeff_bigO (K : Type*) [Field K] [NumberField K]
    (w : NonzeroIdeal K → ℂ) (hw : ∀ I, ‖w I‖ ≤ 1) :
    (fun N : ℕ ↦ ∑ n ∈ Finset.Icc 1 N, ‖coeff K w n‖)
      =O[atTop] (fun N : ℕ ↦ (N : ℝ) ^ (1 : ℝ)) := by
  refine (isBigO_of_le atTop fun N ↦ ?_).trans (sum_idealNormMultiplicity_isBigO K)
  rw [Real.norm_of_nonneg (Finset.sum_nonneg fun _ _ ↦ norm_nonneg _),
    Real.norm_of_nonneg (Finset.sum_nonneg fun _ _ ↦ Nat.cast_nonneg _)]
  exact Finset.sum_le_sum fun n _ ↦ norm_coeff_le K w hw n

theorem lseries_eq_ideal_sum (K : Type*) [Field K] [NumberField K]
    (w : NonzeroIdeal K → ℂ) (hw : ∀ I, ‖w I‖ ≤ 1) {s : ℂ} (hs : 1 < s.re) :
    LSeries (coeff K w) s = ∑' I : NonzeroIdeal K, w I * (Ideal.absNorm I.1 : ℂ) ^ (-s) := by
  classical
  let e := Equiv.sigmaFiberEquiv (fun I : NonzeroIdeal K ↦ Ideal.absNorm I.1)
  have hn : Summable fun I : NonzeroIdeal K ↦ ‖w I * (Ideal.absNorm I.1 : ℂ) ^ (-s)‖ := by
    refine Summable.of_nonneg_of_le (fun _ ↦ norm_nonneg _) (fun I ↦ ?_)
      (hasSum_nonzeroIdeal_absNorm_cpow K hs).summable.norm
    rw [norm_mul]
    exact mul_le_of_le_one_left (norm_nonneg _) (hw I)
  have he : Summable fun x : Σ n, {I : NonzeroIdeal K // Ideal.absNorm I.1 = n} ↦
      w (e x) * (Ideal.absNorm (e x).1 : ℂ) ^ (-s) :=
    (e.summable_iff (f := fun I : NonzeroIdeal K ↦
      w I * (Ideal.absNorm I.1 : ℂ) ^ (-s))).mpr hn.of_norm
  have hf : ∀ n : ℕ,
      (∑' I : {I : NonzeroIdeal K // Ideal.absNorm I.1 = n},
        w I.1 * (Ideal.absNorm I.1.1 : ℂ) ^ (-s)) = coeff K w n * (n : ℂ) ^ (-s) := by
    intro n
    rw [tsum_congr (fun I : {I : NonzeroIdeal K // Ideal.absNorm I.1 = n} ↦
      show w I.1 * (Ideal.absNorm I.1.1 : ℂ) ^ (-s) = w I.1 * (n : ℂ) ^ (-s) by rw [I.2]),
      tsum_mul_right, coeff]
  rw [show LSeries (coeff K w) s = ∑' n, coeff K w n * (n : ℂ) ^ (-s) from
      tsum_congr fun n ↦ LSeries.term_def₀ (coeff_zero K w) s n,
    ← e.tsum_eq (fun I : NonzeroIdeal K ↦ w I * (Ideal.absNorm I.1 : ℂ) ^ (-s)), he.tsum_sigma]
  exact (tsum_congr hf).symm

private theorem integral_eq_mellin (S : ℝ → ℂ) (hS : ∀ t < 1, S t = 0) (s : ℂ) :
    ∫ t in Ioi (1 : ℝ), S t * (t : ℂ) ^ (-(s + 1)) = mellin S (-s) := by
  rw [mellin, show (∫ t in Ioi (0 : ℝ), (t : ℂ) ^ (-s - 1) • S t) =
      ∫ t in Ioi (1 : ℝ), (t : ℂ) ^ (-s - 1) • S t from ?_]
  · refine setIntegral_congr_fun measurableSet_Ioi fun t _ ↦ ?_
    rw [smul_eq_mul]
    ring_nf
  · have hi : Ioi (0 : ℝ) ∩ Ioi (1 : ℝ) = Ioi (1 : ℝ) :=
      inter_eq_right.mpr (Ioi_subset_Ioi (by norm_num))
    rw [← hi, ← setIntegral_indicator measurableSet_Ioi]
    refine setIntegral_congr_ae measurableSet_Ioi ?_
    filter_upwards [show ∀ᵐ t : ℝ ∂volume, t ≠ 1 from
      ae_iff.mpr (by simp : volume {t : ℝ | ¬ t ≠ 1} = 0)] with t ht _
    rw [indicator_apply]
    by_cases h1 : t ∈ Ioi (1 : ℝ)
    · rw [ite_eq_left h1]
    · rw [ite_eq_right h1, hS t (lt_of_le_of_ne (not_lt.mp (by simpa using h1)) ht), smul_zero]

/-- A genuine analytic extension, constructed by Mellin integration of exact
norm-ordered partial sums. The cancellation premise will be instantiated for
actual ideal-norm residue characters in the next module. -/
theorem analytic_extension (K : Type*) [Field K] [NumberField K]
    (w : NonzeroIdeal K → ℂ) (hw : ∀ I, ‖w I‖ ≤ 1) {r : ℝ} (hr : 0 ≤ r) (hr1 : r < 1)
    (hO : (fun N : ℕ ↦ ∑' I : BoundedIdeal K N, w I.1)
      =O[atTop] (fun N : ℕ ↦ (N : ℝ) ^ r)) :
    ∃ F : ℂ → ℂ, AnalyticOn ℂ F {s : ℂ | r < s.re} ∧
      ∀ s : ℂ, 1 < s.re →
        F s = ∑' I : NonzeroIdeal K, w I * (Ideal.absNorm I.1 : ℂ) ^ (-s) := by
  classical
  let c := coeff K w
  let S : ℝ → ℂ := fun t ↦ ∑ n ∈ Finset.Icc 1 ⌊t⌋₊, c n
  have hOc : (fun N : ℕ ↦ ∑ n ∈ Finset.Icc 1 N, c n)
      =O[atTop] (fun N : ℕ ↦ (N : ℝ) ^ r) := by
    simpa only [c, sum_coeff_eq] using hO
  have hS0 : ∀ t : ℝ, t < 1 → S t = 0 := by
    intro t ht
    dsimp only [S]
    rw [Nat.floor_eq_zero.mpr ht, Finset.Icc_eq_empty (by norm_num), Finset.sum_empty]
  have hSr : S =O[atTop] (fun t : ℝ ↦ t ^ r) :=
    (hOc.comp_tendsto tendsto_nat_floor_atTop).trans
      (isEquivalent_nat_floor.isBigO.rpow hr (eventually_ge_atTop 0))
  refine ⟨fun s ↦ s * mellin S (-s), ?_, fun s hs ↦ ?_⟩
  · refine DifferentiableOn.analyticOn (fun s hs ↦ ?_)
      (isOpen_lt continuous_const Complex.continuous_re)
    change r < s.re at hs
    have hfc : LocallyIntegrableOn S (Ioi (0 : ℝ)) := by
      simpa only [one_mul] using (locallyIntegrableOn_mul_sum_Icc (a := 0) (m := 1)
        c le_rfl (locallyIntegrableOn_const 1)).mono_set Ioi_subset_Ici_self
    have htop : S =O[atTop] (fun t : ℝ ↦ t ^ (-(-r))) := by simpa using hSr
    have hbot : S =O[𝓝[>] (0 : ℝ)] (fun t : ℝ ↦ t ^ (-(-s.re - 1))) :=
      Filter.EventuallyEq.trans_isBigO
        (by filter_upwards [Ioo_mem_nhdsGT one_pos] with t ht using hS0 t ht.2)
        (isBigO_zero _ _)
    have hd : DifferentiableAt ℂ (mellin S) (-s) :=
      mellin_differentiableAt_of_isBigO_rpow hfc htop (by rw [Complex.neg_re]; linarith)
        hbot (by rw [Complex.neg_re]; linarith)
    exact (differentiableAt_id.mul (hd.comp s differentiableAt_id.neg)).differentiableWithinAt
  · have hsum : LSeriesSummable c s := LSeriesSummable_of_sum_norm_bigO
      (sum_norm_coeff_bigO K w hw) zero_le_one hs
    rw [← lseries_eq_ideal_sum K w hw hs,
      LSeries_eq_mul_integral c hr (hr1.trans hs) hsum hOc,
      integral_eq_mellin S hS0 s]

/-- The actual open-half-plane ideal series has a finite right boundary limit. -/
theorem exists_boundary_limit (K : Type*) [Field K] [NumberField K]
    (w : NonzeroIdeal K → ℂ) (hw : ∀ I, ‖w I‖ ≤ 1) {r : ℝ} (hr : 0 ≤ r) (hr1 : r < 1)
    (hO : (fun N : ℕ ↦ ∑' I : BoundedIdeal K N, w I.1)
      =O[atTop] (fun N : ℕ ↦ (N : ℝ) ^ r)) :
    ∃ v : ℂ, Tendsto (fun s : ℝ ↦ ∑' I : NonzeroIdeal K,
      w I * (Ideal.absNorm I.1 : ℂ) ^ (-(s : ℂ))) (𝓝[>] 1) (𝓝 v) := by
  obtain ⟨F, hF, heq⟩ := analytic_extension K w hw hr hr1 hO
  have hcont : ContinuousAt F 1 :=
    (hF.analyticAt ((isOpen_lt continuous_const Complex.continuous_re).mem_nhds
      (show (1 : ℂ) ∈ {s : ℂ | r < s.re} from hr1))).continuousAt
  refine ⟨F 1, (hcont.tendsto.comp
    ((Complex.continuous_ofReal.tendsto 1).mono_left nhdsWithin_le_nhds)).congr' ?_⟩
  filter_upwards [self_mem_nhdsWithin] with s hs
  exact heq (s : ℂ) hs

end PaperX.IdealSeriesContinuation
