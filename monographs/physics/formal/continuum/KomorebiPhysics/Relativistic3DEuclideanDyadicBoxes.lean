module

public import KomorebiPhysics.Relativistic3DEuclideanDyadicProjection
public import Mathlib.MeasureTheory.Function.LpSpace.Indicator

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped BigOperators ENNReal NNReal MeasureTheory InnerProductSpace Topology unitInterval
open MeasureTheory Set Finset

namespace KomorebiPhysics
namespace Relativistic3DEuclideanDyadicBoxes

namespace Prev
abbrev Axis := Relativistic3DOctreeEuclideanCoding.Axis
abbrev Bit := Relativistic3DOctreeEuclideanCoding.Bit
abbrev Address := Relativistic3DWeightedDyadicReconstruction.Octree.Address
abbrev Prefix (n : ℕ) := Relativistic3DWeightedDyadicReconstruction.Octree.Prefix n
abbrev BitPrefix (n : ℕ) := Relativistic3DBinaryLebesgue.BitPrefix n
abbrev CubePoint := Prev.Axis → I
noncomputable abbrev octreeMeasure :=
  Relativistic3DWeightedDyadicReconstruction.Octree.octreeMeasure
noncomputable abbrev cubeVolume := Relativistic3DBinaryLebesgue.Cube.cubeVolume
end Prev

/-- The binary prefix in one Cartesian direction carried by an octree prefix. -/
def axisBitPrefix (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) : Prev.BitPrefix n :=
  fun k => Relativistic3DOctreeEuclideanCoding.bitsOfOctant (a k) i

/-- The dyadic grid code of one Cartesian coordinate of an octree prefix. -/
def axisCode (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) : ℕ :=
  Relativistic3DBinaryLebesgue.prefixCode n (axisBitPrefix n a i)

