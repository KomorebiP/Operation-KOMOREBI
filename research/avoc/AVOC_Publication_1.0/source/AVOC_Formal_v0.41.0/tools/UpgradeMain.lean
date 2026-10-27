import AVOC.UpgradeRuntime
open Lean

def main (args : List String) : IO UInt32 := do
  let (batch, path) ← match args with
    | [p] => pure (false, p)
    | ["--batch", p] => pure (true, p)
    | _ => IO.eprintln "usage: UpgradeMain [--batch] request.json" *> pure (false, "")
  if path.isEmpty then return 2
  let raw ← IO.FS.readFile path
  if raw.utf8ByteSize > (if batch then 8388608 else 262144) then
    IO.eprintln "input size limit"; return 2
  match Json.parse raw with
  | .error e => IO.eprintln e; return 2
  | .ok wire =>
    if batch then
      match wire.getArr? with
      | .error e => IO.eprintln e; return 2
      | .ok ws =>
        if ws.size > 2000 then IO.eprintln "batch size limit"; return 2
        for w in ws do
          let result := match Komorebi.AVOC.UpgradeRuntime.execute w with
            | .ok x => x
            | .error e => Json.mkObj [("status", .str "error"), ("error", .str e)]
          IO.println result.compress
        return 0
    else
      match Komorebi.AVOC.UpgradeRuntime.execute wire with
      | .error e => IO.eprintln e; return 2
      | .ok result => IO.println result.compress; return 0
