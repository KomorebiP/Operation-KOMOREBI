module

public import KomorebiPhysics.Relativistic3DL2CellReconstruction
public import Mathlib.Probability.ProductMeasure
public import Mathlib.Probability.Distributions.Uniform
public import Mathlib.MeasureTheory.Measure.SeparableMeasure

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped BigOperators ENNReal NNReal MeasureTheory InnerProductSpace Topology
open MeasureTheory WithLp Set Finset

namespace KomorebiPhysics
namespace Relativistic3DWeightedDyadicReconstruction

universe uΩ uI uE

variable {Ω : Type uΩ} {I : Type uI} {E : Type uE}
variable [MeasurableSpace Ω] [Fintype I] [DecidableEq I]
variable [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]
variable (μ : Measure Ω)

/-- A finite measurable partition whose cells all have the same positive volume. -/
structure EqualVolumePartition where
  cell : I → Set Ω
  measurable_cell : ∀ i, MeasurableSet (cell i)
  finite_cell : ∀ i, μ (cell i) ≠ ∞
  cellVolume : ℝ
  cellVolume_pos : 0 < cellVolume
  equal_volume : ∀ i, μ.real (cell i) = cellVolume
  disjoint_cell : ∀ {i j}, i ≠ j → Disjoint (cell i) (cell j)
  cover : (⋃ i, cell i) = Set.univ

abbrev CellState := PiLp 2 (fun _ : I => E)
abbrev ContinuumState := Lp E 2 μ

namespace EqualVolumePartition

variable (P : EqualVolumePartition (μ := μ) (I := I))

/-- The normalization converting physical cell values into `L²`-normalized coefficients. -/
def normalization : ℝ := (Real.sqrt P.cellVolume)⁻¹

omit [Fintype I] [DecidableEq I] in
@[simp] theorem normalization_pos : 0 < P.normalization := by
  simp [normalization, P.cellVolume_pos]

omit [Fintype I] [DecidableEq I] in
@[simp] theorem normalization_sq_mul_volume : P.normalization ^ 2 * P.cellVolume = 1 := by
  rw [normalization, inv_pow, Real.sq_sqrt (le_of_lt P.cellVolume_pos)]
  exact inv_mul_cancel₀ P.cellVolume_pos.ne'

/-- Constant-vector interpolation on one cell before volume normalization. -/
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

/-- Scalar normalization by the inverse square-root cell volume. -/
def normalizationLinear : E →ₗ[ℂ] E where
  toFun v := (P.normalization : ℂ) • v
  map_add' v w := smul_add _ _ _
  map_smul' c v := by
    rw [smul_smul, smul_smul, mul_comm]
    simp only [RingHom.id_apply]

/-- A normalized constant vector supported on one equal-volume cell. -/
def normalizedCellIndicatorLinear (i : I) : E →ₗ[ℂ] Lp E 2 μ :=
  (cellIndicatorLinear μ P i).comp (P.normalizationLinear μ)

/-- Measure-correct piecewise-constant interpolation. -/
def stepLinear : PiLp 2 (fun _ : I => E) →ₗ[ℂ] Lp E 2 μ :=
  ∑ i, (normalizedCellIndicatorLinear μ P i).comp
    (PiLp.proj (𝕜 := ℂ) 2 (fun _ : I => E) i).toLinearMap

