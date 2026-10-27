module
public import Mathlib.Algebra.Star.StarProjection
public import Mathlib.Algebra.Star.BigOperators
public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.LinearAlgebra.Matrix.Kronecker
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, fourth block.
Constructive recovery from an orthogonal partial-isometry syndrome family.
This is the recovery stage of Knill-Laflamme, not its full necessity or the
spectral reduction from an arbitrary positive Gram matrix. -/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.Recovery
open scoped BigOperators Kronecker ComplexOrder

structure OrthogonalSyndromes (R I : Type*) [Ring R] [StarRing R]
    [Fintype I] [DecidableEq I] where
  code : R
  code_projection : IsStarProjection code
  error : I → R
  restricted : ∀ a, error a * code = error a
  gram : ∀ a b, star (error a) * error b = if a=b then code else 0

namespace OrthogonalSyndromes
variable {R I : Type*} [Ring R] [StarRing R] [Fintype I] [DecidableEq I]
variable (S : OrthogonalSyndromes R I)

def packet (a : I) : R := S.error a * star (S.error a)
def total : R := ∑ a, S.packet a
def complement : R := 1-S.total

theorem packet_selfAdjoint (a : I) : IsSelfAdjoint (S.packet a) := by
  change star (S.packet a) = S.packet a
  simp [packet]

theorem packet_mul (a b : I) : S.packet a * S.packet b =
    if a=b then S.packet a else 0 := by
  have heq : S.packet a * S.packet b =
      S.error a * (star (S.error a) * S.error b) * star (S.error b) := by
    unfold packet
    noncomm_ring
  rw [heq, S.gram]
  by_cases h : a=b
  · subst b
    simp [S.restricted, packet]
  · simp [h]

theorem total_projection : IsStarProjection S.total := by
  constructor
  · change S.total*S.total=S.total
    simp [total, Finset.sum_mul, Finset.mul_sum, S.packet_mul]
  · change star (∑ a, S.packet a) = ∑ a, S.packet a
    rw [star_sum]
    exact Finset.sum_congr rfl (fun a _ => (S.packet_selfAdjoint a).star_eq)

theorem complement_projection : IsStarProjection S.complement :=
  S.total_projection.one_sub

theorem total_error (a : I) : S.total*S.error a = S.error a := by
  simp only [total, Finset.sum_mul, packet, mul_assoc, S.gram]
  simp [mul_ite, S.restricted]

theorem complement_error (a : I) : S.complement*S.error a = 0 := by
  simp [complement, sub_mul, S.total_error]

theorem error_adjoint_complement (a : I) : star (S.error a)*S.complement = 0 := by
  have hh := congrArg star (S.complement_error a)
  simpa [star_mul, S.complement_projection.isSelfAdjoint.star_eq] using hh

/-- A total, trace-preserving extension: the unused complement is retained. -/
def decoder (rho : R) : R :=
  (∑ a, star (S.error a)*rho*S.error a) + S.complement*rho*S.complement

/-- Includes the complement Kraus operator rather than silently discarding it. -/
def recoveryKraus : Option I → R
  | none => S.complement
  | some a => star (S.error a)

theorem recoveryKraus_complete :
    (∑ a, star (S.recoveryKraus a)*S.recoveryKraus a) = 1 := by
  rw [Fintype.sum_option]
  simp only [recoveryKraus, star_star, S.complement_projection.isSelfAdjoint.star_eq,
    S.complement_projection.isIdempotentElem.eq]
  change S.complement + S.total = 1
  simp [complement]

theorem decoder_eq_kraus (rho : R) :
    S.decoder rho = ∑ a, S.recoveryKraus a*rho*star (S.recoveryKraus a) := by
  rw [Fintype.sum_option]
  simp [decoder, recoveryKraus, S.complement_projection.isSelfAdjoint.star_eq, add_comm]

theorem decoder_add (rho sigma : R) :
    S.decoder (rho+sigma) = S.decoder rho + S.decoder sigma := by
  simp only [decoder, mul_add, add_mul, Finset.sum_add_distrib]
  abel

/-- Every off-diagonal syndrome term is removed, every diagonal one decoded. -/
theorem decoder_cross_error (rho : R) (hrho : S.code*rho*S.code=rho) (a b : I) :
    S.decoder (S.error a*rho*star (S.error b)) = if a=b then rho else 0 := by
  have hc (c : I) :
      star (S.error c)*(S.error a*rho*star (S.error b))*S.error c =
        if c=a then (if a=b then rho else 0) else 0 := by
    have heq : star (S.error c)*(S.error a*rho*star (S.error b))*S.error c =
        (star (S.error c)*S.error a)*rho*(star (S.error b)*S.error c) := by
      noncomm_ring
    rw [heq, S.gram, S.gram]
    by_cases hca : c=a
    · subst c
      by_cases hab : a=b
      · subst b; simp [hrho]
      · simp [hab, Ne.symm hab]
    · simp [hca]
  have hq : S.complement*(S.error a*rho*star (S.error b))*S.complement=0 := by
    calc
      _ = (S.complement*S.error a)*rho*(star (S.error b)*S.complement) := by
        noncomm_ring
      _ = 0 := by rw [S.complement_error, zero_mul, zero_mul]
  simp only [decoder, hc, hq, add_zero]
  simp

