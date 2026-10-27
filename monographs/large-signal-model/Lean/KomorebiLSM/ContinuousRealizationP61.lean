import KomorebiLSM.ContinuousPopulationBridge
import KomorebiLSM.ContinuousBinnedRecords
import KomorebiLSM.PositiveCellP58
import KomorebiLSM.ContinuousTV
import KomorebiLSM.PositivePackets

/-! P61: the same population-reconstructed polynomial coefficients are used
by the finite matrix/Gram instrument, exact coordinate and packet identities,
bin-history event model, positive cell approximation and common-policy budget.
Dimension, degree, initial admissibility and approximation inputs stay explicit. -/
set_option autoImplicit false
namespace Komorebi.LSM.ContinuousRealizationP61
open ContinuousPopulationBridge MeasureTheory ProbabilityTheory
open scoped BigOperators Matrix

variable {r degree : ℕ} {A D R : Type*}
variable [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
variable [Fintype D] [DecidableEq D] [Fintype R]

/-- The instrument uses the actual inverse-moment fitted coefficients, not
an unrelated model supplied alongside the population reconstruction. -/
noncomputable def realizedInstrument (T S : Operator r)
    (C : A → Fin (degree+1) → Operator r)
    (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
    {q bound : ℕ}
    (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J
      (fittedCoefficients T S C) q bound) :
    ContinuousInstrument.DensityInstrument (A := A) M.coneInstance UniformIntervalMoments.measure :=
  PolynomialGramP53.instrument M b (fittedCoefficients T S C) W

/-- The mass-row equality is the checked coordinate readout identity. Exact
population reconstruction and the independent finite Gram witness then give
the full represented density and actual all-horizon probability laws. -/
theorem population_realization_certificate (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r)
    (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
    {q bound : ℕ}
    (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J
      (fittedCoefficients T S C) q bound)
    (l : State r →ₗ[ℝ] ℝ) (hmass : M.mass.comp T.mulVecLin=l)
    (z₀ : State r) (hinitial : (M.J (T *ᵥ z₀)).PosSemidef ∧ M.mass (T *ᵥ z₀)=1) :
    let I := realizedInstrument T S C M b W
    (∀ a k,fittedCoefficients T S C a k=matrixCLM (T * C a k * T⁻¹)) ∧
    (∀ a u x,I.op a u x=(T * FiniteMomentIdentification.density (C a) u * T⁻¹) *ᵥ x) ∧
    (∀ word : List (A × ℝ),M.mass (FiniteInstruments.wordAction
      (fun s : A × ℝ => (I.op s.1 s.2).toLinearMap) word (T *ᵥ z₀))=
        l (FiniteMomentIdentification.wordState (fun a => FiniteMomentIdentification.density (C a)) word z₀)) ∧
    l z₀=1 ∧
    (∀ a u,u∈Set.Icc (-1 : ℝ) 1 → ∀ x∈M.cone,I.op a u x∈M.cone) ∧
    (∀ a,IsMarkovKernel (I.kernel a)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ N,
      IsProbabilityMeasure (ContinuousRecords.recordLaw I π (T *ᵥ z₀) N)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ N,
      (ContinuousRecords.recordLaw I π (T *ᵥ z₀) (N+1)).fst=
        ContinuousRecords.recordLaw I π (T *ᵥ z₀) N) ∧
    (∀ actions : ℕ → A,∀ N,
      IsProbabilityMeasure (ContinuousRecords.observationLaw I actions (T *ᵥ z₀) N)) ∧
    (∀ actions : ℕ → A,∀ N (event : Set (ContinuousRecords.History ℝ N)),MeasurableSet event →
      ContinuousRecords.observationLaw I actions (T *ᵥ z₀) N event=
        ∫⁻ h in event,ENNReal.ofReal (M.mass (ContinuousRecords.observationRun I actions (T *ᵥ z₀) N h))
          ∂ContinuousRecords.reference UniformIntervalMoments.measure N) := by
  dsimp only
  let I := realizedInstrument T S C M b W
  have hb : T *ᵥ z₀∈M.coneInstance.base := hinitial
  refine ⟨fitted_coefficient_identification T S hcore C,?_,?_,?_,?_,?_,?_,?_,?_,?_⟩
  · intro a u x
    change PolynomialGram.operatorPolynomial (fittedCoefficients T S C a) u x=_
    rw [fitted_density_identification T S hcore,matrixCLM_apply]
  · intro word
    exact fitted_word_likelihood T S hcore C l M.mass hmass word z₀
  · have he := congrArg (fun L : State r →ₗ[ℝ] ℝ => L z₀) hmass
    exact he.symm.trans hinitial.2
  · intro a u hu x hx
    exact W.positive a u hu x hx
  · intro a
    infer_instance
  · intro π N
    exact ContinuousRecords.recordLaw_probability I π ⟨T *ᵥ z₀,hb⟩ N
  · intro π N
    exact ContinuousRecords.recordLaw_consistent I π hb.1 N
  · intro actions N
    exact ContinuousRecords.observationLaw_probability I actions ⟨T *ᵥ z₀,hb⟩ N
  · intro actions N event hEvent
    exact ContinuousRecords.observationLaw_product_density I actions (T *ᵥ z₀) N event hEvent

section OriginalCoordinates

/-- Transporting the independently checked fitted certificate back by the
population-derived inverse atlas constructs an instrument with the literal
original coefficient family. It is not an assumed generating-law equality. -/
noncomputable def originalInstrument (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r)
    (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
    {q bound : ℕ}
    (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J (fittedCoefficients T S C) q bound) :
    ContinuousInstrument.DensityInstrument (A := A)
      (M.transport (populationEquiv T S hcore).symm).coneInstance UniformIntervalMoments.measure :=
  CertifiedTemplate.fittedInstrument M b (fittedCoefficients T S C) (originalCoefficients C) W
    (populationEquiv T S hcore).symm (population_inverse_coefficient_match T S hcore C)

omit [MeasurableSpace A] [MeasurableSingletonClass A] in
theorem original_instrument_op (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r)
    (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
    {q bound : ℕ}
    (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J (fittedCoefficients T S C) q bound)
    (a : A) (u : ℝ) (x : State r) :
    (originalInstrument T S hcore C M b W).op a u x=
      FiniteMomentIdentification.density (C a) u *ᵥ x := by
  change PolynomialGram.operatorPolynomial (fun k => matrixCLM (C a k)) u x=_
  rw [polynomial_matrix_density,matrixCLM_apply]

omit [DecidableEq D] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A] in
theorem original_instrument_mass (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (M : MatrixEmbedding.Embedding (State r) D)
    (l : State r →ₗ[ℝ] ℝ) (hmass : M.mass.comp T.mulVecLin=l) :
    (M.transport (populationEquiv T S hcore).symm).mass=l := by
  apply LinearMap.ext
  intro x
  change M.mass (T *ᵥ x)=l x
  exact congrArg (fun L : State r →ₗ[ℝ] ℝ => L x) hmass

omit [MeasurableSingletonClass A] in
/-- The complete actual record measures of the original declared polynomial
family and the certified reconstructed family coincide in their own atlases. -/
theorem population_record_law (T S : Operator r)
    (hcore : IsUnit (FiniteMomentIdentification.populationCore T S))
    (C : A → Fin (degree+1) → Operator r)
    (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
    {q bound : ℕ}
    (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J (fittedCoefficients T S C) q bound)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) (z₀ : State r) (N : ℕ) :
    ContinuousRecords.recordLaw (originalInstrument T S hcore C M b W) π z₀ N=
      ContinuousRecords.recordLaw (realizedInstrument T S C M b W) π (T *ᵥ z₀) N := by
  have h := CertifiedTemplate.record_law_transport M b (fittedCoefficients T S C)
    (originalCoefficients C) W (populationEquiv T S hcore).symm
    (population_inverse_coefficient_match T S hcore C) π (populationEquiv T S hcore z₀) N
  rw [LinearEquiv.symm_apply_apply] at h
  simpa only [originalInstrument,realizedInstrument,populationEquiv_apply] using h

end OriginalCoordinates

section Template
variable (T S : Operator r) (C : A → Fin (degree+1) → Operator r)
variable (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
variable (template : A → Fin (degree+1) → State r →L[ℝ] State r)
variable {q bound : ℕ} (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J template q bound)
variable (U : State r ≃ₗ[ℝ] State r) (lhat : State r →ₗ[ℝ] ℝ)
variable (hm : CertifiedTemplate.Matches
  (fun s : A × Fin (degree+1) => (template s.1 s.2).toLinearMap)
  (fun s : A × Fin (degree+1) => (fittedCoefficients T S C s.1 s.2).toLinearMap)
  M.mass lhat U.toLinearMap)

/-- A successful fixed-template linear match constructs a finite certificate
for precisely the population-fitted coefficient family used above. -/
noncomputable def recognizedPopulationCertificate :
    PolynomialGram.CoefficientCertificate (b.map U) (M.transport U).coneInstance (M.transport U).J
      (fittedCoefficients T S C) q bound :=
  CertifiedTemplate.transportedCertificate M b template (fittedCoefficients T S C) W U
    (fun a k x => hm.coefficient_apply (a,k) x)

/-- The matching constructor keeps the independent initial-state test. The
same population initial test vector is used in the actual fitted law. -/
theorem recognized_population_probability (z₀ : State r)
    (hinitial : (M.J (U.symm (T *ᵥ z₀))).PosSemidef ∧ lhat (T *ᵥ z₀)=1)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) (N : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw
      (realizedInstrument T S C (M.transport U) (b.map U)
        (recognizedPopulationCertificate T S C M b template W U lhat hm)) π (T *ᵥ z₀) N) :=
  CertifiedTemplate.fitted_record_probability M b template (fittedCoefficients T S C) W U
    (fun a k x => hm.coefficient_apply (a,k) x) lhat hm.2 (T *ᵥ z₀) hinitial π N

end Template

section Atlas

/-- Exact atlas transport is defined by conjugation of the actual fitted
coefficients; no all-word or event-law equality is a hypothesis. -/
noncomputable def atlasCoefficients {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    [FiniteDimensional ℝ E] {n : ℕ} (U : E ≃ₗ[ℝ] E)
    (B : A → Fin n → E →L[ℝ] E) (a : A) (k : Fin n) : E →L[ℝ] E :=
  U.toContinuousLinearEquiv.toContinuousLinearMap.comp
    ((B a k).comp U.symm.toContinuousLinearEquiv.toContinuousLinearMap)

omit [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A] in
theorem atlas_coefficient_match {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    [FiniteDimensional ℝ E] {n : ℕ} (U : E ≃ₗ[ℝ] E)
    (B : A → Fin n → E →L[ℝ] E) (a : A) (k : Fin n) (x : E) :
    atlasCoefficients U B a k (U x)=U (B a k x) := by
  simp [atlasCoefficients]

omit [MeasurableSingletonClass A] in
/-- The actual full common-policy event measures are invariant under an exact
atlas. The transported finite Gram certificate is constructed by P60. -/
theorem population_atlas_law (T S : Operator r)
    (C : A → Fin (degree+1) → Operator r)
    (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
    {q bound : ℕ}
    (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J (fittedCoefficients T S C) q bound)
    (U : State r ≃ₗ[ℝ] State r) (π : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z₀ : State r) (N : ℕ) :
    ContinuousRecords.recordLaw
      (CertifiedTemplate.fittedInstrument M b (fittedCoefficients T S C)
        (atlasCoefficients U (fittedCoefficients T S C)) W U
        (atlas_coefficient_match U (fittedCoefficients T S C))) π (U (T *ᵥ z₀)) N=
      ContinuousRecords.recordLaw (realizedInstrument T S C M b W) π (T *ᵥ z₀) N :=
  CertifiedTemplate.record_law_transport M b (fittedCoefficients T S C)
    (atlasCoefficients U (fittedCoefficients T S C)) W U
    (atlas_coefficient_match U (fittedCoefficients T S C)) π (T *ᵥ z₀) N

end Atlas

section CertifiedConsequences
variable (T S : Operator r) (C : A → Fin (degree+1) → Operator r)
variable (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
variable {q bound : ℕ}
variable (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J (fittedCoefficients T S C) q bound)
local notation "I₀" => realizedInstrument T S C M b W

omit [MeasurableSingletonClass A] in
/-- Complete synthesis preserves the actual event measure. Signed component
packets are allowed here, without being assigned individual probability laws. -/
theorem complete_packet_law {K : Type*} [Fintype K]
    (P : K → State r →ₗ[ℝ] State r) (hP : ∑ k,P k=LinearMap.id)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) (z₀ : State r) (N : ℕ) :
    ContinuousRecords.recordLaw I₀ π (∑ k,P k (T *ᵥ z₀)) N=
      ContinuousRecords.recordLaw I₀ π (T *ᵥ z₀) N := by
  have hs : ∑ k,P k (T *ᵥ z₀)=T *ᵥ z₀ := by
    simpa only [LinearMap.sum_apply,LinearMap.id_apply] using
      congrArg (fun L : State r →ₗ[ℝ] State r => L (T *ᵥ z₀)) hP
  rw [hs]

omit [DecidableEq D] in
/-- Individual normalized packets require their own positivity and positive
mass. The complete synthesis identity alone is not used as a positivity proof. -/
theorem positive_packet_state (P : State r →ₗ[ℝ] State r)
    (hpositive : ∀ x∈M.cone,P x∈M.cone) (z₀ : State r)
    (hinitial : (M.J (T *ᵥ z₀)).PosSemidef ∧ M.mass (T *ᵥ z₀)=1)
    (hmass : 0<M.mass (P (T *ᵥ z₀))) :
    (M.mass (P (T *ᵥ z₀)))⁻¹ • P (T *ᵥ z₀)∈M.coneInstance.base :=
  PositivePackets.normalized_packet M.coneInstance.carrier
    (fun _ ha _ hx => M.coneInstance.smul_mem ha hx) M.mass P hpositive
    (T *ᵥ z₀) hinitial.1 hmass

/-- The exact finite event model is the literal bin pushforward under any
policy depending on the full action/bin history. The partition map is built
from the supplied measurable covering cells rather than assumed as a law. -/
theorem exact_population_bins {J : Type*} [MeasurableSpace J] [Fintype J]
    [MeasurableSingletonClass J] (cells : J → Set ℝ)
    (hcover : ⋃ j,cells j=Set.univ)
    (hdisjoint : Pairwise (fun i j => Disjoint (cells i) (cells j)))
    (hmeas : ∀ j,MeasurableSet (cells j))
    (π : List (A × J) → A → ℝ) (hπ : ∀ h,FiniteBayes.IsPrior (π h))
    (z₀ : State r) (hinitial : (M.J (T *ᵥ z₀)).PosSemidef ∧ M.mass (T *ᵥ z₀)=1) (N : ℕ) :
    let bin := ContinuousBins.partitionBin cells hcover
    (∀ j,bin ⁻¹' {j}=cells j) ∧
    (ContinuousRecords.recordLaw I₀
      (ContinuousBins.liftedBinPolicy bin
        (ContinuousBins.partitionBin_measurable cells hcover hdisjoint hmeas) π hπ) (T *ᵥ z₀) N).map
          (ContinuousBins.historyMap (ContinuousBins.binStep bin) N)=
            ContinuousBins.finiteBinnedLaw I₀ bin π (T *ᵥ z₀) N := by
  dsimp only
  have hb : T *ᵥ z₀∈M.coneInstance.base := hinitial
  have he := ContinuousBins.exact_partition_coarsening I₀ cells hcover hdisjoint hmeas π hπ
    (T *ᵥ z₀) hb N
  exact ⟨he.1,he.2.2.2⟩

omit [MeasurableSpace A] [MeasurableSingletonClass A] in
/-- The positive cell approximation is built from this same fitted instrument
on the same cone/reference. Its averaging and resolution bound are derived. -/
theorem population_cell_resolution {J : Type*} [Fintype J]
    (P : PositiveCellApproximation.CellPartition UniformIntervalMoments.measure J)
    (L h : ℝ) (hL : 0≤L) (hh : 0≤h)
    (hLip : PositiveCellApproximation.CellLipschitz I₀ P L)
    (hDiameter : PositiveCellApproximation.CellDiameter P h) :
    let K := PositiveCellApproximation.instrument I₀ P
    (∀ a y x,x∈M.cone → K.op a y x∈M.cone) ∧
    (∀ a x,M.mass ((∫ y,K.op a y∂UniformIntervalMoments.measure) x)=M.mass x) ∧
    (∀ a j,ContinuousBins.cellOperator UniformIntervalMoments.measure (K.op a) (P.cell j)=
      ContinuousBins.cellOperator UniformIntervalMoments.measure ((I₀).op a) (P.cell j)) ∧
    (∀ a,IsMarkovKernel (K.kernel a)) ∧ PositiveCellApproximation.approximationError I₀ P≤L*h :=
  PositiveCellApproximation.positive_cell_average_certificate I₀ P L h hL hh hLip hDiameter

omit [MeasurableSpace A] [MeasurableSingletonClass A] in
/-- The sharper uniform-interval estimate also concerns the very same actual
fitted density, with its genuine induced base norm and actual interval cells. -/
theorem population_equal_interval_resolution {J : Type*} [Fintype J]
    (P : PositiveCellApproximation.CellPartition UniformIntervalMoments.measure J)
    (left right : J → ℝ) (L h : ℝ) (hL : 0≤L) (hh : 0<h)
    (hcells : ∀ j,P.cell j=Set.Ioc (left j) (right j))
    (hleft : ∀ j,-1≤left j) (hright : ∀ j,right j≤1) (hwidth : ∀ j,right j-left j=h)
    (hLip : ∀ a,∀ y∈Set.Icc (-1 : ℝ) 1,∀ v∈Set.Icc (-1 : ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := M.coneInstance) ((I₀).op a y-(I₀).op a v)≤L*dist y v) :
    PositiveCellApproximation.approximationError I₀ P≤L*h/3 :=
  (PositiveCellApproximation.positive_equal_interval_certificate I₀ P left right L h hL hh
    hcells hleft hright hwidth hLip).2.2.2.2

end CertifiedConsequences

section CommonPolicyBudget

omit [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A] in
/-- The time-indexed law construction has the same chronological states when
the actual density instrument is stationary. -/
theorem stationary_run (C₀ : BaseNorm.ProbabilityCone (State r))
    (J : ContinuousInstrument.DensityInstrument (A := A) C₀ UniformIntervalMoments.measure)
    (x : State r) : (N : ℕ) → ∀ h : ContinuousRecords.History (A × ℝ) N,
      TimeRecords.run (fun _ => J) x N h=ContinuousRecords.run J x N h
  | 0,_ => rfl
  | N+1,h => by
    change J.op h.2.1 h.2.2 (TimeRecords.run (fun _ => J) x N h.1)=_
    rw [stationary_run C₀ J x N h.1]
    rfl

omit [MeasurableSingletonClass A] in
/-- Equality is proved for the actual measures, so a P59 bound for the constant
time family is a bound for the same stationary fitted record law. -/
theorem stationary_record_law (C₀ : BaseNorm.ProbabilityCone (State r))
    (J : ContinuousInstrument.DensityInstrument (A := A) C₀ UniformIntervalMoments.measure)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) (x : State r) (N : ℕ) :
    TimeRecords.recordLaw (fun _ => J) π x N=ContinuousRecords.recordLaw J π x N := by
  unfold TimeRecords.recordLaw ContinuousRecords.recordLaw
  congr 1
  funext h
  simp only [TimeRecords.recordDensity,ContinuousRecords.recordDensity,stationary_run]

/-- The actual reconstructed/certified law is compared only with certified
models on the same cone and reference, using one common history policy.
The instrument and initial discrepancies remain explicit source hypotheses. -/
theorem population_common_policy_budget (T S : Operator r)
    (C : A → Fin (degree+1) → Operator r)
    (M : MatrixEmbedding.Embedding (State r) D) (b : Module.Basis R ℝ (State r))
    {q bound : ℕ}
    (W : PolynomialGram.CoefficientCertificate b M.coneInstance M.J (fittedCoefficients T S C) q bound)
    (others : ℕ → ContinuousInstrument.DensityInstrument (A := A) M.coneInstance UniformIntervalMoments.measure)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z₀ : State r) (hinitial : T *ᵥ z₀∈M.coneInstance.base)
    (otherInitial : ContinuousInstrument.DensityInstrument.State M.coneInstance)
    (ε : ℕ → ℝ) (hε : ∀ t,0≤ε t)
    (herror : ∀ t a x,x∈M.coneInstance.base →
      (∫ y,M.coneInstance.value
        ((realizedInstrument T S C M b W).op a y x-(others t).op a y x)
          ∂UniformIntervalMoments.measure)≤ε t)
    (e₀ : ℝ) (hinitialError : M.coneInstance.value (T *ᵥ z₀-otherInitial.1)≤e₀) (N : ℕ) :
    let initial : ContinuousInstrument.DensityInstrument.State M.coneInstance := ⟨T *ᵥ z₀,hinitial⟩
    letI : IsProbabilityMeasure (TimeRecords.recordLaw (fun _ => realizedInstrument T S C M b W) π initial.1 N) :=
      TimeRecords.recordLaw_probability (fun _ => realizedInstrument T S C M b W) π initial N
    letI : IsProbabilityMeasure (TimeRecords.recordLaw others π otherInitial.1 N) :=
      TimeRecords.recordLaw_probability others π otherInitial N
    TimeRecords.recordLaw (fun _ => realizedInstrument T S C M b W) π initial.1 N=
      ContinuousRecords.recordLaw (realizedInstrument T S C M b W) π initial.1 N ∧
    SequentialLowerCertificate.lawTV
      (TimeRecords.recordLaw (fun _ => realizedInstrument T S C M b W) π initial.1 N)
      (TimeRecords.recordLaw others π otherInitial.1 N)≤min 1 ((e₀+∑ t∈Finset.range N,ε t)/2) := by
  dsimp only
  exact ⟨stationary_record_law M.coneInstance (realizedInstrument T S C M b W) π (T *ᵥ z₀) N,
    ContinuousTV.record_lawTV_le (fun _ => realizedInstrument T S C M b W) others π
      ⟨T *ᵥ z₀,hinitial⟩ otherInitial ε hε herror e₀ hinitialError N⟩

end CommonPolicyBudget

end Komorebi.LSM.ContinuousRealizationP61
