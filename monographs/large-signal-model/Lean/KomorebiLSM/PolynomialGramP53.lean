import KomorebiLSM.PolynomialGram
import KomorebiLSM.MatrixEmbedding
import KomorebiLSM.ContinuousRecords

/-! The full P53 endpoint combines the actual P50 embedded PSD domain, finite
polynomial coefficient/Gram data, actual uniform moments, and the P52 finite
record probability semantics. No stochastic validity is a certificate field. -/
set_option autoImplicit false
namespace Komorebi.LSM.PolynomialGramP53
open PolynomialGram MeasureTheory ProbabilityTheory

variable {E D A R : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [Fintype D] [DecidableEq D] [Fintype A] [Fintype R]
variable [MeasurableSpace A] [MeasurableSingletonClass A]
variable (M : MatrixEmbedding.Embedding E D) (b : Module.Basis R ℝ E)
variable {n q bound : ℕ} (B : A → Fin n → E →L[ℝ] E)
variable (W : CoefficientCertificate b M.coneInstance M.J B q bound)

/-- The finite witness constructs the literal polynomial density instrument
on the embedded matrix cone, not an abstract positive replacement. -/
noncomputable def instrument : ContinuousInstrument.DensityInstrument
    (A := A) M.coneInstance UniformIntervalMoments.measure :=
  W.instrument M.coneInstance_mem

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [MeasurableSingletonClass A] in
@[simp] theorem instrument_op (a : A) (u : ℝ) :
    (instrument M b B W).op a u=operatorPolynomial (B a) u := rfl

/-- P53 for every observation value and every finite horizon. The true PSD
embedding/interior data are in `M`; the literal finite Gram, coefficient and
moment checks are in `W`. Initial positivity and normalization remain explicit. -/
theorem polynomial_gram_probability_certificate (z₀ : E)
    (hz₀ : z₀∈M.cone ∧ M.mass z₀=1) :
    let I := instrument M b B W
    (∀ a u, u∈Set.Icc (-1 : ℝ) 1 → ∀ z∈M.cone,
      operatorPolynomial (B a) u z∈M.cone) ∧
    (∀ word : List (A × ℝ), (∀ s∈word,s.2∈Set.Icc (-1 : ℝ) 1) →
      0≤M.mass (FiniteInstruments.wordAction
        (fun s : A × ℝ => (operatorPolynomial (B s.1) s.2).toLinearMap) word z₀)) ∧
    (∀ a u, u∈Set.Icc (-1 : ℝ) 1 → ∀ z∈M.coneInstance.base,
      0<M.mass (operatorPolynomial (B a) u z) →
      (M.mass (operatorPolynomial (B a) u z))⁻¹ • operatorPolynomial (B a) u z∈M.coneInstance.base) ∧
    (∀ a, IsMarkovKernel (I.kernel a)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ), ∀ T,
      IsProbabilityMeasure (ContinuousRecords.recordLaw I π z₀ T)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ), ∀ T,
      (ContinuousRecords.recordLaw I π z₀ (T+1)).fst=ContinuousRecords.recordLaw I π z₀ T) ∧
    (∀ actions : ℕ → A, ∀ T,
      IsProbabilityMeasure (ContinuousRecords.observationLaw I actions z₀ T)) ∧
    (∀ actions : ℕ → A, ∀ T,
      (ContinuousRecords.observationLaw I actions z₀ (T+1)).fst=
        ContinuousRecords.observationLaw I actions z₀ T) ∧
    (∀ actions : ℕ → A, ∀ T (S : Set (ContinuousRecords.History ℝ T)), MeasurableSet S →
      ContinuousRecords.observationLaw I actions z₀ T S=
        ∫⁻ h in S, ENNReal.ofReal (M.mass (ContinuousRecords.observationRun I actions z₀ T h))
          ∂ContinuousRecords.reference UniformIntervalMoments.measure T) := by
  dsimp only
  have hbase : z₀∈M.coneInstance.base := hz₀
  refine ⟨?_,?_,?_,?_,?_,?_,?_,?_,?_⟩
  · intro a u hu z hz
    exact W.positive a u hu z hz
  · intro word hword
    exact W.word_mass_nonnegative M.coneInstance_mem word hword z₀ hz₀.1
  · intro a u hu z hz hp
    exact W.normalized_update M.coneInstance_mem a u hu z hz hp
  · intro a
    infer_instance
  · intro π T
    exact ContinuousRecords.recordLaw_probability (instrument M b B W) π ⟨z₀,hbase⟩ T
  · intro π T
    exact ContinuousRecords.recordLaw_consistent (instrument M b B W) π hbase.1 T
  · intro actions T
    exact ContinuousRecords.observationLaw_probability (instrument M b B W) actions ⟨z₀,hbase⟩ T
  · intro actions T
    exact ContinuousRecords.observationLaw_consistent (instrument M b B W) actions hbase.1 T
  · intro actions T S hS
    exact ContinuousRecords.observationLaw_product_density (instrument M b B W) actions z₀ T S hS

end Komorebi.LSM.PolynomialGramP53
