import LocalGaugeExactSequence
import LocalGaugeInvariance
import LocalGluingCounterexample
import TameStrictVersusConjugateExample

/-! Positive and negative controls for the CONSTRUCTED class. A gauge quotient
must remove the tame framing discrepancy, but must not erase a genuine gluing
failure for commutative coefficients. -/
namespace Komorebi.StrongArtin.SquareZeroH2

namespace LocalGluingExample
local instance : TopologicalSpace A := ⊥
local instance : DiscreteTopology A := ⟨rfl⟩
local instance : TopologicalSpace B := ⊥
local instance : DiscreteTopology B := ⟨rfl⟩
local instance : TopologicalSpace G := ⊥
local instance : DiscreteTopology G := ⟨rfl⟩
local instance : TopologicalSpace C2 := ⊥
local instance : DiscreteTopology C2 := ⟨rfl⟩

noncomputable def gaugeClass := datum.localConjugacyObstruction
  (fun _ : Fin 3 => C2) datum_continuous loc (fun _ => continuous_of_discreteTopology)
  prescribed prescribed_residue (fun _ => continuous_of_discreteTopology)

theorem gauge_obstruction_nonzero : gaugeClass≠0 := by
  intro hz
  obtain ⟨lift,_hc,_hr,u,_hu,hfix⟩ :=
    (datum.continuous_local_conjugacy_lifts_iff (fun _ : Fin 3 => C2)
      datum_continuous loc (fun _ => continuous_of_discreteTopology)
      prescribed prescribed_residue (fun _ => continuous_of_discreteTopology)).mpr hz
  exact no_simultaneous_lift_even_up_to_local_conjugacy
    ⟨lift,fun i => ⟨u i,fun h => (hfix i h).symm⟩⟩

theorem absolute_zero_does_not_force_local_gauge_zero :
    datum.continuousObstruction datum_continuous=0 ∧ gaugeClass≠0 :=
  ⟨absolute_obstruction_zero,gauge_obstruction_nonzero⟩

theorem actual_h1_localization_cokernel_class_nonzero :
    ∃ b0 : datum.continuousOneCochains,
      ∃ hb0 : datum.continuousDifferential datum_continuous b0=
        datum.continuousDefectOf datum.lift datum.lift_residue datum_continuous,
      datum.h1GluingObstruction (fun _ : Fin 3 => C2) datum_continuous loc
        (fun _ => continuous_of_discreteTopology)
        (datum.prescribedLocalPair (fun _ : Fin 3 => C2) datum_continuous loc
          (fun _ => continuous_of_discreteTopology) prescribed prescribed_residue
          (fun _ => continuous_of_discreteTopology)) b0 hb0 ≠ 0 := by
  obtain ⟨b,hbc,hb⟩ := (datum.continuousObstruction_zero_iff datum_continuous).mp
    absolute_obstruction_zero
  have he : datum.continuousDifferential datum_continuous ⟨b,hbc⟩=
      datum.continuousDefectOf datum.lift datum.lift_residue datum_continuous := by
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    exact (hb g h).symm
  refine ⟨⟨b,hbc⟩,he,fun hz => ?_⟩
  exact gauge_obstruction_nonzero
    ((datum.localGauge_zero_iff_h1Gluing_zero (fun _ : Fin 3 => C2)
      datum_continuous loc (fun _ => continuous_of_discreteTopology) _ ⟨b,hbc⟩ he).mpr hz)

end LocalGluingExample

namespace TameGluingExample
local instance : TopologicalSpace M9 := ⊥
local instance : DiscreteTopology M9 := ⟨rfl⟩
local instance : TopologicalSpace M3 := ⊥
local instance : DiscreteTopology M3 := ⟨rfl⟩
local instance : TopologicalSpace G := ⊥
local instance : DiscreteTopology G := ⟨rfl⟩
local instance : TopologicalSpace C2 := ⊥
local instance : DiscreteTopology C2 := ⟨rfl⟩

