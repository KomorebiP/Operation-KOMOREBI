import KomorebiLSM.ContinuousBins
import KomorebiLSM.ContinuousRecords
import Mathlib.MeasureTheory.Integral.Prod
import KomorebiLSM.UniformIntervalMoments
import KomorebiLSM.BaseNormModels

/-! Actual pushforwards of continuous record laws under a finite observation
bin map. Binned policies depend on the full observed action/bin history. -/
set_option autoImplicit false
open MeasureTheory
open scoped ENNReal BigOperators

namespace Komorebi.LSM.ContinuousBins

open ContinuousRecords

noncomputable section

universe u v


def historyMap {X : Type u} {Z : Type v} (f : X → Z) : (n : ℕ) → History X n → History Z n
  | 0, _ => PUnit.unit
  | n+1, h => (historyMap f n h.1, f h.2)

def historyList {X : Type u} : (n : ℕ) → History X n → List X
  | 0, _ => []
  | n+1, h => historyList n h.1 ++ [h.2]

theorem historyMap_measurable {X Z : Type*} [MeasurableSpace X] [MeasurableSpace Z]
    (f : X → Z) (hf : Measurable f) : (n : ℕ) → Measurable (historyMap f n)
  | 0 => measurable_const
  | n+1 => ((historyMap_measurable f hf n).comp measurable_fst).prodMk (hf.comp measurable_snd)

instance historyFintype {X : Type*} [Fintype X] : (n : ℕ) → Fintype (History X n)
  | 0 => inferInstanceAs (Fintype PUnit)
  | n+1 => by
    let := historyFintype (X := X) n
    exact inferInstanceAs (Fintype (History X n × X))

instance historySingleton {X : Type*} [MeasurableSpace X] [MeasurableSingletonClass X] :
    (n : ℕ) → MeasurableSingletonClass (History X n)
  | 0 => inferInstanceAs (MeasurableSingletonClass PUnit)
  | n+1 => by
    let := historySingleton (X := X) n
    exact inferInstanceAs (MeasurableSingletonClass (History X n × X))

variable {E A Y I : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
variable [MeasurableSpace I] [Fintype I] [MeasurableSingletonClass I]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y} [IsProbabilityMeasure μ]
variable (D : ContinuousInstrument.DensityInstrument (A := A) C μ)

/-- The bin map records the action without losing it. -/
def binStep (bin : Y → I) (r : A × Y) : A × I := (r.1, bin r.2)

omit [Fintype A] [MeasurableSingletonClass A] [Fintype I] [MeasurableSingletonClass I] in
theorem binStep_measurable (bin : Y → I) (hbin : Measurable bin) :
    Measurable (binStep (A := A) bin) := measurable_fst.prodMk (hbin.comp measurable_snd)

omit [CompleteSpace E] [MeasurableSpace E] [BorelSpace E] in
/-- Joint action/observation operators are integrable under counting actions. -/
theorem jointOperator_integrable :
    Integrable (fun r : A × Y => D.op r.1 r.2) (stepReference (A := A) μ) := by
  apply (integrable_prod_iff (ContinuousRecords.op_measurable D).aestronglyMeasurable).mpr
  constructor
  · exact ae_of_all _ fun a => D.integrable_op a
  · exact Integrable.of_finite

omit [CompleteSpace E] [MeasurableSpace E] [BorelSpace E] in
/-- Literal chronological operator products have genuine Bochner integrals. -/
theorem run_integrable (z : E) : (n : ℕ) →
    Integrable (ContinuousRecords.run D z n) (reference (stepReference (A := A) μ) n)
  | 0 => by
    change Integrable (fun _ : PUnit => z) (Measure.dirac PUnit.unit)
    exact integrable_const _
  | n+1 => by
    exact (run_integrable z n).op_fst_snd (by fun_prop)
      ⟨‖ContinuousLinearMap.apply ℝ E‖, (ContinuousLinearMap.apply ℝ E).le_opNorm₂⟩
      (jointOperator_integrable D)

