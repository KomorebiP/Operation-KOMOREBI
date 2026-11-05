import CoupledGuardedMajorant

/-!
# Typed exact evaluation results

This specification composes the finite arrays and checked majorant with the
fixed resource defaults used by `certified_evaluation`. Inputs are already
converted rationals; `none` for `last` is an abstract invalid-input tag.
It does not formalize Python conversion, dictionaries, mutation or exceptions.
-/

set_option autoImplicit false
set_option maxHeartbeats 2500000
noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales

structure EvaluationResult where
  x : ℚ
  last_index : ℕ
  outer_radius : ℚ
  majorant : ℚ
  tail_bound : ℚ
  U : ℚ × ℚ
  V : ℚ × ℚ
  deriving DecidableEq, Repr

inductive EvaluationError where
  | lastInput
  | scales
  | negativeX
  | outerRadius
  | majorant (e : CheckedMajorantError)
  deriving DecidableEq, Repr

def evaluationOuter (x : ℚ) (outer : Option ℚ) : ℚ :=
  outer.getD (max 1 (2*x))

def makeEvaluationResult (p : RationalScales) (x S B : ℚ) (N : ℕ) : EvaluationResult :=
  let tail := B*(x/S)^(2*N+3)
  { x := x, last_index := N, outer_radius := S, majorant := B,
    tail_bound := tail,
    U := (p.arrayPolynomial 0 N x, p.arrayPolynomial 0 N x + tail),
    V := (p.arrayPolynomial 1 N x, p.arrayPolynomial 1 N x + tail) }

/-- Fixed defaults mirror the call `disk_majorant(*p,s)` in the Python source. -/
def certifiedEvaluationSpec (p : RationalScales) (x : ℚ) (last : Option ℕ := some 24)
    (outer : Option ℚ := none) : Except EvaluationError EvaluationResult :=
  match last with
  | none => .error .lastInput
  | some N =>
    if ¬p.strictRational then .error .scales else
    if x < 0 then .error .negativeX else
    let S := evaluationOuter x outer
    if S ≤ x then .error .outerRadius else
    match checkedMajorant p S (some 20) (some 2000000) with
    | .error e => .error (.majorant e)
    | .ok B => .ok (makeEvaluationResult p x S B N)

theorem evaluation_default_outer_gt (x : ℚ) :
    x < evaluationOuter x none := by
  simp only [evaluationOuter, Option.getD_none]
  by_cases h : x < 1
  · exact h.trans_le (le_max_left _ _)
  · have hp : 0 < x := lt_of_lt_of_le (by norm_num : (0 : ℚ) < 1) (le_of_not_gt h)
    exact (show x < 2*x by linarith).trans_le (le_max_right _ _)

theorem strict_rational_real (p : RationalScales) (hp : p.strictRational) :
    p.toReal.positive ∧
      (p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1) := by
  rcases hp with ⟨hq0,hq1,hr0,hr1,ha0,ha1,hb0,hb1⟩
  change (0 < (p.q : ℝ) ∧ 0 < (p.r : ℝ) ∧ 0 < (p.a : ℝ) ∧ 0 < (p.b : ℝ)) ∧
    ((p.q : ℝ) < 1 ∧ (p.r : ℝ) < 1 ∧ (p.a : ℝ) < 1 ∧ (p.b : ℝ) < 1)
  exact_mod_cast (show (0 < p.q ∧ 0 < p.r ∧ 0 < p.a ∧ 0 < p.b) ∧
    (p.q < 1 ∧ p.r < 1 ∧ p.a < 1 ∧ p.b < 1) from
    ⟨⟨hq0,hr0,ha0,hb0⟩,⟨hq1,hr1,ha1,hb1⟩⟩)

theorem evaluation_result_metadata (p : RationalScales) (x S B : ℚ) (N : ℕ) :
    let v := makeEvaluationResult p x S B N
    v.x = x ∧ v.last_index = N ∧ v.outer_radius = S ∧ v.majorant = B := by
  exact ⟨rfl,rfl,rfl,rfl⟩

theorem evaluation_result_tail (p : RationalScales) (x S B : ℚ) (N : ℕ) :
    (makeEvaluationResult p x S B N).tail_bound = B*(x/S)^(2*N+3) := rfl