@[simp] theorem axisCode_lt (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    axisCode n a i < 2 ^ n := by
  exact Relativistic3DBinaryLebesgue.prefixCode_lt n (axisBitPrefix n a i)

/-- Left endpoint of the coordinate interval selected by a prefix. -/
def axisLowerReal (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) : ℝ :=
  (axisCode n a i : ℝ) / (2 : ℝ) ^ n

/-- Right endpoint of the closed coordinate interval selected by a prefix. -/
def axisUpperReal (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) : ℝ :=
  ((axisCode n a i + 1 : ℕ) : ℝ) / (2 : ℝ) ^ n

@[simp] theorem axisLowerReal_nonneg (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    0 ≤ axisLowerReal n a i := by
  unfold axisLowerReal
  exact div_nonneg (Nat.cast_nonneg _) (by positivity)

@[simp] theorem axisLowerReal_le_one (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    axisLowerReal n a i ≤ 1 := by
  have hpow : 0 < (2 : ℝ) ^ n := by positivity
  have hcode : (axisCode n a i : ℝ) < (2 : ℝ) ^ n := by
    exact_mod_cast axisCode_lt n a i
  exact (div_le_one hpow).2 hcode.le

@[simp] theorem axisUpperReal_nonneg (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    0 ≤ axisUpperReal n a i := by
  unfold axisUpperReal
  exact div_nonneg (Nat.cast_nonneg _) (by positivity)

@[simp] theorem axisUpperReal_le_one (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    axisUpperReal n a i ≤ 1 := by
  have hpow : 0 < (2 : ℝ) ^ n := by positivity
  have hcodeNat : axisCode n a i + 1 ≤ 2 ^ n := Nat.succ_le_iff.mpr (axisCode_lt n a i)
  have hcode : ((axisCode n a i + 1 : ℕ) : ℝ) ≤ (2 : ℝ) ^ n := by
    exact_mod_cast hcodeNat
  exact (div_le_one hpow).2 hcode

/-- Lower corner of the ordinary Euclidean dyadic box selected by a prefix. -/
def lowerCorner (n : ℕ) (a : Prev.Prefix n) : Prev.CubePoint :=
  fun i => ⟨axisLowerReal n a i, axisLowerReal_nonneg n a i, axisLowerReal_le_one n a i⟩

/-- Upper corner of the ordinary Euclidean dyadic box selected by a prefix. -/
def upperCorner (n : ℕ) (a : Prev.Prefix n) : Prev.CubePoint :=
  fun i => ⟨axisUpperReal n a i, axisUpperReal_nonneg n a i, axisUpperReal_le_one n a i⟩

/-- Ordinary closed Cartesian dyadic box corresponding to an octree prefix. -/
def dyadicBox (n : ℕ) (a : Prev.Prefix n) : Set Prev.CubePoint :=
  Set.Icc (lowerCorner n a) (upperCorner n a)

@[simp] theorem axisUpperReal_sub_lowerReal
    (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    axisUpperReal n a i - axisLowerReal n a i = ((2 : ℝ) ^ n)⁻¹ := by
  have hne : (2 : ℝ) ^ n ≠ 0 := by positivity
  simp only [axisUpperReal, axisLowerReal]
  push_cast
  field_simp
  ring

@[measurability] theorem measurable_dyadicBox (n : ℕ) (a : Prev.Prefix n) :
    MeasurableSet (dyadicBox n a) := by
  exact measurableSet_Icc

/-- Every coordinate side of a level-`n` box has dyadic width `2⁻ⁿ`. -/
theorem coordinate_volume_dyadicBox (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    volume (Set.Icc (lowerCorner n a i) (upperCorner n a i)) =
      ENNReal.ofReal (((2 : ℝ) ^ n)⁻¹) := by
  rw [unitInterval.volume_Icc]
  congr 1
  exact axisUpperReal_sub_lowerReal n a i

/-- A level-`n` ordinary dyadic box has Euclidean volume `8⁻ⁿ`. -/
theorem cubeVolume_dyadicBox (n : ℕ) (a : Prev.Prefix n) :
    Prev.cubeVolume (dyadicBox n a) = ((8 : ℝ≥0∞)⁻¹) ^ n := by
  have hbox : dyadicBox n a =
      Set.univ.pi (fun i : Prev.Axis =>
        Set.Icc (lowerCorner n a i) (upperCorner n a i)) := by
    ext x
    simp [dyadicBox, Set.mem_Icc]
  rw [hbox]
  change Measure.pi (fun _ : Prev.Axis => volume)
      (Set.univ.pi (fun i : Prev.Axis =>
        Set.Icc (lowerCorner n a i) (upperCorner n a i))) = _
  rw [Measure.pi_pi]
  simp only [coordinate_volume_dyadicBox]
  rw [Finset.prod_const, Finset.card_univ]
  change (ENNReal.ofReal (((2 : ℝ) ^ n)⁻¹)) ^ 3 = ((8 : ℝ≥0∞)⁻¹) ^ n
  apply (ENNReal.toReal_eq_toReal_iff' (by finiteness) (by finiteness)).mp
  rw [ENNReal.toReal_pow, ENNReal.toReal_pow]
  simp [ENNReal.toReal_inv]
  show (((2 : ℝ) ^ n) ^ 3 = (8 : ℝ) ^ n)
  calc
    ((2 : ℝ) ^ n) ^ 3 = (2 : ℝ) ^ (n * 3) := by rw [pow_mul]
    _ = (2 : ℝ) ^ (3 * n) := by rw [Nat.mul_comm]
    _ = ((2 : ℝ) ^ 3) ^ n := by rw [pow_mul]
    _ = (8 : ℝ) ^ n := by norm_num

/-- The coordinate stream of an address in a prefix cylinder has the prescribed
finite binary prefix. -/
theorem streamPrefix_coordinate_eq_axisBitPrefix
    {n : ℕ} {a : Prev.Prefix n} {x : Prev.Address}
    (hx : x ∈ Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell n a)
    (i : Prev.Axis) :
    Relativistic3DBinaryLebesgue.streamPrefix n
      (Relativistic3DOctreeEuclideanCoding.coordinateStream
        (Relativistic3DOctreeEuclideanCoding.addressBitEquiv x) i) =
      axisBitPrefix n a i := by
  have hx' : (Finset.range n).restrict x = a := by
    simpa [Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell] using hx
  funext k
  change Relativistic3DOctreeEuclideanCoding.bitsOfOctant (x k.1) i =
    Relativistic3DOctreeEuclideanCoding.bitsOfOctant (a k) i
  have hk : x k.1 = a k := by
    simpa [Finset.restrict_def] using congrFun hx' k
  rw [hk]

/-- The finite binary partial sum of a coordinate is exactly the lower endpoint
of its ordinary dyadic interval. -/
theorem binaryPartial_coordinate_eq_axisLowerReal
    {n : ℕ} {a : Prev.Prefix n} {x : Prev.Address}
    (hx : x ∈ Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell n a)
    (i : Prev.Axis) :
    Relativistic3DBinaryLebesgue.binaryPartial n
      (Relativistic3DOctreeEuclideanCoding.coordinateStream
        (Relativistic3DOctreeEuclideanCoding.addressBitEquiv x) i) =
      axisLowerReal n a i := by
  rw [Relativistic3DBinaryLebesgue.binaryPartial_eq_grid]
  rw [streamPrefix_coordinate_eq_axisBitPrefix hx i]
  rfl

@[simp] theorem axisUpperReal_eq_lower_add_width
    (n : ℕ) (a : Prev.Prefix n) (i : Prev.Axis) :
    axisUpperReal n a i = axisLowerReal n a i + ((2 : ℝ) ^ n)⁻¹ := by
  linarith [axisUpperReal_sub_lowerReal n a i]

/-- An octree prefix cylinder decodes inside its corresponding ordinary closed
dyadic box. -/
theorem prefixCell_subset_preimage_dyadicBox (n : ℕ) (a : Prev.Prefix n) :
    Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell n a ⊆
      Relativistic3DOctreeEuclideanCoding.octreeCubeCode ⁻¹' dyadicBox n a := by
  intro x hx
  change Relativistic3DOctreeEuclideanCoding.octreeCubeCode x ∈ dyadicBox n a
  rw [dyadicBox, Set.mem_Icc]
  constructor
  · intro i
    change axisLowerReal n a i ≤
      Relativistic3DOctreeEuclideanCoding.binaryValue
        (Relativistic3DOctreeEuclideanCoding.coordinateStream
          (Relativistic3DOctreeEuclideanCoding.addressBitEquiv x) i)
    rw [← binaryPartial_coordinate_eq_axisLowerReal hx i]
    exact Relativistic3DBinaryLebesgue.binaryPartial_le_binaryValue _ _
  · intro i
    change Relativistic3DOctreeEuclideanCoding.binaryValue
        (Relativistic3DOctreeEuclideanCoding.coordinateStream
          (Relativistic3DOctreeEuclideanCoding.addressBitEquiv x) i) ≤
      axisUpperReal n a i
    rw [axisUpperReal_eq_lower_add_width]
    rw [← binaryPartial_coordinate_eq_axisLowerReal hx i]
    exact Relativistic3DBinaryLebesgue.binaryValue_le_partial_add _ _

/-- Prefix cylinders and ordinary closed dyadic boxes have the same pullback
modulo the binary-boundary null set. -/
theorem prefixCell_ae_eq_preimage_dyadicBox (n : ℕ) (a : Prev.Prefix n) :
    Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell n a =ᵐ[Prev.octreeMeasure]
      Relativistic3DOctreeEuclideanCoding.octreeCubeCode ⁻¹' dyadicBox n a := by
  apply ae_eq_of_subset_of_measure_ge
  · exact prefixCell_subset_preimage_dyadicBox n a
  · rw [Relativistic3DBinaryLebesgue.Cube.octreeCubeCode_measurePreserving.measure_preimage
      (measurable_dyadicBox n a).nullMeasurableSet]
    rw [cubeVolume_dyadicBox]
    rw [Relativistic3DWeightedDyadicReconstruction.Octree.octreeMeasure_prefixCell]
  · exact (Relativistic3DWeightedDyadicReconstruction.Octree.measurable_prefixCell n a).nullMeasurableSet
  · finiteness


universe uE
variable {E : Type uE} [NormedAddCommGroup E]

/-- Constant `L²` field supported on one octree prefix cylinder. -/
noncomputable def octreePrefixIndicator (n : ℕ) (a : Prev.Prefix n) (c : E) :
    Lp E 2 Prev.octreeMeasure :=
  indicatorConstLp 2
    (Relativistic3DWeightedDyadicReconstruction.Octree.measurable_prefixCell n a)
    (by
      rw [Relativistic3DWeightedDyadicReconstruction.Octree.octreeMeasure_prefixCell]
      finiteness) c

/-- Constant Euclidean `L²` field supported on the corresponding closed dyadic box. -/
noncomputable def euclideanBoxIndicator (n : ℕ) (a : Prev.Prefix n) (c : E) :
    Lp E 2 Prev.cubeVolume :=
  indicatorConstLp 2 (measurable_dyadicBox n a)
    (by rw [cubeVolume_dyadicBox]; finiteness) c

/-- Indicators supported on almost-everywhere equal finite-measure sets define the same
`L²` vector, including the zero-vector case. -/
theorem indicatorConstLp_eq_of_ae_eq
    {α : Type*} [MeasurableSpace α] {μ : Measure α}
    {s t : Set α} (hs : MeasurableSet s) (ht : MeasurableSet t)
    (hμs : μ s ≠ ∞) (hμt : μ t ≠ ∞) (c : E)
    (hst : s =ᵐ[μ] t) :
    indicatorConstLp 2 hs hμs c = indicatorConstLp 2 ht hμt c := by
  by_cases hc : c = 0
  · subst c
    simp [indicatorConstLp]
  · exact (indicatorConstLp_inj hs hμs ht hμt hc).2 hst

variable [InnerProductSpace ℂ E]

/-- Pulling an ordinary dyadic-box indicator back along the octree decoder gives
exactly the corresponding prefix-cylinder vector in `L²`. -/
theorem cubePullback_euclideanBoxIndicator
    (n : ℕ) (a : Prev.Prefix n) (c : E) :
    Relativistic3DEuclideanDyadicProjection.cubePullback (E := E)
        (euclideanBoxIndicator n a c) =
      octreePrefixIndicator n a c := by
  change Lp.compMeasurePreserving
      Relativistic3DOctreeEuclideanCoding.octreeCubeCode
      Relativistic3DBinaryLebesgue.Cube.octreeCubeCode_measurePreserving
      (indicatorConstLp 2 (measurable_dyadicBox n a)
        (by rw [cubeVolume_dyadicBox]; finiteness) c) =
    indicatorConstLp 2
      (Relativistic3DWeightedDyadicReconstruction.Octree.measurable_prefixCell n a)
      (by finiteness) c
  rw [Lp.indicatorConstLp_compMeasurePreserving]
  apply indicatorConstLp_eq_of_ae_eq
  exact (prefixCell_ae_eq_preimage_dyadicBox n a).symm

/-- The Hilbert adjoint transports a prefix-cylinder vector to the ordinary
Euclidean dyadic-box indicator. -/
theorem cubeAdjoint_octreePrefixIndicator
    [CompleteSpace E] (n : ℕ) (a : Prev.Prefix n) (c : E) :
    Relativistic3DEuclideanDyadicProjection.cubeAdjoint (E := E)
        (octreePrefixIndicator n a c) =
      euclideanBoxIndicator n a c := by
  rw [← cubePullback_euclideanBoxIndicator]
  exact Relativistic3DEuclideanDyadicProjection.cubeAdjoint_pullback
    (E := E) (euclideanBoxIndicator n a c)


/-- The canonical equivalence between indices `0 ≤ k ≤ d` and `0 ≤ k < d+1`. -/
def rangeSuccEquivIic (d : ℕ) : ↥(Finset.range (d + 1)) ≃ ↥(Finset.Iic d) where
  toFun i := ⟨i.1, Finset.mem_Iic.mpr (Nat.le_of_lt_succ (Finset.mem_range.mp i.2))⟩
  invFun i := ⟨i.1, Finset.mem_range.mpr (Nat.lt_succ_iff.mpr (Finset.mem_Iic.mp i.2))⟩
  left_inv _i := Subtype.ext rfl
  right_inv _i := Subtype.ext rfl

/-- Regard a range-indexed prefix of length `d+1` as an initial-segment prefix. -/
def prefixToInitial (d : ℕ) (a : Prev.Prefix (d + 1)) :
    Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d :=
  fun i => a ((rangeSuccEquivIic d).symm i)

/-- Convert an initial-segment prefix back to the range-indexed convention. -/
def initialToPrefix (d : ℕ)
    (a : Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d) :
    Prev.Prefix (d + 1) :=
  fun i => a (rangeSuccEquivIic d i)

@[simp] theorem initialToPrefix_prefixToInitial
    (d : ℕ) (a : Prev.Prefix (d + 1)) :
    initialToPrefix d (prefixToInitial d a) = a := by
  funext i
  simp [initialToPrefix, prefixToInitial]

@[simp] theorem prefixToInitial_initialToPrefix
    (d : ℕ)
    (a : Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d) :
    prefixToInitial d (initialToPrefix d a) = a := by
  funext i
  simp [initialToPrefix, prefixToInitial]

/-- The singleton initial cylinder is exactly the corresponding range-prefix cell. -/
theorem initialCylinder_singleton_eq_prefixCell
    (d : ℕ) (a : Prev.Prefix (d + 1)) :
    Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d
        ({prefixToInitial d a} : Set
          (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d)) =
      Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1) a := by
  ext x
  constructor
  · intro hx
    have hx' : (Finset.Iic d).restrict x = prefixToInitial d a := by
      simpa [Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder] using hx
    have hrange : (Finset.range (d + 1)).restrict x = a := by
      funext i
      have hi := congrFun hx' (rangeSuccEquivIic d i)
      change x i.1 = a i at hi
      exact hi
    simpa [Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell] using hrange
  · intro hx
    have hx' : (Finset.range (d + 1)).restrict x = a := by
      simpa [Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell] using hx
    have hIic : (Finset.Iic d).restrict x = prefixToInitial d a := by
      funext i
      have hi := congrFun hx' ((rangeSuccEquivIic d).symm i)
      change x i.1 = a ((rangeSuccEquivIic d).symm i) at hi
      exact hi
    simpa [Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder] using hIic


/-- Membership in a range-prefix cell is exactly equality of the corresponding
initial-prefix restriction. -/
@[simp] theorem mem_prefixCell_initialToPrefix_iff
    (d : ℕ)
    (p : Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d)
    (x : Prev.Address) :
    x ∈ Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1)
        (initialToPrefix d p) ↔
      (Finset.Iic d).restrict x = p := by
  rw [← initialCylinder_singleton_eq_prefixCell d (initialToPrefix d p)]
  simp [Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder]


/-- The finite collection of initial prefixes selected by a set. -/
noncomputable def initialPrefixFinset
    (d : ℕ)
    (S : Set (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d)) :
    Finset (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d) := by
  classical
  exact Finset.univ.filter (fun p => p ∈ S)

@[simp] theorem mem_initialPrefixFinset
    (d : ℕ)
    (S : Set (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d))
    (p : Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d) :
    p ∈ initialPrefixFinset d S ↔ p ∈ S := by
  classical
  simp [initialPrefixFinset]

omit [InnerProductSpace ℂ E] in
/-- A finite-prefix cylinder indicator is the exact finite sum of its singleton
prefix-cell indicators. -/
theorem initialCylinderIndicator_eq_sum_singletons
    (d : ℕ)
    (S : Set (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d))
    (hS : MeasurableSet S) (c : E) :
    indicatorConstLp 2 hS.cylinder
        (measure_ne_top Prev.octreeMeasure
          (Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d S)) c =
      ∑ p ∈ initialPrefixFinset d S,
        octreePrefixIndicator (d + 1) (initialToPrefix d p) c := by
  classical
  let T : Finset
      (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d) :=
    initialPrefixFinset d S
  have hpoint :
      (Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d S).indicator
          (fun _ => c) =
        (fun x => Finset.sum T (fun p =>
          (Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1)
            (initialToPrefix d p)).indicator (fun _ => c) x)) := by
    funext x
    let q : Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d :=
      (Finset.Iic d).restrict x
    by_cases hq : q ∈ S
    · have hqT : q ∈ T := by simpa [T] using hq
      have hxCylinder :
          x ∈ Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d S := by
        simpa [Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder, q]
      rw [Set.indicator_of_mem hxCylinder]
      rw [Finset.sum_eq_single q]
      · have hxq : x ∈ Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1)
            (initialToPrefix d q) :=
          (mem_prefixCell_initialToPrefix_iff d q x).2 rfl
        rw [Set.indicator_of_mem hxq]
      · intro p hpT hpne
        have hxnot : x ∉ Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1)
            (initialToPrefix d p) := by
          rw [mem_prefixCell_initialToPrefix_iff]
          intro hqp
          exact hpne hqp.symm
        rw [Set.indicator_of_notMem hxnot]
      · exact fun hnot => (hnot hqT).elim
    · have hxnotCylinder :
          x ∉ Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d S := by
        simpa [Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder, q]
      rw [Set.indicator_of_notMem hxnotCylinder]
      symm
      apply Finset.sum_eq_zero
      intro p hpT
      have hpS : p ∈ S := by simpa [T] using hpT
      have hxnot : x ∉ Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1)
          (initialToPrefix d p) := by
        rw [mem_prefixCell_initialToPrefix_iff]
        intro hqp
        apply hq
        have hqeq : q = p := by simpa [q] using hqp
        exact hqeq ▸ hpS
      rw [Set.indicator_of_notMem hxnot]
  have hsumAE :
      (fun x => Finset.sum T (fun p =>
          octreePrefixIndicator (d + 1) (initialToPrefix d p) c x)) =ᵐ[Prev.octreeMeasure]
        (fun x => Finset.sum T (fun p =>
          (Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1)
            (initialToPrefix d p)).indicator (fun _ => c) x)) := by
    induction T using Finset.induction_on with
    | empty => simp
    | @insert p T hp ih =>
        simp only [Finset.sum_insert hp]
        exact indicatorConstLp_coeFn.add ih
  rw [Lp.ext_iff]
  calc
    ⇑(indicatorConstLp 2 hS.cylinder
        (measure_ne_top Prev.octreeMeasure
          (Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d S)) c) =ᵐ[Prev.octreeMeasure]
        (Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d S).indicator
          (fun _ => c) := indicatorConstLp_coeFn
    _ =ᵐ[Prev.octreeMeasure] (fun x => Finset.sum T (fun p =>
          (Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1)
            (initialToPrefix d p)).indicator (fun _ => c) x)) :=
      Filter.EventuallyEq.of_eq hpoint
    _ =ᵐ[Prev.octreeMeasure] (fun x => Finset.sum T (fun p =>
          octreePrefixIndicator (d + 1) (initialToPrefix d p) c x)) := hsumAE.symm
    _ =ᵐ[Prev.octreeMeasure] ⇑(Finset.sum T (fun p =>
          octreePrefixIndicator (d + 1) (initialToPrefix d p) c)) :=
      (Lp.coeFn_fun_finsetSum T
        (fun p => octreePrefixIndicator (d + 1) (initialToPrefix d p) c)).symm

