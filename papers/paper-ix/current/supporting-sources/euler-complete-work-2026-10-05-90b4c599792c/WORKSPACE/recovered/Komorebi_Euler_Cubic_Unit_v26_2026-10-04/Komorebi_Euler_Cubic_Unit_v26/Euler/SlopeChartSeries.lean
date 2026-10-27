module
public import Euler.NormalizedLowerChart
public import Euler.LocalRootTransport
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- The lower-root chart when its slope is no deeper than the skeleton's. -/
def slopeBeforeSeries (d δ : ℕ) (A L : Series) : Series :=
  C ((2:D)^(d-δ))*X*A+L

/-- The upper-root chart when its slope is no deeper than the lower slope. -/
def slopeAfterSeries (d δ : ℕ) (A L : Series) : Series :=
  X*A+C ((2:D)^(δ-d))*L

lemma slopeBeforeSeries_restricted (d δ : ℕ) {A L : Series}
    (hA : Restricted A) (hL : Restricted L) :
    Restricted (slopeBeforeSeries d δ A L) := by
  unfold slopeBeforeSeries
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.mul 1
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
        (by simpa using polynomial_restricted (Polynomial.X:Polynomial D))) hA) hL

lemma slopeAfterSeries_restricted (d δ : ℕ) {A L : Series}
    (hA : Restricted A) (hL : Restricted L) :
    Restricted (slopeAfterSeries d δ A L) := by
  unfold slopeAfterSeries
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.mul 1
      (by simpa using polynomial_restricted (Polynomial.X:Polynomial D)) hA)
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hL)

lemma slopeBeforeSeries_reval (d δ : ℕ) {A L : Series}
    (hA : Restricted A) (hL : Restricted L) (y : D) :
    reval (slopeBeforeSeries d δ A L) y=
      (2:D)^(d-δ)*y*reval A y+reval L y := by
  have hX : Restricted ((X:Series)*A) := PowerSeries.isRestricted.mul 1
    (by simpa using polynomial_restricted (Polynomial.X:Polynomial D)) hA
  rw [slopeBeforeSeries,mul_assoc,
    reval_add (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hX) hL,
    reval_C_mul hX,reval_X_mul hA]
  ring

lemma slopeAfterSeries_reval (d δ : ℕ) {A L : Series}
    (hA : Restricted A) (hL : Restricted L) (y : D) :
    reval (slopeAfterSeries d δ A L) y=
      y*reval A y+(2:D)^(δ-d)*reval L y := by
  rw [slopeAfterSeries,
    reval_add (PowerSeries.isRestricted.mul 1
      (by simpa using polynomial_restricted (Polynomial.X:Polynomial D)) hA)
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hL),
    reval_X_mul hA,reval_C_mul hL]

lemma slopeBeforeSeries_red (d δ : ℕ) (A L : Series) (hδ : δ<d) :
    PowerSeries.map red (slopeBeforeSeries d δ A L)=PowerSeries.map red L := by
  rw [slopeBeforeSeries,map_add,map_mul,map_mul,map_C,map_pow,red_two,
    zero_pow (by omega : d-δ≠0),map_zero,zero_mul,zero_mul,zero_add]

lemma slopeAfterSeries_red (d δ : ℕ) (A L : Series) (hδ : d<δ)
    (hA : PowerSeries.map red A=1) :
    PowerSeries.map red (slopeAfterSeries d δ A L)=X := by
  rw [slopeAfterSeries,map_add,map_mul,map_X,hA,mul_one,map_mul,map_C,map_pow,
    red_two,zero_pow (by omega : δ-d≠0),map_zero,zero_mul,add_zero]

lemma slopeEqualSeries_red (d : ℕ) (A L : Series) (c : F₂)
    (hA : PowerSeries.map red A=1) (hL : PowerSeries.map red L=X+C c) :
    PowerSeries.map red (slopeAfterSeries d d A L)=C c := by
  simp only [slopeAfterSeries,Nat.sub_self,pow_zero,map_one,one_mul,map_add,
    map_mul,map_X,hA,mul_one,hL]
  have hx : (X:PowerSeries F₂)+(X:PowerSeries F₂)=0 := by
    ext n
    simp only [map_add,map_zero]
    have h (z:F₂) : z+z=0 := by fin_cases z <;> decide
    exact h _
  rw [← add_assoc,hx,zero_add]

/-- The powers of two are not conflated with chart radius or derivative scale. -/
lemma slopeBefore_normalization (k d δ : ℕ) (hδ : δ≤d) (y a l : D) :
    (2:D)^(k+d)*y*a+(2:D)^δ*((2:D)^k*l)=
      (2:D)^(k+δ)*((2:D)^(d-δ)*y*a+l) := by
  have hd : (2:D)^d=(2:D)^δ*(2:D)^(d-δ) := by
    rw [← pow_add,Nat.add_sub_of_le hδ]
  rw [pow_add,pow_add,hd]
  ring

lemma slopeAfter_normalization (k d δ : ℕ) (hδ : d≤δ) (y a l : D) :
    (2:D)^(k+d)*y*a+(2:D)^δ*((2:D)^k*l)=
      (2:D)^(k+d)*(y*a+(2:D)^(δ-d)*l) := by
  have hd : (2:D)^δ=(2:D)^d*(2:D)^(δ-d) := by
    rw [← pow_add,Nat.add_sub_of_le hδ]
  rw [pow_add,hd]
  ring

/-- Evenness of the whole equal-slope core admits an integral restricted half. -/
theorem restricted_divide_even {f : Series} (hf : Restricted f)
    (he : PowerSeries.map red f=0) :
    ∃ g:Series, C (2:D)*g=f ∧ Restricted g := by
  obtain ⟨g,hg⟩ := divide_even_series f (by
    intro n
    rw [← coeff_map,he]
    simp)
  refine ⟨g,hg,?_⟩
  rw [restricted_iff]
  have hc (n : ℕ) : ‖coeff n g‖=(2:ℝ)*‖coeff n f‖ := by
    have heq:=congrArg (coeff n) hg
    rw [coeff_C_mul] at heq
    have hn:=congrArg norm heq
    rw [norm_mul,norm_two] at hn
    linarith
  simp_rw [hc]
  convert ((restricted_iff f).mp hf).const_mul (2:ℝ) using 1; simp

end Komorebi.Euler
