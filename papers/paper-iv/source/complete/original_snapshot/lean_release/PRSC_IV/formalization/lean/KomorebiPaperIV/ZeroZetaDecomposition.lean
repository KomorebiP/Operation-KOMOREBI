/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroLatticeComparison

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem tsum_injection_add_complement {α β : Type*} (i : α → β)
    (hi : Function.Injective i) {f : β → ℂ} (hf : Summable f) :
    (∑' a, f (i a)) + (∑' b : ↥((range i)ᶜ), f b) = ∑' b, f b := by
  rw [← tsum_range f hi]
  exact (hf.subtype (range i)).tsum_add_tsum_compl (hf.subtype (range i)ᶜ)

theorem finite_subtype_tsum_entire {α : Type*} {S : Set α} (hS : S.Finite)
    (f : α → ℂ → ℂ) (hf : ∀ a, Differentiable ℂ (f a)) :
    Differentiable ℂ (fun s => ∑' a : S, f a s) := by
  classical
  let := hS.fintype
  simp only [tsum_fintype]
  exact Differentiable.fun_sum (fun a _ => hf a)

def SignedZeroEnumeration.reducedExceptionZeta {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) (s : ℂ) : ℂ :=
  ∑' z : ↥((range (e.reducedZero hn))ᶜ), absoluteZeroZetaTerm (entireReducedDenominator N) z.val s

def SignedZeroEnumeration.absoluteExceptionZeta {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) (s : ℂ) : ℂ :=
  ∑' z : ↥((range (e.orbitZero hn))ᶜ), absoluteZeroZetaTerm (canonicalSignedDenominator N) z.val s

theorem absoluteZeroZetaTerm_entire (f : ℂ → ℂ) (z : {z : ℂ // f z = 0}) :
    Differentiable ℂ (absoluteZeroZetaTerm f z) := by
  unfold absoluteZeroZetaTerm
  exact weightedDirichletTerm_differentiable _ _ z

theorem SignedZeroEnumeration.reducedExceptionZeta_entire {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) : Differentiable ℂ (e.reducedExceptionZeta hn) :=
  finite_subtype_tsum_entire (e.reducedZero_finite_complement hn) _
    (absoluteZeroZetaTerm_entire _)

theorem SignedZeroEnumeration.absoluteExceptionZeta_entire {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) : Differentiable ℂ (e.absoluteExceptionZeta hn) :=
  finite_subtype_tsum_entire (e.orbitZero_finite_complement hn) _
    (absoluteZeroZetaTerm_entire _)

theorem SignedZeroEnumeration.reducedZetaTerm {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) (m : ℕ) (s : ℂ) :
    absoluteZeroZetaTerm (entireReducedDenominator N) (e.reducedZero hn m) s =
      positiveZetaTerm (e.root m) ((N : ℂ) * s) := by
  simp only [absoluteZeroZetaTerm, weightedDirichletTerm, SignedZeroEnumeration.reducedZero,
    (e.reducedRoot_zero_simple hn m).2, Nat.cast_one, one_mul, e.reducedRoot_norm,
    Real.log_pow, positiveZetaTerm]
  push_cast
  congr 1
  ring

theorem SignedZeroEnumeration.orbitZetaTerm {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) (p : Fin N × ℕ) (s : ℂ) :
    absoluteZeroZetaTerm (canonicalSignedDenominator N) (e.orbitZero hn p) s =
      positiveZetaTerm (e.root p.2) s := by
  simp only [absoluteZeroZetaTerm, weightedDirichletTerm, SignedZeroEnumeration.orbitZero,
    (e.orbit_zero_simple hn p).2, Nat.cast_one, one_mul, e.orbit_norm hn, positiveZetaTerm]

theorem SignedZeroEnumeration.reducedZeta_decomposition {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {s : ℂ} (hs : 1 / (N : ℝ) < s.re) :
    absoluteZeroZeta (entireReducedDenominator N) s =
      (∑' m, positiveZetaTerm (e.root m) ((N : ℂ) * s)) +
        e.reducedExceptionZeta (by omega) s := by
  have hsum := ((entireReducedDenominator_zeta_absolute_convergence hN s).mpr hs).of_norm
  have h := tsum_injection_add_complement (e.reducedZero (by omega))
    (e.reducedZero_injective (by omega)) hsum
  simpa only [e.reducedZetaTerm, absoluteZeroZeta, SignedZeroEnumeration.reducedExceptionZeta] using h.symm

theorem SignedZeroEnumeration.absoluteZeta_decomposition {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) {s : ℂ} (hs : 1 < s.re) :
    absoluteZeroZeta (canonicalSignedDenominator N) s =
      (N : ℂ) * (∑' m, positiveZetaTerm (e.root m) s) +
        e.absoluteExceptionZeta (by omega) s := by
  have hsum := ((canonicalSignedDenominator_zeta_absolute_convergence hN s).mpr hs).of_norm
  have h := tsum_injection_add_complement (e.orbitZero (by omega))
    (e.orbitZero_injective (by omega)) hsum
  have hp := hsum.comp_injective (e.orbitZero_injective (by omega))
  have hprod := hp.tsum_prod
  simp only [Function.comp_apply] at hprod
  erw [hprod] at h
  simpa only [Function.comp_apply, e.orbitZetaTerm, tsum_fintype, Finset.sum_const,
    Finset.card_univ, Fintype.card_fin, nsmul_eq_mul, absoluteZeroZeta,
    SignedZeroEnumeration.absoluteExceptionZeta] using h.symm

end
end Komorebi.PaperIV
