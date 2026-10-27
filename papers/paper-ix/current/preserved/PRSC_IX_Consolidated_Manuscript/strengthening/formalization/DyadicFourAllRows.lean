module
public import ChargedDworkClosure
public import DyadicFourCongruences
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicFourAllRows
open PowerSeries DworkAlgebra HurwitzDworkClosure DworkCriterion Mahler
open DyadicFourKernel DyadicFourDwork DyadicFourCongruences

abbrev B : PowerSeries ℚ_[2] →ₗ[ℚ_[2]] PowerSeries ℚ_[2] :=
  ChargedDworkClosure.B (derivative ℚ_[2]) 1

def Flat (f : PowerSeries ℚ_[2]) : Prop :=
  ChargedDworkClosure.flat (derivative ℚ_[2]) 1 (integralSeries 2) f

def CoeffFlat (a : ℕ→ℤ_[2]) : Prop := ∀s d, (2:ℤ_[2])^s ∣ difference 4 s a d

theorem decode_B (f : PowerSeries ℚ_[2]) (d : ℕ) :
    EGF.decode (B f) d = (2:ℚ_[2])⁻¹*(EGF.decode f (d+4)-EGF.decode f d) := by
  simp only [B,ChargedDworkClosure.B,LinearMap.smul_apply,LinearMap.sub_apply,
    LinearMap.id_apply,Int.cast_one,one_smul]
  simp only [EGF.decode,coeff_smul,map_sub,smul_eq_mul]
  have h4 := decode_deriv 2 f 4 d
  simp only [EGF.decode] at h4
  linear_combination (2:ℚ_[2])⁻¹*h4

