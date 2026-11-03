import CoupledNormalization

/-!
# Bounded contraction ladders and guarded reverse folds

An exact rational algorithm specification for the valid-input arithmetic
core of `disk_majorant`. Step exhaustion and post-update size failures are
explicit errors. The first small-radius seed is not size-checked. Successful
returns refine the proved fuel majorant and hence certify actual functions.
This does not assert Python interpreter or library implementation correctness.
-/

set_option autoImplicit false
set_option maxHeartbeats 2500000
noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales

inductive MajorantError where
  | steps
  | bits
  deriving DecidableEq, Repr

def majorantSeed (R : ℚ) : ℚ := R/(1-R^2)
def majorantStep (R B : ℚ) : ℚ := R*(1+B^2)

inductive LadderTrace (Q : ℚ) : ℚ → List ℚ → ℚ → Prop where
  | stop {R : ℚ} (small : R < 1) : LadderTrace Q R [] R
  | step {R t : ℚ} {xs : List ℚ} (large : 1 ≤ R)
      (child : LadderTrace Q (Q*R) xs t) : LadderTrace Q R (R::xs) t

def buildLadder (Q : ℚ) : ℕ → ℚ → Except MajorantError (List ℚ × ℚ)
  | 0, R => if R < 1 then .ok ([],R) else .error .steps
  | n+1, R => if R < 1 then .ok ([],R) else
      match buildLadder Q n (Q*R) with
      | .error e => .error e
      | .ok (xs,t) => .ok (R::xs,t)

theorem ladder_terminal (Q R t : ℚ) (xs : List ℚ) (h : LadderTrace Q R xs t) :
    t = Q^xs.length * R := by
  induction h with
  | stop => simp
  | @step R t xs hlarge hchild ih =>
    rw [ih, List.length_cons, pow_succ]
    ring

theorem ladder_terminal_small (Q R t : ℚ) (xs : List ℚ) (h : LadderTrace Q R xs t) : t < 1 := by
  induction h with
  | stop hs => exact hs
  | step _ _ ih => exact ih

theorem ladder_adequate (Q R t : ℚ) (xs : List ℚ) (h : LadderTrace Q R xs t) :
    Q^xs.length * R < 1 := by
  rw [← ladder_terminal Q R t xs h]
  exact ladder_terminal_small Q R t xs h

theorem ladder_fold_eq (Q R t : ℚ) (xs : List ℚ) (h : LadderTrace Q R xs t) :
    xs.foldr majorantStep (majorantSeed t) = rationalDiskMajorant Q xs.length R := by
  induction h with
  | stop hs => rfl
  | @step R t xs hlarge hchild ih =>
    simp only [List.foldr_cons, List.length_cons, rationalDiskMajorant,
      ite_eq_right (not_lt.mpr hlarge)]
    rw [ih]
    rfl

theorem build_ladder_ok (Q R : ℚ) (fuel : ℕ) (xs : List ℚ) (t : ℚ)
    (h : buildLadder Q fuel R = .ok (xs,t)) :
    LadderTrace Q R xs t ∧ xs.length ≤ fuel := by
  induction fuel generalizing R xs t with
  | zero =>
    by_cases hs : R < 1
    · simp only [buildLadder, ite_eq_left hs, Except.ok.injEq, Prod.mk.injEq] at h
      rcases h with ⟨rfl,rfl⟩
      exact ⟨.stop hs, by simp⟩
    · simp only [buildLadder, ite_eq_right hs] at h
      cases h
  | succ n ih =>
    by_cases hs : R < 1
    · simp only [buildLadder, ite_eq_left hs, Except.ok.injEq, Prod.mk.injEq] at h
      rcases h with ⟨rfl,rfl⟩
      exact ⟨.stop hs, by simp⟩
    · simp only [buildLadder, ite_eq_right hs] at h
      cases he : buildLadder Q n (Q*R) with
      | error e => rw [he] at h; cases h
      | ok pair =>
        rcases pair with ⟨ys,u⟩
        rw [he] at h
        obtain ⟨ht,hl⟩ := ih (Q*R) ys u he
        cases h
        exact ⟨.step (le_of_not_gt hs) ht, by simpa using Nat.succ_le_succ hl⟩