/-- Every singleton prefix-cylinder vector belongs to the corresponding finite-prefix
subspace used in Block 39. -/
theorem octreePrefixIndicator_mem_initialLevel
    (d : ℕ) (a : Prev.Prefix (d + 1)) (c : E) :
    octreePrefixIndicator (d + 1) a c ∈
      Relativistic3DWeightedDyadicReconstruction.Octree.initialLevelSubmodule
        (E := E) d := by
  apply Submodule.subset_span
  let p := prefixToInitial d a
  refine ⟨({p} : Set
      (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d)),
    measurableSet_singleton p, c, ?_⟩
  unfold octreePrefixIndicator
  apply indicatorConstLp_eq_of_ae_eq
  refine Filter.Eventually.of_forall (fun x => ?_)
  apply propext
  change x ∈ Relativistic3DWeightedDyadicReconstruction.Octree.prefixCell (d + 1) a ↔
    x ∈ Relativistic3DWeightedDyadicReconstruction.Octree.initialCylinder d ({p} : Set
      (Relativistic3DWeightedDyadicReconstruction.Octree.InitialPrefix d))
  rw [initialCylinder_singleton_eq_prefixCell]

/-- Every ordinary level-`d+1` dyadic-box indicator lies in the transported closed
Euclidean level `V_d` from Block 39. -/
theorem euclideanBoxIndicator_mem_euclideanLevel
    [CompleteSpace E] (d : ℕ) (a : Prev.Prefix (d + 1)) (c : E) :
    euclideanBoxIndicator (d + 1) a c ∈
      Relativistic3DEuclideanDyadicProjection.euclideanLevel (E := E) d := by
  rw [← cubeAdjoint_octreePrefixIndicator]
  exact Relativistic3DEuclideanDyadicProjection.cubeAdjoint_mem_euclideanLevel
    (E := E) (octreePrefixIndicator_mem_initialLevel d a c)


