module
public import RiccatiFlatPropagation
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.RatioRiccati
open PowerSeries SingularRatioAmice ExponentialSection SectionLogBridge SingularNormalizedSection
open EulerSeriesInverse RiccatiFlatPropagation

/-- Derivative relation for the original factorial-denominator sections, away from the wrap index. -/
theorem original_derivative (N c : ℕ) (hc : c+1<N) :
    derivative ℚ (originalSection N (c+1))=originalSection N c := by
  have h := section_derivative N ((c+1:ℕ):ZMod N)
  have hr : ((c+1:ℕ):ZMod N)-1=(c:ZMod N) := by push_cast; ring
  rw [hr, sectionSeries_is_original N (c+1) hc,
    sectionSeries_is_original N c (by omega)] at h
  exact h

/-- A nonzero leading coefficient certifies that the original section can be cancelled. -/
theorem original_nonzero (N c : ℕ) (hc : c<N) : originalSection N c≠0 := by
  intro hz
  have h := congrArg (coeff c) hz
  simp only [originalSection, coeff_mk, Nat.mod_eq_of_lt hc, ite_true, map_zero] at h
  exact (one_div_ne_zero (Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero c))) h

/-- The actual consecutive ratios satisfy the Riccati equation. -/
theorem ratio_riccati (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c+2<N) :
    X*derivative ℚ (ratioSeries N hN (c+1)) =
      ratioSeries N hN (c+1)*(1+ratioSeries N hN c-ratioSeries N hN (c+1)) := by
  let H := originalSection N (c+2)
  let J := originalSection N (c+1)
  let K := originalSection N c
  let r := ratioSeries N hN c
  let s := ratioSeries N hN (c+1)
  have hs : s*H=X*J := ratio_cleared N hN (c+1) (by omega)
  have hr : r*J=X*K := ratio_cleared N hN c (by omega)
  have hder := congrArg (derivative ℚ) hs
  have hH : derivative ℚ H=J := original_derivative N (c+1) hc
  have hJ : derivative ℚ J=K := original_derivative N c (by omega)
  simp only [Derivation.leibniz, derivative_X, smul_eq_mul, hH, hJ, one_mul] at hder
  change derivative ℚ s*H+s*J=J+X*K at hder
  change X*derivative ℚ s=s*(1+r-s)
  apply mul_right_cancel₀ (pow_ne_zero 2 (original_nonzero N (c+2) hc))
  change (X*derivative ℚ s)*H^2=(s*(1+r-s))*H^2
  linear_combination (X*H)*hder+((s-1-r)*H)*hs-(X*H)*hr

variable (p : ℕ) [Fact p.Prime]

/-- Scalar extension of the independently defined rational ratio. -/
def ratio (N : ℕ) (hN : N≠0) (c : ℕ) : PowerSeries ℚ_[p] :=
  SeriesDifferenceBridge.rationalMap p (ratioSeries N hN c)

@[simp] theorem ratio_zero (N : ℕ) (hN : N≠0) (c : ℕ) :
    constantCoeff (ratio p N hN c)=(c+1:ℚ_[p]) := by
  simp [ratio, SeriesDifferenceBridge.rationalMap, ratio_constant]

/-- The mapped Riccati equation uses the actual derivative on Q_p[[t]]. -/
theorem ratio_riccati_padic (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c+2<N) :
    X*derivative ℚ_[p] (ratio p N hN (c+1)) =
      ratio p N hN (c+1)*(1+ratio p N hN c-ratio p N hN (c+1)) := by
  have h := congrArg (PowerSeries.map (Rat.castHom ℚ_[p])) (ratio_riccati N hN c hc)
  simpa only [map_mul, map_add, map_sub, map_one, PowerSeries.map_X,
    ←derivative_map_rat, ratio, SeriesDifferenceBridge.rationalMap] using h

/-- Original ratios have p-supported coefficients whenever p divides the packet modulus. -/
theorem ratio_p_support (N : ℕ) (hN : N≠0) (hdiv : p∣N) (c : ℕ) :
    Supported p p (ratio p N hN c) := by
  intro d hd
  have hNd : ¬N∣d := fun h => hd (dvd_trans hdiv h)
  simp only [ratio, SeriesDifferenceBridge.rationalMap, coeff_map,
    RatioSeriesSupport.ratio_support N hN c d hNd, map_zero]

/-- Centering the actual ratio gives exactly the equation used in the Picard propagation. -/
theorem centered_equation (N : ℕ) (hN : N≠0) (c : ℕ) (hc : c+2<N) :
    euler p (c+2) (ratio p N hN (c+1)-C (c+2:ℚ_[p])) =
      forcing p (c+2) (ratio p N hN c-C (c+1:ℚ_[p]))
        (ratio p N hN (c+1)-C (c+2:ℚ_[p])) := by
  simp only [euler, forcing, Derivation.map_sub, derivative_C, sub_zero, mul_sub]
  rw [ratio_riccati_padic p N hN c hc]
  simp only [map_add, map_natCast]
  ring

/-- Nonsingular propagation for the actual original ratio family. -/
theorem next_ratio_flat (N : ℕ) (hN : N≠0) (hdiv : p∣N) (c : ℕ)
    (hc : c+2<N) (hn : ¬p∣c+2) (hf : Flat p (ratio p N hN c)) :
    Flat p (ratio p N hN (c+1)) := by
  let q := ratio p N hN c-C (c+1:ℚ_[p])
  let y := ratio p N hN (c+1)-C (c+2:ℚ_[p])
  have hq : Flat p q := flat_sub p hf (flat_constant p _ (natCast_mem _ _))
  have hsup : Supported p p q := supported_sub p (ratio_p_support p N hN hdiv c)
    (supported_constant p p _)
  have hq0 : constantCoeff q=0 := by simp [q]
  have hy0 : constantCoeff y=0 := by simp [y]; ring
  have hy : Flat p y := riccati_solution_flat p (c+2) hn q y hq hsup hq0 hy0
    (centered_equation p N hN c hc)
  have h := flat_add p hy (flat_constant p (c+2:ℚ_[p]) (natCast_mem _ _))
  simpa only [y, sub_add_cancel] using h

end KomorebiPaperIX.RatioRiccati
