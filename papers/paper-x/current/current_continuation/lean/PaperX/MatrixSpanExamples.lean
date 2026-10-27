import PaperX.MatrixSpanBound
import PaperX.CertificateExamples
import Mathlib.GroupTheory.FreeGroup.Basic

/-! A full-span 3-adic template with a genuine nonunit comparison.
The uniform theorem applies to every integral representation in its rational
isomorphism class, rather than just the displayed pair. -/
set_option autoImplicit false
namespace PaperX.MatrixSpanExamples
open scoped Matrix
open PaperX.RepresentationLimits PaperX.RepresentationClasses
variable {R : Type*} [CommRing R]

def upper (a : R) : Matrix (Fin 2) (Fin 2) R := !![1, a; 0, 1]
def lower (a : R) : Matrix (Fin 2) (Fin 2) R := !![1, 0; a, 1]

def upperUnit (a : R) : (Matrix (Fin 2) (Fin 2) R)ˣ where
  val := upper a
  inv := upper (-a)
  val_inv := by ext i j; fin_cases i <;> fin_cases j <;>
    simp [upper, Matrix.mul_apply, Fin.sum_univ_two]
  inv_val := by ext i j; fin_cases i <;> fin_cases j <;>
    simp [upper, Matrix.mul_apply, Fin.sum_univ_two]

def lowerUnit (a : R) : (Matrix (Fin 2) (Fin 2) R)ˣ where
  val := lower a
  inv := lower (-a)
  val_inv := by ext i j; fin_cases i <;> fin_cases j <;>
    simp [lower, Matrix.mul_apply, Fin.sum_univ_two]
  inv_val := by ext i j; fin_cases i <;> fin_cases j <;>
    simp [lower, Matrix.mul_apply, Fin.sum_univ_two]

def pairRep (a b : R) : MatrixRep R (FreeGroup (Fin 2)) (Fin 2) :=
  (Units.coeHom _).comp (FreeGroup.lift fun i : Fin 2 =>
    if i = 0 then upperUnit a else lowerUnit b)

@[simp] theorem pairRep_zero (a b : R) :
    pairRep a b (FreeGroup.of 0) = upper a := by
  simp [pairRep, upperUnit]

@[simp] theorem pairRep_one (a b : R) :
    pairRep a b (FreeGroup.of 1) = lower b := by
  simp [pairRep, lowerUnit]

/-- The integral action span contains a times every matrix, proved directly
from the two generators and their product. -/
theorem scalar_matrix_mem_span (a : R) (M : Matrix (Fin 2) (Fin 2) R) :
    a • M ∈ Submodule.span R (Set.range (pairRep a 1)) := by
  let S := Submodule.span R (Set.range (pairRep a 1))
  have hU : upper a ∈ S := by
    apply Submodule.subset_span
    exact ⟨FreeGroup.of 0, pairRep_zero a 1⟩
  have hL : lower (1 : R) ∈ S := by
    apply Submodule.subset_span
    exact ⟨FreeGroup.of 1, pairRep_one a 1⟩
  have hI : (1 : Matrix (Fin 2) (Fin 2) R) ∈ S := by
    apply Submodule.subset_span
    exact ⟨1, map_one _⟩
  have hUL : upper a * lower 1 ∈ S := by
    apply Submodule.subset_span
    exact ⟨FreeGroup.of 0 * FreeGroup.of 1, by simp⟩
  have h00 := S.add_mem (S.sub_mem (S.sub_mem hUL hU) hL) hI
  have h01 := S.sub_mem hU hI
  have h10 := S.sub_mem hL hI
  have h11 := S.sub_mem (S.smul_mem a hI) h00
  have hm : a • M =
      M 0 0 • (upper a * lower 1 - upper a - lower 1 + 1) +
      M 0 1 • (upper a - 1) + (a * M 1 0) • (lower 1 - 1) +
      M 1 1 • (a • (1 : Matrix (Fin 2) (Fin 2) R) -
        (upper a * lower 1 - upper a - lower 1 + 1)) := by
    ext i j
    fin_cases i <;> fin_cases j <;>
      simp [upper, lower] <;> ring
  rw [hm]
  exact S.add_mem (S.add_mem (S.add_mem (S.smul_mem _ h00) (S.smul_mem _ h01))
    (S.smul_mem _ h10)) (S.smul_mem _ h11)

@[simp] theorem changeCoefficients_pairRep {S : Type*} [CommRing S]
    (f : R →+* S) (a b : R) :
    changeCoefficients f (pairRep a b) = pairRep (f a) (f b) := by
  apply FreeGroup.ext_hom
  intro i
  fin_cases i <;> ext j k <;> fin_cases j <;> fin_cases k <;>
    simp [upper, lower]

/-- Over a field, the same explicit matrices span the complete matrix algebra. -/
theorem field_span_eq_top {K : Type*} [Field K] (a : K) (ha : a ≠ 0) :
    Submodule.span K (Set.range (pairRep a 1)) = ⊤ := by
  apply top_unique
  intro M _
  have h := (Submodule.span K (Set.range (pairRep a 1))).smul_mem a⁻¹
    (scalar_matrix_mem_span a M)
  simpa [smul_smul, ha] using h

def comparison (a : R) : Matrix (Fin 2) (Fin 2) R := !![1, 0; 0, a]

@[simp] theorem comparison_det (a : R) : (comparison a).det = a := by
  simp [comparison, Matrix.det_fin_two]

/-- The two actual representations are intertwined for every free-group word. -/
theorem comparison_intertwines (a : R) (g : FreeGroup (Fin 2)) :
    pairRep 1 a g * comparison a = comparison a * pairRep a 1 g := by
  induction g using FreeGroup.induction_on with
  | one => simp
  | of i =>
      fin_cases i <;> ext j k <;> fin_cases j <;> fin_cases k <;>
        simp [upper, lower, comparison]
  | inv_of i hi =>
      let x := FreeGroup.of i
      change pairRep 1 a x⁻¹ * comparison a = comparison a * pairRep a 1 x⁻¹
      calc
        pairRep 1 a x⁻¹ * comparison a =
            pairRep 1 a x⁻¹ * comparison a * (pairRep a 1 x * pairRep a 1 x⁻¹) := by
          rw [← map_mul, mul_inv_cancel, map_one, mul_one]
        _ = pairRep 1 a x⁻¹ * (comparison a * pairRep a 1 x) * pairRep a 1 x⁻¹ := by
          simp only [mul_assoc]
        _ = pairRep 1 a x⁻¹ * (pairRep 1 a x * comparison a) * pairRep a 1 x⁻¹ := by
          rw [← hi]
        _ = comparison a * pairRep a 1 x⁻¹ := by
          rw [← mul_assoc, ← map_mul, inv_mul_cancel, map_one, one_mul]
  | mul x y hx hy =>
      simp only [map_mul]
      calc
        pairRep 1 a x * pairRep 1 a y * comparison a =
          pairRep 1 a x * (comparison a * pairRep a 1 y) := by rw [mul_assoc, hy]
        _ = comparison a * (pairRep a 1 x * pairRep a 1 y) := by rw [← mul_assoc, hx, mul_assoc]

noncomputable def tau : MatrixRep ℤ_[3] (FreeGroup (Fin 2)) (Fin 2) := pairRep 3 1
noncomputable def rho : MatrixRep ℤ_[3] (FreeGroup (Fin 2)) (Fin 2) := pairRep 1 3

/-- The actual 3-adic template has integral matrix-span exponent one. -/
theorem three_adic_span (M : Matrix (Fin 2) (Fin 2) ℤ_[3]) :
    (3 : ℤ_[3]) • M ∈ Submodule.span ℤ_[3] (Set.range tau) :=
  scalar_matrix_mem_span 3 M

/-- The field span is verified from the actual generator matrices. -/
theorem three_adic_full_field_span :
    Submodule.span ℚ_[3]
      (Set.range (fun g => (tau g).map (algebraMap ℤ_[3] ℚ_[3]))) = ⊤ := by
  have he : (fun g => (tau g).map (algebraMap ℤ_[3] ℚ_[3])) =
      (pairRep (3 : ℚ_[3]) 1 : FreeGroup (Fin 2) → Matrix (Fin 2) (Fin 2) ℚ_[3]) := by
    funext g
    change changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) (pairRep 3 1) g = _
    rw [changeCoefficients_pairRep, map_ofNat, map_one]
  rw [he]
  exact field_span_eq_top 3 (by norm_num)

/-- The displayed comparison is nonsingular over Q_3. -/
theorem three_adic_field_conjugate :
    Conjugate (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) tau)
      (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) rho) := by
  obtain ⟨u, _, hu⟩ := PaperX.CertificateIsomorphisms.exists_conjugating_unit
    (algebraMap ℤ_[3] ℚ_[3]) (IsFractionRing.injective ℤ_[3] ℚ_[3])
    rho tau (comparison 3) (by rw [comparison_det]; norm_num)
    (comparison_intertwines 3)
  exact ⟨u, hu⟩

/-- One explicit depth works for the entire rational isomorphism class. -/
theorem every_conjugate_has_depth_three (σ : MatrixRep ℤ_[3] (FreeGroup (Fin 2)) (Fin 2))
    (hσ : Conjugate (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) tau)
      (changeCoefficients (algebraMap ℤ_[3] ℚ_[3]) σ)) :
    ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[3], (∀ g, σ g * P = P * tau g) ∧
      (P.map (Ideal.Quotient.mk ((Ideal.span {(3 : ℤ_[3])}) ^ 3))).det ≠ 0 := by
  obtain ⟨u, hu⟩ := hσ
  have hi : ∀ g, (σ g).map (algebraMap ℤ_[3] ℚ_[3]) * (u : Matrix (Fin 2) (Fin 2) ℚ_[3]) =
      (u : Matrix (Fin 2) (Fin 2) ℚ_[3]) * (tau g).map (algebraMap ℤ_[3] ℚ_[3]) := by
    intro g
    have he := congrArg (fun r : MatrixRep ℚ_[3] (FreeGroup (Fin 2)) (Fin 2) => r g) hu
    change (u : Matrix (Fin 2) (Fin 2) ℚ_[3]) * (tau g).map (algebraMap ℤ_[3] ℚ_[3]) *
      (↑(u⁻¹) : Matrix (Fin 2) (Fin 2) ℚ_[3]) = (σ g).map (algebraMap ℤ_[3] ℚ_[3]) at he
    rw [← he, mul_assoc, mul_assoc]
    simp
  have hh := PaperX.MatrixSpanBound.exists_bounded_comparison σ tau 3
    (PadicInt.irreducible_p (p := 3)) 1 (by simpa using three_adic_span)
    (u : Matrix (Fin 2) (Fin 2) ℚ_[3]) u.ne_zero hi
  exact hh

/-- The exhibited comparison is an integral nonunit. -/
theorem displayed_comparison_not_unit : ¬ IsUnit (comparison (3 : ℤ_[3])) := by
  intro h
  have hd := (Matrix.isUnit_iff_isUnit_det _).mp h
  rw [comparison_det] at hd
  exact (PadicInt.irreducible_p (p := 3)).not_isUnit hd

/-- No alternative integral change of basis exists: the first named generator
is trivial modulo three for tau and nontrivial modulo three for rho. -/
theorem not_integrally_conjugate : ¬ Conjugate tau rho := by
  intro hc
  obtain ⟨u, hu⟩ := changeCoefficients_conjugacy
    (PadicInt.toZMod : ℤ_[3] →+* ZMod 3) hc
  have hτ : changeCoefficients (PadicInt.toZMod : ℤ_[3] →+* ZMod 3)
      tau (FreeGroup.of 0) = 1 := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [tau, upper]
    rw [map_ofNat]
    decide +kernel
  have hρ : changeCoefficients (PadicInt.toZMod : ℤ_[3] →+* ZMod 3)
      rho (FreeGroup.of 0) 0 1 = 1 := by simp [rho, upper]
  have he := congrArg (fun σ : MatrixRep (ZMod 3) (FreeGroup (Fin 2)) (Fin 2) =>
    σ (FreeGroup.of 0)) hu
  rw [conjugate_apply, hτ, mul_one] at he
  simp only [Units.mul_inv] at he
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod 3) => M 0 1) he
  rw [hρ] at h01
  simp at h01

/-- A direct invocation of the uniform theorem for the displayed nonintegrally
conjugate pair. -/
theorem actual_nonunit_class_has_certificate :
    ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[3], (∀ g, rho g * P = P * tau g) ∧
      (P.map (Ideal.Quotient.mk ((Ideal.span {(3 : ℤ_[3])}) ^ 3))).det ≠ 0 :=
  every_conjugate_has_depth_three rho three_adic_field_conjugate

end PaperX.MatrixSpanExamples
