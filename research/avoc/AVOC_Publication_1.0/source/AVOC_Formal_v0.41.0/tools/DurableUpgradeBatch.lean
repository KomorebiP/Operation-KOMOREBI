import AVOC.DurableUpgradeRuntime
import Lean

open Lean

def main : IO UInt32 := do
  let input ← (← IO.getStdin).readToEnd
  let output ← IO.getStdout
  match Json.parse input with
  | .error e => output.putStrLn e; return 2
  | .ok j =>
    match j.getArr? with
    | .error e => output.putStrLn e; return 2
    | .ok items =>
      let answers := items.map fun x =>
        match Komorebi.AVOC.DurableUpgradeRuntime.execute x with
        | .error msg => Json.mkObj [("status", .str "error"), ("error", .str msg)]
        | .ok result => result
      output.putStrLn (Json.arr answers).compress
      return 0
