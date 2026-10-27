module

public import DworkClosure
public import EGFCoordinates
public import DworkCriterion
public import Mathlib.RingTheory.PowerSeries.Derivative
public import Mathlib.NumberTheory.Padics.PadicIntegers

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.HurwitzDworkClosure

open PowerSeries DworkAlgebra DworkClosure

variable (p : ℕ) [Fact p.Prime]

/-- The actual integral Hurwitz lattice inside Q_p[[t]], using factorial-scaled coefficients. -/
def integralSeries : Subring (PowerSeries ℚ_[p]) where
  carrier := {f | ∀ n, EGF.decode f n ∈ PadicInt.subring p}
  zero_mem' := by intro n; simp
  one_mem' := by
    intro n
    by_cases hn : n=0
    · subst n; simp [EGF.decode]
    · simp [EGF.decode, coeff_one, hn]
  add_mem' := by
    intro f g hf hg n
    rw [EGF.decode_add]
    exact (PadicInt.subring p).add_mem (hf n) (hg n)
  neg_mem' := by
    intro f hf n
    have he : EGF.decode (-f) n = -EGF.decode f n := by simp [EGF.decode]
    rw [he]
    exact (PadicInt.subring p).neg_mem (hf n)
  mul_mem' := by
    intro f g hf hg n
    have h := EGF.egf_product (EGF.decode f) (EGF.decode g) n
    simp only [EGF.encode_decode] at h
    rw [h]
    apply (PadicInt.subring p).sum_mem
    intro r _
    exact (PadicInt.subring p).mul_mem
      ((PadicInt.subring p).mul_mem (natCast_mem (PadicInt.subring p) _) (hf r)) (hg (n-r))

theorem decode_derivative (f : PowerSeries ℚ_[p]) (n : ℕ) :
    EGF.decode (derivative ℚ_[p] f) n = EGF.decode f (n+1) := by
  simp only [EGF.decode, coeff_derivative, Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
  ring

/-- Stability of the actual integral lattice under differentiation is a theorem. -/
theorem integral_derivative (f : PowerSeries ℚ_[p]) (hf : f∈integralSeries p) :
    derivative ℚ_[p] f∈integralSeries p := by
  intro n
  rw [decode_derivative]
  exact hf (n+1)

theorem decode_deriv (f : PowerSeries ℚ_[p]) (a n : ℕ) :
    EGF.decode (deriv (derivative ℚ_[p]) a f) n = EGF.decode f (n+a) := by
  induction a generalizing n with
  | zero => simp
  | succ a ih =>
    rw [deriv_succ, decode_derivative, ih]
    congr 1; omega

theorem decode_one (n : ℕ) : EGF.decode (1 : PowerSeries ℚ_[p]) n = Hurwitz.oneSeries n := by
  by_cases h : n=0
  · subst n; simp [EGF.decode, Hurwitz.oneSeries]
  · simp [EGF.decode, Hurwitz.oneSeries, coeff_one, h]

/-- The inverse recurrence is derived from the actual power-series inverse equation. -/
theorem inverse_decode_step (f : PowerSeries ℚ_[p]) (hf0 : constantCoeff f=1) (n : ℕ) :
    EGF.decode f⁻¹ n = Hurwitz.oneSeries n -
      ∑ k ∈ Finset.range n, (n.choose k : ℚ_[p]) * EGF.decode f⁻¹ k * EGF.decode f (n-k) := by
  have h := EGF.egf_product (EGF.decode f⁻¹) (EGF.decode f) n
  simp only [EGF.encode_decode] at h
  rw [PowerSeries.inv_mul_cancel f (by rw [hf0]; exact one_ne_zero), decode_one,
    Finset.sum_range_succ] at h
  simp only [Nat.choose_self, Nat.cast_one, Nat.sub_self, one_mul] at h
  have hz : EGF.decode f 0=1 := by simp [EGF.decode, coeff_zero_eq_constantCoeff, hf0]
  rw [hz, mul_one] at h
  linear_combination -h

/-- Actual reciprocal integrality, with no integral-inverse hypothesis. -/
theorem integral_inverse (f : PowerSeries ℚ_[p]) (hf : f∈integralSeries p)
    (hf0 : constantCoeff f=1) : f⁻¹∈integralSeries p := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    rw [inverse_decode_step p f hf0 n]
    apply (PadicInt.subring p).sub_mem
    · by_cases hn : n=0 <;> simp [Hurwitz.oneSeries, hn]
    · apply (PadicInt.subring p).sum_mem
      intro k hk
      exact (PadicInt.subring p).mul_mem
        ((PadicInt.subring p).mul_mem (natCast_mem (PadicInt.subring p) _)
          (ih k (Finset.mem_range.mp hk))) (hf (n-k))

/-- Product closure for the actual p-adic Hurwitz flatness condition. -/
theorem flat_product {f g : PowerSeries ℚ_[p]}
    (hf : flat (derivative ℚ_[p]) p (integralSeries p) f)
    (hg : flat (derivative ℚ_[p]) p (integralSeries p) g) :
    flat (derivative ℚ_[p]) p (integralSeries p) (f*g) :=
  flat_mul _ p (Fact.out : p.Prime) _ (integral_derivative p) hf hg

/-- Full all-iterate reciprocal closure, with the inverse and its integrality both derived. -/
theorem flat_reciprocal (f : PowerSeries ℚ_[p])
    (hf : flat (derivative ℚ_[p]) p (integralSeries p) f) (hf0 : constantCoeff f=1) :
    flat (derivative ℚ_[p]) p (integralSeries p) f⁻¹ := by
  apply flat_inverse _ p (Fact.out : p.Prime) _ (integral_derivative p) f f⁻¹
  · exact PowerSeries.mul_inv_cancel f (by rw [hf0]; exact one_ne_zero)
  · exact hf
  · exact integral_inverse p f (by simpa using hf 0) hf0

/-- The normalized differential operator agrees with the literal coefficient defect. -/
theorem decode_B (f : PowerSeries ℚ_[p]) (n : ℕ) :
    EGF.decode (B (derivative ℚ_[p]) p f) n =
      (p:ℚ_[p])⁻¹ * (EGF.decode f (n+p^2)-EGF.decode f (n+p)) := by
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply, EGF.decode,
    coeff_smul, map_sub, smul_eq_mul]
  have h1 := decode_deriv p f (p^2) n
  have h2 := decode_deriv p f p n
  simp only [EGF.decode] at h1 h2
  linear_combination (p:ℚ_[p])⁻¹ * (h1-h2)

