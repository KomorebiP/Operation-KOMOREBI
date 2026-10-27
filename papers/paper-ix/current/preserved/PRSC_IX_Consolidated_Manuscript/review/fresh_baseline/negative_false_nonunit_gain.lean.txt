module
public import MahlerExamples
example : (3:ℤ) ∣ KomorebiPaperIX.Mahler.difference 2 1 (fun n : ℕ => (3:ℤ)^n) 0 := by
 norm_num
