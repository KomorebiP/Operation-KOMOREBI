import CoupledPythonSource

/-! Universal refinement of the source-bound imperative translation.
No Python interpreter, primitive implementation or parser correctness is
introduced as an axiom. See Block19 for the explicit translation trust boundary. -/

set_option autoImplicit false
set_option maxHeartbeats 2500000
noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales.Python

def canonicalRows (p : RationalScales) (N : ℕ) : Arrays :=
  (List.ofFn (fun i : Fin (N+1) => (p.derivatives i.val).1),
   List.ofFn (fun i : Fin (N+1) => (p.derivatives i.val).2))

theorem weighted_products (p : RationalScales) (q r : ℚ) (n : ℕ) :
    weighted q r (products (n+1) (canonicalRows p n)) = derivativeRow q r p.derivatives n := by
  unfold weighted products derivativeRow
  simp only [List.map_ofFn, Fin.sum_ofFn]
  apply Finset.sum_congr rfl
  intro i _
  have he : n+1-1-i.val = n-i.val := by omega
  have hn : 2*(n+1) = 2*n+2 := by omega
  have hu : ((canonicalRows p n).1[i.val]?).getD 0 = (p.derivatives i.val).1 := by
    simp only [canonicalRows,List.getElem?_ofFn,dite_eq_left i.isLt,Option.getD_some]
  have hj : n+1-1-i.val < n+1 := by omega
  have hv : ((canonicalRows p n).2[n+1-1-i.val]?).getD 0 = (p.derivatives (n+1-1-i.val)).2 := by
    simp only [canonicalRows,List.getElem?_ofFn,dite_eq_left hj,Option.getD_some]
  dsimp only [Function.comp_apply]
  rw [hu,hv,he,hn]

theorem append_rows_correct (p : RationalScales) (n : ℕ) :
    appendRows p (n+1) (canonicalRows p n) = canonicalRows p (n+1) := by
  have hnext := rational_derivatives_succ p n
  apply Prod.ext
  · change (canonicalRows p n).1 ++ [weighted p.q p.r (products (n+1) (canonicalRows p n))] = _
    rw [weighted_products]
    have hf := congrArg Prod.fst hnext
    simp only [RationalScales.derivativeNext] at hf
    rw [← hf]
    exact (List.ofFn_succ_last (f := fun i : Fin (n+1+1) => (p.derivatives i.val).1)).symm
  · change (canonicalRows p n).2 ++ [weighted p.a p.b (products (n+1) (canonicalRows p n))] = _
    rw [weighted_products]
    have hf := congrArg Prod.snd hnext
    simp only [RationalScales.derivativeNext] at hf
    rw [← hf]
    exact (List.ofFn_succ_last (f := fun i : Fin (n+1+1) => (p.derivatives i.val).2)).symm

theorem derivative_for_correct (p : RationalScales) (N : ℕ) :
    derivativeFor p N = canonicalRows p N := by
  induction N with
  | zero => simp [derivativeFor, canonicalRows, List.ofFn_succ, rational_derivatives_zero]
  | succ n ih =>
    simp only [derivativeFor, List.range_succ, List.foldl_append, List.foldl_cons,
      List.foldl_nil] at *
    rw [ih]
    exact append_rows_correct p n

theorem source_array_bounds (p : RationalScales) (n : ℕ) (i : Fin (n+1)) :
    i.val < (derivativeFor p n).1.length ∧
      n+1-1-i.val < (derivativeFor p n).2.length := by
  rw [derivative_for_correct]
  simp only [canonicalRows, List.length_ofFn]
  exact ⟨i.isLt, by omega⟩