theorem decode_B_iter (f : PowerSeries ℚ_[2]) (s d : ℕ) :
    EGF.decode ((B^s) f) d = ((2:ℚ_[2])⁻¹)^s*difference 4 s (EGF.decode f) d := by
  induction s generalizing d with
  | zero => simp
  | succ s ih =>
    rw [pow_succ',Module.End.mul_apply,decode_B,ih,ih,difference_succ,pow_succ]
    ring

theorem difference_coe (a : ℕ→ℤ_[2]) (s d : ℕ) :
    difference 4 s (fun n => (a n:ℚ_[2])) d = ((difference 4 s a d:ℤ_[2]):ℚ_[2]) := by
  induction s generalizing d with
  | zero => rfl
  | succ s ih => rw [difference_succ,difference_succ,ih,ih]; rfl

theorem flat_encode_iff (a : ℕ→ℤ_[2]) : Flat (encodeIntegral 2 a) ↔ CoeffFlat a := by
  have he : EGF.decode (encodeIntegral 2 a) = fun n => (a n:ℚ_[2]) := by
    funext n; exact decode_encodeIntegral 2 a n
  constructor
  · intro H s d
    have hd := H s d
    change EGF.decode ((B^s) (encodeIntegral 2 a)) d ∈ _ at hd
    rw [decode_B_iter,he,difference_coe] at hd
    exact (normalized_mem_iff 2 _ s).mp hd
  · intro H s d
    change EGF.decode ((B^s) (encodeIntegral 2 a)) d ∈ _
    rw [decode_B_iter,he,difference_coe]
    exact (normalized_mem_iff 2 _ s).mpr (H s d)

theorem packed_difference_support (a : ℕ→ℤ_[2]) (s d : ℕ) (hd : ¬4∣d) :
    difference 4 s (packed 4 a) d = 0 := by
  induction s generalizing d with
  | zero => simp [packed,hd]
  | succ s ih =>
    have hd4 : ¬4∣d+4 := by simpa using hd
    rw [difference_succ,ih _ hd4,ih _ hd,sub_self]

theorem packed_flat_of_kummer (a : ℕ→ℤ_[2]) (H : KummerSequences.Kummer 2 a) :
    CoeffFlat (packed 4 a) := by
  intro s d
  by_cases hd : 4∣d
  · obtain ⟨r,rfl⟩ := hd
    change (2:ℤ_[2])^s ∣ difference (4*1) s (packed 4 a) (4*r)
    rw [packet_difference 4 1 s r (by decide)]
    exact H s r
  · rw [packed_difference_support a s d hd]
    exact dvd_zero _

theorem source_flat (j : ℕ) : Flat (sourceSeries j) :=
  (flat_encode_iff _).mpr (packed_flat_of_kummer _ (source_kummer j))

/-- Reciprocal closure for the unshifted fourth-order operator is derived with charges. -/
theorem flat_reciprocal (f : PowerSeries ℚ_[2]) (H : Flat f) (h0 : constantCoeff f=1) :
    Flat f⁻¹ := by
  have hi := ChargedDworkClosure.flat_inverse (derivative ℚ_[2])
    (integralSeries 2) (integral_derivative 2) 1 f f⁻¹
    (PowerSeries.mul_inv_cancel f (by rw [h0]; exact one_ne_zero)) H
    (integral_inverse 2 f (H 0) h0)
  have hs := ChargedDworkClosure.flat_charge_shift (derivative ℚ_[2]) (-1)
    (integralSeries 2) f⁻¹ hi
  exact hs

theorem actual_packet_flat (j : ℕ) (hj : j<4) :
    Flat (PowerSeries.map (Rat.castHom ℚ_[2])
      (ExponentialSection.expandedPacket 4 (by decide) j)) := by
  rw [packet_is_reciprocal j hj]
  exact flat_reciprocal _ (source_flat j) (sourceSeries_constant j hj)

theorem lifted_flat (j : ℕ) (hj : j<4) : CoeffFlat (packed 4 (normalizedLift j hj)) := by
  apply (flat_encode_iff _).mp
  rw [normalizedLift,SeriesDifferenceBridge.packet_encoding 2 4 _ _ (packet_support j)]
  exact actual_packet_flat j hj

/-- Full normalized Kummer divisibility at every row, including n=0. -/
theorem base_step_bound (j k n : ℕ) (hj : j<4) :
    (2:ℤ_[2])^k ∣ difference 1 k (normalizedLift j hj) n := by
  have H := lifted_flat j hj k (4*n)
  change (2:ℤ_[2])^k ∣ difference (4*1) k (packed 4 (normalizedLift j hj)) (4*n) at H
  rw [packet_difference 4 1 k n (by decide)] at H
  exact H

/-- Every natural-number step inherits the full order, uniformly from the first row. -/
theorem normalized_bound (j u k n : ℕ) (hj : j<4) :
    (2:ℤ_[2])^k ∣ difference u k (normalizedLift j hj) n := by
  have H := StepMultiples.divisibility_transfer ((2:ℤ_[2])^k) 1 u k 0
    (normalizedLift j hj) (fun r _ => base_step_bound j k r hj) n (Nat.zero_le n)
  simpa only [mul_one] using H

theorem normalized_precision (j u k n : ℕ) (hj : j<4) :
    GlobalEulerBoundary.precision 2 (k:ℤ)
      (difference u k (Congruential.coeff 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (normalizedLift j hj) n) _ (normalized_difference_coe j u k n hj)
    _ (normalized_bound j u k n hj)

theorem unnormalized_bound (j u k n : ℕ) (hj : j<4) :
    (2:ℤ_[2])^k ∣ difference u k (unnormalizedLift j hj) n := by
  have he : difference u k (unnormalizedLift j hj) n =
      (j.factorial:ℤ_[2])*difference u k (normalizedLift j hj) n := by
    induction k generalizing n with
    | zero => rfl
    | succ k ih => rw [difference_succ,ih,ih,difference_succ,mul_sub]
  rw [he]
  exact dvd_mul_of_dvd_right (normalized_bound j u k n hj) _

theorem unnormalized_precision (j u k n : ℕ) (hj : j<4) :
    GlobalEulerBoundary.precision 2 (k:ℤ)
      (difference u k (Congruential.unnormalized 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (unnormalizedLift j hj) n) _ (unnormalized_difference_coe j u k n hj)
    _ (unnormalized_bound j u k n hj)

end KomorebiPaperIX.DyadicFourAllRows
