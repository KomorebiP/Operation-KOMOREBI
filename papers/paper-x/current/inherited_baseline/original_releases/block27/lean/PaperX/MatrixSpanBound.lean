import PaperX.CertificateIsomorphisms
import PaperX.PrimitiveMatrix
import PaperX.IntegralActionSpan
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.Data.Matrix.Basis

/-! A full integral matrix span controls the denominator of a primitive
comparison uniformly across the representations compared with a fixed template. -/
set_option autoImplicit false
namespace PaperX.MatrixSpanBound
open PaperX.RepresentationLimits
variable {R G ι : Type*} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]

/-- Intertwining extends from the group action to its integral linear span. -/
theorem intertwining_on_span (ρ τ : MatrixRep R G ι) (P : Matrix ι ι R)
    (hP : ∀ g, ρ g * P = P * τ g)
    {A : Matrix ι ι R} (hA : A ∈ Submodule.span R (Set.range τ)) :
    ∃ C : Matrix ι ι R, C * P = P * A := by
  induction hA using Submodule.span_induction with
  | mem A hA =>
      obtain ⟨g, rfl⟩ := hA
      exact ⟨ρ g, hP g⟩
  | zero => exact ⟨0, by simp⟩
  | add A B _ _ hA hB =>
      obtain ⟨C, hC⟩ := hA
      obtain ⟨D, hD⟩ := hB
      exact ⟨C + D, by simp [add_mul, mul_add, hC, hD]⟩
  | smul a A _ hA =>
      obtain ⟨C, hC⟩ := hA
      exact ⟨a • C, by rw [Matrix.smul_mul, hC, Matrix.mul_smul]⟩

/-- A unit entry and a scalar-full matrix span give an integral left
comparison. This constructs the matrix rather than assuming a bounded inverse. -/
theorem factorization_of_unit_entry (ρ τ : MatrixRep R G ι)
    (P : Matrix ι ι R) (hP : ∀ g, ρ g * P = P * τ g)
    (a : R) (hspan : ∀ M : Matrix ι ι R,
      a • M ∈ Submodule.span R (Set.range τ))
    (i₀ j₀ : ι) (hu : IsUnit (P i₀ j₀)) :
    ∃ B : Matrix ι ι R, B * P = a • (1 : Matrix ι ι R) := by
  classical
  obtain ⟨u, hu⟩ := hu
  have hC : ∀ k : ι, ∃ C : Matrix ι ι R,
      C * P = P * (a • Matrix.single j₀ k 1) := fun k =>
    intertwining_on_span ρ τ P hP (hspan _)
  choose C hC using hC
  let B : Matrix ι ι R := fun k l => (↑(u⁻¹) : R) * C k i₀ l
  refine ⟨B, ?_⟩
  ext k l
  have hc := congrArg (fun M : Matrix ι ι R => M i₀ l) (hC k)
  have hb : (B * P) k l = (↑(u⁻¹) : R) * (C k * P) i₀ l := by
    change (∑ j, ((↑(u⁻¹) : R) * (C k) i₀ j) * P j l) =
      (↑(u⁻¹) : R) * ∑ j, (C k) i₀ j * P j l
    simp only [Finset.mul_sum, mul_assoc]
  rw [hb, hc, Matrix.mul_smul]
  by_cases hl : l = k
  · subst l
    simp [Matrix.mul_single_apply_same, ← hu, mul_assoc, mul_comm]
  · simp [Matrix.mul_single_apply_of_ne (1 : R) j₀ k i₀ l hl P, Ne.symm hl]

/-- Taking determinants gives the uniform divisibility bound. -/
theorem det_dvd_scalar_power (P B : Matrix ι ι R) (a : R)
    (h : B * P = a • (1 : Matrix ι ι R)) :
    P.det ∣ a ^ Fintype.card ι := by
  refine ⟨B.det, ?_⟩
  have hd := congrArg Matrix.det h
  simpa only [Matrix.det_mul, Matrix.det_smul, Matrix.det_one, mul_one, mul_comm] using hd.symm

