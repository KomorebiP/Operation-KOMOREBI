import CoupledSourceExpressions

/-! The typed source-expression interpreter agrees with the separately emitted
source operations for every input in each source-variable environment. The
parser and AST-data extraction remain trusted; the arithmetic printer is now
checked against this independent semantic interpretation. -/

set_option autoImplicit false
set_option maxHeartbeats 2500000
noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions

def interpretedProducts (n : ℕ) (uv : Arrays) : List Product :=
  List.ofFn (fun i : Fin n =>
    let e := env [("n",n),("i",i.val)] [] [("u",uv.1),("v",uv.2)]
    (evalRat e Source.product,evalNat e Source.q_power,evalNat e Source.r_power))

theorem product_expression_lowering (n : ℕ) (uv : Arrays) :
    interpretedProducts n uv = products n uv := by
  rfl

def interpretedWeights (p : RationalScales) (ts : List Product) : ℚ × ℚ :=
  let e := fun t : Product => env [("i",t.2.1),("j",t.2.2)]
    [("c",t.1),("q",p.q),("r",p.r),("a",p.a),("b",p.b)]
  ((ts.map (fun t => evalRat (e t) Source.weight_u)).sum,
   (ts.map (fun t => evalRat (e t) Source.weight_v)).sum)

theorem weight_expression_lowering (p : RationalScales) (ts : List Product) :
    interpretedWeights p ts = (weighted p.q p.r ts,weighted p.a p.b ts) := by
  rfl

def expressionAppend (p : RationalScales) (n : ℕ) (uv : Arrays) : Arrays :=
  let weights := interpretedWeights p (interpretedProducts n uv)
  (uv.1++[weights.1],uv.2++[weights.2])

theorem expression_append_lowering (p : RationalScales) (n : ℕ) (uv : Arrays) :
    expressionAppend p n uv = appendRows p n uv := by
  simp only [expressionAppend,product_expression_lowering,weight_expression_lowering,appendRows]

def expressionFor (p : RationalScales) (N : ℕ) : Arrays :=
  (List.range N).foldl (fun uv k => expressionAppend p (k+1) uv) ([1],[1])

theorem expression_for_lowering (p : RationalScales) (N : ℕ) :
    expressionFor p N = derivativeFor p N := by
  simp only [expressionFor,expression_append_lowering,derivativeFor]

theorem expression_arrays_correct (p : RationalScales) (N : ℕ) :
    expressionFor p N = canonicalRows p N := by
  rw [expression_for_lowering,derivative_for_correct]

def interpretedOrdinary (row : List ℚ) : List ℚ :=
  row.mapIdx (fun n a => evalRat (env [("n",n)] [("a",a)]) Source.ordinary)

theorem ordinary_expression_lowering (row : List ℚ) :
    interpretedOrdinary row = ordinary row := by
  rfl

def interpretedPartial (row : List ℚ) (x : ℚ) : ℚ :=
  ((interpretedOrdinary row).mapIdx (fun n c =>
    evalRat (env [("n",n)] [("c",c),("x",x)]) Source.partial_term)).sum

theorem partial_expression_lowering (row : List ℚ) (x : ℚ) :
    interpretedPartial row x = partialSum row x := by
  rfl

theorem seed_expression_lowering (x : ℚ) :
    evalRat (env [] [("x",x)]) Source.seed = seed x := by
  rfl

theorem update_expression_lowering (x b : ℚ) :
    evalRat (env [] [("x",x),("bound",b)]) Source.update = update x b := by
  rfl

theorem outer_expression_lowering (x : ℚ) :
    evalRat (env [] [("x",x)]) Source.outer_default = outerRadius x none := by
  rfl

theorem tail_expression_lowering (B x S : ℚ) (N : ℕ) :
    evalRat (env [("last",N)] [("majorant",B),("x",x),("s",S)]) Source.tail = tail B x S N := by
  rfl

theorem resource_expression_defaults :
    evalNat (env) Source.steps_default = defaultSteps ∧
    evalNat (env) Source.bits_default = defaultBits ∧
    evalNat (env) Source.last_default = defaultLast := by
  exact ⟨rfl,rfl,rfl⟩

def interpretedDictionary (x : ℚ) (N : ℕ) (S B u v : ℚ) : Dictionary :=
  let t := evalRat (env [("last",N)] [("majorant",B),("x",x),("s",S)]) Source.tail
  evalDictionary (env [("last",N)]
    [("x",x),("s",S),("majorant",B),("tail",t)] [("partial",[u,v])]) Source.dictionary

theorem dictionary_expression_lowering (x : ℚ) (N : ℕ) (S B u v : ℚ) :
    interpretedDictionary x N S B u v = resultDictionary x N S B u v := by
  rfl

def expressionResult (p : RationalScales) (x : ℚ) (N : ℕ) (S B : ℚ) : Dictionary :=
  let uv := expressionFor p N
  interpretedDictionary x N S B (interpretedPartial uv.1 x) (interpretedPartial uv.2 x)

theorem expression_result_correct (p : RationalScales) (x : ℚ) (N : ℕ) (S B : ℚ) :
    expressionResult p x N S B = encode (makeEvaluationResult p x S B N) := by
  simp only [expressionResult,expression_for_lowering,partial_expression_lowering,
    dictionary_expression_lowering]
  exact dictionary_correct p x S B N

theorem expression_result_success (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (v : EvaluationResult)
    (h : certifiedEvaluationSpec p x last outer = .ok v) :
    expressionResult p v.x v.last_index v.outer_radius v.majorant = encode v := by
  obtain ⟨N,B,_,_,_,_,_,rfl⟩ := evaluation_success_shape p x last outer v h
  exact expression_result_correct p x N (evaluationOuter x outer) B

theorem source_return_interpreted (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (d : Dictionary) (h : EvaluationRun p x last outer (.ok d)) :
    ∃ v, certifiedEvaluationSpec p x last outer = .ok v ∧
      d = expressionResult p v.x v.last_index v.outer_radius v.majorant := by
  obtain ⟨v,hv,hd⟩ := source_return_refines p x last outer d h
  exact ⟨v,hv,hd.trans (expression_result_success p x last outer v hv).symm⟩

theorem interpreted_result_encloses (p : RationalScales) (x : ℚ) (last : Option ℕ)
    (outer : Option ℚ) (v : EvaluationResult)
    (h : certifiedEvaluationSpec p x last outer = .ok v) :
    expressionResult p v.x v.last_index v.outer_radius v.majorant = encode v ∧
      ((v.U.1 : ℝ) ≤ p.toReal.realComponent 0 (x : ℝ) ∧
        p.toReal.realComponent 0 (x : ℝ) ≤ (v.U.2 : ℝ)) ∧
      ((v.V.1 : ℝ) ≤ p.toReal.realComponent 1 (x : ℝ) ∧
        p.toReal.realComponent 1 (x : ℝ) ≤ (v.V.2 : ℝ)) := by
  exact ⟨expression_result_success p x last outer v h,
    evaluation_success_encloses p x last outer v h⟩

theorem expression_first_omitted_degree (B x S : ℚ) :
    evalRat (env [("last",0)] [("majorant",B),("x",x),("s",S)]) Source.tail = B*(x/S)^3 := by
  rfl

theorem expression_dictionary_keys (x : ℚ) (N : ℕ) (S B u v : ℚ) :
    (interpretedDictionary x N S B u v).map Prod.fst =
      ["x","last_index","outer_radius","majorant","tail_bound","U","V"] := by
  rfl

end Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions
