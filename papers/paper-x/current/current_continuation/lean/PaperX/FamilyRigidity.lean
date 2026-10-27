import PaperX.OrthogonalProjectors
import PaperX.PrecisionAveraging

/-! Complete labeled projector decompositions with the same positive reduction
are conjugate by an equivariant integral unit congruent to the identity.
The carrier group need not be finite and the coefficient ring need not be complete. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.FamilyRigidity
open PaperX.RepresentationLimits PaperX.MatrixProjector PaperX.OrthogonalProjectors
open scoped BigOperators

variable {R Γ ι J : Type*} [CommRing R] [Group Γ]
  [Fintype ι] [DecidableEq ι] [Fintype J]
variable {ρ : MatrixRep R Γ ι}

/-- The change of decomposition respects each label separately. -/
def comparison (E F : Family ρ J) : Matrix ι ι R :=
  ∑ i, (F.projector i).matrix * (E.projector i).matrix

theorem comparison_right (E F : Family ρ J) (j : J) :
    comparison E F * (E.projector j).matrix =
      (F.projector j).matrix * (E.projector j).matrix := by
  classical
  unfold comparison
  rw [Finset.sum_mul]
  simp only [mul_assoc, E.product]
  simp

theorem comparison_left (E F : Family ρ J) (j : J) :
    (F.projector j).matrix * comparison E F =
      (F.projector j).matrix * (E.projector j).matrix := by
  classical
  unfold comparison
  rw [Finset.mul_sum]
  simp only [← mul_assoc, F.product]
  simp

theorem comparison_intertwines (E F : Family ρ J) (j : J) :
    comparison E F * (E.projector j).matrix =
      (F.projector j).matrix * comparison E F :=
  (comparison_right E F j).trans (comparison_left E F j).symm

