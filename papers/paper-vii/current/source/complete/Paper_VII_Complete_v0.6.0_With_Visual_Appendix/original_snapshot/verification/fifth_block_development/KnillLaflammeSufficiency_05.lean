module
public import SyndromeRecovery
import all SyndromeRecovery
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


/-- Diagonal Gram data. Weights may vanish; no invertibility is assumed. -/
structure DiagonalErrors (n I : Type*) [Fintype n] [DecidableEq n]
    [Fintype I] [DecidableEq I] where
  code : Matrix n n ℂ
  code_projection : IsStarProjection code
  error : I → Matrix n n ℂ
  restricted : ∀ a, error a * code = error a
  weight : I → ℝ
  nonnegative : ∀ a, 0 ≤ weight a
  gram : ∀ a b, star (error a) * error b = if a=b then (weight a : ℂ) • code else 0

namespace DiagonalErrors
variable (D : DiagonalErrors n I)

/-- Null eigenvalue directions vanish on the code. -/
theorem zero_weight_error (a : I) (ha : D.weight a = 0) : D.error a = 0 := by
  have hh : star (D.error a) * D.error a = 0 := by
    simpa only [ite_true, ha, Complex.ofReal_zero, zero_smul] using D.gram a a
  exact Matrix.conjTranspose_mul_self_eq_zero.mp hh

/-- Only strictly positive eigenvalues are normalized. -/
abbrev Active := {a : I // 0 < D.weight a}

noncomputable def normalizedError (a : D.Active) : Matrix n n ℂ :=
  (Real.sqrt (D.weight a) : ℂ)⁻¹ • D.error a

theorem sqrt_weight_ne_zero (a : D.Active) : (Real.sqrt (D.weight a) : ℂ) ≠ 0 := by
  exact_mod_cast (ne_of_gt (Real.sqrt_pos.mpr a.property))

theorem sqrt_weight_sq (a : I) :
    (Real.sqrt (D.weight a) : ℂ) * (Real.sqrt (D.weight a) : ℂ) = (D.weight a : ℂ) := by
  exact_mod_cast Real.mul_self_sqrt (D.nonnegative a)

theorem normalized_restricted (a : D.Active) : D.normalizedError a * D.code = D.normalizedError a := by
  simp [normalizedError, D.restricted]

theorem normalized_gram (a b : D.Active) :
    star (D.normalizedError a) * D.normalizedError b = if a=b then D.code else 0 := by
  simp only [normalizedError, star_smul, smul_mul_assoc, mul_smul_comm, smul_smul, D.gram]
  by_cases h : a=b
  · subst b
    simp only [ite_true, smul_smul]
    have hs : star ((Real.sqrt (D.weight a) : ℂ)⁻¹) = (Real.sqrt (D.weight a) : ℂ)⁻¹ := by simp
    rw [hs]
    have heq : (Real.sqrt (D.weight a) : ℂ)⁻¹ *
        (Real.sqrt (D.weight a) : ℂ)⁻¹ * (D.weight a : ℂ) = 1 := by
      rw [← D.sqrt_weight_sq]
      field_simp [D.sqrt_weight_ne_zero a]
    rw [heq, one_smul]
  · have hab : (a : I) ≠ (b : I) := fun h' => h (Subtype.ext h')
    simp [h, hab]

/-- The previous block's recovery object, now constructed from diagonal Gram data. -/
noncomputable def syndromes : OrthogonalSyndromes (Matrix n n ℂ) D.Active where
  code := D.code
  code_projection := D.code_projection
  error := D.normalizedError
  restricted := D.normalized_restricted
  gram := D.normalized_gram

theorem error_eq_sqrt_normalized (a : D.Active) :
    D.error a = (Real.sqrt (D.weight a) : ℂ) • D.normalizedError a := by
  simp [normalizedError, smul_smul, D.sqrt_weight_ne_zero a]

theorem decode_diagonal_error (rho : Matrix n n ℂ) (hrho : D.code*rho*D.code=rho) (a : I) :
    D.syndromes.decoder (D.error a*rho*star (D.error a)) = (D.weight a : ℂ) • rho := by
  by_cases ha : 0 < D.weight a
  · let a' : D.Active := ⟨a,ha⟩
    have heq := D.error_eq_sqrt_normalized a'
    change D.error a = _ at heq
    rw [heq]
    simp only [star_smul, smul_mul_assoc, mul_smul_comm, smul_smul,
      Complex.star_def, Complex.conj_ofReal]
    rw [D.syndromes.decoder_smul]
    change ((Real.sqrt (D.weight a) : ℂ) * (Real.sqrt (D.weight a) : ℂ)) •
      D.syndromes.decoder (D.syndromes.error a'*rho*star (D.syndromes.error a')) = _
    rw [D.syndromes.decoder_cross_error rho hrho, if_pos rfl, D.sqrt_weight_sq]
  · have hz : D.weight a = 0 := le_antisymm (le_of_not_gt ha) (D.nonnegative a)
    rw [D.zero_weight_error a hz]
    simp only [zero_mul, star_zero, mul_zero, hz, Complex.ofReal_zero, zero_smul]
    exact D.syndromes.decoderLinear.map_zero

theorem decode_noise (rho : Matrix n n ℂ) (hrho : D.code*rho*D.code=rho) :
    D.syndromes.decoder (noise D.error rho) = (∑ a, (D.weight a : ℂ)) • rho := by
  change D.syndromes.decoderLinear (∑ a, D.error a*rho*star (D.error a)) = _
  rw [map_sum]
  change (∑ a, D.syndromes.decoder (D.error a*rho*star (D.error a))) = _
  simp_rw [D.decode_diagonal_error rho hrho]
  rw [Finset.sum_smul]

end DiagonalErrors

end KomorebiPaperVII.KnillLaflamme
