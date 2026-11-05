import CoupledPythonRefinement

/-! A typed expression interpreter, separate from the source-to-term printer.
Natural subtraction describes the reachable nonnegative index fragment; the
Python integer and subscript obligations are proved in CoupledPythonRefinement.
This does not give semantics to arbitrary Python objects or statements. -/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions

inductive NatExpr where
  | literal (n : ℕ)
  | variable (name : String)
  | add (a b : NatExpr)
  | sub (a b : NatExpr)
  | mul (a b : NatExpr)
  | pow (a b : NatExpr)
  deriving Repr

inductive RatExpr where
  | literal (n : ℕ)
  | variable (name : String)
  | add (a b : RatExpr)
  | sub (a b : RatExpr)
  | mul (a b : RatExpr)
  | div (a b : RatExpr)
  | pow (a : RatExpr) (n : NatExpr)
  | choose (n k : NatExpr)
  | factorial (n : NatExpr)
  | entry (name : String) (n : NatExpr)
  | maximum (a b : RatExpr)
  deriving Repr

inductive ValueExpr where
  | rational (r : RatExpr)
  | integer (n : NatExpr)
  | tuple (a b : ValueExpr)
  deriving Repr

structure Environment where
  natural : String → ℕ
  rational : String → ℚ
  array : String → List ℚ

def evalNat (e : Environment) : NatExpr → ℕ
  | .literal n => n
  | .variable s => e.natural s
  | .add a b => evalNat e a + evalNat e b
  | .sub a b => evalNat e a - evalNat e b
  | .mul a b => evalNat e a * evalNat e b
  | .pow a b => evalNat e a ^ evalNat e b

def evalRat (e : Environment) : RatExpr → ℚ
  | .literal n => (n : ℚ)
  | .variable s => e.rational s
  | .add a b => evalRat e a + evalRat e b
  | .sub a b => evalRat e a - evalRat e b
  | .mul a b => evalRat e a * evalRat e b
  | .div a b => evalRat e a / evalRat e b
  | .pow a n => evalRat e a ^ evalNat e n
  | .choose n k => ((evalNat e n).choose (evalNat e k) : ℚ)
  | .factorial n => ((evalNat e n).factorial : ℚ)
  | .entry s n => (e.array s)[evalNat e n]?.getD 0
  | .maximum a b => max (evalRat e a) (evalRat e b)

def evalValue (e : Environment) : ValueExpr → Value
  | .rational r => .rational (evalRat e r)
  | .integer n => .integer (evalNat e n : ℤ)
  | .tuple a b => .tuple (evalValue e a) (evalValue e b)

def evalDictionary (e : Environment) (xs : List (String × ValueExpr)) : Dictionary :=
  xs.map (fun kv => (kv.1, evalValue e kv.2))

def env (ns : List (String × ℕ) := []) (qs : List (String × ℚ) := [])
    (arrays : List (String × List ℚ) := []) : Environment :=
  { natural := fun s => ((ns.find? (fun kv => kv.1 == s)).map Prod.snd).getD 0,
    rational := fun s => ((qs.find? (fun kv => kv.1 == s)).map Prod.snd).getD 0,
    array := fun s => ((arrays.find? (fun kv => kv.1 == s)).map Prod.snd).getD [] }

end Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions
