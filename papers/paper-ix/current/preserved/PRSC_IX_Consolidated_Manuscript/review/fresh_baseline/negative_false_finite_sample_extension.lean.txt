module
public import MahlerExamples
example : KomorebiPaperIX.Mahler.difference 1 1 (fun n : ℕ => (n:ℤ)) 0 =
 KomorebiPaperIX.Mahler.difference 1 1
 (KomorebiPaperIX.Mahler.interpolant 0 (KomorebiPaperIX.Mahler.coefficient (fun n : ℕ => (n:ℤ)))) 0 := by
 norm_num [KomorebiPaperIX.Mahler.interpolant, KomorebiPaperIX.Mahler.coefficient]
