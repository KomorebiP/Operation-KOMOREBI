import PaperICompletion4.GroupedPrimary

/-! # Intrinsic primary multiplicities of the actual operator
Each primary multiplicity is the residue-field dimension of X_p/p(T)X_p.
It is identified with each presentation fibre, not just their maximum.
-/
set_option autoImplicit false
noncomputable section
open scoped Pointwise
namespace Komorebi.PaperICompletion4.OperatorIntrinsicFormula
open Polynomial
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.PaperICompletion3.OperatorPrimaryAPI
open Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion4.GroupedPrimary
open Komorebi.SeedRankBasics
universe u v
variable {k : Type u} [Field k]
variable {V : Type v} [AddCommGroup V] [Module k V]

/-- The literal intrinsic quotient of the actual polynomial module. -/
abbrev IntrinsicPrimaryQuotient (T : Module.End k V) (p : k[X]) :=
  ScalarQuotient (primarySubmodule (Module.AEval' T) p) p

/-- Intrinsic multiplicity is residue-field dimension, not base-field dimension. -/
def intrinsicMultiplicity (T : Module.End k V) (p : k[X]) : ℕ :=
  Module.finrank (k[X] ⧸ Ideal.span {p}) (IntrinsicPrimaryQuotient T p)

/-- The underlying primary condition is the paper's actual p(T)-annihilation condition. -/
theorem operator_primary_membership (T : Module.End k V) (p : k[X]) (x : V) :
    Module.AEval'.of T x ∈ primarySubmodule (Module.AEval' T) p ↔
      ∃ n : ℕ, ((aeval T p) ^ n) x = 0 := by
  change (∃ n : ℕ, ((aeval T) (p ^ n)) x = 0) ↔ _
  simp only [map_pow]

/-- Scalar-image membership agrees with the literal image of p(T) on V. -/
theorem operator_scalarImage_membership (T : Module.End k V) (p : k[X]) (x : V) :
    Module.AEval'.of T x ∈ p • (⊤ : Submodule k[X] (Module.AEval' T)) ↔
      ∃ y : V, (aeval T p) y = x := by
  rw [mem_scalarImage_iff]
  rfl

