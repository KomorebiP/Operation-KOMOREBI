import PaperICompletion7
example (R : Type) [Ring R] : DivisionRing (R ⧸ Ring.jacobson R) :=
  Komorebi.PaperICompletion7.LocalResidue.residueDivisionRing R
