module
public import QuantumStateBridge
import all QuantumStateBridge
import all KnillLaflammeNecessity
import all KnillLaflammeSufficiency
import all SyndromeRecovery
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII fifth block.
The same constructed recovery corrects the entire error span, not just one Kraus presentation.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.KnillLaflamme
open scoped BigOperators ComplexOrder
open Matrix
variable {n I J : Type*} [Fintype n] [DecidableEq n]
    [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]

/-- Rank-one Kraus rigidity also applies to a nonnegative multiple of the code map. -/
theorem scaled_corrected_kraus_family (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ) (t : ℝ) (ht : 0 ≤ t)
    (hcorrect : ∀ rho, P*rho*P=rho → noise R (noise E rho)=(t : ℂ) • rho) :
    ∃ z : J × I → ℂ, ∀ r a, R r*E a*P=z (r,a) • P := by
  let Q : Matrix n n ℂ := (Real.sqrt t : ℂ) • P
  have hsqrt : (Real.sqrt t : ℂ)*(Real.sqrt t : ℂ)=(t : ℂ) := by
    exact_mod_cast Real.mul_self_sqrt ht
  have hmap (rho : Matrix n n ℂ) :
      noise (fun ra : J × I => R ra.1*E ra.2*P) rho=Q*rho*star Q := by
    have hrho : P*(P*rho*P)*P=P*rho*P := by
      simp only [← mul_assoc, hP.isIdempotentElem.eq]
      rw [mul_assoc (P*rho), hP.isIdempotentElem.eq]
    have heq : noise (fun ra : J × I => R ra.1*E ra.2*P) rho =
        noise R (noise E (P*rho*P)) := by
      simp only [noise, Fintype.sum_prod_type, star_mul, hP.isSelfAdjoint.star_eq,
        Finset.mul_sum, Finset.sum_mul, mul_assoc]
    rw [heq, hcorrect _ hrho]
    simp only [Q, star_smul, hP.isSelfAdjoint.star_eq, Complex.star_def,
      Complex.conj_ofReal, smul_mul_assoc, mul_smul_comm, smul_smul, hsqrt]
  obtain ⟨z,hz⟩ := kraus_rank_one_rigidity (fun ra : J × I => R ra.1*E ra.2*P) Q hmap
  refine ⟨fun ra => z ra*(Real.sqrt t : ℂ), ?_⟩
  intro r a
  exact (hz (r,a)).trans (smul_smul _ _ _)

namespace Data
variable (K : Data n I)

/-- Scalar corrected Kraus operators for arbitrary Gram data, including zero trace. -/
theorem recovery_scalar_composites :
    ∃ z : (Option K.diagonal.Active) × I → ℂ,
      ∀ r a, K.diagonal.syndromes.recoveryKraus r*K.error a*K.code=z (r,a) • K.code := by
  have hreal : ((Matrix.trace K.gramMatrix).re : ℂ)=Matrix.trace K.gramMatrix := by
    exact Complex.ext rfl (by simpa using (RCLike.nonneg_iff.mp K.gram_positive.trace_nonneg).2.symm)
  apply scaled_corrected_kraus_family K.code K.code_projection K.error
    K.diagonal.syndromes.recoveryKraus (Matrix.trace K.gramMatrix).re
    (RCLike.nonneg_iff.mp K.gram_positive.trace_nonneg).1
  intro rho hrho
  change (∑ r, K.diagonal.syndromes.recoveryKraus r*noise K.error rho*
    star (K.diagonal.syndromes.recoveryKraus r)) = _
  rw [← K.diagonal.syndromes.decoder_eq_kraus, hreal]
  exact K.recovery_noise_scaled rho hrho
end Data

end KomorebiPaperVII.KnillLaflamme
