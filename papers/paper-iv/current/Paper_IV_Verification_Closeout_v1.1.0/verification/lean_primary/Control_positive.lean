import KomorebiPaperIV.CyclicFilters
example (f : PowerSeries Nat) : Komorebi.PaperIV.cyclicProjector 3 1 (Komorebi.PaperIV.cyclicProjector 3 1 f) = Komorebi.PaperIV.cyclicProjector 3 1 f := Komorebi.PaperIV.cyclicProjector_idempotent 3 1 f
run_cmd Lean.logInfo "PAPER_IV_POSITIVE_CONTROL_PASS"
