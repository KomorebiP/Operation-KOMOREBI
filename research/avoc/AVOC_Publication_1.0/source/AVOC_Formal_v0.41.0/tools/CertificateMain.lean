import AVOC.BindingCodec

/-- Trusted entry point. Untrusted inputs are JSON data, never Lean source. -/
def main (args : List String) : IO UInt32 := do
  let [path] := args | do
    IO.eprintln "usage: CertificateMain request.json"
    return 2
  let input ← IO.FS.readFile path
  if input.utf8ByteSize > 1048576 then
    IO.eprintln "input byte limit exceeded"
    return 2
  let result := do
    let j ← Lean.Json.parse input
    let a ← j.getArr?
    if a.size = 4 then
      Komorebi.AVOC.Binding.checkBoundJson j
    else
      Komorebi.AVOC.Certificate.checkJson j
  match result with
  | .error e =>
      IO.eprintln e
      return 2
  | .ok false =>
      IO.println "{\"accepted\":false}"
      return 1
  | .ok true =>
      IO.println "{\"accepted\":true}"
      return 0