/-- Span of the singleton octree prefix-cell vectors at one finite depth. -/
noncomputable def octreeSingletonLevel (d : ℕ) :
    Submodule ℂ (Lp E 2 Prev.octreeMeasure) :=
  Submodule.span ℂ {f | ∃ a : Prev.Prefix (d + 1), ∃ c : E,
    f = octreePrefixIndicator (d + 1) a c}

/-- Singleton prefix-cell vectors generate no more than the Block 39 initial level. -/
theorem octreeSingletonLevel_le_initialLevel (d : ℕ) :
    octreeSingletonLevel (E := E) d ≤
      Relativistic3DWeightedDyadicReconstruction.Octree.initialLevelSubmodule
        (E := E) d := by
  apply Submodule.span_le.2
  rintro f ⟨a, c, rfl⟩
  exact octreePrefixIndicator_mem_initialLevel d a c

/-- Every finite-prefix cylinder vector is a finite sum of singleton prefix-cell
vectors, so the Block 39 level is generated by the singleton cells. -/
theorem initialLevel_le_octreeSingletonLevel (d : ℕ) :
    Relativistic3DWeightedDyadicReconstruction.Octree.initialLevelSubmodule
        (E := E) d ≤
      octreeSingletonLevel (E := E) d := by
  apply Submodule.span_le.2
  rintro f ⟨S, hS, c, rfl⟩
  rw [initialCylinderIndicator_eq_sum_singletons (E := E) d S hS c]
  apply Submodule.sum_mem
  intro p hp
  apply Submodule.subset_span
  exact ⟨initialToPrefix d p, c, rfl⟩

