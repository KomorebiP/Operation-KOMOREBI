import PaperICompletion4.OperatorIntrinsicFormula
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperIRelease.PolynomialModule
open Polynomial
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.PaperICompletion4.IntrinsicPrimary Komorebi.PaperICompletion4.GroupedPrimary
universe u v
variable (k : Type u) [Field k] (M : Type v) [AddCommGroup M]
variable [Module k M] [Module k[X] M] [IsScalarTower k k[X] M]

/-- Multiplication by X in an existing polynomial module. -/
def variableAction : Module.End k M where
  toFun m := (X : k[X]) • m
  map_add' := smul_add _
  map_smul' c m := by
    change (X : k[X]) • (c • m) = c • ((X : k[X]) • m)
    exact smul_comm _ _ _

/-- Every pre-existing polynomial-module action is its variable-action evaluation module. -/
def evaluationEquiv : Module.AEval' (variableAction k M) ≃ₗ[k[X]] M :=
  LinearEquiv.ofAEval (variableAction k M) (LinearEquiv.refl k M) (fun _ => rfl)

/-- Finite-dimensional existing polynomial modules are torsion. -/
theorem polynomialModule_isTorsion [FiniteDimensional k M] : Module.IsTorsion k[X] M := by
  intro m
  obtain ⟨p, hp⟩ := operatorModule_isTorsion (variableAction k M)
    (x := (evaluationEquiv k M).symm m)
  refine ⟨p, ?_⟩
  change (p : k[X]) • (evaluationEquiv k M).symm m = 0 at hp
  change (p : k[X]) • m = 0
  have h := congrArg (evaluationEquiv k M) hp
  rw [(evaluationEquiv k M).map_smul, LinearEquiv.apply_symm_apply, map_zero] at h
  exact h

/-- Positive elementary divisors for the existing module, without a supplied operator presentation. -/
theorem exists_positive_primary_decomposition [FiniteDimensional k M] :
    ∃ (ι : Type u) (_ : Fintype ι) (p : ι → k[X])
      (_ : ∀ i, Irreducible (p i)) (e : ι → ℕ) (_ : ∀ i, 0 < e i),
      Nonempty (M ≃ₗ[k[X]] ((i : ι) → k[X] ⧸ Ideal.span {p i ^ e i})) := by
  obtain ⟨ι, hι, p, hp, e, he, ⟨f⟩⟩ := exists_positive_primaryProduct_equiv (variableAction k M)
  exact ⟨ι, hι, p, hp, e, he, ⟨(evaluationEquiv k M).symm.trans f⟩⟩

local instance : DecidableEq (IsDedekindDomain.HeightOneSpectrum k[X]) := Classical.decEq _

/-- The actual ideal-primary subspaces sum internally to the given module. -/
theorem primary_internal_decomposition [FiniteDimensional k M] :
    DirectSum.IsInternal (fun p : IsDedekindDomain.HeightOneSpectrum k[X] => p.asIdeal.primaryComponent M) := by
  apply DirectSum.isInternal_submodule_of_iSupIndep_of_iSup_eq_top
  · exact Ideal.iSupIndep_primaryComponent k[X] M
  · exact Ideal.iSup_primaryComponent_eq_top (polynomialModule_isTorsion k M)

/-- Only finitely many intrinsic prime-ideal components are nonzero. -/
theorem finitely_many_primary_components [FiniteDimensional k M] :
    Set.Finite {p : IsDedekindDomain.HeightOneSpectrum k[X] |
      p.asIdeal.primaryComponent M ≠ ⊥} := by
  let : IsNoetherian k[X] M := isNoetherian_of_tower k (inferInstance : IsNoetherian k M)
  exact Submodule.finite_ne_bot_of_iSupIndep (Ideal.iSupIndep_primaryComponent k[X] M)

/-- Every intrinsic primary component has the matching finite elementary-divisor presentation. -/
theorem exists_grouped_primary_decomposition [FiniteDimensional k M] :
    ∃ (ι : Type u) (_ : Fintype ι) (q : ι → k[X])
      (_ : ∀ i, Irreducible (q i)) (e : ι → ℕ) (_ : ∀ i, 0 < e i),
      ∀ p : k[X], Irreducible p → Nonempty
        (primarySubmodule M p ≃ₗ[k[X]]
          ((i : {i : ι // Ideal.span {q i} = Ideal.span {p}}) →
            k[X] ⧸ Ideal.span {q i.val ^ e i.val})) := by
  obtain ⟨ι, hι, q, hq, e, he, ⟨f⟩⟩ := exists_positive_primary_decomposition k M
  exact ⟨ι, hι, q, hq, e, he, fun p hp =>
    ⟨(primaryCongr p f).trans (groupedPrimaryEquiv q hq e p hp)⟩⟩


/-- Literal finite direct-sum presentation by powers of the specified irreducible. -/
theorem intrinsic_primary_finite_power_sum [FiniteDimensional k M]
    (p : k[X]) (hp : Irreducible p) :
    ∃ (ι : Type u) (_ : Fintype ι) (e : ι → ℕ), (∀ i, 0 < e i) ∧
      Nonempty (primarySubmodule M p ≃ₗ[k[X]]
        DirectSum ι (fun i => k[X] ⧸ Ideal.span {p ^ e i})) := by
  classical
  obtain ⟨ι, hι, q, hq, e, he, hcomponents⟩ := exists_grouped_primary_decomposition k M
  let J := {i : ι // Ideal.span {q i} = Ideal.span {p}}
  let f (i : J) : (k[X] ⧸ Ideal.span {q i.val ^ e i.val}) ≃ₗ[k[X]]
      (k[X] ⧸ Ideal.span {p ^ e i.val}) := Submodule.quotEquivOfEq _ _ (by
        simpa only [Ideal.span_singleton_pow] using
          congrArg (fun I : Ideal k[X] => I ^ e i.val) i.property)
  refine ⟨J, inferInstance, fun i => e i.val, fun i => he i.val, ?_⟩
  exact ⟨((hcomponents p hp).some.trans (LinearEquiv.piCongrRight f)).trans
    (DirectSum.linearEquivFunOnFintype k[X] J _).symm⟩

end Komorebi.PaperIRelease.PolynomialModule