omit [DecidableEq I] [CompleteSpace E] in
@[simp] theorem stepLinear_apply (ψ : PiLp 2 (fun _ : I => E)) :
    P.stepLinear μ ψ =
      ∑ i, indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i)
        ((P.normalization : ℂ) • ψ i) := by
  simp [stepLinear, normalizedCellIndicatorLinear, normalizationLinear, cellIndicatorLinear]

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
theorem inner_normalizedCellIndicator (i j : I) (v w : E) :
    inner ℂ
      (indicatorConstLp 2 (P.measurable_cell i) (P.finite_cell i)
        ((P.normalization : ℂ) • v))
      (indicatorConstLp 2 (P.measurable_cell j) (P.finite_cell j)
        ((P.normalization : ℂ) • w)) =
      if i = j then inner ℂ v w else 0 := by
  rw [MeasureTheory.L2.inner_indicatorConstLp_indicatorConstLp
    (hμs := P.finite_cell i) (hμt := P.finite_cell j)]
  split
  next hij =>
    subst j
    rw [Set.inter_self, P.equal_volume]
    simp only [inner_smul_left, inner_smul_right, Complex.conj_ofReal]
    have hr : P.cellVolume * P.normalization ^ 2 = 1 := by
      rw [mul_comm]
      exact P.normalization_sq_mul_volume
    have hc : (P.cellVolume : ℂ) * (P.normalization : ℂ) ^ 2 = 1 := by
      exact_mod_cast hr
    rw [RCLike.real_smul_eq_coe_mul]
    calc
      (P.cellVolume : ℂ) *
          ((P.normalization : ℂ) * ((P.normalization : ℂ) * inner ℂ v w)) =
          ((P.cellVolume : ℂ) * (P.normalization : ℂ) ^ 2) * inner ℂ v w := by ring
      _ = inner ℂ v w := by rw [hc, one_mul]
  next hij =>
    rw [P.real_inter_eq_zero_of_ne μ hij]
    simp

/-- Equal-volume interpolation is an exact `L²` isometry. -/
theorem step_inner (ψ φ : PiLp 2 (fun _ : I => E)) :
    inner ℂ (P.stepLinear μ ψ) (P.stepLinear μ φ) = inner ℂ ψ φ := by
  rw [P.stepLinear_apply μ, P.stepLinear_apply μ]
  simp_rw [inner_sum, sum_inner, P.inner_normalizedCellIndicator μ]
  simp [PiLp.inner_apply]

/-- The normalized equal-volume interpolation as a linear isometry. -/
def stepIsometry : PiLp 2 (fun _ : I => E) →ₗᵢ[ℂ] Lp E 2 μ :=
  (P.stepLinear μ).isometryOfInner (P.step_inner μ)


end EqualVolumePartition

/-! ## The octree address continuum

`Address = ℕ → Fin 8` records one of eight three-dimensional child cubes at
successive dyadic scales.  The product probability measure assigns volume
`8⁻ⁿ` to every level-`n` prefix cell.
-/

namespace Octree

abbrev Octant := Fin 8

instance : MeasurableSpace Octant := ⊤

instance : MeasurableSingletonClass Octant :=
  ⟨fun _ => by simp⟩

/-- Uniform probability measure on the eight children of one cube. -/
noncomputable def octantMeasure : Measure Octant :=
  (PMF.uniformOfFintype Octant).toMeasure

noncomputable instance octantMeasure_probability :
    IsProbabilityMeasure octantMeasure := by
  unfold octantMeasure
  infer_instance

/-- Infinite octree addresses. -/
abbrev Address := ℕ → Octant

/-- Product probability measure on the octree address continuum. -/
noncomputable def octreeMeasure : Measure Address :=
  Measure.infinitePi (fun _ : ℕ => octantMeasure)

noncomputable instance octreeMeasure_probability :
    IsProbabilityMeasure octreeMeasure := by
  unfold octreeMeasure
  infer_instance

/-- A level-`n` octree prefix. -/
abbrev Prefix (n : ℕ) := (i : Finset.range n) → Octant

/-- The cylinder cell determined by a finite octree prefix. -/
def prefixCell (n : ℕ) (a : Prefix n) : Set Address :=
  cylinder (Finset.range n) {a}

/-- Side length of one level-`n` dyadic cube. -/
def meshSide (n : ℕ) : ℝ := ((2 : ℝ)⁻¹) ^ n

/-- Physical volume of one level-`n` cell. -/
def prefixVolume (n : ℕ) : ℝ := ((8 : ℝ)⁻¹) ^ n

@[simp] theorem meshSide_pos (n : ℕ) : 0 < meshSide n := by
  simp [meshSide]