/-- Exact generator-level identification of the octree finite-prefix level. -/
theorem initialLevel_eq_octreeSingletonLevel (d : ℕ) :
    Relativistic3DWeightedDyadicReconstruction.Octree.initialLevelSubmodule
        (E := E) d =
      octreeSingletonLevel (E := E) d :=
  le_antisymm (initialLevel_le_octreeSingletonLevel d)
    (octreeSingletonLevel_le_initialLevel d)

/-- Algebraic span of ordinary closed level-`d+1` Euclidean dyadic-box indicators. -/
noncomputable def euclideanDyadicLevelRaw (d : ℕ) :
    Submodule ℂ (Lp E 2 Prev.cubeVolume) :=
  Submodule.span ℂ {f | ∃ a : Prev.Prefix (d + 1), ∃ c : E,
    f = euclideanBoxIndicator (d + 1) a c}

/-- Every ordinary dyadic-box generator belongs to the transported Block 39 raw level. -/
theorem euclideanDyadicLevelRaw_le_euclideanLevelRaw
    [CompleteSpace E] (d : ℕ) :
    euclideanDyadicLevelRaw (E := E) d ≤
      Relativistic3DEuclideanDyadicProjection.euclideanLevelRaw (E := E) d := by
  apply Submodule.span_le.2
  rintro f ⟨a, c, rfl⟩
  rw [← cubeAdjoint_octreePrefixIndicator]
  exact ⟨octreePrefixIndicator (d + 1) a c,
    octreePrefixIndicator_mem_initialLevel d a c, rfl⟩

