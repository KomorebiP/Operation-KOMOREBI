import AVOC.SemanticLibraryCodec
open Lean

def main (args : List String) : IO UInt32 := do
  let (batch,path) ← match args with
    | [p] => pure (false,p)
    | ["--batch",p] => pure (true,p)
    | _ => IO.eprintln "usage: SemanticLibraryMain [--batch] request.json" *> pure (false,"")
  if path.isEmpty then return 2
  let text ← IO.FS.readFile path
  if text.utf8ByteSize > 33554432 then IO.eprintln "input byte cap"; return 2
  let j ← match Json.parse text with
    | .error e => IO.eprintln e *> pure Json.null
    | .ok j => pure j
  let reply (q : Json) : Json := match Komorebi.AVOC.LibraryCodec.execute q with
    | .ok value => value
    | .error e => Json.mkObj [("status",.str "error"),("error",.str e)]
  if batch then
    match j.getArr? with
    | .error e => IO.eprintln e; return 2
    | .ok qs =>
      if qs.size > 128 then IO.eprintln "batch size cap"; return 2
      for q in qs do IO.println (reply q).compress
      return 0
  else
    let result := reply j
    IO.println result.compress
    return match result.getObjValAs? String "status" with
      | .ok "globally_certified" => 0
      | .ok "unfunded" => 0
      | _ => 2
