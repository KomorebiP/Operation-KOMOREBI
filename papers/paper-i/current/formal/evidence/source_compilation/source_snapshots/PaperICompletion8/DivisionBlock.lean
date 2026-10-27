import KomorebiVerification.SemisimpleCompletion
import KomorebiVerification.SeedRankBasics
import KomorebiVerification.SeedRankOperations
import PaperICompletion8.DivisionRows
import KomorebiVerification.FullMatrixCyclicity

/-! Canonical seed ranks for the actual left matrix module over a division ring. -/
set_option autoImplicit false

-- Keep theorem bodies stable in this audit release while making the build warning-fatal.
set_option linter.unnecessarySimpa false
set_option linter.style.haveILetI false
set_option linter.unusedSectionVars false

namespace Komorebi.PaperICompletion8.DivisionBlock

open scoped BigOperators

open Komorebi.SeedRankBasics
open Komorebi.SeedRankOperations
open Komorebi.PaperICompletion8.DivisionRows

universe u v

variable {k : Type u} [DivisionRing k]

abbrev BlockAlgebra (d : ℕ) := Matrix (Fin d) (Fin d) k

abbrev BlockModule (d m : ℕ) := Matrix (Fin d) (Fin m) k

section BlockModules

local instance (priority := 100) blockModuleAction (d m : ℕ) :
    Module (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) :=
  Matrix.Module.matrixModule

/-- The scoped matrix-module action is ordinary multiplication on a
rectangular matrix. -/
theorem block_smul_eq_mul {d m : ℕ}
    (A : BlockAlgebra (k := k) d) (V : BlockModule (k := k) d m) :
    A • V = A * V := by
  ext i j
  change (∑ b, A i b • V b) j = ∑ b, A i b * V b j
  simp

/-- The bespoke row-space notion is exactly `FamilyGenerates` for the
canonical full-matrix module. -/
theorem leftGenerates_iff_familyGenerates {r d m : ℕ}
    (v : Fin r → BlockModule (k := k) d m) :
    LeftGenerates v ↔
      FamilyGenerates (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) v := by
  classical
  rw [FamilyGenerates, Generates, eq_top_iff,
    Submodule.top_le_span_range_iff_forall_exists_fun]
  constructor
  · intro h X
    obtain ⟨A, hA⟩ := h X
    refine ⟨A, ?_⟩
    simpa only [block_smul_eq_mul] using hA.symm
  · intro h X
    obtain ⟨A, hA⟩ := h X
    refine ⟨A, ?_⟩
    simpa only [block_smul_eq_mul] using hA.symm

open Komorebi.SemisimpleCompletion (seedFinrank_eq_of_exists_fin_family_iff)

/-- The one-block ceiling count is the general `SeedRankBasics.seedFinrank`,
not merely a bespoke minimum. -/
theorem oneBlock_seedFinrank_eq_ceilDiv {d m : ℕ} (hd : 0 < d) :
    seedFinrank (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) =
      m ⌈/⌉ d := by
  apply seedFinrank_eq_of_exists_fin_family_iff (c := m ⌈/⌉ d)
  intro r
  constructor
  · rintro ⟨v, hv⟩
    have hm : m ≤ r * d := (exists_leftGenerators_iff (k := k) hd).mp
      ⟨v, (leftGenerates_iff_familyGenerates v).mpr hv⟩
    apply (ceilDiv_le_iff_le_mul hd).mpr
    simpa [Nat.mul_comm] using hm
  · intro hr
    have hm : m ≤ r * d := by
      simpa [Nat.mul_comm] using (ceilDiv_le_iff_le_mul hd).mp hr
    obtain ⟨v, hv⟩ := (exists_leftGenerators_iff (k := k) hd).mpr hm
    exact ⟨v, (leftGenerates_iff_familyGenerates v).mp hv⟩

/-- Cardinal-valued form of the same one-block formula. -/
theorem oneBlock_seedRank_eq_ceilDiv {d m : ℕ} (hd : 0 < d) :
    seedRank (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) =
      ((m ⌈/⌉ d : ℕ) : Cardinal) := by
  classical
  have hfin : Module.Finite (BlockAlgebra (k := k) d)
      (BlockModule (k := k) d m) := by
    obtain ⟨v, hv⟩ := exists_leftGenerators_of_le (k := k)
      (r := m ⌈/⌉ d) hd (by
        have hm : m ≤ d * (m ⌈/⌉ d) := (ceilDiv_le_iff_le_mul hd).mp le_rfl
        simpa [Nat.mul_comm] using hm)
    exact Module.Finite.of_surjective
      (multiSeedMap (BlockAlgebra (k := k) d) (BlockModule (k := k) d m) v)
      ((familyGenerates_iff_surjective _ _ v).mp
        ((leftGenerates_iff_familyGenerates v).mp hv))
  letI := hfin
  rw [seedRank_eq_seedFinrank,
    oneBlock_seedFinrank_eq_ceilDiv (k := k) hd]

end BlockModules

end Komorebi.PaperICompletion8.DivisionBlock