theorem decode_B_iterate (f : PowerSeries ℚ_[p]) (s n : ℕ) :
    EGF.decode ((B (derivative ℚ_[p]) p ^ s) f) n =
      ((p:ℚ_[p])⁻¹)^s * DworkCriterion.defectIter p (p*(p-1)) s (EGF.decode f) n := by
  have hp : 0<p := (Fact.out : p.Prime).pos
  induction s generalizing n with
  | zero => simp
  | succ s ih =>
    rw [pow_succ', Module.End.mul_apply, decode_B, ih, ih, DworkCriterion.defectIter_succ]
    have he : p+p*(p-1)=p^2 := by have := Nat.sub_add_cancel (show 1≤p by omega); nlinarith
    rw [Nat.add_assoc, he, pow_succ]
    ring

/-- An explicit integral coefficient sequence encoded as a formal exponential series. -/
def encodeIntegral (a : ℕ → ℤ_[p]) : PowerSeries ℚ_[p] := EGF.encode (fun n => (a n : ℚ_[p]))

@[simp] theorem decode_encodeIntegral (a : ℕ → ℤ_[p]) (n : ℕ) :
    EGF.decode (encodeIntegral p a) n = (a n : ℚ_[p]) := by simp [encodeIntegral]

theorem integral_encode (a : ℕ → ℤ_[p]) : encodeIntegral p a ∈ integralSeries p := by
  intro n
  rw [decode_encodeIntegral]
  exact (a n).property

theorem defectIter_coe (a : ℕ → ℤ_[p]) (L s n : ℕ) :
    DworkCriterion.defectIter p L s (fun r => (a r : ℚ_[p])) n =
      ((DworkCriterion.defectIter p L s a n : ℤ_[p]) : ℚ_[p]) := by
  induction s generalizing n with
  | zero => rfl
  | succ s ih =>
    rw [DworkCriterion.defectIter_succ, DworkCriterion.defectIter_succ, ih, ih]
    rfl

/-- Normalized integrality is equivalent to divisibility inside Z_p, not inside the field. -/
theorem normalized_mem_iff (x : ℤ_[p]) (s : ℕ) :
    ((p:ℚ_[p])⁻¹)^s * (x : ℚ_[p]) ∈ PadicInt.subring p ↔ (p:ℤ_[p])^s ∣ x := by
  have hp : (p:ℚ_[p]) ≠ 0 := Nat.cast_ne_zero.mpr (Fact.out : p.Prime).ne_zero
  constructor
  · intro h
    refine ⟨⟨((p:ℚ_[p])⁻¹)^s * (x : ℚ_[p]), h⟩, ?_⟩
    apply Subtype.ext
    change (x:ℚ_[p]) = (p:ℚ_[p])^s * (((p:ℚ_[p])⁻¹)^s * (x:ℚ_[p]))
    rw [← mul_assoc, ← mul_pow, mul_inv_cancel₀ hp, one_pow, one_mul]
  · rintro ⟨y, rfl⟩
    change ((p:ℚ_[p])⁻¹)^s * ((p:ℚ_[p])^s * (y:ℚ_[p])) ∈ PadicInt.subring p
    rw [← mul_assoc, ← mul_pow, inv_mul_cancel₀ hp, one_pow, one_mul]
    exact y.property

/-- Identification with the previously checked coefficient-level criterion. -/
theorem flat_encode_iff (a : ℕ → ℤ_[p]) :
    flat (derivative ℚ_[p]) p (integralSeries p) (encodeIntegral p a) ↔
      DworkCriterion.flat p a := by
  have he : EGF.decode (encodeIntegral p a) = fun n => (a n : ℚ_[p]) := by
    funext n
    exact decode_encodeIntegral p a n
  constructor
  · intro h s n
    have hn := h s n
    rw [decode_B_iterate, he, defectIter_coe] at hn
    exact (normalized_mem_iff p _ s).mp hn
  · intro h s n
    rw [decode_B_iterate, he, defectIter_coe]
    exact (normalized_mem_iff p _ s).mpr (h s n)

end KomorebiPaperIX.HurwitzDworkClosure
