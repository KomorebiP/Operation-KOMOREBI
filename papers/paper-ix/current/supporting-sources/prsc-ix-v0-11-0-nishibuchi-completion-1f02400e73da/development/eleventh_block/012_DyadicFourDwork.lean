module
public import CubicDworkClosure
public import DyadicFourKernel
public import EulerDefect
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicFourDwork
open PowerSeries DworkAlgebra HurwitzDworkClosure DworkCriterion DyadicFourKernel

/-- The larger normalized operator is (D^8-D^4)/2, not the odd-prime operator. -/
abbrev B4 : PowerSeries ℚ_[2] →ₗ[ℚ_[2]] PowerSeries ℚ_[2] :=
  CubicDworkAlgebra.B (derivative ℚ_[2]) 2

def Flat4 (f:PowerSeries ℚ_[2]) : Prop :=
  CubicDworkClosure.flat (derivative ℚ_[2]) 2 (integralSeries 2) f

def CoeffFlat4 (a:ℕ→ℤ_[2]) : Prop := ∀s d, (2:ℤ_[2])^s ∣ defectIter 4 4 s a d

theorem decode_B4 (f:PowerSeries ℚ_[2]) (d:ℕ) :
    EGF.decode (B4 f) d = (2:ℚ_[2])⁻¹*(EGF.decode f (d+8)-EGF.decode f (d+4)) := by
  simp only [B4,CubicDworkAlgebra.B,LinearMap.smul_apply,LinearMap.sub_apply,
    EGF.decode,coeff_smul,map_sub,smul_eq_mul]
  have h8 := decode_deriv 2 f 8 d
  have h4 := decode_deriv 2 f 4 d
  simp only [EGF.decode] at h8 h4
  change _ = _
  linear_combination (2:ℚ_[2])⁻¹*(h8-h4)