theorem build_ladder_of_trace (Q R t : ℚ) (xs : List ℚ) (h : LadderTrace Q R xs t)
    (fuel : ℕ) (hl : xs.length ≤ fuel) : buildLadder Q fuel R = .ok (xs,t) := by
  induction h generalizing fuel with
  | stop hs => cases fuel <;> simp only [buildLadder, ite_eq_left hs]
  | @step R t xs hlarge hchild ih =>
    cases fuel with
    | zero => simp at hl
    | succ n =>
      have hn : xs.length ≤ n := by simpa using hl
      simp only [buildLadder, ite_eq_right (not_lt.mpr hlarge), ih n hn]

theorem build_ladder_ok_iff (Q R : ℚ) (fuel : ℕ) (xs : List ℚ) (t : ℚ) :
    buildLadder Q fuel R = .ok (xs,t) ↔ LadderTrace Q R xs t ∧ xs.length ≤ fuel :=
  ⟨build_ladder_ok Q R fuel xs t, fun h => build_ladder_of_trace Q R t xs h.1 fuel h.2⟩

theorem build_ladder_not_bits (Q R : ℚ) (fuel : ℕ) : buildLadder Q fuel R ≠ .error .bits := by
  induction fuel generalizing R with
  | zero => simp only [buildLadder]; split <;> simp
  | succ n ih =>
    simp only [buildLadder]
    split
    · simp
    · cases he : buildLadder Q n (Q*R) with
      | ok pair => simp
      | error e =>
        have hn := ih (Q*R)
        rw [he] at hn
        exact hn

theorem build_ladder_exists_of_adequate (Q R : ℚ) (fuel : ℕ) (ht : Q^fuel*R < 1) :
    ∃ xs t, buildLadder Q fuel R = .ok (xs,t) := by
  induction fuel generalizing R with
  | zero =>
    have hR : R < 1 := by simpa using ht
    exact ⟨[],R,by simp only [buildLadder,ite_eq_left hR]⟩
  | succ n ih =>
    by_cases hs : R < 1
    · exact ⟨[],R,by simp [buildLadder,hs]⟩
    · have hc : Q^n*(Q*R) < 1 := by simpa only [pow_succ, mul_assoc] using ht
      obtain ⟨xs,t,he⟩ := ih (Q*R) hc
      exact ⟨R::xs,t,by simp only [buildLadder,ite_eq_right hs,he]⟩

def guardedFold (fits : ℚ → Bool) (seed : ℚ) : List ℚ → Except MajorantError ℚ
  | [] => .ok seed
  | R::xs => match guardedFold fits seed xs with
      | .error e => .error e
      | .ok B => if fits (majorantStep R B) then .ok (majorantStep R B) else .error .bits

def FoldFits (fits : ℚ → Bool) (seed : ℚ) : List ℚ → Prop
  | [] => True
  | R::xs => FoldFits fits seed xs ∧ fits (majorantStep R (xs.foldr majorantStep seed)) = true

theorem guarded_fold_not_steps (fits : ℚ → Bool) (seed : ℚ) (xs : List ℚ) :
    guardedFold fits seed xs ≠ .error .steps := by
  induction xs with
  | nil => simp [guardedFold]
  | cons R xs ih =>
    simp only [guardedFold]
    cases he : guardedFold fits seed xs with
    | error e => rw [he] at ih; exact ih
    | ok B => simp only; split <;> simp

