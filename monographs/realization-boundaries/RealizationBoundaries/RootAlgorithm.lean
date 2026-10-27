import RealizationBoundaries.RootConsequences
import Mathlib.Data.List.OfFn

/-! # A finite arithmetic implementation of the normal-form root correction

The executable input is a rational, a finite list of natural residue codes,
and an explicit Boolean selector oracle. List position n names prime VALUE n,
not the nth prime. Unused and nonprime positions carry no mathematical data.
The proof connects the finite implementation to the original ambient group.
-/
set_option autoImplicit false
namespace RealizationBoundaries

def finiteCodeValue (d : List ℕ) (p : Prime) : Coordinate p :=
  (d[p.val]?.getD 0 : Coordinate p)

def oracleSection (a : Prime → Bool) (r : ℚ) (p : Prime) : Coordinate p :=
  if a p then (r : Coordinate p) else 0

def codedNormalValue (a : Prime → Bool) (r : ℚ) (d : List ℕ) : Ambient :=
  fun p => oracleSection a r p + finiteCodeValue d p

def rootCorrectionBound (r : ℚ) (d : List ℕ) (m : ℕ) : ℕ :=
  max d.length (r.den * (r / m).den + 1)

def rootCorrectionValue (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m : ℕ) (p : Prime) : Coordinate p :=
  (m : Coordinate p)⁻¹ *
    (codedNormalValue a r d p - (m : Coordinate p) * oracleSection a (r / m) p)

/-- A finite loop. ZMod inversion is its computable extended-Euclidean implementation. -/
def rootCorrectionCode (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) : List ℕ :=
  List.ofFn fun i : Fin (rootCorrectionBound r d m) =>
    if h : i.val.Prime then (rootCorrectionValue a r d m ⟨i.val, h⟩).val else 0

@[simp] theorem rootCorrectionCode_length (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) (m : ℕ) :
    (rootCorrectionCode a r d m).length = rootCorrectionBound r d m := by
  simp [rootCorrectionCode]

theorem finiteCodeValue_eq_zero (d : List ℕ) (p : Prime) (h : d.length ≤ p.val) :
    finiteCodeValue d p = 0 := by
  simp [finiteCodeValue, List.getElem?_eq_none h]

theorem oracleSection_eq (a : Prime → Bool) (r : ℚ) :
    oracleSection a r = rationalSection {p | a p = true} r := by
  funext p
  cases h : a p <;> simp [oracleSection, rationalSection, h]

theorem codedNormalValue_mem (a : Prime → Bool) (r : ℚ) (d : List ℕ) :
    codedNormalValue a r d ∈ selectorGroup {p | a p = true} := by
  apply (selectorGroup _).add_mem
  · exact (oracleSection_eq a r).symm ▸ rationalSection_mem _ r
  · apply finiteSupport_le_preimage
    apply (Set.finite_Iio d.length).preimage Subtype.val_injective.injOn |>.subset
    intro p hp
    by_contra hn
    exact hp (finiteCodeValue_eq_zero d p (Nat.le_of_not_gt hn))

