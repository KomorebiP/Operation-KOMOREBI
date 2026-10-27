import ProofPath.TraceWire
import Lean.Data.Json.Parser
import Lean.Data.Json.Printer

/-!
IO adapter for canonical NDJSON pairs [problem, certificate]. The proved part
is Wire.acceptJson on Json syntax trees. This adapter and the standard text
parser/printer are executed and cross-checked, not added as axioms or presented
as a proof of arbitrary file-system/byte-level behavior.
-/
open Lean ProofPath.Trace ProofPath.Trace.Wire

def inspectPair (line : String) : String :=
  match Json.parse line with
  | .error _ => "REJECT_FORMAT"
  | .ok j =>
    match j with
    | .arr a =>
      match a.toList with
      | [jp, jc] =>
        match decodeProblem jp, decodeCertificate jc with
        | some p, some c =>
          if line != (Json.arr #[encodeProblem p, encodeCertificate c]).compress then
            "REJECT_NONCANONICAL"
          else if !problemValid p then "REJECT_PROBLEM"
          else if !certificateValid p c then "REJECT_CERTIFICATE_SHAPE"
          else if acceptJson jp jc then
            if c.feasible then "ACCEPT_POSITIVE" else "ACCEPT_NEGATIVE"
          else "REJECT_CERTIFICATE"
        | _, _ => "REJECT_FORMAT"
      | _ => "REJECT_FORMAT"
    | _ => "REJECT_FORMAT"

def main (args : List String) : IO UInt32 := do
  match args with
  | [path] =>
    let text ← IO.FS.readFile path
    for line in text.splitOn "\n" do
      if !line.isEmpty then
        if line.utf8ByteSize > 8388608 then
          IO.println "RESOURCE_LIMIT"
        else
          IO.println (inspectPair line)
    return 0
  | _ =>
    IO.eprintln "Usage: lean --run CheckTraceJson.lean canonical_pairs.ndjson"
    return 2
