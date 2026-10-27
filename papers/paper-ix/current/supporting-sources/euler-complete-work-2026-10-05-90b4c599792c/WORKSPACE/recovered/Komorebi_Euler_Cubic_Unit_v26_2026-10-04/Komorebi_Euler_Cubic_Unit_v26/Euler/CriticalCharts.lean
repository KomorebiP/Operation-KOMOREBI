module
public import Mathlib.Analysis.Calculus.Deriv.Pow
public import Mathlib.Analysis.Calculus.Deriv.Comp
public import Mathlib.Analysis.Calculus.Deriv.Add
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.NumberTheory.Padics.PadicNumbers
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.NormNum
@[expose] public section
noncomputable section
namespace Komorebi.Euler
section
variable {K : Type*} [NontriviallyNormedField K]

def CriticalZero (f : K → K) (x : K) : Prop := f x=0 ∧ deriv f x=0

/-- A nonvanishing differentiable gauge preserves value-and-derivative zeros. -/
theorem gauge_critical_iff (u f : K → K) (x : K)
    (hu : DifferentiableAt K u x) (hf : DifferentiableAt K f x)
    (hne : u x ≠ 0) :
    CriticalZero (fun y => u y*f y) x ↔ CriticalZero f x := by
  unfold CriticalZero
  have hder : deriv (fun y => u y*f y) x = deriv u x*f x+u x*deriv f x := by
    simpa only [Pi.mul_def] using (deriv_mul hu hf)
  rw [hder]
  constructor
  · rintro ⟨hv,hd⟩
    have hz : f x=0 := (mul_eq_zero.mp hv).resolve_left hne
    refine ⟨hz, ?_⟩
    simpa only [hz, mul_zero, zero_add, mul_eq_zero, hne, false_or] using hd
  · rintro ⟨hv,hd⟩
    simp [hv,hd]

/-- An invertible first derivative in the coordinate change preserves a
critical zero.  This uses actual analytic derivatives, not unit-step differences. -/
theorem chart_critical_iff (f φ : K → K) (x : K)
    (hf : DifferentiableAt K f (φ x)) (hφ : DifferentiableAt K φ x)
    (hne : deriv φ x ≠ 0) :
    CriticalZero (fun y => f (φ y)) x ↔ CriticalZero f (φ x) := by
  unfold CriticalZero
  have hder : deriv (fun y => f (φ y)) x = deriv f (φ x)*deriv φ x := by
    simpa only [Function.comp_def, smul_eq_mul] using (deriv_comp x hf hφ)
  rw [hder]
  simp only [mul_eq_zero, hne, or_false]

variable [CharZero K]

/-- Exact square-chart criterion at one point.  The only possible critical
zero is the chart center, and it occurs precisely when the scalar is zero. -/
theorem square_chart_critical_iff (u φ : K → K) (ξ x : K)
    (hu : DifferentiableAt K u x) (hφ : DifferentiableAt K φ x)
    (hu0 : u x ≠ 0) (hφ0 : deriv φ x ≠ 0) :
    CriticalZero (fun y => u y*(φ y^2-ξ)) x ↔ ξ=0 ∧ φ x=0 := by
  have hsq : HasDerivAt (fun y => φ y^2-ξ) (2*φ x*deriv φ x) x := by
    simpa using (hφ.hasDerivAt.pow 2).sub_const ξ
  rw [gauge_critical_iff u _ x hu hsq.differentiableAt hu0]
  unfold CriticalZero
  rw [hsq.deriv]
  have ht : (2:K) ≠ 0 := by norm_num
  constructor
  · rintro ⟨hv,hd⟩
    have hz : φ x=0 := by
      rcases mul_eq_zero.mp hd with h | h
      · exact (mul_eq_zero.mp h).resolve_left ht
      · exact False.elim (hφ0 h)
    refine ⟨?_,hz⟩
    simpa [hz] using hv
  · rintro ⟨rfl,hz⟩
    simp [hz]

/-- Once a nonzero exact square scalar is known, all roots in the valid chart
are simple.  This theorem does not assume that the scalar is nonzero for Euler. -/
theorem square_chart_no_critical (u φ : K → K) (ξ x : K)
    (hu : DifferentiableAt K u x) (hφ : DifferentiableAt K φ x)
    (hu0 : u x ≠ 0) (hφ0 : deriv φ x ≠ 0) (hξ : ξ ≠ 0) :
    ¬ CriticalZero (fun y => u y*(φ y^2-ξ)) x := by
  rw [square_chart_critical_iff u φ ξ x hu hφ hu0 hφ0]
  exact fun h => hξ h.1

/-- A nonsquare derivative scalar excludes all critical points. -/
theorem derivative_square_nonsquare (f φ : K → K) (A u x : K)
    (hu : u ≠ 0)
    (hderiv : deriv f x = A+3*u*φ x^2)
    (hnonsquare : ¬ ∃ z : K, z^2 = -A/(3*u)) : deriv f x ≠ 0 := by
  intro hz
  apply hnonsquare
  refine ⟨φ x, ?_⟩
  have h3 : (3:K) ≠ 0 := by norm_num
  apply (eq_div_iff (mul_ne_zero h3 hu)).mpr
  have h := hderiv.symm.trans hz
  calc
    φ x^2*(3*u) = 3*u*φ x^2 := by ring
    _ = -A := eq_neg_of_add_eq_zero_right h

/-- For a cubic derivative square chart with zero scalar, a critical zero
must be the inflection center. -/
theorem cubic_zero_scalar_critical_iff (f φ : K → K) (u ρ x : K)
    (hu : u ≠ 0) (hchart : φ x=0 ↔ x=ρ)
    (hderiv : deriv f x=3*u*φ x^2) :
    CriticalZero f x ↔ x=ρ ∧ f ρ=0 := by
  have h3 : (3:K) ≠ 0 := by norm_num
  unfold CriticalZero
  rw [hderiv]
  constructor
  · rintro ⟨hf,hd⟩
    have hz : φ x^2=0 := (mul_eq_zero.mp hd).resolve_left (mul_ne_zero h3 hu)
    have hx : x=ρ := hchart.mp (eq_zero_of_pow_eq_zero hz)
    exact ⟨hx, hx ▸ hf⟩
  · rintro ⟨hx,hf⟩
    exact ⟨hx ▸ hf, by rw [hchart.mpr hx]; simp⟩

end
end Komorebi.Euler