/-- Outside the input support and the two denominator-prime sets the defect is zero. -/
theorem root_defect_zero_outside (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) (p : Prime)
    (hd : d.length ≤ p.val) (hp : ¬ p.val ∣ r.den * (r / m).den) :
    codedNormalValue a r d p - (m : Coordinate p) * oracleSection a (r / m) p = 0 := by
  have ht : ((r / m).den : Coordinate p) ≠ 0 :=
    (coordinate_cast_eq_zero _ p).not.mpr (fun h => hp (dvd_mul_of_dvd_right h _))
  have he : (m : ℚ) * (r / m) = r := mul_div_cancel₀ r (Nat.cast_ne_zero.mpr hm.ne')
  have hc : (r : Coordinate p) = (m : Coordinate p) * ((r / m : ℚ) : Coordinate p) := by
    calc
      _ = (((m : ℚ) * (r / m) : ℚ) : Coordinate p) := congrArg (fun q : ℚ => (q : Coordinate p)) he.symm
      _ = _ := by rw [Rat.cast_mul_of_ne_zero (by simp) ht]; simp
  cases hs : a p <;> simp [codedNormalValue, oracleSection, hs,
    finiteCodeValue_eq_zero d p hd, hc]

theorem rootCorrectionValue_zero_outside (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) (p : Prime) (hp : rootCorrectionBound r d m ≤ p.val) :
    rootCorrectionValue a r d m p = 0 := by
  have hd : d.length ≤ p.val := (le_max_left _ _).trans hp
  have hden : ¬ p.val ∣ r.den * (r / m).den := by
    intro h
    have hle := Nat.le_of_dvd (Nat.mul_pos r.den_pos (r / m).den_pos) h
    have hbound := (le_max_right d.length (r.den * (r / m).den + 1)).trans hp
    omega
  simp [rootCorrectionValue, root_defect_zero_outside a r d hm p hd hden]

/-- Extraction correspondence for every prime of the infinite ambient product. -/
theorem rootCorrectionCode_exact (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) :
    finiteCodeValue (rootCorrectionCode a r d m) = rootCorrectionValue a r d m := by
  funext p
  by_cases hp : p.val < rootCorrectionBound r d m
  · simp [finiteCodeValue, rootCorrectionCode, hp, p.property]
    rfl
  · rw [finiteCodeValue_eq_zero _ p (by simpa using Nat.le_of_not_gt hp),
      rootCorrectionValue_zero_outside a r d hm p (Nat.le_of_not_gt hp)]

/-- The printed finite procedure produces a root of the original ambient value. -/
theorem finite_root_algorithm_correct (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m)
    (h : ∀ p : Prime, p.val ∣ m → codedNormalValue a r d p = 0) :
    m • codedNormalValue a (r / m) (rootCorrectionCode a r d m) =
      codedNormalValue a r d := by
  funext p
  rw [coordinate_nsmul]
  change (m : Coordinate p) * (oracleSection a (r / m) p +
    finiteCodeValue (rootCorrectionCode a r d m) p) = _
  rw [congrFun (rootCorrectionCode_exact a r d hm) p]
  by_cases hp : p.val ∣ m
  · simp [(coordinate_cast_eq_zero m p).mpr hp, h p hp]
  · have hn := (coordinate_cast_eq_zero m p).not.mpr hp
    simp only [rootCorrectionValue, mul_add, mul_inv_cancel_left₀ hn]
    exact add_sub_cancel _ _

/-- Trial division and finitely many residue tests implement the obstruction test. -/
def finiteRootTest (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) : Bool :=
  (List.range (m + 1)).all fun n =>
    if h : n.Prime then
      if n ∣ m then decide (codedNormalValue a r d ⟨n, h⟩ = 0) else true
    else true

theorem finiteRootTest_exact (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) :
    finiteRootTest a r d m = true ↔
      ∀ p : Prime, p.val ∣ m → codedNormalValue a r d p = 0 := by
  simp only [finiteRootTest, List.all_eq_true, List.mem_range]
  constructor
  · intro h p hp
    rcases p with ⟨n, hn⟩
    change n ∣ m at hp
    have ht : (if h : n.Prime then if n ∣ m then decide (codedNormalValue a r d ⟨n, h⟩ = 0) else true else true) = true := h n (by have := Nat.le_of_dvd hm hp; omega)
    simpa [hn, hp] using ht
  · intro h n _
    split_ifs with hn hd
    · exact decide_eq_true (h ⟨n, hn⟩ hd)
    · rfl
    · rfl

/-- None is a rejected root request; Some contains the rational and finite output. -/
def finiteRootSolver (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    Option (ℚ × List ℕ) :=
  if 0 < m ∧ finiteRootTest a r d m = true then
    some (r / m, rootCorrectionCode a r d m)
  else none

theorem finiteRootSolver_some_iff (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m : ℕ) (t : ℚ) (e : List ℕ) :
    finiteRootSolver a r d m = some (t, e) ↔
      0 < m ∧ finiteRootTest a r d m = true ∧
      t = r / m ∧ e = rootCorrectionCode a r d m := by
  simp only [finiteRootSolver]
  split_ifs with h
  · simp only [Option.some.injEq, Prod.mk.injEq]
    exact ⟨fun he => ⟨h.1, h.2, he.1.symm, he.2.symm⟩,
      fun he => ⟨he.2.2.1.symm, he.2.2.2.symm⟩⟩
  · simp only [false_iff]
    rintro ⟨hm, ht, _, _⟩
    exact h ⟨hm, ht⟩

theorem finiteRootSolver_sound (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m : ℕ) (t : ℚ) (e : List ℕ) (h : finiteRootSolver a r d m = some (t, e)) :
    m • codedNormalValue a t e = codedNormalValue a r d := by
  obtain ⟨hm, ht, rfl, rfl⟩ := (finiteRootSolver_some_iff a r d m t e).mp h
  exact finite_root_algorithm_correct a r d hm ((finiteRootTest_exact a r d hm).mp ht)

/-- Rejection has a single prime coordinate as a mathematical certificate. -/
theorem finiteRootSolver_rejection_certificate (a : Prime → Bool) (r : ℚ)
    (d : List ℕ) {m : ℕ} (hm : 0 < m)
    (h : finiteRootSolver a r d m = none) :
    ∃ p : Prime, p.val ∣ m ∧ codedNormalValue a r d p ≠ 0 := by
  by_contra hn
  have ht : finiteRootTest a r d m = true := (finiteRootTest_exact a r d hm).mpr (by
    intro p hp
    by_contra hnz
    exact hn ⟨p, hp, hnz⟩)
  simp [finiteRootSolver, hm, ht] at h

/-- For positive multipliers rejection is equivalent to no root in the original group. -/
theorem finiteRootSolver_complete (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) :
    (∃ t e, finiteRootSolver a r d m = some (t, e)) ↔
      ∃ y : selectorGroup {p | a p = true},
        m • y = ⟨codedNormalValue a r d, codedNormalValue_mem a r d⟩ := by
  constructor
  · rintro ⟨t, e, he⟩
    exact ⟨⟨codedNormalValue a t e, codedNormalValue_mem a t e⟩,
      Subtype.ext (finiteRootSolver_sound a r d m t e he)⟩
  · intro hy
    have hr := (preimage_root_iff _ hm _).mp hy
    have ht := (finiteRootTest_exact a r d hm).mpr hr
    exact ⟨r / m, rootCorrectionCode a r d m, by simp [finiteRootSolver, hm, ht]⟩

/-- The finite output has no nonzero correction outside the printed support set. -/
theorem finiteRootSolver_support_bound (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) (p : Prime)
    (hd : finiteCodeValue d p = 0) (hp : ¬ p.val ∣ r.den * (r / m).den) :
    finiteCodeValue (rootCorrectionCode a r d m) p = 0 := by
  rw [congrFun (rootCorrectionCode_exact a r d hm) p]
  have he : (m : ℚ) * (r / m) = r := mul_div_cancel₀ r (Nat.cast_ne_zero.mpr hm.ne')
  have ht : ((r / m).den : Coordinate p) ≠ 0 :=
    (coordinate_cast_eq_zero _ p).not.mpr (fun h => hp (dvd_mul_of_dvd_right h _))
  have hc : (r : Coordinate p) = (m : Coordinate p) * ((r / m : ℚ) : Coordinate p) := by
    calc
      _ = (((m : ℚ) * (r / m) : ℚ) : Coordinate p) := congrArg (fun q : ℚ => (q : Coordinate p)) he.symm
      _ = _ := by rw [Rat.cast_mul_of_ne_zero (by simp) ht]; simp
  cases hs : a p <;> simp [rootCorrectionValue, codedNormalValue, oracleSection, hs, hd, hc]

/-- Every actual finite-support input admits a finite residue list. The existence
proof does not claim to extract a list from an arbitrary infinite function. -/
theorem finiteCodeValue_represents (x : finiteSupport) :
    ∃ d : List ℕ, finiteCodeValue d = x.val := by
  classical
  let hf := x.property
  let s := hf.toFinset
  let N := s.sup Subtype.val + 1
  let d : List ℕ := List.ofFn fun i : Fin N =>
    if h : i.val.Prime then (x.val ⟨i.val, h⟩).val else 0
  refine ⟨d, ?_⟩
  funext p
  by_cases hp : p.val < N
  · simp only [finiteCodeValue, d, List.getElem?_ofFn, hp, dite_true, dite_eq_left p.property,
      Option.getD_some, ZMod.natCast_zmod_val]
    rfl
  · have hx : x.val p = 0 := by
      by_contra hn
      have hmem : p ∈ s := (Set.Finite.mem_toFinset hf).mpr hn
      have hle : p.val ≤ s.sup Subtype.val := Finset.le_sup hmem
      have hlt : p.val < N := Nat.lt_succ_of_le hle
      exact hp hlt
    have hlen : d.length = N := by simp only [d, List.length_ofFn]
    rw [finiteCodeValue_eq_zero d p (hlen.symm ▸ Nat.le_of_not_gt hp), hx]

/-- Thus the finite engine covers every original selector-group normal form. -/
theorem codedNormalValue_represents (a : Prime → Bool)
    (x : selectorGroup {p | a p = true}) :
    ∃ r : ℚ, ∃ d : List ℕ, codedNormalValue a r d = x.val := by
  obtain ⟨r, d, hd⟩ := normalForm_exists _ x
  obtain ⟨code, hc⟩ := finiteCodeValue_represents d
  refine ⟨r, code, ?_⟩
  change oracleSection a r + finiteCodeValue code = x.val
  rw [oracleSection_eq, hc, ← hd]

def rootObstructs (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m n : ℕ) : Bool :=
  if h : n.Prime then decide (n ∣ m ∧ codedNormalValue a r d ⟨n, h⟩ ≠ 0)
  else false

/-- The implementation returns the first obstructing prime, not just a rejection flag. -/
def firstRootObstruction (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) : Option ℕ :=
  (List.range (m + 1)).find? (rootObstructs a r d m)

theorem firstRootObstruction_spec (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m n : ℕ) (h : firstRootObstruction a r d m = some n) :
    ∃ hp : n.Prime, n ∣ m ∧ codedNormalValue a r d ⟨n, hp⟩ ≠ 0 := by
  have ht := List.find?_some h
  by_cases hp : n.Prime
  · exact ⟨hp, by simpa [rootObstructs, hp] using ht⟩
  · simp [rootObstructs, hp] at ht

theorem firstRootObstruction_none_iff (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) :
    firstRootObstruction a r d m = none ↔
      ∀ p : Prime, p.val ∣ m → codedNormalValue a r d p = 0 := by
  rw [firstRootObstruction, List.find?_eq_none]
  constructor
  · intro h p hp
    rcases p with ⟨n, hn⟩
    change n ∣ m at hp
    have hle := Nat.le_of_dvd hm hp
    have ht := h n (List.mem_range.mpr (Nat.lt_succ_of_le hle))
    simpa [rootObstructs, hn, hp] using ht
  · intro h n _
    by_cases hn : n.Prime
    · by_cases hd : n ∣ m
      · simpa [rootObstructs, hn, hd] using h ⟨n, hn⟩ hd
      · simp [rootObstructs, hn, hd]
    · simp [rootObstructs, hn]

/-- The positive-multiplier certified routine: error p, or a rational/finite root. -/
def certifiedRootSolver (a : Prime → Bool) (r : ℚ) (d : List ℕ) (m : ℕ) :
    Except ℕ (ℚ × List ℕ) :=
  match firstRootObstruction a r d m with
  | some p => .error p
  | none => .ok (r / m, rootCorrectionCode a r d m)

theorem certifiedRootSolver_error (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    (m n : ℕ) (h : certifiedRootSolver a r d m = .error n) :
    ∃ hp : n.Prime, n ∣ m ∧ codedNormalValue a r d ⟨n, hp⟩ ≠ 0 := by
  unfold certifiedRootSolver at h
  split at h
  next p hp =>
    cases h
    exact firstRootObstruction_spec a r d m n hp
  next => cases h

theorem certifiedRootSolver_ok (a : Prime → Bool) (r : ℚ) (d : List ℕ)
    {m : ℕ} (hm : 0 < m) (t : ℚ) (e : List ℕ)
    (h : certifiedRootSolver a r d m = .ok (t, e)) :
    m • codedNormalValue a t e = codedNormalValue a r d := by
  unfold certifiedRootSolver at h
  split at h
  next => cases h
  next hn =>
    cases h
    exact finite_root_algorithm_correct a r d hm
      ((firstRootObstruction_none_iff a r d hm).mp hn)

end RealizationBoundaries
