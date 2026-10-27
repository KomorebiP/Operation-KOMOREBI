import AVOC.BindingCodec

/-- Differential-test driver. Production admission uses CertificateMain.lean. -/
def main (args : List String) : IO UInt32 := do
  let [path] := args | return 2
  let text ← IO.FS.readFile path
  if text.utf8ByteSize > 1048576 then return 2
  let result : Except String (List Bool) := do
    let j ← Lean.Json.parse text
    let arr ← j.getArr?
    arr.toList.mapM fun (q : Lean.Json) => do
      let a ← q.getArr?
      if a.size = 4 then
        Komorebi.AVOC.Binding.checkBoundJson q
      else
        Komorebi.AVOC.Certificate.checkJson q
  match result with
  | .error e => IO.eprintln e; return 2
  | .ok bs =>
      IO.println ("[" ++ String.intercalate "," (bs.map fun b => if b then "true" else "false") ++ "]")
      return 0