theorem evaluation_result_endpoints (p : RationalScales) (x S B : ℚ) (N : ℕ) :
    let v := makeEvaluationResult p x S B N
    v.U = (p.arrayPolynomial 0 N x, p.arrayPolynomial 0 N x+v.tail_bound) ∧
      v.V = (p.arrayPolynomial 1 N x, p.arrayPolynomial 1 N x+v.tail_bound) := by
  exact ⟨rfl,rfl⟩

theorem evaluation_result_retained_count (p : RationalScales) (x S B : ℚ) (N : ℕ) :
    let v := makeEvaluationResult p x S B N
    (p.ordinaryArray 0 v.last_index).length = N+1 ∧
      (p.ordinaryArray 1 v.last_index).length = N+1 := by
  exact ⟨ordinary_array_length p 0 N,ordinary_array_length p 1 N⟩

theorem evaluation_result_zero_index (p : RationalScales) (x S B : ℚ) :
    let v := makeEvaluationResult p x S B 0
    v.tail_bound = B*(x/S)^3 ∧ v.U.1 = x ∧ v.V.1 = x := by
  simp [makeEvaluationResult, array_polynomial_eq, RationalScales.polynomial,
    RationalScales.componentCoefficient, RationalScales.coefficients]

theorem evaluation_invalid_last_first (p : RationalScales) (x : ℚ) (outer : Option ℚ) :
    certifiedEvaluationSpec p x none outer = .error .lastInput := rfl

theorem evaluation_invalid_scales (p : RationalScales) (x : ℚ) (N : ℕ)
    (outer : Option ℚ) (hp : ¬p.strictRational) :
    certifiedEvaluationSpec p x (some N) outer = .error .scales := by
  simp only [certifiedEvaluationSpec,ite_eq_left hp]

theorem evaluation_negative_x (p : RationalScales) (x : ℚ) (N : ℕ)
    (outer : Option ℚ) (hp : p.strictRational) (hx : x < 0) :
    certifiedEvaluationSpec p x (some N) outer = .error .negativeX := by
  simp only [certifiedEvaluationSpec,ite_eq_right (not_not.mpr hp),ite_eq_left hx]

theorem evaluation_invalid_outer (p : RationalScales) (x S : ℚ) (N : ℕ)
    (hp : p.strictRational) (hx : 0 ≤ x) (hS : S ≤ x) :
    certifiedEvaluationSpec p x (some N) (some S) = .error .outerRadius := by
  simp [certifiedEvaluationSpec,hp,not_lt.mpr hx,evaluationOuter,hS]

theorem evaluation_of_majorant_ok (p : RationalScales) (x B : ℚ) (N : ℕ)
    (outer : Option ℚ) (hp : p.strictRational) (hx : 0 ≤ x)
    (hS : x < evaluationOuter x outer)
    (hB : checkedMajorant p (evaluationOuter x outer) (some 20) (some 2000000) = .ok B) :
    certifiedEvaluationSpec p x (some N) outer =
      .ok (makeEvaluationResult p x (evaluationOuter x outer) B N) := by
  simp only [certifiedEvaluationSpec,ite_eq_right (not_not.mpr hp),
    ite_eq_right (not_lt.mpr hx),ite_eq_right (not_le.mpr hS),hB]

theorem evaluation_majorant_error (p : RationalScales) (x : ℚ) (N : ℕ)
    (outer : Option ℚ) (e : CheckedMajorantError) (hp : p.strictRational) (hx : 0 ≤ x)
    (hS : x < evaluationOuter x outer)
    (hB : checkedMajorant p (evaluationOuter x outer) (some 20) (some 2000000) = .error e) :
    certifiedEvaluationSpec p x (some N) outer = .error (.majorant e) := by
  simp only [certifiedEvaluationSpec,ite_eq_right (not_not.mpr hp),
    ite_eq_right (not_lt.mpr hx),ite_eq_right (not_le.mpr hS),hB]

