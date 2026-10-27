import Mathlib.LinearAlgebra.Pi
import Mathlib.Tactic

/-! Paper XI, Proposition 14.6. The supplied equivalences are actual
root-to-vertex transports. Constructing the graph/tree is a separate obligation. -/
set_option autoImplicit false
namespace PaperXI.HolonomyResidual

variable {K Vr Vu Vv Wr Wu Wv : Type*} [Field K]
variable [AddCommGroup Vr] [Module K Vr] [AddCommGroup Vu] [Module K Vu]
variable [AddCommGroup Vv] [Module K Vv] [AddCommGroup Wr] [Module K Wr]
variable [AddCommGroup Wu] [Module K Wu] [AddCommGroup Wv] [Module K Wv]

def transported (U : Vr ≃ₗ[K] Wr) (A : Vr ≃ₗ[K] Vu) (B : Wr ≃ₗ[K] Wu) :
    Vu ≃ₗ[K] Wu := (A.symm.trans U).trans B

@[simp] theorem transported_apply (U : Vr ≃ₗ[K] Wr) (A : Vr ≃ₗ[K] Vu)
    (B : Wr ≃ₗ[K] Wu) (x : Vu) : transported U A B x = B (U (A.symm x)) := rfl

def cycleDefect (U : Vr ≃ₗ[K] Wr)
    (Au : Vr ≃ₗ[K] Vu) (Av : Vr ≃ₗ[K] Vv)
    (Bu : Wr ≃ₗ[K] Wu) (Bv : Wr ≃ₗ[K] Wv)
    (A : Vu ≃ₗ[K] Vv) (B : Wu ≃ₗ[K] Wv) : Vr →ₗ[K] Wr :=
  U.toLinearMap.comp (Av.symm.toLinearMap.comp (A.toLinearMap.comp Au.toLinearMap)) -
    Bv.symm.toLinearMap.comp (B.toLinearMap.comp (Bu.toLinearMap.comp U.toLinearMap))

def edgeResidual (U : Vr ≃ₗ[K] Wr)
    (Au : Vr ≃ₗ[K] Vu) (Av : Vr ≃ₗ[K] Vv)
    (Bu : Wr ≃ₗ[K] Wu) (Bv : Wr ≃ₗ[K] Wv)
    (A : Vu ≃ₗ[K] Vv) (B : Wu ≃ₗ[K] Wv) : Vu →ₗ[K] Wv :=
  (transported U Av Bv).toLinearMap.comp A.toLinearMap -
    B.toLinearMap.comp (transported U Au Bu).toLinearMap

theorem residual_factorization (U : Vr ≃ₗ[K] Wr)
    (Au : Vr ≃ₗ[K] Vu) (Av : Vr ≃ₗ[K] Vv)
    (Bu : Wr ≃ₗ[K] Wu) (Bv : Wr ≃ₗ[K] Wv)
    (A : Vu ≃ₗ[K] Vv) (B : Wu ≃ₗ[K] Wv) :
    edgeResidual U Au Av Bu Bv A B =
      Bv.toLinearMap.comp ((cycleDefect U Au Av Bu Bv A B).comp Au.symm.toLinearMap) := by
  ext x
  simp [edgeResidual, cycleDefect, transported]

theorem residual_zero_iff (U : Vr ≃ₗ[K] Wr)
    (Au : Vr ≃ₗ[K] Vu) (Av : Vr ≃ₗ[K] Vv)
    (Bu : Wr ≃ₗ[K] Wu) (Bv : Wr ≃ₗ[K] Wv)
    (A : Vu ≃ₗ[K] Vv) (B : Wu ≃ₗ[K] Wv) :
    edgeResidual U Au Av Bu Bv A B = 0 ↔ cycleDefect U Au Av Bu Bv A B = 0 := by
  rw [residual_factorization]
  constructor
  · intro h
    apply LinearMap.ext
    intro x
    have hx := LinearMap.congr_fun h (Au x)
    simpa using hx
  · intro h; simp [h]

end PaperXI.HolonomyResidual
