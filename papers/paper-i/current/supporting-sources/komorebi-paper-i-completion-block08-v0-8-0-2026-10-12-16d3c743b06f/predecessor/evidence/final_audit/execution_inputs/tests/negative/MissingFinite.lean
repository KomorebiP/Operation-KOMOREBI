import PaperICompletion7
set_option autoImplicit false
open Komorebi.SeedRankBasics Komorebi.PaperICompletion7.Nakayama
open Komorebi.PaperICompletion7.ModuleTop
example {R M : Type} [Ring R] [AddCommGroup M] [Module R M] (s : Set M) :
    Generates R M s ↔ Generates (R ⧸ Ring.jacobson R) (RadicalTop R M)
      (idealTopMap (Ring.jacobson R) '' s) := generates_iff_radicalTop s
