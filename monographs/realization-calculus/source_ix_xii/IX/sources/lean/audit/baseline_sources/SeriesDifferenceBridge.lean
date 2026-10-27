module
public import WeightedDworkTransfer
public import StandardWindowPrecision
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.SeriesDifferenceBridge
open PowerSeries HurwitzDworkClosure DworkAlgebra DworkClosure Mahler
variable (p : ℕ) [Fact p.Prime]

/-- The original rational series, after the actual injective coefficient map. -/
def rationalMap (f : PowerSeries ℚ) : PowerSeries ℚ_[p] :=
  PowerSeries.map (Rat.castHom ℚ_[p]) f

/-- Factorial-scaled coefficients commute with scalar extension. -/
theorem decode_rationalMap (f : PowerSeries ℚ) (d : ℕ) :
    EGF.decode (rationalMap p f) d = ((EGF.decode f d : ℚ) : ℚ_[p]) := by
  simp only [rationalMap, EGF.decode, coeff_map]
  rfl

/-- Integral packet values constructed from proved integral Hurwitz coefficients. -/
def packetLift (N : ℕ) (f : PowerSeries ℚ)
    (hf : rationalMap p f∈integralSeries p) (n : ℕ) : ℤ_[p] :=
  ⟨EGF.decode (rationalMap p f) (N*n), hf (N*n)⟩

@[simp] theorem packetLift_coe (N : ℕ) (f : PowerSeries ℚ)
    (hf : rationalMap p f∈integralSeries p) (n : ℕ) :
    (packetLift p N f hf n : ℚ_[p]) = ((EGF.decode f (N*n) : ℚ) : ℚ_[p]) :=
  decode_rationalMap p f (N*n)

/-- The sparse encoding reconstructs the original series; support is checked, not inferred from a name. -/
theorem packet_encoding (N : ℕ) (f : PowerSeries ℚ)
    (hf : rationalMap p f∈integralSeries p)
    (hs : ∀ d, ¬N∣d → coeff d f=0) :
    encodeIntegral p (DworkCriterion.packed N (packetLift p N f hf)) = rationalMap p f := by
  have he : (fun d => ((DworkCriterion.packed N (packetLift p N f hf) d : ℤ_[p]) : ℚ_[p])) =
      EGF.decode (rationalMap p f) := by
    funext d
    by_cases hd : N∣d
    · rw [DworkCriterion.packed, ite_eq_left hd]
      change EGF.decode (rationalMap p f) (N*(d/N)) = _
      rw [Nat.mul_div_cancel' hd]
    · rw [DworkCriterion.packed, ite_eq_right hd]
      simp [rationalMap, EGF.decode, hs d hd]
  change EGF.encode _ = _
  rw [he, EGF.encode_decode]

/-- A genuinely flat rational series with the proved packet support has saturated differences in Z_p. -/
theorem packet_divisibility (m : ℕ) (hm : m∣p-1) (hmpos : 0<m)
    (f : PowerSeries ℚ)
    (hf : DworkClosure.flat (derivative ℚ_[p]) p (integralSeries p) (rationalMap p f))
    (hs : ∀ d, ¬(m*p)∣d → coeff d f=0) (u k n : ℕ) :
    (p:ℤ_[p])^(min k (m*n)) ∣ difference (u*((p-1)/m)) k
      (packetLift p (m*p) f (hf 0)) n := by
  have H : DworkCriterion.flat p
      (DworkCriterion.packed (m*p) (packetLift p (m*p) f (hf 0))) := by
    apply (flat_encode_iff p _).mp
    rw [packet_encoding p (m*p) f (hf 0) hs]
    exact hf
  apply StepMultiples.saturated_multiple_step (p:ℤ_[p]) m ((p-1)/m)
  intro r s
  exact DworkCriterion.saturated_bound_of_flat p m (Fact.out : p.Prime).pos hm hmpos _ H r s

/-- The final rational statement is proved by comparison with the integral lift, not field divisibility. -/
theorem packet_precision (m : ℕ) (hm : m∣p-1) (hmpos : 0<m)
    (f : PowerSeries ℚ)
    (hf : DworkClosure.flat (derivative ℚ_[p]) p (integralSeries p) (rationalMap p f))
    (hs : ∀ d, ¬(m*p)∣d → coeff d f=0) (u k n : ℕ) :
    GlobalEulerBoundary.precision p ((min k (m*n):ℕ):ℤ)
      (difference (u*((p-1)/m)) k (fun r => EGF.decode f (m*p*r)) n) := by
  apply StandardWindowPrecision.rational_precision_of_divisibility p
    (difference (u*((p-1)/m)) k (packetLift p (m*p) f (hf 0)) n)
  · change (algebraMap ℤ_[p] ℚ_[p]) (difference _ _ _ _) =
      (algebraMap ℚ ℚ_[p]) (difference _ _ _ _)
    rw [←DifferenceFiltration.difference_map, ←DifferenceFiltration.difference_map]
    congr 1
  · exact packet_divisibility p m hm hmpos f hf hs u k n

end KomorebiPaperIX.SeriesDifferenceBridge
