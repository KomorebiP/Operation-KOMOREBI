import KomorebiPaperIV
example (f : PowerSeries Nat) :
    Komorebi.PaperIV.cyclicProjector 3 1 (Komorebi.PaperIV.cyclicProjector 3 1 f) =
    Komorebi.PaperIV.cyclicProjector 3 1 f :=
  Komorebi.PaperIV.cyclicProjector_idempotent 3 1 f
#print axioms Komorebi.PaperIV.cyclicProjector_idempotent
#print axioms Komorebi.PaperIV.cyclicAlgebra_pointwise_exponential
run_cmd Lean.logInfo "PAPER_IV_EXTRACTED_IMPORT_PASS"
