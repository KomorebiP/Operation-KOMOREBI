module
public import Euler.UndepletionAlgebra
public import Euler.DiscriminantReduction
@[expose] public section
noncomputable section
namespace Komorebi.Euler

section Field
variable {K : Type*} [Field K] [CharZero K]

/-- The degree-two perturbation model, not an Euler residual. -/
def quadraticJetModel (a b c d e y : K) : K :=
  a*y^2 + e*(b*y+c) + e^2*d

/-- Critical-point motion produces a second-order value term. -/
theorem quadraticJet_critical_value (a b c d e : K) (ha : a ≠ 0) :
    quadraticJetModel a b c d e (-e*b/(2*a)) =
      e*c + e^2*(d-b^2/(4*a)) := by
  unfold quadraticJetModel
  field_simp
  ring

/-- Coordinate-free version of the same second-order coefficient calculation. -/
theorem quadraticJet_drift_coefficient (a b d s : K) (ha : a ≠ 0)
    (hs : 2*a*s+b=0) :
    a*s^2+b*s+d=d-b^2/(4*a) := by
  have hx : s = -b/(2*a) := by
    apply (eq_div_iff (mul_ne_zero (by norm_num) ha)).mpr
    linear_combination hs
  rw [hx]
  field_simp
  ring

/-- Exact rational packets for a negative control of the unrestricted inference. -/
def spectralProbe1 (x : K) : K := (31/84:K)*(15*x^2-254*x+1001)
def spectralProbe2 (x : K) : K := -(127/84:K)*(3*x^2-62*x+245)
def spectralProbe (e x : K) : K :=
  1+spectralWeight e 4*spectralProbe1 x+spectralWeight e 16*spectralProbe2 x

lemma spectralProbe_at_zero (x : K) : spectralProbe 0 x=x^2 := by
  simp only [spectralProbe, spectralWeight_zero, one_mul]
  unfold spectralProbe1 spectralProbe2
  ring

lemma spectralProbe_at_eight (x : K) : spectralProbe 8 x=(x-8)^2 := by
  norm_num [spectralProbe, spectralWeight, spectralProbe1, spectralProbe2]
  ring

lemma spectralProbe_first_defect_value :
    (3:K)*spectralProbe1 0+15*spectralProbe2 0 = -4448 := by
  norm_num [spectralProbe1, spectralProbe2]

lemma spectralProbe_first_defect_nonzero :
    (3:K)*spectralProbe1 0+15*spectralProbe2 0 ≠ 0 := by
  rw [spectralProbe_first_defect_value]
  norm_num

end Field

section Analytic
variable {K : Type*} [NontriviallyNormedField K] [CharZero K]

omit [CharZero K] in
theorem quadraticJet_hasDerivAt (a b c d e y : K) :
    HasDerivAt (quadraticJetModel a b c d e) (2*a*y+e*b) y := by
  have hfun : quadraticJetModel a b c d e =
      (fun y => a*y^2+(e*b)*y+(e*c+e^2*d)) := by
    funext y
    unfold quadraticJetModel
    ring
  rw [hfun]
  exact quadratic_hasDerivAt a (e*b) (e*c+e^2*d) y

/-- A genuine derivative statement at the moving critical point of the jet model. -/
theorem quadraticJet_critical_derivative (a b c d e : K) (ha : a ≠ 0) :
    deriv (quadraticJetModel a b c d e) (-e*b/(2*a))=0 := by
  rw [(quadraticJet_hasDerivAt a b c d e _).deriv]
  field_simp
  ring

/-- The moved critical point is a multiple zero exactly when its computed value vanishes. -/
theorem quadraticJet_critical_iff (a b c d e : K) (ha : a ≠ 0) :
    CriticalZero (quadraticJetModel a b c d e) (-e*b/(2*a)) ↔
      e*c+e^2*(d-b^2/(4*a))=0 := by
  unfold CriticalZero
  rw [quadraticJet_critical_value a b c d e ha,
      quadraticJet_critical_derivative a b c d e ha]
  simp

omit [CharZero K] in
/-- A value/slope correction at a fixed point need not obstruct motion of a double root. -/
theorem translating_square_critical (e : K) :
    CriticalZero (fun x : K => (x-e)^2) e := by
  unfold CriticalZero
  constructor
  · simp
  · have hfun : (fun x : K => (x-e)^2) =
        (fun x => (1:K)*x^2+(-2*e)*x+e^2) := by
      funext x
      ring
    rw [hfun, (quadratic_hasDerivAt (1:K) (-2*e) (e^2) e).deriv]
    ring

/-- This actual resolvent-weighted SYNTHETIC family has double zeros at two parameter values. -/
theorem spectralProbe_critical_at_zero : CriticalZero (spectralProbe (0:K)) 0 := by
  have hf : spectralProbe (0:K)=(fun x : K => (x-0)^2) := by
    funext x
    simp [spectralProbe_at_zero]
  rw [hf]
  exact translating_square_critical 0

theorem spectralProbe_critical_at_eight : CriticalZero (spectralProbe (8:K)) 8 := by
  have hf : spectralProbe (8:K)=(fun x : K => (x-8)^2) := by
    funext x
    exact spectralProbe_at_eight x
  rw [hf]
  exact translating_square_critical 8

/-- Neither nonconstant packet in the negative control has a critical zero. -/
theorem spectralProbe1_no_critical (x : K) : ¬ CriticalZero spectralProbe1 x := by
  have hf : (spectralProbe1 : K → K)=
      (fun y => (155/28:K)*y^2+(-3937/42:K)*y+(31031/84:K)) := by
    funext y
    unfold spectralProbe1
    ring
  rw [hf, quadratic_analytic_critical_iff]
  intro hx
  have h := (quadratic_critical_exists_iff (155/28:K) (-3937/42) (31031/84)
    (by norm_num)).mp ⟨x,hx⟩
  norm_num at h

theorem spectralProbe2_no_critical (x : K) : ¬ CriticalZero spectralProbe2 x := by
  have hf : (spectralProbe2 : K → K)=
      (fun y => (-127/28:K)*y^2+(3937/42:K)*y+(-31115/84:K)) := by
    funext y
    unfold spectralProbe2
    ring
  rw [hf, quadratic_analytic_critical_iff]
  intro hx
  have h := (quadratic_critical_exists_iff (-127/28:K) (3937/42) (-31115/84)
    (by norm_num)).mp ⟨x,hx⟩
  norm_num at h

omit [CharZero K] in
/-- The necessary norm margin: a merely nonzero leading correction is insufficient. -/
theorem dominant_critical_value_nonzero (main remainder : K)
    (h : ‖remainder‖ < ‖main‖) : main+remainder ≠ 0 := by
  intro hz
  have heq : remainder = -main := eq_neg_of_add_eq_zero_right hz
  rw [heq, norm_neg] at h
  exact (lt_irrefl _ h)

omit [CharZero K] in
/-- Use this only after locating the actual perturbed critical point and bounding its value error. -/
theorem moved_value_certificate (f : K → K) (x e defect remainder : K)
    (hv : f x=e*defect+remainder)
    (hgap : ‖remainder‖ < ‖e*defect‖) : ¬ CriticalZero f x := by
  intro hcrit
  exact dominant_critical_value_nonzero (e*defect) remainder hgap
    (hv.symm.trans hcrit.1)
end Analytic
end Komorebi.Euler
