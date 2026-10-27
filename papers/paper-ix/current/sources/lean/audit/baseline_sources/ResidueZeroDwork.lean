module

public import HurwitzDworkClosure
public import HurwitzInverse
public import WindowIndependence

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.ResidueZeroDwork

open PowerSeries HurwitzDworkClosure DworkAlgebra DworkClosure

variable (p : ℕ) [Fact p.Prime]

/-- Literal residue-zero exponential-section coefficients in the integral ring. -/
def sectionCoefficients (N : ℕ) (d : ℕ) : ℤ_[p] := if N∣d then 1 else 0

@[simp] theorem section_zero (N : ℕ) : sectionCoefficients p N 0=1 := by
  simp [sectionCoefficients]

/-- The prime-power differential shifts agree on the actual section, in characteristic zero. -/
theorem section_defect_zero (m : ℕ) (hm : m∣p-1) :
    DworkCriterion.defect p (p*(p-1)) (sectionCoefficients p (m*p)) = 0 := by
  funext d
  have hd : m*p ∣ p*(p-1) := by
    obtain ⟨q,hq⟩ := hm
    refine ⟨q, ?_⟩
    rw [hq]; ring
  simp [DworkCriterion.defect, sectionCoefficients, Nat.dvd_add_left hd]

/-- All positive defects vanish; integrality at order zero is automatic in Z_p. -/
theorem section_flat (m : ℕ) (hm : m∣p-1) :
    DworkCriterion.flat p (sectionCoefficients p (m*p)) := by
  intro s d
  cases s with
  | zero => simp
  | succ s =>
    have he : DworkCriterion.defectIter p (p*(p-1)) (s+1)
        (sectionCoefficients p (m*p)) = 0 := by
      induction s with
      | zero => exact section_defect_zero p m hm
      | succ s ih =>
        funext n
        rw [DworkCriterion.defectIter_succ]
        simp [ih]
    rw [he]
    exact dvd_zero _

/-- The existing integral lift of the original rational packet, not a newly named sequence. -/
def zeroPacket (m : ℕ) : ℕ → ℤ_[p] :=
  WindowIndependence.coeffPadic p m 0 (Fact.out : p.Prime).pos