section Scalars
variable [Algebra ℂ R] [StarModule ℂ R]

theorem decoder_smul (z : ℂ) (rho : R) : S.decoder (z • rho) = z • S.decoder rho := by
  simp [decoder, Finset.smul_sum, smul_add]

def decoderLinear : R →ₗ[ℂ] R where
  toFun := S.decoder
  map_add' := S.decoder_add
  map_smul' := S.decoder_smul

/-- Exact recovery of every normalized mixture of the certified syndrome errors. -/
theorem decoder_weighted_noise (rho : R) (hrho : S.code*rho*S.code=rho)
    (weights : I → ℂ) (hweights : ∑ a, weights a=1) :
    S.decoder (∑ a, weights a • (S.error a*rho*star (S.error a))) = rho := by
  change S.decoderLinear (∑ a, weights a • (S.error a*rho*star (S.error a))) = rho
  rw [map_sum]
  simp only [map_smul]
  change (∑ a, weights a • S.decoder (S.error a*rho*star (S.error a))) = rho
  simp_rw [S.decoder_cross_error rho hrho, ite_true]
  rw [← Finset.sum_smul, hweights, one_smul]

/-- Coherent error superpositions are corrected with their exact norm factor. -/
theorem decoder_error_superposition (rho : R) (hrho : S.code*rho*S.code=rho)
    (z : I → ℂ) :
    S.decoder ((∑ a, z a • S.error a)*rho*star (∑ b, z b • S.error b)) =
      (∑ a, z a * star (z a)) • rho := by
  have heq : (∑ a, z a • S.error a)*rho*star (∑ b, z b • S.error b) =
      ∑ a, ∑ b, (z a * star (z b)) • (S.error a*rho*star (S.error b)) := by
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
  change S.decoderLinear (∑ a, ∑ b, (z a * star (z b)) •
    (S.error a*rho*star (S.error b))) = _
  simp only [map_sum, map_smul]
  change (∑ a, ∑ b, (z a * star (z b)) • S.decoder
    (S.error a*rho*star (S.error b))) = _
  simp_rw [S.decoder_cross_error rho hrho]
  simp [smul_ite, Finset.sum_smul]
end Scalars
end OrthogonalSyndromes

section Matrices
variable {n I : Type*} [Fintype n] [DecidableEq n] [Fintype I] [DecidableEq I]
variable (S : OrthogonalSyndromes (Matrix n n ℂ) I)

theorem recovery_positive {rho : Matrix n n ℂ} (hrho : rho.PosSemidef) :
    (S.decoder rho).PosSemidef := by
  rw [S.decoder_eq_kraus]
  exact Matrix.posSemidef_sum _ (fun a _ =>
    hrho.mul_mul_conjTranspose_same (S.recoveryKraus a))

theorem recovery_trace_preserving (rho : Matrix n n ℂ) :
    Matrix.trace (S.decoder rho) = Matrix.trace rho := by
  rw [S.decoder_eq_kraus, Matrix.trace_sum]
  have cyclic (a : Option I) :
      Matrix.trace (S.recoveryKraus a*rho*star (S.recoveryKraus a)) =
        Matrix.trace ((star (S.recoveryKraus a)*S.recoveryKraus a)*rho) := by
    rw [Matrix.trace_mul_comm, Matrix.mul_assoc]
  simp_rw [cyclic]
  rw [← Matrix.trace_sum, ← Finset.sum_mul, S.recoveryKraus_complete, Matrix.one_mul]

/-- The actual identity-tensor recovery, checked at every finite auxiliary dimension. -/
theorem recovery_complete_positivity {J : Type*} [Fintype J] [DecidableEq J]
    {rho : Matrix (J × n) (J × n) ℂ} (hrho : rho.PosSemidef) :
    Matrix.PosSemidef (fun (x y : J × n) =>
      S.decoder (fun u v => rho (x.1,u) (y.1,v)) x.2 y.2) := by
  have heq : (fun (x y : J × n) => S.decoder (fun u v => rho (x.1,u) (y.1,v)) x.2 y.2) =
      ∑ a, ((1 : Matrix J J ℂ) ⊗ₖ S.recoveryKraus a)*rho*
        (((1 : Matrix J J ℂ) ⊗ₖ S.recoveryKraus a).conjTranspose) := by
    ext ⟨i,u⟩ ⟨j,v⟩
    simp_rw [S.decoder_eq_kraus, Matrix.sum_apply, Matrix.mul_apply,
      Matrix.conjTranspose_apply, Matrix.kroneckerMap_apply]
    simp [Fintype.sum_prod_type, Matrix.one_apply, apply_ite]
  rw [heq]
  exact Matrix.posSemidef_sum _ (fun a _ =>
    hrho.mul_mul_conjTranspose_same ((1 : Matrix J J ℂ) ⊗ₖ S.recoveryKraus a))

theorem recovery_density_matrix {rho : Matrix n n ℂ}
    (hrho : rho.PosSemidef) (htrace : Matrix.trace rho=1) :
    (S.decoder rho).PosSemidef ∧ Matrix.trace (S.decoder rho)=1 :=
  ⟨recovery_positive S hrho, (recovery_trace_preserving S rho).trans htrace⟩
end Matrices
end KomorebiPaperVII.Recovery
