import PaperXII.InverseLimitRepresentations
import PaperX.RepresentationTopology
import Mathlib.Topology.Algebra.Group.Matrix

/-! The actual adic matrix-group comparison for the reconstruction part of 10.5.
Precision n means R / I^n; precision zero is the trivial quotient, and the
first residual quotient occurs at precision one. -/
set_option autoImplicit false
namespace PaperXII.AdicMatrixGroups

open ContinuousMonoidHom Matrix

variable {R : Type} [CommRing R] (I : Ideal R)
variable {ι : Type} [Fintype ι] [DecidableEq ι]

/-- The literal ideal-power quotient, with a dedicated name to specify its discrete topology. -/
def Coeff (n : ℕ) := R ⧸ I ^ n

instance coeffCommRing (n : ℕ) : CommRing (Coeff I n) :=
  inferInstanceAs (CommRing (R ⧸ I ^ n))

instance coeffTopologicalSpace (n : ℕ) : TopologicalSpace (Coeff I n) := ⊥

instance coeffDiscreteTopology (n : ℕ) : DiscreteTopology (Coeff I n) := ⟨rfl⟩

/-- The actual quotient homomorphism. -/
def quotientMap (n : ℕ) : R →+* Coeff I n := Ideal.Quotient.mk (I ^ n)

/-- Adjacent reduction on coefficient rings. -/
def coefficientStep (n : ℕ) : Coeff I (n + 1) →+* Coeff I n :=
  Ideal.Quotient.factorPow I (Nat.le_succ n)

/-- Adjacent reduction on actual general linear groups, with its discrete continuity proof. -/
def step (n : ℕ) : GL ι (Coeff I (n + 1)) →ₜ* GL ι (Coeff I n) where
  __ := GeneralLinearGroup.map (coefficientStep I n)
  continuous_toFun := continuous_of_discreteTopology.generalLinearGroup_map

/-- The previously defined compatible-tuple inverse-limit group for the quotient matrix groups. -/
def Limit : Subgroup (∀ n, GL ι (Coeff I n)) :=
  InverseLimitRepresentations.limit (step (ι := ι) I)

/-- Reduction of an integral invertible matrix to one finite precision. -/
def reduce (n : ℕ) : GL ι R →* GL ι (Coeff I n) :=
  GeneralLinearGroup.map (quotientMap I n)

/-- The canonical homomorphism from GL over the coefficient ring to the limit. -/
def toLimit : GL ι R →* Limit (ι := ι) I where
  toFun A := ⟨fun n ↦ reduce I n A, fun n ↦ by
    apply Units.ext
    ext i j
    exact rfl⟩
  map_one' := by apply Subtype.ext; funext n; exact map_one (reduce I n)
  map_mul' A B := by apply Subtype.ext; funext n; exact map_mul (reduce I n) A B

