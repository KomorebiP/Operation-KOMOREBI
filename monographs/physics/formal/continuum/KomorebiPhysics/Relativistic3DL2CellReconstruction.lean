module

public import KomorebiPhysics.Relativistic3DRegularConnection
public import Mathlib.MeasureTheory.Function.L2Space
public import Mathlib.Analysis.InnerProductSpace.PiL2
public import Mathlib.Analysis.InnerProductSpace.Adjoint
public import Mathlib.MeasureTheory.Integral.Bochner.Set

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped BigOperators ENNReal NNReal MeasureTheory InnerProductSpace Topology
open MeasureTheory WithLp

namespace KomorebiPhysics
namespace Relativistic3DL2CellReconstruction

/-!
# Finite-cell reconstruction inside genuine `L²`

This block constructs a concrete continuum Hilbert reconstruction for a finite
partition by pairwise-disjoint measurable unit-volume cells.  The discrete
coefficients are cell-normalized amplitudes.  Their step-function interpolation
is an exact isometry into `Lp E 2 μ`; its Hilbert adjoint is cell integration;
and their composite is the orthogonal projection onto the finite step subspace.

The block also proves a best-approximation theorem and an approximation-to-
projection convergence criterion.  It deliberately does not claim that a
specific dyadic cubical family is dense.  That geometric density theorem is the
next independent obligation.
-/

universe uΩ uI uE

variable {Ω : Type uΩ} {I : Type uI} {E : Type uE}
variable [MeasurableSpace Ω] [Fintype I] [DecidableEq I]
variable [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]
variable (μ : Measure Ω)

structure UnitVolumePartition where
  cell : I → Set Ω
  measurable_cell : ∀ i, MeasurableSet (cell i)
  finite_cell : ∀ i, μ (cell i) ≠ ∞
  unit_cell : ∀ i, μ.real (cell i) = 1
  disjoint_cell : ∀ {i j}, i ≠ j → Disjoint (cell i) (cell j)
  cover : (⋃ i, cell i) = Set.univ

abbrev CellState := PiLp 2 (fun _ : I => E)
abbrev ContinuumState := Lp E 2 μ

namespace UnitVolumePartition

variable (P : UnitVolumePartition (μ := μ) (I := I))

/-- Constant vector supported on one cell. -/
def cellIndicatorLinear (i : I) : E →ₗ[ℂ] Lp E 2 μ where
  toFun v := indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i) v
  map_add' v w := (indicatorConstLp_add).symm
  map_smul' c v := by
    rw [Lp.ext_iff]
    filter_upwards [
      indicatorConstLp_coeFn (p := (2 : ℝ≥0∞))
        (hs := P.measurable_cell i) (hμs := P.finite_cell i) (c := c • v),
      Lp.coeFn_smul c
        (indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i) v),
      indicatorConstLp_coeFn (p := (2 : ℝ≥0∞))
        (hs := P.measurable_cell i) (hμs := P.finite_cell i) (c := v)
    ] with x hx hsmul hv
    by_cases hxi : x ∈ P.cell i
    · simp [hx, hsmul, hv, hxi]
    · simp [hx, hsmul, hv, hxi]

/-- Piecewise-constant interpolation into genuine `L²`. -/
def stepLinear : PiLp 2 (fun _ : I => E) →ₗ[ℂ] Lp E 2 μ :=
  ∑ i, (cellIndicatorLinear μ P i).comp (PiLp.proj (𝕜 := ℂ) 2 (fun _ : I => E) i).toLinearMap

omit [DecidableEq I] [CompleteSpace E] in
@[simp] theorem stepLinear_apply (ψ : PiLp 2 (fun _ : I => E)) :
    stepLinear μ P ψ = ∑ i, indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i) (ψ i) := by
  simp [stepLinear, cellIndicatorLinear]

omit [Fintype I] [DecidableEq I] in
theorem real_inter_eq_zero_of_ne {i j : I} (hij : i ≠ j) :
    μ.real (P.cell i ∩ P.cell j) = 0 := by
  have hd := P.disjoint_cell hij
  have hset : P.cell i ∩ P.cell j = ∅ := by
    ext x
    constructor
    · intro hx
      exact False.elim ((Set.disjoint_left.1 hd) hx.1 hx.2)
    · intro hx
      cases hx
  rw [hset]
  simp

