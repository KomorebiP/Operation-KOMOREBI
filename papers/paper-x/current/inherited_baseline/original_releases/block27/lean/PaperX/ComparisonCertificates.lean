import PaperX.MatrixWitnessLimits
import PaperX.RepresentationForests
import PaperX.FiniteFiberBranches

/-! Finite local intertwining certificates are selected together with the global
representation. A fixed detecting depth prevents the comparison determinants
from tending to zero. No compatible choices of witnesses are assumed. -/
set_option autoImplicit false
namespace PaperX.ComparisonCertificates
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationForests
variable {R G ι S : Type} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
variable (I : Ideal R) (C : Conditions (G := G) (ι := ι) I)
variable {H : S → Type} [∀ s, Group (H s)]
variable (φ : ∀ s, H s →* G) (τ : ∀ s, MatrixRep R (H s) ι) (d : S → ℕ)

/-- The determinant test is imposed only once the fixed detecting precision is
available. In particular, precision zero is not required to contain a nonzero scalar. -/
structure Node (k : ℕ) where
  rep : MatrixRep (R ⧸ I^k) G ι
  allowed : C.allowed k rep
  comparison : ∀ _s : S, Matrix ι ι (R ⧸ I^k)
  intertwines : ∀ s g, rep (φ s g) * comparison s = comparison s * (reduce I (τ s) k) g
  detected : ∀ s (h : d s ≤ k), Ideal.Quotient.factorPow I h (comparison s).det ≠ 0

/-- The full certificate reduces, including its determinant test at the same
fixed depth. This is a total parent map, not a surjectivity assumption. -/
def nodeTransition {j k : ℕ} (h : j ≤ k) (x : Node I C φ τ d k) :
    Node I C φ τ d j where
  rep := transition I h x.rep
  allowed := C.downward h x.rep x.allowed
  comparison s := (x.comparison s).map (Ideal.Quotient.factorPow I h)
  intertwines s g := by
    have hx := congrArg (fun A => A.map (Ideal.Quotient.factorPow I h)) (x.intertwines s g)
    rw [Matrix.map_mul, Matrix.map_mul] at hx
    have hτ := congrArg (fun ρ => ρ g) (transition_reduce I (τ s) h)
    change ((reduce I (τ s) k) g).map (Ideal.Quotient.factorPow I h) = _ at hτ
    rw [hτ] at hx
    exact hx
  detected s hs := by
    change Ideal.Quotient.factorPow I hs
      ((Ideal.Quotient.factorPow I h).mapMatrix (x.comparison s)).det ≠ 0
    rw [← (Ideal.Quotient.factorPow I h).map_det]
    simpa only [Ideal.Quotient.factor_comp_apply] using x.detected s (hs.trans h)

/-- Both representations and their comparison matrices belong to the branch. -/
def certificateTower : PaperX.Compactness.Tower where
  Level k := Node I C φ τ d k
  parent k := nodeTransition I C φ τ d (Nat.le_succ k)

/-- Coefficient finiteness controls witnesses, whereas finiteness of the actual
allowed representation set is a separate premise. The group need not be finite. -/
theorem node_finite [Finite S] (k : ℕ) [Finite (R ⧸ I^k)]
    [Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ}] :
    Finite (Node I C φ τ d k) := by
  let f : Node I C φ τ d k →
      {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ} × (S → Matrix ι ι (R ⧸ I^k)) :=
    fun x => (⟨x.rep, x.allowed⟩, x.comparison)
  apply Finite.of_injective f
  intro x y h
  have hrep : x.rep = y.rep := congrArg (fun z => z.1.val) h
  have hmat : x.comparison = y.comparison := congrArg Prod.snd h
  cases x
  cases y
  cases hrep
  cases hmat
  rfl

/-- Compactness makes simultaneous coherent choices from separately occupied
augmented levels. No coherent sequence of comparison matrices is an input. -/
theorem exists_certificate_branch [Finite S]
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (finiteC : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ})
    (occupied : ∀ k, Nonempty (Node I C φ τ d k)) :
    Nonempty (PaperX.Compactness.Branch (certificateTower I C φ τ d)) := by
  apply PaperX.Compactness.finite_branch_compactness
  · apply PaperX.FiniteFiberBranches.finite_levels
    intro k
    let : Finite (R ⧸ I^k) := finiteR k
    let : Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ} := finiteC k
    exact node_finite I C φ τ d k
  · exact occupied

/-- Adjacent compatibility gives compatibility at every pair of precisions. -/
theorem branch_rep_compatible
    (b : PaperX.Compactness.Branch (certificateTower I C φ τ d))
    {j k : ℕ} (h : j ≤ k) :
    transition I h (b.value k).rep = (b.value j).rep := by
  ext g a c
  apply (Ideal.Quotient.eq_factor_of_eq_factor_succ
    (fun _ _ h => Ideal.pow_le_pow_right h)
    (fun m => (b.value m).rep g a c) ?_ h).symm
  intro m
  exact (congrArg (fun x => x.rep g a c) (b.compatible m)).symm

def branchRepFamily
    (b : PaperX.Compactness.Branch (certificateTower I C φ τ d)) : Family R I G ι where
  maps k := (b.value k).rep
  compatible := branch_rep_compatible I C φ τ d b

open PaperX.MatrixWitnessLimits

/-- The comparison matrices come from the same augmented branch as the representation. -/
def branchMatrixFamily
    (b : PaperX.Compactness.Branch (certificateTower I C φ τ d)) (s : S) :
    MatrixFamily R I ι :=
  matrix_family_of_succ I (fun k => (b.value k).comparison s)
    (fun k => congrArg (fun x => x.comparison s) (b.compatible k))

