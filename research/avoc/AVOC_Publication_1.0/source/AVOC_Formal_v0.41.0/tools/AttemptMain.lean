import AVOC.AttemptCodec
open Lean

def main (args : List String) : IO UInt32 := do
  match args with
  | [path] =>
      let raw ← IO.FS.readFile path
      if raw.utf8ByteSize > 65536 then IO.eprintln "attempt request too large"; return 2
      match Json.parse raw >>= Komorebi.AVOC.Attempts.execute with
      | .error e => IO.eprintln e; return 2
      | .ok result => IO.println result.compress; return 0
  | _ => IO.eprintln "usage: AttemptMain request.json"; return 2
