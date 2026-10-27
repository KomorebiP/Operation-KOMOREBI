module

public import KomorebiPhysics.Relativistic3DWeightedDyadicReconstruction
public import Mathlib.MeasureTheory.Constructions.UnitInterval
public import Mathlib.MeasureTheory.Function.LpSpace.Basic
public import Mathlib.Analysis.Real.OfDigits

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped BigOperators ENNReal NNReal MeasureTheory InnerProductSpace Topology unitInterval
open MeasureTheory Set Finset WithLp

namespace KomorebiPhysics
namespace Relativistic3DOctreeEuclideanCoding

namespace Prev
abbrev Octant := Relativistic3DWeightedDyadicReconstruction.Octree.Octant
abbrev Address := Relativistic3DWeightedDyadicReconstruction.Octree.Address
noncomputable abbrev octantMeasure :=
  Relativistic3DWeightedDyadicReconstruction.Octree.octantMeasure
noncomputable abbrev octreeMeasure :=
  Relativistic3DWeightedDyadicReconstruction.Octree.octreeMeasure
end Prev

/-- Three Cartesian coordinate axes. -/
abbrev Axis := Fin 3

/-- One binary coordinate digit. -/
abbrev Bit := Fin 2

instance bitMeasurableSpace : MeasurableSpace Bit := ⊤
instance bitMeasurableSingleton : MeasurableSingletonClass Bit := ⟨fun _ => by simp⟩

/-- The three coordinate bits carried by one octree digit.
The least-significant bit is the `x` bit, followed by `y` and `z`. -/
def bitsOfOctant (o : Prev.Octant) : Axis → Bit :=
  fun i => ⟨(o.val / (2 ^ i.val)) % 2, Nat.mod_lt _ (by omega)⟩

/-- Reassemble an octree digit from its three Cartesian bits. -/
def octantOfBits (b : Axis → Bit) : Prev.Octant :=
  ⟨(b 0).val + 2 * (b 1).val + 4 * (b 2).val, by omega⟩

@[simp] theorem octantOfBits_bitsOfOctant (o : Prev.Octant) :
    octantOfBits (bitsOfOctant o) = o := by
  apply Fin.ext
  simp [octantOfBits, bitsOfOctant]
  omega

@[simp] theorem bitsOfOctant_octantOfBits (b : Axis → Bit) :
    bitsOfOctant (octantOfBits b) = b := by
  funext i
  apply Fin.ext
  fin_cases i <;> simp [bitsOfOctant, octantOfBits] <;> omega

/-- Exact finite equivalence between one octree digit and three binary digits. -/
def octantBitEquiv : Prev.Octant ≃ (Axis → Bit) where
  toFun := bitsOfOctant
  invFun := octantOfBits
  left_inv := octantOfBits_bitsOfOctant
  right_inv := bitsOfOctant_octantOfBits

/-- The digit equivalence as a measurable equivalence of finite discrete spaces. -/
def octantBitMeasurableEquiv : Prev.Octant ≃ᵐ (Axis → Bit) where
  toEquiv := octantBitEquiv
  measurable_toFun := measurable_of_finite _
  measurable_invFun := measurable_of_finite _

/-- Uniform measure on the eight three-bit vectors. -/
noncomputable def bitVectorMeasure : Measure (Axis → Bit) :=
  (PMF.uniformOfFintype (Axis → Bit)).toMeasure

noncomputable instance bitVectorMeasure_probability :
    IsProbabilityMeasure bitVectorMeasure := by
  unfold bitVectorMeasure
  infer_instance

@[simp] theorem bitVectorMeasure_singleton (b : Axis → Bit) :
    bitVectorMeasure {b} = (8 : ℝ≥0∞)⁻¹ := by
  have h := PMF.toMeasure_uniformOfFintype_apply
    (α := Axis → Bit) ({b} : Set (Axis → Bit)) (by measurability)
  change bitVectorMeasure {b} = _
  rw [bitVectorMeasure]
  convert h using 1
  norm_num [Axis, Bit]

