import PaperX.CompletionExamples
import PaperX.RepresentationClasses

/-! Exact comparison matrices can lose every fixed determinant certificate as
their precision grows.  This is an algebraic boundary, not a Galois example. -/
set_option autoImplicit false
namespace PaperX.CertificateBoundary
open scoped Matrix
open PaperX.CompletionBoundary PaperX.RepresentationLimits PaperX.RepresentationClasses
variable {R : Type*} [CommRing R]

def nilpotent (a : R) : Matrix (Fin 2) (Fin 2) R := !![0,a;0,0]

def comparison (a : R) : Matrix (Fin 2) (Fin 2) R := !![a,0;0,1]

@[simp] theorem comparison_det (a : R) : (comparison a).det = a := by
  simp [comparison, Matrix.det_fin_two]

theorem comparison_intertwines (a : R) :
    nilpotent a * comparison a = comparison a * nilpotent 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [nilpotent, comparison, Matrix.mul_apply, Fin.sum_univ_succ]

theorem comparison_intertwines_representation (a : R) (g : Multiplicative ℤ) :
    unipotent a g * comparison a = comparison a * unipotent 1 g := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [unipotent, comparison, Matrix.mul_apply, Fin.sum_univ_succ]

@[simp] theorem changeCoefficients_unipotent {S : Type*} [CommRing S]
    (f : R →+* S) (a : R) : changeCoefficients f (unipotent a) = unipotent (f a) := by
  apply MonoidHom.ext
  intro g
  ext i j
  fin_cases i <;> fin_cases j <;> simp [changeCoefficients, unipotent]

@[simp] theorem map_comparison {S : Type*} [CommRing S] (f : R →+* S) (a : R) :
    (comparison a).map f = comparison (f a) := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [comparison]

/-- All integral intertwiners have the forced determinant, including matrices
other than the displayed diagonal comparison. -/
theorem intertwiner_det (a : R) (P : Matrix (Fin 2) (Fin 2) R)
    (h : nilpotent a * P = P * nilpotent 1) :
    P.det = a * (P 1 1)^2 := by
  have hc := congrArg (fun M : Matrix (Fin 2) (Fin 2) R => M 1 1) h
  have ha := congrArg (fun M : Matrix (Fin 2) (Fin 2) R => M 0 1) h
  simp [nilpotent, Matrix.mul_apply, Fin.sum_univ_succ] at hc ha
  rw [Matrix.det_fin_two, ← ha, ← hc]
  ring

theorem representation_intertwiner_det (a : R) (P : Matrix (Fin 2) (Fin 2) R)
    (h : ∀ g, unipotent a g * P = P * unipotent 1 g) :
    P.det = a * (P 1 1)^2 := by
  have H := h (Multiplicative.ofAdd (1 : ℤ))
  have hc := congrArg (fun M : Matrix (Fin 2) (Fin 2) R => M 1 1) H
  have ha := congrArg (fun M : Matrix (Fin 2) (Fin 2) R => M 0 1) H
  simp [unipotent, Matrix.mul_apply, Fin.sum_univ_succ] at hc ha
  have hc' : P 1 0 = 0 := hc
  have ha' : P 0 0 = a * P 1 1 := by linear_combination -ha
  rw [Matrix.det_fin_two, hc', ha']
  ring

/-- At every fixed precision, sufficiently deep approximants force every
integral comparison determinant to vanish, not just one chosen determinant. -/
theorem every_intertwiner_invisible (I : Ideal R) (π : R) (hπ : π ∈ I)
    (k n : ℕ) (hkn : k ≤ n) (P : Matrix (Fin 2) (Fin 2) R)
    (h : ∀ g, unipotent (π^n) g * P = P * unipotent 1 g) :
    Ideal.Quotient.mk (I^k) P.det = 0 := by
  rw [representation_intertwiner_det _ P h]
  apply Ideal.Quotient.eq_zero_iff_mem.mpr
  exact Ideal.mul_mem_right _ _ (Ideal.pow_le_pow_right hkn (Ideal.pow_mem_pow hπ n))

theorem no_uniform_detecting_depth (I : Ideal R) (π : R) (hπ : π ∈ I) :
    ¬ ∃ b : ℕ, ∀ n : ℕ, ∃ P : Matrix (Fin 2) (Fin 2) R,
      (∀ g, unipotent (π^n) g * P = P * unipotent 1 g) ∧
      Ideal.Quotient.mk (I^(b+1)) P.det ≠ 0 := by
  rintro ⟨b, hb⟩
  obtain ⟨P, hP, hdet⟩ := hb (b+1)
  exact hdet (every_intertwiner_invisible I π hπ (b+1) (b+1) le_rfl P hP)

theorem trivial_not_conjugate [Nontrivial R] :
    ¬ Conjugate (unipotent (1 : R)) (unipotent 0) := by
  intro h
  obtain ⟨u, hu⟩ := conjugate_symm h
  have H := congrArg
    (fun ρ : MatrixRep R (Multiplicative ℤ) (Fin 2) =>
      ρ (Multiplicative.ofAdd (1 : ℤ))) hu
  simp only [conjugate_apply, trivial_apply, mul_one, Units.mul_inv] at H
  have H01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) R => M 0 1) H
  simp [unipotent] at H01

section Field
variable {K : Type*} [Field K]

/-- Every nonzero parameter gives an actual invertible change of basis over
the field. This does not give a bounded integral comparison determinant. -/
theorem field_conjugate (a : K) (ha : a ≠ 0) :
    Conjugate (unipotent (1 : K)) (unipotent a) := by
  let u := Matrix.nonsingInvUnit (comparison a)
    (by simpa using (isUnit_iff_ne_zero.mpr ha : IsUnit a))
  refine ⟨u, ?_⟩
  apply MonoidHom.ext
  intro g
  change (u : Matrix (Fin 2) (Fin 2) K) * unipotent 1 g *
    (↑(u⁻¹) : Matrix (Fin 2) (Fin 2) K) = _
  have hu : (u : Matrix (Fin 2) (Fin 2) K) = comparison a := rfl
  rw [hu, ← comparison_intertwines_representation]
  rw [← hu, mul_assoc]
  simp

theorem every_nonzero_power_field_conjugate (π : K) (hπ : π ≠ 0) (n : ℕ) :
    Conjugate (unipotent (1 : K)) (unipotent (π^n)) :=
  field_conjugate _ (pow_ne_zero n hπ)

end Field
end PaperX.CertificateBoundary