/-- Coordinates of the limit form an actual compatible matrix representation of the limit group. -/
def coordinateFamily : PaperX.RepresentationLimits.Family R I (Limit (ι := ι) I) ι where
  maps n :=
    { toFun g := (g.val n).val
      map_one' := rfl
      map_mul' _ _ := rfl }
  compatible := by
    intro j k hjk
    ext g a b
    apply (Ideal.Quotient.eq_factor_of_eq_factor_succ
      (fun _ _ h ↦ Ideal.pow_le_pow_right h)
      (fun n ↦ (g.val n).val a b) ?_ hjk).symm
    intro n
    exact (congrArg (fun A : GL ι (Coeff I n) ↦ A.val a b) (g.property n)).symm

/-- Lift the coordinate representation entrywise, including its inverses. -/
noncomputable def lift [IsAdicComplete I R] : Limit (ι := ι) I →* GL ι R :=
  PaperX.RepresentationLimits.unitRepresentation I (coordinateFamily I)

/-- Every reduction of the lifted matrix is the prescribed matrix. -/
theorem reduce_lift [IsAdicComplete I R] (g : Limit (ι := ι) I) (n : ℕ) :
    reduce I n (lift I g) = g.val n := by
  apply Units.ext
  exact congrArg (fun ρ ↦ ρ g)
    (PaperX.RepresentationLimits.reconstruct_reduces I (coordinateFamily I) n)

/-- Separatedness detects equality of invertible matrices at all precisions. -/
theorem ext_of_reductions [IsHausdorff I R] {A B : GL ι R}
    (h : ∀ n, reduce I n A = reduce I n B) : A = B := by
  apply Units.ext
  apply PaperX.RepresentationLimits.matrix_ext I
  intro n
  exact congrArg Units.val (h n)

/-- Reducing after lifting returns the original tuple. -/
theorem toLimit_lift [IsAdicComplete I R] (g : Limit (ι := ι) I) :
    toLimit I (lift I g) = g := by
  apply Subtype.ext
  funext n
  exact reduce_lift I g n

/-- Lifting the reductions returns the original integral matrix. -/
theorem lift_toLimit [IsAdicComplete I R] (A : GL ι R) :
    lift I (toLimit I A) = A := by
  apply ext_of_reductions I
  intro n
  exact reduce_lift I (toLimit I A) n

/-- The matrix-group isomorphism is proved from adic completeness. -/
noncomputable def groupEquiv [IsAdicComplete I R] : GL ι R ≃* Limit (ι := ι) I where
  toFun := toLimit I
  invFun := lift I
  left_inv := lift_toLimit I
  right_inv := toLimit_lift I
  map_mul' := (toLimit I).map_mul

/-- Coordinate matrix representations are continuous into the discrete finite-precision rings. -/
theorem coordinateFamily_continuous (n : ℕ) :
    PaperX.RepresentationTopology.FiniteRepContinuous ((coordinateFamily (ι := ι) I).maps n) := by
  intro i j
  apply (PaperX.RepresentationTopology.finiteContinuous_iff _).mpr
  have hn : Continuous (fun g : Limit (ι := ι) I ↦ g.val n) :=
    (continuous_apply n).comp continuous_subtype_val
  have hm : Continuous (fun g : Limit (ι := ι) I ↦ (g.val n).val) :=
    Units.continuous_val.comp hn
  exact (continuous_apply j).comp ((continuous_apply i).comp hm)

/-- The lifting homomorphism is continuous for the actual I-adic topology on R. -/
theorem lift_continuous [IsAdicComplete I R] :
    let _ : TopologicalSpace R := I.adicTopology
    Continuous (lift (ι := ι) I) := by
  let _ : TopologicalSpace R := I.adicTopology
  have hc := PaperX.RepresentationTopology.reconstructed_continuous I
    (coordinateFamily (ι := ι) I) (coordinateFamily_continuous I)
  apply Units.continuous_iff.mpr
  constructor
  · exact hc
  · exact hc.comp continuous_inv

/-- Reduction is continuous from the adic coefficient topology to the discrete quotient. -/
theorem quotientMap_continuous (n : ℕ) :
    let _ : TopologicalSpace R := I.adicTopology
    Continuous (quotientMap I n) := by
  let _ : TopologicalSpace R := I.adicTopology
  exact (PaperX.RepresentationTopology.finiteContinuous_iff _).mp
    (PaperX.RepresentationTopology.reductions_of_continuous I (fun x : R ↦ x)
      continuous_id n)

/-- The canonical homomorphism to the inverse limit is continuous. -/
theorem toLimit_continuous :
    let _ : TopologicalSpace R := I.adicTopology
    Continuous (toLimit (ι := ι) I) := by
  let _ : TopologicalSpace R := I.adicTopology
  apply Continuous.subtype_mk
  apply continuous_pi
  intro n
  exact (quotientMap_continuous I n).generalLinearGroup_map

/-- The proved group isomorphism is also a homeomorphism. -/
noncomputable def homeomorph [IsAdicComplete I R] :
    let _ : TopologicalSpace R := I.adicTopology
    GL ι R ≃ₜ Limit (ι := ι) I := by
  let _ : TopologicalSpace R := I.adicTopology
  exact
    { toEquiv := (groupEquiv I).toEquiv
      continuous_toFun := toLimit_continuous I
      continuous_invFun := lift_continuous I }

end PaperXII.AdicMatrixGroups