/-- The complete fine-record fiber of one action/bin record. -/
def binFiber (bin : Y → I) (n : ℕ) (b : History (A × I) n) : Set (History (A × Y) n) :=
  historyMap (binStep bin) n ⁻¹' {b}

omit [Fintype A] [Fintype I] in
theorem binFiber_measurable (bin : Y → I) (hbin : Measurable bin)
    (n : ℕ) (b : History (A × I) n) : MeasurableSet (binFiber bin n b) :=
  (historyMap_measurable _ (binStep_measurable bin hbin) n) (measurableSet_singleton b)

omit [MeasurableSpace Y] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
  [MeasurableSpace I] [Fintype I] [MeasurableSingletonClass I] in
theorem binFiber_succ (bin : Y → I) (n : ℕ) (b : History (A × I) (n+1)) :
    binFiber bin (n+1) b = binFiber bin n b.1 ×ˢ ({b.2.1} ×ˢ (bin ⁻¹' {b.2.2})) := by
  rcases b with ⟨b, a, i⟩
  ext h
  simp only [binFiber, historyMap, binStep, Set.mem_preimage, Set.mem_singleton_iff,
    Set.mem_prod, Prod.mk.injEq]

/-- Unweighted cell operators follow the same chronological product. -/
def binnedRun (bin : Y → I) (z : E) : (n : ℕ) → History (A × I) n → E
  | 0, _ => z
  | n+1, b => cellOperator μ (D.op b.2.1) (bin ⁻¹' {b.2.2}) (binnedRun bin z n b.1)

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace I] [Fintype I] [MeasurableSingletonClass I] in
theorem step_cell_integral (bin : Y → I) (a : A) (i : I) (z : E) :
    (∫ r in ({a} ×ˢ (bin ⁻¹' {i})), D.op r.1 r.2 z ∂stepReference (A := A) μ) =
      cellOperator μ (D.op a) (bin ⁻¹' {i}) z := by
  have hint : IntegrableOn (fun r : A × Y => D.op r.1 r.2 z)
      ({a} ×ˢ (bin ⁻¹' {i})) (stepReference (A := A) μ) :=
    ((ContinuousLinearMap.apply ℝ E z).integrable_comp (jointOperator_integrable D)).integrableOn
  rw [stepReference, setIntegral_prod _ hint]
  simp only [integral_singleton, Measure.real, Measure.count_singleton, ENNReal.toReal_one, one_smul]
  exact (cellOperator_apply μ (D.op a) (D.integrable_op a) _ z).symm

set_option backward.isDefEq.respectTransparency false in
omit [MeasurableSpace E] [BorelSpace E] [Fintype I] [MeasurableSingletonClass I] in
/-- Integrating the actual fine operator product over the complete bin fiber
produces the literal chronological product of integrated cell operators. -/
theorem run_binFiber_integral (bin : Y → I) (hbin : Measurable bin) (z : E) :
    (n : ℕ) → ∀ b : History (A × I) n,
      (∫ h in binFiber bin n b, ContinuousRecords.run D z n h ∂reference (stepReference (A := A) μ) n) =
        binnedRun D bin z n b
  | 0, b => by
    have hb : b = PUnit.unit := Subsingleton.elim _ _
    subst b
    simp [binFiber, historyMap, reference, ContinuousRecords.run, binnedRun]
  | n+1, b => by
    rw [binFiber_succ, reference, setIntegral_prod _ (run_integrable D z (n+1)).integrableOn]
    change (∫ h in binFiber bin n b.1, ∫ r in ({b.2.1} ×ˢ (bin ⁻¹' {b.2.2})),
      D.op r.1 r.2 (ContinuousRecords.run D z n h) ∂stepReference (A := A) μ
      ∂reference (stepReference (A := A) μ) n) = _
    simp_rw [step_cell_integral D bin]
    rw [(cellOperator μ (D.op b.2.1) (bin ⁻¹' {b.2.2})).integral_comp_comm
      (run_integrable D z n).integrableOn, run_binFiber_integral bin hbin z n b.1]
    rfl

/-- A real finite-action policy on exactly the observed bin history. -/
def binWeight (π : List (A × I) → A → ℝ) : (n : ℕ) → History (A × I) n → ℝ
  | 0, _ => 1
  | n+1, b => binWeight π n b.1 * π (historyList n b.1) b.2.1

omit [MeasurableSpace A] [MeasurableSingletonClass A] [MeasurableSpace I] [Fintype I]
  [MeasurableSingletonClass I] in
theorem binWeight_nonneg (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h)) :
    (n : ℕ) → ∀ b : History (A × I) n, 0 ≤ binWeight π n b
  | 0, _ => by norm_num [binWeight]
  | n+1, b => mul_nonneg (binWeight_nonneg π hπ n b.1) ((hπ _).1 _)

/-- The fine policy reads only the measurable bin record. -/
def liftedBinPolicy (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h)) :
    ContinuousRecords.Policy (A := A) (Y := Y) where
  probability n h a := ENNReal.ofReal (π (historyList n (historyMap (binStep bin) n h)) a)
  measurable_probability n a := by
    have hm : Measurable (fun b : History (A × I) n => ENNReal.ofReal (π (historyList n b) a)) :=
      Measurable.of_discrete
    exact hm.comp (historyMap_measurable _ (binStep_measurable bin hbin) n)
  sum_one n h := by
    rw [← ENNReal.ofReal_sum_of_nonneg (fun a _ => (hπ _).1 a), (hπ _).2, ENNReal.ofReal_one]

theorem liftedBinPolicy_weight (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h)) :
    (n : ℕ) → ∀ h : History (A × Y) n,
      (liftedBinPolicy bin hbin π hπ).weight n h = ENNReal.ofReal (binWeight π n (historyMap (binStep bin) n h))
  | 0, _ => by simp [ContinuousRecords.Policy.weight, binWeight]
  | n+1, h => by
    change (liftedBinPolicy bin hbin π hπ).weight n h.1 *
      ENNReal.ofReal (π (historyList n (historyMap (binStep bin) n h.1)) h.2.1) =
      ENNReal.ofReal (binWeight π n (historyMap (binStep bin) n h.1) *
        π (historyList n (historyMap (binStep bin) n h.1)) h.2.1)
    rw [liftedBinPolicy_weight bin hbin π hπ n h.1,
      ENNReal.ofReal_mul (binWeight_nonneg π hπ n _)]

/-- The actual finite model uses integrated cell operators with the same policy. -/
def binnedBranches (bin : Y → I) (π : List (A × I) → A → ℝ)
    (h : List (A × I)) (s : A × I) : E →ₗ[ℝ] E :=
  π h s.1 • (cellOperator μ (D.op s.1) (bin ⁻¹' {s.2})).toLinearMap

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A]
  [Fintype A] [MeasurableSingletonClass A] in
theorem bin_cell_instrument (bin : Y → I) (hbin : Measurable bin) (a : A) :
    C.Instrument (fun i => (cellOperator μ (D.op a) (bin ⁻¹' {i})).toLinearMap) := by
  apply cellInstrument C μ (D.op a) (D.integrable_op a) (D.positive a) (D.mass_preserving a)
    (fun i => bin ⁻¹' {i}) (fun i => hbin (measurableSet_singleton i))
  · intro i j hij
    apply Set.disjoint_left.mpr
    intro y hi hj
    apply hij
    exact hi.symm.trans hj
  · ext y
    simp

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A]
  [MeasurableSingletonClass A] in
theorem binnedBranches_instrument (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h)) (h : List (A × I)) :
    C.Instrument (binnedBranches D bin π h) := by
  exact ObservationTree.policy_instrument C π hπ
    (fun _ s => (cellOperator μ (D.op s.1) (bin ⁻¹' {s.2})).toLinearMap)
    (fun _ a => bin_cell_instrument D bin hbin a) h

def weightedBinnedRun (bin : Y → I) (π : List (A × I) → A → ℝ) (z : E) :
    (n : ℕ) → History (A × I) n → E
  | 0, _ => z
  | n+1, b => binnedBranches D bin π (historyList n b.1) b.2 (weightedBinnedRun bin π z n b.1)

omit [CompleteSpace E] [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [MeasurableSpace I] [Fintype I]
  [MeasurableSingletonClass I] [IsProbabilityMeasure μ] in
theorem weightedBinnedRun_factor (bin : Y → I) (π : List (A × I) → A → ℝ) (z : E) :
    (n : ℕ) → ∀ b : History (A × I) n,
      weightedBinnedRun D bin π z n b = binWeight π n b • binnedRun D bin z n b
  | 0, _ => by simp [weightedBinnedRun, binWeight, binnedRun]
  | n+1, b => by
    simp only [weightedBinnedRun, binnedBranches, weightedBinnedRun_factor bin π z n b.1,
      LinearMap.smul_apply, ContinuousLinearMap.coe_coe, map_smul, smul_smul, binWeight, binnedRun]

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A]
  [MeasurableSingletonClass A] in
theorem weightedBinnedRun_mem (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (z : E) (hz : z ∈ C.carrier) : (n : ℕ) → ∀ b : History (A × I) n,
      weightedBinnedRun D bin π z n b ∈ C.carrier
  | 0, _ => hz
  | n+1, b => (binnedBranches_instrument D bin hbin π hπ _).1 b.2 _
      (weightedBinnedRun_mem bin hbin π hπ z hz n b.1)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A]
  [MeasurableSingletonClass A] in
theorem weightedBinnedRun_mass (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h)) (z : E) :
    (n : ℕ) → (∑ b : History (A × I) n, C.mass (weightedBinnedRun D bin π z n b)) = C.mass z
  | 0 => by change (∑ _ : PUnit, C.mass z) = _; simp
  | n+1 => by
    change (∑ b : History (A × I) n × (A × I), C.mass
      (binnedBranches D bin π (historyList n b.1) b.2 (weightedBinnedRun D bin π z n b.1))) = _
    rw [Fintype.sum_prod_type]
    simp_rw [(binnedBranches_instrument D bin hbin π hπ _).2]
    exact weightedBinnedRun_mass bin hbin π hπ z n

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A]
  [MeasurableSingletonClass A] in
/-- The finite cell-model record distribution is a prior at every horizon. -/
theorem binned_record_prior (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (z : E) (hz : z ∈ C.base) (n : ℕ) :
    FiniteBayes.IsPrior (fun b : History (A × I) n => C.mass (weightedBinnedRun D bin π z n b)) :=
  ⟨fun b => C.mass_nonneg (weightedBinnedRun_mem D bin hbin π hπ z hz.1 n b),
    (weightedBinnedRun_mass D bin hbin π hπ z n).trans hz.2⟩

/-- An actual measure associated to that finite instrument's prior. -/
def finiteBinnedLaw (bin : Y → I) (π : List (A × I) → A → ℝ) (z : E) (n : ℕ) :
    Measure (History (A × I) n) :=
  Measure.count.withDensity (fun b => ENNReal.ofReal (C.mass (weightedBinnedRun D bin π z n b)))

omit [CompleteSpace E] [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [Fintype A] [Fintype I] [IsProbabilityMeasure μ] in
theorem finiteBinnedLaw_singleton (bin : Y → I) (π : List (A × I) → A → ℝ) (z : E)
    (n : ℕ) (b : History (A × I) n) :
    finiteBinnedLaw D bin π z n {b} = ENNReal.ofReal (C.mass (weightedBinnedRun D bin π z n b)) := by
  rw [finiteBinnedLaw, withDensity_apply _ (measurableSet_singleton b), lintegral_singleton]
  simp

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
theorem finiteBinnedLaw_probability (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (z : E) (hz : z ∈ C.base) (n : ℕ) : IsProbabilityMeasure (finiteBinnedLaw D bin π z n) := by
  constructor
  rw [finiteBinnedLaw, withDensity_apply _ MeasurableSet.univ, Measure.restrict_univ,
    lintegral_count, tsum_fintype, ← ENNReal.ofReal_sum_of_nonneg
      (fun b _ => (binned_record_prior D bin hbin π hπ z hz n).1 b),
    (binned_record_prior D bin hbin π hπ z hz n).2, ENNReal.ofReal_one]

omit [Fintype I] [MeasurableSingletonClass I] in
/-- The actual nonnegative record density integrated over one bin fiber. -/
theorem mass_run_binFiber_lintegral (bin : Y → I) (hbin : Measurable bin)
    (z : E) (hz : z ∈ C.carrier) (n : ℕ) (b : History (A × I) n) :
    (∫⁻ h in binFiber bin n b, ENNReal.ofReal (C.mass (ContinuousRecords.run D z n h))
      ∂reference (stepReference (A := A) μ) n) = ENNReal.ofReal (C.mass (binnedRun D bin z n b)) := by
  have hint : Integrable (fun h => C.mass (ContinuousRecords.run D z n h))
      (reference (stepReference (A := A) μ) n) :=
    (ContinuousInstrument.massCLM C).integrable_comp (run_integrable D z n)
  rw [← ofReal_integral_eq_lintegral_ofReal hint.integrableOn
    (ae_restrict_of_ae ((ContinuousRecords.run_mem_ae D hz n).mono fun _ hh => C.mass_nonneg hh))]
  congr 1
  exact ((ContinuousInstrument.massCLM C).integral_comp_comm (run_integrable D z n).integrableOn).trans
    (congrArg (ContinuousInstrument.massCLM C) (run_binFiber_integral D bin hbin z n b))

/-- The probability of every complete binned record is exactly the finite
integrated-cell model's probability, including the action-policy factors. -/
theorem binned_recordLaw_singleton (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (z : E) (hz : z ∈ C.carrier) (n : ℕ) (b : History (A × I) n) :
    ((ContinuousRecords.recordLaw D (liftedBinPolicy bin hbin π hπ) z n).map
      (historyMap (binStep bin) n)) {b} = finiteBinnedLaw D bin π z n {b} := by
  rw [Measure.map_apply (historyMap_measurable _ (binStep_measurable bin hbin) n)
    (measurableSet_singleton b), finiteBinnedLaw_singleton]
  change ContinuousRecords.recordLaw D (liftedBinPolicy bin hbin π hπ) z n (binFiber bin n b) = _
  rw [ContinuousRecords.recordLaw_event _ _ _ _ _ (binFiber_measurable bin hbin n b)]
  have hweight : ∀ᵐ h ∂(reference (stepReference (A := A) μ) n).restrict (binFiber bin n b),
      (liftedBinPolicy bin hbin π hπ).weight n h = ENNReal.ofReal (binWeight π n b) := by
    filter_upwards [ae_restrict_mem (binFiber_measurable bin hbin n b)] with h hh
    rw [liftedBinPolicy_weight]
    exact congrArg (fun q => ENNReal.ofReal (binWeight π n q)) hh
  calc
    _ = ∫⁻ h in binFiber bin n b, ENNReal.ofReal (binWeight π n b) *
        ENNReal.ofReal (C.mass (ContinuousRecords.run D z n h))
        ∂reference (stepReference (A := A) μ) n := by
      apply lintegral_congr_ae
      filter_upwards [hweight] with h hh
      exact congrArg (fun w => w * ENNReal.ofReal (C.mass (ContinuousRecords.run D z n h))) hh
    _ = ENNReal.ofReal (binWeight π n b) *
        ∫⁻ h in binFiber bin n b, ENNReal.ofReal (C.mass (ContinuousRecords.run D z n h))
          ∂reference (stepReference (A := A) μ) n := by
      apply lintegral_const_mul
      exact ((ContinuousInstrument.massCLM C).continuous.measurable.comp
        (ContinuousRecords.run_measurable D z n)).ennreal_ofReal
    _ = ENNReal.ofReal (binWeight π n b) * ENNReal.ofReal (C.mass (binnedRun D bin z n b)) := by
      rw [mass_run_binFiber_lintegral D bin hbin z hz n b]
    _ = _ := by
      rw [weightedBinnedRun_factor, map_smul, smul_eq_mul,
        ENNReal.ofReal_mul (binWeight_nonneg π hπ n b)]

/-- P56's equality of actual measures at every horizon. The continuous policy
is allowed to depend on the entire action/bin history and only that history. -/
theorem actual_binned_recordLaw (bin : Y → I) (hbin : Measurable bin)
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (z : E) (hz : z ∈ C.carrier) (n : ℕ) :
    (ContinuousRecords.recordLaw D (liftedBinPolicy bin hbin π hπ) z n).map
      (historyMap (binStep bin) n) = finiteBinnedLaw D bin π z n := by
  apply Measure.ext_of_singleton
  intro b
  exact binned_recordLaw_singleton D bin hbin π hπ z hz n b

/-- A covering partition supplies a literal bin map, without assuming one. -/
def partitionBin (S : I → Set Y) (hcover : ⋃ i, S i = Set.univ) (y : Y) : I :=
  Classical.choose (show ∃ i, y ∈ S i from Set.mem_iUnion.mp (hcover.symm ▸ Set.mem_univ y))

omit [MeasurableSpace Y] [MeasurableSpace I] [Fintype I] [MeasurableSingletonClass I] in
theorem partitionBin_mem (S : I → Set Y) (hcover : ⋃ i, S i = Set.univ) (y : Y) :
    y ∈ S (partitionBin S hcover y) :=
  Classical.choose_spec (show ∃ i, y ∈ S i from Set.mem_iUnion.mp (hcover.symm ▸ Set.mem_univ y))

omit [MeasurableSpace Y] [MeasurableSpace I] [Fintype I] [MeasurableSingletonClass I] in
theorem partitionBin_fiber (S : I → Set Y) (hcover : ⋃ i, S i = Set.univ)
    (hdis : Pairwise (fun i j => Disjoint (S i) (S j))) (i : I) :
    partitionBin S hcover ⁻¹' {i} = S i := by
  ext y
  constructor
  · intro hy
    exact hy ▸ partitionBin_mem S hcover y
  · intro hy
    change partitionBin S hcover y = i
    by_contra hne
    exact Set.disjoint_left.mp (hdis hne) (partitionBin_mem S hcover y) hy

omit [MeasurableSingletonClass I] in
theorem partitionBin_measurable (S : I → Set Y) (hcover : ⋃ i, S i = Set.univ)
    (hdis : Pairwise (fun i j => Disjoint (S i) (S j))) (hS : ∀ i, MeasurableSet (S i)) :
    Measurable (partitionBin S hcover) := by
  apply measurable_to_countable
  intro y
  rw [partitionBin_fiber S hcover hdis]
  exact hS _

/-- P56 for any finite measurable partition: the constructed measurable map has
exactly those cells and pushes the actual law to the finite integrated model. -/
theorem exact_partition_coarsening (S : I → Set Y) (hcover : ⋃ i, S i = Set.univ)
    (hdis : Pairwise (fun i j => Disjoint (S i) (S j))) (hS : ∀ i, MeasurableSet (S i))
    (π : List (A × I) → A → ℝ) (hπ : ∀ h, FiniteBayes.IsPrior (π h))
    (z : E) (hz : z ∈ C.base) (n : ℕ) :
    (∀ i, partitionBin S hcover ⁻¹' {i} = S i) ∧
    (∀ h, C.Instrument (binnedBranches D (partitionBin S hcover) π h)) ∧
    FiniteBayes.IsPrior (fun b : History (A × I) n =>
      C.mass (weightedBinnedRun D (partitionBin S hcover) π z n b)) ∧
    (ContinuousRecords.recordLaw D
      (liftedBinPolicy (partitionBin S hcover) (partitionBin_measurable S hcover hdis hS) π hπ) z n).map
        (historyMap (binStep (partitionBin S hcover)) n) =
          finiteBinnedLaw D (partitionBin S hcover) π z n := by
  refine ⟨partitionBin_fiber S hcover hdis, ?_, ?_, ?_⟩
  · exact binnedBranches_instrument D _ (partitionBin_measurable S hcover hdis hS) π hπ
  · exact binned_record_prior D _ (partitionBin_measurable S hcover hdis hS) π hπ z hz n
  · exact actual_binned_recordLaw D _ (partitionBin_measurable S hcover hdis hS) π hπ z hz.1 n

omit [CompleteSpace E] [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] [MeasurableSpace I] [Fintype I]
  [MeasurableSingletonClass I] [IsProbabilityMeasure μ] in
/-- A bin-history policy factor commutes with exact cell integration. -/
theorem policy_density_cell (π : List (A × I) → A → ℝ) (h : List (A × I)) (a : A)
    (S : Set Y) :
    cellOperator μ (fun y => π h a • D.op a y) S = π h a • cellOperator μ (D.op a) S := by
  exact integral_smul _ _

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A]
  [Fintype A] [MeasurableSingletonClass A] [MeasurableSpace I] [Fintype I]
  [MeasurableSingletonClass I] [IsProbabilityMeasure μ] in
/-- The earlier chronological repeated-integral theorem instantiated with the
literal policy-weighted density is the actual finite cell branch model. -/
theorem policy_iterated_record_probability (bin : Y → I)
    (π : List (A × I) → A → ℝ) (n : ℕ) (h : List (A × I)) (z : E)
    (w : ObservationTree.Record (A × I) n) :
    C.mass (iteratedCellVector μ (fun h a y => π h a • D.op a y)
      (fun i => bin ⁻¹' {i}) h (ObservationTree.recordList w) z) =
        ObservationTree.recordLaw C (binnedBranches D bin π) n h z w := by
  have hB : ∀ h a, Integrable (fun y => π h a • D.op a y) μ :=
    fun h a => Integrable.smul (π h a) (D.integrable_op a)
  have heq : (fun h (s : A × I) =>
      (cellOperator μ (fun y => π h s.1 • D.op s.1 y) (bin ⁻¹' {s.2})).toLinearMap) =
        binnedBranches D bin π := by
    funext h s
    rw [policy_density_cell]
    rfl
  rw [iterated_cell_record_probability C μ _ hB, heq]

namespace QuadraticExample

def op (u : ℝ) : ℝ →L[ℝ] ℝ := (3 * u^2) • ContinuousLinearMap.id ℝ ℝ

theorem op_integrable : Integrable op UniformIntervalMoments.measure :=
  (UniformIntervalMoments.continuous_integrable (by fun_prop : Continuous (fun u : ℝ => 3 * u^2))).smul_const _

/-- A valid normalized scalar density that vanishes at the bin midpoint. -/
def instrument : ContinuousInstrument.DensityInstrument (A := Unit)
    BaseNorm.scalarCone UniformIntervalMoments.measure where
  op _ := op
  measurable_op _ := by unfold op; fun_prop
  integrable_op _ := op_integrable
  positive _ := ae_of_all _ fun u z hz => mul_nonneg (by positivity : 0 ≤ 3 * u^2) hz
  mass_preserving _ z := by
    rw [ContinuousLinearMap.integral_apply op_integrable z]
    change (∫ u, (3 * u^2) * z ∂UniformIntervalMoments.measure) = z
    rw [integral_mul_const, integral_const_mul]
    change 3 * UniformIntervalMoments.moment 2 * z = z
    rw [UniformIntervalMoments.moment_two]
    ring

theorem full_cell : cellOperator UniformIntervalMoments.measure (instrument.op ()) Set.univ 1 = 1 := by
  rw [cellOperator, Measure.restrict_univ]
  exact instrument.mass_preserving () 1

theorem midpoint : instrument.op () 0 1 = 0 := by norm_num [instrument, op]

theorem integrated_cell_ne_point_sample :
    cellOperator UniformIntervalMoments.measure (instrument.op ()) Set.univ 1 ≠ instrument.op () 0 1 := by
  rw [full_cell, midpoint]
  norm_num

end QuadraticExample

end
end Komorebi.LSM.ContinuousBins