omit [Fintype I] in
theorem inner_cellIndicator (i j : I) (v w : E) :
    inner ℂ
      (indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i) v)
      (indicatorConstLp 2 (P.measurable_cell j) (P.finite_cell j) w) =
      if i = j then inner ℂ v w else 0 := by
  rw [MeasureTheory.L2.inner_indicatorConstLp_indicatorConstLp
    (hμs := P.finite_cell i) (hμt := P.finite_cell j)]
  by_cases hij : i = j
  · subst j
    simp [P.unit_cell]
  · simp [hij, (real_inter_eq_zero_of_ne (μ := μ) P hij)]

theorem step_inner (ψ φ : PiLp 2 (fun _ : I => E)) :
    inner ℂ (stepLinear μ P ψ) (stepLinear μ P φ) = inner ℂ ψ φ := by
  rw [stepLinear_apply (μ := μ) P, stepLinear_apply (μ := μ) P]
  simp_rw [inner_sum, sum_inner, inner_cellIndicator (μ := μ) P]
  simp [PiLp.inner_apply]

/-- The step reconstruction is an exact linear isometry. -/
def stepIsometry : PiLp 2 (fun _ : I => E) →ₗᵢ[ℂ] Lp E 2 μ :=
  stepLinear μ P |>.isometryOfInner (step_inner (μ := μ) P)



omit [CompleteSpace E] in
theorem inner_single_left (i : I) (v : E) (ψ : PiLp 2 (fun _ : I => E)) :
    inner ℂ (PiLp.single 2 i v) ψ = inner ℂ v (ψ i) := by
  rw [PiLp.inner_apply, Finset.sum_eq_single i]
  · simp
  · intro j _ hji
    simp [hji]
  · simp

/-- Interpolation of one coordinate is its constant cell indicator. -/
theorem step_single (i : I) (v : E) :
    stepIsometry μ P (PiLp.single 2 i v) =
      indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i) v := by
  change stepLinear μ P (PiLp.single 2 i v) = _
  rw [stepLinear_apply (μ := μ) P, Finset.sum_eq_single i]
  · simp
  · intro j _ hji
    have hs : (PiLp.single 2 i v : PiLp 2 (fun _ : I => E)) j = 0 := by simp [hji]
    rw [hs]
    change (cellIndicatorLinear μ P j) 0 = 0
    exact map_zero (cellIndicatorLinear μ P j)
  · simp

/-- Cell averaging, defined as the Hilbert adjoint of step interpolation. -/
def averagingCLM : Lp E 2 μ →L[ℂ] PiLp 2 (fun _ : I => E) :=
  ContinuousLinearMap.adjoint (stepIsometry μ P).toContinuousLinearMap

/-- Step interpolation followed by cell averaging is the identity. -/
@[simp] theorem averaging_step (ψ : PiLp 2 (fun _ : I => E)) :
    averagingCLM μ P (stepIsometry μ P ψ) = ψ := by
  apply ext_inner_left ℂ
  intro φ
  change inner ℂ φ
      (ContinuousLinearMap.adjoint (stepIsometry μ P).toContinuousLinearMap
        ((stepIsometry μ P).toContinuousLinearMap ψ)) = inner ℂ φ ψ
  rw [ContinuousLinearMap.adjoint_inner_right]
  exact step_inner (μ := μ) P φ ψ


/-- The adjoint coefficient is the Bochner integral over the corresponding cell. -/
theorem averaging_apply (f : Lp E 2 μ) (i : I) :
    averagingCLM μ P f i = ∫ x in P.cell i, f x ∂μ := by
  apply ext_inner_left ℂ
  intro v
  calc
    inner ℂ v (averagingCLM μ P f i) =
        inner ℂ (PiLp.single 2 i v) (averagingCLM μ P f) := by
          symm
          exact inner_single_left i v (averagingCLM μ P f)
    _ = inner ℂ ((stepIsometry μ P).toContinuousLinearMap (PiLp.single 2 i v)) f := by
          simpa [averagingCLM] using
            (ContinuousLinearMap.adjoint_inner_right
              (stepIsometry μ P).toContinuousLinearMap (PiLp.single 2 i v) f)
    _ = inner ℂ (stepIsometry μ P (PiLp.single 2 i v)) f := by rfl
    _ = inner ℂ
          (indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i) v) f := by
          rw [step_single (μ := μ) P]
    _ = inner ℂ v (∫ x in P.cell i, f x ∂μ) := by
          exact MeasureTheory.L2.inner_indicatorConstLp_eq_inner_setIntegral
            ℂ (P.measurable_cell i) (P.finite_cell i) v f