theorem ordinary_rows_correct (p : RationalScales) (N : ℕ) :
    ordinary (canonicalRows p N).1 = p.ordinaryArray 0 N ∧
      ordinary (canonicalRows p N).2 = p.ordinaryArray 1 N := by
  have row (i : Fin 2) :
      ordinary (List.ofFn (fun n : Fin (N+1) => p.derivativeComponent i n.val)) =
        p.ordinaryArray i N := by
    rw [ordinary_array_eq]
    apply List.ext_getElem
    · simp [ordinary]
    · intro n hn hm
      simp only [ordinary,List.getElem_mapIdx,List.getElem_ofFn]
      exact derivative_component_normalized p i n
  exact ⟨by simpa [canonicalRows,RationalScales.derivativeComponent] using row 0,
    by simpa [canonicalRows,RationalScales.derivativeComponent] using row 1⟩

theorem partial_rows_correct (p : RationalScales) (N : ℕ) (x : ℚ) :
    partialSum (derivativeFor p N).1 x = p.arrayPolynomial 0 N x ∧
      partialSum (derivativeFor p N).2 x = p.arrayPolynomial 1 N x := by
  rw [derivative_for_correct]
  obtain ⟨hu,hv⟩ := ordinary_rows_correct p N
  simp only [partialSum,hu,hv,RationalScales.arrayPolynomial,and_self]

def attach (xs : List ℚ) : Except MajorantError (List ℚ × ℚ) →
    Except MajorantError (List ℚ × ℚ)
  | .error e => .error e
  | .ok (ys,t) => .ok (xs++ys,t)

theorem ladder_run_correct (Q : ℚ) (budget : ℕ) (xs : List ℚ) (x : ℚ)
    (out : Except MajorantError (List ℚ × ℚ)) (h : LadderRun Q budget xs x out) :
    out = attach xs (buildLadder Q (budget-xs.length) x) := by
  induction h with
  | stop xs x small =>
    cases budget-xs.length <;> simp [buildLadder,small,attach]
  | exhausted xs x large full =>
    simp [Nat.sub_eq_zero_of_le full,buildLadder,not_lt.mpr large,attach]
  | step xs x out large room child ih =>
    have he : budget-xs.length = (budget-(xs++[x]).length)+1 := by simp only [List.length_append,List.length_singleton]; omega
    rw [he]
    simp only [buildLadder,ite_eq_right (not_lt.mpr large)]
    rw [mul_comm x Q] at ih
    rw [ih]
    cases hc : buildLadder Q (budget-(xs++[x]).length) (Q*x) with
    | error e => rfl
    | ok pair => rcases pair with ⟨ys,t⟩; simp [attach,List.append_assoc]

theorem ladder_empty_correct (p : RationalScales) (R : ℚ) (budget : ℕ)
    (out : Except MajorantError (List ℚ × ℚ)) (h : LadderRun p.maxScale budget [] R out) :
    out = buildLadder p.maxScale budget R := by
  have he := ladder_run_correct p.maxScale budget [] R out h
  simp only [List.length_nil,Nat.sub_zero] at he
  rw [he]
  cases buildLadder p.maxScale budget R <;> rfl

theorem seed_correct (x : ℚ) : seed x = majorantSeed x := by simp [seed,majorantSeed,pow_two]
theorem update_correct (x b : ℚ) : update x b = majorantStep x b := by simp [update,majorantStep,pow_two]

theorem fold_for_append (bits : ℕ) (xs ys : List ℚ) (B : ℚ) :
    foldFor bits (xs++ys) B =
      match foldFor bits xs B with
      | .error e => .error e
      | .ok C => foldFor bits ys C := by
  induction xs generalizing B with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.cons_append,foldFor]
    split
    · rfl
    · exact ih _

theorem fold_for_reverse (bits : ℕ) (xs : List ℚ) (B : ℚ) :
    foldFor bits xs.reverse B = guardedFold (sizeFits bits) B xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih =>
    rw [List.reverse_cons,fold_for_append,ih]
    simp only [guardedFold]
    cases he : guardedFold (sizeFits bits) B xs with
    | error e => rfl
    | ok C =>
      simp only [foldFor,update_correct]
      by_cases hb : rationalBitSize (majorantStep x C) ≤ bits
      · simp [hb,not_lt.mpr hb,sizeFits]
      · simp [hb,lt_of_not_ge hb,sizeFits]

