import AVOC.AttemptCodec
open Lean

def main (args : List String) : IO UInt32 := do
  match args with
  | [path] =>
      let raw ← IO.FS.readFile path
      if raw.utf8ByteSize > 16777216 then IO.eprintln "batch too large"; return 2
      match Json.parse raw >>= Json.getArr? with
      | .error e => IO.eprintln e; return 2
      | .ok arr =>
          let out := arr.map fun x => match Komorebi.AVOC.Attempts.execute x with
            | .ok r => r
            | .error e => Json.mkObj [("status",.str "error"),("error",.str e)]
          IO.println (Json.arr out).compress
          return 0
  | _ => IO.eprintln "usage: AttemptBatch request.json"; return 2