/-- Orthogonal projection onto the finite cell-step subspace. -/
def stepProjection : Lp E 2 μ →L[ℂ] Lp E 2 μ :=
  (stepIsometry μ P).toContinuousLinearMap.comp (averagingCLM μ P)


@[simp] theorem stepProjection_apply (f : Lp E 2 μ) :
    stepProjection μ P f = stepIsometry μ P (averagingCLM μ P f) := rfl

/-- The projection is the step function whose coefficients are the cell integrals. -/
theorem stepProjection_eq_sum_cellIntegrals (f : Lp E 2 μ) :
    stepProjection μ P f =
      ∑ i, indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i)
        (∫ x in P.cell i, f x ∂μ) := by
  rw [stepProjection_apply]
  change stepLinear μ P (averagingCLM μ P f) = _
  rw [stepLinear_apply (μ := μ) P]
  apply Finset.sum_congr rfl
  intro i _
  rw [averaging_apply (μ := μ) P]

@[simp] theorem stepProjection_step (ψ : PiLp 2 (fun _ : I => E)) :
    stepProjection μ P (stepIsometry μ P ψ) = stepIsometry μ P ψ := by
  simp [stepProjection]

@[simp] theorem stepProjection_idem (f : Lp E 2 μ) :
    stepProjection μ P (stepProjection μ P f) = stepProjection μ P f := by
  simp [stepProjection]

/-- The projection is self-adjoint. -/
theorem adjoint_stepProjection :
    ContinuousLinearMap.adjoint (stepProjection (E := E) μ P) =
      stepProjection (E := E) μ P := by
  simp [stepProjection, averagingCLM, ContinuousLinearMap.adjoint_comp]

/-- The projection residual is orthogonal to every finite cell-step state. -/
theorem inner_step_residual (ψ : PiLp 2 (fun _ : I => E)) (f : Lp E 2 μ) :
    inner ℂ (stepIsometry μ P ψ) (f - stepProjection μ P f) = 0 := by
  change inner ℂ ((stepIsometry μ P).toContinuousLinearMap ψ)
      (f - stepProjection μ P f) = 0
  rw [← ContinuousLinearMap.adjoint_inner_right
    (stepIsometry μ P).toContinuousLinearMap ψ (f - stepProjection μ P f)]
  change inner ℂ ψ (averagingCLM μ P (f - stepProjection μ P f)) = 0
  simp [stepProjection]


/-- Pythagorean decomposition into the step projection and its orthogonal residual. -/
theorem norm_sq_stepProjection_add_residual (f : Lp E 2 μ) :
    ‖f‖ ^ 2 = ‖stepProjection μ P f‖ ^ 2 + ‖f - stepProjection μ P f‖ ^ 2 := by
  have horth : inner ℂ (stepProjection μ P f) (f - stepProjection μ P f) = 0 := by
    rw [stepProjection_apply]
    exact inner_step_residual (μ := μ) P (averagingCLM μ P f) f
  calc
    ‖f‖ ^ 2 = ‖stepProjection μ P f + (f - stepProjection μ P f)‖ ^ 2 := by
      congr 1
      abel
    _ = ‖stepProjection μ P f‖ ^ 2 + ‖f - stepProjection μ P f‖ ^ 2 := by
      simpa [pow_two] using
        norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero
          (stepProjection μ P f) (f - stepProjection μ P f) horth

/-- Orthogonal cell averaging is contractive in `L²`. -/
theorem norm_stepProjection_le (f : Lp E 2 μ) :
    ‖stepProjection μ P f‖ ≤ ‖f‖ := by
  have h := norm_sq_stepProjection_add_residual (μ := μ) P f
  nlinarith [sq_nonneg ‖f - stepProjection μ P f‖,
    norm_nonneg (stepProjection μ P f), norm_nonneg f]