theorem finish_majorant_correct (Q : ℚ) (R : ℚ) (steps bits : ℕ)
    (out : Except MajorantError (List ℚ × ℚ))
    (h : out = buildLadder Q steps R) :
    finishMajorant bits out = guardedMajorant Q steps (sizeFits bits) R := by
  rw [h]
  simp only [guardedMajorant]
  cases he : buildLadder Q steps R with
  | error e => rfl
  | ok pair => rcases pair with ⟨xs,t⟩; simp only [finishMajorant,fold_for_reverse,seed_correct]

theorem majorant_run_correct (p : RationalScales) (R : ℚ) (steps bits : ℕ)
    (out : Except CheckedMajorantError ℚ) (h : MajorantRun p R steps bits out) :
    checkedMajorant p R (some steps) (some bits) = out := by
  cases h with
  | scales bad => exact checked_invalid_scales p R (some steps) (some bits) bad
  | radius valid negative => exact checked_negative_radius p R (some steps) (some bits) valid negative
  | zero valid origin => subst R; exact checked_zero_before_resources p _ _ valid
  | bitsInvalid valid positive invalid =>
    subst bits
    exact (checked_invalid_bits p R steps valid positive).2
  | positive valid positive positiveBits out trace =>
    obtain ⟨m,rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt positiveBits)
    rw [checked_valid_inputs p R steps m valid positive]
    rw [finish_majorant_correct p.maxScale R steps (m+1) out (ladder_empty_correct p R steps out trace)]
    rfl

def encode (v : EvaluationResult) : Dictionary :=
  [("x", .rational v.x), ("last_index", .integer (v.last_index : ℤ)),
   ("outer_radius", .rational v.outer_radius), ("majorant", .rational v.majorant),
   ("tail_bound", .rational v.tail_bound),
   ("U", .tuple (.rational v.U.1) (.rational v.U.2)),
   ("V", .tuple (.rational v.V.1) (.rational v.V.2))]

def encodeOutcome : Except EvaluationError EvaluationResult → Except EvaluationError Dictionary
  | .error e => .error e
  | .ok v => .ok (encode v)

theorem dictionary_correct (p : RationalScales) (x S B : ℚ) (N : ℕ) :
    resultDictionary x N S B (partialSum (derivativeFor p N).1 x) (partialSum (derivativeFor p N).2 x) =
      encode (makeEvaluationResult p x S B N) := by
  obtain ⟨hu,hv⟩ := partial_rows_correct p N x
  rw [hu,hv]
  rfl

