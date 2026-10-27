import PaperIRelease.PacketDescent
import PaperIRelease.AlgebraTransfer
import KomorebiVerification.SeedRankOperations

set_option autoImplicit false
set_option linter.unnecessarySimpa false
noncomputable section

namespace Komorebi.PaperIRelease

open Komorebi.Foundation

universe u
variable {𝕜 X : Type u} [Field 𝕜] [AddCommGroup X] [Module 𝕜 X]

/-- Compress an ambient operator to the actual range of an idempotent.
On a range vector this is the literal action `e T e`, because `e x = x`. -/
def cornerCompression (e : Module.End 𝕜 X) (T : Module.End 𝕜 X) :
    Module.End 𝕜 (LinearMap.range e) where
  toFun x := ⟨e (T x), ⟨T x, rfl⟩⟩
  map_add' x y := Subtype.ext (by simp)
  map_smul' a x := Subtype.ext (by simp)

theorem idempotent_range_fixed (e : Module.End 𝕜 X)
    (he : ∀ x, e (e x) = e x) (x : LinearMap.range e) : e (x : X) = x := by
  obtain ⟨y, hy⟩ := x.property
  rw [← hy]
  exact he y

/-- The genuine unital corner acting on `range(e)`. The identity here is the
restriction of `e`, rather than the ambient identity on unrelated packets. -/
def packetCornerAlgebra (A : Subalgebra 𝕜 (Module.End 𝕜 X))
    (e : Module.End 𝕜 X) (heA : e ∈ A) (he : ∀ x, e (e x) = e x) :
    Subalgebra 𝕜 (Module.End 𝕜 (LinearMap.range e)) where
  carrier := {T | ∃ a ∈ A, cornerCompression e a = T}
  zero_mem' := ⟨0, A.zero_mem, by ext x; simp [cornerCompression]⟩
  add_mem' := by
    rintro T U ⟨a, ha, rfl⟩ ⟨b, hb, rfl⟩
    exact ⟨a + b, A.add_mem ha hb, by ext x; simp [cornerCompression]⟩
  mul_mem' := by
    rintro T U ⟨a, ha, rfl⟩ ⟨b, hb, rfl⟩
    exact ⟨a * e * b, A.mul_mem (A.mul_mem ha heA) hb, rfl⟩
  algebraMap_mem' a := by
    refine ⟨algebraMap 𝕜 (Module.End 𝕜 X) a, A.algebraMap_mem a, ?_⟩
    ext x
    change e (a • (x : X)) = a • (x : X)
    rw [map_smul, idempotent_range_fixed e he x]

/-- Every corner action is an actual action by an element of the ambient
algebra. The representing ambient element can be chosen independently of x. -/
theorem corner_action_ambient
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (e : Module.End 𝕜 X)
    (heA : e ∈ A) (he : ∀ x, e (e x) = e x)
    (T : packetCornerAlgebra A e heA he) :
    ∃ a : A, ∀ x : LinearMap.range e, (T • x : LinearMap.range e).val = a • (x : X) := by
  obtain ⟨a, ha, hT⟩ := T.property
  refine ⟨⟨e * a, A.mul_mem heA ha⟩, ?_⟩
  intro x
  change (T.val x : X) = e (a (x : X))
  rw [← hT]
  rfl

/-- The unital corner identity acts as the original projector on its range. -/
theorem corner_one_eq_projector
    (A : Subalgebra 𝕜 (Module.End 𝕜 X)) (e : Module.End 𝕜 X)
    (heA : e ∈ A) (he : ∀ x, e (e x) = e x) (x : LinearMap.range e) :
    ((1 : packetCornerAlgebra A e heA he) • x : LinearMap.range e).val = e (x : X) := by
  rw [one_smul, idempotent_range_fixed e he x]

end Komorebi.PaperIRelease
