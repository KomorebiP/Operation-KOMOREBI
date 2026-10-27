import AVOC.RecorderPolicy
open Komorebi.AVOC
-- A valid early sample cannot license a batch with a later unknown completion.
example : RecorderPolicy.gatedCounts (fun _ : Unit => 1) (fun _ : Unit => ())
    (fun _ : Unit => fun _ : Unit => [true])
    (fun _ : Unit => [.begin 0 (), .report 0 (), .report 99 ()]) () () =
      some ⟨1, by decide⟩ := by decide
