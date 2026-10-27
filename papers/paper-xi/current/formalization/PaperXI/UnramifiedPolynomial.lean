import PaperXI.MonicResidueAlgebra
import Mathlib.RingTheory.DiscreteValuationRing.TFAE
import Mathlib.RingTheory.LocalRing.Etale
import Mathlib.RingTheory.Smooth.Fiber
import Mathlib.RingTheory.RamificationInertia.Ramification
import Mathlib.LinearAlgebra.Dimension.Localization
import Mathlib.RingTheory.Localization.FractionRing
import Mathlib.RingTheory.IntegralClosure.IsIntegralClosure.Basic

/-! An irreducible residue polynomial constructs a finite etale DVR and its
actual fraction field, without any supplied ambient Galois extension. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.UnramifiedPolynomial
open Polynomial IsLocalRing
open PaperXI.MonicResidueAlgebra
variable {R : Type*} [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
variable (f : R[X]) [hm : Fact f.Monic]
variable [hi : Fact (Irreducible (f.map (residue R)))]

theorem irreducible : Irreducible f :=
  Polynomial.Monic.irreducible_of_irreducible_map (residue R) f hm.out hi.out

instance domain : IsDomain (AdjoinRoot f) :=
  AdjoinRoot.isDomain_of_prime ((irreducible_iff_prime).mp (irreducible f))

instance faithful : FaithfulSMul R (AdjoinRoot f) :=
  AdjoinRoot.faithfulSMul_of_monic_of_degree_pos hm.out (degree_pos f)

theorem not_field : ¬ IsField (AdjoinRoot f) := by
  intro h
  have : IsField R := IsLocalHom.isField
    (f := algebraMap R (AdjoinRoot f)) (FaithfulSMul.algebraMap_injective _ _) h
  exact IsDiscreteValuationRing.not_isField R this

/-- The monogenic local domain is a DVR, rather than merely a free module. -/
instance dvr : IsDiscreteValuationRing (AdjoinRoot f) := by
  apply ((IsDiscreteValuationRing.TFAE (AdjoinRoot f) (not_field f)).out 5 1).mp
  obtain ⟨π, hπ⟩ := IsDiscreteValuationRing.exists_irreducible R
  rw [maximalIdeal_eq, specialIdeal, hπ.maximalIdeal_eq, Ideal.map_span, Set.image_singleton]
  infer_instance

/-- The uniformizer is unchanged. -/
theorem uniformizer (π : R) (hπ : Ideal.span {π} = maximalIdeal R) :
    Ideal.span {algebraMap R (AdjoinRoot f) π} = maximalIdeal (AdjoinRoot f) := by
  rw [maximalIdeal_eq, specialIdeal, ← hπ, Ideal.map_span, Set.image_singleton]


/-- The constructed upper field is the fraction field of the actual root DVR. -/
abbrev field := FractionRing (AdjoinRoot f)

instance baseFieldAlgebra : Algebra (FractionRing R) (field f) :=
  FractionRing.liftAlgebra R (field f)

instance baseFieldTower : IsScalarTower R (FractionRing R) (field f) :=
  FractionRing.isScalarTower_liftAlgebra R (field f)

theorem natDegree_pos_of_residue_irreducible :
    0 < f.natDegree :=
  Polynomial.natDegree_pos_iff_degree_pos.mpr (degree_pos f)

theorem field_degree : Module.finrank (FractionRing R) (field f) = f.natDegree := by
  rw [IsFractionRing.finrank_eq R (FractionRing R) (AdjoinRoot f) (field f)]
  exact MonicResidueAlgebra.rank f

instance finiteFieldExtension : FiniteDimensional (FractionRing R) (field f) :=
  .of_finrank_pos ((field_degree f).symm ▸ natDegree_pos_of_residue_irreducible f)



theorem integralClosure : IsIntegralClosure (AdjoinRoot f) R (field f) := by
  let := AdjoinRoot.isIntegral_of_monic hm.out
  infer_instance

variable [Finite (ResidueField R)]

/-- Finite presentation, flatness and the separable residue identify the actual etale predicate. -/
theorem etale : Algebra.Etale R (AdjoinRoot f) := by
  let : Algebra.FormallyUnramified R (AdjoinRoot f) :=
    Algebra.FormallyUnramified.of_map_maximalIdeal (maximalIdeal_eq f).symm
  let : Algebra.FinitePresentation R (AdjoinRoot f) :=
    Algebra.FinitePresentation.of_finiteType.mp inferInstance
  exact Algebra.Etale.of_formallyUnramified_of_flat

theorem ramificationIdx_one :
    (maximalIdeal (AdjoinRoot f)).ramificationIdx R = 1 := by
  let := etale f
  exact Ideal.ramificationIdx_eq_one _ _

end PaperXI.UnramifiedPolynomial
