import PaperX.RepresentationClasses
import PaperX.RepresentationTopology
import PaperX.FiniteFiberBranches

/-!
A prescribed compatible branch of actual change-of-basis classes lifts to
exactly compatible matrices over finite quotient rings.  Completeness then
reconstructs a representation with exactly those reduction classes.  No lift
of a prescribed change-of-basis matrix is assumed.
-/
set_option autoImplicit false

namespace PaperX.ClassBranchLifting
open PaperX.Compactness PaperX.FiniteFiberBranches
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.RepresentationTopology

variable {R G ι : Type} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
variable (I : Ideal R)

/-- The tower contains actual quotient representations. -/
def matrixTower : Tower where
  Level k := MatrixRep (R ⧸ I ^ k) G ι
  parent k := transition I (Nat.le_succ k)

/-- The quotient tower contains their actual invertible-change-of-basis classes. -/
def classTower : Tower where
  Level k := ClassRep (R ⧸ I ^ k) G ι
  parent k := transitionClass I (Nat.le_succ k)

/-- Coefficient reduction commutes with passing to a conjugacy class. -/
def classTowerMap : TowerMap (matrixTower (G := G) (ι := ι) I)
    (classTower (G := G) (ι := ι) I) where
  map _ := classOf
  parent_commutes _ _ := rfl

/-- Finiteness of each coefficient quotient suffices to lift a fixed branch.
Finiteness of the source group or of all representation classes is not required. -/
theorem lift_class_branch
    (finiteR : ∀ k, Finite (R ⧸ I ^ k))
    (b : Branch (classTower (G := G) (ι := ι) I)) :
    ∃ a : Branch (matrixTower (G := G) (ι := ι) I),
      ∀ k, classOf (a.value k) = b.value k := by
  apply lift_branch (classTowerMap I) (fun _ => classOf_surjective)
  intro k c
  let : Finite (R ⧸ I ^ k) := finiteR k
  exact finite_class_fiber c

/-- Immediate compatibility of actual matrices implies compatibility between
every pair of precisions. -/
theorem matrix_branch_compatible
    (a : Branch (matrixTower (G := G) (ι := ι) I))
    {j k : ℕ} (h : j ≤ k) : transition I h (a.value k) = a.value j := by
  ext g i l
  apply (Ideal.Quotient.eq_factor_of_eq_factor_succ
    (fun _ _ h => Ideal.pow_le_pow_right h)
    (fun m => DFunLike.coe (F := MatrixRep (R ⧸ I ^ m) G ι) (a.value m) g i l) ?_ h).symm
  intro m
  exact (congrArg (fun (ρ : MatrixRep (R ⧸ I ^ m) G ι) => ρ g i l)
    (a.compatible m)).symm

/-- A strictly compatible matrix branch gives the existing reconstruction input. -/
def matrixBranchFamily (a : Branch (matrixTower (G := G) (ι := ι) I)) :
    Family R I G ι where
  maps := a.value
  compatible := matrix_branch_compatible I a

/-- Every prescribed compatible class branch has a fully compatible matrix
family above it. This theorem needs no completeness assumption. -/
theorem family_of_class_branch
    (finiteR : ∀ k, Finite (R ⧸ I ^ k))
    (b : Branch (classTower (G := G) (ι := ι) I)) :
    ∃ f : Family R I G ι, ∀ k, classOf (f.maps k) = b.value k := by
  obtain ⟨a, ha⟩ := lift_class_branch I finiteR b
  exact ⟨matrixBranchFamily I a, ha⟩

/-- The reconstructed integral representation has each prescribed finite class.
The theorem does not assert uniqueness up to integral conjugacy. -/
theorem realization_of_class_branch [IsAdicComplete I R]
    (finiteR : ∀ k, Finite (R ⧸ I ^ k))
    (b : Branch (classTower (G := G) (ι := ι) I)) :
    ∃ ρ : MatrixRep R G ι, ∀ k, classOf (reduce I ρ k) = b.value k := by
  obtain ⟨f, hf⟩ := family_of_class_branch I finiteR b
  refine ⟨reconstruct I f, ?_⟩
  intro k
  rw [reconstruct_reduces]
  exact hf k

/-- Actual continuous finite representatives give an actually adically continuous
integral representation. Continuity is explicitly required for the selected
classes and is not inferred from the finite coefficient rings alone. -/
theorem continuous_realization_of_class_branch [TopologicalSpace G]
    [IsAdicComplete I R]
    (finiteR : ∀ k, Finite (R ⧸ I ^ k))
    (b : Branch (classTower (G := G) (ι := ι) I))
    (continuous : ∀ k (ρ : MatrixRep (R ⧸ I ^ k) G ι),
      classOf ρ = b.value k → FiniteRepContinuous ρ) :
    ∃ ρ : MatrixRep R G ι,
      (∀ k, classOf (reduce I ρ k) = b.value k) ∧ AdicRepContinuous I ρ := by
  obtain ⟨f, hf⟩ := family_of_class_branch I finiteR b
  refine ⟨reconstruct I f, ?_, reconstructed_continuous I f ?_⟩
  · intro k
    rw [reconstruct_reduces]
    exact hf k
  · intro k
    exact continuous k (f.maps k) (hf k)

end PaperX.ClassBranchLifting
