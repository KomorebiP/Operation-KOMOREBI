import KomorebiPaperIIIStirling
open Komorebi.PaperIII.CompositionTermCount

theorem wrong_factorial : Fintype.card (DecoratedPartition 2 (Fin 2)) = 10 := by
  rw [card_decoratedPartition_two]; norm_num; decide
