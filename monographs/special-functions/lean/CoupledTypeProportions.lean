import CoupledGrowthTypes

/-! # Perron proportions of the two real type vectors

The limiting comparisons below retain real-filter boundedness explicitly.
They do not presume convergence of either ordinary type profile.
-/

set_option autoImplicit false
set_option maxHeartbeats 2000000

noncomputable section
open Filter Set
open scoped Topology Matrix

namespace Komorebi.SpecialFunctions.Coupled.Scales

theorem affine_scale_tendsto {p : ℝ} (hp : 0 < p) (c : ℝ) :
    Tendsto (fun R : ℝ => p * (R - c)) atTop atTop := by
  apply tendsto_atTop.2
  intro B
  filter_upwards [eventually_ge_atTop (B / p + c)] with R hR
  have hh := mul_le_mul_of_nonneg_left hR hp.le
  have hd : p * (B / p) = B := mul_div_cancel₀ B (ne_of_gt hp)
  nlinarith only [hh, hd]

theorem affine_power_ratio_tendsto {p : ℝ} (hp : 0 < p) (c ρ : ℝ) :
    Tendsto (fun R : ℝ => (p * (R - c)) ^ ρ / R ^ ρ) atTop (𝓝 (p ^ ρ)) := by
  have hh : Tendsto (fun R : ℝ => p * (1 - c / R)) atTop (𝓝 p) := by
    convert (tendsto_const_nhds (x := p)).mul
      ((tendsto_const_nhds (x := (1 : ℝ))).sub (tendsto_id.const_div_atTop c)) using 1 <;>
      simp
  apply (hh.rpow_const (Or.inl (ne_of_gt hp))).congr'
  filter_upwards [eventually_gt_atTop (max c 0)] with R hR
  have hR0 : 0 < R := lt_of_le_of_lt (le_max_right _ _) hR
  have hRc : 0 < R - c := sub_pos.mpr (lt_of_le_of_lt (le_max_left _ _) hR)
  rw [← Real.div_rpow (mul_pos hp hRc).le hR0.le]
  congr 1
  field_simp

theorem lower_comparison_of_tendsto {f g : ℝ → ℝ} {a : ℝ}
    (hb : atTop.IsBoundedUnder (· ≤ ·) f)
    (hg : Tendsto g atTop (𝓝 a)) (hgf : g ≤ᶠ[atTop] f) :
    a ≤ Filter.liminf f atTop := by
  have hh := liminf_le_liminf hgf hg.isBoundedUnder_ge hb.isCoboundedUnder_ge
  rwa [hg.liminf_eq] at hh

theorem upper_comparison_of_tendsto {f g : ℝ → ℝ} {a : ℝ}
    (hb : atTop.IsBoundedUnder (· ≥ ·) f)
    (hg : Tendsto g atTop (𝓝 a)) (hfg : f ≤ᶠ[atTop] g) :
    Filter.limsup f atTop ≤ a := by
  have hh := limsup_le_limsup hfg hb.isCoboundedUnder_le hg.isBoundedUnder_le
  rwa [hg.limsup_eq] at hh