theorem guarded_fold_ok_iff (fits : ℚ → Bool) (seed B : ℚ) (xs : List ℚ) :
    guardedFold fits seed xs = .ok B ↔ B = xs.foldr majorantStep seed ∧ FoldFits fits seed xs := by
  induction xs generalizing B with
  | nil => simp [guardedFold, FoldFits, eq_comm]
  | cons R xs ih =>
    cases he : guardedFold fits seed xs with
    | error e =>
      have hf : ¬FoldFits fits seed xs := by
        intro hf
        have hc := (ih (xs.foldr majorantStep seed)).mpr ⟨rfl,hf⟩
        rw [he] at hc
        cases hc
      simp [guardedFold, he, FoldFits, hf]
    | ok C =>
      have hc := (ih C).mp he
      rcases hc with ⟨rfl,hf⟩
      simp only [guardedFold,he,List.foldr_cons,FoldFits]
      cases hb : fits (majorantStep R (xs.foldr majorantStep seed)) <;> simp_all
      exact eq_comm

theorem guarded_fold_bits_iff (fits : ℚ → Bool) (seed : ℚ) (xs : List ℚ) :
    guardedFold fits seed xs = .error .bits ↔ ¬FoldFits fits seed xs := by
  constructor
  · intro he hf
    have ho := (guarded_fold_ok_iff fits seed (xs.foldr majorantStep seed) xs).mpr ⟨rfl,hf⟩
    rw [he] at ho
    cases ho
  · intro hf
    cases he : guardedFold fits seed xs with
    | ok B => exact False.elim (hf ((guarded_fold_ok_iff fits seed B xs).mp he).2)
    | error e =>
      cases e with
      | bits => rfl
      | steps => exact False.elim (guarded_fold_not_steps fits seed xs he)

def guardedMajorant (Q : ℚ) (maxSteps : ℕ) (fits : ℚ → Bool) (R : ℚ) : Except MajorantError ℚ :=
  match buildLadder Q maxSteps R with
  | .error e => .error e
  | .ok (xs,t) => guardedFold fits (majorantSeed t) xs

theorem guarded_majorant_success (Q R B : ℚ) (budget : ℕ) (fits : ℚ → Bool)
    (h : guardedMajorant Q budget fits R = .ok B) :
    ∃ xs t, LadderTrace Q R xs t ∧ xs.length ≤ budget ∧
      FoldFits fits (majorantSeed t) xs ∧ B = rationalDiskMajorant Q xs.length R := by
  cases he : buildLadder Q budget R with
  | error e => simp only [guardedMajorant,he] at h; cases h
  | ok pair =>
    rcases pair with ⟨xs,t⟩
    have ht := build_ladder_ok Q R budget xs t he
    have hf := (guarded_fold_ok_iff fits (majorantSeed t) B xs).mp (by simpa [guardedMajorant,he] using h)
    exact ⟨xs,t,ht.1,ht.2,hf.2,hf.1.trans (ladder_fold_eq Q R t xs ht.1)⟩

theorem guarded_majorant_small (Q R : ℚ) (budget : ℕ) (fits : ℚ → Bool) (hs : R < 1) :
    guardedMajorant Q budget fits R = .ok (majorantSeed R) := by
  cases budget <;> simp [guardedMajorant,buildLadder,hs,guardedFold]

theorem guarded_majorant_zero (Q : ℚ) (budget : ℕ) (fits : ℚ → Bool) :
    guardedMajorant Q budget fits 0 = .ok 0 := by
  simpa [majorantSeed] using guarded_majorant_small Q 0 budget fits (by norm_num)

theorem guarded_majorant_no_steps (Q R : ℚ) (fits : ℚ → Bool) (hR : 1 ≤ R) :
    guardedMajorant Q 0 fits R = .error .steps := by
  simp only [guardedMajorant,buildLadder,ite_eq_right (not_lt.mpr hR)]

