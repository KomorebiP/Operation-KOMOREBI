module

public import KomorebiPhysics.Relativistic3DOctreeEuclideanCoding
public import Mathlib.Probability.CDF
public import Mathlib.Data.Nat.Digits.Lemmas

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped BigOperators ENNReal NNReal MeasureTheory Topology unitInterval
open MeasureTheory Set Finset ProbabilityTheory

namespace KomorebiPhysics
namespace Relativistic3DBinaryLebesgue

namespace Prev
abbrev Bit := Relativistic3DOctreeEuclideanCoding.Bit
abbrev BitStream := Relativistic3DOctreeEuclideanCoding.BitStream
noncomputable abbrev binaryValue :=
  Relativistic3DOctreeEuclideanCoding.binaryValue
noncomputable abbrev binaryPoint :=
  Relativistic3DOctreeEuclideanCoding.binaryPoint
end Prev

/-- Uniform probability measure on one fair bit. -/
noncomputable def bitMeasure : Measure Prev.Bit :=
  (PMF.uniformOfFintype Prev.Bit).toMeasure

noncomputable instance bitMeasure_probability :
    IsProbabilityMeasure bitMeasure := by
  unfold bitMeasure
  infer_instance

@[simp] theorem bitMeasure_singleton (b : Prev.Bit) :
    bitMeasure {b} = (2 : ℝ≥0∞)⁻¹ := by
  have h := PMF.toMeasure_uniformOfFintype_apply
    (α := Prev.Bit) ({b} : Set Prev.Bit) (by measurability)
  change bitMeasure {b} = _
  rw [bitMeasure]
  convert h using 1
  norm_num [Prev.Bit]

/-- Product probability measure on infinite fair-bit streams. -/
noncomputable def bitStreamMeasure : Measure Prev.BitStream :=
  Measure.infinitePi (fun _ : ℕ => bitMeasure)

noncomputable instance bitStreamMeasure_probability :
    IsProbabilityMeasure bitStreamMeasure := by
  unfold bitStreamMeasure
  infer_instance

/-- A length-`n` bit prefix indexed exactly as an infinite-product cylinder. -/
abbrev BitPrefix (n : ℕ) := (i : Finset.range n) → Prev.Bit

/-- Cylinder event determined by one finite binary prefix. -/
def prefixCell (n : ℕ) (a : BitPrefix n) : Set Prev.BitStream :=
  cylinder (Finset.range n) {a}

@[measurability] theorem measurable_prefixCell (n : ℕ) (a : BitPrefix n) :
    MeasurableSet (prefixCell n a) := by
  exact MeasurableSet.of_mem_measurableCylinders
    (cylinder_mem_measurableCylinders _ _ (by measurability))

@[simp] theorem bitStreamMeasure_prefixCell (n : ℕ) (a : BitPrefix n) :
    bitStreamMeasure (prefixCell n a) = ((2 : ℝ≥0∞)⁻¹) ^ n := by
  have hcyl := Measure.infinitePi_cylinder
    (μ := fun _ : ℕ => bitMeasure)
    (s := Finset.range n) (S := ({a} : Set (BitPrefix n))) (by measurability)
  rw [bitStreamMeasure, prefixCell, hcyl]
  have hsingle :
      ({a} : Set (BitPrefix n)) =
        Set.univ.pi (fun i => ({a i} : Set Prev.Bit)) := by
    ext b
    simp [funext_iff]
  rw [hsingle, Measure.pi_pi]
  simp [bitMeasure]

