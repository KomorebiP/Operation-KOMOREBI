module
public import ExactTreeCompiler
import all ExactTreeCompiler
public import TreeCompilerUpdates
import all TreeCompilerUpdates

/-!
Executable regression suite, not additional manuscript theorems.
Independent exhaustive enumeration is compared to the verified recurrence,
returned pruning, and cached update on deterministic exact-rational examples.
-/
public section
set_option autoImplicit false
set_option maxRecDepth 8192
set_option maxHeartbeats 4000000
namespace CompilerExecution
open KomorebiPaperVIII CandidateTree

def binaryTree : ℕ → ℕ → CandidateTree ℕ
  | 0, label => .leaf label
  | depth + 1, label => .node label 1
      (fun i => binaryTree depth (2 * label + 1 + i.val))

def allTotals : List (List ℚ) → List ℚ
  | [] => [0]
  | choices :: rest => choices.flatMap (fun c => (allTotals rest).map (fun s => c + s))

def exhaustiveScores (keep overhead : ℕ → ℚ) : CandidateTree ℕ → List ℚ
  | .leaf a => [keep a]
  | .node a _ children => keep a ::
      (allTotals (List.ofFn (fun i => exhaustiveScores keep overhead (children i)))).map
        (fun x => overhead a + x)

def run : IO Unit := do
  let mut cases : ℕ := 0
  let mut enumerated : ℕ := 0
  let mut updates : ℕ := 0
  for seed in List.range 40 do
    for lam in ([0, 1/2, 3] : List ℚ) do
      let cost : ℕ → ℚ := fun a => ((seed * 17 + a * 11 + 3) % 29 : ℕ)
      let err : ℕ → ℚ := fun a => ((seed * 7 + a * 5) % 13 : ℕ)
      let overhead : ℕ → ℚ := fun a => ((seed + a) % 4 : ℕ)
      let keep := fun a => cost a + lam * err a
      for depth in List.range 5 do
        let t := binaryTree depth 0
        let vals := exhaustiveScores keep overhead t
        let actual := optimalValue keep overhead t
        if !(vals.all (fun v => decide (actual ≤ v))) || !(vals.contains actual) then
          throw (IO.userError s!"FAIL recurrence at seed {seed}, depth {depth}")
        let result := compile keep overhead t
        if cutValue keep overhead result != actual then
          throw (IO.userError s!"FAIL returned cut at seed {seed}, depth {depth}")
        let siblings := fun i : Fin 2 => binaryTree 2 (1 + i.val)
        let ctx : CachedContext ℕ ℚ := .frame 0 1 siblings 0
          (fun i => optimalValue keep overhead (siblings i)) .hole
        let newTree := binaryTree depth (seed + 200)
        let incremental := CachedContext.updateValue keep overhead ctx
          (optimalValue keep overhead newTree)
        let full := optimalValue keep overhead (CachedContext.fill ctx newTree)
        if incremental != full then
          throw (IO.userError s!"FAIL cached update at seed {seed}, depth {depth}")
        cases := cases + 1
        enumerated := enumerated + vals.length
        updates := updates + 1
  IO.println s!"PASS exact-rational compiler cases: {cases}"
  IO.println s!"PASS exhaustively enumerated pruning scores: {enumerated}"
  IO.println s!"PASS cached updates versus full recomputation: {updates}"

end CompilerExecution
#eval CompilerExecution.run
