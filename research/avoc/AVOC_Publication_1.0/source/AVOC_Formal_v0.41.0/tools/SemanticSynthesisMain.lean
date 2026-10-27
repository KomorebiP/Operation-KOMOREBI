import AVOC.SemanticSynthesisRuntime
open Lean

def main (args : List String) : IO UInt32 := do
  let (batch,path) ← match args with
    | [p] => pure (false,p)
    | ["--batch",p] => pure (true,p)
    | _ => IO.eprintln "usage: SemanticSynthesisMain [--batch] request.json" *> pure (false,"")
  if path.isEmpty then return 2
  let raw ← IO.FS.readFile path
  if raw.utf8ByteSize > 8388608 then IO.eprintln "input size cap"; return 2
  match Json.parse raw with
  | .error e => IO.eprintln e; return 2
  | .ok j =>
    let reply (w : Json) : Json := match Komorebi.AVOC.SemanticSynthesisRuntime.execute w with
      | .ok out => out
      | .error e => Json.mkObj [("status",.str "error"),("error",.str e)]
    if batch then
      match j.getArr? with
      | .error e => IO.eprintln e; return 2
      | .ok ws =>
        if ws.size > 1000 then IO.eprintln "batch cap"; return 2
        for w in ws do IO.println (reply w).compress
        return 0
    else
      let r := reply j
      IO.println r.compress
      return match r.getObjValAs? String "status" with
        | .ok "checked" => 0
        | .ok "unfunded" => 0
        | .ok "query_unfunded" => 0
        | _ => 2
