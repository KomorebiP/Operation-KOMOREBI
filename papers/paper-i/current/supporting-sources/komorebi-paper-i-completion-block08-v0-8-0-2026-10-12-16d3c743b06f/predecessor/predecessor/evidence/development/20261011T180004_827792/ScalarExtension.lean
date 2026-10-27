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
  ext T
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

end Komorebi.PaperICompletion6.ScalarExtension