@[simp] theorem prefixVolume_pos (n : ℕ) : 0 < prefixVolume n := by
  simp [prefixVolume]


/-- Halving the mesh divides every side length by two. -/
theorem meshSide_succ (n : ℕ) : meshSide (n + 1) = meshSide n / 2 := by
  simp [meshSide, pow_succ, div_eq_mul_inv, mul_comm]

/-- One three-dimensional refinement divides cell volume by eight. -/
theorem prefixVolume_succ (n : ℕ) : prefixVolume (n + 1) = prefixVolume n / 8 := by
  simp [prefixVolume, pow_succ, div_eq_mul_inv, mul_comm]

/-- The octree volume is the cube of the dyadic side length. -/
theorem prefixVolume_eq_meshSide_cube (n : ℕ) :
    prefixVolume n = meshSide n ^ 3 := by
  rw [prefixVolume, meshSide]
  calc
    ((8 : ℝ)⁻¹) ^ n = (((2 : ℝ)⁻¹) ^ 3) ^ n := by norm_num
    _ = ((2 : ℝ)⁻¹) ^ (3 * n) := by rw [pow_mul]
    _ = ((2 : ℝ)⁻¹) ^ (n * 3) := by rw [Nat.mul_comm]
    _ = (((2 : ℝ)⁻¹) ^ n) ^ 3 := by rw [pow_mul]

/-- A level-`n` octree partition has exactly `8ⁿ` cells. -/
theorem card_prefix (n : ℕ) : Fintype.card (Prefix n) = 8 ^ n := by
  simp [Prefix]

@[simp] theorem octantMeasure_singleton (x : Octant) :
    octantMeasure {x} = (8 : ℝ≥0∞)⁻¹ := by
  have h := PMF.toMeasure_uniformOfFintype_apply
    (α := Octant) ({x} : Set Octant) (by measurability)
  change octantMeasure {x} = _
  rw [octantMeasure]
  convert h using 1
  all_goals norm_num

@[measurability] theorem measurable_prefixCell (n : ℕ) (a : Prefix n) :
    MeasurableSet (prefixCell n a) := by
  exact MeasurableSet.of_mem_measurableCylinders
    (cylinder_mem_measurableCylinders _ _ (by measurability))

@[simp] theorem octreeMeasure_prefixCell (n : ℕ) (a : Prefix n) :
    octreeMeasure (prefixCell n a) = ((8 : ℝ≥0∞)⁻¹) ^ n := by
  have hcyl := Measure.infinitePi_cylinder
    (μ := fun _ : ℕ => octantMeasure)
    (s := Finset.range n) (S := ({a} : Set (Prefix n))) (by measurability)
  rw [octreeMeasure, prefixCell, hcyl]
  have hsingle :
      ({a} : Set (Prefix n)) =
        Set.univ.pi (fun i => ({a i} : Set Octant)) := by
    ext b
    simp [funext_iff]
  rw [hsingle, Measure.pi_pi]
  simp [octantMeasure]

@[simp] theorem octreeMeasureReal_prefixCell (n : ℕ) (a : Prefix n) :
    octreeMeasure.real (prefixCell n a) = prefixVolume n := by
  rw [Measure.real, octreeMeasure_prefixCell, prefixVolume,
    ENNReal.toReal_pow, ENNReal.toReal_inv]
  norm_num

omit [MeasurableSpace Ω] [Fintype I] [DecidableEq I]
    [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E] in
 theorem prefixCell_disjoint (n : ℕ) {a b : Prefix n} (hab : a ≠ b) :
    Disjoint (prefixCell n a) (prefixCell n b) := by
  rw [Set.disjoint_left]
  intro x hxa hxb
  have ha : (Finset.range n).restrict x = a := by
    simpa [prefixCell, cylinder] using hxa
  have hb : (Finset.range n).restrict x = b := by
    simpa [prefixCell, cylinder] using hxb
  exact hab (ha.symm.trans hb)