theorem evaluation_success_shape (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (v : EvaluationResult)
    (h : certifiedEvaluationSpec p x last outer = .ok v) :
    ∃ N B, last = some N ∧ p.strictRational ∧ 0 ≤ x ∧ x < evaluationOuter x outer ∧
      checkedMajorant p (evaluationOuter x outer) (some 20) (some 2000000) = .ok B ∧
      v = makeEvaluationResult p x (evaluationOuter x outer) B N := by
  cases last with
  | none => cases h
  | some N =>
    by_cases hp : p.strictRational
    · by_cases hx : x < 0
      · rw [evaluation_negative_x p x N outer hp hx] at h
        cases h
      · by_cases hS : evaluationOuter x outer ≤ x
        · simp only [certifiedEvaluationSpec,ite_eq_right (not_not.mpr hp),
            ite_eq_right hx,ite_eq_left hS] at h
          cases h
        · cases he : checkedMajorant p (evaluationOuter x outer) (some 20) (some 2000000) with
          | error e =>
            rw [evaluation_majorant_error p x N outer e hp (le_of_not_gt hx)
              (lt_of_not_ge hS) he] at h
            cases h
          | ok B =>
            rw [evaluation_of_majorant_ok p x B N outer hp (le_of_not_gt hx)
              (lt_of_not_ge hS) he] at h
            cases h
            exact ⟨N,B,rfl,hp,le_of_not_gt hx,lt_of_not_ge hS,rfl,rfl⟩
    · rw [evaluation_invalid_scales p x N outer hp] at h
      cases h

theorem evaluation_success_metadata (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (v : EvaluationResult)
    (h : certifiedEvaluationSpec p x last outer = .ok v) :
    v.x = x ∧ last = some v.last_index ∧ v.outer_radius = evaluationOuter x outer ∧
      v.tail_bound = v.majorant*(x/v.outer_radius)^(2*v.last_index+3) ∧
      (p.ordinaryArray 0 v.last_index).length = v.last_index+1 ∧
      (p.ordinaryArray 1 v.last_index).length = v.last_index+1 := by
  obtain ⟨N,B,hN,_,_,_,_,rfl⟩ := evaluation_success_shape p x last outer v h
  exact ⟨rfl,hN,rfl,rfl,ordinary_array_length p 0 N,ordinary_array_length p 1 N⟩

theorem evaluation_success_encloses (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (v : EvaluationResult)
    (h : certifiedEvaluationSpec p x last outer = .ok v) :
    ((v.U.1 : ℝ) ≤ p.toReal.realComponent 0 (x : ℝ) ∧
      p.toReal.realComponent 0 (x : ℝ) ≤ (v.U.2 : ℝ)) ∧
    ((v.V.1 : ℝ) ≤ p.toReal.realComponent 1 (x : ℝ) ∧
      p.toReal.realComponent 1 (x : ℝ) ≤ (v.V.2 : ℝ)) := by
  obtain ⟨N,B,_,hp,hx,hS,hB,rfl⟩ := evaluation_success_shape p x last outer v h
  obtain ⟨hs,hc⟩ := strict_rational_real p hp
  exact ⟨checked_endpoint_enclosure p hs hc hp x (evaluationOuter x outer) B hx hS
      20 1999999 hB N 0,
    checked_endpoint_enclosure p hs hc hp x (evaluationOuter x outer) B hx hS
      20 1999999 hB N 1⟩

theorem evaluation_success_disk_error (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (v : EvaluationResult)
    (h : certifiedEvaluationSpec p x last outer = .ok v) (i : Fin 2)
    (z : ℂ) (hz : ‖z‖ ≤ (x : ℝ)) :
    ‖p.toReal.complexComponent i z - p.toReal.oddPolynomial i v.last_index z‖ ≤
      (v.tail_bound : ℝ) := by
  obtain ⟨N,B,_,hp,hx,hS,hB,rfl⟩ := evaluation_success_shape p x last outer v h
  obtain ⟨hs,hc⟩ := strict_rational_real p hp
  have hcore := checked_success_core p (evaluationOuter x outer) B 20 1999999 hp
    (hx.trans_lt hS) hB
  obtain ⟨xs,t,ht,_,_,hvalue⟩ := guarded_majorant_success p.maxScale
    (evaluationOuter x outer) B 20 (sizeFits 2000000) hcore
  change _ ≤ ((B*(x/evaluationOuter x outer)^(2*N+3) : ℚ) : ℝ)
  rw [hvalue]
  exact p.toReal.rational_outer_remainder hs hc p.maxScale x (evaluationOuter x outer)
    (rational_maxScale_cast p) hx hS xs.length (ladder_adequate _ _ _ _ ht) N i hz

end Komorebi.SpecialFunctions.Coupled.Scales
