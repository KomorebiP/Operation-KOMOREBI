import PaperICompletion.CyclicClassification
import Mathlib.Algebra.Polynomial.Module.FiniteDimensional
import Mathlib.RingTheory.Ideal.Quotient.Operations

/-!
# General polynomial-module seed formula: primary products

The actual polynomial module is decomposed by the proved PID structure theorem.
Chinese remainder coefficients construct shared generators across coprime blocks.
Residue fields, rather than base-field eigenvalues, supply the lower bounds.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperICompletion3.PrimarySeedFormula

open Polynomial
open Komorebi.SeedRankBasics

universe u v w

/-- The actual polynomial module of a finite-dimensional operator is torsion. -/
theorem operatorModule_isTorsion {k : Type u} [Field k]
    {V : Type v} [AddCommGroup V] [Module k V] [FiniteDimensional k V]
    (T : Module.End k V) : Module.IsTorsion k[X] (Module.AEval' T) :=
  Module.AEval.isTorsion_of_finiteDimensional k V T

/-- Primary blocks are constructed from the operator, not supplied by the caller.
Exponent-zero summands are allowed by the upstream normal form and are zero modules. -/
theorem exists_primaryProduct_equiv {k : Type u} [Field k]
    {V : Type v} [AddCommGroup V] [Module k V] [FiniteDimensional k V]
    (T : Module.End k V) :
    ∃ (ι : Type u) (_ : Fintype ι) (p : ι → k[X])
      (_ : ∀ i, Irreducible (p i)) (e : ι → ℕ),
      Nonempty (Module.AEval' T ≃ₗ[k[X]]
        ((i : ι) → k[X] ⧸ Ideal.span {p i ^ e i})) := by
  obtain ⟨ι, hι, p, hp, e, ⟨f⟩⟩ := Module.equiv_directSum_of_isTorsion
    (operatorModule_isTorsion T)
  exact ⟨ι, hι, p, hp, e, ⟨f.trans DFinsupp.linearEquivFunOnFintype⟩⟩

section ResidueLowerBound
variable {R : Type u} [CommRing R]
variable {M : Type v} [AddCommGroup M] [Module R M]
variable {K : Type w} [Field K] [Algebra R K]
variable {Y : Type*} [AddCommGroup Y] [Module K Y] [Module R Y]
  [IsScalarTower R K Y]

/-- Every surjective residue-field factor bounds the number of module generators.
The residue extension may have degree greater than one over the original base field. -/
theorem residue_finrank_le_card_of_generates {ι : Type*} [Fintype ι]
    (f : M →ₗ[R] Y) (hf : Function.Surjective f)
    (s : ι → M) (hs : FamilyGenerates R M s) :
    Module.finrank K Y ≤ Fintype.card ι := by
  have hspanR : Submodule.span R (Set.range (fun i ↦ f (s i))) = ⊤ := by
    rw [show Set.range (fun i ↦ f (s i)) = f '' Set.range s from Set.range_comp f s,
      ← Submodule.map_span, hs, Submodule.map_top, LinearMap.range_eq_top.mpr hf]
  have hspanK : Submodule.span K (Set.range (fun i ↦ f (s i))) = ⊤ := by
    apply top_unique
    intro y _
    have hy : y ∈ Submodule.span R (Set.range (fun i ↦ f (s i))) := by rw [hspanR]; trivial
    exact Submodule.span_le_restrictScalars R K _ hy
  exact finrank_le_of_span_eq_top (R := K) hspanK
end ResidueLowerBound

section ChineseRemainderGenerators
variable {R : Type u} [CommRing R]
variable {ι : Type v} [Fintype ι]

/-- One vector per color, supported exactly on blocks of that color. -/
def coloredSeeds (I : ι → Ideal R) {r : ℕ} (color : ι → Fin r)
    (j : Fin r) : (i : ι) → R ⧸ I i :=
  fun i ↦ if color i = j then 1 else 0

/-- Blocks sharing a color may share one seed exactly because their
quotient ideals are pairwise coprime. The CRT coefficients are constructed. -/
theorem coloredSeeds_generate (I : ι → Ideal R) {r : ℕ} (color : ι → Fin r)
    (hcoprime : ∀ i j, i ≠ j → color i = color j → IsCoprime (I i) (I j)) :
    FamilyGenerates R ((i : ι) → R ⧸ I i) (coloredSeeds I color) := by
  classical
  apply top_unique
  intro x _
  have hex : ∀ j : Fin r, ∃ a : R,
      ∀ i : {i : ι // color i = j}, Ideal.Quotient.mk (I i) a = x i := by
    intro j
    apply Ideal.pi_quotient_surjective
    intro i i' hne
    exact hcoprime i i' (fun h ↦ hne (Subtype.ext h)) (i.property.trans i'.property.symm)
  choose a ha using hex
  have hsum : ∑ j : Fin r, a j • coloredSeeds I color j = x := by
    funext i
    simp only [Finset.sum_apply, Pi.smul_apply, coloredSeeds]
    simp only [smul_ite, smul_zero]
    simpa [Algebra.smul_def] using ha (color i) ⟨i, rfl⟩
  rw [← hsum]
  exact Submodule.sum_mem _ fun j _ ↦ Submodule.smul_mem _ _
    (Submodule.subset_span (Set.mem_range_self j))
end ChineseRemainderGenerators

section FiberColors
variable {ι : Type u} [Fintype ι] {Λ : Type v}

/-- Number of blocks carrying a specified primary label. -/
def fiberMultiplicity (label : ι → Λ) (a : Λ) : ℕ :=
  by
  classical
  exact Fintype.card {i : ι // label i = a}

/-- Maximum fiber multiplicity, including the empty family with maximum zero. -/
def maxMultiplicity (label : ι → Λ) : ℕ :=
  Finset.univ.sup fun i ↦ fiberMultiplicity label (label i)

theorem fiberMultiplicity_le_max (label : ι → Λ) (i : ι) :
    fiberMultiplicity label (label i) ≤ maxMultiplicity label :=
  Finset.le_sup (f := fun i ↦ fiberMultiplicity label (label i)) (Finset.mem_univ i)

/-- Rank a block within its own primary fiber. -/
def fiberColor (label : ι → Λ) (i : ι) : Fin (maxMultiplicity label) := by
  classical
  exact ⟨(Fintype.equivFin {j : ι // label j = label i}) ⟨i, rfl⟩,
    lt_of_lt_of_le (Fin.isLt _) (fiberMultiplicity_le_max label i)⟩

/-- Distinct blocks in the same primary fiber receive distinct colors. -/
theorem fiberColor_injective_on_fiber (label : ι → Λ) {i j : ι}
    (hlabel : label i = label j) (hcolor : fiberColor label i = fiberColor label j) : i = j := by
  classical
  have hval := congrArg Fin.val hcolor
  simp only [fiberColor] at hval
  have transport (a b : Λ) (h : a = b) (z : ι) (hz : label z = a) :
      ((Fintype.equivFin {x : ι // label x = a}) ⟨z, hz⟩).val =
      ((Fintype.equivFin {x : ι // label x = b}) ⟨z, hz.trans h⟩).val := by
    subst b
    rfl
  have hcolor' :
      (Fintype.equivFin {z : ι // label z = label i}) ⟨i, rfl⟩ =
      (Fintype.equivFin {z : ι // label z = label i}) ⟨j, hlabel.symm⟩ := by
    apply Fin.ext
    exact hval.trans (transport (label j) (label i) hlabel.symm j rfl)
  exact congrArg Subtype.val ((Fintype.equivFin _).injective hcolor')
end FiberColors

section QuotientFibers
variable {R : Type u} [CommRing R]
variable {ι : Type v} [Fintype ι]

/-- The literal quotient map onto all blocks with a selected residue ideal. -/
def residueFiberMap (I P : ι → Ideal R) (hIP : ∀ i, I i ≤ P i) (a : Ideal R) :
    ((i : ι) → R ⧸ I i) →ₗ[R] ({i : ι // P i = a} → R ⧸ a) :=
  LinearMap.pi fun i ↦
    (Ideal.Quotient.factorₐ R ((hIP i).trans_eq i.property)).toLinearMap.comp
      (LinearMap.proj i.val)

/-- Every residue-fiber map is onto, including empty fibers. -/
theorem residueFiberMap_surjective (I P : ι → Ideal R)
    (hIP : ∀ i, I i ≤ P i) (a : Ideal R) :
    Function.Surjective (residueFiberMap I P hIP a) := by
  classical
  intro y
  have hex : ∀ i : {i : ι // P i = a}, ∃ x : R ⧸ I i,
      Ideal.Quotient.factor ((hIP i).trans_eq i.property) x = y i := by
    intro i
    exact Ideal.Quotient.factor_surjective _ (y i)
  choose x hx using hex
  refine ⟨fun i ↦ if h : P i = a then x ⟨i, h⟩ else 0, ?_⟩
  ext i
  simpa [residueFiberMap, i.property] using hx i

/-- A primary residue fiber requires at least its own number of generators. -/
theorem fiberMultiplicity_le_of_generates (I P : ι → Ideal R)
    (hIP : ∀ i, I i ≤ P i) (a : Ideal R) [a.IsMaximal]
    {κ : Type*} [Fintype κ] (s : κ → ((i : ι) → R ⧸ I i))
    (hs : FamilyGenerates R ((i : ι) → R ⧸ I i) s) :
    fiberMultiplicity P a ≤ Fintype.card κ := by
  classical
  letI : Field (R ⧸ a) := Ideal.Quotient.field a
  have h := residue_finrank_le_card_of_generates (K := R ⧸ a)
    (residueFiberMap I P hIP a) (residueFiberMap_surjective I P hIP a) s hs
  simpa [fiberMultiplicity, Module.finrank_pi] using h

/-- Exact generator count for finite products of primary quotients.
All residue lower bounds and the simultaneous CRT upper bound are proved here. -/
theorem primaryProduct_seedNumber_isLeast (I P : ι → Ideal R)
    (hIP : ∀ i, I i ≤ P i) (hmax : ∀ i, (P i).IsMaximal)
    (hcoprime : ∀ i j, P i ≠ P j → IsCoprime (I i) (I j)) :
    IsLeast {r : ℕ | ∃ s : Fin r → ((i : ι) → R ⧸ I i),
      FamilyGenerates R ((i : ι) → R ⧸ I i) s} (maxMultiplicity P) := by
  classical
  constructor
  · refine ⟨coloredSeeds I (fiberColor P), coloredSeeds_generate I (fiberColor P) ?_⟩
    intro i j hne hc
    exact hcoprime i j (fun he ↦ hne (fiberColor_injective_on_fiber P he hc))
  · rintro r ⟨s, hs⟩
    apply Finset.sup_le
    intro i _
    letI : (P i).IsMaximal := hmax i
    simpa using fiberMultiplicity_le_of_generates I P hIP (P i) s hs
end QuotientFibers

section PrimePowers
variable {R : Type u} [CommRing R] [IsDomain R] [IsPrincipalIdealRing R]
variable {ι : Type v} [Fintype ι]

/-- Distinct irreducible principal ideals have coprime powers. -/
theorem coprime_primePower_ideals (p q : R) (hp : Irreducible p) (hq : Irreducible q)
    (hneq : Ideal.span {p} ≠ Ideal.span {q}) (m n : ℕ) :
    IsCoprime (Ideal.span {p ^ m}) (Ideal.span {q ^ n}) := by
  apply (Ideal.isCoprime_span_singleton_iff _ _).mpr
  apply IsCoprime.pow
  apply hp.coprime_iff_not_dvd.mpr
  intro hdiv
  exact hneq (Ideal.span_singleton_eq_span_singleton.mpr
    ((hp.associated_of_dvd hq hdiv)))

/-- Positive exponent prime-power quotients have the exact maximum-primary-fiber seed number. -/
theorem primePowerProduct_seedNumber_isLeast (p : ι → R) (hp : ∀ i, Irreducible (p i))
    (e : ι → ℕ) (he : ∀ i, 0 < e i) :
    IsLeast {r : ℕ | ∃ s : Fin r → ((i : ι) → R ⧸ Ideal.span {p i ^ e i}),
      FamilyGenerates R ((i : ι) → R ⧸ Ideal.span {p i ^ e i}) s}
      (maxMultiplicity fun i ↦ Ideal.span {p i}) := by
  apply primaryProduct_seedNumber_isLeast
    (fun i ↦ Ideal.span {p i ^ e i}) (fun i ↦ Ideal.span {p i})
  · intro i
    exact Ideal.span_singleton_le_span_singleton.mpr (dvd_pow_self _ (Nat.ne_of_gt (he i)))
  · intro i
    exact PrincipalIdealRing.isMaximal_of_irreducible (hp i)
  · intro i j hne
    exact coprime_primePower_ideals (p i) (p j) (hp i) (hp j) hne (e i) (e j)
end PrimePowers

end Komorebi.PaperICompletion3.PrimarySeedFormula