/-- The grouped elementary divisors are the actual intrinsic primary component. -/
def operatorPrimaryComponentEquiv {T : Module.End k V} (D : PrimaryPresentation T)
    (p : k[X]) (hp : Irreducible p) :
    primarySubmodule (Module.AEval' T) p ≃ₗ[k[X]]
      ((i : {i : D.Index // D.label i = Ideal.span {p}}) →
        k[X] ⧸ Ideal.span {D.prime i ^ D.exponent i}) :=
  (primaryCongr p D.equiv).trans (groupedPrimaryEquiv D.prime D.irreducible D.exponent p hp)

/-- Any actual primary presentation identifies the intrinsic quotient with its residue fibre. -/
def operatorPrimaryQuotientEquiv [FiniteDimensional k V]
    {T : Module.End k V} (D : PrimaryPresentation T) (p : k[X]) (hp : Irreducible p) :
    IntrinsicPrimaryQuotient T p ≃ₗ[k[X] ⧸ Ideal.span {p}]
      ({i : D.Index // D.label i = Ideal.span {p}} → k[X] ⧸ Ideal.span {p}) := by
  let : IsArtinian k[X] (Module.AEval' T) := isArtinian_of_tower k inferInstance
  exact (primaryQuotientEquivGlobal (Module.AEval' T) p).trans
    ((scalarQuotientCongr p D.equiv).trans
      (primaryProductQuotientEquiv D.prime D.irreducible D.exponent D.positive p hp))

/-- The intrinsic dimension equals the number of blocks in each primary fibre. -/
theorem intrinsicMultiplicity_eq_fiber [FiniteDimensional k V]
    {T : Module.End k V} (D : PrimaryPresentation T) (p : k[X]) (hp : Irreducible p) :
    intrinsicMultiplicity T p = fiberMultiplicity D.label (Ideal.span {p}) := by
  classical
  let : (Ideal.span {p}).IsMaximal := PrincipalIdealRing.isMaximal_of_irreducible hp
  let : Field (k[X] ⧸ Ideal.span {p}) := Ideal.Quotient.field _
  have h := (operatorPrimaryQuotientEquiv D p hp).finrank_eq
  simpa [intrinsicMultiplicity, fiberMultiplicity, Module.finrank_pi,
    ← Nat.card_eq_fintype_card] using h

/-- Any actual primary decomposition of the intrinsic component has the intrinsic count.
This also applies to decompositions not obtained by grouping a presentation of V. -/
theorem intrinsicMultiplicity_eq_card_of_component_decomposition
    {ι : Type v} [Fintype ι] (T : Module.End k V) (p : k[X]) (hp : Irreducible p)
    (q : ι → k[X]) (hq : ∀ i, Irreducible (q i)) (e : ι → ℕ) (he : ∀ i, 0 < e i)
    (hlabel : ∀ i, Ideal.span {q i} = Ideal.span {p})
    (f : primarySubmodule (Module.AEval' T) p ≃ₗ[k[X]]
      ((i : ι) → k[X] ⧸ Ideal.span {q i ^ e i})) :
    intrinsicMultiplicity T p = Fintype.card ι := by
  classical
  let : (Ideal.span {p}).IsMaximal := PrincipalIdealRing.isMaximal_of_irreducible hp
  let : Field (k[X] ⧸ Ideal.span {p}) := Ideal.Quotient.field _
  have E := (scalarQuotientCongr p f).trans (primaryProductQuotientEquiv q hq e he p hp)
  have h := E.finrank_eq
  have hc : intrinsicMultiplicity T p =
      Fintype.card {i : ι // Ideal.span {q i} = Ideal.span {p}} := by
    simpa [intrinsicMultiplicity, Module.finrank_pi, ← Nat.card_eq_fintype_card] using h
  exact hc.trans (Fintype.card_congr (Equiv.subtypeUnivEquiv hlabel))

/-- Every individual fibre multiplicity, not merely its maximum, is presentation invariant. -/
theorem primary_fiber_presentation_invariant [FiniteDimensional k V]
    {T : Module.End k V} (D E : PrimaryPresentation T) (p : k[X]) (hp : Irreducible p) :
    fiberMultiplicity D.label (Ideal.span {p}) =
      fiberMultiplicity E.label (Ideal.span {p}) :=
  (intrinsicMultiplicity_eq_fiber D p hp).symm.trans
    (intrinsicMultiplicity_eq_fiber E p hp)

/-- A missing primary label contributes zero to the intrinsic quotient dimension. -/
theorem intrinsicMultiplicity_eq_zero_of_absent [FiniteDimensional k V]
    {T : Module.End k V} (D : PrimaryPresentation T) (p : k[X]) (hp : Irreducible p)
    (h : ∀ i, D.label i ≠ Ideal.span {p}) : intrinsicMultiplicity T p = 0 := by
  classical
  rw [intrinsicMultiplicity_eq_fiber D p hp]
  let : IsEmpty {i : D.Index // D.label i = Ideal.span {p}} :=
    ⟨fun i ↦ h i.val i.property⟩
  simp [fiberMultiplicity]

/-- The printed primary quotient formula for the canonical seed rank. -/
theorem operator_seedFinrank_eq_intrinsic_primary_max [FiniteDimensional k V]
    {T : Module.End k V} (D : PrimaryPresentation T) :
    seedFinrank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V =
      Finset.univ.sup (fun i : D.Index ↦ intrinsicMultiplicity T (D.prime i)) := by
  rw [D.seedFinrank_eq]
  unfold PrimaryPresentation.maxCount maxMultiplicity
  congr 1
  funext i
  exact (intrinsicMultiplicity_eq_fiber D (D.prime i) (D.irreducible i)).symm


/-- Associated irreducibles define the same intrinsic multiplicity. -/
theorem intrinsicMultiplicity_eq_of_span_eq [FiniteDimensional k V]
    (T : Module.End k V) (p q : k[X]) (hp : Irreducible p) (hq : Irreducible q)
    (h : Ideal.span {p} = Ideal.span {q}) :
    intrinsicMultiplicity T p = intrinsicMultiplicity T q := by
  let D := chosenPrimaryPresentation T
  rw [intrinsicMultiplicity_eq_fiber D p hp, intrinsicMultiplicity_eq_fiber D q hq, h]

/-- Every intrinsic multiplicity is bounded by the canonical seed number. -/
theorem intrinsicMultiplicity_le_seedFinrank [FiniteDimensional k V]
    (T : Module.End k V) (p : k[X]) (hp : Irreducible p) :
    intrinsicMultiplicity T p ≤ seedFinrank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V := by
  classical
  let D := chosenPrimaryPresentation T
  by_cases h : ∃ i : D.Index, D.label i = Ideal.span {p}
  · obtain ⟨i, hi⟩ := h
    rw [intrinsicMultiplicity_eq_fiber D p hp, D.seedFinrank_eq, ← hi]
    exact fiberMultiplicity_le_max D.label i
  · rw [intrinsicMultiplicity_eq_zero_of_absent D p hp (by simpa using h)]
    exact Nat.zero_le _

/-- The exact set in the printed maximum: all monic irreducible polynomials. -/
def monicPrimaryMultiplicityValues (T : Module.End k V) : Set ℕ :=
  {n | ∃ p : k[X], p.Monic ∧ Irreducible p ∧ intrinsicMultiplicity T p = n}

/-- The zero-dimensional case also has a nonempty value set, containing the value at X. -/
theorem monicPrimaryMultiplicityValues_nonempty (T : Module.End k V) :
    (monicPrimaryMultiplicityValues T).Nonempty :=
  ⟨intrinsicMultiplicity T X, X, monic_X, irreducible_X, rfl⟩

/-- The set of intrinsic primary dimensions is bounded; its supremum is a true finite maximum. -/
theorem monicPrimaryMultiplicityValues_bddAbove [FiniteDimensional k V] (T : Module.End k V) :
    BddAbove (monicPrimaryMultiplicityValues T) := by
  refine ⟨seedFinrank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V, ?_⟩
  rintro n ⟨p, _, hp, rfl⟩
  exact intrinsicMultiplicity_le_seedFinrank T p hp

/-- A presentation-free definition of the intrinsic maximum. -/
def intrinsicSeedMaximum (T : Module.End k V) : ℕ := sSup (monicPrimaryMultiplicityValues T)

/-- The maximum is attained by a monic irreducible, including when every multiplicity is zero. -/
theorem intrinsicSeedMaximum_attained [FiniteDimensional k V] (T : Module.End k V) :
    ∃ p : k[X], p.Monic ∧ Irreducible p ∧ intrinsicMultiplicity T p = intrinsicSeedMaximum T :=
  Nat.sSup_mem (monicPrimaryMultiplicityValues_nonempty T)
    (monicPrimaryMultiplicityValues_bddAbove T)

/-- The complete printed maximum formula, with no supplied presentation or seed certificate. -/
theorem operator_seedFinrank_eq_intrinsicSeedMaximum [FiniteDimensional k V]
    (T : Module.End k V) :
    seedFinrank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = intrinsicSeedMaximum T := by
  classical
  let D := chosenPrimaryPresentation T
  apply le_antisymm
  · rw [operator_seedFinrank_eq_intrinsic_primary_max D]
    apply Finset.sup_le
    intro i _
    let p := normalize (D.prime i)
    have hp : Irreducible p := (associated_normalize (D.prime i)).irreducible (D.irreducible i)
    have hm : p.Monic := Polynomial.monic_normalize (D.irreducible i).ne_zero
    have heq : intrinsicMultiplicity T p = intrinsicMultiplicity T (D.prime i) :=
      intrinsicMultiplicity_eq_of_span_eq T p (D.prime i) hp (D.irreducible i)
        (Ideal.span_singleton_eq_span_singleton.mpr (normalize_associated (D.prime i)))
    rw [← heq]
    exact le_csSup (monicPrimaryMultiplicityValues_bddAbove T) ⟨p, hm, hp, rfl⟩
  · exact csSup_le (monicPrimaryMultiplicityValues_nonempty T)
      (fun n ⟨p, _, hp, hn⟩ ↦ hn ▸ intrinsicMultiplicity_le_seedFinrank T p hp)

/-- Cardinal-valued seed rank equals the same exact intrinsic maximum. -/
theorem operator_seedRank_eq_intrinsicSeedMaximum [FiniteDimensional k V]
    (T : Module.End k V) :
    seedRank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V =
      (intrinsicSeedMaximum T : Cardinal) := by
  let D := chosenPrimaryPresentation T
  rw [D.seedRank_eq, ← D.seedFinrank_eq, operator_seedFinrank_eq_intrinsicSeedMaximum T]

end Komorebi.PaperICompletion4.OperatorIntrinsicFormula
