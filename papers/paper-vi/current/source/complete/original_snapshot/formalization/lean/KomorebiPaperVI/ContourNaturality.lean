import KomorebiPaperVI.Algebra
import Mathlib.MeasureTheory.Integral.CircleIntegral
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

/-! Author: Komorebi P. Actual finite contour integrals of matrix resolvents.
This module proves naturality for a supplied common contour representation. -/
namespace KomorebiPaperVI.ContourNaturality
open scoped BigOperators
open Complex
set_option backward.isDefEq.respectTransparency false
variable {I J K : Type*} [Fintype I] [Fintype J] [Fintype K] [DecidableEq I] [DecidableEq J]

noncomputable def resolvent (A : Matrix I I ℂ) (z : ℂ) : Matrix I I ℂ :=
  (Matrix.scalar I z-A)⁻¹

noncomputable def circleMatrix (F : ℂ → Matrix I J ℂ) (c : ℂ) (r : ℝ) : Matrix I J ℂ :=
  fun i j => ∮ z in C(c,r),F z i j

omit [DecidableEq I] [DecidableEq J] [Fintype J] [Fintype K] in
theorem circle_mul_left (C : Matrix K I ℂ) (F : ℂ → Matrix I J ℂ) (c : ℂ) (r : ℝ)
    (hF : ∀ i j,CircleIntegrable (fun z => F z i j) c r) :
    C*circleMatrix F c r=circleMatrix (fun z => C*F z) c r := by
  ext i j
  simp only [Matrix.mul_apply,circleMatrix]
  have hi (k : I) : CircleIntegrable (fun z => C i k*F z k j) c r := by
    convert! (hF k j).const_smul (a := C i k) using 1
  rw [circleIntegral.integral_fun_sum (fun k _ => hi k)]
  simp only [circleIntegral.integral_const_mul]

omit [DecidableEq I] [DecidableEq J] [Fintype I] [Fintype K] in
theorem circle_mul_right (C : Matrix J K ℂ) (F : ℂ → Matrix I J ℂ) (c : ℂ) (r : ℝ)
    (hF : ∀ i j,CircleIntegrable (fun z => F z i j) c r) :
    circleMatrix F c r*C=circleMatrix (fun z => F z*C) c r := by
  ext i j
  simp only [Matrix.mul_apply,circleMatrix]
  have hi (k : J) : CircleIntegrable (fun z => F z i k*C k j) c r := by
    have hc : CircleIntegrable (fun z => C k j*F z i k) c r := by
      convert! (hF i k).const_smul (a := C k j) using 1
    simpa only [mul_comm] using hc
  rw [circleIntegral.integral_fun_sum (fun k _ => hi k)]
  simp only [mul_comm,circleIntegral.integral_const_mul]

omit [Fintype K] in
theorem resolvent_intertwines (C : Matrix J I ℂ) (A : Matrix I I ℂ) (B : Matrix J J ℂ)
    (h : C*A=B*C) (z : ℂ) (hA : IsUnit (Matrix.scalar I z-A))
    (hB : IsUnit (Matrix.scalar J z-B)) : C*resolvent A z=resolvent B z*C := by
  have he := Algebra.rectangular_resolvent_identity C A B (resolvent A z) (resolvent B z) z
    (fun i j => mul_comm _ _)
    (Matrix.mul_nonsing_inv _ ((Matrix.isUnit_iff_isUnit_det _).mp hA))
    (Matrix.nonsing_inv_mul _ ((Matrix.isUnit_iff_isUnit_det _).mp hB))
  simpa only [h,sub_self,Matrix.mul_zero,Matrix.zero_mul,sub_eq_zero] using he

noncomputable def calculus (A : Matrix I I ℂ) (f : ℂ → ℂ) (c : K → ℂ) (r : K → ℝ) :
    Matrix I I ℂ := ((2*Real.pi:ℂ)*Complex.I)⁻¹ •
      ∑ k,circleMatrix (fun z => f z • resolvent A z) (c k) (r k)

theorem common_contour_naturality (C : Matrix J I ℂ) (A : Matrix I I ℂ) (B : Matrix J J ℂ)
    (h : C*A=B*C) (f : ℂ → ℂ) (c : K → ℂ) (r : K → ℝ) (hr : ∀ k,0 ≤ r k)
    (hA : ∀ k z,z∈Metric.sphere (c k) (r k) → IsUnit (Matrix.scalar I z-A))
    (hB : ∀ k z,z∈Metric.sphere (c k) (r k) → IsUnit (Matrix.scalar J z-B))
    (hiA : ∀ k i j,CircleIntegrable (fun z => f z*resolvent A z i j) (c k) (r k))
    (hiB : ∀ k i j,CircleIntegrable (fun z => f z*resolvent B z i j) (c k) (r k)) :
    C*calculus A f c r=calculus B f c r*C := by
  unfold calculus
  rw [Matrix.mul_smul,Matrix.smul_mul,Matrix.mul_sum,Matrix.sum_mul]
  congr 1
  apply Finset.sum_congr rfl
  intro k _
  have ha : ∀ i j,CircleIntegrable (fun z => (f z • resolvent A z) i j) (c k) (r k) := hiA k
  have hb : ∀ i j,CircleIntegrable (fun z => (f z • resolvent B z) i j) (c k) (r k) := hiB k
  rw [circle_mul_left C (fun z => f z • resolvent A z) _ _ ha,
    circle_mul_right C (fun z => f z • resolvent B z) _ _ hb]
  ext i j
  apply circleIntegral.integral_congr (hr k)
  intro z hz
  have he := resolvent_intertwines C A B h z (hA k z hz) (hB k z hz)
  change (C*(f z • resolvent A z)) i j=((f z • resolvent B z)*C) i j
  rw [Matrix.mul_smul,Matrix.smul_mul,he]

end KomorebiPaperVI.ContourNaturality
