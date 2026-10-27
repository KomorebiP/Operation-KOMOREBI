import PaperXI.HolonomyResidual
import Mathlib.Analysis.Normed.Operator.Basic

/-! Continuous forms of the exact residual identity and its conditioning bound.
The maps are actual continuous linear equivalences. No isometry is assumed. -/
set_option autoImplicit false

namespace PaperXI.ContinuousHolonomyResidual

variable {K Vr Vu Vv Wr Wu Wv : Type*} [NontriviallyNormedField K]
variable [NormedAddCommGroup Vr] [NormedSpace K Vr]
variable [NormedAddCommGroup Vu] [NormedSpace K Vu]
variable [NormedAddCommGroup Vv] [NormedSpace K Vv]
variable [NormedAddCommGroup Wr] [NormedSpace K Wr]
variable [NormedAddCommGroup Wu] [NormedSpace K Wu]
variable [NormedAddCommGroup Wv] [NormedSpace K Wv]

def transported (U : Vr ≃L[K] Wr) (A : Vr ≃L[K] Vu) (B : Wr ≃L[K] Wu) :
    Vu ≃L[K] Wu := (A.symm.trans U).trans B

@[simp] theorem transported_apply (U : Vr ≃L[K] Wr) (A : Vr ≃L[K] Vu)
    (B : Wr ≃L[K] Wu) (x : Vu) : transported U A B x = B (U (A.symm x)) := rfl

@[simp] theorem transported_toLinearEquiv (U : Vr ≃L[K] Wr) (A : Vr ≃L[K] Vu)
    (B : Wr ≃L[K] Wu) : (transported U A B).toLinearEquiv =
      HolonomyResidual.transported U.toLinearEquiv A.toLinearEquiv B.toLinearEquiv := rfl

def cycleDefect (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv) : Vr →L[K] Wr :=
  U.toContinuousLinearMap.comp
      (Av.symm.toContinuousLinearMap.comp (A.toContinuousLinearMap.comp Au.toContinuousLinearMap)) -
    Bv.symm.toContinuousLinearMap.comp
      (B.toContinuousLinearMap.comp (Bu.toContinuousLinearMap.comp U.toContinuousLinearMap))

def edgeResidual (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv) : Vu →L[K] Wv :=
  (transported U Av Bv).toContinuousLinearMap.comp A.toContinuousLinearMap -
    B.toContinuousLinearMap.comp (transported U Au Bu).toContinuousLinearMap

@[simp] theorem cycleDefect_toLinearMap (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv) :
    (cycleDefect U Au Av Bu Bv A B).toLinearMap =
      HolonomyResidual.cycleDefect U.toLinearEquiv Au.toLinearEquiv Av.toLinearEquiv
        Bu.toLinearEquiv Bv.toLinearEquiv A.toLinearEquiv B.toLinearEquiv := rfl

@[simp] theorem edgeResidual_toLinearMap (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv) :
    (edgeResidual U Au Av Bu Bv A B).toLinearMap =
      HolonomyResidual.edgeResidual U.toLinearEquiv Au.toLinearEquiv Av.toLinearEquiv
        Bu.toLinearEquiv Bv.toLinearEquiv A.toLinearEquiv B.toLinearEquiv := rfl

theorem residual_factorization (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv) :
    edgeResidual U Au Av Bu Bv A B =
      Bv.toContinuousLinearMap.comp
        ((cycleDefect U Au Av Bu Bv A B).comp Au.symm.toContinuousLinearMap) := by
  ext x
  exact LinearMap.congr_fun (HolonomyResidual.residual_factorization
    U.toLinearEquiv Au.toLinearEquiv Av.toLinearEquiv Bu.toLinearEquiv
    Bv.toLinearEquiv A.toLinearEquiv B.toLinearEquiv) x

theorem residual_zero_iff (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv) :
    edgeResidual U Au Av Bu Bv A B = 0 ↔ cycleDefect U Au Av Bu Bv A B = 0 := by
  rw [residual_factorization]
  constructor
  · intro h
    ext x
    have hx := congrArg (fun f : Vu →L[K] Wv => f (Au x)) h
    simpa using hx
  · intro h
    simp [h]

theorem residual_norm_bound (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv) :
    ‖edgeResidual U Au Av Bu Bv A B‖ ≤
      ‖Bv.toContinuousLinearMap‖ * ‖cycleDefect U Au Av Bu Bv A B‖ *
        ‖Au.symm.toContinuousLinearMap‖ := by
  rw [residual_factorization]
  calc
    _ ≤ ‖Bv.toContinuousLinearMap‖ *
        ‖(cycleDefect U Au Av Bu Bv A B).comp Au.symm.toContinuousLinearMap‖ :=
      ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ ‖Bv.toContinuousLinearMap‖ *
        (‖cycleDefect U Au Av Bu Bv A B‖ * ‖Au.symm.toContinuousLinearMap‖) :=
      mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _)
    _ = _ := (mul_assoc _ _ _).symm

theorem uniform_bound (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv)
    (C_B ε C_A : ℝ) (hB : ‖Bv.toContinuousLinearMap‖ ≤ C_B)
    (hD : ‖cycleDefect U Au Av Bu Bv A B‖ ≤ ε)
    (hA : ‖Au.symm.toContinuousLinearMap‖ ≤ C_A) :
    ‖edgeResidual U Au Av Bu Bv A B‖ ≤ C_B * ε * C_A := by
  apply (residual_norm_bound U Au Av Bu Bv A B).trans
  have hB0 : 0 ≤ C_B := (norm_nonneg _).trans hB
  have hD0 : 0 ≤ ε := (norm_nonneg _).trans hD
  exact mul_le_mul (mul_le_mul hB hD (norm_nonneg _) hB0) hA
    (norm_nonneg _) (mul_nonneg hB0 hD0)

/-- A bound on the actual mixed path factor suffices. This factor is not the
condition number of either individual transport. -/
theorem product_conditioning_bound (U : Vr ≃L[K] Wr)
    (Au : Vr ≃L[K] Vu) (Av : Vr ≃L[K] Vv)
    (Bu : Wr ≃L[K] Wu) (Bv : Wr ≃L[K] Wv)
    (A : Vu ≃L[K] Vv) (B : Wu ≃L[K] Wv)
    (C ε : ℝ)
    (hC : ‖Bv.toContinuousLinearMap‖ * ‖Au.symm.toContinuousLinearMap‖ ≤ C)
    (hD : ‖cycleDefect U Au Av Bu Bv A B‖ ≤ ε) :
    ‖edgeResidual U Au Av Bu Bv A B‖ ≤ C * ε := by
  apply (residual_norm_bound U Au Av Bu Bv A B).trans
  rw [mul_right_comm]
  exact mul_le_mul hC hD (norm_nonneg _)
    ((mul_nonneg (norm_nonneg _) (norm_nonneg _)).trans hC)

end PaperXI.ContinuousHolonomyResidual
