import PaperIRelease.GrammarIdeal
open Komorebi.PaperIRelease.GrammarAlgebra
noncomputable section
abbrev noArrow : Fin 0 → Fin 1 := Fin.elim0
abbrev grammar : Grammar ℚ (Fin 1) (Fin 0) := freeGrammar noArrow noArrow
def invalidCollapsed : CollapsedRealization grammar ℚ where
  vertex _ := 0
  arrow a := Fin.elim0 a
  vertex_idempotent _ := by simp
  vertex_orthogonal _ _ _ := by simp
  vertex_complete := by simp
  arrow_corner a := Fin.elim0 a
  declared _ _ h := h.elim