/-- The transported Block 39 raw level is generated by ordinary dyadic-box indicators. -/
theorem euclideanLevelRaw_le_euclideanDyadicLevelRaw
    [CompleteSpace E] (d : ℕ) :
    Relativistic3DEuclideanDyadicProjection.euclideanLevelRaw (E := E) d ≤
      euclideanDyadicLevelRaw (E := E) d := by
  rintro f ⟨g, hg, rfl⟩
  rw [initialLevel_eq_octreeSingletonLevel] at hg
  refine Submodule.span_induction ?_ ?_ ?_ ?_ hg
  · intro h hh
    rcases hh with ⟨a, c, rfl⟩
    change Relativistic3DEuclideanDyadicProjection.cubeAdjoint (E := E)
      (octreePrefixIndicator (d + 1) a c) ∈ euclideanDyadicLevelRaw (E := E) d
    rw [cubeAdjoint_octreePrefixIndicator]
    apply Submodule.subset_span
    exact ⟨a, c, rfl⟩
  · simpa only [map_zero] using
      (Submodule.zero_mem (euclideanDyadicLevelRaw (E := E) d))
  · intro x y hx hy hxm hym
    simpa only [map_add] using
      Submodule.add_mem (euclideanDyadicLevelRaw (E := E) d) hxm hym
  · intro r x hx hxm
    simpa only [map_smul] using
      Submodule.smul_mem (euclideanDyadicLevelRaw (E := E) d) r hxm

/-- Exact identification of the raw transported level with the algebraic span of
ordinary dyadic-box step fields. -/
theorem euclideanLevelRaw_eq_euclideanDyadicLevelRaw
    [CompleteSpace E] (d : ℕ) :
    Relativistic3DEuclideanDyadicProjection.euclideanLevelRaw (E := E) d =
      euclideanDyadicLevelRaw (E := E) d :=
  le_antisymm (euclideanLevelRaw_le_euclideanDyadicLevelRaw d)
    (euclideanDyadicLevelRaw_le_euclideanLevelRaw d)

/-- Closed ordinary Euclidean dyadic-box step subspace at finite depth `d+1`. -/
noncomputable def euclideanDyadicLevel (d : ℕ) :
    Submodule ℂ (Lp E 2 Prev.cubeVolume) :=
  (euclideanDyadicLevelRaw (E := E) d).topologicalClosure

/-- The transported Block 39 level is exactly the closed ordinary dyadic-box step
subspace, modulo the null boundaries proved above. -/
theorem euclideanLevel_eq_euclideanDyadicLevel
    [CompleteSpace E] (d : ℕ) :
    Relativistic3DEuclideanDyadicProjection.euclideanLevel (E := E) d =
      euclideanDyadicLevel (E := E) d := by
  rw [Relativistic3DEuclideanDyadicProjection.euclideanLevel,
    euclideanDyadicLevel, euclideanLevelRaw_eq_euclideanDyadicLevelRaw]