theorem guarded_majorant_disk_bound (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (R B : ℚ) (hR : 0 ≤ R) (budget : ℕ) (fits : ℚ → Bool)
    (h : guardedMajorant p.maxScale budget fits R = .ok B) (i : Fin 2)
    (z : ℂ) (hz : ‖z‖ ≤ (R : ℝ)) : ‖p.toReal.complexComponent i z‖ ≤ (B : ℝ) := by
  obtain ⟨xs,t,ht,_,_,hB⟩ := guarded_majorant_success p.maxScale R B budget fits h
  rw [hB]
  exact p.toReal.rational_disk_majorant_sound hs hc p.maxScale R
    (rational_maxScale_cast p) hR xs.length (ladder_adequate _ _ _ _ ht) i hz

theorem guarded_majorant_endpoint_enclosure (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (x S B : ℚ) (hx : 0 ≤ x) (hxS : x < S) (budget : ℕ) (fits : ℚ → Bool)
    (h : guardedMajorant p.maxScale budget fits S = .ok B) (N : ℕ) (i : Fin 2) :
    (p.arrayPolynomial i N x : ℝ) ≤ p.toReal.realComponent i (x : ℝ) ∧
      p.toReal.realComponent i (x : ℝ) ≤ ((p.arrayPolynomial i N x+B*(x/S)^(2*N+3) : ℚ) : ℝ) := by
  obtain ⟨xs,t,ht,_,_,hB⟩ := guarded_majorant_success p.maxScale S B budget fits h
  rw [hB]
  exact array_endpoint_enclosure p hs hc x S hx hxS xs.length (ladder_adequate _ _ _ _ ht) N i

theorem guarded_majorant_step_failure (Q R : ℚ) (budget : ℕ) (fits : ℚ → Bool)
    (h : buildLadder Q budget R = .error .steps) :
    guardedMajorant Q budget fits R = .error .steps := by
  simp only [guardedMajorant,h]

theorem guarded_majorant_bit_failure (Q R t : ℚ) (budget : ℕ) (fits : ℚ → Bool)
    (xs : List ℚ) (h : buildLadder Q budget R = .ok (xs,t))
    (hf : ¬FoldFits fits (majorantSeed t) xs) :
    guardedMajorant Q budget fits R = .error .bits := by
  simp only [guardedMajorant,h]
  exact (guarded_fold_bits_iff fits (majorantSeed t) xs).mpr hf

/-- Mathematical binary width, including width zero for integer zero. -/
def integerWidth (n : ℕ) : ℕ := if n = 0 then 0 else n.log2+1
def rationalBitSize (B : ℚ) : ℕ := max (integerWidth B.num.natAbs) (integerWidth B.den)
def sizeFits (maxBits : ℕ) (B : ℚ) : Bool := decide (rationalBitSize B ≤ maxBits)

theorem size_fits_iff (maxBits : ℕ) (B : ℚ) :
    sizeFits maxBits B = true ↔ rationalBitSize B ≤ maxBits := by simp [sizeFits]

inductive CheckedMajorantError where
  | scales
  | radius
  | stepsInput
  | bitsInput
  | resource (e : MajorantError)
  deriving DecidableEq, Repr

def RationalScales.strictRational (p : RationalScales) : Prop :=
  0 < p.q ∧ p.q < 1 ∧ 0 < p.r ∧ p.r < 1 ∧ 0 < p.a ∧ p.a < 1 ∧ 0 < p.b ∧ p.b < 1

instance (p : RationalScales) : Decidable p.strictRational := by
  unfold RationalScales.strictRational
  infer_instance

/-- None represents an invalid nonnegative exact-integer resource input.
This is an input abstraction, not a Python runtime type checker. -/
def checkedMajorant (p : RationalScales) (R : ℚ) (steps bits : Option ℕ) :
    Except CheckedMajorantError ℚ :=
  if ¬p.strictRational then .error .scales else
  if R < 0 then .error .radius else
  if R = 0 then .ok 0 else
  match steps with
  | none => .error .stepsInput
  | some n => match bits with
      | none => .error .bitsInput
      | some 0 => .error .bitsInput
      | some (m+1) => match guardedMajorant p.maxScale n (sizeFits (m+1)) R with
          | .ok B => .ok B
          | .error e => .error (.resource e)

theorem checked_invalid_scales (p : RationalScales) (R : ℚ) (steps bits : Option ℕ)
    (hp : ¬p.strictRational) : checkedMajorant p R steps bits = .error .scales := by
  simp only [checkedMajorant,ite_eq_left hp]

theorem checked_negative_radius (p : RationalScales) (R : ℚ) (steps bits : Option ℕ)
    (hp : p.strictRational) (hR : R < 0) : checkedMajorant p R steps bits = .error .radius := by
  simp only [checkedMajorant,ite_eq_right (not_not.mpr hp),ite_eq_left hR]

theorem checked_zero_before_resources (p : RationalScales) (steps bits : Option ℕ)
    (hp : p.strictRational) : checkedMajorant p 0 steps bits = .ok 0 := by
  simp [checkedMajorant,hp]

theorem checked_invalid_steps (p : RationalScales) (R : ℚ) (bits : Option ℕ)
    (hp : p.strictRational) (hR : 0 < R) : checkedMajorant p R none bits = .error .stepsInput := by
  simp [checkedMajorant,hp,not_lt.mpr hR.le,ne_of_gt hR]

theorem checked_invalid_bits (p : RationalScales) (R : ℚ) (n : ℕ)
    (hp : p.strictRational) (hR : 0 < R) :
    checkedMajorant p R (some n) none = .error .bitsInput ∧
      checkedMajorant p R (some n) (some 0) = .error .bitsInput := by
  simp [checkedMajorant,hp,not_lt.mpr hR.le,ne_of_gt hR]

theorem checked_valid_inputs (p : RationalScales) (R : ℚ) (n m : ℕ)
    (hp : p.strictRational) (hR : 0 < R) :
    checkedMajorant p R (some n) (some (m+1)) =
      match guardedMajorant p.maxScale n (sizeFits (m+1)) R with
      | .ok B => .ok B
      | .error e => .error (.resource e) := by
  simp only [checkedMajorant,ite_eq_right (not_not.mpr hp),
    ite_eq_right (not_lt.mpr hR.le),ite_eq_right (ne_of_gt hR)]

theorem checked_small_seed_unchecked (p : RationalScales) (R : ℚ) (n m : ℕ)
    (hp : p.strictRational) (hR : 0 < R) (hs : R < 1) :
    checkedMajorant p R (some n) (some (m+1)) = .ok (majorantSeed R) := by
  rw [checked_valid_inputs p R n m hp hR,guarded_majorant_small p.maxScale R n (sizeFits (m+1)) hs]

theorem checked_success_core (p : RationalScales) (R B : ℚ) (n m : ℕ)
    (hp : p.strictRational) (hR : 0 < R)
    (h : checkedMajorant p R (some n) (some (m+1)) = .ok B) :
    guardedMajorant p.maxScale n (sizeFits (m+1)) R = .ok B := by
  rw [checked_valid_inputs p R n m hp hR] at h
  cases he : guardedMajorant p.maxScale n (sizeFits (m+1)) R with
  | ok C => rw [he] at h; cases h; rfl
  | error e => rw [he] at h; cases h

theorem checked_endpoint_enclosure (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (hp : p.strictRational) (x S B : ℚ) (hx : 0 ≤ x) (hxS : x < S) (n m : ℕ)
    (h : checkedMajorant p S (some n) (some (m+1)) = .ok B) (N : ℕ) (i : Fin 2) :
    (p.arrayPolynomial i N x : ℝ) ≤ p.toReal.realComponent i (x : ℝ) ∧
      p.toReal.realComponent i (x : ℝ) ≤ ((p.arrayPolynomial i N x+B*(x/S)^(2*N+3) : ℚ) : ℝ) := by
  have hS : 0 < S := hx.trans_lt hxS
  exact guarded_majorant_endpoint_enclosure p hs hc x S B hx hxS n (sizeFits (m+1))
    (checked_success_core p S B n m hp hS h) N i

end Komorebi.SpecialFunctions.Coupled.Scales
