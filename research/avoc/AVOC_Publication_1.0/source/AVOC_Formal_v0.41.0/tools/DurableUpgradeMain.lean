import AVOC.DurableUpgradeRuntime
import Lean

open Lean

def main (args : List String) : IO UInt32 := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  let text ← match args with
    | [path] => IO.FS.readFile path
    | _ => stdin.readToEnd
  match Json.parse text with
  | .error e =>
    stdout.putStrLn ((Json.mkObj [("status", .str "error"), ("error", .str e)]).compress)
    return 2
  | .ok j =>
    match Komorebi.AVOC.DurableUpgradeRuntime.execute j with
    | .error e =>
      stdout.putStrLn ((Json.mkObj [("status", .str "error"), ("error", .str e)]).compress)
      return 2
    | .ok result =>
      stdout.putStrLn result.compress
      return 0
