import KomorebiLSM.CoveredAdaptiveActions
import Mathlib.Probability.Distributions.Bernoulli

/-! Exact probability-kernel boundaries for covered adaptive evidence. -/
set_option autoImplicit false
namespace Komorebi.LSM.CoveredAdaptiveActions.Boundaries
open MeasureTheory ProbabilityTheory

noncomputable def neverPolicy : Kernel Unit Bool :=
  Kernel.deterministic (fun _ => false) measurable_const

noncomputable def observations (tag : Bool) : Kernel (Unit × Bool) Bool :=
  Kernel.deterministic (fun h => if h.2 then tag else false) (measurable_of_countable _)

instance neverPolicy_markov : IsMarkovKernel neverPolicy := by
  unfold neverPolicy
  infer_instance

instance observations_markov (tag : Bool) : IsMarkovKernel (observations tag) := by
  unfold observations
  infer_instance

def oneTest : Unit × Bool → ℝ := fun _ => 1

theorem target_propensity_zero : propensity neverPolicy true ()=0 := by
  simp [propensity,neverPolicy,Kernel.deterministic_apply,Measure.real]

theorem unobserved_evidence_zero (r : Bool × Bool) :
    weightedTest neverPolicy oneTest true ((),r)=0 := by
  simp [weightedTest,oneTest,target_propensity_zero]

theorem unobserved_mean_one : targetMean (observations true) oneTest true ()=1 := by
  change (∫ _ : Bool,(1:ℝ)∂observations true ((),true))=1
  rw [integral_const,probReal_univ,one_smul]

/-- Two genuine probability experiments have the same complete observed pair
law while disagreeing on the never-selected target action. -/
theorem unobserved_joint_law_agreement :
    (neverPolicy ⊗ₖ observations false) ()=(neverPolicy ⊗ₖ observations true) () := by
  ext s hs
  simp only [observations,Kernel.compProd_deterministic_apply _ hs,
    neverPolicy,Kernel.deterministic_apply]
  simp only [Measure.dirac_apply]
  rfl

def responseTest : Unit × Bool → ℝ := fun p => if p.2 then 1 else 0

theorem unobserved_kernel_means_disagree :
    targetMean (observations false) responseTest true ()=0 ∧
    targetMean (observations true) responseTest true ()=1 := by
  simp [targetMean,observations,Kernel.deterministic_apply,responseTest]

noncomputable def halfPolicy : Kernel Unit Bool :=
  Kernel.const Unit (bernoulliMeasure true false ⟨1/2,by constructor <;> norm_num⟩)

instance halfPolicy_markov : IsMarkovKernel halfPolicy := by
  unfold halfPolicy
  infer_instance

theorem half_propensity : propensity halfPolicy true ()=1/2 := by
  norm_num [propensity,halfPolicy,Kernel.const_apply,
    bernoulliMeasure_real_apply _ (measurableSet_singleton true),unitInterval.toNNReal]
  rfl

theorem covered_weight_two : weightedTest halfPolicy oneTest true ((),(true,true))=2 := by
  norm_num [weightedTest,oneTest,half_propensity]

/-- The value two occurs with positive probability in the actual randomized
action/observation experiment; it is not an off-support test point. -/
theorem covered_pair_mass : ((halfPolicy ⊗ₖ observations true) ()).real {(true,true)}=1/2 := by
  unfold Measure.real
  rw [observations,Kernel.compProd_deterministic_apply _ (measurableSet_singleton _)]
  have hs : {b : Bool | (b,if b then true else false)∈({(true,true)} : Set (Bool × Bool))}={true} := by
    ext b
    cases b <;> simp
  rw [hs]
  exact half_propensity

end Komorebi.LSM.CoveredAdaptiveActions.Boundaries