/-- The actual full Hurwitz product equals one; all off-support terms are proved zero. -/
theorem zero_packet_section_product (m : ℕ) (hm : 0<m) :
    Hurwitz.convolution (DworkCriterion.packed (m*p) (zeroPacket p m))
      (sectionCoefficients p (m*p)) = Hurwitz.oneSeries := by
  have hN : 0<m*p := Nat.mul_pos hm (Fact.out : p.Prime).pos
  funext d
  by_cases hd : m*p∣d
  · obtain ⟨r, rfl⟩ := hd
    rw [Hurwitz.convolution, HurwitzInverse.sum_on_multiples (m*p) r hN]
    · have hr := WindowIndependence.coeffPadic_row p m 0 (Fact.out : p.Prime).pos r
      simp only [Nat.add_zero] at hr
      change (∑ q ∈ Finset.range (r+1), _) = _
      have hs : (∑ q ∈ Finset.range (r+1),
          (((m*p*r).choose (m*p*q) : ℤ_[p]) *
          DworkCriterion.packed (m*p) (zeroPacket p m) (m*p*q) *
          sectionCoefficients p (m*p) (m*p*r-m*p*q))) =
          ∑ q ∈ Finset.range (r+1),
            (((m*p*r).choose (m*p*q) : ℤ_[p]) * zeroPacket p m q) := by
        apply Finset.sum_congr rfl
        intro q _
        rw [DworkCriterion.packed_multiple _ hN]
        simp [sectionCoefficients, ← Nat.mul_sub_left_distrib]
      rw [hs]
      simpa [zeroPacket, Hurwitz.oneSeries, hN.ne'] using hr
    · intro k _ hk
      simp [DworkCriterion.packed, hk]
  · have hd0 : d≠0 := by intro he; subst d; exact hd (dvd_zero _)
    rw [Hurwitz.convolution, Hurwitz.oneSeries, ite_eq_right hd0]
    apply Finset.sum_eq_zero
    intro k hk
    by_cases hNk : m*p∣k
    · have hdiff : ¬m*p∣d-k := by
        intro H
        have h := dvd_add hNk H
        rw [Nat.add_sub_of_le (Finset.mem_range_succ_iff.mp hk)] at h
        exact hd h
      simp [sectionCoefficients, hdiff]
    · simp [DworkCriterion.packed, hNk]

/-- Coefficient convolution is exactly multiplication of the actual exponential encodings. -/
theorem encode_convolution (a b : ℕ → ℤ_[p]) :
    encodeIntegral p (Hurwitz.convolution a b) = encodeIntegral p a * encodeIntegral p b := by
  apply_fun EGF.decode using (by
    intro f g h
    have hh := congrArg EGF.encode h
    simpa using hh)
  funext n
  have h := EGF.egf_product (fun n => (a n : ℚ_[p])) (fun n => (b n : ℚ_[p])) n
  rw [decode_encodeIntegral]
  change ((Hurwitz.convolution a b n : ℤ_[p]) : ℚ_[p]) = _
  rw [show encodeIntegral p a = EGF.encode (fun n => (a n : ℚ_[p])) from rfl,
    show encodeIntegral p b = EGF.encode (fun n => (b n : ℚ_[p])) from rfl, h]
  simp [Hurwitz.convolution]

/-- The packed original Euler sequence encodes the actual reciprocal of the residue section. -/
theorem zero_packet_is_reciprocal (m : ℕ) (hm : 0<m) :
    encodeIntegral p (DworkCriterion.packed (m*p) (zeroPacket p m)) =
      (encodeIntegral p (sectionCoefficients p (m*p)))⁻¹ := by
  have hc : constantCoeff (encodeIntegral p (sectionCoefficients p (m*p))) = 1 := by
    simp [encodeIntegral, EGF.encode, sectionCoefficients]
  have h := congrArg (encodeIntegral p) (zero_packet_section_product p m hm)
  rw [encode_convolution] at h
  have h1 : encodeIntegral p (Hurwitz.oneSeries : ℕ → ℤ_[p]) = 1 := by
    ext n
    by_cases hn : n=0 <;> simp [encodeIntegral, EGF.encode, Hurwitz.oneSeries, hn, coeff_one]
  rw [h1] at h
  have hu := PowerSeries.mul_inv_cancel (encodeIntegral p (sectionCoefficients p (m*p)))
    (by rw [hc]; exact one_ne_zero)
  calc
    _ = _ * ((encodeIntegral p (sectionCoefficients p (m*p))) *
        (encodeIntegral p (sectionCoefficients p (m*p)))⁻¹) := by rw [hu, mul_one]
    _ = _ := by rw [← mul_assoc, h, one_mul]

/-- Unconditional flatness for the actual j=0 Euler family. No Euler flatness premise. -/
theorem zero_packet_flat (m : ℕ) (hm : m∣p-1) (hmpos : 0<m) :
    DworkCriterion.flat p (DworkCriterion.packed (m*p) (zeroPacket p m)) := by
  apply (flat_encode_iff p _).mp
  rw [zero_packet_is_reciprocal p m hmpos]
  apply flat_reciprocal
  · exact (flat_encode_iff p _).mpr (section_flat p m hm)
  · simp [encodeIntegral, EGF.encode, sectionCoefficients]

/-- All difference orders and rows, at the basic step, for the original residue-zero family. -/
theorem zero_packet_global_bound (m k n : ℕ) (hm : m∣p-1) (hmpos : 0<m) :
    (p:ℤ_[p])^(min k (m*n)) ∣ Mahler.difference ((p-1)/m) k (zeroPacket p m) n :=
  DworkCriterion.saturated_bound_of_flat p m (Fact.out : p.Prime).pos hm hmpos
    (zeroPacket p m) (zero_packet_flat p m hm hmpos) k n

/-- The coefficient lift is proved to represent the original rational Euler coefficients. -/
theorem zero_packet_coe (m n : ℕ) :
    (zeroPacket p m n : ℚ_[p]) = (Congruential.coeff (m*p) 0 n : ℚ_[p]) :=
  WindowIndependence.coeffPadic_coe p m 0 (Fact.out : p.Prime).pos n

end KomorebiPaperIX.ResidueZeroDwork
