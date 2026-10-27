import KomorebiVerification.PaperII.ResultantSeparation
import Mathlib.LinearAlgebra.Charpoly.Basic
import Mathlib.LinearAlgebra.Charpoly.BaseChange

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

end Komorebi.PaperII.ReleaseResultantPolynomial
