import KomorebiLSM.ObservableOperatorSets
import KomorebiLSM.RegressionConfidence
import KomorebiLSM.CountableConfidence

/-! Full P82 confidence transfer from actual rowwise P81 regression events.
Rows and moments share observations freely; only the literal finite prospective
budget is added. Exact mass intersection preserves the true coefficients. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservableMoments
open MeasureTheory ProbabilityTheory Matrix RegressionConfidence
open scoped BigOperators NNReal Matrix

variable {Ω H A Y : Type*} {p r : ℕ} [mΩ : MeasurableSpace Ω] [mH : MeasurableSpace H]
variable [MeasurableSpace Y] [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]
variable {C : BaseNorm.ProbabilityCone (Fin r → ℝ)} {ν : Measure Y} [IsProbabilityMeasure ν]
variable (D : ContinuousInstrument.DensityInstrument (A := A) C ν)
variable {μ : Measure Ω} [IsProbabilityMeasure μ] {ℱ : Filtration ℕ mΩ}
variable (P : AccessibleProcess (H := H) (μ := μ) D ℱ)

abbrev RowIndex (A : Type*) (p r : ℕ) := A × Fin p × Fin r

noncomputable def rowParameter (g : Fin p → Y → ℝ) (k : RowIndex A p r) : Fin r → ℝ :=
  fun l => momentMatrix D (g k.2.1) k.1 k.2.2 l

/-- Every fitted row is the literal ridge estimator from the recorded
action-gated design and recorded accessible-state response. -/
noncomputable def fittedMomentMatrices (γ : A → ℝ) (g : Fin p → Y → ℝ)
    (n : ℕ) (ω : Ω) : CoefficientFamily A p r := fun a j i =>
  ridgeEstimate (γ a) (fun s => gatedDesign D P a s ω)
    (fun s => gatedResponse D P a (g j) i s ω) n

noncomputable def actionDesign (γ : A → ℝ) (n : ℕ) (ω : Ω) : A → Matrix (Fin r) (Fin r) ℝ :=
  fun a => ridgeMatrix (γ a) (fun s => gatedDesign D P a s ω) n

noncomputable def momentRadius (γ : A → ℝ) (σ S : RowIndex A p r → ℝ)
    (α : RowIndex A p r → NNReal) (n : ℕ) (ω : Ω) : A → Fin p → Fin r → ℝ :=
  fun a j i => noiseRadius (γ a) (σ (a,j,i)) (α (a,j,i))
    (fun s => gatedDesign D P a s ω) n+Real.sqrt (γ a)*S (a,j,i)

noncomputable def rowGoodEvent (γ : A → ℝ) (σ : RowIndex A p r → ℝ)
    (α : RowIndex A p r → NNReal) (g : Fin p → Y → ℝ) (k : RowIndex A p r) : Set Ω :=
  regressionGood (γ k.1) (σ k) (α k) (gatedDesign D P k.1)
    (gatedResponse D P k.1 (g k.2.1) k.2.2) (rowParameter D g k)

/-- A literal finite intersection of the actual Gaussian-mixture P81 events. -/
noncomputable def operatorGoodEvent (γ : A → ℝ) (σ : RowIndex A p r → ℝ)
    (α : RowIndex A p r → NNReal) (g : Fin p → Y → ℝ) : Set Ω :=
  ⋂ k : RowIndex A p r,rowGoodEvent D P γ σ α g k

