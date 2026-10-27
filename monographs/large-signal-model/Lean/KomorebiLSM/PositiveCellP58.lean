import KomorebiLSM.PositiveCellUniform

/-! Full P58 endpoints on the actual averaged continuous instrument. -/
set_option autoImplicit false
namespace Komorebi.LSM.PositiveCellApproximation
open MeasureTheory ProbabilityTheory ContinuousInstrument ContinuousBins
variable {E A Y I : Type*} [Fintype I]
variable [NormedAddCommGroup E] [NormedSpace ℝ E] [FiniteDimensional ℝ E]
variable [MeasurableSpace E] [BorelSpace E]
variable [MeasurableSpace Y] [PseudoMetricSpace Y] [BorelSpace Y]
variable {C : BaseNorm.ProbabilityCone E} {μ : Measure Y} [IsProbabilityMeasure μ]

/-- P58: the actual normalized Bochner cell averages preserve the cone and
mass, retain every exact event-cell operator, and satisfy the displayed
supremum discrepancy bound in the genuine induced base norm. -/
theorem positive_cell_average_certificate
    (D : DensityInstrument (A := A) C μ) (P : CellPartition μ I)
    (L h : ℝ) (hL : 0≤L) (hh : 0≤h)
    (hl : CellLipschitz D P L) (hd : CellDiameter P h) :
    let K := instrument D P
    (∀ a y z,z∈C.carrier → K.op a y z∈C.carrier) ∧
    (∀ a z,C.mass ((∫ y,K.op a y∂μ) z)=C.mass z) ∧
    (∀ a i,cellOperator μ (K.op a) (P.cell i)=cellOperator μ (D.op a) (P.cell i)) ∧
    (∀ a,IsMarkovKernel (K.kernel a)) ∧ approximationError D P≤L*h := by
  dsimp only
  refine ⟨?_,(instrument D P).mass_preserving,?_,?_,approximationError_le_diameter D P hL hh hl hd⟩
  · exact fun a y z hz => operator_positive D P a y hz
  · exact exact_cell_operator D P
  · intro a
    infer_instance

omit [MeasurableSpace Y] [PseudoMetricSpace Y] [BorelSpace Y] [IsProbabilityMeasure μ] in
/-- The same actual positive approximation has the sharper uniform equal-cell
error Lh/3; positivity and exact normalization are retained together with it. -/
theorem positive_equal_interval_certificate
    (D : DensityInstrument (A := A) C UniformIntervalMoments.measure)
    (P : CellPartition UniformIntervalMoments.measure I)
    (a b : I → ℝ) (L h : ℝ) (hL : 0≤L) (hh : 0<h)
    (hc : ∀ i,P.cell i=Set.Ioc (a i) (b i))
    (ha : ∀ i,-1≤a i) (hb : ∀ i,b i≤1) (hw : ∀ i,b i-a i=h)
    (hl : ∀ act,∀ y∈Set.Icc (-1 : ℝ) 1,∀ v∈Set.Icc (-1 : ℝ) 1,
      inducedNorm (C := C) (D.op act y-D.op act v)≤L*dist y v) :
    let K := instrument D P
    (∀ act y z,z∈C.carrier → K.op act y z∈C.carrier) ∧
    (∀ act z,C.mass ((∫ y,K.op act y∂UniformIntervalMoments.measure) z)=C.mass z) ∧
    (∀ act i,cellOperator UniformIntervalMoments.measure (K.op act) (P.cell i)=
      cellOperator UniformIntervalMoments.measure (D.op act) (P.cell i)) ∧
    (∀ act,IsMarkovKernel (K.kernel act)) ∧ approximationError D P≤L*h/3 := by
  dsimp only
  refine ⟨?_,(instrument D P).mass_preserving,?_,?_,
    approximationError_le_equal_intervals P D a b h L hh hL hc ha hb hw hl⟩
  · exact fun act y z hz => operator_positive D P act y hz
  · exact exact_cell_operator D P
  · intro act
    infer_instance

end Komorebi.LSM.PositiveCellApproximation
