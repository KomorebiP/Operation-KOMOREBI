module
public import Euler.CriticalCharts
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Tactic.LinearCombination
@[expose] public section
noncomputable section
namespace Komorebi.Euler

section Algebra
variable {K : Type*} [Field K] [CharZero K]

def QuadraticCritical (a b c x : K) : Prop :=
  a*x^2+b*x+c=0 ∧ 2*a*x+b=0

def CubicCritical (u A C x : K) : Prop :=
  u*x^3+A*x+C=0 ∧ 3*u*x^2+A=0

/-- The discriminant obstruction for a quadratic is necessary and sufficient
for a critical zero over the ground field, not merely its algebraic closure. -/
theorem quadratic_critical_exists_iff (a b c : K) (ha : a ≠ 0) :
    (∃ x : K, QuadraticCritical a b c x) ↔ b^2-4*a*c=0 := by
  constructor
  · rintro ⟨x,hv,hs⟩
    linear_combination (2*a*x+b)*hs-4*a*hv
  · intro hd
    refine ⟨-b/(2*a), ?_, ?_⟩
    · field_simp
      linear_combination -hd
    · field_simp
      ring

omit [CharZero K] in
/-- A depressed cubic can have a critical zero only on its exact discriminant
locus.  No valuation or finite-precision surrogate is used here. -/
theorem cubic_critical_discriminant (u A C x : K)
    (h : CubicCritical u A C x) : 4*A^3+27*u*C^2=0 := by
  rcases h with ⟨hv,hs⟩
  have ha : A = -3*u*x^2 := by linear_combination hs
  have hc : C = 2*u*x^3 := by rw [ha] at hv; linear_combination hv
  rw [ha,hc]
  ring

/-- In characteristic zero the discriminant-zero cubic always has a ground-field
critical zero.  When A is nonzero it is -3C/(2A); otherwise it is zero. -/
theorem cubic_critical_exists_iff (u A C : K) (hu : u ≠ 0) :
    (∃ x : K, CubicCritical u A C x) ↔ 4*A^3+27*u*C^2=0 := by
  constructor
  · rintro ⟨x,hx⟩
    exact cubic_critical_discriminant u A C x hx
  · intro hd
    by_cases ha : A=0
    · have hc : C=0 := by
        rw [ha] at hd
        have h27 : (27:K) ≠ 0 := by norm_num
        have hz : C^2=0 := by
          simpa only [zero_pow (by decide : 3 ≠ 0), mul_zero, zero_add,
            mul_eq_zero, h27, hu, false_or] using hd
        exact eq_zero_of_pow_eq_zero hz
      refine ⟨0, ?_, ?_⟩ <;> simp [ha,hc]
    · refine ⟨-3*C/(2*A), ?_, ?_⟩
      · field_simp
        linear_combination -C*hd
      · field_simp
        linear_combination hd

/-- Triple-jet vanishing of a cubic is strictly stronger than discriminant zero. -/
theorem cubic_triple_iff (u A C x : K) (hu : u ≠ 0) :
    (CubicCritical u A C x ∧ 3*u*x=0) ↔ x=0 ∧ A=0 ∧ C=0 := by
  have h3 : (3:K) ≠ 0 := by norm_num
  constructor
  · rintro ⟨⟨hv,hs⟩,h2⟩
    have hx : x=0 := (mul_eq_zero.mp h2).resolve_left (mul_ne_zero h3 hu)
    refine ⟨hx, ?_, ?_⟩
    · simpa [hx] using hs
    · simpa [hx] using hv
  · rintro ⟨rfl,rfl,rfl⟩
    simp [CubicCritical]
end Algebra

section Analytic
variable {K : Type*} [NontriviallyNormedField K]

lemma quadratic_hasDerivAt (a b c x : K) :
    HasDerivAt (fun y : K => a*y^2+b*y+c) (2*a*x+b) x := by
  simpa [mul_assoc, mul_left_comm, mul_comm] using
    ((((hasDerivAt_id x).pow 2).const_mul a).add
      ((hasDerivAt_id x).const_mul b)).add_const c

lemma cubic_hasDerivAt (u A C x : K) :
    HasDerivAt (fun y : K => u*y^3+A*y+C) (3*u*x^2+A) x := by
  simpa [mul_assoc, mul_left_comm, mul_comm] using
    ((((hasDerivAt_id x).pow 3).const_mul u).add
      ((hasDerivAt_id x).const_mul A)).add_const C

/-- Genuine analytic critical zeros of the quadratic, with no derivative
surrogate, are equivalent to the algebraic condition above. -/
theorem quadratic_analytic_critical_iff (a b c x : K) :
    CriticalZero (fun y => a*y^2+b*y+c) x ↔ QuadraticCritical a b c x := by
  unfold CriticalZero QuadraticCritical
  rw [(quadratic_hasDerivAt a b c x).deriv]

theorem cubic_analytic_critical_iff (u A C x : K) :
    CriticalZero (fun y => u*y^3+A*y+C) x ↔ CubicCritical u A C x := by
  unfold CriticalZero CubicCritical
  rw [(cubic_hasDerivAt u A C x).deriv]

/-- Exact criterion under an independently supplied differentiable cubic chart.
This does NOT manufacture that chart for the infinite Euler residual. -/
theorem cubic_chart_no_critical (g φ : K → K) (u A C x : K)
    (hg : DifferentiableAt K g x) (hφ : DifferentiableAt K φ x)
    (hg0 : g x ≠ 0) (hφ0 : deriv φ x ≠ 0)
    (hdisc : 4*A^3+27*u*C^2 ≠ 0) :
    ¬ CriticalZero (fun y => g y*(u*φ y^3+A*φ y+C)) x := by
  let p : K → K := fun y => u*y^3+A*y+C
  have hp := (cubic_hasDerivAt u A C (φ x)).differentiableAt
  change ¬ CriticalZero (fun y => g y*(p (φ y))) x
  have hcomp : DifferentiableAt K (fun y => p (φ y)) x := hp.comp x hφ
  rw [gauge_critical_iff g (fun y => p (φ y)) x hg hcomp hg0]
  rw [chart_critical_iff p φ x hp hφ hφ0]
  rw [cubic_analytic_critical_iff]
  intro h
  exact hdisc (cubic_critical_discriminant u A C (φ x) h)
end Analytic
end Komorebi.Euler
