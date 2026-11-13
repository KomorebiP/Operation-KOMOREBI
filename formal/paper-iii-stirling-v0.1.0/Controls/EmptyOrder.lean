import KomorebiPaperIIIStirling
open Komorebi.PaperIII.CompositionTermCount

theorem wrong_empty_order : Fintype.card (DecoratedPartition 0 (Fin 0)) = 0 := by
  rw [card_decoratedPartition_zero]; decide
