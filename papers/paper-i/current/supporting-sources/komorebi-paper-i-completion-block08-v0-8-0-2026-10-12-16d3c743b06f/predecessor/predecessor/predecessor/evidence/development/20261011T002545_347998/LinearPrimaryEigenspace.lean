import PaperICompletion4
import Mathlib.RingTheory.Polynomial.Quotient
import Mathlib.LinearAlgebra.Dimension.Free

/-! # Linear primary multiplicity is actual geometric multiplicity
The polynomial scalar quotient is identified with the literal cokernel of p(T).
For p = X - C a, evaluation identifies its residue field with the base field.
Rank-nullity then computes the dimension of the actual eigenspace, without
any diagonalizability hypothesis.
-/
set_option autoImplicit false
noncomputable section
open scoped Pointwise
namespace Komorebi.PaperICompletion5.LinearPrimaryEigenspace
open Polynomial
open Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula
universe u v
variable {k : Type u} [Field k]
variable {V : Type v} [AddCommGroup V] [Module k V]

/-- The original vector, followed by the actual cokernel quotient. -/
def polynomialCokernelMap (T : Module.End k V) (p : k[X]) :
    Module.AEval' T →ₗ[k] V ⧸ LinearMap.range (aeval T p) :=
  (LinearMap.range (aeval T p)).mkQ.comp (Module.AEval'.of T).symm.toLinearMap

/-- No finite-dimensional hypothesis is required for this quotient map. -/
theorem polynomialCokernelMap_surjective (T : Module.End k V) (p : k[X]) :
    Function.Surjective (polynomialCokernelMap T p) :=
  (LinearMap.range (aeval T p)).mkQ_surjective.comp (Module.AEval'.of T).symm.surjective

/-- The kernel is exactly the actual polynomial scalar image. -/
theorem polynomialCokernelMap_ker (T : Module.End k V) (p : k[X]) :
    (polynomialCokernelMap T p).ker =
      (p • (⊤ : Submodule k[X] (Module.AEval' T))).restrictScalars k := by
  ext x
  change Submodule.Quotient.mk ((Module.AEval'.of T).symm x) =
    (0 : V ⧸ LinearMap.range (aeval T p)) ↔
      x ∈ p • (⊤ : Submodule k[X] (Module.AEval' T))
  rw [Submodule.Quotient.mk_eq_zero, LinearMap.mem_range, mem_scalarImage_iff]
  rfl

/-- The natural base-field-linear equivalence from polynomial quotient to cokernel. -/
def polynomialQuotientEquivCokernel (T : Module.End k V) (p : k[X]) :
    ScalarQuotient (Module.AEval' T) p ≃ₗ[k] V ⧸ LinearMap.range (aeval T p) :=
  (Submodule.Quotient.restrictScalarsEquiv k
    (p • (⊤ : Submodule k[X] (Module.AEval' T)))).symm.trans
    ((Submodule.quotEquivOfEq _ _ (polynomialCokernelMap_ker T p).symm).trans
      ((polynomialCokernelMap T p).quotKerEquivOfSurjective
        (polynomialCokernelMap_surjective T p)))

/-- The equivalence preserves the literal representative in the original vector space. -/
theorem polynomialQuotientEquivCokernel_mk (T : Module.End k V) (p : k[X]) (x : V) :
    polynomialQuotientEquivCokernel T p (Submodule.Quotient.mk (Module.AEval'.of T x)) =
      Submodule.Quotient.mk x := by
  simp [polynomialQuotientEquivCokernel, polynomialCokernelMap]

/-- Endomorphisms have equal nullity and cokernel dimension in finite dimension. -/
theorem finrank_cokernel_eq_finrank_kernel [FiniteDimensional k V] (S : Module.End k V) :
    Module.finrank k (V ⧸ LinearMap.range S) = Module.finrank k (LinearMap.ker S) := by
  have hq := (LinearMap.range S).finrank_quotient_add_finrank
  have hk := S.finrank_range_add_finrank_ker
  omega

/-- Evaluation identifies the linear residue field with a one-dimensional base-field space. -/
theorem linearResidue_finrank (a : k) :
    Module.finrank k (k[X] ⧸ Ideal.span {X - C a}) = 1 := by
  simpa using (quotientSpanXSubCAlgEquiv a).toLinearEquiv.finrank_eq

/-- Linear primary multiplicity equals the dimension of the actual eigenspace.
This holds over any field and includes non-diagonalizable operators. -/
theorem intrinsicMultiplicity_X_sub_C_eq_eigenspace [FiniteDimensional k V]
    (T : Module.End k V) (a : k) :
    intrinsicMultiplicity T (X - C a) = Module.finrank k (T.eigenspace a) := by
  let p : k[X] := X - C a
  let : (Ideal.span {p}).IsMaximal :=
    PrincipalIdealRing.isMaximal_of_irreducible (irreducible_X_sub_C a)
  let : Field (k[X] ⧸ Ideal.span {p}) := Ideal.Quotient.field _
  let : IsArtinian k[X] (Module.AEval' T) := isArtinian_of_tower k inferInstance
  have hd : Module.finrank (k[X] ⧸ Ideal.span {p}) (IntrinsicPrimaryQuotient T p) =
      Module.finrank k (IntrinsicPrimaryQuotient T p) := by
    have h := Module.finrank_mul_finrank k (k[X] ⧸ Ideal.span {p})
      (IntrinsicPrimaryQuotient T p)
    simpa only [p, linearResidue_finrank, one_mul] using h
  have heval : aeval T p = T - a • 1 := by
    simp [p, Algebra.algebraMap_eq_smul_one]
  calc
    intrinsicMultiplicity T (X - C a) =
        Module.finrank k (IntrinsicPrimaryQuotient T p) := hd
    _ = Module.finrank k (ScalarQuotient (Module.AEval' T) p) :=
      ((primaryQuotientEquivGlobal (Module.AEval' T) p).restrictScalars k).finrank_eq
    _ = Module.finrank k (V ⧸ LinearMap.range (aeval T p)) :=
      (polynomialQuotientEquivCokernel T p).finrank_eq
    _ = Module.finrank k (LinearMap.ker (aeval T p)) :=
      finrank_cokernel_eq_finrank_kernel (aeval T p)
    _ = Module.finrank k (T.eigenspace a) := by rw [heval, Module.End.eigenspace_def]

end Komorebi.PaperICompletion5.LinearPrimaryEigenspace