theorem decode_B4_iter (f:PowerSeries ℚ_[2]) (s d:ℕ) :
    EGF.decode ((B4^s) f) d = ((2:ℚ_[2])⁻¹)^s*defectIter 4 4 s (EGF.decode f) d := by
  induction s generalizing d with
  | zero => simp
  | succ s ih =>
    rw [pow_succ',Module.End.mul_apply,decode_B4,ih,ih,defectIter_succ,pow_succ]
    have hd : d+4+4=d+8 := by omega
    rw [hd]
    ring

theorem defect_coe (a:ℕ→ℤ_[2]) (s d:ℕ) :
    defectIter 4 4 s (fun n => (a n:ℚ_[2])) d = (defectIter 4 4 s a d:ℚ_[2]) := by
  induction s generalizing d with
  | zero => rfl
  | succ s ih => rw [defectIter_succ,defectIter_succ,ih,ih]; rfl

theorem flat4_encode_iff (a:ℕ→ℤ_[2]) :
    Flat4 (encodeIntegral 2 a) ↔ CoeffFlat4 a := by
  have he : EGF.decode (encodeIntegral 2 a) = fun n => (a n:ℚ_[2]) := by
    funext n; exact decode_encodeIntegral 2 a n
  constructor
  · intro H s d
    have hd := H s d
    change EGF.decode ((B4^s) (encodeIntegral 2 a)) d ∈ _ at hd
    rw [decode_B4_iter,he,defect_coe] at hd
    exact (normalized_mem_iff 2 _ s).mp hd
  · intro H s d
    change EGF.decode ((B4^s) (encodeIntegral 2 a)) d ∈ _
    rw [decode_B4_iter,he,defect_coe]
    exact (normalized_mem_iff 2 _ s).mpr (H s d)

theorem packed_flat_of_kummer (a:ℕ→ℤ_[2]) (H:KummerSequences.Kummer 2 a) :
    CoeffFlat4 (packed 4 a) := by
  intro s d
  by_cases hd:4∣d
  · obtain ⟨r,rfl⟩ := hd
    rw [defect_is_shifted_difference,←Nat.mul_add]
    change (2:ℤ_[2])^s ∣ Mahler.difference (4*1) s (packed 4 a) (4*(r+s))
    rw [packet_difference 4 1 s (r+s) (by decide)]
    exact H s (r+s)
  · rw [EulerDefect.defect_support 4 4 (dvd_refl _) (packed 4 a)
      (fun n hn => by simp [packed,hn]) s d hd]
    exact dvd_zero _

def sourceSeries (j:ℕ) : PowerSeries ℚ_[2] := encodeIntegral 2 (packed 4 (sourcePacket j))

theorem sourceSeries_flat (j:ℕ) : Flat4 (sourceSeries j) :=
  (flat4_encode_iff _).mpr (packed_flat_of_kummer _ (source_kummer j))

theorem sourceSeries_encoding (j:ℕ) (hj:j<4) :
    sourceSeries j = PowerSeries.map (Rat.castHom ℚ_[2])
      (expand 4 (by decide) (Congruential.sectionKernel 4 j)) := by
  ext d
  by_cases hd:4∣d
  · obtain ⟨r,rfl⟩ := hd
    simp only [sourceSeries,encodeIntegral,EGF.encode,coeff_mk,coeff_map,coeff_expand_mul,
      Congruential.sectionKernel,map_div₀,map_natCast]
    rw [packed_multiple 4 (by decide),source_coe j r hj]
    rw [Nat.cast_choose ℚ_[2] (by omega : 4*r≤4*r+j)]
    rw [show 4*r+j-4*r=j by omega]
    have h1 : ((4*r).factorial:ℚ_[2])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
    have h2 : (j.factorial:ℚ_[2])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
    have h3 : ((4*r+j).factorial:ℚ_[2])≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
    field_simp
  · simp [sourceSeries,encodeIntegral,EGF.encode,packed,hd,
      coeff_expand_of_not_dvd 4 (by decide) _ hd]

theorem sourceSeries_constant (j:ℕ) (hj:j<4) : constantCoeff (sourceSeries j)=1 := by
  rw [sourceSeries_encoding j hj]
  simp [constantCoeff_expand,Congruential.kernel_constant_one]

/-- A genuine reciprocal retains integral Hurwitz coefficients and all larger defects. -/
theorem flat4_reciprocal (f:PowerSeries ℚ_[2]) (H:Flat4 f) (h0:constantCoeff f=1) :
    Flat4 f⁻¹ := by
  apply CubicDworkClosure.flat_inverse (derivative ℚ_[2]) 2 Nat.prime_two
    (integralSeries 2) (integral_derivative 2) f f⁻¹
  · exact PowerSeries.mul_inv_cancel f (by rw [h0]; exact one_ne_zero)
  · exact H
  · exact integral_inverse 2 f (H 0) h0

/-- Identification with the original normalized reciprocal packet. -/
theorem packet_is_reciprocal (j:ℕ) (hj:j<4) :
    PowerSeries.map (Rat.castHom ℚ_[2]) (ExponentialSection.expandedPacket 4 (by decide) j) =
      (sourceSeries j)⁻¹ := by
  apply (PowerSeries.eq_inv_iff_mul_eq_one (by rw [sourceSeries_constant j hj]; exact one_ne_zero)).mpr
  rw [sourceSeries_encoding j hj]
  have h := congrArg (fun f:PowerSeries ℚ => PowerSeries.map (Rat.castHom ℚ_[2])
    (expand 4 (by decide) f)) (Congruential.packet_times_kernel 4 j)
  simpa only [map_mul,map_one,ExponentialSection.expandedPacket] using h

theorem actual_packet_flat (j:ℕ) (hj:j<4) :
    Flat4 (PowerSeries.map (Rat.castHom ℚ_[2]) (ExponentialSection.expandedPacket 4 (by decide) j)) := by
  rw [packet_is_reciprocal j hj]
  exact flat4_reciprocal _ (sourceSeries_flat j) (sourceSeries_constant j hj)

end KomorebiPaperIX.DyadicFourDwork
