import KomorebiReader.FactorialLanes

namespace Komorebi.Reader.FactorialControls

open Komorebi.Reader.FactorialLanes

theorem displayed_thirty_four_factorial :
    24 * laneProduct 10 4 3 = 295232799039604140847618609643520000000 := by
  decide

theorem empty_lanes (j n : ℕ) : Nat.factorial j * laneProduct 0 j n = Nat.factorial j := by
  simpa using factorial_lane_reconstruction 0 j n

theorem displayed_normalization :
    (Nat.factorial 4 : ℚ) * (Nat.factorial 20 : ℚ) / (Nat.factorial 24 : ℚ) =
      1 / 10626 := by
  norm_num [Nat.factorial]

theorem displayed_diagonal_bridge :
    (Nat.choose 24 10 : ℚ) / (Nat.choose 24 4 : ℚ) =
      (Nat.choose 20 10 : ℚ) / (Nat.choose 14 4 : ℚ) :=
  binomial_diagonal_bridge 20 10 4 (by decide)

end Komorebi.Reader.FactorialControls
