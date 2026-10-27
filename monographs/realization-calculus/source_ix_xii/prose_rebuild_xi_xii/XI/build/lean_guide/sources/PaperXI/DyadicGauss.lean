import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic

/-! Dyadic quadratic refinements in explicit symplectic coordinates. -/
noncomputable section
set_option autoImplicit false
namespace PaperXI.Dyadic
open scoped BigOperators
abbrev F2 := ZMod 2

def sign (t : F2) : ℤ := if t = 0 then 1 else -1

@[simp] theorem sign_zero : sign 0 = 1 := by simp [sign]
@[simp] theorem sign_one : sign 1 = -1 := by norm_num [sign]

theorem sign_add (a b : F2) : sign (a + b) = sign a * sign b := by
  fin_cases a <;> fin_cases b <;> decide

theorem sign_injective : Function.Injective sign := by
  intro a b
  fin_cases a <;> fin_cases b <;> intro h
  · rfl
  · change (1 : ℤ) = -1 at h
    omega
  · change (-1 : ℤ) = 1 at h
    omega
  · rfl

theorem sign_sum {ι : Type*} (s : Finset ι) (f : ι → F2) :
    sign (∑ i ∈ s, f i) = ∏ i ∈ s, sign (f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert a s ha ih => simp [ha, sign_add, ih]

def plane (a x : F2 × F2) : F2 := x.1 * x.2 + a.1 * x.1 + a.2 * x.2

theorem plane_gauss (a : F2 × F2) :
    (∑ x : F2 × F2, sign (plane a x)) = sign (a.1 * a.2) * 2 := by
  rcases a with ⟨a, b⟩
  fin_cases a <;> fin_cases b <;> decide

open scoped Classical
variable {ι : Type*} [Fintype ι]

def quadratic (a x : ι → F2 × F2) : F2 := ∑ i, plane (a i) (x i)

def arf (a : ι → F2 × F2) : F2 := ∑ i, (a i).1 * (a i).2

theorem gauss_sum (a : ι → F2 × F2) :
    (∑ x, sign (quadratic a x)) = sign (arf a) * 2 ^ Fintype.card ι := by
  classical
  simp only [quadratic, sign_sum]
  rw [← Fintype.prod_sum (fun (i : ι) (x : F2 × F2) => sign (plane (a i) x))]
  simp_rw [plane_gauss]
  rw [Finset.prod_mul_distrib, ← sign_sum]
  simp [arf]

end PaperXI.Dyadic
