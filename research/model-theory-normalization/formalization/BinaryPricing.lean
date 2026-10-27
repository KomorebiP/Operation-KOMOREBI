module
public import BinaryCosted

@[expose] public section
namespace Komorebi.Binary

/-- Arithmetic building blocks whose computation and gate/cell prices are verified here. -/
inductive Request where
  | add (a b : Word)
  | multiply (a b : Word)
  | quotient (a b : Word)
  | remainder (a b : Word)
  | modularMultiply (a b m : Word)
  deriving Repr

def Request.Valid : Request → Prop
  | .add _ _ | .multiply _ _ => True
  | .quotient _ b | .remainder _ b => 0<value b
  | .modularMultiply _ _ m => 0<value m

def Request.width : Request → Nat
  | .add a b | .multiply a b | .quotient a b | .remainder a b => max a.length b.length
  | .modularMultiply a b m => max (max a.length b.length) m.length

def Request.evaluate : Request → BitEval Word
  | .add a b => addEval a b false
  | .multiply a b => mulEval a b
  | .quotient a b => let z:=divEval a b; (z.1.1,z.2)
  | .remainder a b => let z:=divEval a b; (z.1.2,z.2)
  | .modularMultiply a b m => residueMulEval a b m

def Request.spec : Request → Nat
  | .add a b => value a+value b
  | .multiply a b => value a*value b
  | .quotient a b => value a/value b
  | .remainder a b => value a%value b
  | .modularMultiply a b m => (value a*value b)%value m

theorem Request.correct (request : Request) (h : request.Valid) :
    value request.evaluate.1=request.spec := by
  cases request with
  | add a b => simp [Request.evaluate,Request.spec]
  | multiply a b => simp [Request.evaluate,Request.spec]
  | quotient a b => exact (divEval_semantics a b h).1
  | remainder a b => exact (divEval_semantics a b h).2
  | modularMultiply a b m => exact residueMulEval_value a b m h

theorem Request.cost_bound (request : Request) (B : Nat) (h : request.width≤B) :
    request.evaluate.2≤residueBudget B := by
  cases request with
  | add a b =>
    simp only [Request.width,max_le_iff] at h
    simp only [Request.evaluate,addEval_cost]
    have hm : max a.length b.length≤B := max_le h.1 h.2
    dsimp [residueBudget]; nlinarith
  | multiply a b =>
    simp only [Request.width,max_le_iff] at h
    have hc := mulEval_budget a b B h.1 h.2
    dsimp [Request.evaluate,residueBudget,primitiveBudget] at *
    nlinarith
  | quotient a b =>
    simp only [Request.width,max_le_iff] at h
    have hc := divEval_budget a b B h.1 h.2
    dsimp [Request.evaluate,residueBudget,primitiveBudget] at *
    nlinarith
  | remainder a b =>
    simp only [Request.width,max_le_iff] at h
    have hc := divEval_budget a b B h.1 h.2
    dsimp [Request.evaluate,residueBudget,primitiveBudget] at *
    nlinarith
  | modularMultiply a b m =>
    simp only [Request.width,max_le_iff] at h
    exact residueMulEval_budget a b m B h.1.1 h.1.2 h.2

/-- The trace explicitly records bit words. It is NOT inferred from a scalar unit total. -/
def evaluateTrace : List Request → List Word × Nat
  | [] => ([],0)
  | t::ts =>
    let a:=t.evaluate
    let tail:=evaluateTrace ts
    (a.1::tail.1,a.2+tail.2)

theorem evaluateTrace_correct (ts : List Request) (h : ∀t∈ts,t.Valid) :
    (evaluateTrace ts).1.map value = ts.map Request.spec := by
  induction ts with
  | nil => rfl
  | cons t ts ih =>
    have ht:=Request.correct t (h t (by simp))
    have hs:=ih (fun s hs => h s (List.mem_cons_of_mem t hs))
    simp only [evaluateTrace,List.map_cons,ht,hs]

theorem evaluateTrace_cost (ts : List Request) (B : Nat) (h : ∀t∈ts,t.width≤B) :
    (evaluateTrace ts).2≤ts.length*residueBudget B := by
  induction ts with
  | nil => simp [evaluateTrace]
  | cons t ts ih =>
    have ht:=Request.cost_bound t B (h t (by simp))
    have hs:=ih (fun s hs => h s (List.mem_cons_of_mem t hs))
    simp only [evaluateTrace,List.length_cons]
    nlinarith

/-- This conditional lifting theorem exposes its two premises. A source program
must still prove its trace-length and operand-width bounds; the theorem does not
manufacture that implementation refinement from the old unit counter. -/
theorem evaluateTrace_budget (ts : List Request) (B A : Nat)
    (hl : ts.length≤A) (hw : ∀t∈ts,t.width≤B) :
    (evaluateTrace ts).2≤A*(256*(B+1)^2) := by
  have hc:=evaluateTrace_cost ts B hw
  exact le_trans hc (Nat.mul_le_mul_right (residueBudget B) hl)

end Komorebi.Binary
