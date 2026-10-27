import Mathlib.LinearAlgebra.Dual.Defs
import Mathlib.LinearAlgebra.BilinearMap
import Mathlib.LinearAlgebra.Prod
import Mathlib.Tactic.Ring

/-! The manuscript's standard alternating form on X plus its linear dual. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergForm

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

def form : (X × Module.Dual K X) →ₗ[K] (X × Module.Dual K X) →ₗ[K] K where
  toFun v :=
    { toFun := fun w => w.2 v.1 - v.2 w.1
      map_add' := by
        intro w t
        simp only [Prod.fst_add, Prod.snd_add, LinearMap.add_apply, map_add]
        ring
      map_smul' := by
        intro a w
        change (a • w.2) v.1 - v.2 (a • w.1) = a • (w.2 v.1 - v.2 w.1)
        simp only [LinearMap.smul_apply, map_smul, smul_eq_mul]
        ring }
  map_add' := by
    intro v w
    apply LinearMap.ext
    intro t
    change t.2 (v + w).1 - (v + w).2 t.1 =
      (t.2 v.1 - v.2 t.1) + (t.2 w.1 - w.2 t.1)
    simp only [Prod.fst_add, Prod.snd_add, LinearMap.add_apply, map_add]
    ring
  map_smul' := by
    intro a v
    apply LinearMap.ext
    intro w
    change w.2 (a • v.1) - (a • v.2) w.1 = a • (w.2 v.1 - v.2 w.1)
    simp only [LinearMap.smul_apply, map_smul, smul_eq_mul]
    ring

@[simp] theorem form_apply (v w : X × Module.Dual K X) :
    form v w = w.2 v.1 - v.2 w.1 := rfl

theorem form_self (v : X × Module.Dual K X) : form v v = 0 := by
  simp

theorem form_skew (v w : X × Module.Dual K X) : form v w = -form w v := by
  simp

end PaperXI.HeisenbergForm
