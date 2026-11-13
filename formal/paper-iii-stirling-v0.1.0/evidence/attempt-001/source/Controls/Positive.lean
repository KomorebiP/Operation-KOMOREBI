import KomorebiPaperIIIStirling
open Komorebi.PaperIII.CompositionTermCount
namespace Komorebi.PaperIII.StirlingControls

theorem empty_order_empty_labels : Fintype.card (DecoratedPartition 0 (Fin 0)) = 1 :=
  card_decoratedPartition_zero (Fin 0)

theorem first_order : Fintype.card (DecoratedPartition 1 (Fin 2)) = 2 := by
  simpa using card_decoratedPartition_one (Fin 2)

theorem second_order : Fintype.card (DecoratedPartition 2 (Fin 2)) = 6 := by
  simpa using card_decoratedPartition_two (Fin 2)

theorem third_order : Fintype.card (DecoratedPartition 3 (Fin 2)) = 22 := by
  rw [card_decoratedPartition]
  norm_num [Finset.sum_range_succ, Nat.stirlingSecond]

theorem positive_order_empty_labels : Fintype.card (DecoratedPartition 3 (Fin 0)) = 0 := by
  rw [card_decoratedPartition]
  norm_num [Finset.sum_range_succ, Nat.stirlingSecond]

end Komorebi.PaperIII.StirlingControls
