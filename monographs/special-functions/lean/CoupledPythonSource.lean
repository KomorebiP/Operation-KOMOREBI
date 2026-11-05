import CoupledEvaluationResult

/-! Source-bound imperative translation. Regenerate with bind_python_source.py.
Exact arithmetic and standard-library primitives are interpreted mathematically.
The Python parser/translation boundary is separately recorded, not a Lean axiom. -/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales.Python

abbrev Arrays := List ℚ × List ℚ
abbrev Product := ℚ × ℕ × ℕ

def products (n : ℕ) (uv : Arrays) : List Product :=
  List.ofFn (fun i : Fin n =>
    ((((((2*n)).choose ((2*i.val)+1) : ℚ)*(uv.1[i.val]?).getD 0)*(uv.2[((n-1)-i.val)]?).getD 0), ((2*i.val)+1), ((2*((n-1)-i.val))+1)))

def weighted (q r : ℚ) (terms : List Product) : ℚ :=
  (terms.map (fun t => ((t.1*(q^t.2.1))*(r^t.2.2)))).sum

def appendRows (p : RationalScales) (n : ℕ) (uv : Arrays) : Arrays :=
  let terms := products n uv
  let u := uv.1 ++ [weighted p.q p.r terms]
  let v := uv.2 ++ [weighted p.a p.b terms]
  (u,v)

def derivativeFor (p : RationalScales) (N : ℕ) : Arrays :=
  (List.range N).foldl (fun uv k => appendRows p (k+1) uv) ([1],[1])

def ordinary (row : List ℚ) : List ℚ :=
  row.mapIdx (fun n a => (a/((((2*n)+1)).factorial : ℚ)))

def partialSum (row : List ℚ) (x : ℚ) : ℚ :=
  ((ordinary row).mapIdx (fun n c => (c*(x^((2*n)+1))))).sum

def seed (x : ℚ) : ℚ := (x/(1-(x*x)))
def update (x bound : ℚ) : ℚ := (x*(1+(bound*bound)))

/-- Operational semantics of the source while loop, including the pre-append
length guard. The accumulator is stored in original, not reversed, order. -/
inductive LadderRun (Q : ℚ) (budget : ℕ) :
    List ℚ → ℚ → Except MajorantError (List ℚ × ℚ) → Prop where
  | stop (xs : List ℚ) (x : ℚ) (small : x < 1) : LadderRun Q budget xs x (.ok (xs,x))
  | exhausted (xs : List ℚ) (x : ℚ) (large : 1 ≤ x) (full : budget ≤ xs.length) :
      LadderRun Q budget xs x (.error .steps)
  | step (xs : List ℚ) (x : ℚ) (out : Except MajorantError (List ℚ × ℚ))
      (large : 1 ≤ x) (room : xs.length < budget)
      (child : LadderRun Q budget (xs++[x]) (x*Q) out) : LadderRun Q budget xs x out

/-- Source for-loop order: consume reversed(ladder), checking every update. -/
def foldFor (bits : ℕ) : List ℚ → ℚ → Except MajorantError ℚ
  | [], bound => .ok bound
  | x::xs, bound =>
      let next := update x bound
      if bits < rationalBitSize next then .error .bits else foldFor bits xs next

def finishMajorant (bits : ℕ) : Except MajorantError (List ℚ × ℚ) → Except MajorantError ℚ
  | .error e => .error e
  | .ok (xs,x) => foldFor bits xs.reverse (seed x)

inductive MajorantRun (p : RationalScales) (R : ℚ) (steps bits : ℕ) :
    Except CheckedMajorantError ℚ → Prop where
  | scales (bad : ¬p.strictRational) : MajorantRun p R steps bits (.error .scales)
  | radius (valid : p.strictRational) (negative : R < 0) :
      MajorantRun p R steps bits (.error .radius)
  | zero (valid : p.strictRational) (origin : R = 0) : MajorantRun p R steps bits (.ok 0)
  | bitsInvalid (valid : p.strictRational) (positive : 0 < R) (invalid : bits = 0) :
      MajorantRun p R steps bits (.error .bitsInput)
  | positive (valid : p.strictRational) (positive : 0 < R) (positiveBits : 0 < bits)
      (out : Except MajorantError (List ℚ × ℚ)) (trace : LadderRun p.maxScale steps [] R out) :
      MajorantRun p R steps bits
        (match finishMajorant bits out with
         | .ok B => .ok B
         | .error e => .error (.resource e))

inductive Value where
  | rational (q : ℚ)
  | integer (z : ℤ)
  | tuple (a b : Value)
  deriving DecidableEq, Repr

abbrev Dictionary := List (String × Value)

/-- Exact type tags for _index; bool and int subclasses belong to distinct tags. -/
inductive IndexValue where
  | integer (z : ℤ)
  | boolean (b : Bool)
  | other
  deriving DecidableEq, Repr