/-- A primitive integral comparison has determinant dividing the scalar
matrix-span bound to the matrix rank. -/
theorem primitive_det_dvd (ρ τ : MatrixRep R G ι) (P : Matrix ι ι R)
    (hP : ∀ g, ρ g * P = P * τ g) (a : R)
    (hspan : ∀ M : Matrix ι ι R, a • M ∈ Submodule.span R (Set.range τ))
    (hunit : ∃ i j, IsUnit (P i j)) : P.det ∣ a ^ Fintype.card ι := by
  obtain ⟨i, j, hij⟩ := hunit
  obtain ⟨B, hB⟩ := factorization_of_unit_entry ρ τ P hP a hspan i j hij
  exact det_dvd_scalar_power P B a hB

section Detector
variable [IsDomain R]

/-- Dividing a fixed power gives nonvanishing one precision higher.
This implication needs only a nonzero nonunit, not the DVR hypothesis. -/
theorem nonzero_reduction_of_dvd_power (π x : R) (hπ : π ≠ 0)
    (hnunit : ¬ IsUnit π) (m : ℕ) (hdiv : x ∣ π ^ m) :
    Ideal.Quotient.mk ((Ideal.span {π}) ^ (m + 1)) x ≠ 0 := by
  intro hzero
  have hmem := Ideal.Quotient.eq_zero_iff_mem.mp hzero
  rw [Ideal.span_singleton_pow, Ideal.mem_span_singleton] at hmem
  obtain ⟨b, hb⟩ := hmem.trans hdiv
  have hc : (1 : R) = π * b :=
    mul_left_cancel₀ (pow_ne_zero m hπ) (by simpa [pow_succ, mul_assoc] using hb)
  exact hnunit (isUnit_iff_dvd_one.mpr ⟨b, hc⟩)

/-- A fixed scalar matrix-span exponent produces one determinant detector
for every primitive integral comparison with the template. -/
theorem primitive_comparison_detector (ρ τ : MatrixRep R G ι)
    (P : Matrix ι ι R) (hP : ∀ g, ρ g * P = P * τ g)
    (π : R) (hπ : π ≠ 0) (hnunit : ¬ IsUnit π) (c : ℕ)
    (hspan : ∀ M : Matrix ι ι R,
      π ^ c • M ∈ Submodule.span R (Set.range τ))
    (hunit : ∃ i j, IsUnit (P i j)) :
    (P.map (Ideal.Quotient.mk
      ((Ideal.span {π}) ^ (c * Fintype.card ι + 1)))).det ≠ 0 := by
  have hd : P.det ∣ π ^ (c * Fintype.card ι) := by
    simpa only [pow_mul] using primitive_det_dvd ρ τ P hP (π ^ c) hspan hunit
  have hz := nonzero_reduction_of_dvd_power π P.det hπ hnunit
    (c * Fintype.card ι) hd
  change ((Ideal.Quotient.mk
    ((Ideal.span {π}) ^ (c * Fintype.card ι + 1))).mapMatrix P).det ≠ 0
  rwa [← RingHom.map_det]

end Detector
section Uniform
variable [IsDomain R] [IsDiscreteValuationRing R]
variable {K : Type*} [Field K] [Algebra R K] [IsFractionRing R K]

/-- Starting from a nonzero field intertwiner, both primitive normalization
and the bounded determinant certificate are constructed. -/
theorem exists_bounded_comparison (ρ τ : MatrixRep R G ι)
    (π : R) (hπ : Irreducible π) (c : ℕ)
    (hspan : ∀ M : Matrix ι ι R,
      π ^ c • M ∈ Submodule.span R (Set.range τ))
    (Q : Matrix ι ι K) (hQ : Q ≠ 0)
    (hinter : ∀ g, (ρ g).map (algebraMap R K) * Q =
      Q * (τ g).map (algebraMap R K)) :
    ∃ P : Matrix ι ι R, (∀ g, ρ g * P = P * τ g) ∧
      (P.map (Ideal.Quotient.mk
        ((Ideal.span {π}) ^ (c * Fintype.card ι + 1)))).det ≠ 0 := by
  obtain ⟨s, P, _, _, hunit, hP⟩ :=
    PrimitiveMatrix.intertwiner_normalization (R := R) ρ τ Q hQ hinter
  refine ⟨P, hP, primitive_comparison_detector ρ τ P hP π
    hπ.ne_zero hπ.not_isUnit c hspan ?_⟩
  obtain ⟨i, j, hij⟩ := hunit
  exact ⟨i, j, by rw [hij]; exact isUnit_one⟩

