import AVOC.MultiLevelCodec
open Lean

def main (args : List String) : IO UInt32 := do
  let (batch,path) ← match args with
    | [p] => pure (false,p)
    | ["--batch",p] => pure (true,p)
    | _ => IO.eprintln "usage: MultiLevelMain [--batch] request.json" *> pure (false,"")
  if path.isEmpty then return 2
  let text ← IO.FS.readFile path
  if text.utf8ByteSize > 4194304 then IO.eprintln "input byte cap"; return 2
  let j ← match Json.parse text with
    | .error e => IO.eprintln e *> pure Json.null
    | .ok j => pure j
  let reply (q : Json) : Json :=
    match Komorebi.AVOC.Affine.MultiLevelCodec.process q with
    | .ok value => value
    | .error e => Json.mkObj [("status",.str "error"),("error",.str e)]
  if batch then
    match j.getArr? with
    | .error e => IO.eprintln e; return 2
    | .ok qs =>
      if qs.size > 256 then IO.eprintln "batch size cap"; return 2
      for q in qs do IO.println (reply q).compress
      return 0
  else
    let r := reply j
    IO.println r.compress
    return if (r.getObjValAs? String "status").toOption == some "error" then 2 else 0
