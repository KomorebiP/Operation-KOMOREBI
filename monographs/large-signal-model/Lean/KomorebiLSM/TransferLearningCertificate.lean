import KomorebiLSM.EllipsoidDiscoveryP63
import KomorebiLSM.BernsteinCoefficientError
import KomorebiLSM.PredictableResidualP66
import KomorebiLSM.CoveredAdaptiveEvidence
import KomorebiLSM.ObservationLawComparison

/-! P70 composition. Structural replay, common-domain approximation, external
causal comparison and actual sequential evidence retain their own assumptions.
The new bridges below derive full-law upper and simultaneous lower certificates;
neither structural acceptance nor nonrejection is an accuracy assumption. -/
set_option autoImplicit false
namespace Komorebi.LSM.TransferLearningCertificate
open MeasureTheory ProbabilityTheory
open scoped BigOperators NNReal ENNReal

section Structure
variable {D A : Type*} [Fintype D] [DecidableEq D]
variable [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]

/-- The structural part of P70 is obtained from a literal finite P62 certificate,
including exact integrated mass and a normalized initial state. No successful
geometry-discovery proposal is required. -/
theorem structural_acceptance (c : D → ℝ) (H : Matrix D D ℝ) (hH : H.PosDef)
    {n q bound : ℕ} (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (cert : OrientedEllipsoid.PolynomialCertificate c H B q bound)
    (z : OrientedEllipsoid.State D) (hz : z∈OrientedEllipsoid.cone c H)
    (hm : OrientedEllipsoid.mass z=1) :
    (∀ word : List (A × ℝ),(∀ s∈word,s.2∈Set.Icc (-1:ℝ) 1) →
      0≤OrientedEllipsoid.mass (FiniteInstruments.wordAction
        (fun s : A × ℝ => (OrientedEllipsoid.polynomialOperator (B s.1) s.2).toLinearMap) word z)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ T,
      IsProbabilityMeasure (ContinuousRecords.recordLaw (cert.instrument hH) π z T)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ T extra,
      (ContinuousRecords.recordLaw (cert.instrument hH) π z (T+extra)).map
        (ContinuousRecords.truncate T extra)=ContinuousRecords.recordLaw (cert.instrument hH) π z T) := by
  exact ⟨fun word hword => cert.word_mass_nonneg hH word hword hz,
    fun π T => cert.record_law_probability hH π z hz hm T,
    fun π T extra => cert.record_law_prefix hH π z hz T extra⟩
end Structure

section Approximation
variable {E A : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
variable (C : BaseNorm.ProbabilityCone E)

/-- Finite positive coefficient budgets and a genuine Lipschitz hypothesis give
an upper bound for the actual complete joint laws of the true density and its
fitted polynomial model. The common cone, reference and policy are explicit. -/
theorem common_domain_upper_law (n : ℕ)
    (D : ContinuousInstrument.DensityInstrument (A := A) C BernsteinKernel.measure)
    (T : A → Fin (n+1) → E →L[ℝ] E) (eta : A → Fin (n+1) → ℝ)
    (hT : ∀ a k z,z∈C.carrier → T a k z∈C.carrier)
    (hm : ∀ a z,C.mass (((1/((n:ℝ)+1)) • ∑ k,T a k) z)=C.mass z)
    (L : ℝ) (hL : 0≤L)
    (hLip : ∀ a x,x∈Set.Icc (0:ℝ) 1 → ∀ v∈Set.Icc (0:ℝ) 1,
      PositiveCellApproximation.inducedNorm (C := C) (D.op a v-D.op a x)≤L*|v-x|)
    (herror : ∀ a k z,z∈C.base →
      C.value (PositivePolynomialApproximation.coefficient n (D.op a) k z-T a k z)≤eta a k)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ))
    (z : ContinuousInstrument.DensityInstrument.State C) (horizon : ℕ) :
    SequentialLowerCertificate.lawTV (TimeRecords.recordLaw (fun _ => D) π z.1 horizon)
      (TimeRecords.recordLaw (fun _ => BernsteinCoefficientError.fittedInstrument C n T hT hm)
        π z.1 horizon)≤
      min 1 ((horizon:ℝ)/2*(L/Real.sqrt (3*((n:ℝ)+2))+
        BernsteinCoefficientError.maximumCoefficientError n eta)) := by
  let F := BernsteinCoefficientError.fittedInstrument C n T hT hm
  let ε := L/Real.sqrt (3*((n:ℝ)+2))+
    BernsteinCoefficientError.maximumCoefficientError n eta
  have heta (a : A) (k : Fin (n+1)) : 0≤eta a k :=
    (C.value_nonneg _).trans (herror a k z.1 z.2)
  have hε : 0≤ε := by
    have hA : Nonempty A := by
      by_contra h
      let : IsEmpty A := ⟨fun a => h ⟨a⟩⟩
      have hh := π.sum_one 0 PUnit.unit
      simp at hh
    have hcoef : 0≤BernsteinCoefficientError.maximumCoefficientError n eta :=
      (mul_nonneg (by positivity : 0≤1/((n:ℝ)+1))
        (Finset.sum_nonneg (fun k _ => heta (Classical.choice hA) k))).trans
          (BernsteinCoefficientError.coefficient_error_le_maximum n eta (Classical.choice hA))
    exact add_nonneg (div_nonneg hL (Real.sqrt_nonneg _)) hcoef
  have h := ContinuousTV.record_lawTV_le (fun _ => D) (fun _ => F) π z z (fun _ => ε)
    (fun _ => hε)
    (fun _ a u hu => BernsteinCoefficientError.uniform_bias_plus_coefficient_error
      C n D T eta L hL hLip herror a u hu)
    0 (by simp) horizon
  convert h using 1
  congr 1
  simp only [Finset.sum_const,Finset.card_range,nsmul_eq_mul,zero_add]
  dsimp only [ε]
  ring