theorem evaluation_run_correct (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (out : Except EvaluationError Dictionary)
    (h : EvaluationRun p x last outer out) :
    out = encodeOutcome (certifiedEvaluationSpec p x last outer) := by
  cases h with
  | lastInvalid invalid => subst last; rfl
  | scales N index bad => subst last; rw [evaluation_invalid_scales p x N outer bad]; rfl
  | negative N index valid negative => subst last; rw [evaluation_negative_x p x N outer valid negative]; rfl
  | outerInvalid N index valid nonneg bad =>
    subst last
    change evaluationOuter x outer ≤ x at bad
    simp only [certifiedEvaluationSpec,ite_eq_right (not_not.mpr valid),
      ite_eq_right (not_lt.mpr nonneg),ite_eq_left bad,encodeOutcome]
  | evaluated N index valid nonneg strictOuter uv arrays u v first second out majorant =>
    subst last
    rw [← arrays] at first second
    subst u; subst v
    have hm := majorant_run_correct p (outerRadius x outer) defaultSteps defaultBits out majorant
    change checkedMajorant p (evaluationOuter x outer) (some 20) (some 2000000) = out at hm
    cases out with
    | error e =>
      rw [evaluation_majorant_error p x N outer e valid nonneg strictOuter hm]
      rfl
    | ok B =>
      rw [evaluation_of_majorant_ok p x B N outer valid nonneg strictOuter hm]
      exact congrArg Except.ok (dictionary_correct p x (outerRadius x outer) B N)

theorem source_return_refines (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (d : Dictionary) (h : EvaluationRun p x last outer (.ok d)) :
    ∃ v, certifiedEvaluationSpec p x last outer = .ok v ∧ d = encode v := by
  have he := evaluation_run_correct p x last outer (.ok d) h
  cases hs : certifiedEvaluationSpec p x last outer with
  | error e => rw [hs] at he; cases he
  | ok v =>
    rw [hs] at he
    exact ⟨v,rfl,Except.ok.inj he⟩

theorem source_return_encloses (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (d : Dictionary) (h : EvaluationRun p x last outer (.ok d)) :
    ∃ v, d = encode v ∧
      ((v.U.1 : ℝ) ≤ p.toReal.realComponent 0 (x : ℝ) ∧
        p.toReal.realComponent 0 (x : ℝ) ≤ (v.U.2 : ℝ)) ∧
      ((v.V.1 : ℝ) ≤ p.toReal.realComponent 1 (x : ℝ) ∧
        p.toReal.realComponent 1 (x : ℝ) ≤ (v.V.2 : ℝ)) := by
  obtain ⟨v,hv,hd⟩ := source_return_refines p x last outer d h
  exact ⟨v,hd,evaluation_success_encloses p x last outer v hv⟩

theorem source_return_disk_error (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (d : Dictionary) (h : EvaluationRun p x last outer (.ok d)) :
    ∃ v, d = encode v ∧ ∀ i : Fin 2, ∀ z : ℂ, ‖z‖ ≤ (x : ℝ) →
      ‖p.toReal.complexComponent i z - p.toReal.oddPolynomial i v.last_index z‖ ≤
        (v.tail_bound : ℝ) := by
  obtain ⟨v,hv,hd⟩ := source_return_refines p x last outer d h
  exact ⟨v,hd,fun i z hz => evaluation_success_disk_error p x last outer v hv i z hz⟩

theorem source_dictionary_keys (v : EvaluationResult) :
    (encode v).map Prod.fst = ["x","last_index","outer_radius","majorant","tail_bound","U","V"] := rfl

theorem source_default_parameters : defaultSteps = 20 ∧ defaultBits = 2000000 ∧ defaultLast = 24 :=
  ⟨rfl,rfl,rfl⟩

theorem source_integer_index_safe (n : ℕ) (i : Fin (n+1)) :
    0 ≤ (n+1 : ℤ)-1-(i.val : ℤ) ∧
      ((n+1 : ℤ)-1-(i.val : ℤ)).toNat = n+1-1-i.val := by
  omega

theorem source_factorial_nonzero (n : ℕ) : (((2*n+1).factorial : ℚ)) ≠ 0 :=
  oddFactorial_ne_zero n

theorem source_seed_safe (p : RationalScales) (R : ℚ) (steps : ℕ) (xs : List ℚ) (t : ℚ)
    (hp : p.strictRational) (hR : 0 < R) (h : LadderRun p.maxScale steps [] R (.ok (xs,t))) :
    0 < t ∧ 0 < 1-t*t := by
  have hbuild := (ladder_empty_correct p R steps (.ok (xs,t)) h).symm
  have ht := (build_ladder_ok p.maxScale R steps xs t hbuild).1
  have hq : 0 < p.maxScale := hp.1.trans_le
    ((le_max_left p.q p.r).trans (le_max_left (max p.q p.r) (max p.a p.b)))
  have hpos : 0 < t := by
    rw [ladder_terminal p.maxScale R t xs ht]
    exact mul_pos (pow_pos hq _) hR
  have hsmall := ladder_terminal_small p.maxScale R t xs ht
  exact ⟨hpos,by nlinarith⟩

theorem source_ladder_total (Q : ℚ) (budget : ℕ) (xs : List ℚ) (x : ℚ) :
    ∃ out, LadderRun Q budget xs x out := by
  have go : ∀ fuel : ℕ, ∀ ys : List ℚ, ∀ y : ℚ,
      budget-ys.length = fuel → ∃ out, LadderRun Q budget ys y out := by
    intro fuel
    induction fuel with
    | zero =>
      intro ys y hf
      by_cases hs : y < 1
      · exact ⟨.ok (ys,y),.stop ys y hs⟩
      · exact ⟨.error .steps,.exhausted ys y (le_of_not_gt hs) (by omega)⟩
    | succ n ih =>
      intro ys y hf
      by_cases hs : y < 1
      · exact ⟨.ok (ys,y),.stop ys y hs⟩
      · have hr : ys.length < budget := by omega
        have hc : budget-(ys++[y]).length = n := by
          simp only [List.length_append,List.length_singleton]
          omega
        obtain ⟨out,hout⟩ := ih (ys++[y]) (y*Q) hc
        exact ⟨out,.step ys y out (le_of_not_gt hs) hr hout⟩
  exact go (budget-xs.length) xs x rfl

theorem source_majorant_total (p : RationalScales) (R : ℚ) (steps bits : ℕ) :
    ∃ out, MajorantRun p R steps bits out := by
  by_cases hp : p.strictRational
  · by_cases hn : R < 0
    · exact ⟨.error .radius,.radius hp hn⟩
    · by_cases hz : R = 0
      · exact ⟨.ok 0,.zero hp hz⟩
      · have hpos : 0 < R := lt_of_le_of_ne (le_of_not_gt hn) (Ne.symm hz)
        by_cases hb : bits = 0
        · exact ⟨.error .bitsInput,.bitsInvalid hp hpos hb⟩
        · obtain ⟨out,trace⟩ := source_ladder_total p.maxScale steps [] R
          exact ⟨_,.positive hp hpos (Nat.pos_of_ne_zero hb) out trace⟩
  · exact ⟨.error .scales,.scales hp⟩

theorem source_evaluation_total (p : RationalScales) (x : ℚ) (last : Option ℕ) (outer : Option ℚ) :
    ∃ out, EvaluationRun p x last outer out := by
  cases last with
  | none => exact ⟨.error .lastInput,.lastInvalid rfl⟩
  | some N =>
    by_cases hp : p.strictRational
    · by_cases hn : x < 0
      · exact ⟨.error .negativeX,.negative N rfl hp hn⟩
      · have hx := le_of_not_gt hn
        by_cases hS : outerRadius x outer ≤ x
        · exact ⟨.error .outerRadius,.outerInvalid N rfl hp hx hS⟩
        · obtain ⟨out,majorant⟩ := source_majorant_total p (outerRadius x outer) defaultSteps defaultBits
          exact ⟨_,.evaluated N rfl hp hx (lt_of_not_ge hS) (derivativeFor p N) rfl
            (partialSum (derivativeFor p N).1 x) (partialSum (derivativeFor p N).2 x)
            rfl rfl out majorant⟩
    · exact ⟨.error .scales,.scales N rfl hp⟩

theorem source_evaluation_deterministic (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (a b : Except EvaluationError Dictionary)
    (ha : EvaluationRun p x last outer a) (hb : EvaluationRun p x last outer b) : a = b :=
  (evaluation_run_correct p x last outer a ha).trans (evaluation_run_correct p x last outer b hb).symm

theorem source_evaluation_iff (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (out : Except EvaluationError Dictionary) :
    EvaluationRun p x last outer out ↔ out = encodeOutcome (certifiedEvaluationSpec p x last outer) := by
  constructor
  · exact evaluation_run_correct p x last outer out
  · intro he
    obtain ⟨actual,ha⟩ := source_evaluation_total p x last outer
    rw [he,(evaluation_run_correct p x last outer actual ha).symm]
    exact ha

theorem source_index_classification (input : IndexValue) (N : ℕ) :
    classifyIndex input = some N ↔ input = .integer (N : ℤ) := by
  cases input with
  | boolean b => simp [classifyIndex]
  | other => simp [classifyIndex]
  | integer z =>
    constructor
    · intro h
      by_cases hz : z < 0
      · simp [classifyIndex,hz] at h
      · have hn : z.toNat = N := by simpa [classifyIndex,hz] using h
        have he : z = (N : ℤ) := by omega
        rw [he]
    · intro h
      have he := IndexValue.integer.inj h
      rw [he]
      simp [classifyIndex]

theorem source_invalid_index_before_conversion {α ε : Type} (convert : α → Except ε ℚ)
    (input : IndexValue) (q r a b x : α) (outer : Option α) (h : classifyIndex input = none) :
    prepare convert input q r a b x outer = .error (.validation .lastInput) := by
  simp [prepare,h]
  rfl

theorem raw_source_return_encloses {α ε : Type} (convert : α → Except ε ℚ)
    (input : IndexValue) (q r a b x : α) (outer : Option α) (d : Dictionary)
    (h : RawEvaluationRun convert input q r a b x outer (.ok d)) :
    ∃ s v, prepare convert input q r a b x outer = .ok s ∧
      d = encode v ∧ v.x = s.x ∧
      ((v.U.1 : ℝ) ≤ s.p.toReal.realComponent 0 (s.x : ℝ) ∧
        s.p.toReal.realComponent 0 (s.x : ℝ) ≤ (v.U.2 : ℝ)) ∧
      ((v.V.1 : ℝ) ≤ s.p.toReal.realComponent 1 (s.x : ℝ) ∧
        s.p.toReal.realComponent 1 (s.x : ℝ) ≤ (v.V.2 : ℝ)) := by
  generalize ho : (Except.ok d : Except (RawError ε) Dictionary) = outcome at h
  cases h with
  | preparationError e hs => cases ho
  | prepared s hs out execution =>
    cases out with
    | error e => cases ho
    | ok d =>
      cases ho
      obtain ⟨v,hv,hd⟩ := source_return_refines s.p s.x (some s.N) (some s.S) d execution
      exact ⟨s,v,hs,hd,(evaluation_success_metadata s.p s.x (some s.N) (some s.S) v hv).1,
        evaluation_success_encloses s.p s.x (some s.N) (some s.S) v hv⟩

theorem raw_source_total {α ε : Type} (convert : α → Except ε ℚ)
    (input : IndexValue) (q r a b x : α) (outer : Option α) :
    ∃ out, RawEvaluationRun convert input q r a b x outer out := by
  cases h : prepare convert input q r a b x outer with
  | error e => exact ⟨_,.preparationError e h⟩
  | ok s =>
    obtain ⟨out,ho⟩ := source_evaluation_total s.p s.x (some s.N) (some s.S)
    exact ⟨_,.prepared s h out ho⟩

theorem raw_source_return_disk_error {α ε : Type} (convert : α → Except ε ℚ)
    (input : IndexValue) (q r a b x : α) (outer : Option α) (d : Dictionary)
    (h : RawEvaluationRun convert input q r a b x outer (.ok d)) :
    ∃ s v, prepare convert input q r a b x outer = .ok s ∧ d = encode v ∧ v.x = s.x ∧
      ∀ i : Fin 2, ∀ z : ℂ, ‖z‖ ≤ (s.x : ℝ) →
        ‖s.p.toReal.complexComponent i z - s.p.toReal.oddPolynomial i v.last_index z‖ ≤
          (v.tail_bound : ℝ) := by
  generalize ho : (Except.ok d : Except (RawError ε) Dictionary) = outcome at h
  cases h with
  | preparationError e hs => cases ho
  | prepared s hs out execution =>
    cases out with
    | error e => cases ho
    | ok d =>
      cases ho
      obtain ⟨v,hv,hd⟩ := source_return_refines s.p s.x (some s.N) (some s.S) d execution
      exact ⟨s,v,hs,hd,(evaluation_success_metadata s.p s.x (some s.N) (some s.S) v hv).1,
        fun i z hz => evaluation_success_disk_error s.p s.x (some s.N) (some s.S) v hv i z hz⟩

theorem dictionary_representation_injective : Function.Injective encode := by
  intro a b h
  cases a
  cases b
  simp_all [encode,Prod.ext_iff]

end Komorebi.SpecialFunctions.Coupled.Scales.Python