/-- The digit encoding preserves the uniform one-octant probability measure. -/
theorem octantBit_measurePreserving :
    MeasurePreserving octantBitMeasurableEquiv Prev.octantMeasure bitVectorMeasure := by
  refine ⟨octantBitMeasurableEquiv.measurable, ?_⟩
  apply Measure.ext_of_singleton
  intro b
  rw [Measure.map_apply octantBitMeasurableEquiv.measurable (measurableSet_singleton b)]
  have hpre : octantBitMeasurableEquiv ⁻¹' ({b} : Set (Axis → Bit)) =
      {octantBitMeasurableEquiv.symm b} := by
    ext o
    constructor
    · intro h
      have h' := congrArg octantBitMeasurableEquiv.symm h
      simpa using h'
    · intro h
      subst o
      simp
  rw [hpre]
  rw [Relativistic3DWeightedDyadicReconstruction.Octree.octantMeasure_singleton]
  exact (bitVectorMeasure_singleton b).symm

/-- An octree address rewritten as a sequence of three-bit vectors. -/
abbrev BitCubeAddress := ℕ → Axis → Bit

/-- Exact address-level equivalence obtained digit by digit. -/
def addressBitEquiv : Prev.Address ≃ BitCubeAddress where
  toFun := fun a n => bitsOfOctant (a n)
  invFun := fun b n => octantOfBits (b n)
  left_inv := by
    intro a
    funext n
    simp
  right_inv := by
    intro b
    funext n i
    simp

/-- The finite digit encoder is continuous. -/
theorem continuous_bitsOfOctant : Continuous bitsOfOctant := by
  exact continuous_of_discreteTopology

/-- The address factorization is continuous in the product topologies. -/
theorem continuous_addressBitEquiv :
    Continuous (addressBitEquiv : Prev.Address → BitCubeAddress) := by
  rw [continuous_pi_iff]
  intro n
  exact continuous_bitsOfOctant.comp (continuous_apply n)

/-- The address equivalence as a measurable equivalence of product spaces. -/
def addressBitMeasurableEquiv : Prev.Address ≃ᵐ BitCubeAddress where
  toEquiv := addressBitEquiv
  measurable_toFun := by
    rw [measurable_pi_iff]
    intro n
    exact octantBitMeasurableEquiv.measurable.comp (measurable_pi_apply n)
  measurable_invFun := by
    rw [measurable_pi_iff]
    intro n
    exact octantBitMeasurableEquiv.symm.measurable.comp (measurable_pi_apply n)

/-- Infinite product of the uniform three-bit vector measure. -/
noncomputable def bitCubeMeasure : Measure BitCubeAddress :=
  Measure.infinitePi (fun _ : ℕ => bitVectorMeasure)

noncomputable instance bitCubeMeasure_probability :
    IsProbabilityMeasure bitCubeMeasure := by
  unfold bitCubeMeasure
  infer_instance

/-- The exact digitwise address factorization preserves the full product measure. -/
theorem addressBit_measurePreserving :
    MeasurePreserving addressBitMeasurableEquiv Prev.octreeMeasure bitCubeMeasure := by
  refine ⟨addressBitMeasurableEquiv.measurable, ?_⟩
  have hmap := Measure.infinitePi_map_pi
    (μ := fun _ : ℕ => Prev.octantMeasure)
    (f := fun _ : ℕ => (octantBitMeasurableEquiv : Prev.Octant → Axis → Bit))
    (fun _ => octantBitMeasurableEquiv.measurable)
  rw [octantBit_measurePreserving.map_eq] at hmap
  have hfun :
      ((fun x i => octantBitMeasurableEquiv (x i)) : Prev.Address → BitCubeAddress) =
        (fun a n => bitsOfOctant (a n)) := by
    funext a n
    rfl
  change Measure.map (fun a n => bitsOfOctant (a n))
      (Measure.infinitePi (fun _ : ℕ => Prev.octantMeasure)) =
    Measure.infinitePi (fun _ : ℕ => bitVectorMeasure)
  rw [← hfun]
  exact hmap


/-- One infinite binary coordinate stream. -/
abbrev BitStream := ℕ → Bit

/-- The standard base-two positional value of a bit stream. -/
noncomputable def binaryValue (s : BitStream) : ℝ :=
  Real.ofDigits s