end Approximation

section Evidence
variable {Ω J Y : Type*} [mΩ : MeasurableSpace Ω] [MeasurableSpace Y] [Countable J]
variable {μ : Measure Ω} [IsProbabilityMeasure μ]

omit [IsProbabilityMeasure μ] in
/-- A measurable high-probability event can be refined by an AE implication
without requiring the target predicate itself to be measurable. The returned
set remains measurable and has exactly the same probability as the original. -/
theorem refine_event_ae (E : Set Ω) (hE : MeasurableSet E) (P : Ω → Prop)
    (hP : ∀ᵐ ω∂μ,ω∈E → P ω) :
    ∃ G : Set Ω,MeasurableSet G ∧ G⊆E ∧ μ G=μ E ∧ ∀ ω∈G,P ω := by
  have hbad : μ {ω | ¬(ω∈E → P ω)}=0 := ae_iff.mp hP
  obtain ⟨N,hsub,hN,hnull⟩ := exists_measurable_superset_of_null hbad
  have hNae : ∀ᵐ ω∂μ,ω∉N := by
    apply ae_iff.mpr
    simpa using hnull
  refine ⟨E\N,hE.diff hN,Set.sdiff_subset,?_,?_⟩
  · apply measure_congr
    filter_upwards [hNae] with ω hω
    simp only [Set.mem_sdiff,hω,not_false_eq_true,and_true]
  · intro ω hω
    by_contra hnot
    exact hω.2 (hsub (by exact fun hp => hnot (hp hω.1)))

