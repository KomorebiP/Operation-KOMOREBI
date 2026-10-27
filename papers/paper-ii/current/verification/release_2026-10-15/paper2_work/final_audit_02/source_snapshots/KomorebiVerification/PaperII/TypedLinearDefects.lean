/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Algebra.Module.Submodule.LinearMap
import Mathlib.Algebra.Polynomial.Eval.Defs
import Mathlib.Analysis.Normed.Operator.Basic
import Mathlib.Tactic.Abel

/-!
# Paper II: typed linear defects

Author: Komorebi P.

The fine and coarse state spaces in this file are genuinely different
modules.  Thus the coarsening map cannot be silently treated as an
endomorphism.  We define its one-step intertwining defect, telescope that
defect through every natural power, and derive the scalar-shift resolvent
identity from explicit two-sided inverse witnesses.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.TypedLinearDefects

open scoped BigOperators

universe u v w

variable {R : Type u} [Semiring R]
variable {Xf : Type v} {Xc : Type w}
variable [AddCommGroup Xf] [AddCommGroup Xc]
variable [Module R Xf] [Module R Xc]

/-! ## Typed power defects -/

/-- The typed one-step defect `C ∘ Tf - Tc ∘ C`. -/
def defect (C : Xf →ₗ[R] Xc)
    (Tf : Module.End R Xf) (Tc : Module.End R Xc) : Xf →ₗ[R] Xc :=
  C.comp Tf - Tc.comp C