omit [MeasurableSpace Ω] [Fintype I] [DecidableEq I]
    [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E] in
 theorem iUnion_prefixCell (n : ℕ) :
    (⋃ a : Prefix n, prefixCell n a) = Set.univ := by
  ext x
  simp [prefixCell, cylinder]

/-- The equal-volume measurable partition by level-`n` prefix cells. -/
def prefixPartition (n : ℕ) :
    EqualVolumePartition (μ := octreeMeasure) (I := Prefix n) where
  cell := prefixCell n
  measurable_cell := measurable_prefixCell n
  finite_cell := fun a => by
    rw [octreeMeasure_prefixCell]
    finiteness
  cellVolume := prefixVolume n
  cellVolume_pos := prefixVolume_pos n
  equal_volume := octreeMeasureReal_prefixCell n
  disjoint_cell := prefixCell_disjoint n
  cover := iUnion_prefixCell n

/-- Measure-correct level-`n` reconstruction into continuum `L²`. -/
def prefixStepIsometry (n : ℕ) :
    PiLp 2 (fun _ : Prefix n => E) →ₗᵢ[ℂ] Lp E 2 octreeMeasure :=
  (prefixPartition n).stepIsometry octreeMeasure

/-- Prefix coordinates indexed by the initial segment `0, …, a`. -/
abbrev InitialPrefix (a : ℕ) := (i : Finset.Iic a) → Octant

/-- A measurable cylinder depending only on the first `a + 1` octree digits. -/
def initialCylinder (a : ℕ) (S : Set (InitialPrefix a)) : Set Address :=
  cylinder (Finset.Iic a) S

/-- Constant-vector cylinder indicators at one finite prefix depth. -/
noncomputable def initialLevelIndicatorSet (a : ℕ) :
    Set (Lp E 2 octreeMeasure) :=
  {f | ∃ (S : Set (InitialPrefix a)) (hS : MeasurableSet S) (c : E),
      f = indicatorConstLp 2 hS.cylinder
        (measure_ne_top octreeMeasure (initialCylinder a S)) c}

/-- The finite-prefix step subspace at depth `a + 1`. -/
noncomputable def initialLevelSubmodule (a : ℕ) :
    Submodule ℂ (Lp E 2 octreeMeasure) :=
  Submodule.span ℂ (initialLevelIndicatorSet (E := E) a)

omit [CompleteSpace E] in
/-- Initial-prefix step spaces are nested with refinement depth. -/
theorem initialLevelSubmodule_mono {a b : ℕ} (hab : a ≤ b) :
    initialLevelSubmodule (E := E) a ≤ initialLevelSubmodule (E := E) b := by
  apply Submodule.span_le.2
  intro f hf
  rcases hf with ⟨S, hS, c, rfl⟩
  let hsub : Finset.Iic a ⊆ Finset.Iic b := Finset.Iic_subset_Iic.2 hab
  let T : Set (InitialPrefix b) :=
    Finset.restrict₂ (π := fun _ : ℕ => Octant) hsub ⁻¹' S
  have hT : MeasurableSet T :=
    (Finset.measurable_restrict₂ (X := fun _ : ℕ => Octant) hsub) hS
  have hcyl : initialCylinder a S = initialCylinder b T := by
    ext x
    simp [initialCylinder, T, cylinder, Finset.restrict₂_def, Finset.restrict_def]
  apply Submodule.subset_span
  refine ⟨T, hT, c, ?_⟩
  rw [Lp.ext_iff]
  filter_upwards [
    indicatorConstLp_coeFn (p := (2 : ℝ≥0∞))
      (hs := hS.cylinder)
      (hμs := measure_ne_top octreeMeasure (initialCylinder a S)) (c := c),
    indicatorConstLp_coeFn (p := (2 : ℝ≥0∞))
      (hs := hT.cylinder)
      (hμs := measure_ne_top octreeMeasure (initialCylinder b T)) (c := c)
  ] with x hx hy
  rw [hx, hy]
  exact congrArg (fun s : Set Address => s.indicator (fun _ => c) x) hcyl

