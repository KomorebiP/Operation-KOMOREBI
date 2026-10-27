import ContinuousFiniteImageCapstone
import NonzeroRepresentationObstruction
import RelativeObstructionNegativeControl
import Mathlib.Topology.Compactness.Compact

/-! Kernel-checked positive and negative controls. Finite enumerations use
`decide`, never `native_decide`. Positive lifting is obtained by the general
averaging theorem, not by inserting a preselected representation lift. -/
namespace Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples

local instance (n : ℕ) : TopologicalSpace (ZMod n) := ⊥
local instance (n : ℕ) : DiscreteTopology (ZMod n) := ⟨rfl⟩

abbrev Q := Multiplicative (ZMod 2)
abbrev ProductSource := ℕ → Q

def quotientLabel : ProductSource →* Q where
  toFun g := g 0
  map_one' := rfl
  map_mul' _ _ := rfl

theorem quotientLabel_continuous : Continuous quotientLabel := continuous_apply 0

def q : ZMod 9 →+* ZMod 3 := ZMod.castHom (by decide : 3 ∣ 9) (ZMod 3)

theorem q_surjective : Function.Surjective q := ZMod.castHom_surjective (by decide)

theorem q_squareZero : ∀ a b : ZMod 9, q a=0 → q b=0 → a*b=0 := by decide

def signRepresentation : Q →* (ZMod 3)ˣ where
  toFun g := (ZMod.unitOfCoprime 2 (by decide : Nat.Coprime 2 3))^g.toAdd.val
  map_one' := by decide
  map_mul' := by decide

theorem quotient_order_isUnit : IsUnit (Fintype.card Q : ZMod 9) := by
  change IsUnit (2 : ZMod 9)
  exact (ZMod.unitOfCoprime 2 (by decide : Nat.Coprime 2 9)).isUnit

/-- The source has its infinite product topology. The proof does not place the
discrete topology on it; the corrected lift is continuous by quotient factorization. -/
theorem infinite_product_source_has_continuous_lift :
    ∃ LQ : Q →* (ZMod 9)ˣ, (∀ a, q (LQ a)=(signRepresentation a : ZMod 3)) ∧
      Continuous (LQ.comp quotientLabel) ∧
      ∀ g, q ((LQ.comp quotientLabel) g)=(signRepresentation (quotientLabel g) : ZMod 3) :=
  continuous_representation_lifts_through_finite_quotient quotientLabel
    quotientLabel_continuous q q_surjective q_squareZero signRepresentation quotient_order_isUnit

/-- A concrete matrix representation also lifts by the general theorem. -/
theorem all_C2_matrix_representations_lift (rho : Q →* (Matrix (Fin 2) (Fin 2) (ZMod 3))ˣ) :
    ∃ L : Q →* (Matrix (Fin 2) (Fin 2) (ZMod 9))ˣ,
      ∀ a, (q.mapMatrix : Matrix (Fin 2) (Fin 2) (ZMod 9) →+*
        Matrix (Fin 2) (Fin 2) (ZMod 3)) (L a)=(rho a : Matrix (Fin 2) (Fin 2) (ZMod 3)) := by
  let D := matrixDatum q q_surjective q_squareZero rho
  have hu : IsUnit (Fintype.card Q : Matrix (Fin 2) (Fin 2) (ZMod 9)) := by
    change IsUnit (2 : Matrix (Fin 2) (Fin 2) (ZMod 9))
    exact ⟨⟨2,5,by decide,by decide⟩,rfl⟩
  exact D.representation_lifts_of_groupOrder_isUnit hu

/-- The genuinely nonzero H² obstruction remains nonzero in the continuous
cochain quotient; continuity is not a shortcut around obstruction vanishing. -/
theorem continuous_absolute_obstruction_nonzero :
    Example.datum.continuousObstruction (by exact continuous_of_discreteTopology) ≠ 0 := by
  intro hz
  exact Example.obstruction_nonzero
    (Example.datum.continuous_zero_implies_ordinary_zero _ hz)

theorem continuous_absolute_zero_but_fixed_subgroup_nonzero :
    RelativeExample.datum.continuousObstruction (by exact continuous_of_discreteTopology)=0 ∧
    RelativeExample.datum.continuousRelativeObstruction RelativeExample.H
      (by exact continuous_of_discreteTopology)
      RelativeExample.prescribed_subgroup_multiplicative ≠ 0 := by
  constructor
  · exact (RelativeExample.datum.continuous_zero_iff_ordinary_zero_of_discrete_source _).mpr
      RelativeExample.absolute_obstruction_zero
  · intro hz
    obtain ⟨L,_,_,hfix⟩ := (RelativeExample.datum.continuous_fixed_restriction_lifts_iff
      RelativeExample.H _ RelativeExample.prescribed_subgroup_multiplicative).mpr hz
    exact RelativeExample.no_fixed_subgroup_lift ⟨L,hfix⟩

/-- The positive test genuinely has a non-discrete compact source. -/
theorem productSource_compact : CompactSpace ProductSource := inferInstance

theorem productSource_not_discrete : ¬ DiscreteTopology ProductSource := by
  intro h
  have : DiscreteTopology ProductSource := h
  have : Finite ProductSource := finite_of_compact_of_discrete
  exact not_finite ProductSource

theorem product_residual_representation_continuous :
    Continuous (signRepresentation.comp quotientLabel) :=
  (continuous_of_discreteTopology : Continuous signRepresentation).comp quotientLabel_continuous

theorem product_continuous_obstruction_zero :
    (continuousSectionDatum q q_surjective q_squareZero (signRepresentation.comp quotientLabel)).continuousObstruction
      (continuousSectionDatum_continuous_lift q q_surjective q_squareZero
        (signRepresentation.comp quotientLabel) product_residual_representation_continuous)=0 := by
  obtain ⟨LQ,_,hc,hL⟩ := infinite_product_source_has_continuous_lift
  exact (continuous_lifts_iff_constructed_obstruction_zero q q_surjective q_squareZero
    (signRepresentation.comp quotientLabel) product_residual_representation_continuous).mp
    ⟨LQ.comp quotientLabel,hc,hL⟩

end Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples
