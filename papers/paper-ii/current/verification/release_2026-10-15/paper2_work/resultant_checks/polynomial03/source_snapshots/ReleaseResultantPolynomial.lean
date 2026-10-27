import KomorebiVerification.PaperII.ResultantSeparation
import Mathlib.LinearAlgebra.Charpoly.Basic
import Mathlib.LinearAlgebra.Charpoly.BaseChange
import Mathlib.LinearAlgebra.Projection

/-! Polynomial-to-operator bridges for the Paper II release. -/

set_option autoImplicit false

noncomputable section

namespace Komorebi.PaperII.ReleaseResultantPolynomial

open Polynomial ResultantSeparation

universe u v w

variable {K : Type u} {M : Type v}
variable [Field K] [AddCommGroup M] [Module K M]

theorem evaluated_polynomials_commute (A : Module.End K M) (p q : K[X]) :
    Commute (aeval A p) (aeval A q) := by
  change aeval A p * aeval A q = aeval A q * aeval A p
  rw [← map_mul, ← map_mul, mul_comm p q]

/-- Evaluation derives every certificate field from the polynomial identity and
the characteristic factorization; annihilation is Cayley--Hamilton. -/
theorem certificate_of_charpoly [Module.Free K M] [Module.Finite K M]
    (A : Module.End K M) (f g u v : K[X]) (r : K)
    (hr : r ≠ 0) (hchar : A.charpoly = f * g)
    (hbez : u * f + v * g = C r) :
    EvaluatedBezoutCertificate (aeval A f) (aeval A g)
      (aeval A u) (aeval A v) r where
  r_ne_zero := hr
  commute_FG := evaluated_polynomials_commute A f g
  commute_FU := evaluated_polynomials_commute A f u
  commute_FV := evaluated_polynomials_commute A f v
  commute_GU := evaluated_polynomials_commute A g u
  commute_GV := evaluated_polynomials_commute A g v
  commute_UV := evaluated_polynomials_commute A u v
  bezout := by
    have h := congrArg (aeval A) hbez
    simpa only [map_add, map_mul, aeval_C, Algebra.algebraMap_eq_smul_one] using h
  annihilate := by
    rw [← map_mul, ← hchar]
    exact A.aeval_self_charpoly

/-- A monic factor of degree zero is one, so the all-constant boundary case
also admits the actual Sylvester resultant as a clearing scalar. -/
theorem exists_resultant_bezout {R : Type w} [CommRing R]
    (f g : R[X]) (hf : f.Monic) :
    ∃ u v : R[X], u * f + v * g = C (f.resultant g) := by
  by_cases hf0 : f.natDegree = 0
  · have hf1 : f = 1 := eq_one_of_monic_natDegree_zero hf hf0
    subst f
    exact ⟨C ((1 : R[X]).resultant g), 0, by simp⟩
  · obtain ⟨u, v, _, _, h⟩ := exists_mul_add_mul_eq_C_resultant f g le_rfl le_rfl
      (Or.inl hf0)
    exact ⟨u, v, by simpa only [mul_comm u f, mul_comm v g] using h⟩

theorem resultant_nonzero_of_coprime (f g : K[X]) (h : IsCoprime f g) :
    f.resultant g ≠ 0 := by
  intro hz
  exact (Polynomial.resultant_eq_zero_iff.mp hz).2 h

/-- The polynomial/resultant endpoint constructs the evaluated certificate,
rather than assuming its commutations or its annihilation equation. -/
theorem resultant_projector_exists [Module.Free K M] [Module.Finite K M]
    (A : Module.End K M) (f g : K[X]) (hf : f.Monic)
    (hc : IsCoprime f g) (hchar : A.charpoly = f * g) :
    ∃ u v : K[X],
      u * f + v * g = C (f.resultant g) ∧
      EvaluatedBezoutCertificate (aeval A f) (aeval A g)
        (aeval A u) (aeval A v) (f.resultant g) ∧
      separator (f.resultant g) (aeval A v) (aeval A g) *
        separator (f.resultant g) (aeval A v) (aeval A g) =
        separator (f.resultant g) (aeval A v) (aeval A g) := by
  obtain ⟨u, v, hbez⟩ := exists_resultant_bezout f g hf
  have cert := certificate_of_charpoly A f g u v (f.resultant g)
    (resultant_nonzero_of_coprime f g hc) hchar hbez
  exact ⟨u, v, hbez, cert, separator_idempotent cert⟩

section ExactKernels

variable {F G U V : Module.End K M} {r : K}

theorem first_mul_separator_eq_zero
    (cert : EvaluatedBezoutCertificate F G U V r) :
    F * separator r V G = 0 := by
  rw [separator, mul_smul_comm, separatorNumerator, ← mul_assoc,
    cert.commute_FV.eq, mul_assoc, cert.annihilate, mul_zero, smul_zero]

theorem second_mul_separator_eq_self
    (cert : EvaluatedBezoutCertificate F G U V r) :
    G * separator r V G = G := by
  have hz : G * (U * F) = 0 := by
    rw [← mul_assoc, cert.commute_GU.eq, mul_assoc, ← cert.commute_FG.eq,
      cert.annihilate, mul_zero]
  have hb := congrArg (G * ·) cert.bezout
  have hvg : G * (V * G) = r • G := by
    simpa only [mul_add, hz, zero_add, mul_smul_comm, mul_one] using hb
  rw [separator, mul_smul_comm, separatorNumerator, hvg, smul_smul]
  simp [cert.r_ne_zero]

theorem separator_range_eq_first_kernel
    (cert : EvaluatedBezoutCertificate F G U V r) :
    LinearMap.range (separator r V G) = LinearMap.ker F := by
  ext x
  constructor
  · rintro ⟨y, rfl⟩
    exact LinearMap.congr_fun (first_mul_separator_eq_zero cert) y
  · intro hx
    exact ⟨x, separator_apply_of_mem_ker_F cert hx⟩

theorem separator_kernel_eq_second_kernel
    (cert : EvaluatedBezoutCertificate F G U V r) :
    LinearMap.ker (separator r V G) = LinearMap.ker G := by
  ext x
  constructor
  · intro hx
    change G x = 0
    have h := LinearMap.congr_fun (second_mul_separator_eq_self cert) x
    change separator r V G x = 0 at hx
    change G (separator r V G x) = G x at h
    simpa only [hx, map_zero] using h.symm
  · intro hx
    exact separator_apply_of_mem_ker_G hx

theorem complementary_kernels
    (cert : EvaluatedBezoutCertificate F G U V r) :
    IsCompl (LinearMap.ker F) (LinearMap.ker G) := by
  have hi : IsIdempotentElem (separator r V G) := separator_idempotent cert
  simpa only [separator_range_eq_first_kernel cert,
    separator_kernel_eq_second_kernel cert] using LinearMap.IsIdempotentElem.isCompl hi

end ExactKernels

section IntegralBaseChange

open scoped TensorProduct

variable {R : Type w} {L : Type v} [CommRing R] [AddCommGroup L]
variable [Module R L] [Algebra R K]

/-- The image of the actual integral module in its scalar extension. -/
def tensorLattice : Submodule R (K ⊗[R] L) :=
  LinearMap.range (TensorProduct.mk R K L 1)

theorem aeval_baseChange (A : Module.End R L) (p : R[X]) :
    (aeval A p).baseChange K =
      aeval (A.baseChange K) (p.map (algebraMap R K)) := by
  apply Polynomial.map_aeval_eq_aeval_map
    (ψ := (Module.End.baseChangeHom R K L).toRingHom)
  ext r
  simp [Algebra.algebraMap_eq_smul_one, LinearMap.baseChange_smul,
    LinearMap.baseChange_one]

theorem integral_evaluation_preserves_tensorLattice (A : Module.End R L) (p : R[X])
    (x : K ⊗[R] L) (hx : x ∈ tensorLattice (K := K) (R := R) (L := L)) :
    aeval (A.baseChange K) (p.map (algebraMap R K)) x ∈
      tensorLattice (K := K) (R := R) (L := L) := by
  obtain ⟨y, rfl⟩ := hx
  rw [← aeval_baseChange]
  exact ⟨aeval A p y, rfl⟩

theorem certificate_of_integral_charpoly [Module.Free R L] [Module.Finite R L]
    (A : Module.End R L) (f g u v : R[X]) (r : R)
    (hr : algebraMap R K r ≠ 0) (hchar : A.charpoly = f * g)
    (hbez : u * f + v * g = C r) :
    EvaluatedBezoutCertificate
      (aeval (A.baseChange K) (f.map (algebraMap R K)))
      (aeval (A.baseChange K) (g.map (algebraMap R K)))
      (aeval (A.baseChange K) (u.map (algebraMap R K)))
      (aeval (A.baseChange K) (v.map (algebraMap R K))) (algebraMap R K r) := by
  apply certificate_of_charpoly _ _ _ _ _ _ hr
  · simpa only [LinearMap.charpoly_baseChange, hchar, Polynomial.map_mul]
  · have h := congrArg (Polynomial.map (algebraMap R K)) hbez
    simpa only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_C] using h

theorem mapped_resultant_nonzero (f g : R[X]) (hf : f.Monic) (hg : g.Monic)
    (hc : IsCoprime (f.map (algebraMap R K)) (g.map (algebraMap R K))) :
    algebraMap R K (f.resultant g) ≠ 0 := by
  have h := resultant_nonzero_of_coprime _ _ hc
  simpa only [hf.natDegree_map, hg.natDegree_map,
    Polynomial.resultant_map_map] using h

end IntegralBaseChange

end Komorebi.PaperII.ReleaseResultantPolynomial