def classifyIndex : IndexValue → Option ℕ
  | .integer z => if z < 0 then none else some z.toNat
  | .boolean _ => none
  | .other => none

def defaultSteps : ℕ := 20
def defaultBits : ℕ := 2000000
def defaultLast : ℕ := 24
def outerRadius (x : ℚ) (s : Option ℚ) : ℚ := s.getD (max 1 (2*x))
def tail (B x s : ℚ) (N : ℕ) : ℚ := (B*((x/s)^((2*N)+3)))

def resultDictionary (x : ℚ) (N : ℕ) (s B : ℚ) (u v : ℚ) : Dictionary :=
  let t := tail B x s N
  [("x", .rational x),
   ("last_index", .integer (N : ℤ)),
   ("outer_radius", .rational s),
   ("majorant", .rational B),
   ("tail_bound", .rational t),
   ("U", .tuple (.rational u) (.rational (u+t))),
   ("V", .tuple (.rational v) (.rational (v+t)))]

/-- Post-conversion execution. Arrays and partials occur before the majorant
call, as in the source; a resource exception has no result dictionary. -/
inductive EvaluationRun (p : RationalScales) (x : ℚ) (last : Option ℕ) (outer : Option ℚ) :
    Except EvaluationError Dictionary → Prop where
  | lastInvalid (invalid : last = none) : EvaluationRun p x last outer (.error .lastInput)
  | scales (N : ℕ) (index : last = some N) (bad : ¬p.strictRational) :
      EvaluationRun p x last outer (.error .scales)
  | negative (N : ℕ) (index : last = some N) (valid : p.strictRational) (negative : x < 0) :
      EvaluationRun p x last outer (.error .negativeX)
  | outerInvalid (N : ℕ) (index : last = some N) (valid : p.strictRational)
      (nonneg : 0 ≤ x) (bad : outerRadius x outer ≤ x) :
      EvaluationRun p x last outer (.error .outerRadius)
  | evaluated (N : ℕ) (index : last = some N) (valid : p.strictRational)
      (nonneg : 0 ≤ x) (strictOuter : x < outerRadius x outer)
      (uv : Arrays) (arrays : derivativeFor p N = uv)
      (u v : ℚ) (first : partialSum uv.1 x = u) (second : partialSum uv.2 x = v)
      (out : Except CheckedMajorantError ℚ)
      (majorant : MajorantRun p (outerRadius x outer) defaultSteps defaultBits out) :
      EvaluationRun p x last outer
        (match out with
         | .error e => .error (.majorant e)
         | .ok B => .ok (resultDictionary x N (outerRadius x outer) B u v))

inductive RawError (ε : Type) where
  | conversion (e : ε)
  | validation (e : EvaluationError)

structure Prepared where
  p : RationalScales
  x : ℚ
  N : ℕ
  S : ℚ

/-- Conversion is an explicit primitive parameter. Its failure object is
propagated, and every early guard prevents subsequent conversions. -/
def prepare {α ε : Type} (convert : α → Except ε ℚ) (index : IndexValue)
    (q r a b x : α) (outer : Option α) : Except (RawError ε) Prepared := do
  let N ← match classifyIndex index with
    | none => .error (.validation .lastInput)
    | some n => .ok n
  let q' ← (convert q).mapError RawError.conversion
  let r' ← (convert r).mapError RawError.conversion
  let a' ← (convert a).mapError RawError.conversion
  let b' ← (convert b).mapError RawError.conversion
  let p : RationalScales := ⟨q',r',a',b'⟩
  if ¬p.strictRational then .error (.validation .scales) else do
  let x' ← (convert x).mapError RawError.conversion
  if x' < 0 then .error (.validation .negativeX) else do
  let S ← match outer with
    | none => .ok (outerRadius x' none)
    | some s => (convert s).mapError RawError.conversion
  if S ≤ x' then .error (.validation .outerRadius) else .ok ⟨p,x',N,S⟩

inductive RawEvaluationRun {α ε : Type} (convert : α → Except ε ℚ) (index : IndexValue)
    (q r a b x : α) (outer : Option α) : Except (RawError ε) Dictionary → Prop where
  | preparationError (e : RawError ε) (h : prepare convert index q r a b x outer = .error e) :
      RawEvaluationRun convert index q r a b x outer (.error e)
  | prepared (s : Prepared) (h : prepare convert index q r a b x outer = .ok s)
      (out : Except EvaluationError Dictionary)
      (execution : EvaluationRun s.p s.x (some s.N) (some s.S) out) :
      RawEvaluationRun convert index q r a b x outer (out.mapError RawError.validation)

end Komorebi.SpecialFunctions.Coupled.Scales.Python