@[simp] theorem binaryValue_nonneg (s : BitStream) :
    0 ≤ binaryValue s := by
  exact Real.ofDigits_nonneg s

@[simp] theorem binaryValue_le_one (s : BitStream) :
    binaryValue s ≤ 1 := by
  exact Real.ofDigits_le_one s

/-- The binary value bundled as a point of the closed unit interval. -/
noncomputable def binaryPoint (s : BitStream) : I :=
  ⟨binaryValue s, binaryValue_nonneg s, binaryValue_le_one s⟩

/-- Extract one Cartesian binary stream from the interleaved three-bit address. -/
def coordinateStream (b : BitCubeAddress) (i : Axis) : BitStream :=
  fun n => b n i

/-- Decode all three binary streams to a point of the closed unit cube. -/
noncomputable def cubeCode (b : BitCubeAddress) : Axis → I :=
  fun i => binaryPoint (coordinateStream b i)

/-- The binary-series coordinate map is continuous. -/
theorem continuous_binaryValue : Continuous binaryValue := by
  exact Real.continuous_ofDigits

/-- Extracting one coordinate stream from the product address is continuous. -/
theorem continuous_coordinateStream (i : Axis) :
    Continuous (fun b : BitCubeAddress => coordinateStream b i) := by
  rw [continuous_pi_iff]
  intro n
  exact continuous_apply i |>.comp (continuous_apply n)

/-- The three-coordinate binary decoding map is continuous. -/
theorem continuous_cubeCode : Continuous cubeCode := by
  rw [continuous_pi_iff]
  intro i
  exact Continuous.subtype_mk
    (continuous_binaryValue.comp (continuous_coordinateStream i)) _

/-- Hence the three-coordinate binary decoding map is measurable. -/
theorem measurable_cubeCode : Measurable cubeCode :=
  continuous_cubeCode.measurable

/-- Two binary streams agreeing through depth `n` decode within one dyadic interval. -/
theorem abs_binaryValue_sub_le {x y : BitStream} {n : ℕ}
    (hxy : ∀ i < n, x i = y i) :
    |binaryValue x - binaryValue y| ≤ ((2 : ℝ) ^ n)⁻¹ := by
  exact Real.abs_ofDigits_sub_ofDigits_le hxy

/-- Coordinatewise dyadic control for two three-dimensional addresses. -/
theorem abs_cubeCode_coordinate_sub_le {x y : BitCubeAddress} {n : ℕ}
    (hxy : ∀ k < n, x k = y k) (i : Axis) :
    |((cubeCode x i : I) : ℝ) - ((cubeCode y i : I) : ℝ)| ≤ ((2 : ℝ) ^ n)⁻¹ := by
  apply abs_binaryValue_sub_le
  intro k hk
  exact congrFun (hxy k hk) i

/-- Every point of the unit interval has at least one binary stream representation. -/
theorem binaryPoint_surjective : Function.Surjective binaryPoint := by
  intro x
  rcases (Real.ofDigits_SurjOn (b := 2) (by norm_num)) x.property with
    ⟨s, -, hs⟩
  refine ⟨s, Subtype.ext ?_⟩
  exact hs

/-- Every point of the closed three-dimensional unit cube has a binary address. -/
theorem cubeCode_surjective : Function.Surjective cubeCode := by
  intro x
  choose s hs using fun i => binaryPoint_surjective (x i)
  refine ⟨fun n i => s i n, ?_⟩
  funext i
  exact hs i

/-- The Euclidean cube is the topological quotient of the compact three-bit address space
under binary-expansion ambiguity. -/
theorem cubeCode_isQuotientMap : Topology.IsQuotientMap cubeCode :=
  Topology.IsQuotientMap.of_surjective_continuous cubeCode_surjective continuous_cubeCode

/-- Decode an octree address directly as a point of the closed unit cube. -/
noncomputable def octreeCubeCode (a : Prev.Address) : Axis → I :=
  cubeCode (addressBitEquiv a)

/-- The octree-to-cube decoder is continuous. -/
theorem continuous_octreeCubeCode : Continuous octreeCubeCode := by
  exact continuous_cubeCode.comp continuous_addressBitEquiv

