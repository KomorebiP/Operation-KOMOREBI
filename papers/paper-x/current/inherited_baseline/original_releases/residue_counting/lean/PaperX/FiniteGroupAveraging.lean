import PaperX.RepresentationClasses
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.RingTheory.LocalRing.ResidueField.Basic

/-! Explicit finite-group averaging lifts residual equivariant isomorphisms.
The order of the finite source group must be a unit. -/
set_option autoImplicit false

namespace PaperX.FiniteGroupAveraging
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open scoped BigOperators

variable {R S : Type*} [CommRing R] [CommRing S]
variable {Γ : Type*} [Group Γ] [Fintype Γ]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Reynolds averaging on the actual comparison matrix. -/
noncomputable def average (ρ τ : MatrixRep R Γ ι)
    (hΓ : IsUnit (Fintype.card Γ : R)) (A : Matrix ι ι R) : Matrix ι ι R :=
  (↑(hΓ.unit⁻¹) : R) • ∑ g : Γ, ρ g * A * τ g⁻¹

/-- Averaging constructs an intertwiner without requiring the original matrix
to intertwine. -/
theorem average_intertwines (ρ τ : MatrixRep R Γ ι)
    (hΓ : IsUnit (Fintype.card Γ : R)) (A : Matrix ι ι R) (h : Γ) :
    ρ h * average ρ τ hΓ A = average ρ τ hΓ A * τ h := by
  unfold average
  rw [Matrix.mul_smul, Matrix.smul_mul, Finset.mul_sum, Finset.sum_mul]
  congr 1
  refine Fintype.sum_bijective (h * ·) (Group.mulLeft_bijective h) _ _ fun g => ?_
  have hcancel : τ h⁻¹ * τ h = 1 := by rw [← map_mul, inv_mul_cancel, map_one]
  simp only [mul_inv_rev, map_mul, mul_assoc, hcancel, mul_one]

/-- If the reduction already intertwines, the average has exactly the same
reduction as the original matrix. -/
theorem map_average_of_intertwines (f : R →+* S) (ρ τ : MatrixRep R Γ ι)
    (hΓ : IsUnit (Fintype.card Γ : R)) (A : Matrix ι ι R)
    (hA : ∀ g, (ρ g).map f * A.map f = A.map f * (τ g).map f) :
    (average ρ τ hΓ A).map f = A.map f := by
  have hterm (g : Γ) : (ρ g * A * τ g⁻¹).map f = A.map f := by
    rw [Matrix.map_mul, Matrix.map_mul, hA, mul_assoc, ← Matrix.map_mul,
      ← map_mul, mul_inv_cancel, map_one, Matrix.map_one, mul_one] <;> simp
  have hsum : (∑ g : Γ, ρ g * A * τ g⁻¹).map f =
      (Fintype.card Γ : S) • A.map f := by
    change f.mapMatrix (∑ g : Γ, ρ g * A * τ g⁻¹) = _
    rw [map_sum]
    simp only [RingHom.mapMatrix_apply, hterm, Finset.sum_const, Finset.card_univ]
    exact_mod_cast (show Fintype.card Γ • A.map f = Fintype.card Γ • A.map f from rfl)
  have hsmul (r : R) (M : Matrix ι ι R) :
      (r • M).map f = f r • M.map f := by
    ext i j
    exact map_mul f r (M i j)
  unfold average
  rw [hsmul, hsum, smul_smul]
  have hinv : f (↑(hΓ.unit⁻¹) : R) * (Fintype.card Γ : S) = 1 := by
    simpa only [map_mul, hΓ.unit_spec, map_natCast, map_one] using
      congrArg f hΓ.unit.inv_mul
  rw [hinv, one_smul]

omit [Fintype ι] [DecidableEq ι] in
/-- Entrywise surjectivity supplies a matrix lift. -/
theorem exists_matrix_lift (f : R →+* S) (hf : Function.Surjective f)
    (B : Matrix ι ι S) : ∃ A : Matrix ι ι R, A.map f = B := by
  classical
  choose a ha using fun i j => hf (B i j)
  exact ⟨a, by ext i j; exact ha i j⟩

/-- A local homomorphism reflects matrix units through the determinant. -/
theorem matrix_isUnit_of_map (f : R →+* S) [IsLocalHom f]
    (A : Matrix ι ι R) (hA : IsUnit (A.map f)) : IsUnit A := by
  apply (Matrix.isUnit_iff_isUnit_det _).mpr
  apply isUnit_of_map_unit f
  rw [RingHom.map_det]
  exact (Matrix.isUnit_iff_isUnit_det _).mp hA

