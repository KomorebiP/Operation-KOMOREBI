import KomorebiLSM.ConditionalStochasticCompletion
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.BigOperators.Fin

open Komorebi.LSM.Behavior

def badProcess (w : List (Unit × Unit)) : ℝ := (-1 : ℝ) ^ w.length

def emptySelection (_ : Fin 1) : List (Unit × Unit) := []

-- An invertible core alone must not imply stochastic probability validity.
example : 0 ≤ ((reconstructed badProcess emptySelection emptySelection ((),())).mulVecLin
    (tableState badProcess emptySelection [])) 0 := by
  have hcore : core badProcess emptySelection emptySelection = 1 := by
    ext i j
    fin_cases i
    fin_cases j
    norm_num [core, emptySelection, badProcess]
  rw [reconstructed, hcore, inv_one, mul_one]
  norm_num [Matrix.mulVecLin_apply, shiftedCore, tableState, emptySelection,
    badProcess, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]
