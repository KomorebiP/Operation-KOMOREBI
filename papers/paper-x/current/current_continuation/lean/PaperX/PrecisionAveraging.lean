import PaperX.FiniteGroupAveraging
import Mathlib.RingTheory.LocalRing.Quotient
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.Ring

/-! Finite-group averaging with a controlled loss of coefficient precision.
The group order may be a nonunit, but must be nonzero and divide a specified
power of the ideal generator.  Cancellation is performed in the integral domain,
without supplying a fraction-field comparison. -/
set_option autoImplicit false

namespace PaperX.PrecisionAveraging
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.FiniteGroupAveraging
open scoped BigOperators

variable {R : Type*} [CommRing R] [IsDomain R]
variable {Γ : Type*} [Group Γ] [Fintype Γ]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

omit [IsDomain R] in
/-- The unnormalized group sum is always an exact intertwiner. -/
theorem sum_intertwines (ρ τ : MatrixRep R Γ ι)
    (A : Matrix ι ι R) (h : Γ) :
    ρ h * (∑ g : Γ, ρ g * A * τ g⁻¹) =
      (∑ g : Γ, ρ g * A * τ g⁻¹) * τ h := by
  rw [Finset.mul_sum, Finset.sum_mul]
  refine Fintype.sum_bijective (h * ·) (Group.mulLeft_bijective h) _ _ fun g => ?_
  have hcancel : τ h⁻¹ * τ h = 1 := by rw [← map_mul, inv_mul_cancel, map_one]
  simp only [mul_inv_rev, map_mul, mul_assoc, hcancel, mul_one]

/-- An approximate intertwiner at depth `e+k` can be corrected to an exact
integral intertwiner while retaining its reduction at depth `k`. -/
theorem correct_intertwiner (π : R) (e k : ℕ)
    (ρ τ : MatrixRep R Γ ι) (hΓ : (Fintype.card Γ : R) ≠ 0)
    (hdiv : (Fintype.card Γ : R) ∣ π^e) (A : Matrix ι ι R)
    (hA : ∀ g, (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) *
        A.map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) =
      A.map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) *
        (τ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k)))) :
    ∃ P : Matrix ι ι R,
      P.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        A.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) ∧
      ∀ g, ρ g * P = P * τ g := by
  classical
  let I : Ideal R := Ideal.span {π}
  let f := Ideal.Quotient.mk (I^(e+k))
  let a : R := Fintype.card Γ
  let S : Matrix ι ι R := ∑ g : Γ, ρ g * A * τ g⁻¹
  have hterm (g : Γ) : (ρ g * A * τ g⁻¹).map f = A.map f := by
    rw [Matrix.map_mul, Matrix.map_mul, hA, mul_assoc, ← Matrix.map_mul,
      ← map_mul, mul_inv_cancel, map_one, Matrix.map_one, mul_one] <;> simp
  have hsum : S.map f = (a • A).map f := by
    change f.mapMatrix (∑ g : Γ, ρ g * A * τ g⁻¹) = _
    rw [map_sum]
    simp only [RingHom.mapMatrix_apply, hterm, Finset.sum_const, Finset.card_univ]
    ext i j
    simp [a, Matrix.map_apply, nsmul_eq_mul]
  have hentry (i j : ι) : π^(e+k) ∣ S i j - a * A i j := by
    rw [← Ideal.mem_span_singleton, ← Ideal.span_singleton_pow]
    apply (Ideal.Quotient.mk_eq_mk_iff_sub_mem _ _).mp
    exact congrArg (fun M => M i j) hsum
  choose E hE using hentry
  obtain ⟨b, hb⟩ := hdiv
  let P : Matrix ι ι R := fun i j => A i j + (b * π^k) * E i j
  have heq : a • P = S := by
    ext i j
    have H := hE i j
    change S i j - a * A i j = π^(e+k) * E i j at H
    change a * (A i j + (b * π^k) * E i j) = S i j
    rw [pow_add, hb] at H
    dsimp [a] at *
    linear_combination -H
  refine ⟨P, ?_, ?_⟩
  · ext i j
    apply (Ideal.Quotient.mk_eq_mk_iff_sub_mem _ _).mpr
    rw [Ideal.span_singleton_pow, Ideal.mem_span_singleton]
    refine ⟨b * E i j, ?_⟩
    change A i j + (b * π^k) * E i j - A i j = π^k * (b * E i j)
    ring
  · intro g
    have H := sum_intertwines ρ τ A g
    change ρ g * S = S * τ g at H
    rw [← heq, Matrix.mul_smul, Matrix.smul_mul] at H
    ext i j
    apply mul_left_cancel₀ hΓ
    exact congrArg (fun M => M i j) H


