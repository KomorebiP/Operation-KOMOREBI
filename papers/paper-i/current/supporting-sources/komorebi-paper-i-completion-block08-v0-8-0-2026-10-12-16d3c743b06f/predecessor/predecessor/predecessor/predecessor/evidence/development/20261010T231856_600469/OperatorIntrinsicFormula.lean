import PaperICompletion4.IntrinsicPrimary

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

end Komorebi.PaperICompletion4.OperatorIntrinsicFormula