/-- Big-endian list of natural binary digits associated with a prefix. -/
def prefixDigits (n : ℕ) (a : BitPrefix n) : List ℕ :=
  (List.ofFn (fun i : Fin n =>
    (a ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val)).reverse

@[simp] theorem length_prefixDigits (n : ℕ) (a : BitPrefix n) :
    (prefixDigits n a).length = n := by
  simp [prefixDigits]

lemma prefixDigits_lt_two (n : ℕ) (a : BitPrefix n) :
    ∀ x ∈ prefixDigits n a, x < 2 := by
  intro x hx
  simp [prefixDigits] at hx
  rcases hx with ⟨i, rfl⟩
  exact (a ⟨i.val, Finset.mem_range.mpr i.isLt⟩).isLt

/-- Natural number encoded by a length-`n` binary prefix. -/
def prefixCode (n : ℕ) (a : BitPrefix n) : ℕ :=
  Nat.ofDigits 2 (prefixDigits n a)

@[simp] theorem prefixCode_lt (n : ℕ) (a : BitPrefix n) :
    prefixCode n a < 2 ^ n := by
  have h := Nat.ofDigits_lt_base_pow_length (b := 2) (by norm_num)
    (prefixDigits_lt_two n a)
  simpa [prefixCode, length_prefixDigits] using h

/-- Prefix encoding as an element of `Fin (2^n)`. -/
def prefixCodeFin (n : ℕ) (a : BitPrefix n) : Fin (2 ^ n) :=
  ⟨prefixCode n a, prefixCode_lt n a⟩

private lemma prefixFunction_injective (n : ℕ) :
    Function.Injective
      (fun a : BitPrefix n =>
        fun i : Fin n => a ⟨i.val, Finset.mem_range.mpr i.isLt⟩) := by
  intro a b h
  funext i
  let j : Fin n := ⟨i.val, Finset.mem_range.mp i.property⟩
  exact congrFun h j

/-- The numeric code is injective on fixed-length prefixes. -/
theorem prefixCode_injective (n : ℕ) :
    Function.Injective (prefixCode n) := by
  intro a b hab
  have ha : prefixDigits n a ∈
      {L : List ℕ | L.length = n ∧ ∀ x ∈ L, x < 2} := by
    exact ⟨length_prefixDigits n a, prefixDigits_lt_two n a⟩
  have hb : prefixDigits n b ∈
      {L : List ℕ | L.length = n ∧ ∀ x ∈ L, x < 2} := by
    exact ⟨length_prefixDigits n b, prefixDigits_lt_two n b⟩
  have hl : prefixDigits n a = prefixDigits n b :=
    Nat.injOn_ofDigits (by norm_num) n ha hb hab
  have hl' :
      (List.ofFn (fun i : Fin n =>
        (a ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val)).reverse =
      (List.ofFn (fun i : Fin n =>
        (b ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val)).reverse := by
    simpa [prefixDigits] using hl
  have hvals :
      (fun i : Fin n =>
        (a ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val) =
      (fun i : Fin n =>
        (b ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val) := by
    apply List.ofFn_injective
    exact List.reverse_injective hl'
  have hfn :
      (fun i : Fin n => a ⟨i.val, Finset.mem_range.mpr i.isLt⟩) =
      (fun i : Fin n => b ⟨i.val, Finset.mem_range.mpr i.isLt⟩) := by
    funext i
    apply Fin.ext
    exact congrFun hvals i
  exact prefixFunction_injective n hfn

/-- The fixed-length prefix code is a bijection with the binary grid. -/
theorem prefixCodeFin_bijective (n : ℕ) :
    Function.Bijective (prefixCodeFin n) := by
  apply (Fintype.bijective_iff_injective_and_card _).2
  constructor
  · intro a b h
    apply prefixCode_injective n
    exact Fin.ext_iff.mp h
  · simp [BitPrefix, Prev.Bit]

/-- Exact equivalence between length-`n` bit prefixes and the binary grid `Fin (2^n)`. -/
noncomputable def prefixCodeEquiv (n : ℕ) : BitPrefix n ≃ Fin (2 ^ n) :=
  Equiv.ofBijective (prefixCodeFin n) (prefixCodeFin_bijective n)

/-- Finite product measure carried by the first `n` fair bits. -/
noncomputable def prefixMeasure (n : ℕ) : Measure (BitPrefix n) :=
  Measure.pi (fun _ : Finset.range n => bitMeasure)

noncomputable instance prefixMeasure_probability (n : ℕ) :
    IsProbabilityMeasure (prefixMeasure n) := by
  unfold prefixMeasure
  infer_instance

@[simp] theorem prefixMeasure_singleton (n : ℕ) (a : BitPrefix n) :
    prefixMeasure n {a} = ((2 : ℝ≥0∞)⁻¹) ^ n := by
  rw [prefixMeasure]
  have hsingle :
      ({a} : Set (BitPrefix n)) =
        Set.univ.pi (fun i => ({a i} : Set Prev.Bit)) := by
    ext b
    simp [funext_iff]
  rw [hsingle, Measure.pi_pi]
  simp [bitMeasure]

/-- Uniform measure on the binary grid of mesh `2^{-n}`. -/
noncomputable def binaryGridMeasure (n : ℕ) : Measure (Fin (2 ^ n)) :=
  (PMF.uniformOfFintype (Fin (2 ^ n))).toMeasure

noncomputable instance binaryGridMeasure_probability (n : ℕ) :
    IsProbabilityMeasure (binaryGridMeasure n) := by
  unfold binaryGridMeasure
  infer_instance

@[simp] theorem binaryGridMeasure_singleton (n : ℕ) (j : Fin (2 ^ n)) :
    binaryGridMeasure n {j} = ((2 : ℝ≥0∞) ^ n)⁻¹ := by
  have h := PMF.toMeasure_uniformOfFintype_apply
    (α := Fin (2 ^ n)) ({j} : Set (Fin (2 ^ n))) (by measurability)
  change binaryGridMeasure n {j} = _
  rw [binaryGridMeasure]
  convert h using 1
  simp

/-- Prefix coding preserves the finite uniform measures. -/
theorem prefixCode_measurePreserving (n : ℕ) :
    MeasurePreserving (prefixCodeEquiv n) (prefixMeasure n) (binaryGridMeasure n) := by
  refine ⟨measurable_of_finite _, ?_⟩
  apply Measure.ext_of_singleton
  intro j
  rw [Measure.map_apply (measurable_of_finite _)
    (measurableSet_singleton j)]
  have hpre :
      (prefixCodeEquiv n) ⁻¹' ({j} : Set (Fin (2 ^ n))) =
        {(prefixCodeEquiv n).symm j} := by
    ext a
    constructor
    · intro ha
      have h := congrArg (prefixCodeEquiv n).symm ha
      simpa using h
    · intro ha
      subst a
      simp
  rw [hpre, prefixMeasure_singleton, binaryGridMeasure_singleton]
  exact ENNReal.inv_pow.symm

/-- Exactly `k` grid points lie below the `k`-th dyadic boundary. -/
theorem card_grid_lt {n k : ℕ} (hk : k ≤ 2 ^ n) :
    Fintype.card {j : Fin (2 ^ n) // j.val < k} = k := by
  let e : {j : Fin (2 ^ n) // j.val < k} ≃ Fin k :=
    { toFun := fun j => ⟨j.1.val, j.2⟩
      invFun := fun j => ⟨⟨j.val, lt_of_lt_of_le j.isLt hk⟩, j.isLt⟩
      left_inv := by intro j; rfl
      right_inv := by intro j; rfl }
  simpa using Fintype.card_congr e

/-- Uniform binary grid mass below the `k`-th dyadic boundary. -/
theorem binaryGridMeasure_lt {n k : ℕ} (hk : k ≤ 2 ^ n) :
    binaryGridMeasure n {j | j.val < k} =
      (k : ℝ≥0∞) * ((2 : ℝ≥0∞) ^ n)⁻¹ := by
  rw [binaryGridMeasure]
  have h := PMF.toMeasure_uniformOfFintype_apply
    (α := Fin (2 ^ n)) ({j : Fin (2 ^ n) | j.val < k}) (by measurability)
  rw [h]
  congr 1
  · exact_mod_cast card_grid_lt hk
  · simp

/-- Restriction of an infinite bit stream to its first `n` digits. -/
def streamPrefix (n : ℕ) (s : Prev.BitStream) : BitPrefix n :=
  fun i => s i.1

/-- The dyadic grid index encoded by the first `n` digits. -/
noncomputable def gridIndex (n : ℕ) (s : Prev.BitStream) : Fin (2 ^ n) :=
  prefixCodeEquiv n (streamPrefix n s)

/-- Finite binary partial sum. -/
noncomputable def binaryPartial (n : ℕ) (s : Prev.BitStream) : ℝ :=
  ∑ i ∈ Finset.range n, Real.ofDigitsTerm s i

lemma binaryValue_eq_partial_add_tail (n : ℕ) (s : Prev.BitStream) :
    Prev.binaryValue s = binaryPartial n s + ((2 : ℝ) ^ n)⁻¹ *
      Real.ofDigits (fun i => s (i + n)) := by
  simpa [Prev.binaryValue,
    Relativistic3DOctreeEuclideanCoding.binaryValue, binaryPartial] using
      Real.ofDigits_eq_sum_add_ofDigits s n

lemma binaryPartial_le_binaryValue (n : ℕ) (s : Prev.BitStream) :
    binaryPartial n s ≤ Prev.binaryValue s := by
  rw [binaryValue_eq_partial_add_tail]
  have htail : 0 ≤ Real.ofDigits (fun i => s (i + n)) := Real.ofDigits_nonneg _
  have hpow : 0 ≤ ((2 : ℝ) ^ n)⁻¹ := by positivity
  exact le_add_of_nonneg_right (mul_nonneg hpow htail)

lemma binaryValue_le_partial_add (n : ℕ) (s : Prev.BitStream) :
    Prev.binaryValue s ≤ binaryPartial n s + ((2 : ℝ) ^ n)⁻¹ := by
  have h := Real.ofDigits_le_one (fun i => s (i+n))
  have hp : 0 ≤ ((2 : ℝ) ^ n)⁻¹ := by positivity
  calc
    Prev.binaryValue s = binaryPartial n s + ((2 : ℝ) ^ n)⁻¹ *
        Real.ofDigits (fun i => s (i+n)) := binaryValue_eq_partial_add_tail n s
    _ ≤ binaryPartial n s + ((2 : ℝ) ^ n)⁻¹ := by
      simpa [add_comm] using
        add_le_add_left (mul_le_of_le_one_right hp h) (binaryPartial n s)


lemma prefixCode_streamPrefix_succ (n : ℕ) (s : Prev.BitStream) :
    prefixCode (n+1) (streamPrefix (n+1) s) =
      2 * prefixCode n (streamPrefix n s) + (s n).val := by
  have hlist :
      List.ofFn (fun i : Fin (n+1) =>
        ((streamPrefix (n+1) s)
          ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val) =
      (List.ofFn (fun i : Fin n =>
        ((streamPrefix n s)
          ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val)).concat (s n).val := by
    rw [List.ofFn_succ']
    congr 1
  change Nat.ofDigits 2
      (List.ofFn (fun i : Fin (n+1) =>
        ((streamPrefix (n+1) s)
          ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val)).reverse =
    2 * Nat.ofDigits 2
      (List.ofFn (fun i : Fin n =>
        ((streamPrefix n s)
          ⟨i.val, Finset.mem_range.mpr i.isLt⟩).val)).reverse + (s n).val
  rw [hlist]
  simp [Nat.ofDigits_cons, Nat.add_comm]

lemma binaryPartial_succ (n : ℕ) (s : Prev.BitStream) :
    binaryPartial (n+1) s =
      binaryPartial n s + (s n).val * ((2 : ℝ) ^ (n+1))⁻¹ := by
  simp [binaryPartial, Finset.sum_range_succ, Real.ofDigitsTerm]

/-- The first `n` binary digits are exactly the dyadic grid index divided by `2^n`. -/
theorem binaryPartial_eq_grid (n : ℕ) (s : Prev.BitStream) :
    binaryPartial n s =
      (prefixCode n (streamPrefix n s) : ℝ) / (2 : ℝ) ^ n := by
  induction n with
  | zero => simp [binaryPartial, prefixCode, prefixDigits, streamPrefix]
  | succ n ih =>
      rw [binaryPartial_succ, ih, prefixCode_streamPrefix_succ]
      push_cast
      rw [pow_succ]
      field_simp

lemma binaryPartial_eq_gridIndex (n : ℕ) (s : Prev.BitStream) :
    binaryPartial n s = (gridIndex n s).val / (2 : ℝ) ^ n := by
  rw [binaryPartial_eq_grid]
  rfl

@[fun_prop] theorem measurable_streamPrefix (n : ℕ) :
    Measurable (streamPrefix n) := by
  unfold streamPrefix
  fun_prop


/-- Restricting the infinite fair stream to its first `n` coordinates gives the finite product law. -/
theorem streamPrefix_measurePreserving (n : ℕ) :
    MeasurePreserving (streamPrefix n) bitStreamMeasure (prefixMeasure n) := by
  refine ⟨measurable_streamPrefix n, ?_⟩
  change Measure.map (Finset.restrict (Finset.range n))
      (Measure.infinitePi (fun _ : ℕ => bitMeasure)) =
    Measure.pi (fun _ : Finset.range n => bitMeasure)
  exact Measure.infinitePi_map_restrict (fun _ : ℕ => bitMeasure)

@[fun_prop] theorem measurable_gridIndex (n : ℕ) :
    Measurable (gridIndex n) := by
  unfold gridIndex
  exact (prefixCode_measurePreserving n).measurable.comp
    (measurable_streamPrefix n)


/-- The first `n` digits are uniformly distributed over the dyadic grid. -/
theorem gridIndex_measurePreserving (n : ℕ) :
    MeasurePreserving (gridIndex n) bitStreamMeasure (binaryGridMeasure n) := by
  change MeasurePreserving
    ((prefixCodeEquiv n : BitPrefix n → Fin (2 ^ n)) ∘ streamPrefix n)
    bitStreamMeasure (binaryGridMeasure n)
  exact (prefixCode_measurePreserving n).comp (streamPrefix_measurePreserving n)

/-- Exact probability that the first `n` bits encode a grid point below `k`. -/
theorem bitStreamMeasure_gridIndex_lt {n k : ℕ} (hk : k ≤ 2 ^ n) :
    bitStreamMeasure {s | (gridIndex n s).val < k} =
      (k : ℝ≥0∞) * ((2 : ℝ≥0∞) ^ n)⁻¹ := by
  change bitStreamMeasure
      ((gridIndex n) ⁻¹' {j : Fin (2 ^ n) | j.val < k}) = _
  rw [← Measure.map_apply (measurable_gridIndex n) (by measurability)]
  rw [(gridIndex_measurePreserving n).map_eq]
  exact binaryGridMeasure_lt hk

/-- If the grid index is below `k`, the full binary value is at most the `k`-th boundary. -/
lemma binaryValue_le_div_of_gridIndex_lt {n k : ℕ} {s : Prev.BitStream}
    (h : (gridIndex n s).val < k) :
    Prev.binaryValue s ≤ (k : ℝ) / (2 : ℝ) ^ n := by
  have hden : 0 < (2 : ℝ) ^ n := pow_pos (by norm_num) _
  have hsucc : ((gridIndex n s).val : ℝ) + 1 ≤ (k : ℝ) := by
    exact_mod_cast Nat.succ_le_iff.mpr h
  calc
    Prev.binaryValue s ≤ binaryPartial n s + ((2 : ℝ) ^ n)⁻¹ :=
      binaryValue_le_partial_add n s
    _ = ((gridIndex n s).val : ℝ) / (2 : ℝ) ^ n +
        1 / (2 : ℝ) ^ n := by
      rw [binaryPartial_eq_gridIndex]
      simp [one_div]
    _ = (((gridIndex n s).val : ℝ) + 1) / (2 : ℝ) ^ n := by ring
    _ ≤ (k : ℝ) / (2 : ℝ) ^ n :=
      (div_le_div_iff_of_pos_right hden).2 hsucc

/-- A strict binary-value bound forces the finite grid index below the same boundary. -/
lemma gridIndex_lt_of_binaryValue_lt_div {n k : ℕ} {s : Prev.BitStream}
    (h : Prev.binaryValue s < (k : ℝ) / (2 : ℝ) ^ n) :
    (gridIndex n s).val < k := by
  have hden : 0 < (2 : ℝ) ^ n := pow_pos (by norm_num) _
  have hp := binaryPartial_le_binaryValue n s
  rw [binaryPartial_eq_gridIndex] at hp
  have hdiv : ((gridIndex n s).val : ℝ) / (2 : ℝ) ^ n <
      (k : ℝ) / (2 : ℝ) ^ n := hp.trans_lt h
  exact_mod_cast (div_lt_div_iff_of_pos_right hden).1 hdiv

/-- The binary sublevel event at a real threshold. -/
def binarySublevel (x : ℝ) : Set Prev.BitStream :=
  {s | Prev.binaryValue s ≤ x}

@[measurability] theorem measurable_binarySublevel (x : ℝ) :
    MeasurableSet (binarySublevel x) := by
  unfold binarySublevel
  exact Relativistic3DOctreeEuclideanCoding.continuous_binaryValue.measurable
    measurableSet_Iic

/-- Real-valued CDF of the fair binary expansion. -/
noncomputable def binaryCDF (x : ℝ) : ℝ :=
  bitStreamMeasure.real (binarySublevel x)

/-- Real-valued mass of the first-`n` grid event. -/
theorem bitStreamMeasure_real_gridIndex_lt {n k : ℕ} (hk : k ≤ 2 ^ n) :
    bitStreamMeasure.real {s | (gridIndex n s).val < k} =
      (k : ℝ) / (2 : ℝ) ^ n := by
  rw [measureReal_def, bitStreamMeasure_gridIndex_lt hk]
  simp [ENNReal.toReal_mul, ENNReal.toReal_inv, ENNReal.toReal_pow, div_eq_mul_inv]

/-- Integer below the dyadic boundary `2^n x`. -/
def dyadicFloor (n : ℕ) (x : ℝ) : ℕ :=
  ⌊(2 : ℝ) ^ n * x⌋₊

lemma dyadicFloor_le_pow {n : ℕ} {x : ℝ} (hx : x ≤ 1) :
    dyadicFloor n x ≤ 2 ^ n := by
  apply Nat.floor_le_of_le
  have hpow : 0 ≤ (2 : ℝ) ^ n := by positivity
  have := mul_le_mul_of_nonneg_left hx hpow
  norm_num at this ⊢
  exact this

lemma dyadicFloor_succ_le_pow {n : ℕ} {x : ℝ} (hx0 : 0 ≤ x) (hx1 : x < 1) :
    dyadicFloor n x + 1 ≤ 2 ^ n := by
  apply Nat.succ_le_iff.mpr
  rw [dyadicFloor, Nat.floor_lt (mul_nonneg (by positivity) hx0)]
  have hp : 0 < (2 : ℝ) ^ n := pow_pos (by norm_num) n
  have hmul : (2 : ℝ) ^ n * x < (2 : ℝ) ^ n * 1 :=
    mul_lt_mul_of_pos_left hx1 hp
  norm_num at hmul ⊢
  exact hmul

lemma dyadicFloor_div_le {n : ℕ} {x : ℝ} (hx0 : 0 ≤ x) :
    (dyadicFloor n x : ℝ) / (2 : ℝ) ^ n ≤ x := by
  have hpow : 0 < (2 : ℝ) ^ n := pow_pos (by norm_num) _
  apply (div_le_iff₀ hpow).2
  simpa [dyadicFloor, mul_comm] using
    (Nat.floor_le (mul_nonneg hpow.le hx0) :
      ((dyadicFloor n x : ℕ) : ℝ) ≤ (2 : ℝ) ^ n * x)

lemma lt_dyadicFloor_succ_div (n : ℕ) (x : ℝ) :
    x < ((dyadicFloor n x : ℝ) + 1) / (2 : ℝ) ^ n := by
  have hpow : 0 < (2 : ℝ) ^ n := pow_pos (by norm_num) _
  apply (lt_div_iff₀ hpow).2
  simpa [dyadicFloor, mul_comm] using
    (Nat.lt_floor_add_one ((2 : ℝ) ^ n * x))

lemma gridIndex_lt_floor_subset_binarySublevel {n : ℕ} {x : ℝ} (hx0 : 0 ≤ x) :
    {s | (gridIndex n s).val < dyadicFloor n x} ⊆ binarySublevel x := by
  intro s hs
  exact (binaryValue_le_div_of_gridIndex_lt hs).trans (dyadicFloor_div_le hx0)

lemma binarySublevel_subset_gridIndex_lt_succFloor (n : ℕ) (x : ℝ) :
    binarySublevel x ⊆ {s | (gridIndex n s).val < dyadicFloor n x + 1} := by
  intro s hs
  apply gridIndex_lt_of_binaryValue_lt_div
  exact lt_of_le_of_lt hs (by
    simpa [Nat.cast_add, Nat.cast_one] using lt_dyadicFloor_succ_div n x)

/-- Lower dyadic CDF bound. -/
theorem dyadicFloor_div_le_binaryCDF {n : ℕ} {x : ℝ}
    (hx0 : 0 ≤ x) (hx1 : x ≤ 1) :
    (dyadicFloor n x : ℝ) / (2 : ℝ) ^ n ≤ binaryCDF x := by
  rw [binaryCDF]
  rw [← bitStreamMeasure_real_gridIndex_lt (dyadicFloor_le_pow hx1)]
  exact measureReal_mono (gridIndex_lt_floor_subset_binarySublevel hx0)

/-- Upper dyadic CDF bound away from the endpoint `1`. -/
theorem binaryCDF_le_succFloor_div {n : ℕ} {x : ℝ}
    (hx0 : 0 ≤ x) (hx1 : x < 1) :
    binaryCDF x ≤ ((dyadicFloor n x : ℝ) + 1) / (2 : ℝ) ^ n := by
  have h : bitStreamMeasure.real (binarySublevel x) ≤
      bitStreamMeasure.real
        {s | (gridIndex n s).val < dyadicFloor n x + 1} :=
    measureReal_mono (binarySublevel_subset_gridIndex_lt_succFloor n x)
      (by finiteness)
  rw [bitStreamMeasure_real_gridIndex_lt
    (dyadicFloor_succ_le_pow hx0 hx1)] at h
  simpa [binaryCDF, Nat.cast_add, Nat.cast_one] using h

lemma binaryCDF_one : binaryCDF 1 = 1 := by
  have hsub : binarySublevel 1 = Set.univ := by
    ext s
    simp [binarySublevel,
      Relativistic3DOctreeEuclideanCoding.binaryValue_le_one]
  rw [binaryCDF, hsub]
  simp [measureReal_def]

/-- The binary CDF differs from `x` by at most one dyadic mesh cell. -/
theorem abs_binaryCDF_sub_le {x : ℝ} (hx0 : 0 ≤ x) (hx1 : x < 1) (n : ℕ) :
    |binaryCDF x - x| ≤ ((2 : ℝ) ^ n)⁻¹ := by
  have hlo := dyadicFloor_div_le_binaryCDF (n := n) hx0 hx1.le
  have hup := binaryCDF_le_succFloor_div (n := n) hx0 hx1
  have hfloor := dyadicFloor_div_le (n := n) hx0
  have hnext := lt_dyadicFloor_succ_div n x
  have hpow : 0 ≤ ((2 : ℝ) ^ n)⁻¹ := by positivity
  have hsplit :
      ((dyadicFloor n x : ℝ) + 1) / (2 : ℝ) ^ n =
        (dyadicFloor n x : ℝ) / (2 : ℝ) ^ n + ((2 : ℝ) ^ n)⁻¹ := by
    field_simp
  rw [hsplit] at hup hnext
  rw [abs_le]
  constructor <;> linarith

/-- The fair binary expansion has CDF `x` on the closed unit interval. -/
theorem binaryCDF_eq (x : ℝ) (hx0 : 0 ≤ x) (hx1 : x ≤ 1) :
    binaryCDF x = x := by
  rcases hx1.eq_or_lt with rfl | hxlt
  · exact binaryCDF_one
  · have hlim : Filter.Tendsto (fun n : ℕ => ((2 : ℝ) ^ n)⁻¹)
        Filter.atTop (𝓝 0) := by
      simpa [inv_pow] using
        (tendsto_pow_atTop_nhds_zero_of_lt_one
          (show 0 ≤ (2 : ℝ)⁻¹ by positivity)
          (show (2 : ℝ)⁻¹ < 1 by norm_num))
    have habs : |binaryCDF x - x| ≤ 0 :=
      ge_of_tendsto' hlim (fun n => abs_binaryCDF_sub_le hx0 hxlt n)
    have hz : |binaryCDF x - x| = 0 :=
      le_antisymm habs (abs_nonneg _)
    exact sub_eq_zero.mp (abs_eq_zero.mp hz)

/-- Binary decoding into the unit interval is measurable. -/
theorem measurable_binaryPoint : Measurable Prev.binaryPoint := by
  exact (Continuous.subtype_mk
    Relativistic3DOctreeEuclideanCoding.continuous_binaryValue _).measurable

/-- Fair binary streams push forward to normalized Lebesgue measure on the unit interval. -/
theorem binaryPoint_measurePreserving :
    MeasurePreserving Prev.binaryPoint bitStreamMeasure volume := by
  refine ⟨measurable_binaryPoint, ?_⟩
  apply Measure.ext_of_Iic
  intro x
  apply (ENNReal.toReal_eq_toReal_iff'
    (measure_ne_top _ _) (measure_ne_top _ _)).mp
  rw [Measure.map_apply measurable_binaryPoint measurableSet_Iic]
  change binaryCDF x.1 = (volume (Set.Iic x)).toReal
  rw [binaryCDF_eq x.1 x.2.1 x.2.2, unitInterval.volume_Iic]
  exact (ENNReal.toReal_ofReal x.2.1).symm

namespace Cube

abbrev Axis := Relativistic3DOctreeEuclideanCoding.Axis
abbrev BitCubeAddress := Relativistic3DOctreeEuclideanCoding.BitCubeAddress
noncomputable abbrev bitVectorMeasure :=
  Relativistic3DOctreeEuclideanCoding.bitVectorMeasure
noncomputable abbrev bitCubeMeasure :=
  Relativistic3DOctreeEuclideanCoding.bitCubeMeasure

/-- The uniform three-bit vector measure is the product of three fair-bit measures. -/
theorem bitVectorMeasure_eq_pi :
    bitVectorMeasure = Measure.pi (fun _ : Axis => bitMeasure) := by
  apply Measure.ext_of_singleton
  intro b
  rw [Relativistic3DOctreeEuclideanCoding.bitVectorMeasure_singleton]
  have hsingle :
      ({b} : Set (Axis → Prev.Bit)) =
        Set.univ.pi (fun i => ({b i} : Set Prev.Bit)) := by
    ext c
    simp [funext_iff]
  rw [hsingle, Measure.pi_pi]
  simp only [bitMeasure_singleton, Finset.prod_const, Finset.card_univ]
  change (8 : ℝ≥0∞)⁻¹ = ((2 : ℝ≥0∞)⁻¹) ^ 3
  apply (ENNReal.toReal_eq_toReal_iff' (by finiteness) (by finiteness)).mp
  norm_num [ENNReal.toReal_inv, ENNReal.toReal_pow]

/-- Transpose time-major bit vectors into three coordinate streams. -/
def transposeBits (b : BitCubeAddress) : Axis → Prev.BitStream :=
  fun i n => b n i

@[fun_prop] theorem measurable_transposeBits : Measurable transposeBits := by
  unfold transposeBits
  fun_prop

/-- Product fair-bit measure on the three coordinate streams. -/
noncomputable def coordinateBitMeasure : Measure (Axis → Prev.BitStream) :=
  Measure.pi (fun _ : Axis => bitStreamMeasure)

/-- Uncurry the time-major bit array to a measure on time-coordinate pairs. -/
def uncurryTime : BitCubeAddress → (ℕ × Axis → Prev.Bit) :=
  (MeasurableEquiv.curry ℕ Axis Prev.Bit).symm

/-- Swap the time and coordinate indices. -/
def swapTimeAxis : (ℕ × Axis → Prev.Bit) → (Axis × ℕ → Prev.Bit) :=
  MeasurableEquiv.piCongrLeft (fun _ : Axis × ℕ => Prev.Bit)
    (Equiv.prodComm ℕ Axis)

/-- Curry a coordinate-time array into three infinite coordinate streams. -/
def curryAxis : (Axis × ℕ → Prev.Bit) → (Axis → Prev.BitStream) :=
  MeasurableEquiv.curry Axis ℕ Prev.Bit

@[fun_prop] theorem measurable_uncurryTime : Measurable uncurryTime := by
  exact (MeasurableEquiv.curry ℕ Axis Prev.Bit).symm.measurable

@[fun_prop] theorem measurable_swapTimeAxis : Measurable swapTimeAxis := by
  exact (MeasurableEquiv.piCongrLeft (fun _ : Axis × ℕ => Prev.Bit)
    (Equiv.prodComm ℕ Axis)).measurable

@[fun_prop] theorem measurable_curryAxis : Measurable curryAxis := by
  exact (MeasurableEquiv.curry Axis ℕ Prev.Bit).measurable

lemma bitCubeMeasure_eq_nestedInfinitePi :
    bitCubeMeasure =
      Measure.infinitePi (fun _ : ℕ =>
        Measure.infinitePi (fun _ : Axis => bitMeasure)) := by
  change Measure.infinitePi (fun _ : ℕ => bitVectorMeasure) = _
  congr 1
  funext n
  rw [bitVectorMeasure_eq_pi]
  exact (Measure.infinitePi_eq_pi (fun _ : Axis => bitMeasure)).symm

/-- Uncurrying preserves the nested fair-bit product measure. -/
theorem uncurryTime_measurePreserving :
    MeasurePreserving uncurryTime bitCubeMeasure
      (Measure.infinitePi (fun _ : ℕ × Axis => bitMeasure)) := by
  refine ⟨measurable_uncurryTime, ?_⟩
  rw [bitCubeMeasure_eq_nestedInfinitePi]
  exact Measure.infinitePi_map_curry_symm (fun _ : ℕ => fun _ : Axis => bitMeasure)

/-- Swapping time and coordinate indices preserves the fair-bit product measure. -/
theorem swapTimeAxis_measurePreserving :
    MeasurePreserving swapTimeAxis
      (Measure.infinitePi (fun _ : ℕ × Axis => bitMeasure))
      (Measure.infinitePi (fun _ : Axis × ℕ => bitMeasure)) := by
  refine ⟨measurable_swapTimeAxis, ?_⟩
  exact Measure.infinitePi_map_piCongrLeft
    (fun _ : Axis × ℕ => bitMeasure) (Equiv.prodComm ℕ Axis)

/-- Currying the coordinate-major pair array gives the product of three stream measures. -/
theorem curryAxis_measurePreserving :
    MeasurePreserving curryAxis
      (Measure.infinitePi (fun _ : Axis × ℕ => bitMeasure))
      coordinateBitMeasure := by
  refine ⟨measurable_curryAxis, ?_⟩
  rw [coordinateBitMeasure, ← Measure.infinitePi_eq_pi]
  exact Measure.infinitePi_map_curry (fun _ : Axis => fun _ : ℕ => bitMeasure)

lemma transposeBits_eq_composite :
    transposeBits = curryAxis ∘ swapTimeAxis ∘ uncurryTime := by
  funext b i n
  rfl

/-- Transposition carries the time-major product measure to three independent fair streams. -/
theorem transposeBits_measurePreserving :
    MeasurePreserving transposeBits bitCubeMeasure coordinateBitMeasure := by
  rw [transposeBits_eq_composite]
  exact curryAxis_measurePreserving.comp
    (swapTimeAxis_measurePreserving.comp uncurryTime_measurePreserving)

/-- Product normalized Lebesgue measure on the closed unit cube. -/
noncomputable def cubeVolume : Measure (Axis → I) :=
  Measure.pi (fun _ : Axis => volume)

/-- Coordinatewise binary decoding carries three fair streams to cube volume. -/
theorem coordinateBinary_measurePreserving :
    MeasurePreserving
      (fun s : Axis → Prev.BitStream => fun i => Prev.binaryPoint (s i))
      coordinateBitMeasure cubeVolume := by
  exact measurePreserving_pi
    (fun _ : Axis => bitStreamMeasure)
    (fun _ : Axis => volume)
    (fun _ => binaryPoint_measurePreserving)

lemma cubeCode_eq_composite :
    Relativistic3DOctreeEuclideanCoding.cubeCode =
      (fun s : Axis → Prev.BitStream => fun i => Prev.binaryPoint (s i)) ∘
        transposeBits := by
  funext b i
  rfl

/-- Three fair coordinate streams push forward to ordinary volume on the unit cube. -/
theorem cubeCode_measurePreserving :
    MeasurePreserving Relativistic3DOctreeEuclideanCoding.cubeCode
      bitCubeMeasure cubeVolume := by
  rw [cubeCode_eq_composite]
  exact coordinateBinary_measurePreserving.comp transposeBits_measurePreserving

/-- Octree product measure pushes forward to ordinary volume on the unit cube. -/
theorem octreeCubeCode_measurePreserving :
    MeasurePreserving Relativistic3DOctreeEuclideanCoding.octreeCubeCode
      Relativistic3DOctreeEuclideanCoding.Prev.octreeMeasure cubeVolume := by
  change MeasurePreserving
    (Relativistic3DOctreeEuclideanCoding.cubeCode ∘
      Relativistic3DOctreeEuclideanCoding.addressBitMeasurableEquiv)
    Relativistic3DOctreeEuclideanCoding.Prev.octreeMeasure cubeVolume
  exact cubeCode_measurePreserving.comp
    Relativistic3DOctreeEuclideanCoding.addressBit_measurePreserving

universe uE
variable {E : Type uE} [NormedAddCommGroup E] [NormedSpace ℂ E]

/-- Isometric pullback of Euclidean-cube `L²` fields to the octree address continuum. -/
noncomputable def pullbackCubeL2 :
    Lp E 2 cubeVolume →ₗᵢ[ℂ]
      Lp E 2 Relativistic3DOctreeEuclideanCoding.Prev.octreeMeasure :=
  Lp.compMeasurePreservingₗᵢ ℂ
    Relativistic3DOctreeEuclideanCoding.octreeCubeCode
    octreeCubeCode_measurePreserving

@[simp] theorem pullbackCubeL2_norm (f : Lp E 2 cubeVolume) :
    ‖pullbackCubeL2 f‖ = ‖f‖ := by
  exact LinearIsometry.norm_map _ _

end Cube

end Relativistic3DBinaryLebesgue
end KomorebiPhysics
