import AVOC.LazyStagedCodec
open Lean

def main (args : List String) : IO UInt32 := do
  let path ← match args with
    | [p] => pure p
    | _ => IO.eprintln "usage: LazyStagedMain request.json" *> pure ""
  if path.isEmpty then return 2
  let text ← IO.FS.readFile path
  if text.utf8ByteSize > 4194304 then IO.eprintln "input byte cap"; return 2
  let request ← match Json.parse text with
    | .error e => IO.eprintln e *> pure Json.null
    | .ok j => pure j
  let result := match Komorebi.AVOC.Affine.LazyStagedCodec.process request with
    | .ok value => value
    | .error e => Json.mkObj [("status",.str "error"),("error",.str e)]
  IO.println result.compress
  return if (result.getObjValAs? String "status").toOption == some "error" then 2 else 0
