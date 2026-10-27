import KomorebiLSM.ProposalError

open Komorebi.LSM.ProposalError

-- For A=I, the nonsingular-inverse convention returns zero, not a solution of 0c=1.
example : Matrix.toEuclideanCLM (𝕜 := ℝ)
    ((1 : Matrix Unit Unit ℝ) - 1)
    (fixedCenter (1 : Matrix Unit Unit ℝ) (fun _ => 1)) =
      WithLp.toLp 2 (fun _ : Unit => (1 : ℝ)) := by
  ext i
  norm_num [fixedCenter]