/-- The algebraic union of all finite-prefix step subspaces. -/
noncomputable def finitePrefixSubmodule : Submodule ℂ (Lp E 2 octreeMeasure) :=
  ⨆ a : ℕ, initialLevelSubmodule (E := E) a

omit [CompleteSpace E] in
/-- Membership in the finite-prefix union occurs at one finite depth. -/
theorem mem_finitePrefixSubmodule_iff {f : Lp E 2 octreeMeasure} :
    f ∈ finitePrefixSubmodule (E := E) ↔
      ∃ a : ℕ, f ∈ initialLevelSubmodule (E := E) a := by
  rw [finitePrefixSubmodule]
  exact Submodule.mem_iSup_of_directed _
    (fun a b => ⟨max a b,
      initialLevelSubmodule_mono (E := E) (le_max_left _ _),
      initialLevelSubmodule_mono (E := E) (le_max_right _ _)⟩)

/-- Measurable finite-coordinate cylinders are measure-dense for the octree product measure. -/
theorem measurableCylinders_measureDense :
    octreeMeasure.MeasureDense (measurableCylinders (fun _ : ℕ => Octant)) := by
  apply Measure.MeasureDense.of_generateFrom_isSetAlgebra_finite
    (μ := octreeMeasure) isSetAlgebra_measurableCylinders
  simpa using
    (generateFrom_measurableCylinders (α := fun _ : ℕ => Octant)).symm

instance factTwoNeTop : Fact ((2 : ℝ≥0∞) ≠ ∞) := ⟨by norm_num⟩

omit [CompleteSpace E] in
/-- Finite-prefix octree step functions are dense in continuum `L²`. -/
theorem finitePrefixSubmodule_dense :
    Dense (finitePrefixSubmodule (E := E) : Set (Lp E 2 octreeMeasure)) := by
  let hMD := measurableCylinders_measureDense
  let M := finitePrefixSubmodule (E := E)
  rw [Submodule.dense_iff_topologicalClosure_eq_top]
  apply le_antisymm le_top
  intro f _hf
  refine Lp.induction (p := (2 : ℝ≥0∞)) (μ := octreeMeasure)
    (by norm_num) (motive := fun g => g ∈ M.topologicalClosure) ?_ ?_
    M.isClosed_topologicalClosure f
  · intro c s hs hμs
    have hcl := hMD.indicatorConstLp_subset_closure (p := (2 : ℝ≥0∞)) c
      ⟨s, hs, hμs.ne, rfl⟩
    apply (closure_minimal _ M.isClosed_topologicalClosure) hcl
    intro g hg
    rcases hg with ⟨s, hs, hfin, rfl⟩
    rw [measurableCylinders_nat] at hs
    simp only [Set.mem_iUnion, Set.mem_singleton_iff] at hs
    rcases hs with ⟨a, S, hS, rfl⟩
    apply M.le_topologicalClosure
    apply (le_iSup (fun n : ℕ => initialLevelSubmodule (E := E) n) a)
    apply Submodule.subset_span
    exact ⟨S, hS, c, rfl⟩
  · intro f g hf hg hdis hfM hgM
    exact M.topologicalClosure.add_mem hfM hgM

omit [CompleteSpace E] in
/-- Every continuum `L²` state has a finite-depth octree-step approximation. -/
theorem exists_initialLevel_approx (f : Lp E 2 octreeMeasure)
    {ε : ℝ} (hε : 0 < ε) :
    ∃ a : ℕ, ∃ g : Lp E 2 octreeMeasure,
      g ∈ initialLevelSubmodule (E := E) a ∧ dist g f < ε := by
  obtain ⟨g, hg, hdist⟩ :=
    Metric.mem_closure_iff.1 (finitePrefixSubmodule_dense (E := E) f) ε hε
  obtain ⟨a, ha⟩ := mem_finitePrefixSubmodule_iff (E := E).1 hg
  exact ⟨a, g, ha, by simpa [dist_comm] using hdist⟩

end Octree

end Relativistic3DWeightedDyadicReconstruction
end KomorebiPhysics
