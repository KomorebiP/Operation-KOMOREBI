import KomorebiLSM.BayesianDefect
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Setoid.Partition
#check Quotient.mk_surjective
#check Quotient.sound
#check Quotient.exact
#check Setoid.ext
#check Setoid.le_def
#check Fintype.ofFinite
#synth Finite (Quotient (⊤ : Setoid (Fin 6)))
#check Fintype.bijective_iff_injective_and_card
#check Fintype.bijective_iff_surjective_and_card
#check Fintype.injective_iff_surjective
#check Fintype.card_quotient_le
#print Setoid.ker
