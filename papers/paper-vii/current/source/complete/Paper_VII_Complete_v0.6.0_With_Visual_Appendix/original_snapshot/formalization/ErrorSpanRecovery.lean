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

/-- The scalar-composite coefficients recover the original compressed Gram entries. -/
theorem compressed_gram_from_scalar (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ)
    (hR : (∑ r, star (R r)*R r)=1) (z : J × I → ℂ)
    (hz : ∀ r a, R r*E a*P=z (r,a) • P) (a b : I) :
    P*star (E a)*E b*P=(∑ r, star (z (r,a))*z (r,b)) • P := by
  have heq : P*star (E a)*E b*P = ∑ r, star (R r*E a*P)*(R r*E b*P) := by
    calc
      _ = P*star (E a)*(∑ r, star (R r)*R r)*E b*P := by rw [hR, mul_one]
      _ = _ := by
        simp only [Finset.mul_sum, Finset.sum_mul, star_mul,
          hP.isSelfAdjoint.star_eq, mul_assoc]
  rw [heq]
  simp_rw [hz, star_smul, hP.isSelfAdjoint.star_eq, smul_mul_assoc,
    mul_smul_comm, smul_smul, hP.isIdempotentElem.eq]
  rw [Finset.sum_smul]

/-- Trace preservation of the actual normalized Kraus sum. -/
theorem noise_preserves_trace (E : I → Matrix n n ℂ)
    (hE : (∑ a, star (E a)*E a)=1) (rho : Matrix n n ℂ) :
    Matrix.trace (noise E rho)=Matrix.trace rho := by
  rw [noise, Matrix.trace_sum]
  have cyclic (a : I) : Matrix.trace (E a*rho*star (E a)) =
      Matrix.trace ((star (E a)*E a)*rho) := by
    rw [Matrix.trace_mul_comm, Matrix.mul_assoc]
  simp_rw [cyclic]
  rw [← Matrix.trace_sum, ← Finset.sum_mul, hE, Matrix.one_mul]

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

/-- Cross terms for the original, not necessarily orthogonal or normalized, errors. -/
theorem recovery_cross_error (rho : Matrix n n ℂ) (hrho : K.code*rho*K.code=rho) (a b : I) :
    K.diagonal.syndromes.decoder (K.error a*rho*star (K.error b)) = K.gramMatrix b a • rho := by
  by_cases hp : K.code=0
  · have hz : rho=0 := by simpa [hp] using hrho.symm
    simp [hz, KomorebiPaperVII.Recovery.OrthogonalSyndromes.decoder]
  · obtain ⟨z,hz⟩ := K.recovery_scalar_composites
    have hcoeff : (∑ r, z (r,a)*star (z (r,b)))=K.gramMatrix b a := by
      apply smul_left_injective ℂ hp
      change (∑ r, z (r,a)*star (z (r,b))) • K.code=K.gramMatrix b a • K.code
      rw [← K.gram b a, compressed_gram_from_scalar K.code K.code_projection K.error
        K.diagonal.syndromes.recoveryKraus K.recovery_complete z hz b a]
      simp only [mul_comm]
    rw [K.diagonal.syndromes.decoder_eq_kraus]
    change noise K.diagonal.syndromes.recoveryKraus (K.error a*rho*star (K.error b)) = _
    rw [recovery_cross_from_scalar K.code K.code_projection K.error
      K.diagonal.syndromes.recoveryKraus z hz rho hrho a b, hcoeff]

/-- One decoder corrects every coherent combination, with its exact Gram weight. -/
theorem recovery_error_superposition (rho : Matrix n n ℂ) (hrho : K.code*rho*K.code=rho)
    (c : I → ℂ) :
    K.diagonal.syndromes.decoder ((∑ a, c a • K.error a)*rho*star (∑ b, c b • K.error b)) =
      (∑ a, ∑ b, c a*star (c b)*K.gramMatrix b a) • rho := by
  have heq : (∑ a, c a • K.error a)*rho*star (∑ b, c b • K.error b) =
      ∑ a, ∑ b, (c a*star (c b)) • (K.error a*rho*star (K.error b)) := by
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
  rw [heq]
  change K.diagonal.syndromes.decoderLinear (∑ a, ∑ b, (c a*star (c b)) •
    (K.error a*rho*star (K.error b))) = _
  simp only [map_sum, map_smul]
  change (∑ a, ∑ b, (c a*star (c b)) • K.diagonal.syndromes.decoder
    (K.error a*rho*star (K.error b))) = _
  simp_rw [K.recovery_cross_error rho hrho]
  simp only [smul_smul, Finset.sum_smul]

