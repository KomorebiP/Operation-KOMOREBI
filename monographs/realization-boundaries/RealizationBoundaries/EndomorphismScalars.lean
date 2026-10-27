import RealizationBoundaries.DiagonalRealization

/-!
# Rational quotient scalars and the full endomorphism ring

The eventual rational value is derived from membership in the actual rational
line. Its ring laws and surjectivity are proved. Exceptional primes, including
denominator primes, are retained by the finite-defect formulation.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- The scalar on the target rational line, chosen only after admissibility is proved. -/
def diagonalSlope (S T : Set Prime) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c) : ℚ :=
  Classical.choose ((mem_selectorGroup_iff T _).mp
    ((diagonalAdmissible_selector_iff S T c).mp hc))

theorem diagonalSlope_spec (S T : Set Prime) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c) :
    diagonalTail c (quotientMap (indicator S)) =
      diagonalSlope S T c hc • quotientMap (indicator T) :=
  (Classical.choose_spec ((mem_selectorGroup_iff T _).mp
    ((diagonalAdmissible_selector_iff S T c).mp hc))).symm

/-- Infinite target support is needed to identify the rational scalar uniquely. -/
theorem diagonalSlope_unique (S T : Set Prime) (hT : T.Infinite) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c) (r : ℚ)
    (hr : diagonalTail c (quotientMap (indicator S)) = r • quotientMap (indicator T)) :
    diagonalSlope S T c hc = r := by
  apply smul_left_injective ℚ (indicator_tail_ne_zero hT)
  exact (diagonalSlope_spec S T c hc).symm.trans hr

/-- The same scalar governs every element of the quotient line. -/
theorem diagonalSlope_on_line (S T : Set Prime) (c : Ambient)
    (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c) (r : ℚ) :
    diagonalTail c (r • quotientMap (indicator S)) =
      (r * diagonalSlope S T c hc) • quotientMap (indicator T) := by
  rw [map_smul, diagonalSlope_spec, smul_smul]

/-- On a selected coordinate, the finite defect is the difference from rational reduction. -/
theorem diagonal_section_defect_support (S : Set Prime) (c : Ambient) (r : ℚ) :
    support (diagonal c (indicator S) - rationalSection S r) =
      {p | p ∈ S ∧ c p ≠ (r : Coordinate p)} := by
  classical
  ext p
  by_cases hp : p ∈ S <;> simp [support, rationalSection, indicator, hp, sub_eq_zero]

/-- The printed eventual-rational condition, with all exceptions explicitly finite. -/
theorem diagonalEndRing_mem_iff (S : Set Prime) (c : Ambient) :
    c ∈ diagonalEndRing (selectorLine S) ↔
      ∃ r : ℚ, {p | p ∈ S ∧ c p ≠ (r : Coordinate p)}.Finite := by
  change DiagonalAdmissible (selectorLine S) (selectorLine S) c ↔ _
  rw [diagonalAdmissible_iff_finite_defect]
  simp only [mem_finiteSupport, diagonal_section_defect_support]

/-- Each finite-defect scalar equals the unique rational quotient scalar. -/
theorem diagonalSlope_eq_of_finite_defect (S T : Set Prime) (hT : T.Infinite)
    (c : Ambient) (hc : DiagonalAdmissible (selectorLine S) (selectorLine T) c)
    (r : ℚ) (hr : diagonal c (indicator S) - rationalSection T r ∈ finiteSupport) :
    diagonalSlope S T c hc = r := by
  apply diagonalSlope_unique S T hT c hc r
  have hq := (quotientMap_eq_iff _ _).mpr hr
  rw [quotientMap_rationalSection] at hq
  exact hq

/-- The unique rational value is a ring homomorphism on the admissible diagonal ring. -/
def quotientScalar (S : Set Prime) (hS : S.Infinite) :
    diagonalEndRing (selectorLine S) →+* ℚ where
  toFun c := diagonalSlope S S c.val c.property
  map_zero' := by
    apply diagonalSlope_unique S S hS 0 _ 0
    have hz : diagonal 0 (indicator S) = 0 := by funext p; simp
    rw [diagonalTail_quotient, hz, map_zero, zero_smul]
  map_one' := by
    apply diagonalSlope_unique S S hS 1 _ 1
    simp
  map_add' c d := by
    apply smul_left_injective ℚ (indicator_tail_ne_zero hS)
    calc
      _ = diagonalTail (c + d).val (quotientMap (indicator S)) :=
        (diagonalSlope_spec S S (c + d).val (c + d).property).symm
      _ = diagonalTail c.val (quotientMap (indicator S)) +
          diagonalTail d.val (quotientMap (indicator S)) :=
        diagonalTail_add c.val d.val _
      _ = _ := by
        rw [diagonalSlope_spec S S c.val c.property,
          diagonalSlope_spec S S d.val d.property]
        exact (add_smul _ _ _).symm
  map_mul' c d := by
    apply smul_left_injective ℚ (indicator_tail_ne_zero hS)
    calc
      _ = diagonalTail (c * d).val (quotientMap (indicator S)) :=
        (diagonalSlope_spec S S (c * d).val (c * d).property).symm
      _ = diagonalTail c.val (diagonalTail d.val (quotientMap (indicator S))) :=
        diagonalTail_mul c.val d.val _
      _ = _ := by
        rw [diagonalSlope_spec S S d.val d.property, map_smul,
          diagonalSlope_spec S S c.val c.property, smul_smul, mul_comm]