/-- A prescribed quotient intertwiner lifts after losing at most `e` powers
of the principal ideal.  The higher-depth quotient matrix need not itself admit
an exact lift with its entire original reduction. -/
theorem exists_intertwiner_lift (π : R) (e k : ℕ)
    (ρ τ : MatrixRep R Γ ι) (hΓ : (Fintype.card Γ : R) ≠ 0)
    (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (B : Matrix ι ι (R ⧸ (Ideal.span {π})^(e+k)))
    (hB : ∀ g, (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) * B =
      B * (τ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k)))) :
    ∃ P : Matrix ι ι R,
      P.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        B.map (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e)) ∧
      ∀ g, ρ g * P = P * τ g := by
  obtain ⟨A, hA⟩ := PaperX.FiniteGroupAveraging.exists_matrix_lift
    (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) Ideal.Quotient.mk_surjective B
  obtain ⟨P, hP, hρ⟩ := correct_intertwiner π e k ρ τ hΓ hdiv A
    (by simpa only [hA] using hB)
  refine ⟨P, hP.trans ?_, hρ⟩
  rw [← hA]
  ext i j
  simp

omit [IsDomain R] in
/-- Every positive quotient by a nonunit principal ideal has a unit-reflecting
quotient map over a local ring. -/
theorem positive_quotient_local [IsLocalRing R] (π : R)
    (hπ : ¬ IsUnit π) (k : ℕ) (hk : 0 < k) :
    IsLocalHom (Ideal.Quotient.mk ((Ideal.span {π})^k)) := by
  have hI : (Ideal.span {π} : Ideal R)^k ≠ ⊤ := by
    rw [Ideal.span_singleton_pow]
    intro h
    exact hπ ((isUnit_pow_iff hk.ne').mp (Ideal.span_singleton_eq_top.mp h))
  let : Nontrivial (R ⧸ (Ideal.span {π})^k) := Ideal.Quotient.nontrivial_iff.mpr hI
  exact IsLocalHom.of_surjective _ Ideal.Quotient.mk_surjective

/-- An invertible approximate comparison yields an integral isomorphism, with
its prescribed comparison retained at the lower positive precision. -/
theorem exists_isomorphism_lift [IsLocalRing R] (π : R) (e k : ℕ)
    (ρ τ : MatrixRep R Γ ι) (hΓ : (Fintype.card Γ : R) ≠ 0)
    (hdiv : (Fintype.card Γ : R) ∣ π^e) (hπ : ¬ IsUnit π) (hk : 0 < k)
    (B : (Matrix ι ι (R ⧸ (Ideal.span {π})^(e+k)))ˣ)
    (hB : ∀ g, (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) *
        (B : Matrix ι ι _) =
      (B : Matrix ι ι _) * (τ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k)))) :
    ∃ P : (Matrix ι ι R)ˣ,
      (P : Matrix ι ι R).map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        (B : Matrix ι ι _).map
          (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e)) ∧
      ∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g := by
  obtain ⟨P, hP, hρ⟩ := exists_intertwiner_lift π e k ρ τ hΓ hdiv B hB
  let f := Ideal.Quotient.mk ((Ideal.span {π})^k)
  let : IsLocalHom f := positive_quotient_local π hπ k hk
  have hu : IsUnit (P.map f) := by
    rw [hP]
    exact B.isUnit.map
      (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e)).mapMatrix
  obtain ⟨u, hu⟩ := matrix_isUnit_of_map f P hu
  exact ⟨u, by simpa only [hu] using hP, by simpa only [hu] using hρ⟩

/-- Finite precision `e+k` detects integral isomorphism for every positive `k`.
The comparison matrix constructed from the finite isomorphism agrees with it
at precision `k`, rather than necessarily at the entire input precision. -/
theorem conjugacy_iff_reduction [IsLocalRing R] (π : R) (e k : ℕ)
    (ρ τ : MatrixRep R Γ ι) (hΓ : (Fintype.card Γ : R) ≠ 0)
    (hdiv : (Fintype.card Γ : R) ∣ π^e) (hπ : ¬ IsUnit π) (hk : 0 < k) :
    Conjugate (reduce (Ideal.span {π}) τ (e+k))
      (reduce (Ideal.span {π}) ρ (e+k)) ↔ Conjugate τ ρ := by
  constructor
  · rintro ⟨B, hB⟩
    have hinter (g : Γ) :
        (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) *
            (B : Matrix ι ι _) =
          (B : Matrix ι ι _) *
            (τ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) := by
      change reduce (Ideal.span {π}) ρ (e+k) g * (B : Matrix ι ι _) =
        (B : Matrix ι ι _) * reduce (Ideal.span {π}) τ (e+k) g
      rw [← hB]
      simp only [conjugate_apply, mul_assoc, Units.inv_mul, mul_one]
    obtain ⟨P, _, hP⟩ := exists_isomorphism_lift π e k ρ τ hΓ hdiv hπ hk B hinter
    refine ⟨P, MonoidHom.ext fun g => ?_⟩
    change (P : Matrix ι ι R) * τ g * (↑(P⁻¹) : Matrix ι ι R) = ρ g
    rw [← hP, mul_assoc]
    simp
  · exact changeCoefficients_conjugacy (Ideal.Quotient.mk ((Ideal.span {π})^(e+k)))

end PaperX.PrecisionAveraging
