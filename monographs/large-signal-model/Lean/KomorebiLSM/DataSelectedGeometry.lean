import KomorebiLSM.EuclideanMatrixNorms
import KomorebiLSM.RobustOrientedMargin

/-! P78: an already justified coverage event survives arbitrary data-dependent
geometry selection, and whole-state Euclidean errors pay the actual condition number. -/
set_option autoImplicit false
namespace Komorebi.LSM.DataSelectedGeometry
open MeasureTheory EuclideanMatrixNorms
open scoped Matrix BigOperators ENNReal

section Coverage
variable {E S G Ω : Type*} [AddCommGroup E] [Module ℝ E]

/-- Operators and initial state stay in one fixed predictive coordinate system. -/
structure Model (S E : Type*) [AddCommGroup E] [Module ℝ E] where
  initial : E
  operator : S → E →ₗ[ℝ] E

def DomainValid (domain : G → Set E) (g : G) (M : Model S E) : Prop :=
  M.initial∈domain g ∧ ∀ s z,z∈domain g → M.operator s z∈domain g

/-- The same entire uncertainty set is quantified after geometry selection. -/
theorem selected_geometry_on_coverage (domain : G → Set E)
    (U : Ω → Set (Model S E)) (selected : Ω → G) (truth : Model S E)
    (verifies : ∀ ω M,M∈U ω → DomainValid domain (selected ω) M) :
    {ω | truth∈U ω}⊆{ω | DomainValid domain (selected ω) truth} := by
  intro ω hω
  exact verifies ω truth hω

/-- No union over the possibly infinite collection of geometry proposals is used. -/
theorem selected_geometry_probability [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]
    (domain : G → Set E) (U : Ω → Set (Model S E)) (selected : Ω → G) (truth : Model S E)
    (_hcoverage : MeasurableSet {ω | truth∈U ω})
    (_hverified : MeasurableSet {ω | DomainValid domain (selected ω) truth})
    (delta : ℝ≥0∞) (hprob : 1-delta≤μ {ω | truth∈U ω})
    (verifies : ∀ ω M,M∈U ω → DomainValid domain (selected ω) M) :
    1-delta≤μ {ω | DomainValid domain (selected ω) truth} :=
  hprob.trans (measure_mono (selected_geometry_on_coverage domain U selected truth verifies))

/-- If a procedure sometimes withholds a result, false acceptance is still
contained in the original coverage failure event. -/
theorem false_acceptance_subset (domain : G → Set E)
    (U : Ω → Set (Model S E)) (selected : Ω → G) (truth : Model S E) (accepts : Ω → Prop)
    (verifies : ∀ ω,accepts ω → ∀ M,M∈U ω → DomainValid domain (selected ω) M) :
    {ω | accepts ω ∧ ¬DomainValid domain (selected ω) truth}⊆{ω | truth∉U ω} := by
  intro ω hω hmem
  exact hω.2 (verifies ω hω.1 truth hmem)

theorem false_acceptance_probability [MeasurableSpace Ω] (μ : Measure Ω) [IsProbabilityMeasure μ]
    (domain : G → Set E) (U : Ω → Set (Model S E)) (selected : Ω → G) (truth : Model S E)
    (accepts : Ω → Prop) (delta : ℝ≥0∞)
    (_hcoverage : MeasurableSet {ω | truth∉U ω})
    (_hfailure : MeasurableSet {ω | accepts ω ∧ ¬DomainValid domain (selected ω) truth})
    (hprob : μ {ω | truth∉U ω}≤delta)
    (verifies : ∀ ω,accepts ω → ∀ M,M∈U ω → DomainValid domain (selected ω) M) :
    μ {ω | accepts ω ∧ ¬DomainValid domain (selected ω) truth}≤delta :=
  (measure_mono (false_acceptance_subset domain U selected truth accepts verifies)).trans hprob
end Coverage

section EuclideanError
variable {D : Type*} [Fintype D] [DecidableEq D]
abbrev WholeState (D : Type*) := EuclideanSpace ℝ (Unit ⊕ D)

def massPart (y : WholeState D) : ℝ := y (Sum.inl ())
noncomputable def spatialPart (y : WholeState D) : EuclideanSpace ℝ D :=
  WithLp.toLp 2 (fun i => y (Sum.inr i))

omit [DecidableEq D] in
/-- The whole-state norm here is the Euclidean two-norm, not the Lorentz base norm. -/
theorem whole_norm_sq (y : WholeState D) : ‖y‖^2=|massPart y|^2+‖spatialPart y‖^2 := by
  rw [EuclideanSpace.real_norm_sq_eq,EuclideanSpace.real_norm_sq_eq]
  simp [massPart,spatialPart,Fintype.sum_sum_type]

noncomputable def wholeInput (v : EuclideanSpace ℝ D) : WholeState D :=
  WithLp.toLp 2 (Sum.elim (fun _ : Unit => (1 : ℝ)) (fun i => v i))

omit [Fintype D] [DecidableEq D] in
@[simp] theorem wholeInput_mass (v : EuclideanSpace ℝ D) : massPart (wholeInput v)=1 := rfl
omit [Fintype D] [DecidableEq D] in
@[simp] theorem wholeInput_spatial (v : EuclideanSpace ℝ D) : spatialPart (wholeInput v)=v := by
  ext i
  rfl