theorem canonical_type_envelopes (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {ε : ℝ} (hε : 0 < ε) :
    (∀ᶠ R in atTop, s.lowerType hs hstrict i - ε ≤ s.growthRatio hs hstrict i R) ∧
    (∀ᶠ R in atTop, s.growthRatio hs hstrict i R ≤ s.upperType hs hstrict i + ε) := by
  have hb := s.canonical_growth_ratio_bounded hs hstrict i
  exact ⟨(eventually_lt_of_lt_liminf (by dsimp [lowerType]; linarith) hb.2).mono
      (fun _ h => h.le),
    (eventually_lt_of_limsup_lt (by dsimp [upperType]; linarith) hb.1).mono
      (fun _ h => h.le)⟩

def scaledLogProfile (s : Scales) (ρ : ℝ) (i : Fin 2) (p c R : ℝ) : ℝ :=
  Real.log (s.realComponent i (p * (R - c))) / R ^ ρ

theorem scaled_log_factorization (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {p c R : ℝ} (hp : 0 < p) (hR : c < R) :
    s.scaledLogProfile (s.characteristicExponent hs hstrict) i p c R =
      s.growthRatio hs hstrict i (p * (R - c)) *
        ((p * (R - c)) ^ (s.characteristicExponent hs hstrict) /
          R ^ (s.characteristicExponent hs hstrict)) := by
  have hn := ne_of_gt (Real.rpow_pos_of_pos (mul_pos hp (sub_pos.mpr hR))
    (s.characteristicExponent hs hstrict))
  dsimp [scaledLogProfile, growthRatio]
  field_simp

theorem scaled_type_envelopes (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {p ε : ℝ} (hp : 0 < p) (c : ℝ) (hε : 0 < ε) :
    (∀ᶠ R in atTop, (s.lowerType hs hstrict i - ε) *
        ((p * (R - c)) ^ (s.characteristicExponent hs hstrict) /
          R ^ (s.characteristicExponent hs hstrict)) ≤
      s.scaledLogProfile (s.characteristicExponent hs hstrict) i p c R) ∧
    (∀ᶠ R in atTop, s.scaledLogProfile (s.characteristicExponent hs hstrict) i p c R ≤
      (s.upperType hs hstrict i + ε) *
        ((p * (R - c)) ^ (s.characteristicExponent hs hstrict) /
          R ^ (s.characteristicExponent hs hstrict))) := by
  have ht := affine_scale_tendsto hp c
  have hh := s.canonical_type_envelopes hs hstrict i hε
  have hlo := ht.eventually hh.1
  have hhi := ht.eventually hh.2
  have hboth : ∀ᶠ R : ℝ in atTop,
      (s.lowerType hs hstrict i - ε) *
        ((p * (R - c)) ^ (s.characteristicExponent hs hstrict) /
          R ^ (s.characteristicExponent hs hstrict)) ≤
        s.scaledLogProfile (s.characteristicExponent hs hstrict) i p c R ∧
      s.scaledLogProfile (s.characteristicExponent hs hstrict) i p c R ≤
        (s.upperType hs hstrict i + ε) *
          ((p * (R - c)) ^ (s.characteristicExponent hs hstrict) /
            R ^ (s.characteristicExponent hs hstrict)) := by
    filter_upwards [hlo, hhi, eventually_gt_atTop (max c 0)] with R hl hu hR
    have hR0 := lt_of_le_of_lt (le_max_right c 0) hR
    have hRc := lt_of_le_of_lt (le_max_left c 0) hR
    have hf : 0 ≤ (p * (R - c)) ^ (s.characteristicExponent hs hstrict) /
        R ^ (s.characteristicExponent hs hstrict) :=
      (div_pos (Real.rpow_pos_of_pos (mul_pos hp (sub_pos.mpr hRc)) _)
        (Real.rpow_pos_of_pos hR0 _)).le
    rw [s.scaled_log_factorization hs hstrict i hp hRc]
    exact ⟨mul_le_mul_of_nonneg_right hl hf, mul_le_mul_of_nonneg_right hu hf⟩
  exact ⟨hboth.mono (fun _ h => h.1), hboth.mono (fun _ h => h.2)⟩

theorem log_power_correction_tendsto {ρ : ℝ} (hρ : 0 < ρ) (c : ℝ) :
    Tendsto (fun R : ℝ => (Real.log R + c) / R ^ ρ) atTop (𝓝 0) := by
  have h1 := (isLittleO_log_rpow_atTop hρ).tendsto_div_nhds_zero
  have h2 := (tendsto_rpow_atTop hρ).const_div_atTop c
  simpa only [add_div, add_zero] using h1.add h2

theorem lower_type_row (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {p u : ℝ} (hp : 0 < p) (hu : 0 < u)
    (hrow : ∀ᶠ R in atTop,
      s.scaledLogProfile (s.characteristicExponent hs hstrict) 0 p 1 R +
        s.scaledLogProfile (s.characteristicExponent hs hstrict) 1 u 1 R ≤
          s.growthRatio hs hstrict i R) :
    s.lowerType hs hstrict 0 * p ^ (s.characteristicExponent hs hstrict) +
      s.lowerType hs hstrict 1 * u ^ (s.characteristicExponent hs hstrict) ≤
        s.lowerType hs hstrict i := by
  have hε (ε : ℝ) (hε : 0 < ε) :
      (s.lowerType hs hstrict 0 - ε) * p ^ (s.characteristicExponent hs hstrict) +
        (s.lowerType hs hstrict 1 - ε) * u ^ (s.characteristicExponent hs hstrict) ≤
          s.lowerType hs hstrict i := by
    have hlim := ((affine_power_ratio_tendsto hp 1 (s.characteristicExponent hs hstrict)).const_mul
      (s.lowerType hs hstrict 0 - ε)).add
      ((affine_power_ratio_tendsto hu 1 (s.characteristicExponent hs hstrict)).const_mul
        (s.lowerType hs hstrict 1 - ε))
    apply lower_comparison_of_tendsto (s.canonical_growth_ratio_bounded hs hstrict i).1 hlim
    filter_upwards [(s.scaled_type_envelopes hs hstrict 0 hp 1 hε).1,
      (s.scaled_type_envelopes hs hstrict 1 hu 1 hε).1, hrow] with R h0 h1 hR
    exact (add_le_add h0 h1).trans hR
  have ht : Tendsto (fun ε : ℝ =>
      (s.lowerType hs hstrict 0 - ε) * p ^ (s.characteristicExponent hs hstrict) +
        (s.lowerType hs hstrict 1 - ε) * u ^ (s.characteristicExponent hs hstrict))
      (𝓝[>] 0) (𝓝 (s.lowerType hs hstrict 0 * p ^ (s.characteristicExponent hs hstrict) +
        s.lowerType hs hstrict 1 * u ^ (s.characteristicExponent hs hstrict))) := by
    have hc : Continuous (fun ε : ℝ =>
      (s.lowerType hs hstrict 0 - ε) * p ^ (s.characteristicExponent hs hstrict) +
        (s.lowerType hs hstrict 1 - ε) * u ^ (s.characteristicExponent hs hstrict)) := by fun_prop
    simpa only [sub_zero] using (hc.tendsto 0).mono_left nhdsWithin_le_nhds
  apply le_of_tendsto ht
  filter_upwards [self_mem_nhdsWithin] with ε hpos
  exact hε ε hpos

theorem upper_type_row (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {p u : ℝ} (hp : 0 < p) (hu : 0 < u)
    (hrow : ∀ᶠ R in atTop, s.growthRatio hs hstrict i R ≤
      (Real.log R + Real.log 2) / R ^ (s.characteristicExponent hs hstrict) +
        s.scaledLogProfile (s.characteristicExponent hs hstrict) 0 p 0 R +
          s.scaledLogProfile (s.characteristicExponent hs hstrict) 1 u 0 R) :
    s.upperType hs hstrict i ≤
      s.upperType hs hstrict 0 * p ^ (s.characteristicExponent hs hstrict) +
        s.upperType hs hstrict 1 * u ^ (s.characteristicExponent hs hstrict) := by
  have hρ := (s.characteristicExponent_spec hs hstrict).1
  have hε (ε : ℝ) (hε : 0 < ε) : s.upperType hs hstrict i ≤
      (s.upperType hs hstrict 0 + ε) * p ^ (s.characteristicExponent hs hstrict) +
        (s.upperType hs hstrict 1 + ε) * u ^ (s.characteristicExponent hs hstrict) := by
    have hlim := ((log_power_correction_tendsto hρ (Real.log 2)).add
      ((affine_power_ratio_tendsto hp 0 (s.characteristicExponent hs hstrict)).const_mul
        (s.upperType hs hstrict 0 + ε))).add
        ((affine_power_ratio_tendsto hu 0 (s.characteristicExponent hs hstrict)).const_mul
          (s.upperType hs hstrict 1 + ε))
    simp only [zero_add] at hlim
    apply upper_comparison_of_tendsto (s.canonical_growth_ratio_bounded hs hstrict i).2 hlim
    filter_upwards [(s.scaled_type_envelopes hs hstrict 0 hp 0 hε).2,
      (s.scaled_type_envelopes hs hstrict 1 hu 0 hε).2, hrow] with R h0 h1 hR
    exact hR.trans (add_le_add (add_le_add le_rfl h0) h1)
  have ht : Tendsto (fun ε : ℝ =>
      (s.upperType hs hstrict 0 + ε) * p ^ (s.characteristicExponent hs hstrict) +
        (s.upperType hs hstrict 1 + ε) * u ^ (s.characteristicExponent hs hstrict))
      (𝓝[>] 0) (𝓝 (s.upperType hs hstrict 0 * p ^ (s.characteristicExponent hs hstrict) +
        s.upperType hs hstrict 1 * u ^ (s.characteristicExponent hs hstrict))) := by
    have hc : Continuous (fun ε : ℝ =>
      (s.upperType hs hstrict 0 + ε) * p ^ (s.characteristicExponent hs hstrict) +
        (s.upperType hs hstrict 1 + ε) * u ^ (s.characteristicExponent hs hstrict)) := by fun_prop
    simpa only [add_zero] using (hc.tendsto 0).mono_left nhdsWithin_le_nhds
  apply ge_of_tendsto ht
  filter_upwards [self_mem_nhdsWithin] with ε hpos
  exact hε ε hpos

theorem canonical_lower_type_superinvariant (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.characteristicMatrix (s.characteristicExponent hs hstrict) *ᵥ
      s.lowerType hs hstrict ≤ s.lowerType hs hstrict := by
  have hrow : ∀ i : Fin 2, ∀ᶠ R in atTop,
      s.scaledLogProfile (s.characteristicExponent hs hstrict) 0 (![s.q, s.a] i) 1 R +
        s.scaledLogProfile (s.characteristicExponent hs hstrict) 1 (![s.r, s.b] i) 1 R ≤
          s.growthRatio hs hstrict i R := by
    intro i
    filter_upwards [eventually_gt_atTop (1 : ℝ)] with R hR
    have hh := s.real_axis_log_unit_lower hs hstrict hR
    have hden := (Real.rpow_pos_of_pos (by linarith only [hR] : 0 < R)
      (s.characteristicExponent hs hstrict)).le
    fin_cases i
    · simpa [scaledLogProfile, growthRatio, realComponent, ← add_div] using
        div_le_div_of_nonneg_right hh.1 hden
    · simpa [scaledLogProfile, growthRatio, realComponent, ← add_div] using
        div_le_div_of_nonneg_right hh.2 hden
  intro i
  fin_cases i
  · have hh := s.lower_type_row hs hstrict 0 hs.1 hs.2.1 (hrow 0)
    simpa [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two, mul_comm] using hh
  · have hh := s.lower_type_row hs hstrict 1 hs.2.2.1 hs.2.2.2 (hrow 1)
    simpa [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two, mul_comm] using hh

theorem canonical_upper_type_subinvariant (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.upperType hs hstrict ≤
      s.characteristicMatrix (s.characteristicExponent hs hstrict) *ᵥ s.upperType hs hstrict := by
  have hm := s.minScale_positive hs
  have hrow : ∀ i : Fin 2, ∀ᶠ R in atTop, s.growthRatio hs hstrict i R ≤
      (Real.log R + Real.log 2) / R ^ (s.characteristicExponent hs hstrict) +
        s.scaledLogProfile (s.characteristicExponent hs hstrict) 0 (![s.q, s.a] i) 0 R +
          s.scaledLogProfile (s.characteristicExponent hs hstrict) 1 (![s.r, s.b] i) 0 R := by
    intro i
    filter_upwards [eventually_gt_atTop (0 : ℝ), eventually_ge_atTop (1 / s.minScale)]
      with R hR hRm
    have hmr : 1 ≤ s.minScale * R := by
      have hh := mul_le_mul_of_nonneg_left hRm hm.le
      rwa [mul_one_div_cancel (ne_of_gt hm)] at hh
    have hh := s.real_axis_log_full_upper hs hstrict hR hmr
    have hden := (Real.rpow_pos_of_pos hR (s.characteristicExponent hs hstrict)).le
    fin_cases i
    · simpa [scaledLogProfile, growthRatio, realComponent, ← add_div] using
        div_le_div_of_nonneg_right hh.1 hden
    · simpa [scaledLogProfile, growthRatio, realComponent, ← add_div] using
        div_le_div_of_nonneg_right hh.2 hden
  intro i
  fin_cases i
  · have hh := s.upper_type_row hs hstrict 0 hs.1 hs.2.1 (hrow 0)
    simpa [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two, mul_comm] using hh
  · have hh := s.upper_type_row hs hstrict 1 hs.2.2.1 hs.2.2.2 (hrow 1)
    simpa [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two, mul_comm] using hh

theorem positive_dot_rigidity {l x y : Fin 2 → ℝ}
    (hl : ∀ i, 0 < l i) (hxy : x ≤ y) (hd : dotProduct l x = dotProduct l y) : x = y := by
  have he : l 0 * (y 0 - x 0) + l 1 * (y 1 - x 1) = 0 := by
    simp only [dotProduct, Fin.sum_univ_two] at hd
    nlinarith only [hd]
  have h0 := mul_nonneg (hl 0).le (sub_nonneg.mpr (hxy 0))
  have h1 := mul_nonneg (hl 1).le (sub_nonneg.mpr (hxy 1))
  have hz0 : l 0 * (y 0 - x 0) = 0 := by linarith only [he, h0, h1]
  have hz1 : l 1 * (y 1 - x 1) = 0 := by linarith only [he, h0, h1]
  have hx0 := (mul_eq_zero.mp hz0).resolve_left (ne_of_gt (hl 0))
  have hx1 := (mul_eq_zero.mp hz1).resolve_left (ne_of_gt (hl 1))
  funext i
  fin_cases i
  · exact (sub_eq_zero.mp hx0).symm
  · exact (sub_eq_zero.mp hx1).symm

theorem left_eigenvector_preserves_dot {P : Matrix (Fin 2) (Fin 2) ℝ}
    {l : Fin 2 → ℝ} (hleft : Pᵀ *ᵥ l = l) (x : Fin 2 → ℝ) :
    dotProduct l (P *ᵥ x) = dotProduct l x := by
  calc
    _ = dotProduct x (Pᵀ *ᵥ l) := (Matrix.dotProduct_transpose_mulVec P x l).symm
    _ = dotProduct x l := by rw [hleft]
    _ = dotProduct l x := dotProduct_comm _ _

theorem canonical_type_fixed_vectors (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.characteristicMatrix (s.characteristicExponent hs hstrict) *ᵥ s.lowerType hs hstrict =
      s.lowerType hs hstrict ∧
    s.characteristicMatrix (s.characteristicExponent hs hstrict) *ᵥ s.upperType hs hstrict =
      s.upperType hs hstrict := by
  have hρ := s.characteristicExponent_spec hs hstrict
  have hleft := s.characteristic_left_eigenvector hs hρ.2
  have hl := s.characteristicLeftVector_positive hs hstrict.1 hρ.1
  constructor
  · exact positive_dot_rigidity hl (s.canonical_lower_type_superinvariant hs hstrict)
      (left_eigenvector_preserves_dot hleft _)
  · exact (positive_dot_rigidity hl (s.canonical_upper_type_subinvariant hs hstrict)
      (left_eigenvector_preserves_dot hleft _).symm).symm

theorem characteristic_fixed_proportion (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {x : Fin 2 → ℝ}
    (hx : s.characteristicMatrix (s.characteristicExponent hs hstrict) *ᵥ x = x) :
    x = (x 1 / s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) 1) •
      s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) := by
  let ρ := s.characteristicExponent hs hstrict
  let w := s.normalizedCharacteristicVector ρ
  have hρ := s.characteristicExponent_spec hs hstrict
  have hq : 0 < 1 - s.q ^ ρ :=
    sub_pos.mpr (rpow_contraction_bounds hs.1 hstrict.1 hρ.1).2
  have hw1 : w 1 ≠ 0 := ne_of_gt (s.normalizedCharacteristicVector_positive hs hstrict.1 hρ.1 1)
  have hx0 := congrFun hx 0
  simp only [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two] at hx0
  have hww : (1 - s.q ^ ρ) * w 0 = s.r ^ ρ * w 1 := by
    have hh : s.q ^ ρ * w 0 + s.r ^ ρ * w 1 = w 0 := by
      simpa [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two, ρ, w] using
        congrFun (s.normalized_characteristic_eigenvector hs hρ.2) 0
    nlinarith only [hh]
  funext i
  fin_cases i
  · change x 0 = x 1 / w 1 * w 0
    apply (mul_left_cancel₀ (ne_of_gt hq))
    calc
      (1 - s.q ^ ρ) * x 0 = s.r ^ ρ * x 1 := by
        change s.q ^ ρ * x 0 + s.r ^ ρ * x 1 = x 0 at hx0
        nlinarith only [hx0]
      _ = (x 1 / w 1) * (s.r ^ ρ * w 1) := by field_simp
      _ = (x 1 / w 1) * ((1 - s.q ^ ρ) * w 0) := by rw [hww]
      _ = (1 - s.q ^ ρ) * (x 1 / w 1 * w 0) := by ring
  · change x 1 = x 1 / w 1 * w 1
    exact (div_mul_cancel₀ _ hw1).symm

def lowerTypeScalar (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : ℝ :=
  s.lowerType hs hstrict 1 /
    s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) 1

def upperTypeScalar (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : ℝ :=
  s.upperType hs hstrict 1 /
    s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) 1

theorem canonical_type_proportions (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    0 < s.lowerTypeScalar hs hstrict ∧
    s.lowerTypeScalar hs hstrict ≤ s.upperTypeScalar hs hstrict ∧
    s.lowerType hs hstrict = s.lowerTypeScalar hs hstrict •
      s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) ∧
    s.upperType hs hstrict = s.upperTypeScalar hs hstrict •
      s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) := by
  have hρ := (s.characteristicExponent_spec hs hstrict).1
  have hw := s.normalizedCharacteristicVector_positive hs hstrict.1 hρ 1
  have hf := s.canonical_type_fixed_vectors hs hstrict
  exact ⟨div_pos (s.canonical_types_positive hs hstrict 1).1 hw,
    div_le_div_of_nonneg_right (s.canonical_type_bounds hs hstrict 1).2.1 hw.le,
    s.characteristic_fixed_proportion hs hstrict hf.1,
    s.characteristic_fixed_proportion hs hstrict hf.2⟩

theorem canonical_positive_type_proportions (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ∃ τlo τhi : ℝ, 0 < τlo ∧ τlo ≤ τhi ∧
      s.lowerType hs hstrict = τlo •
        s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) ∧
      s.upperType hs hstrict = τhi •
        s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) :=
  ⟨s.lowerTypeScalar hs hstrict, s.upperTypeScalar hs hstrict,
    s.canonical_type_proportions hs hstrict⟩

theorem characteristic_fixed_ratios (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {x : Fin 2 → ℝ}
    (hx : s.characteristicMatrix (s.characteristicExponent hs hstrict) *ᵥ x = x)
    (hx1 : 0 < x 1) :
    x 0 / x 1 = s.r ^ (s.characteristicExponent hs hstrict) /
      (1 - s.q ^ (s.characteristicExponent hs hstrict)) ∧
    x 0 / x 1 = (1 - s.b ^ (s.characteristicExponent hs hstrict)) /
      s.a ^ (s.characteristicExponent hs hstrict) := by
  have hρ := (s.characteristicExponent_spec hs hstrict).1
  have hq := (rpow_contraction_bounds hs.1 hstrict.1 hρ).2
  have ha := Real.rpow_pos_of_pos hs.2.2.1 (s.characteristicExponent hs hstrict)
  have h0 : s.q ^ (s.characteristicExponent hs hstrict) * x 0 +
      s.r ^ (s.characteristicExponent hs hstrict) * x 1 = x 0 := by
    simpa [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two] using congrFun hx 0
  have h1 : s.a ^ (s.characteristicExponent hs hstrict) * x 0 +
      s.b ^ (s.characteristicExponent hs hstrict) * x 1 = x 1 := by
    simpa [characteristicMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_two] using congrFun hx 1
  constructor
  · apply (div_eq_div_iff (ne_of_gt hx1) (ne_of_gt (sub_pos.mpr hq))).2
    nlinarith only [h0]
  · apply (div_eq_div_iff (ne_of_gt hx1) (ne_of_gt ha)).2
    nlinarith only [h1]

theorem canonical_type_ratios (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    s.lowerType hs hstrict 0 / s.lowerType hs hstrict 1 =
      s.upperType hs hstrict 0 / s.upperType hs hstrict 1 ∧
    s.lowerType hs hstrict 0 / s.lowerType hs hstrict 1 =
      s.r ^ (s.characteristicExponent hs hstrict) /
        (1 - s.q ^ (s.characteristicExponent hs hstrict)) ∧
    s.lowerType hs hstrict 0 / s.lowerType hs hstrict 1 =
      (1 - s.b ^ (s.characteristicExponent hs hstrict)) /
        s.a ^ (s.characteristicExponent hs hstrict) := by
  have hf := s.canonical_type_fixed_vectors hs hstrict
  have hpos := s.canonical_types_positive hs hstrict 1
  have hl := s.characteristic_fixed_ratios hs hstrict hf.1 hpos.1
  have hu := s.characteristic_fixed_ratios hs hstrict hf.2 hpos.2
  exact ⟨hl.1.trans hu.1.symm, hl⟩

theorem ordinary_type_limit_iff (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    (∃ τ : ℝ, Tendsto (s.growthRatio hs hstrict i) atTop (𝓝 τ)) ↔
      s.lowerType hs hstrict i = s.upperType hs hstrict i := by
  constructor
  · rintro ⟨τ, hτ⟩
    exact hτ.liminf_eq.trans hτ.limsup_eq.symm
  · intro he
    have hb := s.canonical_growth_ratio_bounded hs hstrict i
    exact ⟨s.lowerType hs hstrict i, tendsto_of_liminf_eq_limsup rfl he.symm hb.1 hb.2⟩

theorem type_equality_iff_scalar_equality (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    s.lowerType hs hstrict i = s.upperType hs hstrict i ↔
      s.lowerTypeScalar hs hstrict = s.upperTypeScalar hs hstrict := by
  have hh := s.canonical_type_proportions hs hstrict
  have hl := congrFun hh.2.2.1 i
  have hu := congrFun hh.2.2.2 i
  have hw := s.normalizedCharacteristicVector_positive hs hstrict.1
    (s.characteristicExponent_spec hs hstrict).1 i
  change s.lowerType hs hstrict i = s.lowerTypeScalar hs hstrict *
    s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) i at hl
  change s.upperType hs hstrict i = s.upperTypeScalar hs hstrict *
    s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) i at hu
  rw [hl, hu]
  exact mul_left_inj' (ne_of_gt hw)

theorem canonical_type_limit_equivalence (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i j : Fin 2) :
    (∃ τ : ℝ, Tendsto (s.growthRatio hs hstrict i) atTop (𝓝 τ)) ↔
      (∃ τ : ℝ, Tendsto (s.growthRatio hs hstrict j) atTop (𝓝 τ)) := by
  rw [s.ordinary_type_limit_iff hs hstrict i, s.ordinary_type_limit_iff hs hstrict j,
    s.type_equality_iff_scalar_equality hs hstrict i,
    s.type_equality_iff_scalar_equality hs hstrict j]

theorem canonical_type_limit_vector (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    (hi : ∃ τ : ℝ, Tendsto (s.growthRatio hs hstrict i) atTop (𝓝 τ)) :
    ∃ τ : ℝ, 0 < τ ∧ Tendsto (fun R : ℝ => fun j : Fin 2 => s.growthRatio hs hstrict j R)
      atTop (𝓝 (τ • s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict))) := by
  have hh := s.canonical_type_proportions hs hstrict
  have he := (s.type_equality_iff_scalar_equality hs hstrict i).mp
    ((s.ordinary_type_limit_iff hs hstrict i).mp hi)
  refine ⟨s.lowerTypeScalar hs hstrict, hh.1, tendsto_pi_nhds.2 ?_⟩
  intro j
  have hb := s.canonical_growth_ratio_bounded hs hstrict j
  have hj := (s.type_equality_iff_scalar_equality hs hstrict j).mpr he
  have ht := tendsto_of_liminf_eq_limsup rfl hj.symm hb.1 hb.2
  exact (congrFun hh.2.2.1 j) ▸ ht

theorem canonical_maximum_type_proportions (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ∃ τlo τhi : ℝ, 0 < τlo ∧ τlo ≤ τhi ∧
      (fun i : Fin 2 => Filter.liminf (fun R : ℝ => Real.log (s.maximumModulus i R) /
        R ^ (s.characteristicExponent hs hstrict)) atTop) = τlo •
          s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) ∧
      (fun i : Fin 2 => Filter.limsup (fun R : ℝ => Real.log (s.maximumModulus i R) /
        R ^ (s.characteristicExponent hs hstrict)) atTop) = τhi •
          s.normalizedCharacteristicVector (s.characteristicExponent hs hstrict) := by
  have hlo : (fun i : Fin 2 => Filter.liminf (fun R : ℝ => Real.log (s.maximumModulus i R) /
      R ^ (s.characteristicExponent hs hstrict)) atTop) = s.lowerType hs hstrict :=
    funext (fun i => (s.maximum_type_identification hs hstrict i).1)
  have hhi : (fun i : Fin 2 => Filter.limsup (fun R : ℝ => Real.log (s.maximumModulus i R) /
      R ^ (s.characteristicExponent hs hstrict)) atTop) = s.upperType hs hstrict :=
    funext (fun i => (s.maximum_type_identification hs hstrict i).2)
  rw [hlo, hhi]
  exact s.canonical_positive_type_proportions hs hstrict

theorem canonical_maximum_type_limit_equivalence (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i j : Fin 2) :
    (∃ τ : ℝ, Tendsto (fun R : ℝ => Real.log (s.maximumModulus i R) /
        R ^ (s.characteristicExponent hs hstrict)) atTop (𝓝 τ)) ↔
      (∃ τ : ℝ, Tendsto (fun R : ℝ => Real.log (s.maximumModulus j R) /
        R ^ (s.characteristicExponent hs hstrict)) atTop (𝓝 τ)) := by
  have hconv (k : Fin 2) :
      (∃ τ : ℝ, Tendsto (fun R : ℝ => Real.log (s.maximumModulus k R) /
        R ^ (s.characteristicExponent hs hstrict)) atTop (𝓝 τ)) ↔
      (∃ τ : ℝ, Tendsto (s.growthRatio hs hstrict k) atTop (𝓝 τ)) := by
    exact exists_congr (fun τ =>
      Filter.tendsto_congr' (s.maximum_growth_ratio_eventually_eq hs hstrict k))
  rw [hconv, hconv]
  exact s.canonical_type_limit_equivalence hs hstrict i j

end Komorebi.SpecialFunctions.Coupled.Scales
