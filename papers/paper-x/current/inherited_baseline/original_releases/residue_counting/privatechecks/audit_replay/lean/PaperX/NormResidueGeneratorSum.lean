import PaperX.NormResidueWeightedCounting
import PaperX.NormSignPartition

/-! The finite residue calculation is the actual principal-norm sum on cone
points, before applying roots-of-unity multiplicity or dividing by a norm. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.NormResidueLattice
open Ideal NumberField
open PaperX.IdealClassQuantitative PaperX.ResidueLattice PaperX.NormResidue
open PaperX.NormSignGeometry
open scoped nonZeroDivisors Classical Pointwise BigOperators
variable (K : Type*) [Field K] [NumberField K]

/-- The actual absolute principal norm weight of the unique algebraic integer
underlying an integral ideal-lattice point. -/
def generatorPointWeight (J : (Ideal (𝓞 K))⁰) (m : ℕ) (χ : ZMod m → ℂ)
    (x : idealEuclideanLattice K J) : ℂ :=
  χ (Ideal.absNorm (Ideal.span {integerRepresentative K J x}) : ZMod m)

theorem normWeight_actualPoint (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    (χ : ZMod m → ℂ) (positive : Bool) {t : ℝ} (ht : 0 < t)
    (x : LatticePoints (idealEuclideanLattice K J) (signRegion K positive) t) :
    normWeight K M J m hM χ positive (Submodule.Quotient.mk x.1) =
      generatorPointWeight K J m χ x.1 := by
  have hx : integerPoint K (integerRepresentative K J x.1) ∈ t • signRegion K positive := by
    rw [integerRepresentative_point]
    exact x.2
  have he := normWeight_mk K M J m hM χ positive ((idealPointEquiv K J).symm x.1) ht hx
  rw [Equiv.apply_symm_apply] at he
  exact he

/-- The residue-weighted count on either sign portion is its actual point sum. -/
theorem weightedFiberCount_eq_generatorPointSum (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    [Fintype (IdealResidues K M J)] (χ : ZMod m → ℂ) (positive : Bool)
    {t : ℝ} (ht : 0 < t) :
    weightedFiberCount (idealEuclideanLattice K M) (idealEuclideanLattice K J)
        (signRegion K positive) (normWeight K M J m hM χ positive) t =
      ∑ᶠ x : LatticePoints (idealEuclideanLattice K J) (signRegion K positive) t,
        generatorPointWeight K J m χ x.1 := by
  rw [weightedFiberCount_eq_pointSum _ _ (signRegion_bounded K positive)]
  unfold latticePointSum
  exact finsum_congr (normWeight_actualPoint K M J m hM χ positive ht)

/-- Recombination gives one sum over the actual cone points, weighted by the
absolute norms of their actual principal ideals. No multiplicity is suppressed. -/
theorem normWeightedCount_eq_generatorPointSum (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    [Fintype (IdealResidues K M J)] (χ : ZMod m → ℂ) {t : ℝ} (ht : 0 < t) :
    normWeightedCount K M J m hM χ t =
      ∑ᶠ x : LatticePoints (idealEuclideanLattice K J) (coneRegion K 1) t,
        χ (Ideal.absNorm (Ideal.span {integerRepresentative K J x.1}) : ZMod m) := by
  unfold normWeightedCount
  simp_rw [weightedFiberCount_eq_generatorPointSum K M J m hM χ _ ht]
  rw [Fintype.sum_bool]
  exact (finsum_latticePoints_sign_split K (idealEuclideanLattice K J)
    (generatorPointWeight K J m χ) ht).symm

end PaperX.NormResidueLattice
