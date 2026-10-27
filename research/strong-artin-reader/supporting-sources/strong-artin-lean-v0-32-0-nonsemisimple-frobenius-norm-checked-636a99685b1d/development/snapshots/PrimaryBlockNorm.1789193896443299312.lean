import NilpotentPolynomialImage
import Mathlib.Algebra.Polynomial.Derivative

/-! Exact norm image on an arbitrary nilpotent primary block, including resonant
nontrivial eigenvalues. The degree is m*p^a with m nonzero in k. -/
noncomputable section
namespace Komorebi.StrongArtin.NonsemisimpleNorm
open Polynomial
open scoped BigOperators
variable {k V : Type*} [Field k] [AddCommGroup V] [Module k V]

@[simp] theorem normPolynomial_eval (lam : k) (m : ℕ) :
    (normPolynomial k m).eval lam = ∑ j ∈ Finset.range m, lam^j := by
  simp [normPolynomial]

@[simp] theorem normPolynomial_eval_one (m : ℕ) :
    (normPolynomial k m).eval 1 = (m : k) := by
  simp [normPolynomial]

theorem normPolynomial_eval_zero_of_root (lam : k) (m : ℕ)
    (hl : lam ≠ 1) (hroot : lam^m = 1) : (normPolynomial k m).eval lam = 0 := by
  have h := congrArg (Polynomial.eval lam) (normPolynomial_mul_X_sub_one (k := k) m)
  simp only [eval_mul, eval_sub, eval_X, eval_one, eval_pow, hroot, sub_self] at h
  exact (mul_eq_zero.mp h).resolve_right (sub_ne_zero.mpr hl)

theorem normPolynomial_eval_ne_zero (lam : k) (m : ℕ) (hm : (m : k) ≠ 0)
    (hn : lam = 1 ∨ lam^m ≠ 1) : (normPolynomial k m).eval lam ≠ 0 := by
  rcases hn with rfl | hn
  · simpa using hm
  · intro hzero
    have h := congrArg (Polynomial.eval lam) (normPolynomial_mul_X_sub_one (k := k) m)
    simp only [eval_mul, eval_sub, eval_X, eval_one, eval_pow, hzero, zero_mul] at h
    exact hn (sub_eq_zero.mp h.symm)

/-- Each nontrivial m-th root is a simple zero of the geometric norm when m is a unit. -/
theorem normPolynomial_simple_root_factor (lam : k) (m : ℕ)
    (hl0 : lam ≠ 0) (hl1 : lam ≠ 1) (hroot : lam^m = 1) (hm : (m : k) ≠ 0) :
    ∃ g : k[X], normPolynomial k m = (X - C lam) * g ∧ g.eval lam ≠ 0 := by
  have hz := normPolynomial_eval_zero_of_root lam m hl1 hroot
  obtain ⟨g, hg⟩ := (dvd_iff_isRoot (a := lam) (p := normPolynomial k m)).mpr hz
  refine ⟨g, hg, ?_⟩
  have hd := congrArg (fun f : k[X] => f.derivative.eval lam)
    (normPolynomial_mul_X_sub_one (k := k) m)
  simp only [derivative_mul, derivative_sub, derivative_X, derivative_one,
    derivative_pow, eval_add, eval_mul, eval_sub, eval_one, eval_zero,
    eval_X, eval_pow, eval_natCast, sub_zero, mul_one, hz, add_zero] at hd
  have hder : (normPolynomial k m).derivative.eval lam = g.eval lam := by
    rw [hg]
    simp
  rw [hder] at hd
  intro hg0
  rw [hg0, zero_mul] at hd
  exact (mul_ne_zero hm (pow_ne_zero _ hl0)) hd.symm

/-- Multiplicity of the norm zero on a lambda-primary block. -/
def resonanceExponent (m p a : ℕ) (lam : k) : ℕ :=
  if lam = 1 then p^a - 1 else if lam^m = 1 then p^a else 0

theorem normPolynomial_exact_root_factor (m p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hm : (m : k) ≠ 0) (lam : k) (hl : lam ≠ 0) :
    ∃ g : k[X], normPolynomial k (m*p^a) =
      (X - C lam)^(resonanceExponent m p a lam) * g ∧ g.eval lam ≠ 0 := by
  by_cases h1 : lam = 1
  · subst lam
    refine ⟨normPolynomial k m ^ (p^a), ?_, ?_⟩
    · simpa [resonanceExponent] using normPolynomial_mixed_degree (k := k) m p a
    · simpa using pow_ne_zero (p^a) hm
  · by_cases hr : lam^m = 1
    · obtain ⟨g, hg, hge⟩ := normPolynomial_simple_root_factor lam m hl h1 hr hm
      refine ⟨(X-1)^(p^a-1)*g^(p^a), ?_, ?_⟩
      · rw [normPolynomial_mixed_degree, hg, mul_pow]
        simp only [resonanceExponent, h1, hr, if_false, if_true]
        ring
      · simpa using mul_ne_zero (pow_ne_zero (p^a-1) (sub_ne_zero.mpr h1))
          (pow_ne_zero (p^a) hge)
    · refine ⟨normPolynomial k (m*p^a), ?_, ?_⟩
      · simp [resonanceExponent, h1, hr]
      · rw [normPolynomial_mixed_degree]
        simp only [eval_mul, eval_pow, eval_sub, eval_X, eval_one]
        exact mul_ne_zero (pow_ne_zero _ (sub_ne_zero.mpr h1))
          (pow_ne_zero _ (normPolynomial_eval_ne_zero lam m hm (Or.inr hr)))

/-- The full Jordan-primary image and kernel criterion for every positive degree. -/
theorem primary_norm_range_ker (T : Module.End k V) (lam : k)
    (hN : IsNilpotent (T - algebraMap k (Module.End k V) lam))
    (m p a : ℕ) [Fact (Nat.Prime p)] [CharP k p]
    (hm : (m : k) ≠ 0) (hl : lam ≠ 0) :
    LinearMap.range (operatorNorm T (m*p^a)) =
      LinearMap.range ((T - algebraMap k (Module.End k V) lam)^resonanceExponent m p a lam) ∧
    LinearMap.ker (operatorNorm T (m*p^a)) =
      LinearMap.ker ((T - algebraMap k (Module.End k V) lam)^resonanceExponent m p a lam) := by
  obtain ⟨g, hf, hg⟩ := normPolynomial_exact_root_factor m p a hm lam hl
  simpa using aeval_range_ker_of_root_factor T lam hN
    (normPolynomial k (m*p^a)) g (resonanceExponent m p a lam) hf hg

end Komorebi.StrongArtin.NonsemisimpleNorm
