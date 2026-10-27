import PaperX.NormResidueLatticeMap
import PaperX.IdealNormWeightedAttachment
import PaperX.ResidueLatticePointSums

/-! Exact attachment of cone lattice sums to bounded algebraic generators. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NormResidueLattice
open Ideal NumberField
open NumberField.mixedEmbedding NumberField.mixedEmbedding.fundamentalCone
open NumberField.mixedEmbedding.euclidean
open PaperX.IdealClassQuantitative PaperX.ResidueLattice PaperX.IdealNormWeighted
open scoped nonZeroDivisors Classical Pointwise

variable (K : Type*) [Field K] [NumberField K]

/-- The absolute principal norm at an actual ideal-lattice point is its mixed norm. -/
theorem integerRepresentative_absNorm_cast (J : (Ideal (𝓞 K))⁰)
    (x : idealEuclideanLattice K J) :
    (absNorm (span {integerRepresentative K J x}) : ℝ) =
      mixedEmbedding.norm (toMixed K x.1) := by
  rw [absNorm_span_singleton, Nat.cast_natAbs, ← Rat.cast_intCast, Int.cast_abs,
    Algebra.coe_norm_int, ← norm_eq_norm]
  congr 1
  have h := congrArg (toMixed K) (integerRepresentative_point K J x)
  simpa only [integerPoint, ContinuousLinearEquiv.apply_symm_apply] using h

/-- The bounded cone-point equivalence preserves the represented mixed coordinate. -/
theorem coneLatticeEquiv_coe (J : (Ideal (𝓞 K))⁰) (Y : ℝ)
    (x : (coneRegion K Y ∩ idealEuclideanLattice K J : Set (euclidean.mixedSpace K))) :
    ((coneLatticeEquiv K J Y x).val : mixedSpace K) = toMixed K x.val := rfl

/-- Actual dilated lattice points correspond to generators bounded by the degree power. -/
def latticePointsGeneratorEquiv (J : (Ideal (𝓞 K))⁰) {t : ℝ} (ht : 0 < t) :
    LatticePoints (idealEuclideanLattice K J) (coneRegion K 1) t ≃
      {a : idealSet K J // mixedEmbedding.norm (a : mixedSpace K) ≤
        t ^ Module.finrank ℚ K} := by
  let e : LatticePoints (idealEuclideanLattice K J) (coneRegion K 1) t ≃
      (coneRegion K (t ^ Module.finrank ℚ K) ∩ idealEuclideanLattice K J :
        Set (euclidean.mixedSpace K)) :=
    { toFun := fun x => ⟨x.1.1, ⟨by
        rw [← smul_coneRegion_one K ht]
        exact x.2, x.1.2⟩⟩
      invFun := fun x => ⟨⟨x.1, x.2.2⟩, by
        rw [smul_coneRegion_one K ht]
        exact x.2.1⟩
      left_inv := fun _ => rfl
      right_inv := fun _ => rfl }
  exact e.trans (coneLatticeEquiv K J _)

/-- This equivalence preserves the actual natural-number norm used by every weight. -/
theorem latticePointsGeneratorEquiv_absNorm (J : (Ideal (𝓞 K))⁰) {t : ℝ}
    (ht : 0 < t) (x : LatticePoints (idealEuclideanLattice K J) (coneRegion K 1) t) :
    generatorAbsNorm K J (latticePointsGeneratorEquiv K J ht x).val =
      absNorm (span {integerRepresentative K J x.val}) := by
  apply Nat.cast_injective (R := ℝ)
  rw [generatorAbsNorm_cast, integerRepresentative_absNorm_cast]
  rfl

/-- Arbitrary norm weights agree exactly on the lattice and algebraic-generator domains. -/
theorem latticeGeneratorSum_eq_boundedGeneratorSum (J : (Ideal (𝓞 K))⁰)
    (f : ℕ → ℂ) {t : ℝ} (ht : 0 < t) :
    (∑ᶠ x : LatticePoints (idealEuclideanLattice K J) (coneRegion K 1) t,
      f (absNorm (span {integerRepresentative K J x.val}))) =
      boundedGeneratorSum K J f (t ^ Module.finrank ℚ K) := by
  unfold boundedGeneratorSum
  exact finsum_eq_of_bijective (latticePointsGeneratorEquiv K J ht)
    (latticePointsGeneratorEquiv K J ht).bijective
    (fun x => congrArg f (latticePointsGeneratorEquiv_absNorm K J ht x).symm)

end PaperX.NormResidueLattice
