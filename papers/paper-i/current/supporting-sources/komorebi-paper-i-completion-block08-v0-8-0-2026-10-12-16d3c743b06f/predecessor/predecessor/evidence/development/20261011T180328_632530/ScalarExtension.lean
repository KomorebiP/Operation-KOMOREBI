import PaperICompletion5
import Mathlib.LinearAlgebra.Charpoly.BaseChange
import Mathlib.RingTheory.TensorProduct.IsBaseChangeHom
import Mathlib.RingTheory.Flat.Basic
import Mathlib.RingTheory.PowerBasis

/-! # Actual scalar extension of finite-dimensional operators
The extension is the literal tensor-product endomorphism `T.baseChange K`.
No minimal-polynomial preservation or descent certificate is an input.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperICompletion6.ScalarExtension
open Polynomial TensorProduct
open scoped TensorProduct
universe u v w
variable {k : Type u} [Field k] {V : Type v} [AddCommGroup V] [Module k V]
variable (K : Type w) [Field K] [Algebra k K]

/-- The endomorphism map provided by the universal property is literal base change. -/
theorem tensor_endHom_eq_baseChange :
    (TensorProduct.isBaseChange k V K).endHom = LinearMap.baseChangeHom k K V V := by
  apply LinearMap.ext
  intro T
  apply (TensorProduct.isBaseChange k V K).algHom_ext
  intro x
  simpa using (TensorProduct.isBaseChange k V K).endHom_comp_apply T x

/-- The full endomorphism space commutes with scalar extension in finite dimension. -/
theorem isBaseChange_endomorphisms [FiniteDimensional k V] :
    IsBaseChange K (LinearMap.baseChangeHom k K V V) := by
  rw [← tensor_endHom_eq_baseChange K]
  exact (TensorProduct.isBaseChange k V K).end

/-- Linear independence of actual operators survives field extension. -/
theorem linearIndependent_baseChange [FiniteDimensional k V] {ι : Type*}
    {f : ι → Module.End k V} (hf : LinearIndependent k f) :
    LinearIndependent K (fun i => (f i).baseChange K) := by
  have h := (Module.Flat.linearIndependent_one_tmul (S := K) hf).map'
    (isBaseChange_endomorphisms (V := V) K).equiv.toLinearMap
    (LinearMap.ker_eq_bot.mpr (isBaseChange_endomorphisms (V := V) K).equiv.injective)
  simpa [Function.comp_def] using h

/-- Powers below the original minimal degree remain independent over the extended field. -/
theorem linearIndependent_baseChange_powers [FiniteDimensional k V] (T : Module.End k V) :
    LinearIndependent K
      (fun i : Fin (minpoly k T).natDegree => (T.baseChange K) ^ (i : ℕ)) := by
  simpa only [LinearMap.baseChange_pow] using
    linearIndependent_baseChange K (linearIndependent_pow (K := k) T)

/-- Evaluating mapped coefficients agrees with extending the evaluated operator. -/
theorem aeval_map_baseChange (T : Module.End k V) (p : k[X]) :
    aeval (T.baseChange K) (p.map (algebraMap k K)) = (aeval T p).baseChange K := by
  rw [aeval_map_algebraMap]
  exact aeval_algHom_apply (Module.End.baseChangeHom k K V) T p

/-- The minimal polynomial itself commutes with every field extension. -/
theorem minpoly_baseChange [FiniteDimensional k V] (T : Module.End k V) :
    minpoly K (T.baseChange K) = (minpoly k T).map (algebraMap k K) := by
  refine minpoly.eq_of_linearIndependent K (T.baseChange K)
    ((minpoly.monic (LinearMap.isIntegral T)).map _) ?_
    (minpoly k T).natDegree ?_ ?_
  · rw [aeval_map_baseChange, minpoly.aeval, LinearMap.baseChange_zero]
  · rw [Polynomial.degree_map_eq_of_injective (algebraMap k K).injective,
      Polynomial.degree_eq_natDegree (minpoly.ne_zero (LinearMap.isIntegral T))]
  · exact linearIndependent_baseChange_powers K T

/-- Minimal-polynomial degree is unchanged by any field extension. -/
theorem minpoly_natDegree_baseChange [FiniteDimensional k V] (T : Module.End k V) :
    (minpoly K (T.baseChange K)).natDegree = (minpoly k T).natDegree := by
  rw [minpoly_baseChange, Polynomial.natDegree_map_eq_of_injective (algebraMap k K).injective]

/-- Equality of minimal and characteristic polynomials is both preserved and reflected. -/
theorem minpoly_eq_charpoly_baseChange_iff [FiniteDimensional k V] (T : Module.End k V) :
    minpoly K (T.baseChange K) = (T.baseChange K).charpoly ↔ minpoly k T = T.charpoly := by
  rw [minpoly_baseChange, LinearMap.charpoly_baseChange]
  exact (Polynomial.map_injective (algebraMap k K).injective).eq_iff

/-- Cyclicity is preserved and reflected for the actual tensor-product operator. -/
theorem hasCyclicVector_baseChange_iff [FiniteDimensional k V] (T : Module.End k V) :
    Komorebi.SingleOperatorGraph.HasCyclicVector (T.baseChange K) ↔
      Komorebi.SingleOperatorGraph.HasCyclicVector T := by
  rw [Komorebi.PaperICompletion.CyclicClassification.hasCyclicVector_iff_minpoly_eq_charpoly,
    Komorebi.PaperICompletion.CyclicClassification.hasCyclicVector_iff_minpoly_eq_charpoly]
  exact minpoly_eq_charpoly_baseChange_iff K T

/-- The base-changed space is nonzero whenever the original vector space is nonzero. -/
theorem baseChange_nontrivial [Nontrivial V] : Nontrivial (K ⊗[k] V) :=
  Function.Injective.nontrivial (Module.Flat.tensorProduct_mk_injective k V K)

/-- The manuscript's clause after extension, over any algebraically closed extension field. -/
theorem hasCyclicVector_iff_extended_spectral_multiplicities_one
    [FiniteDimensional k V] [Nontrivial V] [IsAlgClosed K] (T : Module.End k V) :
    Komorebi.SingleOperatorGraph.HasCyclicVector T ↔
      ∀ a : K, a ∈ spectrum K (T.baseChange K) →
        Module.finrank K ((T.baseChange K).eigenspace a) = 1 := by
  letI : Nontrivial (K ⊗[k] V) := baseChange_nontrivial (V := V) K
  exact (hasCyclicVector_baseChange_iff K T).symm.trans
    (Komorebi.PaperICompletion5.CyclicGeometricCriterion.
      hasCyclicVector_iff_all_spectral_multiplicities_one (T.baseChange K))

end Komorebi.PaperICompletion6.ScalarExtension