/-- The concrete Euclidean dyadic-box levels are nested. -/
theorem euclideanDyadicLevel_mono
    [CompleteSpace E] {n m : ℕ} (h : n ≤ m) :
    euclideanDyadicLevel (E := E) n ≤ euclideanDyadicLevel (E := E) m := by
  rw [← euclideanLevel_eq_euclideanDyadicLevel,
    ← euclideanLevel_eq_euclideanDyadicLevel]
  exact Relativistic3DEuclideanDyadicProjection.euclideanLevel_mono (E := E) h

/-- Directed union of the concrete Euclidean dyadic-box step subspaces. -/
noncomputable def euclideanDyadicFiniteSubmodule :
    Submodule ℂ (Lp E 2 Prev.cubeVolume) :=
  ⨆ n : ℕ, euclideanDyadicLevel (E := E) n

/-- The concrete dyadic-box union is the transported finite-resolution union. -/
theorem euclideanDyadicFiniteSubmodule_eq
    [CompleteSpace E] :
    euclideanDyadicFiniteSubmodule (E := E) =
      Relativistic3DEuclideanDyadicProjection.euclideanFiniteSubmodule (E := E) := by
  unfold euclideanDyadicFiniteSubmodule
  rw [show (⨆ n : ℕ, euclideanDyadicLevel (E := E) n) =
      ⨆ n : ℕ, Relativistic3DEuclideanDyadicProjection.euclideanLevel (E := E) n by
    congr 1
    funext n
    exact (euclideanLevel_eq_euclideanDyadicLevel (E := E) n).symm]
  rfl

/-- Ordinary Euclidean dyadic-box step fields have dense union in cube `L²`. -/
theorem euclideanDyadicFiniteSubmodule_dense
    [CompleteSpace E] :
    (euclideanDyadicFiniteSubmodule (E := E)).topologicalClosure = ⊤ := by
  rw [← Submodule.dense_iff_topologicalClosure_eq_top]
  rw [euclideanDyadicFiniteSubmodule_eq]
  exact Relativistic3DEuclideanDyadicProjection.euclideanFiniteSubmodule_dense (E := E)

/-- Orthogonal projection onto the concrete closed dyadic-box step space,
identified with the transported Block 39 projection by the level equality above. -/
noncomputable def euclideanDyadicProjection
    [CompleteSpace E] (n : ℕ) :
    Lp E 2 Prev.cubeVolume →L[ℂ] Lp E 2 Prev.cubeVolume :=
  Relativistic3DEuclideanDyadicProjection.euclideanProjection (E := E) n

/-- The concrete dyadic projection is definitionally the Block 39 transported projection. -/
@[simp] theorem euclideanDyadicProjection_eq
    [CompleteSpace E] (n : ℕ) :
    euclideanDyadicProjection (E := E) n =
      Relativistic3DEuclideanDyadicProjection.euclideanProjection (E := E) n := rfl

/-- Concrete ordinary dyadic-box averaging projections converge strongly to every
Euclidean `L²` field. -/
theorem euclideanDyadicProjection_tendsto
    [CompleteSpace E]
    (f : Lp E 2 Prev.cubeVolume) :
    Filter.Tendsto (fun n => euclideanDyadicProjection (E := E) n f)
      Filter.atTop (nhds f) := by
  simpa only [euclideanDyadicProjection_eq] using
    Relativistic3DEuclideanDyadicProjection.euclideanProjection_tendsto
      (E := E) f

end Relativistic3DEuclideanDyadicBoxes
end KomorebiPhysics
