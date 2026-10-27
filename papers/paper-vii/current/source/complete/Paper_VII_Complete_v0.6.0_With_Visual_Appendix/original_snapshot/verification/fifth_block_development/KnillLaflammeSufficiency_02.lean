module
public import SyndromeRecovery
public import Mathlib.Analysis.Matrix.PosDef
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII fifth block.
Spectral reduction of general Knill-Laflamme data, retaining singular Gram matrices.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.KnillLaflamme
open scoped BigOperators ComplexOrder
open Matrix
open KomorebiPaperVII.Recovery
variable {n I : Type*} [Fintype n] [DecidableEq n] [Fintype I] [DecidableEq I]

/-- A change of coordinates in the error index, with columns as new errors. -/
def mix (E : I → Matrix n n ℂ) (U : Matrix I I ℂ) (r : I) : Matrix n n ℂ :=
  ∑ a, U a r • E a

/-- Unnormalized finite Kraus sum. -/
def noise (E : I → Matrix n n ℂ) (rho : Matrix n n ℂ) : Matrix n n ℂ :=
  ∑ a, E a * rho * star (E a)

theorem mix_restricted (P : Matrix n n ℂ) (E : I → Matrix n n ℂ)
    (hE : ∀ a, E a * P = E a) (U : Matrix I I ℂ) (r : I) :
    mix E U r * P = mix E U r := by
  simp [mix, Finset.sum_mul, hE]

theorem mix_gram (P : Matrix n n ℂ) (E : I → Matrix n n ℂ)
    (C : Matrix I I ℂ) (hC : ∀ a b, star (E a) * E b = C a b • P)
    (U : Matrix I I ℂ) (r s : I) :
    star (mix E U r) * mix E U s = (star U * C * U) r s • P := by
  simp only [mix, star_sum, star_smul, Finset.sum_mul, Finset.mul_sum,
    smul_mul_assoc, mul_smul_comm, smul_smul, hC]
  simp only [smul_smul, Matrix.mul_apply, Matrix.star_apply, ← Finset.sum_smul]
  congr 1
  apply Finset.sum_congr rfl
  intro b _
  ring

theorem mix_noise (E : I → Matrix n n ℂ) (U : Matrix.unitaryGroup I ℂ)
    (rho : Matrix n n ℂ) : noise (mix E (U : Matrix I I ℂ)) rho = noise E rho := by
  have hU (a b : I) : (∑ r, (U : Matrix I I ℂ) a r * star ((U : Matrix I I ℂ) b r)) =
      if a=b then 1 else 0 := by
    simpa [Matrix.mul_apply, Matrix.star_apply, Matrix.one_apply] using
      congrArg (fun M : Matrix I I ℂ => M a b) (Unitary.coe_mul_star_self U)
  have heq (r : I) : mix E (U : Matrix I I ℂ) r * rho * star (mix E (U : Matrix I I ℂ) r) =
      ∑ a, ∑ b, ((U : Matrix I I ℂ) a r * star ((U : Matrix I I ℂ) b r)) •
        (E a * rho * star (E b)) := by
    unfold mix
    rw [star_sum]
    simp only [star_smul]
    rw [Finset.sum_mul, Finset.sum_mul]
    simp only [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro a _
    apply Finset.sum_congr rfl
    intro b _
    simp only [smul_mul_assoc, mul_smul_comm, smul_smul]
    rw [mul_comm]
  unfold noise
  simp_rw [heq]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro a _
  rw [Finset.sum_comm]
  simp_rw [← Finset.sum_smul, hU]
  simp

theorem diagonalized_gram (P : Matrix n n ℂ) (E : I → Matrix n n ℂ)
    (C : Matrix I I ℂ) (hC : C.PosSemidef)
    (hgram : ∀ a b, star (E a) * E b = C a b • P) (r s : I) :
    star (mix E (hC.isHermitian.eigenvectorUnitary : Matrix I I ℂ) r) *
      mix E (hC.isHermitian.eigenvectorUnitary : Matrix I I ℂ) s =
        if r=s then (hC.isHermitian.eigenvalues r : ℂ) • P else 0 := by
  rw [mix_gram P E C hgram]
  have hdiag : star (hC.isHermitian.eigenvectorUnitary : Matrix I I ℂ) * C *
      (hC.isHermitian.eigenvectorUnitary : Matrix I I ℂ) =
        diagonal (fun r => (hC.isHermitian.eigenvalues r : ℂ)) := by
    simpa [Unitary.conjStarAlgAut_star_apply, Function.comp_def] using
      hC.isHermitian.conjStarAlgAut_star_eigenvectorUnitary
  rw [hdiag]
  by_cases h : r=s
  · subst s; simp
  · simp [h]

end KomorebiPaperVII.KnillLaflamme
