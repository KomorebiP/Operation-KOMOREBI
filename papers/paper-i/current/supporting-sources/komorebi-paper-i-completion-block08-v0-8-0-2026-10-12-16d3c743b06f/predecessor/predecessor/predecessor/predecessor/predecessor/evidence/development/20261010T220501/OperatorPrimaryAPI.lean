import PaperICompletion3.PrimarySeedFormula

/-!
# Public operator-primary API

A presentation contains an actual polynomial-module equivalence. A proved PID
construction produces such a presentation for every finite-dimensional operator.
The minimum is independent of the chosen presentation. No eigenbasis, supplied
seed-number equality, or polynomial cyclicity bridge is an input.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperICompletion3.OperatorPrimaryAPI

open Polynomial
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.SeedRankBasics

universe u v
variable {k : Type u} [Field k]
variable {V : Type v} [AddCommGroup V] [Module k V]

/-- A positive-exponent primary presentation of the actual polynomial action. -/
structure PrimaryPresentation (T : Module.End k V) where
  Index : Type u
  indexFintype : Fintype Index
  prime : Index → k[X]
  irreducible : ∀ i, Irreducible (prime i)
  exponent : Index → ℕ
  positive : ∀ i, 0 < exponent i
  equiv : Module.AEval' T ≃ₗ[k[X]] ((i : Index) → k[X] ⧸ Ideal.span {prime i ^ exponent i})

attribute [instance] PrimaryPresentation.indexFintype

/-- Existence is proved from finite-dimensionality, not assumed. -/
theorem primaryPresentation_nonempty [FiniteDimensional k V] (T : Module.End k V) :
    Nonempty (PrimaryPresentation T) := by
  obtain ⟨ι, hι, p, hp, e, he, ⟨f⟩⟩ := exists_positive_primaryProduct_equiv T
  exact ⟨⟨ι, hι, p, hp, e, he, f⟩⟩

/-- A mathematically chosen presentation. This is not an executable normal-form algorithm. -/
def chosenPrimaryPresentation [FiniteDimensional k V] (T : Module.End k V) :
    PrimaryPresentation T := Classical.choice (primaryPresentation_nonempty T)

/-- Labels are principal ideals, so associated irreducibles are counted together. -/
def PrimaryPresentation.label {T : Module.End k V} (D : PrimaryPresentation T) :
    D.Index → Ideal k[X] := fun i ↦ Ideal.span {D.prime i}

/-- Maximum number of positive primary blocks carrying the same irreducible ideal. -/
def PrimaryPresentation.maxCount {T : Module.End k V} (D : PrimaryPresentation T) : ℕ :=
  maxMultiplicity D.label

/-- Exact least generator number for any actual primary presentation. -/
theorem PrimaryPresentation.seedNumber_isLeast {T : Module.End k V} (D : PrimaryPresentation T) :
    IsLeast {r : ℕ | Komorebi.SingleOperatorGraph.SeedNumberLE T r} D.maxCount := by
  exact operator_seedNumber_isLeast_of_polynomialModule T _
    (seedNumber_isLeast_linearEquiv D.equiv _
      (primePowerProduct_seedNumber_isLeast D.prime D.irreducible D.exponent D.positive))

/-- The presentation formula is the canonical natural-valued seed rank. -/
theorem PrimaryPresentation.seedFinrank_eq {T : Module.End k V} (D : PrimaryPresentation T) :
    seedFinrank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = D.maxCount :=
  Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast T _
    D.seedNumber_isLeast

/-- The presentation formula is also the canonical cardinal-valued seed rank. -/
theorem PrimaryPresentation.seedRank_eq {T : Module.End k V} (D : PrimaryPresentation T) :
    seedRank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = (D.maxCount : Cardinal) :=
  Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast T _
    D.seedNumber_isLeast

/-- The maximum is independent of every choice made in the PID presentation. -/
theorem PrimaryPresentation.maxCount_eq {T : Module.End k V}
    (D E : PrimaryPresentation T) : D.maxCount = E.maxCount :=
  D.seedFinrank_eq.symm.trans E.seedFinrank_eq

/-- Operator-derived primary generator count. -/
def primaryGeneratorCount [FiniteDimensional k V] (T : Module.End k V) : ℕ :=
  (chosenPrimaryPresentation T).maxCount

/-- No supplied decomposition or seed certificate occurs in this public theorem. -/
theorem operator_seedFinrank_eq_primaryGeneratorCount [FiniteDimensional k V]
    (T : Module.End k V) :
    seedFinrank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = primaryGeneratorCount T :=
  (chosenPrimaryPresentation T).seedFinrank_eq

