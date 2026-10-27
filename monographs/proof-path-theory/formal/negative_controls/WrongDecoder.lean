import ProofPath.Recovery
-- The proposed decoder forgets the Boolean answer and is wrong at true.
example : (fun _ : Unit => false) () = true := by decide
