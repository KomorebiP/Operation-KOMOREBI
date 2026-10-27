import PaperIRelease.PolynomialModule
set_option autoImplicit false
noncomputable section
open Polynomial
namespace Komorebi.PaperIRelease.PolynomialModule
universe u v
variable (k : Type u) [Field k]
abbrev MonicIrreducibles := {p : k[X] // p.Monic ∧ Irreducible p}
def monicToSpec (p : MonicIrreducibles k) : IsDedekindDomain.HeightOneSpectrum k[X] where
  asIdeal := Ideal.span {p.val}
  isPrime := Ideal.isPrime_span_singleton_of_prime p.property.2.prime
  ne_bot := fun h => p.property.2.ne_zero (Ideal.span_singleton_eq_bot.mp h)

theorem monicToSpec_injective : Function.Injective (monicToSpec k) := by
  intro p q hpq
  apply Subtype.ext
  apply Polynomial.eq_of_monic_of_associated p.property.1 q.property.1
  apply Ideal.span_singleton_eq_span_singleton.mp
  exact congrArg IsDedekindDomain.HeightOneSpectrum.asIdeal hpq

theorem monicToSpec_surjective : Function.Surjective (monicToSpec k) := by
  classical
  intro P
  obtain ⟨p, hp, hP⟩ := (Ideal.isPrime_iff_of_isPrincipalIdealRing P.ne_bot).mp P.isPrime
  let q : MonicIrreducibles k := ⟨normalize p, Polynomial.monic_normalize hp.ne_zero,
    (normalize_associated p).irreducible_iff.mpr hp.irreducible⟩
  refine ⟨q, IsDedekindDomain.HeightOneSpectrum.ext ?_⟩
  change Ideal.span {normalize p} = P.asIdeal
  rw [hP]
  exact Ideal.span_singleton_eq_span_singleton.mpr (normalize_associated p)

def monicSpectrumEquiv : MonicIrreducibles k ≃ IsDedekindDomain.HeightOneSpectrum k[X] :=
  Equiv.ofBijective (monicToSpec k) ⟨monicToSpec_injective k, monicToSpec_surjective k⟩

variable (M : Type v) [AddCommGroup M] [Module k M] [Module k[X] M]
  [IsScalarTower k k[X] M]
open Komorebi.PaperICompletion4.IntrinsicPrimary
local instance : DecidableEq (MonicIrreducibles k) := Classical.decEq _
theorem monic_primary_internal_decomposition [FiniteDimensional k M] :
    DirectSum.IsInternal (fun p : MonicIrreducibles k => primarySubmodule M p.val) := by
  have hfamily : (fun p : MonicIrreducibles k => primarySubmodule M p.val) =
      (fun p : MonicIrreducibles k => (monicToSpec k p).asIdeal.primaryComponent M) := by
    funext p
    exact primarySubmodule_eq_idealPrimary M p.val
  rw [hfamily]
  apply DirectSum.isInternal_submodule_of_iSupIndep_of_iSup_eq_top
  · exact (Ideal.iSupIndep_primaryComponent k[X] M).comp (monicToSpec_injective k)
  · exact ((monicToSpec_surjective k).iSup_comp
      (fun P : IsDedekindDomain.HeightOneSpectrum k[X] => P.asIdeal.primaryComponent M)).trans
      (Ideal.iSup_primaryComponent_eq_top (polynomialModule_isTorsion k M))

theorem finitely_many_monic_primary_components [FiniteDimensional k M] :
    Set.Finite {p : MonicIrreducibles k | primarySubmodule M p.val ≠ ⊥} := by
  let : IsNoetherian k[X] M := isNoetherian_of_tower k (inferInstance : IsNoetherian k M)
  apply Submodule.finite_ne_bot_of_iSupIndep
  have h := (Ideal.iSupIndep_primaryComponent k[X] M).comp (monicToSpec_injective k)
  change iSupIndep (fun p : MonicIrreducibles k => (Ideal.span {p.val}).primaryComponent M) at h
  simpa only [primarySubmodule_eq_idealPrimary] using h
end Komorebi.PaperIRelease.PolynomialModule
#print axioms Komorebi.PaperIRelease.PolynomialModule.monic_primary_internal_decomposition
#print axioms Komorebi.PaperIRelease.PolynomialModule.finitely_many_monic_primary_components
