import Komorebi.PrecisionEnergy

set_option autoImplicit false
namespace Komorebi.RoundedPosterior

/-- A scalar product-score inflation estimate with a precision-independent coefficient. -/
theorem score_inflation_algebra (s u v up vp a b m n h : ℚ)
    (hs : 0 < s) (hu : 0 ≤ u) (hv : 0 ≤ v) (hup : 0 ≤ up) (hvp : 0 ≤ vp)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hum : u ≤ m) (hvn : v ≤ n)
    (hh : 0 ≤ h) (hh1 : h ≤ 1) (hU : up ≤ u+a*h) (hV : vp ≤ v+b*h) :
    up*(s+vp)/s^2 ≤ u*(s+v)/s^2 + (a*(s+n)+m*b+a*b)/s^2*h := by
  have hprod : up*(s+vp) ≤ (u+a*h)*(s+v+b*h) := by
    apply mul_le_mul hU
    · linarith only [hV]
    · exact add_nonneg hs.le hvp
    · exact add_nonneg hu (mul_nonneg ha hh)
  have h1 := mul_le_mul_of_nonneg_right hum (mul_nonneg hb hh)
  have h2 := mul_le_mul_of_nonneg_right hvn (mul_nonneg ha hh)
  have h3 := mul_le_mul_of_nonneg_left hh1 (mul_nonneg (mul_nonneg ha hb) hh)
  have hnum : up*(s+vp) ≤ u*(s+v)+(a*(s+n)+m*b+a*b)*h := by
    nlinarith only [hprod,h1,h2,h3]
  calc
    _ ≤ (u*(s+v)+(a*(s+n)+m*b+a*b)*h)/s^2 :=
      div_le_div_of_nonneg_right hnum (sq_nonneg s)
    _ = _ := by ring

end Komorebi.RoundedPosterior