/-- Cardinal form, including the zero-dimensional case. -/
theorem operator_seedRank_eq_primaryGeneratorCount [FiniteDimensional k V]
    (T : Module.End k V) :
    seedRank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V =
      (primaryGeneratorCount T : Cardinal) :=
  (chosenPrimaryPresentation T).seedRank_eq

/-- The chosen count is zero exactly for the zero module. -/
theorem primaryGeneratorCount_eq_zero_iff [FiniteDimensional k V] (T : Module.End k V) :
    primaryGeneratorCount T = 0 ↔ Subsingleton V := by
  rw [← Komorebi.SeedRankBasics.seedRank_eq_zero_iff
    (Komorebi.SingleOperatorGraph.operatorAlgebra T) V,
    operator_seedRank_eq_primaryGeneratorCount]
  exact Cardinal.natCast_eq_zero.symm

/-- Any cyclic vector forbids repeated irreducible primary labels. -/
theorem PrimaryPresentation.label_injective_of_cyclic {T : Module.End k V}
    (D : PrimaryPresentation T) (hT : Komorebi.SingleOperatorGraph.HasCyclicVector T) :
    Function.Injective D.label := by
  classical
  obtain ⟨s, hs⟩ := hT
  have hsModule := (familyGenerates_iff_polynomialModule T s).mp hs
  have hsProduct := (familyGenerates_linearEquiv_iff D.equiv
    (fun j ↦ Module.AEval'.of T (s j))).mpr hsModule
  intro i j hij
  let : (D.label i).IsMaximal := PrincipalIdealRing.isMaximal_of_irreducible (D.irreducible i)
  have hIP : ∀ x, Ideal.span {D.prime x ^ D.exponent x} ≤ D.label x := by
    intro x
    exact Ideal.span_singleton_le_span_singleton.mpr
      (dvd_pow_self _ (Nat.ne_of_gt (D.positive x)))
  have hcard := fiberMultiplicity_le_of_generates
    (fun x ↦ Ideal.span {D.prime x ^ D.exponent x}) D.label hIP (D.label i) _ hsProduct
  have hsmall : Nat.card {x : D.Index // D.label x = D.label i} ≤ 1 := by
    simpa [fiberMultiplicity, ← Nat.card_eq_fintype_card] using hcard
  have hsub : Subsingleton {x : D.Index // D.label x = D.label i} :=
    (Nat.card_le_one_iff_subsingleton).mp hsmall
  exact congrArg Subtype.val (@Subsingleton.elim _ hsub ⟨i, rfl⟩ ⟨j, hij.symm⟩)

/-- Distinct primary labels supply a cyclic vector by the literal CRT generator. -/
theorem PrimaryPresentation.cyclic_of_label_injective {T : Module.End k V}
    (D : PrimaryPresentation T) (hD : Function.Injective D.label) :
    Komorebi.SingleOperatorGraph.HasCyclicVector T := by
  let I : D.Index → Ideal k[X] := fun i ↦ Ideal.span {D.prime i ^ D.exponent i}
  let color : D.Index → Fin 1 := fun _ ↦ 0
  have hgen := coloredSeeds_generate I color (by
    intro i j hne _
    exact coprime_primePower_ideals (D.prime i) (D.prime j) (D.irreducible i)
      (D.irreducible j) (fun h ↦ hne (hD h)) (D.exponent i) (D.exponent j))
  let s := fun j : Fin 1 ↦ D.equiv.symm (coloredSeeds I color j)
  have hs : FamilyGenerates k[X] (Module.AEval' T) s :=
    (familyGenerates_linearEquiv_iff D.equiv.symm (coloredSeeds I color)).mpr hgen
  refine ⟨fun j ↦ (Module.AEval'.of T).symm (s j), ?_⟩
  apply (familyGenerates_iff_polynomialModule T _).mpr
  simpa using hs

/-- The primary cyclic criterion is unconditional and includes the zero space. -/
theorem PrimaryPresentation.cyclic_iff_label_injective {T : Module.End k V}
    (D : PrimaryPresentation T) :
    Komorebi.SingleOperatorGraph.HasCyclicVector T ↔ Function.Injective D.label :=
  ⟨D.label_injective_of_cyclic, D.cyclic_of_label_injective⟩

/-- No repeated irreducible primary factor is equivalent to the polynomial cyclic criterion. -/
theorem PrimaryPresentation.label_injective_iff_minpoly_eq_charpoly
    [FiniteDimensional k V] {T : Module.End k V} (D : PrimaryPresentation T) :
    Function.Injective D.label ↔ minpoly k T = T.charpoly :=
  D.cyclic_iff_label_injective.symm.trans
    (Komorebi.PaperICompletion.CyclicClassification.hasCyclicVector_iff_minpoly_eq_charpoly T)

end Komorebi.PaperICompletion3.OperatorPrimaryAPI