/-- An arbitrary residual equivariant matrix lifts to an actual integral
intertwiner with the same reduction. -/
theorem exists_intertwiner_lift (f : R →+* S) (hf : Function.Surjective f)
    (ρ τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (B : Matrix ι ι S)
    (hB : ∀ g, (ρ g).map f * B = B * (τ g).map f) :
    ∃ P : Matrix ι ι R, P.map f = B ∧ ∀ g, ρ g * P = P * τ g := by
  obtain ⟨A, hA⟩ := exists_matrix_lift f hf B
  refine ⟨average ρ τ hΓ A, ?_, average_intertwines ρ τ hΓ A⟩
  rw [map_average_of_intertwines f ρ τ hΓ A (by simpa only [hA] using hB), hA]

/-- A residual isomorphism lifts to an integral equivariant isomorphism whenever
the surjective coefficient map reflects units and the group order is a unit. -/
theorem exists_isomorphism_lift (f : R →+* S) (hf : Function.Surjective f)
    [IsLocalHom f] (ρ τ : MatrixRep R Γ ι)
    (hΓ : IsUnit (Fintype.card Γ : R)) (B : (Matrix ι ι S)ˣ)
    (hB : ∀ g, (ρ g).map f * (B : Matrix ι ι S) =
      (B : Matrix ι ι S) * (τ g).map f) :
    ∃ P : (Matrix ι ι R)ˣ, (P : Matrix ι ι R).map f = B ∧
      ∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g := by
  obtain ⟨P, hP, hρ⟩ := exists_intertwiner_lift f hf ρ τ hΓ B hB
  have hu : IsUnit P := matrix_isUnit_of_map f P (hP.symm ▸ B.isUnit)
  obtain ⟨u, hu⟩ := hu
  exact ⟨u, by simpa only [hu] using hP, by simpa only [hu] using hρ⟩

/-- For a finite group of unit order, reduction through a surjective local
homomorphism preserves and reflects the integral isomorphism class. -/
theorem conjugacy_iff_reduction (f : R →+* S) (hf : Function.Surjective f)
    [IsLocalHom f] (ρ τ : MatrixRep R Γ ι)
    (hΓ : IsUnit (Fintype.card Γ : R)) :
    Conjugate (changeCoefficients f τ) (changeCoefficients f ρ) ↔ Conjugate τ ρ := by
  constructor
  · rintro ⟨B, hB⟩
    have hinter (g : Γ) : (ρ g).map f * (B : Matrix ι ι S) =
        (B : Matrix ι ι S) * (τ g).map f := by
      change changeCoefficients f ρ g * (B : Matrix ι ι S) =
        (B : Matrix ι ι S) * changeCoefficients f τ g
      rw [← hB]
      simp only [conjugate_apply, mul_assoc, Units.inv_mul, mul_one]
    obtain ⟨P, _, hP⟩ := exists_isomorphism_lift f hf ρ τ hΓ B hinter
    refine ⟨P, MonoidHom.ext fun g => ?_⟩
    change (P : Matrix ι ι R) * τ g * (↑(P⁻¹) : Matrix ι ι R) = ρ g
    rw [← hP, mul_assoc]
    simp
  · exact changeCoefficients_conjugacy f

/-- In particular, residual isomorphism over the actual residue field of a
local coefficient ring is equivalent to integral isomorphism. -/
theorem conjugacy_iff_residue [IsLocalRing R] (ρ τ : MatrixRep R Γ ι)
    (hΓ : IsUnit (Fintype.card Γ : R)) :
    Conjugate (changeCoefficients (IsLocalRing.residue R) τ)
      (changeCoefficients (IsLocalRing.residue R) ρ) ↔ Conjugate τ ρ :=
  conjugacy_iff_reduction (IsLocalRing.residue R) IsLocalRing.residue_surjective ρ τ hΓ

/-- The lifted comparison retains any prescribed residual isomorphism, rather
than merely finding an unrelated change of basis. -/
theorem exists_residue_isomorphism_lift [IsLocalRing R]
    (ρ τ : MatrixRep R Γ ι) (hΓ : IsUnit (Fintype.card Γ : R))
    (B : (Matrix ι ι (IsLocalRing.ResidueField R))ˣ)
    (hB : ∀ g, (ρ g).map (IsLocalRing.residue R) * (B : Matrix ι ι _) =
      (B : Matrix ι ι _) * (τ g).map (IsLocalRing.residue R)) :
    ∃ P : (Matrix ι ι R)ˣ, (P : Matrix ι ι R).map (IsLocalRing.residue R) = B ∧
      ∀ g, ρ g * (P : Matrix ι ι R) = (P : Matrix ι ι R) * τ g :=
  exists_isomorphism_lift (IsLocalRing.residue R) IsLocalRing.residue_surjective ρ τ hΓ B hB

end PaperX.FiniteGroupAveraging