/-- The same recovery corrects every normalized channel whose errors lie in the original span. -/
theorem recovery_span_channel (F : J → Matrix n n ℂ) (c : J → I → ℂ)
    (hc : ∀ j, F j=∑ a, c j a • K.error a)
    (hF : (∑ j, star (F j)*F j)=1)
    (rho : Matrix n n ℂ) (hrho : K.code*rho*K.code=rho) :
    K.diagonal.syndromes.decoder (noise F rho)=rho := by
  let q : ℂ := ∑ j, ∑ a, ∑ b, c j a*star (c j b)*K.gramMatrix b a
  have hscaled (rho : Matrix n n ℂ) (hs : K.code*rho*K.code=rho) :
      K.diagonal.syndromes.decoder (noise F rho)=q • rho := by
    change K.diagonal.syndromes.decoderLinear (∑ j, F j*rho*star (F j)) = _
    rw [map_sum]
    change (∑ j, K.diagonal.syndromes.decoder (F j*rho*star (F j))) = _
    simp_rw [hc, K.recovery_error_superposition rho hs]
    rw [← Finset.sum_smul]
  rw [hscaled rho hrho]
  by_cases hp : K.code=0
  · have hz : rho=0 := by simpa [hp] using hrho.symm
    simp [hz]
  · have hpos : K.code.PosSemidef := by
      have hx := Matrix.posSemidef_conjTranspose_mul_self K.code
      change (star K.code*K.code).PosSemidef at hx
      rw [K.code_projection.isSelfAdjoint.star_eq, K.code_projection.isIdempotentElem.eq] at hx
      exact hx
    have ht : Matrix.trace K.code ≠ 0 := (hpos.trace_eq_zero_iff).not.mpr hp
    have hs : K.code*K.code*K.code=K.code := by simp only [K.code_projection.isIdempotentElem.eq]
    have hh := congrArg Matrix.trace (hscaled K.code hs)
    rw [K.recovery_preserves_trace, noise_preserves_trace F hF, Matrix.trace_smul] at hh
    have hq : q=1 := mul_right_cancel₀ ht (by simpa using hh.symm)
    rw [hq, one_smul]

end Data

/-- For an unnormalized error family, exact recovery has a code-independent nonnegative scale. -/
def ErrorFamilyCorrectable (P : Matrix n n ℂ) (E : I → Matrix n n ℂ) : Prop :=
  ∃ m : ℕ, ∃ R : Fin m → Matrix n n ℂ, (∑ r, star (R r)*R r)=1 ∧
    ∃ t : ℝ, 0 ≤ t ∧ ∀ rho, P*rho*P=rho → noise R (noise E rho)=(t : ℂ) • rho

/-- Gram necessity for arbitrary, possibly unnormalized and singular, error families. -/
theorem gram_of_scaled_recovery (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) (R : J → Matrix n n ℂ)
    (hR : (∑ r, star (R r)*R r)=1) (t : ℝ) (ht : 0 ≤ t)
    (hcorrect : ∀ rho, P*rho*P=rho → noise R (noise E rho)=(t : ℂ) • rho) :
    ∃ C : Matrix I I ℂ, C.PosSemidef ∧ ∀ a b, P*star (E a)*E b*P=C a b • P := by
  obtain ⟨z,hz⟩ := scaled_corrected_kraus_family P hP E R t ht hcorrect
  let Z : Matrix J I ℂ := fun r a => z (r,a)
  refine ⟨Z.conjTranspose*Z, Matrix.posSemidef_conjTranspose_mul_self Z, ?_⟩
  intro a b
  simpa [Z, Matrix.mul_apply, Matrix.conjTranspose_apply] using
    compressed_gram_from_scalar P hP E R hR z hz a b

/-- Full finite error-family criterion, with normalization made explicit rather than assumed. -/
theorem error_family_correctable_iff_gram (P : Matrix n n ℂ) (hP : IsStarProjection P)
    (E : I → Matrix n n ℂ) :
    ErrorFamilyCorrectable P E ↔ ∃ C : Matrix I I ℂ, C.PosSemidef ∧
      ∀ a b, P*star (E a)*E b*P=C a b • P := by
  constructor
  · rintro ⟨m,R,hR,t,ht,hcorrect⟩
    exact gram_of_scaled_recovery P hP E R hR t ht hcorrect
  · rintro ⟨C,hC,hgram⟩
    let K : Data n I := ⟨P,hP,E,C,hC,hgram⟩
    let e := Fintype.equivFin (Option K.diagonal.Active)
    let R := K.diagonal.syndromes.recoveryKraus
    refine ⟨Fintype.card (Option K.diagonal.Active), fun r => R (e.symm r), ?_,
      (Matrix.trace C).re, (RCLike.nonneg_iff.mp hC.trace_nonneg).1, ?_⟩
    · exact (e.symm.sum_comp (fun a => star (R a)*R a)).trans K.recovery_complete
    · intro rho hrho
      change (∑ r, R (e.symm r)*noise E rho*star (R (e.symm r))) = _
      rw [e.symm.sum_comp (fun a => R a*noise E rho*star (R a))]
      have hreal : ((Matrix.trace C).re : ℂ)=Matrix.trace C := by
        exact Complex.ext rfl (by simpa using (RCLike.nonneg_iff.mp hC.trace_nonneg).2.symm)
      rw [hreal]
      exact (K.diagonal.syndromes.decoder_eq_kraus (noise E rho)).symm.trans
        (K.recovery_noise_scaled rho hrho)

end KomorebiPaperVII.KnillLaflamme

/-! Complete declaration-level trust audit. -/
#print axioms KomorebiPaperVII.KnillLaflamme.scaled_corrected_kraus_family
#print axioms KomorebiPaperVII.KnillLaflamme.compressed_gram_from_scalar
#print axioms KomorebiPaperVII.KnillLaflamme.noise_preserves_trace
#print axioms KomorebiPaperVII.KnillLaflamme.Data.recovery_scalar_composites
#print axioms KomorebiPaperVII.KnillLaflamme.Data.recovery_cross_error
#print axioms KomorebiPaperVII.KnillLaflamme.Data.recovery_error_superposition
#print axioms KomorebiPaperVII.KnillLaflamme.Data.recovery_span_channel
#print axioms KomorebiPaperVII.KnillLaflamme.gram_of_scaled_recovery
#print axioms KomorebiPaperVII.KnillLaflamme.error_family_correctable_iff_gram