theorem comparison_commutes (E F : Family ρ J) (g : Γ) :
    ρ g * comparison E F = comparison E F * ρ g := by
  unfold comparison
  rw [Finset.mul_sum, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i _
  rw [← mul_assoc, (F.projector i).commutes, mul_assoc,
    (E.projector i).commutes, ← mul_assoc]

/-- Equal reductions of each labeled projector force the comparison to reduce
to the identity; equality of unlabeled sets is not the hypothesis. -/
theorem comparison_map {S : Type*} [CommRing S] (f : R →+* S)
    (E F : Family ρ J)
    (hEF : ∀ i, (E.projector i).matrix.map f = (F.projector i).matrix.map f) :
    (comparison E F).map f = 1 := by
  change f.mapMatrix (∑ i, (F.projector i).matrix * (E.projector i).matrix) = 1
  rw [map_sum]
  have hterm (i : J) :
      f.mapMatrix ((F.projector i).matrix * (E.projector i).matrix) =
        f.mapMatrix (F.projector i).matrix := by
    change ((F.projector i).matrix * (E.projector i).matrix).map f = _
    rw [Matrix.map_mul, hEF, ← Matrix.map_mul, (F.projector i).idempotent]
    rfl
  simp only [hterm]
  rw [← map_sum, F.total, map_one]

/-- A unit-reflecting coefficient map suffices for simultaneous rigidity. -/
theorem exists_conjugating_unit {S : Type*} [CommRing S] (f : R →+* S)
    [IsLocalHom f] (E F : Family ρ J)
    (hEF : ∀ i, (E.projector i).matrix.map f = (F.projector i).matrix.map f) :
    ∃ U : (Matrix ι ι R)ˣ,
      (U : Matrix ι ι R) = comparison E F ∧
      (U : Matrix ι ι R).map f = 1 ∧
      (∀ g, ρ g * (U : Matrix ι ι R) = (U : Matrix ι ι R) * ρ g) ∧
      (∀ j, (U : Matrix ι ι R) * (E.projector j).matrix *
        (↑(U⁻¹) : Matrix ι ι R) = (F.projector j).matrix) := by
  have hm := comparison_map f E F hEF
  have hu : IsUnit (comparison E F) :=
    PaperX.FiniteGroupAveraging.matrix_isUnit_of_map f _ (hm.symm ▸ isUnit_one)
  obtain ⟨U, hU⟩ := hu
  refine ⟨U, hU, by simpa only [hU] using hm, ?_, ?_⟩
  · intro g
    simpa only [hU] using comparison_commutes E F g
  · intro j
    have hj : (U : Matrix ι ι R) * (E.projector j).matrix =
        (F.projector j).matrix * (U : Matrix ι ι R) := by
      simpa only [hU] using comparison_intertwines E F j
    rw [hj, mul_assoc, Units.mul_inv, mul_one]

/-- Positive precision determines a complete labeled decomposition up to an
equivariant change of basis congruent to the identity at that same precision.
There is no extra loss depending on the number of projectors. -/
theorem exists_conjugating_unit_of_reduction [IsLocalRing R]
    (π : R) (hπ : ¬ IsUnit π) (k : ℕ) (hk : 0 < k)
    (E F : Family ρ J)
    (hEF : ∀ i,
      (E.projector i).matrix.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
      (F.projector i).matrix.map (Ideal.Quotient.mk ((Ideal.span {π})^k))) :
    ∃ U : (Matrix ι ι R)ˣ,
      (U : Matrix ι ι R) = comparison E F ∧
      (U : Matrix ι ι R).map (Ideal.Quotient.mk ((Ideal.span {π})^k)) = 1 ∧
      (∀ g, ρ g * (U : Matrix ι ι R) = (U : Matrix ι ι R) * ρ g) ∧
      (∀ j, (U : Matrix ι ι R) * (E.projector j).matrix *
        (↑(U⁻¹) : Matrix ι ι R) = (F.projector j).matrix) := by
  let := PaperX.PrecisionAveraging.positive_quotient_local π hπ k hk
  exact exists_conjugating_unit _ E F hEF

/-- A projector intertwiner maps the actual image into the corresponding image. -/
theorem mulVec_mem_image (E F : Projector ρ) (A : Matrix ι ι R)
    (hA : A * E.matrix = F.matrix * A) (v : E.image.toSubmodule) :
    A.mulVec (v : ι → R) ∈ F.image.toSubmodule := by
  rw [F.image_iff, Matrix.mulVec_mulVec, ← hA, ← Matrix.mulVec_mulVec,
    (E.image_iff _).mp v.property]

theorem inverse_intertwines (E F : Projector ρ) (U : (Matrix ι ι R)ˣ)
    (hU : (U : Matrix ι ι R) * E.matrix = F.matrix * (U : Matrix ι ι R)) :
    (↑(U⁻¹) : Matrix ι ι R) * F.matrix =
      E.matrix * (↑(U⁻¹) : Matrix ι ι R) := by
  calc
    (↑(U⁻¹) : Matrix ι ι R) * F.matrix =
        (↑(U⁻¹) : Matrix ι ι R) * (F.matrix * (U : Matrix ι ι R)) *
          (↑(U⁻¹) : Matrix ι ι R) := by simp [mul_assoc]
    _ = (↑(U⁻¹) : Matrix ι ι R) * ((U : Matrix ι ι R) * E.matrix) *
          (↑(U⁻¹) : Matrix ι ι R) := by rw [hU]
    _ = E.matrix * (↑(U⁻¹) : Matrix ι ι R) := by simp [← mul_assoc]

/-- Simultaneous conjugacy restricts to actual linear isomorphisms of images. -/
def imageEquiv (E F : Projector ρ) (U : (Matrix ι ι R)ˣ)
    (hU : (U : Matrix ι ι R) * E.matrix = F.matrix * (U : Matrix ι ι R)) :
    E.image.toSubmodule ≃ₗ[R] F.image.toSubmodule where
  toFun v := ⟨(U : Matrix ι ι R).mulVec v, mulVec_mem_image E F U hU v⟩
  invFun v := ⟨(↑(U⁻¹) : Matrix ι ι R).mulVec v,
    mulVec_mem_image F E (↑(U⁻¹)) (inverse_intertwines E F U hU) v⟩
  left_inv v := by
    apply Subtype.ext
    change (↑(U⁻¹) : Matrix ι ι R).mulVec ((U : Matrix ι ι R).mulVec v) = v
    rw [Matrix.mulVec_mulVec, Units.inv_mul, Matrix.one_mulVec]
  right_inv v := by
    apply Subtype.ext
    change (U : Matrix ι ι R).mulVec ((↑(U⁻¹) : Matrix ι ι R).mulVec v) = v
    rw [Matrix.mulVec_mulVec, Units.mul_inv, Matrix.one_mulVec]
  map_add' v w := by
    apply Subtype.ext
    exact Matrix.mulVec_add _ _ _
  map_smul' a v := by
    apply Subtype.ext
    exact Matrix.mulVec_smul _ _ _

theorem imageEquiv_apply (E F : Projector ρ) (U : (Matrix ι ι R)ˣ)
    (hU : (U : Matrix ι ι R) * E.matrix = F.matrix * (U : Matrix ι ι R))
    (v : E.image.toSubmodule) :
    (imageEquiv E F U hU v : ι → R) = (U : Matrix ι ι R).mulVec v := rfl

/-- The image isomorphism respects the inherited carrier representation. -/
theorem imageEquiv_equivariant (E F : Projector ρ) (U : (Matrix ι ι R)ˣ)
    (hU : (U : Matrix ι ι R) * E.matrix = F.matrix * (U : Matrix ι ι R))
    (hρ : ∀ g, ρ g * (U : Matrix ι ι R) = (U : Matrix ι ι R) * ρ g)
    (g : Γ) (v : E.image.toSubmodule) :
    imageEquiv E F U hU (E.image.toRepresentation g v) =
      F.image.toRepresentation g (imageEquiv E F U hU v) := by
  apply Subtype.ext
  change (U : Matrix ι ι R).mulVec ((ρ g).mulVec (v : ι → R)) =
    (ρ g).mulVec ((U : Matrix ι ι R).mulVec (v : ι → R))
  rw [Matrix.mulVec_mulVec, Matrix.mulVec_mulVec, hρ]

end PaperX.FamilyRigidity