/-- Full P66 implies simultaneous P68 lower certificates for the actual true
and proposed observation laws, when the true bounded-test means are the actual
conditional expectations. The returned event is genuinely measurable, includes
all registered rules and all positive times, and retains probability 1-delta. -/
theorem simultaneous_lower_evidence (ℱ : Filtration ℕ mΩ) (X : J → ℕ → Ω → ℝ)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i))
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (0:ℝ) 1)
    (P Q : J → ℕ → Ω → Measure Y)
    [∀ j i ω,IsProbabilityMeasure (P j i ω)] [∀ j i ω,IsProbabilityMeasure (Q j i ω)]
    (φ : J → ℕ → Ω → Y → ℝ)
    (hφ : ∀ j i ω,Measurable (φ j i ω))
    (hφ0 : ∀ j i ω y,0≤φ j i ω y) (hφ1 : ∀ j i ω y,φ j i ω y≤1)
    (htrue : ∀ j i,(μ[X j i | ℱ i])=ᵐ[μ] (fun ω => ∫ y,φ j i ω y∂P j i ω))
    (α : J → NNReal) (hα : ∀ j,0<α j) (hs : Summable α)
    (δ : NNReal) (hbudget : ∑' j,α j≤δ) (hδ1 : δ≤1) :
    ∃ good : Set Ω,MeasurableSet good ∧ 1-(δ:ℝ)≤μ.real good ∧
      ∀ ω∈good,∀ j t,0<t →
        max (|SequentialLowerCertificate.residual t (fun i => X j i ω)
          (fun i => ∫ y,φ j i ω y∂Q j i ω)|-PredictableResidual.boundary t (α j)) 0/(t:ℝ)≤
        (∑ i∈Finset.range t,SequentialLowerCertificate.lawTV (P j i ω) (Q j i ω))/(t:ℝ) := by
  let p : J → ℕ → Ω → ℝ := fun j i ω => ∫ y,φ j i ω y∂Q j i ω
  let E : Set Ω := {ω | ∀ j n,
    |PredictableResidual.observedResidual (X j) (p j) (n+1) ω-
      PredictableResidual.conditionalDrift (μ:=μ) ℱ (X j) (p j) (n+1) ω|≤
        PredictableResidual.boundary (n+1) (α j)}
  have hEm : MeasurableSet E := by
    simpa only [E,PredictableResidual.residual_sub_drift] using
      PredictableResidualGeneral.unit_event_measurable ℱ X hX α
  have hprob : 1-(δ:ℝ)≤μ.real E :=
    PredictableResidualGeneral.predictable_residual_certificate_countable ℱ X p hX hb α hα hs δ hbudget hδ1
  have hmeans : ∀ᵐ ω∂μ,∀ j i,(μ[X j i | ℱ i]) ω=∫ y,φ j i ω y∂P j i ω :=
    ae_all_iff.mpr (fun j => ae_all_iff.mpr (fun i => htrue j i))
  have hpoint : ∀ᵐ ω∂μ,ω∈E → ∀ j t,0<t →
      max (|SequentialLowerCertificate.residual t (fun i => X j i ω)
        (fun i => ∫ y,φ j i ω y∂Q j i ω)|-PredictableResidual.boundary t (α j)) 0/(t:ℝ)≤
      (∑ i∈Finset.range t,SequentialLowerCertificate.lawTV (P j i ω) (Q j i ω))/(t:ℝ) := by
    filter_upwards [hmeans] with ω hmeans hall
    intro j t ht
    apply SequentialLowerCertificate.sequential_lower_certificate t ht
      (fun i => P j i ω) (fun i => Q j i ω) (fun i => φ j i ω) (fun i => X j i ω)
      (PredictableResidual.boundary t (α j)) (fun i => hφ j i ω)
      (fun i => hφ0 j i ω) (fun i => hφ1 j i ω)
    have htime : (t-1)+1=t := by omega
    have he := hall j (t-1)
    rw [htime] at he
    have hsum : SequentialLowerCertificate.drift t (fun i => ∫ y,φ j i ω y∂P j i ω)
        (fun i => ∫ y,φ j i ω y∂Q j i ω)=
        PredictableResidual.conditionalDrift (μ:=μ) ℱ (X j) (p j) t ω := by
      apply Finset.sum_congr rfl
      intro i _
      rw [hmeans j i]
    rw [hsum]
    exact he
  obtain ⟨G,hG,hGE,hμG,hgood⟩ := refine_event_ae E hEm _ hpoint
  exact ⟨G,hG,by simpa only [Measure.real,hμG] using hprob,hgood⟩
end Evidence

end Komorebi.LSM.TransferLearningCertificate