/-- The typed power-defect identity for every natural `n`, including zero. -/
theorem power_defect_identity_all
    (C : Xf →ₗ[R] Xc) (Tf : Module.End R Xf) (Tc : Module.End R Xc)
    (n : ℕ) :
    C.comp (Tf ^ n) - (Tc ^ n).comp C =
      ∑ k ∈ Finset.range n,
        (Tc ^ (n - 1 - k)).comp ((defect C Tf Tc).comp (Tf ^ k)) := by
  induction n with
  | zero => simp [defect, Module.End.one_eq_id]
  | succ n ih =>
      have hrecurrence :
          C.comp (Tf ^ (n + 1)) - (Tc ^ (n + 1)).comp C =
            Tc.comp (C.comp (Tf ^ n) - (Tc ^ n).comp C) +
              (defect C Tf Tc).comp (Tf ^ n) := by
        ext x
        simp only [pow_succ', Module.End.mul_apply, LinearMap.sub_apply,
          LinearMap.add_apply, LinearMap.comp_apply, defect, map_sub]
        abel
      rw [Finset.sum_range_succ]
      calc
        C.comp (Tf ^ (n + 1)) - (Tc ^ (n + 1)).comp C =
            Tc.comp (C.comp (Tf ^ n) - (Tc ^ n).comp C) +
              (defect C Tf Tc).comp (Tf ^ n) := hrecurrence
        _ = Tc.comp (∑ k ∈ Finset.range n,
              (Tc ^ (n - 1 - k)).comp
                ((defect C Tf Tc).comp (Tf ^ k))) +
              (defect C Tf Tc).comp (Tf ^ n) := by rw [ih]
        _ = (∑ k ∈ Finset.range n,
              (Tc ^ ((n + 1) - 1 - k)).comp
                ((defect C Tf Tc).comp (Tf ^ k))) +
              (Tc ^ ((n + 1) - 1 - n)).comp
                ((defect C Tf Tc).comp (Tf ^ n)) := by
          congr 1
          · ext x
            simp only [LinearMap.comp_apply, LinearMap.sum_apply, map_sum]
            apply Finset.sum_congr rfl
            intro k hk
            have hklt : k < n := Finset.mem_range.mp hk
            have hexponent : n - 1 - k + 1 = n - k := by omega
            have hsucc : (n + 1) - 1 - k = n - k := by omega
            rw [hsucc, ← hexponent]
            change (Tc * Tc ^ (n - 1 - k))
                ((defect C Tf Tc) ((Tf ^ k) x)) =
              (Tc ^ (n - 1 - k + 1))
                ((defect C Tf Tc) ((Tf ^ k) x))
            rw [← pow_succ']
          · simp [Module.End.one_eq_id]

/-- The positive-power specialization stated in Paper II. -/
theorem power_defect_identity
    (C : Xf →ₗ[R] Xc) (Tf : Module.End R Xf) (Tc : Module.End R Xc)
    (n : ℕ) (_hn : 0 < n) :
    C.comp (Tf ^ n) - (Tc ^ n).comp C =
      ∑ k ∈ Finset.range n,
        (Tc ^ (n - 1 - k)).comp ((defect C Tf Tc).comp (Tf ^ k)) :=
  power_defect_identity_all C Tf Tc n

/-- A zero one-step defect gives exact compatibility with every power. -/
theorem powers_compatible_of_defect_eq_zero
    (C : Xf →ₗ[R] Xc) (Tf : Module.End R Xf) (Tc : Module.End R Xc)
    (hdefect : defect C Tf Tc = 0) (n : ℕ) :
    C.comp (Tf ^ n) = (Tc ^ n).comp C := by
  apply sub_eq_zero.mp
  rw [power_defect_identity_all]
  simp [hdefect]

/-! ## Typed polynomial functional calculus -/

/-- The finite polynomial functional calculus for a module endomorphism.

This explicit coefficient sum works for a possibly noncommutative
endomorphism ring; its scalar coefficients act centrally because the base
ring is commutative.
-/
def polynomialAction
    {S : Type*} [CommSemiring S]
    {M : Type*} [AddCommMonoid M] [Module S M]
    (p : Polynomial S) (T : Module.End S M) : Module.End S M :=
  p.sum fun n a => a • T ^ n

/-- Exact one-step intertwining implies compatibility with every polynomial
in the fine and coarse operators. -/
theorem polynomialAction_compatible_of_defect_eq_zero
    {S : Type*} [CommSemiring S]
    {Mf : Type v} {Mc : Type w}
    [AddCommGroup Mf] [AddCommGroup Mc] [Module S Mf] [Module S Mc]
    (C : Mf →ₗ[S] Mc) (Tf : Module.End S Mf) (Tc : Module.End S Mc)
    (hdefect : defect C Tf Tc = 0) (p : Polynomial S) :
    C.comp (polynomialAction p Tf) =
      (polynomialAction p Tc).comp C := by
  classical
  ext x
  simp only [polynomialAction, Polynomial.sum_def, LinearMap.comp_apply,
    LinearMap.sum_apply, map_sum, LinearMap.smul_apply, map_smul]
  apply Finset.sum_congr rfl
  intro n hn
  rw [show C ((Tf ^ n) x) = (Tc ^ n) (C x) by
    exact LinearMap.congr_fun
      (powers_compatible_of_defect_eq_zero C Tf Tc hdefect n) x]

/-! ## Continuous linear maps and the operator-norm bound -/

variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {Ef : Type v} {Ec : Type w}
variable [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
variable [NormedSpace 𝕜 Ef] [NormedSpace 𝕜 Ec]

/-- The genuinely typed continuous defect `C ∘ Tf - Tc ∘ C`. -/
def continuousDefect (C : Ef →L[𝕜] Ec)
    (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) : Ef →L[𝕜] Ec :=
  C.comp Tf - Tc.comp C

/-- Forgetting continuity sends the continuous defect to the algebraic typed
defect without changing the formula. -/
@[simp]
theorem continuousDefect_toLinearMap
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) :
    (continuousDefect C Tf Tc : Ef →ₗ[𝕜] Ec) =
      defect C.toLinearMap Tf.toLinearMap Tc.toLinearMap := by
  rfl

/-- The continuous-linear-map power-defect identity for every natural power.

The proof is a faithful bridge to `power_defect_identity_all`; injectivity of
the forgetful map shows that no continuity information is lost.
-/
theorem continuous_power_defect_identity_all
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (n : ℕ) :
    C.comp (Tf ^ n) - (Tc ^ n).comp C =
      ∑ k ∈ Finset.range n,
        (Tc ^ (n - 1 - k)).comp
          ((continuousDefect C Tf Tc).comp (Tf ^ k)) := by
  apply ContinuousLinearMap.coe_injective
  simpa only [ContinuousLinearMap.toLinearMap_sub,
    ContinuousLinearMap.toLinearMap_comp,
    ContinuousLinearMap.toLinearMap_pow,
    ContinuousLinearMap.toLinearMap_sum,
    continuousDefect_toLinearMap] using
    (power_defect_identity_all C.toLinearMap Tf.toLinearMap Tc.toLinearMap n)

/-- The positive-power continuous specialization stated in the manuscript. -/
theorem continuous_power_defect_identity
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (n : ℕ) (_hn : 0 < n) :
    C.comp (Tf ^ n) - (Tc ^ n).comp C =
      ∑ k ∈ Finset.range n,
        (Tc ^ (n - 1 - k)).comp
          ((continuousDefect C Tf Tc).comp (Tf ^ k)) :=
  continuous_power_defect_identity_all C Tf Tc n

/-- Powers of a continuous endomorphism satisfy the usual operator-norm
bound, including exponent zero.  The zero case uses `‖id‖ ≤ 1`, so this
does not require the state space to be nontrivial. -/
theorem continuous_end_pow_norm_le
    {E : Type v} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
    (T : E →L[𝕜] E) (n : ℕ) :
    ‖T ^ n‖ ≤ ‖T‖ ^ n := by
  cases n with
  | zero =>
      simpa only [pow_zero, ContinuousLinearMap.one_def] using
        (ContinuousLinearMap.norm_id_le (𝕜 := 𝕜) (E := E))
  | succ n =>
      exact norm_pow_le' T (Nat.succ_pos n)

/-- The manuscript's typed operator-norm power-defect estimate. -/
theorem continuous_norm_power_defect_le
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (n : ℕ) :
    ‖C.comp (Tf ^ n) - (Tc ^ n).comp C‖ ≤
      ‖continuousDefect C Tf Tc‖ *
        ∑ k ∈ Finset.range n, ‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k := by
  rw [continuous_power_defect_identity_all]
  calc
    ‖∑ k ∈ Finset.range n,
        (Tc ^ (n - 1 - k)).comp
          ((continuousDefect C Tf Tc).comp (Tf ^ k))‖ ≤
        ∑ k ∈ Finset.range n,
          ‖(Tc ^ (n - 1 - k)).comp
            ((continuousDefect C Tf Tc).comp (Tf ^ k))‖ :=
      norm_sum_le _ _
    _ ≤ ∑ k ∈ Finset.range n,
          ‖continuousDefect C Tf Tc‖ *
            (‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k) := by
      apply Finset.sum_le_sum
      intro k _hk
      calc
        ‖(Tc ^ (n - 1 - k)).comp
            ((continuousDefect C Tf Tc).comp (Tf ^ k))‖ ≤
            ‖Tc ^ (n - 1 - k)‖ *
              ‖(continuousDefect C Tf Tc).comp (Tf ^ k)‖ :=
          ContinuousLinearMap.opNorm_comp_le _ _
        _ ≤ ‖Tc ^ (n - 1 - k)‖ *
              (‖continuousDefect C Tf Tc‖ * ‖Tf ^ k‖) :=
          mul_le_mul_of_nonneg_left
            (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _)
        _ ≤ ‖Tc‖ ^ (n - 1 - k) *
              (‖continuousDefect C Tf Tc‖ * ‖Tf ^ k‖) :=
          mul_le_mul_of_nonneg_right
            (continuous_end_pow_norm_le Tc (n - 1 - k))
            (mul_nonneg (norm_nonneg _) (norm_nonneg _))
        _ ≤ ‖Tc‖ ^ (n - 1 - k) *
              (‖continuousDefect C Tf Tc‖ * ‖Tf‖ ^ k) :=
          mul_le_mul_of_nonneg_left
            (mul_le_mul_of_nonneg_left
              (continuous_end_pow_norm_le Tf k) (norm_nonneg _))
            (pow_nonneg (norm_nonneg _) _)
        _ = ‖continuousDefect C Tf Tc‖ *
              (‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k) := by
          ac_rfl
    _ = ‖continuousDefect C Tf Tc‖ *
          ∑ k ∈ Finset.range n, ‖Tc‖ ^ (n - 1 - k) * ‖Tf‖ ^ k := by
      rw [Finset.mul_sum]

/-- If both dynamics have operator norm at most `ρ`, the `n`th typed defect
is bounded by the familiar linear-loss majorant
`n * ρ^(n-1) * ‖continuousDefect C Tf Tc‖`.

The statement includes `n = 0`, where both sides vanish.
-/
theorem continuous_norm_power_defect_le_geometric_majorant
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (ρ : ℝ) (hTf : ‖Tf‖ ≤ ρ) (hTc : ‖Tc‖ ≤ ρ) (n : ℕ) :
    ‖C.comp (Tf ^ n) - (Tc ^ n).comp C‖ ≤
      (n : ℝ) * ρ ^ (n - 1) * ‖continuousDefect C Tf Tc‖ := by
  cases n with
  | zero => simp [ContinuousLinearMap.one_def]
  | succ n =>
      have hρ : 0 ≤ ρ := (norm_nonneg Tf).trans hTf
      calc
        ‖C.comp (Tf ^ (n + 1)) - (Tc ^ (n + 1)).comp C‖ ≤
            ‖continuousDefect C Tf Tc‖ *
              ∑ k ∈ Finset.range (n + 1),
                ‖Tc‖ ^ (n + 1 - 1 - k) * ‖Tf‖ ^ k :=
          continuous_norm_power_defect_le C Tf Tc (n + 1)
        _ ≤ ‖continuousDefect C Tf Tc‖ *
              ∑ _k ∈ Finset.range (n + 1), ρ ^ n := by
          apply mul_le_mul_of_nonneg_left _ (norm_nonneg _)
          apply Finset.sum_le_sum
          intro k hk
          have hklt : k < n + 1 := Finset.mem_range.mp hk
          calc
            ‖Tc‖ ^ (n + 1 - 1 - k) * ‖Tf‖ ^ k ≤
                ρ ^ (n + 1 - 1 - k) * ρ ^ k := by
              exact mul_le_mul
                (pow_le_pow_left₀ (norm_nonneg Tc) hTc _)
                (pow_le_pow_left₀ (norm_nonneg Tf) hTf _)
                (pow_nonneg (norm_nonneg Tf) _) (pow_nonneg hρ _)
            _ = ρ ^ n := by
              rw [← pow_add]
              congr 1
              omega
        _ = (n + 1 : ℕ) * ρ ^ n * ‖continuousDefect C Tf Tc‖ := by
          simp only [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
          push_cast
          ring
        _ = ((n + 1 : ℕ) : ℝ) * ρ ^ ((n + 1 : ℕ) - 1) *
              ‖continuousDefect C Tf Tc‖ := by simp

/-- A continuous zero defect gives exact compatibility with every power. -/
theorem continuous_powers_compatible_of_defect_eq_zero
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (hdefect : continuousDefect C Tf Tc = 0) (n : ℕ) :
    C.comp (Tf ^ n) = (Tc ^ n).comp C := by
  apply sub_eq_zero.mp
  rw [continuous_power_defect_identity_all]
  simp [hdefect]

/-- The finite polynomial functional calculus for a continuous
endomorphism. -/
def continuousPolynomialAction
    {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
    (p : Polynomial 𝕜) (T : E →L[𝕜] E) : E →L[𝕜] E :=
  p.sum fun n a => a • T ^ n

/-- Vanishing continuous defect makes the coarsening map intertwine the
polynomial functional calculi of the fine and coarse dynamics. -/
theorem continuousPolynomialAction_compatible_of_defect_eq_zero
    (C : Ef →L[𝕜] Ec) (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec)
    (hdefect : continuousDefect C Tf Tc = 0) (p : Polynomial 𝕜) :
    C.comp (continuousPolynomialAction p Tf) =
      (continuousPolynomialAction p Tc).comp C := by
  classical
  ext x
  simp only [continuousPolynomialAction, Polynomial.sum_def,
    ContinuousLinearMap.comp_apply, sum_apply, map_sum, smul_apply, map_smul]
  apply Finset.sum_congr rfl
  intro n hn
  rw [show C ((Tf ^ n) x) = (Tc ^ n) (C x) by
    have h := continuous_powers_compatible_of_defect_eq_zero
      C Tf Tc hdefect n
    exact congrArg (fun F : Ef →L[𝕜] Ec => F x) h]

/-! ## Typed inverse sandwiches and resolvents -/

/-- An explicitly supplied two-sided inverse of a module endomorphism. -/
structure TwoSidedInverse {M : Type*} [AddCommGroup M] [Module R M]
    (A Ainv : Module.End R M) : Prop where
  left_inv : Ainv.comp A = LinearMap.id
  right_inv : A.comp Ainv = LinearMap.id

/-- The inverse-sandwich identity with different fine and coarse modules. -/
theorem inverse_sandwich_identity
    (A Ainv : Module.End R Xc) (B Binv : Module.End R Xf)
    (C : Xf →ₗ[R] Xc)
    (hA : TwoSidedInverse A Ainv)
    (hB : TwoSidedInverse B Binv) :
    C.comp Binv - Ainv.comp C =
      (Ainv.comp (A.comp C - C.comp B)).comp Binv := by
  calc
    C.comp Binv - Ainv.comp C =
        (Ainv.comp A).comp (C.comp Binv) -
          (Ainv.comp C).comp (B.comp Binv) := by
      rw [hA.left_inv, hB.right_inv]
      simp
    _ = (Ainv.comp (A.comp C - C.comp B)).comp Binv := by
      ext x
      simp only [LinearMap.sub_apply, LinearMap.comp_apply, map_sub]

/-- The endomorphism `z · id - T`. -/
def scalarShift {S : Type*} [CommSemiring S]
    {M : Type*} [AddCommGroup M] [Module S M]
    (z : S) (T : Module.End S M) : Module.End S M :=
  z • (1 : Module.End S M) - T

/-- The difference of the two typed scalar-shift composites is precisely the
one-step defect. -/
theorem scalarShift_comp_sub_comp_scalarShift
    {S : Type*} [CommSemiring S]
    {Mf : Type v} {Mc : Type w}
    [AddCommGroup Mf] [AddCommGroup Mc] [Module S Mf] [Module S Mc]
    (z : S) (C : Mf →ₗ[S] Mc)
    (Tf : Module.End S Mf) (Tc : Module.End S Mc) :
    (scalarShift z Tc).comp C - C.comp (scalarShift z Tf) =
      defect C Tf Tc := by
  ext x
  simp only [scalarShift, defect, LinearMap.sub_apply, LinearMap.comp_apply,
    LinearMap.smul_apply, Module.End.one_apply, map_sub, map_smul]
  abel

/-- The typed scalar-shift resolvent identity.

`Rf` and `Rc` are concrete inverse candidates, and the two hypotheses expose
both inverse equations rather than relying on a partial inverse operation.
-/
theorem scalarShift_resolvent_identity
    {S : Type*} [CommSemiring S]
    {Mf : Type v} {Mc : Type w}
    [AddCommGroup Mf] [AddCommGroup Mc] [Module S Mf] [Module S Mc]
    (z : S) (C : Mf →ₗ[S] Mc)
    (Tf Rf : Module.End S Mf) (Tc Rc : Module.End S Mc)
    (hf : TwoSidedInverse (scalarShift z Tf) Rf)
    (hc : TwoSidedInverse (scalarShift z Tc) Rc) :
    C.comp Rf - Rc.comp C =
      (Rc.comp (defect C Tf Tc)).comp Rf := by
  calc
    C.comp Rf - Rc.comp C =
        (Rc.comp
          ((scalarShift z Tc).comp C - C.comp (scalarShift z Tf))).comp Rf :=
      inverse_sandwich_identity
        (scalarShift z Tc) Rc (scalarShift z Tf) Rf C hc hf
    _ = (Rc.comp (defect C Tf Tc)).comp Rf := by
      rw [scalarShift_comp_sub_comp_scalarShift]

/-- With zero defect, the explicitly witnessed fine and coarse resolvents
intertwine exactly. -/
theorem resolvents_compatible_of_defect_eq_zero
    {S : Type*} [CommSemiring S]
    {Mf : Type v} {Mc : Type w}
    [AddCommGroup Mf] [AddCommGroup Mc] [Module S Mf] [Module S Mc]
    (z : S) (C : Mf →ₗ[S] Mc)
    (Tf Rf : Module.End S Mf) (Tc Rc : Module.End S Mc)
    (hf : TwoSidedInverse (scalarShift z Tf) Rf)
    (hc : TwoSidedInverse (scalarShift z Tc) Rc)
    (hdefect : defect C Tf Tc = 0) :
    C.comp Rf = Rc.comp C := by
  apply sub_eq_zero.mp
  rw [scalarShift_resolvent_identity z C Tf Rf Tc Rc hf hc, hdefect]
  simp

/-! ## Continuous typed resolvents and their norm estimate -/

/-- The continuous endomorphism `z · id - T`. -/
def continuousScalarShift
    (z : 𝕜) {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
    (T : E →L[𝕜] E) : E →L[𝕜] E :=
  z • (1 : E →L[𝕜] E) - T

/-- The continuous scalar-shift commutator is the one-step defect. -/
theorem continuousScalarShift_comp_sub_comp_continuousScalarShift
    (z : 𝕜) (C : Ef →L[𝕜] Ec)
    (Tf : Ef →L[𝕜] Ef) (Tc : Ec →L[𝕜] Ec) :
    (continuousScalarShift z Tc).comp C -
        C.comp (continuousScalarShift z Tf) =
      continuousDefect C Tf Tc := by
  ext x
  simp only [continuousScalarShift, continuousDefect,
    sub_apply, ContinuousLinearMap.comp_apply, smul_apply, one_apply_eq_self,
    map_sub, map_smul]
  abel

/-- The continuous inverse sandwich needs only the two one-sided inverse
equations that actually occur in the calculation: a left inverse for `A`
and a right inverse for `B`. -/
theorem continuous_inverse_sandwich_identity
    (A Ainv : Ec →L[𝕜] Ec) (B Binv : Ef →L[𝕜] Ef)
    (C : Ef →L[𝕜] Ec)
    (hA : Ainv.comp A = 1) (hB : B.comp Binv = 1) :
    C.comp Binv - Ainv.comp C =
      (Ainv.comp (A.comp C - C.comp B)).comp Binv := by
  calc
    C.comp Binv - Ainv.comp C =
        (Ainv.comp A).comp (C.comp Binv) -
          (Ainv.comp C).comp (B.comp Binv) := by
      ext x
      simp only [sub_apply, ContinuousLinearMap.comp_apply]
      have hAx : Ainv (A (C (Binv x))) = C (Binv x) := by
        have h := congrArg (fun F : Ec →L[𝕜] Ec => F (C (Binv x))) hA
        simpa only [ContinuousLinearMap.comp_apply,
          one_apply_eq_self] using h
      have hBx : B (Binv x) = x := by
        have h := congrArg (fun F : Ef →L[𝕜] Ef => F x) hB
        simpa only [ContinuousLinearMap.comp_apply,
          one_apply_eq_self] using h
      rw [hAx, hBx]
    _ = (Ainv.comp (A.comp C - C.comp B)).comp Binv := by
      ext x
      simp only [sub_apply, ContinuousLinearMap.comp_apply, map_sub]

/-- The continuous typed resolvent identity from explicit one-sided inverse
witnesses.  No global inverse operation or spectral hypothesis is hidden in
the statement. -/
theorem continuous_scalarShift_resolvent_identity
    (z : 𝕜) (C : Ef →L[𝕜] Ec)
    (Tf Rf : Ef →L[𝕜] Ef) (Tc Rc : Ec →L[𝕜] Ec)
    (hf : (continuousScalarShift z Tf).comp Rf = 1)
    (hc : Rc.comp (continuousScalarShift z Tc) = 1) :
    C.comp Rf - Rc.comp C =
      (Rc.comp (continuousDefect C Tf Tc)).comp Rf := by
  calc
    C.comp Rf - Rc.comp C =
        (Rc.comp
          ((continuousScalarShift z Tc).comp C -
            C.comp (continuousScalarShift z Tf))).comp Rf :=
      continuous_inverse_sandwich_identity
        (continuousScalarShift z Tc) Rc
        (continuousScalarShift z Tf) Rf C hc hf
    _ = (Rc.comp (continuousDefect C Tf Tc)).comp Rf := by
      rw [continuousScalarShift_comp_sub_comp_continuousScalarShift]

/-- The analytic resolvent-defect estimate
`‖C Rf - Rc C‖ ≤ ‖Rc‖ ‖Δ‖ ‖Rf‖`. -/
theorem continuous_norm_resolvent_defect_le
    (z : 𝕜) (C : Ef →L[𝕜] Ec)
    (Tf Rf : Ef →L[𝕜] Ef) (Tc Rc : Ec →L[𝕜] Ec)
    (hf : (continuousScalarShift z Tf).comp Rf = 1)
    (hc : Rc.comp (continuousScalarShift z Tc) = 1) :
    ‖C.comp Rf - Rc.comp C‖ ≤
      ‖Rc‖ * ‖continuousDefect C Tf Tc‖ * ‖Rf‖ := by
  rw [continuous_scalarShift_resolvent_identity z C Tf Rf Tc Rc hf hc]
  calc
    ‖(Rc.comp (continuousDefect C Tf Tc)).comp Rf‖ ≤
        ‖Rc.comp (continuousDefect C Tf Tc)‖ * ‖Rf‖ :=
      ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ (‖Rc‖ * ‖continuousDefect C Tf Tc‖) * ‖Rf‖ :=
      mul_le_mul_of_nonneg_right
        (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _)

/-- With zero continuous defect, the explicit fine and coarse resolvents
intertwine exactly. -/
theorem continuous_resolvents_compatible_of_defect_eq_zero
    (z : 𝕜) (C : Ef →L[𝕜] Ec)
    (Tf Rf : Ef →L[𝕜] Ef) (Tc Rc : Ec →L[𝕜] Ec)
    (hf : (continuousScalarShift z Tf).comp Rf = 1)
    (hc : Rc.comp (continuousScalarShift z Tc) = 1)
    (hdefect : continuousDefect C Tf Tc = 0) :
    C.comp Rf = Rc.comp C := by
  apply sub_eq_zero.mp
  rw [continuous_scalarShift_resolvent_identity z C Tf Rf Tc Rc hf hc,
    hdefect]
  simp

end Komorebi.PaperII.TypedLinearDefects
