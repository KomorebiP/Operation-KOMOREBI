import KomorebiPaperIIIStirling
open Komorebi.PaperIII.CompositionTermCount

theorem missing_shape : Fintype.card (DecoratedPartition 2 (Fin 2)) = 4 := by
  rw [card_decoratedPartition_two]; norm_num; decide
