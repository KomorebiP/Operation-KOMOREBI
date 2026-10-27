import KomorebiLSM.EllipsoidDiscovery
import KomorebiLSM.EllipsoidPolynomial

/-! P63 separates the operator-only geometry proposal from acceptance. The
actual fitted family supplies the ratio and rank-one anchor; probability
meaning is obtained only from the full P62 quadratic/orientation witnesses,
exact integrated mass, and a normalized initial state in the proposed cone. -/
set_option autoImplicit false
namespace Komorebi.LSM.EllipsoidDiscoveryP63
open EllipsoidDiscovery MeasureTheory ProbabilityTheory
open scoped BigOperators Matrix

variable {D A : Type*} [Fintype D] [DecidableEq D]

/-- Evaluation is the literal matrix polynomial of the fitted coefficients. -/
noncomputable def evaluatedBranch {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (a : A) (u : ℝ) :
    Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ :=
  PolynomialGram.evalMatrix (OrientedEllipsoid.matrixPolynomial (B a)) u

noncomputable def fittedRatio {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (a b : A) (u : ℝ) :
    Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ :=
  ratio (evaluatedBranch B a u) (evaluatedBranch B b u)

noncomputable def proposedCenter {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (a b : A) (u : ℝ) : D → ℝ :=
  fixedCenter (spatialBlock (fittedRatio B a b u)) (translation (fittedRatio B a b u))

noncomputable def anchorDisplacement {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (a b k : A) (u v : ℝ) (z : State D) : D → ℝ :=
  spatial (normalizedImage (evaluatedBranch B k v).mulVecLin z)-proposedCenter B a b u

noncomputable def proposedMetric {n : ℕ}
    (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (a b k : A) (u v : ℝ) (z : State D) (H₀ : Matrix D D ℝ) : Matrix D D ℝ :=
  normalizedMetric H₀ (anchorDisplacement B a b k u v z)

variable [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A]
variable {n : ℕ} (B : A → Fin n → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
variable (a b k : A) (u v : ℝ) (z : State D) (H₀ : Matrix D D ℝ)

local notation "F" => fittedRatio B a b u
local notation "c" => proposedCenter B a b u
local notation "L" => Matrix.mulVecLin (evaluatedBranch B k v)
local notation "δ" => anchorDisplacement B a b k u v z
local notation "H" => proposedMetric B a b k u v z H₀

/-- Full P63 acceptance retains every P62 hypothesis on the complete fitted
family. Neither ratio invariance nor a chosen boundary image is used as a
substitute for the oriented quadratic certificate. -/
theorem conditional_operator_only_ellipsoid_discovery
    (hu : u∈Set.Icc (-1 : ℝ) 1) (hv : v∈Set.Icc (-1 : ℝ) 1)
    (hₐ : IsUnit (evaluatedBranch B a u).det) (hratio : IsUnit F)
    (hmass : mass.comp (F).mulVecLin=mass) (hcenter : IsUnit (1-spatialBlock F).det)
    (hdim : Module.finrank ℝ (invariantForms (spatialBlock F))=1)
    (hinvariant : H₀∈invariantForms (spatialBlock F)) (hpositive : H₀.PosDef)
    (hrank : Module.finrank ℝ (L).range=1) (hanchor : mass (L z)≠0)
    (hdisplacement : spatial (normalizedImage L z)≠c)
    (branches : ∀ action obs,obs∈Set.Icc (-1 : ℝ) 1 →
      OrientedEllipsoid.BranchCertificate c H (evaluatedBranch B action obs))
    (hmoments : ∀ action x,OrientedEllipsoid.mass
      ((∑ j : Fin n,UniformIntervalMoments.moment j • OrientedEllipsoid.matrixOperator (B action j)) x)=
        OrientedEllipsoid.mass x)
    (z₀ : State D) (hinitial : z₀∈OrientedEllipsoid.cone c H ∧ OrientedEllipsoid.mass z₀=1) :
    let hH : (H).PosDef := normalizedMetric_posDef hpositive (sub_ne_zero.mpr hdisplacement)
    let I := OrientedEllipsoid.polynomialDensityInstrument c H hH B branches hmoments
    (u∈Set.Icc (-1 : ℝ) 1 ∧ v∈Set.Icc (-1 : ℝ) 1) ∧
    IsUnit F ∧ F=affineMatrix (translation F) (spatialBlock F) ∧
    (∃! x : D → ℝ,F *ᵥ point 1 x=point 1 x) ∧
    normalizedImage L z=point 1 (spatial (normalizedImage L z)) ∧
    H∈invariantForms (spatialBlock F) ∧ (H).PosDef ∧ quadratic H δ=1 ∧
    (∀ K : Matrix D D ℝ,K∈invariantForms (spatialBlock F) → quadratic K δ=1 → K=H) ∧
    (∀ scale : ℝ,0<scale → normalizedMetric (scale • H₀) δ=H) ∧
    (∀ action obs,obs∈Set.Icc (-1 : ℝ) 1 → ∀ x∈OrientedEllipsoid.cone c H,
      evaluatedBranch B action obs *ᵥ x∈OrientedEllipsoid.cone c H) ∧
    (∀ action obs x,I.op action obs x=evaluatedBranch B action obs *ᵥ x) ∧
    (∀ action,IsMarkovKernel (I.kernel action)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ T,
      IsProbabilityMeasure (ContinuousRecords.recordLaw I π z₀ T)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ T,
      (ContinuousRecords.recordLaw I π z₀ (T+1)).fst=ContinuousRecords.recordLaw I π z₀ T) ∧
    (∀ actions : ℕ → A,∀ T,
      IsProbabilityMeasure (ContinuousRecords.observationLaw I actions z₀ T)) ∧
    (∀ actions : ℕ → A,∀ T,
      (ContinuousRecords.observationLaw I actions z₀ (T+1)).fst=
        ContinuousRecords.observationLaw I actions z₀ T) ∧
    (∀ actions : ℕ → A,∀ T (S : Set (ContinuousRecords.History ℝ T)),MeasurableSet S →
      ContinuousRecords.observationLaw I actions z₀ T S=
        ∫⁻ h in S,ENNReal.ofReal (OrientedEllipsoid.mass (ContinuousRecords.observationRun I actions z₀ T h))
          ∂ContinuousRecords.reference UniformIntervalMoments.measure T) := by
  dsimp only
  have hH : (H).PosDef := normalizedMetric_posDef hpositive (sub_ne_zero.mpr hdisplacement)
  let I := OrientedEllipsoid.polynomialDensityInstrument c H hH B branches hmoments
  have hbase : z₀∈(OrientedEllipsoid.probabilityCone c H hH).base := hinitial
  have hᵦ : IsUnit (evaluatedBranch B b u).det := by
    have hprod := hratio.mul ((Matrix.isUnit_iff_isUnit_det _).mpr hₐ)
    have he : F * evaluatedBranch B a u=evaluatedBranch B b u :=
      ratio_reconstructs _ _ hₐ
    rw [he] at hprod
    exact (Matrix.isUnit_iff_isUnit_det _).mp hprod
  rcases operator_only_proposal (evaluatedBranch B a u) (evaluatedBranch B b u)
    hₐ hᵦ hmass hcenter H₀ hdim hinvariant hpositive L hrank z hanchor hdisplacement with
    ⟨hunit,hblock,hfixed,_,hnormalized,_,hform,hpd,hboundary,hunique⟩
  refine ⟨⟨hu,hv⟩,hunit,hblock,hfixed,hnormalized,hform,hpd,hboundary,hunique,?_,?_,?_,?_,?_,?_,?_,?_,?_⟩
  · intro scale hscale
    exact positive_scale_independent scale hscale hpositive (sub_ne_zero.mpr hdisplacement)
  · intro action obs hobs x hx
    exact (branches action obs hobs).preserves hH hx
  · intro action obs x
    change OrientedEllipsoid.polynomialOperator (B action) obs x=evaluatedBranch B action obs *ᵥ x
    rw [OrientedEllipsoid.polynomialOperator_matrix,OrientedEllipsoid.matrixOperator_apply]
    rfl
  · intro action
    infer_instance
  · intro π T
    exact ContinuousRecords.recordLaw_probability I π ⟨z₀,hbase⟩ T
  · intro π T
    exact ContinuousRecords.recordLaw_consistent I π hbase.1 T
  · intro actions T
    exact ContinuousRecords.observationLaw_probability I actions ⟨z₀,hbase⟩ T
  · intro actions T
    exact ContinuousRecords.observationLaw_consistent I actions hbase.1 T
  · intro actions T S hS
    exact ContinuousRecords.observationLaw_product_density I actions z₀ T S hS

/-- A replayed finite P62 SOS/Gram/coefficient certificate for the computed
geometry discharges the whole-family tests. Probability validity still needs
the explicit normalized initial state, and is separate from proposal success. -/
theorem finite_certificate_all_horizons
    (hpositive : H₀.PosDef) (hdisplacement : spatial (normalizedImage L z)≠c)
    {q bound : ℕ} (cert : OrientedEllipsoid.PolynomialCertificate c H B q bound)
    (z₀ : State D) (hinitial : z₀∈OrientedEllipsoid.cone c H ∧ OrientedEllipsoid.mass z₀=1) :
    let hH : (H).PosDef := normalizedMetric_posDef hpositive (sub_ne_zero.mpr hdisplacement)
    (∀ word : List (A × ℝ),(∀ s∈word,s.2∈Set.Icc (-1 : ℝ) 1) →
      0≤OrientedEllipsoid.mass (FiniteInstruments.wordAction
        (fun s : A × ℝ => (OrientedEllipsoid.polynomialOperator (B s.1) s.2).toLinearMap) word z₀)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ T,
      IsProbabilityMeasure (ContinuousRecords.recordLaw (cert.instrument hH) π z₀ T)) ∧
    (∀ actions : ℕ → A,∀ T,
      IsProbabilityMeasure (ContinuousRecords.observationLaw (cert.instrument hH) actions z₀ T)) ∧
    (∀ π : ContinuousRecords.Policy (A := A) (Y := ℝ),∀ T extra,
      (ContinuousRecords.recordLaw (cert.instrument hH) π z₀ (T+extra)).map
        (ContinuousRecords.truncate T extra)=ContinuousRecords.recordLaw (cert.instrument hH) π z₀ T) := by
  dsimp only
  let hH : (H).PosDef := normalizedMetric_posDef hpositive (sub_ne_zero.mpr hdisplacement)
  exact ⟨fun word hword => cert.word_mass_nonneg hH word hword hinitial.1,
    fun π T => cert.record_law_probability hH π z₀ hinitial.1 hinitial.2 T,
    fun actions T => cert.observation_law_probability hH actions z₀ hinitial.1 hinitial.2 T,
    fun π T extra => cert.record_law_prefix hH π z₀ hinitial.1 T extra⟩

end Komorebi.LSM.EllipsoidDiscoveryP63