/-- Full row coverage is derived by applying P81 to every actual moment row
and then the finite prospective union bound. No independence between rows is
assumed, and no row-confidence event is supplied as a certificate field. -/
theorem moment_row_confidence (γ : A → ℝ) (hγ : ∀ a,0<γ a)
    (σ S : RowIndex A p r → ℝ) (hσ : ∀ k,0<σ k)
    (α : RowIndex A p r → NNReal) (hα : ∀ k,0<α k)
    (δ : NNReal) (hbudget : ∑ k,α k≤δ)
    (g : Fin p → Y → ℝ) (hg : ∀ j,Measurable (g j))
    (hθ : ∀ k,euclideanNorm (rowParameter D g k)≤S k)
    (Hnoise : ∀ k n,ConditionalSubgaussian (ℱ.le n)
      (regressionNoise (rowParameter D g k) (gatedDesign D P k.1)
        (gatedResponse D P k.1 (g k.2.1) k.2.2) n) (σ k) μ) :
    MeasurableSet (operatorGoodEvent D P γ σ α g) ∧
    1-(δ:ℝ)≤μ.real (operatorGoodEvent D P γ σ α g) ∧
    ∀ ω∈operatorGoodEvent D P γ σ α g,∀ n a j i,
      weightedNorm (actionDesign D P γ n ω a)
        (fun l => fittedMomentMatrices D P γ g n ω a j i l-momentMatrix D (g j) a i l)≤
          momentRadius D P γ σ S α n ω a j i := by
  classical
  have hc (k : RowIndex A p r) := regression_confidence_certificate (μ := μ) ℱ
    (γ k.1) (σ k) (α k) (S k) (hγ k.1) (hσ k) (by exact_mod_cast hα k)
    (gatedDesign D P k.1) (gatedResponse D P k.1 (g k.2.1) k.2.2) (rowParameter D g k)
    (fun n i => (measurable_pi_apply i).comp (gatedDesign_measurable D P k.1 n))
    (gatedResponse_measurable D P k.1 (g k.2.1) (hg k.2.1) k.2.2)
    (hθ k) (Hnoise k)
  refine ⟨?_,?_,?_⟩
  · exact MeasurableSet.iInter (fun k => (hc k).1)
  · have hb (k : RowIndex A p r) : μ.real (rowGoodEvent D P γ σ α g k)ᶜ≤(α k:ℝ) := by
      unfold rowGoodEvent
      rw [measureReal_compl (hc k).1,probReal_univ]
      linarith [(hc k).2.1]
    have hu := CountableConfidence.finite_simultaneous_coverage
      (fun k => (rowGoodEvent D P γ σ α g k)ᶜ) (fun k => (hc k).1.compl)
      α δ hbudget hb
    simpa only [compl_compl,operatorGoodEvent] using hu
  · intro ω hω n a j i
    have hr := (hc (a,j,i)).2.2 ω (Set.mem_iInter.mp hω (a,j,i)) n
    change weightedNorm (ridgeMatrix (γ a) (fun s => gatedDesign D P a s ω) n)
      (ridgeEstimate (γ a) (fun s => gatedDesign D P a s ω)
        (fun s => gatedResponse D P a (g j) i s ω) n-rowParameter D g (a,j,i))≤
      noiseRadius (γ a) (σ (a,j,i)) (α (a,j,i))
        (fun s => gatedDesign D P a s ω) n+Real.sqrt (γ a)*S (a,j,i)
    exact hr

/-- The submitted coefficient estimate is the known inverse moment map of
the actual fitted row-regression matrices. -/
noncomputable def coefficientEstimate (W : Matrix (Fin p) (Fin p) ℝ) (γ : A → ℝ)
    (g : Fin p → Y → ℝ) (n : ℕ) (ω : Ω) : CoefficientFamily A p r :=
  fun a => FiniteMomentIdentification.mix W⁻¹ (fittedMomentMatrices D P γ g n ω a)

