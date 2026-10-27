import AVOC.RecorderPolicy
open Komorebi.AVOC
-- Identity false has its report, but identity true has an unresolved intent.
example : RecorderPolicy.gatedCounts (fun _ : Unit => 1) (fun _ : Unit => false)
    (fun _ : Unit => fun _ : Bool => [true])
    (fun _ : Unit => [.begin 0 false, .report 0 false, .begin 1 true]) () () =
      some ⟨1, by decide⟩ := by decide
