import PaperICompletion4
import Mathlib.RingTheory.Polynomial.Quotient
import Mathlib.LinearAlgebra.Dimension.Free
import Mathlib.FieldTheory.IsAlgClosed.Basic
open Polynomial
open scoped Pointwise
open Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula
noncomputable section
universe u v
variable {k : Type u} [Field k] {V : Type v} [AddCommGroup V] [Module k V]
variable (T : Module.End k V) (a : k)
#synth Module k (ScalarQuotient (Module.AEval' T) (X - C a))
#synth Module k (IntrinsicPrimaryQuotient T (X - C a))
#synth IsScalarTower k (k[X] ⧸ Ideal.span {X - C a}) (IntrinsicPrimaryQuotient T (X - C a))
#synth IsScalarTower k (k[X] ⧸ Ideal.span {X - C a}) (ScalarQuotient (Module.AEval' T) (X - C a))
#check Module.finrank_mul_finrank
#check Polynomial.irreducible_X_sub_C
#check Polynomial.aeval_X
#check Polynomial.aeval_C
#check Submodule.quotEquivOfEq
#check Submodule.Quotient.equiv
#check LinearEquiv.quotientEquiv
#check LinearMap.quotKerEquivOfSurjective
#check Module.End.eigenspace
#check Module.End.eigenspace_def
#check IsAlgClosed.degree_eq_one_of_irreducible
#check Polynomial.eq_X_sub_C_of_monic_of_root