/-- Full P82: actual conditional moment semantics and known basis inversion
are combined with the actual finite-family P81 event. On that one measurable
event, every finite-time coefficient set contains the true coefficients after
exact mass intersection, and every directional row bound is genuine. -/
theorem observable_moment_operator_confidence
    (B : A → Fin p → (Fin r → ℝ) →L[ℝ] (Fin r → ℝ))
    (g ψ : Fin p → Y → ℝ) (hg : ∀ j,Measurable (g j))
    (hB : ∀ a y,D.op a y=∑ k,ψ k y • B a k)
    (hgψ : ∀ j k,Integrable (fun y => g j y*ψ k y) ν) (hψ : ∀ k,Integrable (ψ k) ν)
    (hW : IsUnit (basisMomentMatrix (ν := ν) g ψ))
    (γ : A → ℝ) (hγ : ∀ a,0<γ a)
    (σ S : RowIndex A p r → ℝ) (hσ : ∀ k,0<σ k)
    (α : RowIndex A p r → NNReal) (hα : ∀ k,0<α k)
    (δ : NNReal) (hbudget : ∑ k,α k≤δ)
    (hθ : ∀ k,euclideanNorm (rowParameter D g k)≤S k)
    (Hnoise : ∀ k n,ConditionalSubgaussian (ℱ.le n)
      (regressionNoise (rowParameter D g k) (gatedDesign D P k.1)
        (gatedResponse D P k.1 (g k.2.1) k.2.2) n) (σ k) μ) :
    (∀ j n,μ[fun ω => g j (P.observation n ω) • currentState D P (n+1) ω | ℱ n]=ᵐ[μ]
      (fun ω => momentOperator D (g j) (currentAction D P n ω) (currentState D P n ω))) ∧
    (∀ a j i n,μ[gatedResponse D P a (g j) i n | ℱ n]=ᵐ[μ]
      (fun ω => (momentMatrix D (g j) a *ᵥ gatedDesign D P a n ω) i)) ∧
    (∀ a,coefficientMatrices B a=FiniteMomentIdentification.mix
      (basisMomentMatrix (ν := ν) g ψ)⁻¹ (fun j => momentMatrix D (g j) a)) ∧
    MeasurableSet (operatorGoodEvent D P γ σ α g) ∧
    1-(δ:ℝ)≤μ.real (operatorGoodEvent D P γ σ α g) ∧
    (∀ ω∈operatorGoodEvent D P γ σ α g,∀ n,
      coefficientMatrices B∈massConstrainedRegion (basisMomentMatrix (ν := ν) g ψ)
        (fittedMomentMatrices D P γ g n ω) (actionDesign D P γ n ω)
        (momentRadius D P γ σ S α n ω) C.mass (basisIntegral (ν := ν) ψ) ∧
      ∀ a k i x,
        |(coefficientEstimate D P (basisMomentMatrix (ν := ν) g ψ) γ g n ω a k *ᵥ x) i-
          (coefficientMatrices B a k *ᵥ x) i|≤
          ∑ j,|(basisMomentMatrix (ν := ν) g ψ)⁻¹ k j| * momentRadius D P γ σ S α n ω a j i *
            weightedNorm (actionDesign D P γ n ω a)⁻¹ x) := by
  have hi (j : Fin p) (a : A) : Integrable (fun y => g j y • D.op a y) ν :=
    weighted_operator_integrable D B ψ hB (g j) (hgψ j) a
  obtain ⟨hG,hprob,hrows⟩ := moment_row_confidence D P γ hγ σ S hσ α hα δ hbudget g hg hθ Hnoise
  refine ⟨?_,?_,matrix_coefficient_reconstruction D B g ψ hB hgψ hW,hG,hprob,?_⟩
  · intro j n
    exact process_conditional_moment D P (g j) (hg j) (hi j) n
  · intro a j i n
    exact gatedResponse_condExp D P a (g j) (hg j) (hi j) i n
  · intro ω hω n
    have hr := hrows ω hω n
    have htrue := true_coefficients_in_mass_region D B g ψ hB hgψ hψ hW
      (fittedMomentMatrices D P γ g n ω) (actionDesign D P γ n ω)
      (momentRadius D P γ σ S α n ω) hr
    refine ⟨htrue,?_⟩
    exact coefficient_region_directional _ _ _
      (fun a => ridgeMatrix_posDef (γ a) (hγ a) (fun s => gatedDesign D P a s ω) n)
      _ htrue.1

end Komorebi.LSM.ObservableMoments
