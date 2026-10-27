module
public import StoredBudgetCompiler
import all StoredBudgetCompiler
import all QuantizedTreeCompiler
import all DiscretePrecision
import all BudgetConvolution
import all ExactTreeCompiler

/-!
Executable exact-rational tests, not additional kernel-checked declarations.
The oracle enumerates every legal pruning or precision assignment and then
filters the resulting weight/cost pairs. It never calls a DP recurrence.
-/
public section
set_option autoImplicit false
set_option maxRecDepth 8192
set_option maxHeartbeats 8000000
namespace BudgetExecution
open KomorebiPaperVIII CandidateTree BudgetDP

abbrev Point := ℕ × ℚ

def sumChoices : List (List Point) → List Point
  | [] => [(0, 0)]
  | choices :: rest => choices.flatMap (fun x => (sumChoices rest).map
      (fun y => (x.1 + y.1, x.2 + y.2)))

def enumCuts (cost : ℕ → ℚ) (weight : ℕ → ℕ) (overhead : ℕ → ℚ) :
    CandidateTree ℕ → List Point
  | .leaf a => [(weight a, cost a)]
  | .node a _ ts => (weight a, cost a) ::
      (sumChoices (List.ofFn (fun i => enumCuts cost weight overhead (ts i)))).map
        (fun y => (y.1, overhead a + y.2))

def oracle (xs : List Point) (allow : ℕ → Bool) : Option ℚ :=
  xs.foldl (fun acc x => if allow x.1 then
      match acc with
      | none => some x.2
      | some a => some (min a x.2)
    else acc) none

def testTree (mode : ℕ) : ℕ → ℕ → CandidateTree ℕ
  | 0, a => .leaf a
  | d + 1, a => .node a (if mode < 3 then mode else a % 3)
      (fun i => testTree mode d (4 * a + 1 + i.val))

def options (seed edges : ℕ) : List (List Point) :=
  (List.range edges).map (fun e =>
    if (seed + e) % 11 = 0 then [] else
    (List.range (1 + (seed + e) % 3)).map (fun o =>
      ((seed * 3 + e + o * 5) % 8,
       (((seed * 7 + e * 11 + o * 13) % 31 : ℕ) : ℚ) / ((o + 1 : ℕ) : ℚ))))

def run : IO Unit := do
  let maxBudget := 12
  let mut trees : ℕ := 0
  let mut exactTree : ℕ := 0
  let mut budgetTree : ℕ := 0
  let mut enumTree : ℕ := 0
  let mut specificationChecks : ℕ := 0
  for seed in List.range 24 do
    let cost : ℕ → ℚ := fun a => (((seed * 17 + a * 11 + 3) % 29 : ℕ) : ℚ) /
      (((seed + a) % 3 + 1 : ℕ) : ℚ)
    let weight : ℕ → ℕ := fun a => (seed * 7 + a * 5) % 9
    let overhead : ℕ → ℚ := fun a => (((seed + a) % 4 : ℕ) : ℚ) / 2
    for mode in List.range 4 do
      for depth in List.range 4 do
        let t := testTree mode depth 0
        let vals := enumCuts cost weight overhead t
        let table := storedTree maxBudget cost weight overhead t
        for b in List.range (maxBudget + 1) do
          let ex := oracle vals (fun w => w == b)
          let bd := oracle vals (fun w => w ≤ b)
          if lookup table b != ex then
            throw (IO.userError s!"FAIL tree exact seed={seed} mode={mode} depth={depth} b={b}")
          if withinBudget (lookup table) b != bd then
            throw (IO.userError s!"FAIL tree budget seed={seed} mode={mode} depth={depth} b={b}")
          if depth ≤ 2 && b ≤ 4 then
            if budgetTable cost weight overhead t b != ex then
              throw (IO.userError "FAIL tree specification")
            specificationChecks := specificationChecks + 1
          exactTree := exactTree + 1
          budgetTree := budgetTree + 1
        if storedBudget maxBudget cost weight overhead t != oracle vals (fun w => w ≤ maxBudget) then
          throw (IO.userError "FAIL stored root wrapper")
        enumTree := enumTree + vals.length
        trees := trees + 1
  let mut assignments : ℕ := 0
  let mut exactDiscrete : ℕ := 0
  let mut budgetDiscrete : ℕ := 0
  let mut enumDiscrete : ℕ := 0
  for seed in List.range 48 do
    for edgeCount in List.range 6 do
      let es := options seed edgeCount
      let vals := sumChoices es
      let table := storedDiscrete maxBudget es
      for b in List.range (maxBudget + 1) do
        let ex := oracle vals (fun w => w == b)
        let bd := oracle vals (fun w => w ≤ b)
        if lookup table b != ex || discreteTable es b != ex then
          throw (IO.userError s!"FAIL discrete exact seed={seed} edges={edgeCount} b={b}")
        if withinBudget (lookup table) b != bd then
          throw (IO.userError "FAIL discrete budget")
        exactDiscrete := exactDiscrete + 1
        budgetDiscrete := budgetDiscrete + 1
      if storedDiscreteBudget maxBudget es != oracle vals (fun w => w ≤ maxBudget) then
        throw (IO.userError "FAIL discrete wrapper")
      enumDiscrete := enumDiscrete + vals.length
      assignments := assignments + 1
  -- Strict guards and degenerate inputs.
  if storedDiscreteBudget 0 [[(1, (0 : ℚ))]] != none then
    throw (IO.userError "FAIL natural-subtraction underflow guard")
  if storedDiscreteBudget 0 [[(0, (3 : ℚ))]] != some 3 then
    throw (IO.userError "FAIL zero-weight option")
  if storedDiscreteBudget 4 ([[]] : List (List Point)) != none then
    throw (IO.userError "FAIL empty option set")
  if storedDiscreteBudget 0 ([] : List (List Point)) != some 0 then
    throw (IO.userError "FAIL empty assignment")
  -- The Pareto point (cost,error)=(3,2) is unsupported by scalarization,
  -- but is the exact constrained answer at budget 2.
  let t : CandidateTree ℕ := .node 0 0 (fun _ => .node 1 0 (fun _ => .leaf 2))
  let κ : ℕ → ℚ := fun a => if a = 0 then 0 else if a = 1 then 3 else 4
  let w : ℕ → ℕ := fun a => if a = 0 then 4 else if a = 1 then 2 else 0
  if storedBudget 2 κ w (fun _ => 0) t != some 3 then
    throw (IO.userError "FAIL unsupported Pareto point")
  IO.println s!"PASS tree instances: {trees}"
  IO.println s!"PASS tree exact-weight comparisons: {exactTree}"
  IO.println s!"PASS tree budget comparisons: {budgetTree}"
  IO.println s!"PASS independently enumerated tree cuts: {enumTree}"
  IO.println s!"PASS tree specification comparisons: {specificationChecks}"
  IO.println s!"PASS precision instances: {assignments}"
  IO.println s!"PASS precision exact-weight comparisons: {exactDiscrete}"
  IO.println s!"PASS precision budget comparisons: {budgetDiscrete}"
  IO.println s!"PASS independently enumerated assignments: {enumDiscrete}"
  IO.println "PASS boundary regressions: 5"
end BudgetExecution
#eval BudgetExecution.run