def gaugeTestLoc : Fin 2 → C2 →* G := ![LocalGluingExample.axisOne,LocalGluingExample.axisTwo]
def gaugeTestPrescribed : Fin 2 → C2 →* M9ˣ := ![signA,signB]
def gaugeTestRho : G →* M3ˣ := (Units.map matrixReduction.toMonoidHom).comp globalCandidate

theorem matrixReduction_surjective : Function.Surjective matrixReduction :=
  matrix_map_surjective reduction (by decide)

theorem matrixReduction_squareZero :
    ∀ X Y, matrixReduction X=0 → matrixReduction Y=0 → X*Y=0 :=
  matrix_kernel_squareZero reduction (by decide)

noncomputable def gaugeDatum : Datum G M9 M3 :=
  continuousSectionDatum matrixReduction matrixReduction_surjective matrixReduction_squareZero gaugeTestRho

theorem gaugeDatum_continuous : Continuous gaugeDatum.lift :=
  continuousSectionDatum_continuous_lift matrixReduction matrixReduction_surjective
    matrixReduction_squareZero gaugeTestRho continuous_of_discreteTopology

theorem gaugeTestPrescribed_residue :
    ∀ i h, gaugeDatum.q (gaugeTestPrescribed i h)=gaugeDatum.rho (gaugeTestLoc i h) := by
  change ∀ i h, matrixReduction (gaugeTestPrescribed i h)=
    (gaugeTestRho (gaugeTestLoc i h) : M3)
  decide

noncomputable def strictGaugeTestClass := gaugeDatum.simultaneousLocalObstruction
  (fun _ : Fin 2 => C2) gaugeDatum_continuous gaugeTestLoc
    (fun _ => continuous_of_discreteTopology) gaugeTestPrescribed
      gaugeTestPrescribed_residue (fun _ => continuous_of_discreteTopology)

noncomputable def gaugeTestClass := gaugeDatum.localConjugacyObstruction
  (fun _ : Fin 2 => C2) gaugeDatum_continuous gaugeTestLoc
    (fun _ => continuous_of_discreteTopology) gaugeTestPrescribed
      gaugeTestPrescribed_residue (fun _ => continuous_of_discreteTopology)

theorem strict_gauge_test_class_nonzero : strictGaugeTestClass≠0 := by
  intro hz
  obtain ⟨lift,_hc,_hr,hfix⟩ :=
    (gaugeDatum.continuous_simultaneous_local_lifts_iff (fun _ : Fin 2 => C2)
      gaugeDatum_continuous gaugeTestLoc (fun _ => continuous_of_discreteTopology)
      gaugeTestPrescribed gaugeTestPrescribed_residue
      (fun _ => continuous_of_discreteTopology)).mpr hz
  exact no_literal_global_lift ⟨lift,(fun h => hfix 0 h),(fun h => hfix 1 h)⟩

theorem gauge_test_class_zero : gaugeTestClass=0 := by
  apply (gaugeDatum.continuous_local_conjugacy_lifts_iff (fun _ : Fin 2 => C2)
    gaugeDatum_continuous gaugeTestLoc (fun _ => continuous_of_discreteTopology)
    gaugeTestPrescribed gaugeTestPrescribed_residue
    (fun _ => continuous_of_discreteTopology)).mp
  refine ⟨globalCandidate,continuous_of_discreteTopology,fun _ => rfl,
    ![1,conjugator],?_,?_⟩
  · change ∀ i : Fin 2, matrixReduction (![1,conjugator] i)=1
    decide
  · change ∀ (i : Fin 2) (h : C2),
      ![1,conjugator] i*globalCandidate (gaugeTestLoc i h)*(![1,conjugator] i)⁻¹=gaugeTestPrescribed i h
    decide

theorem strict_nonzero_but_gauge_zero : strictGaugeTestClass≠0 ∧ gaugeTestClass=0 :=
  ⟨strict_gauge_test_class_nonzero,gauge_test_class_zero⟩

end TameGluingExample
end Komorebi.StrongArtin.SquareZeroH2