/-- One depth works uniformly across all integral representations admitting
a nonzero field comparison with a fixed template whose field action spans
all matrices. The exponent is obtained from the template alone. -/
theorem exists_uniform_detector (τ : MatrixRep R G ι) (π : R)
    (hπ : Irreducible π)
    (hspan : Submodule.span K
      (Set.range (fun g => (τ g).map (algebraMap R K))) = ⊤) :
    ∃ c : ℕ, ∀ (ρ : MatrixRep R G ι) (Q : Matrix ι ι K), Q ≠ 0 →
      (∀ g, (ρ g).map (algebraMap R K) * Q =
        Q * (τ g).map (algebraMap R K)) →
      ∃ P : Matrix ι ι R, (∀ g, ρ g * P = P * τ g) ∧
        (P.map (Ideal.Quotient.mk
          ((Ideal.span {π}) ^ (c * Fintype.card ι + 1)))).det ≠ 0 := by
  obtain ⟨c, hc⟩ := IntegralActionSpan.exists_uniformizer_power_matrix_subset_span
    π hπ τ hspan
  exact ⟨c, fun ρ Q hQ hinter => exists_bounded_comparison ρ τ π hπ c hc Q hQ hinter⟩

open PaperX.RepresentationClasses in
/-- Every integral representation in the field-isomorphism class of a
fixed full-span template admits a comparison with one common detecting depth.
The empty-rank case is included. -/
theorem uniform_detector_for_conjugates (τ : MatrixRep R G ι) (π : R)
    (hπ : Irreducible π)
    (hspan : Submodule.span K
      (Set.range (fun g => (τ g).map (algebraMap R K))) = ⊤) :
    ∃ c : ℕ, ∀ ρ : MatrixRep R G ι,
      Conjugate (changeCoefficients (algebraMap R K) τ)
        (changeCoefficients (algebraMap R K) ρ) →
      ∃ P : Matrix ι ι R, (∀ g, ρ g * P = P * τ g) ∧
        (P.map (Ideal.Quotient.mk
          ((Ideal.span {π}) ^ (c * Fintype.card ι + 1)))).det ≠ 0 := by
  classical
  cases isEmpty_or_nonempty ι with
  | inl hempty =>
      let := hempty
      refine ⟨0, fun ρ _ => ⟨1, ?_, ?_⟩⟩
      · intro g
        ext i
        exact isEmptyElim i
      · change ((Ideal.Quotient.mk
          ((Ideal.span {π}) ^ (0 * Fintype.card ι + 1))).mapMatrix
          (1 : Matrix ι ι R)).det ≠ 0
        rw [← RingHom.map_det, Matrix.det_one]
        rw [Nat.zero_mul]
        exact nonzero_reduction_of_dvd_power π 1 hπ.ne_zero hπ.not_isUnit 0
          (by simp)
  | inr hnonempty =>
      let := hnonempty
      obtain ⟨c, hc⟩ := exists_uniform_detector τ π hπ hspan
      refine ⟨c, fun ρ hρ => ?_⟩
      obtain ⟨u, hu⟩ := hρ
      apply hc ρ (u : Matrix ι ι K) u.ne_zero
      intro g
      have he := congrArg (fun r : MatrixRep K G ι => r g) hu
      change (u : Matrix ι ι K) * (τ g).map (algebraMap R K) *
        (↑(u⁻¹) : Matrix ι ι K) = (ρ g).map (algebraMap R K) at he
      rw [← he, mul_assoc, mul_assoc]
      simp

end Uniform
end PaperX.MatrixSpanBound
