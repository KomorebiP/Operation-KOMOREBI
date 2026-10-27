import PaperICompletion7
set_option autoImplicit false
open Komorebi.PaperICompletion7.Nakayama
example {R M : Type} [Ring R] [AddCommGroup M] [Module R M] [Module.Finite R M]
    (I : Ideal R) (N : Submodule R M) (h : N ⊔ I • (⊤ : Submodule R M) = ⊤) :
    N = ⊤ := eq_top_of_sup_ideal_smul I (le_refl I) N h