/-- The octree-to-cube decoder is measurable. -/
theorem measurable_octreeCubeCode : Measurable octreeCubeCode := by
  exact measurable_cubeCode.comp addressBitMeasurableEquiv.measurable

/-- The octree-to-cube decoder is surjective. -/
theorem octreeCubeCode_surjective : Function.Surjective octreeCubeCode := by
  intro x
  rcases cubeCode_surjective x with ⟨b, hb⟩
  refine ⟨addressBitEquiv.symm b, ?_⟩
  simpa [octreeCubeCode] using hb

/-- The Euclidean cube is likewise a topological quotient of the original octree
address continuum. -/
theorem octreeCubeCode_isQuotientMap : Topology.IsQuotientMap octreeCubeCode :=
  Topology.IsQuotientMap.of_surjective_continuous
    octreeCubeCode_surjective continuous_octreeCubeCode

/-- Octree addresses with a common depth-`n` prefix decode coordinatewise within one
Euclidean dyadic mesh width `2⁻ⁿ`. -/
theorem abs_octreeCubeCode_coordinate_sub_le {a b : Prev.Address} {n : ℕ}
    (hab : ∀ k < n, a k = b k) (i : Axis) :
    |((octreeCubeCode a i : I) : ℝ) - ((octreeCubeCode b i : I) : ℝ)| ≤
      ((2 : ℝ) ^ n)⁻¹ := by
  apply abs_cubeCode_coordinate_sub_le
  intro k hk
  change bitsOfOctant (a k) = bitsOfOctant (b k)
  rw [hab k hk]

/-- The terminating base-two representation of one half. -/
def halfTerminating : BitStream :=
  fun n => if n = 0 then 1 else 0

/-- The nonterminating base-two representation of one half. -/
def halfRepeating : BitStream :=
  fun n => if n = 0 then 0 else 1

/-- The two standard binary representations of one half are distinct streams. -/
theorem halfRepresentations_ne : halfTerminating ≠ halfRepeating := by
  intro h
  have h0 := congrFun h 0
  norm_num [halfTerminating, halfRepeating] at h0

/-- The terminating stream decodes to one half. -/
theorem binaryValue_halfTerminating :
    binaryValue halfTerminating = (1 : ℝ) / 2 := by
  rw [binaryValue, Real.ofDigits_eq_sum_add_ofDigits halfTerminating 1]
  simp [halfTerminating, Real.ofDigitsTerm, Real.ofDigits]

/-- The repeating stream also decodes to one half. -/
theorem binaryValue_halfRepeating :
    binaryValue halfRepeating = (1 : ℝ) / 2 := by
  have hones : Real.ofDigits (fun _ : ℕ => (1 : Fin 2)) = (1 : ℝ) := by
    simpa using (Real.ofDigits_const_last_eq_one' (b := 2) (by norm_num))
  rw [binaryValue, Real.ofDigits_eq_sum_add_ofDigits halfRepeating 1]
  simp [halfRepeating, Real.ofDigitsTerm, hones]

/-- Binary decoding is surjective but not injective because dyadic points have two expansions. -/
theorem binaryPoint_not_injective : ¬ Function.Injective binaryPoint := by
  intro h
  apply halfRepresentations_ne
  apply h
  apply Subtype.ext
  change binaryValue halfTerminating = binaryValue halfRepeating
  rw [binaryValue_halfTerminating, binaryValue_halfRepeating]

universe uE
variable {E : Type uE} [NormedAddCommGroup E]
variable [NormedSpace ℂ E]

/-- Pull back a three-bit-coordinate `L²` field to the octree address continuum. -/
def pullbackBitL2 :
    Lp E 2 bitCubeMeasure →ₗᵢ[ℂ] Lp E 2 Prev.octreeMeasure :=
  Lp.compMeasurePreservingₗᵢ ℂ addressBitMeasurableEquiv addressBit_measurePreserving

@[simp] theorem pullbackBitL2_norm (f : Lp E 2 bitCubeMeasure) :
    ‖pullbackBitL2 f‖ = ‖f‖ := by
  exact LinearIsometry.norm_map _ _

end Relativistic3DOctreeEuclideanCoding
end KomorebiPhysics