/-- Simultaneous reconstruction produces integral comparisons satisfying the
actual local intertwining equations and retaining a finite nonzero determinant test. -/
theorem branch_realizes [IsAdicComplete I R]
    (b : PaperX.Compactness.Branch (certificateTower I C φ τ d)) :
    let ρ := reconstruct I (branchRepFamily I C φ τ d b)
    let P := fun s => reconstructMatrix I (branchMatrixFamily I C φ τ d b s)
    Realizes I C ρ ∧
      (∀ s g, ρ (φ s g) * P s = P s * τ s g) ∧
      (∀ s, Ideal.Quotient.mk (I^(d s)) (P s).det ≠ 0) := by
  dsimp only
  refine ⟨?_, ?_, ?_⟩
  · intro k
    rw [reconstruct_reduces]
    exact (b.value k).allowed
  · intro s g
    apply reconstructMatrix_local_intertwines
    intro k x
    exact (b.value k).intertwines s x
  · intro s
    have hx := (b.value (d s)).detected s (le_refl _)
    simp only [Ideal.Quotient.factor_eq, RingHom.id_apply] at hx
    rw [(Ideal.Quotient.mk (I^(d s))).map_det]
    change ((reconstructMatrix I (branchMatrixFamily I C φ τ d b s)).map
      (Ideal.Quotient.mk (I^(d s)))).det ≠ 0
    rw [reconstructMatrix_reduces]
    exact hx

/-- Existence uses occupied finite certificate levels. The detecting depths
are fixed before the quantification over precision. -/
theorem exists_comparison_realization [IsAdicComplete I R] [Finite S]
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (finiteC : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ})
    (occupied : ∀ k, Nonempty (Node I C φ τ d k)) :
    ∃ (ρ : MatrixRep R G ι) (P : S → Matrix ι ι R),
      Realizes I C ρ ∧
      (∀ s g, ρ (φ s g) * P s = P s * τ s g) ∧
      (∀ s, Ideal.Quotient.mk (I^(d s)) (P s).det ≠ 0) := by
  obtain ⟨b⟩ := exists_certificate_branch I C φ τ d finiteR finiteC occupied
  exact ⟨reconstruct I (branchRepFamily I C φ τ d b),
    fun s => reconstructMatrix I (branchMatrixFamily I C φ τ d b s),
    branch_realizes I C φ τ d b⟩

/-- Finite continuity is checked on allowed representations, and survives the
same simultaneous reconstruction used for the local comparison certificates. -/
theorem exists_continuous_comparison_realization [IsAdicComplete I R] [Finite S]
    [TopologicalSpace G]
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (finiteC : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ})
    (occupied : ∀ k, Nonempty (Node I C φ τ d k))
    (continuous : ∀ k ρ, C.allowed k ρ → FiniteRepContinuous ρ) :
    ∃ (ρ : MatrixRep R G ι) (P : S → Matrix ι ι R),
      Realizes I C ρ ∧ AdicRepContinuous I ρ ∧
      (∀ s g, ρ (φ s g) * P s = P s * τ s g) ∧
      (∀ s, Ideal.Quotient.mk (I^(d s)) (P s).det ≠ 0) := by
  obtain ⟨b⟩ := exists_certificate_branch I C φ τ d finiteR finiteC occupied
  have hb := branch_realizes I C φ τ d b
  refine ⟨reconstruct I (branchRepFamily I C φ τ d b),
    fun s => reconstructMatrix I (branchMatrixFamily I C φ τ d b s),
    hb.1, ?_, hb.2⟩
  apply reconstructed_continuous
  intro k
  exact continuous k (b.value k).rep (b.value k).allowed

/-- An actual integral realization with detected comparison determinants supplies
an augmented node at every precision by reduction. -/
def node_of_integral (ρ : MatrixRep R G ι) (P : S → Matrix ι ι R)
    (hρ : Realizes I C ρ)
    (hP : ∀ s g, ρ (φ s g) * P s = P s * τ s g)
    (hdet : ∀ s, Ideal.Quotient.mk (I^(d s)) (P s).det ≠ 0) (k : ℕ) :
    Node I C φ τ d k where
  rep := reduce I ρ k
  allowed := hρ k
  comparison s := (P s).map (Ideal.Quotient.mk (I^k))
  intertwines s g := by
    have hx := congrArg (fun A => A.map (Ideal.Quotient.mk (I^k))) (hP s g)
    rw [Matrix.map_mul, Matrix.map_mul] at hx
    exact hx
  detected s hs := by
    change Ideal.Quotient.factorPow I hs
      ((Ideal.Quotient.mk (I^k)).mapMatrix (P s)).det ≠ 0
    rw [← (Ideal.Quotient.mk (I^k)).map_det, Ideal.Quotient.factor_mk]
    exact hdet s

/-- The finite criterion is exact for integral comparisons carrying these fixed
determinant certificates. It does not assert that arbitrary local packets supply them. -/
theorem comparison_realization_iff [IsAdicComplete I R] [Finite S]
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (finiteC : ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ}) :
    (∃ (ρ : MatrixRep R G ι) (P : S → Matrix ι ι R),
      Realizes I C ρ ∧
      (∀ s g, ρ (φ s g) * P s = P s * τ s g) ∧
      (∀ s, Ideal.Quotient.mk (I^(d s)) (P s).det ≠ 0)) ↔
      ∀ k, Nonempty (Node I C φ τ d k) := by
  constructor
  · rintro ⟨ρ, P, hρ, hP, hdet⟩ k
    exact ⟨node_of_integral I C φ τ d ρ P hρ hP hdet k⟩
  · exact exists_comparison_realization I C φ τ d finiteR finiteC

end PaperX.ComparisonCertificates