@[simp] theorem quotientScalar_spec (S : Set Prime) (hS : S.Infinite)
    (c : diagonalEndRing (selectorLine S)) :
    diagonalTail c.val (quotientMap (indicator S)) =
      quotientScalar S hS c • quotientMap (indicator S) :=
  diagonalSlope_spec S S c.val c.property

@[simp] theorem diagonal_section_indicator (S : Set Prime) (r : ℚ) :
    diagonal (rationalSection S r) (indicator S) = rationalSection S r := by
  classical
  funext p
  by_cases hp : p ∈ S <;> simp [rationalSection, indicator, hp]

/-- A rational section is an admissible multiplier, even at denominator primes. -/
def rationalDiagonal (S : Set Prime) (r : ℚ) : diagonalEndRing (selectorLine S) :=
  ⟨rationalSection S r, (diagonalAdmissible_selector_iff S S _).mpr
    (by rw [diagonal_section_indicator]; exact rationalSection_mem S r)⟩

@[simp] theorem quotientScalar_rationalDiagonal (S : Set Prime) (hS : S.Infinite) (r : ℚ) :
    quotientScalar S hS (rationalDiagonal S r) = r := by
  refine diagonalSlope_unique S S hS (rationalDiagonal S r).val
    (rationalDiagonal S r).property r ?_
  change quotientMap (diagonal (rationalSection S r) (indicator S)) = _
  rw [diagonal_section_indicator, quotientMap_rationalSection]

/-- Surjectivity does not require a homomorphic section of the nonsplit group extension. -/
theorem quotientScalar_surjective (S : Set Prime) (hS : S.Infinite) :
    Function.Surjective (quotientScalar S hS) :=
  fun r => ⟨rationalDiagonal S r, quotientScalar_rationalDiagonal S hS r⟩

/-- The kernel consists exactly of families with finitely many nonzero selected entries. -/
theorem quotientScalar_eq_zero_iff (S : Set Prime) (hS : S.Infinite)
    (c : diagonalEndRing (selectorLine S)) :
    quotientScalar S hS c = 0 ↔ {p | p ∈ S ∧ c.val p ≠ 0}.Finite := by
  constructor
  · intro hz
    have hq := quotientScalar_spec S hS c
    rw [hz, zero_smul] at hq
    have hf := (quotientMap_eq_zero_iff _).mp hq
    have he := diagonal_section_defect_support S c.val 0
    simp only [rationalSection_zero, sub_zero, Rat.cast_zero] at he
    change (support (diagonal c.val (indicator S))).Finite at hf
    rwa [he] at hf
  · intro hf
    apply diagonalSlope_eq_of_finite_defect S S hS c.val c.property 0
    change (support (diagonal c.val (indicator S) - rationalSection S 0)).Finite
    simpa only [diagonal_section_defect_support, Rat.cast_zero] using hf

/-- The original endomorphism ring carries this surjective rational quotient character. -/
def endomorphismQuotientScalar (S : Set Prime) (hS : S.Infinite) :
    AddMonoid.End (selectorGroup S) →+* ℚ :=
  (quotientScalar S hS).comp (homDiagonalRing (selectorLine S))

theorem endomorphismQuotientScalar_surjective (S : Set Prime) (hS : S.Infinite) :
    Function.Surjective (endomorphismQuotientScalar S hS) := by
  intro r
  obtain ⟨c, hc⟩ := quotientScalar_surjective S hS r
  obtain ⟨f, hf⟩ := (endomorphismRingEquiv (selectorLine S)).surjective c
  refine ⟨f, ?_⟩
  change quotientScalar S hS (homDiagonalRing (selectorLine S) f) = r
  have he : homDiagonalRing (selectorLine S) f = c := hf
  rw [he, hc]

end RealizationBoundaries