omit [DecidableEq D] in
theorem wholeInput_norm_le_sqrt_two (v : EuclideanSpace ℝ D) (hv : ‖v‖≤1) :
    ‖wholeInput v‖≤Real.sqrt 2 := by
  have hs := whole_norm_sq (wholeInput v)
  rw [wholeInput_mass,wholeInput_spatial] at hs
  norm_num at hs
  have hroot : (Real.sqrt 2)^2=2 := Real.sq_sqrt (by norm_num)
  nlinarith [norm_nonneg v,norm_nonneg (wholeInput v),Real.sqrt_nonneg 2]

omit [DecidableEq D] in
/-- The mass/spatial split costs a second sqrt(2) in the genuine Euclidean norm. -/
theorem combined_output_le_sqrt_two (y : WholeState D) :
    |massPart y|+‖spatialPart y‖≤Real.sqrt 2*‖y‖ := by
  have hs := whole_norm_sq y
  have hroot : (Real.sqrt 2)^2=2 := Real.sq_sqrt (by norm_num)
  have hsq : (|massPart y|+‖spatialPart y‖)^2≤(Real.sqrt 2*‖y‖)^2 := by
    rw [mul_pow,hroot]
    nlinarith [sq_nonneg (|massPart y|-‖spatialPart y‖)]
  exact (sq_le_sq₀ (add_nonneg (abs_nonneg _) (norm_nonneg _))
    (mul_nonneg (Real.sqrt_nonneg _) (norm_nonneg _))).mp hsq

/-- Literal matrix conjugation is the composition of the three Euclidean actions. -/
theorem conjugate_action (T Delta : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (z : WholeState D) :
    Matrix.toEuclideanCLM (𝕜 := ℝ) (T*Delta*T⁻¹) z=
      Matrix.toEuclideanCLM (𝕜 := ℝ) T (Matrix.toEuclideanCLM (𝕜 := ℝ) Delta (Matrix.toEuclideanCLM (𝕜 := ℝ) T⁻¹ z)) := by
  simp only [map_mul]
  rfl

/-- The actual factor two and condition number come from the two Euclidean norm comparisons. -/
theorem transformed_combined_error (T Delta : Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ)
    (e : ℝ) (herror : spectralNorm Delta≤e) (v : EuclideanSpace ℝ D) (hv : ‖v‖≤1) :
    let y := Matrix.toEuclideanCLM (𝕜 := ℝ) (T*Delta*T⁻¹) (wholeInput v)
    |massPart y|+‖spatialPart y‖≤2*spectralNorm T*spectralNorm T⁻¹*e := by
  have he0 : 0≤e := (spectralNorm_nonneg Delta).trans herror
  have ht0 := spectralNorm_nonneg T
  have hi0 := spectralNorm_nonneg T⁻¹
  let z := wholeInput v
  let Iop := Matrix.toEuclideanCLM (𝕜 := ℝ) T⁻¹
  let Dop := Matrix.toEuclideanCLM (𝕜 := ℝ) Delta
  let Top := Matrix.toEuclideanCLM (𝕜 := ℝ) T
  have hi : ‖Iop z‖≤spectralNorm T⁻¹*Real.sqrt 2 :=
    (Iop.le_opNorm z).trans (mul_le_mul_of_nonneg_left (wholeInput_norm_le_sqrt_two v hv) hi0)
  have hd : ‖Dop (Iop z)‖≤e*(spectralNorm T⁻¹*Real.sqrt 2) :=
    (Dop.le_opNorm (Iop z)).trans
      ((mul_le_mul_of_nonneg_right herror (norm_nonneg (Iop z))).trans
        (mul_le_mul_of_nonneg_left hi he0))
  have ht : ‖Top (Dop (Iop z))‖≤spectralNorm T*e*(spectralNorm T⁻¹*Real.sqrt 2) := by
    have hp : ‖Top (Dop (Iop z))‖≤spectralNorm T*‖Dop (Iop z)‖ := Top.le_opNorm _
    exact hp.trans (by simpa only [mul_assoc] using mul_le_mul_of_nonneg_left hd ht0)
  dsimp only
  rw [conjugate_action]
  calc
    _≤Real.sqrt 2*‖Top (Dop (Iop z))‖ := combined_output_le_sqrt_two _
    _≤Real.sqrt 2*(spectralNorm T*e*(spectralNorm T⁻¹*Real.sqrt 2)) :=
      mul_le_mul_of_nonneg_left ht (Real.sqrt_nonneg 2)
    _=(Real.sqrt 2)^2*(spectralNorm T*spectralNorm T⁻¹*e) := by ring
    _=2*spectralNorm T*spectralNorm T⁻¹*e := by
      rw [Real.sq_sqrt (by norm_num : (0 : ℝ)≤2)]
      ring

/-- The same pointwise bound applies to transforms selected after seeing arbitrary data. -/
theorem data_selected_transformed_error {Ω : Type*}
    (T Delta : Ω → Matrix (Unit ⊕ D) (Unit ⊕ D) ℝ) (e : Ω → ℝ)
    (herror : ∀ ω,spectralNorm (Delta ω)≤e ω) (ω : Ω)
    (v : EuclideanSpace ℝ D) (hv : ‖v‖≤1) :
    let y := Matrix.toEuclideanCLM (𝕜 := ℝ) (T ω*Delta ω*(T ω)⁻¹) (wholeInput v)
    |massPart y|+‖spatialPart y‖≤2*spectralNorm (T ω)*spectralNorm (T ω)⁻¹*e ω :=
  transformed_combined_error (T ω) (Delta ω) (e ω) (herror ω) v hv
end EuclideanError

end Komorebi.LSM.DataSelectedGeometry
