import KomorebiVerification.SemisimpleCompletion

/- These four consumer checks are audit fixtures, not new Paper I contract rows. -/
namespace PaperIAudit.Boundaries

-- A dense support graph does not prevent exact cancellation of length-two paths.
def cancellationMatrix : Matrix (Fin 2) (Fin 2) ℚ :=
  fun i _ => if i = 0 then 1 else -1

theorem cancellation_all_entries_nonzero (i j : Fin 2) :
    cancellationMatrix i j ≠ 0 := by
  fin_cases i <;> norm_num [cancellationMatrix]

theorem cancellation_square_zero :
    cancellationMatrix * cancellationMatrix = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [cancellationMatrix, Matrix.mul_apply, Fin.sum_univ_two]

-- The zero-module endpoint is rank zero, not an unqualified rank-one theorem.
theorem zero_module_seed_rank :
    Komorebi.SeedRankBasics.seedRank ℚ (Fin 0 → ℚ) = 0 := by
  exact (Komorebi.SeedRankBasics.seedRank_eq_zero_iff ℚ (Fin 0 → ℚ)).mpr inferInstance

-- Rank one depends on the actual acting full matrix algebra.
theorem full_matrix_rank_one :
    Komorebi.SeedRankBasics.seedRank
      (Matrix (Fin 2) (Fin 2) ℚ) (Fin 2 → ℚ) = 1 := by
  exact Komorebi.SemisimpleCompletion.fullMatrix_seedRank_eq_one (k := ℚ) (by decide)

end PaperIAudit.Boundaries

#print axioms PaperIAudit.Boundaries.cancellation_all_entries_nonzero
#print axioms PaperIAudit.Boundaries.cancellation_square_zero
#print axioms PaperIAudit.Boundaries.zero_module_seed_rank
#print axioms PaperIAudit.Boundaries.full_matrix_rank_one
