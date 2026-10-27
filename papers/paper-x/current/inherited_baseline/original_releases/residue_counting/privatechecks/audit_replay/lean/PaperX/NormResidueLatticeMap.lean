import PaperX.ResidueLatticeIdealPoints
import PaperX.NormResidueArithmetic

/-! Exact descent from actual ideal-lattice residues to arithmetic residue norms.
The map need not be surjective; no codomain density is inferred from it. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.NormResidueLattice
open Ideal NumberField
open PaperX.IdealClassQuantitative PaperX.ResidueLattice PaperX.NormResidue
open scoped nonZeroDivisors

variable (K : Type*) [Field K] [NumberField K]

/-- The unique algebraic integer underlying a point of an actual integral ideal lattice. -/
def integerRepresentative (J : (Ideal (𝓞 K))⁰) (x : idealEuclideanLattice K J) : 𝓞 K :=
  ((idealPointEquiv K J).symm x).1

theorem integerRepresentative_point (J : (Ideal (𝓞 K))⁰) (x : idealEuclideanLattice K J) :
    integerPoint K (integerRepresentative K J x) = x.1 :=
  congrArg Subtype.val ((idealPointEquiv K J).apply_symm_apply x)

theorem integerRepresentative_equiv (J : (Ideal (𝓞 K))⁰) (x : (J : Ideal (𝓞 K))) :
    integerRepresentative K J (idealPointEquiv K J x) = x.1 :=
  congrArg Subtype.val ((idealPointEquiv K J).symm_apply_apply x)

/-- The true map on the ideal-lattice residue quotient, when M lies in the modulus ideal.
The domain is J/(J∩M); it is J/M when M≤J. -/
def residueToIntegerQuotient (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m) :
    IdealResidues K M J → 𝓞 K ⧸ modulusIdeal (𝓞 K) m :=
  Quotient.lift (fun x : idealEuclideanLattice K J => Ideal.Quotient.mk (modulusIdeal (𝓞 K) m)
    (integerRepresentative K J x)) (by
      intro x y hxy
      apply Ideal.Quotient.eq.mpr
      apply hM
      rw [← integerPoint_mem_iff K M, integerPoint_sub,
        integerRepresentative_point, integerRepresentative_point]
      exact (Submodule.Quotient.eq
        ((idealEuclideanLattice K M).comap (idealEuclideanLattice K J).subtype)).mp
          (Quotient.sound hxy))

theorem residueToIntegerQuotient_mk (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    (x : (J : Ideal (𝓞 K))) :
    residueToIntegerQuotient K M J m hM
      (Submodule.Quotient.mk (idealPointEquiv K J x)) =
        Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) x.1 := by
  change Ideal.Quotient.mk _ (integerRepresentative K J (idealPointEquiv K J x)) = _
  rw [integerRepresentative_equiv]

/-- The actual signed element norm on the additive ideal-lattice residue quotient. -/
def residueNorm (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m) :
    IdealResidues K M J → ZMod m :=
  fun c => integerQuotientNorm K m (residueToIntegerQuotient K M J m hM c)

theorem residueNorm_mk (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    (x : (J : Ideal (𝓞 K))) :
    residueNorm K M J m hM (Submodule.Quotient.mk (idealPointEquiv K J x)) =
      (Algebra.norm ℤ x.1 : ZMod m) := by
  rw [residueNorm, residueToIntegerQuotient_mk, integerQuotientNorm_mk]

end PaperX.NormResidueLattice