/-- The orthogonal projection is the best approximation from the finite cell-step subspace. -/
theorem norm_residual_le_norm_sub_step (f : Lp E 2 μ)
    (ψ : PiLp 2 (fun _ : I => E)) :
    ‖f - stepProjection μ P f‖ ≤ ‖f - stepIsometry μ P ψ‖ := by
  have hstep : stepProjection μ P f - stepIsometry μ P ψ =
      stepIsometry μ P (averagingCLM μ P f - ψ) := by
    rw [stepProjection_apply]
    simp
  have horth : inner ℂ (stepProjection μ P f - stepIsometry μ P ψ)
      (f - stepProjection μ P f) = 0 := by
    rw [hstep]
    exact inner_step_residual (μ := μ) P (averagingCLM μ P f - ψ) f
  have hpyth : ‖f - stepIsometry μ P ψ‖ ^ 2 =
      ‖stepProjection μ P f - stepIsometry μ P ψ‖ ^ 2 +
        ‖f - stepProjection μ P f‖ ^ 2 := by
    calc
      ‖f - stepIsometry μ P ψ‖ ^ 2 =
          ‖(stepProjection μ P f - stepIsometry μ P ψ) +
            (f - stepProjection μ P f)‖ ^ 2 := by
            congr 1
            abel
      _ = ‖stepProjection μ P f - stepIsometry μ P ψ‖ ^ 2 +
          ‖f - stepProjection μ P f‖ ^ 2 := by
            simpa [pow_two] using
              norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero
                (stepProjection μ P f - stepIsometry μ P ψ)
                (f - stepProjection μ P f) horth
  nlinarith [sq_nonneg ‖stepProjection μ P f - stepIsometry μ P ψ‖,
    norm_nonneg (f - stepProjection μ P f),
    norm_nonneg (f - stepIsometry μ P ψ)]


/-- The orthogonal projection has operator norm at most one. -/
theorem norm_stepProjection_op_le_one :
    ‖stepProjection (E := E) μ P‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro f
  simpa using norm_stepProjection_le (μ := μ) P f

/-- Fixed points of the projection are exactly the finite cell-step states. -/
theorem stepProjection_eq_self_iff (f : Lp E 2 μ) :
    stepProjection μ P f = f ↔ ∃ ψ, stepIsometry μ P ψ = f := by
  constructor
  · intro h
    exact ⟨averagingCLM μ P f, by simpa using h⟩
  · rintro ⟨ψ, rfl⟩
    exact stepProjection_step (μ := μ) P ψ


section RefiningFamily

variable {ι : ℕ → Type uI}
variable [∀ n, Fintype (ι n)] [∀ n, DecidableEq (ι n)]
variable (Pseq : ∀ n, UnitVolumePartition (μ := μ) (I := ι n))

/-- If finite cell-step reconstructions approximate an `L²` state, then the
orthogonal cell-average projections converge to that state. This isolates the
remaining density obligation for a concrete dyadic family. -/
theorem stepProjection_tendsto_of_step_approximation
    (ψ : ∀ n, PiLp 2 (fun _ : ι n => E)) (f : Lp E 2 μ)
    (hψ : Filter.Tendsto
      (fun n => UnitVolumePartition.stepIsometry μ (Pseq n) (ψ n))
      Filter.atTop (𝓝 f)) :
    Filter.Tendsto
      (fun n => UnitVolumePartition.stepProjection μ (Pseq n) f)
      Filter.atTop (𝓝 f) := by
  rw [tendsto_iff_norm_sub_tendsto_zero]
  have happrox : Filter.Tendsto
      (fun n => ‖f - UnitVolumePartition.stepIsometry μ (Pseq n) (ψ n)‖)
      Filter.atTop (𝓝 0) := by
    have h := tendsto_iff_norm_sub_tendsto_zero.mp hψ
    simpa [norm_sub_rev] using h
  have hsqueeze : Filter.Tendsto
      (fun n => ‖f - UnitVolumePartition.stepProjection μ (Pseq n) f‖)
      Filter.atTop (𝓝 0) :=
    squeeze_zero
      (fun n => norm_nonneg _)
      (fun n => UnitVolumePartition.norm_residual_le_norm_sub_step
        (μ := μ) (Pseq n) f (ψ n))
      happrox
  simpa [norm_sub_rev] using hsqueeze

end RefiningFamily

end UnitVolumePartition



end Relativistic3DL2CellReconstruction
end KomorebiPhysics
