import KomorebiVerification.PaperII.TypedLinearDefects
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Data.Nat.Basic

set_option autoImplicit false
namespace Komorebi.PaperII.ReleaseDefectTower
open scoped BigOperators
open TypedLinearDefects
universe u v

section Algebraic
variable {R : Type u} [Semiring R]
variable {X : ℕ → Type v} [∀ n, AddCommGroup (X n)] [∀ n, Module R (X n)]

/-- The actual ordered composite C_a C_(a+1) ... C_(b-1).
The dependent source and target retain every state space of the tower. -/
def segment (C : ∀ n, X (n + 1) →ₗ[R] X n) {a b : ℕ} (h : a ≤ b) :
    X b →ₗ[R] X a :=
  Nat.leRecOn (C := fun n => X n →ₗ[R] X a) h
    (fun {n} f => f.comp (C n)) LinearMap.id

@[simp] theorem segment_self (C : ∀ n, X (n + 1) →ₗ[R] X n) (a : ℕ) :
    segment C (Nat.le_refl a) = LinearMap.id := by
  exact Nat.leRecOn_self _

theorem segment_succ (C : ∀ n, X (n + 1) →ₗ[R] X n)
    {a b : ℕ} (h : a ≤ b) (hs : a ≤ b + 1) :
    segment C hs = (segment C h).comp (C b) := by
  exact Nat.leRecOn_succ h _

/-- Each summand is the local defect transported by the actual preceding and
following comparison composites. -/
def localTerm (C : ∀ n, X (n + 1) →ₗ[R] X n)
    (T : ∀ n, Module.End R (X n)) (L : ℕ) (k : Fin L) : X L →ₗ[R] X 0 :=
  (segment C (Nat.zero_le k.val)).comp
    ((defect (C k.val) (T (k.val + 1)) (T k.val)).comp
      (segment C (Nat.succ_le_of_lt k.isLt)))

/-- Arbitrary-length typed multilevel defect decomposition, including L=0. -/
theorem multilevel_defect (C : ∀ n, X (n + 1) →ₗ[R] X n)
    (T : ∀ n, Module.End R (X n)) (L : ℕ) :
    (segment C (Nat.zero_le L)).comp (T L) -
        (T 0).comp (segment C (Nat.zero_le L)) =
      ∑ k : Fin L, localTerm C T L k := by
  induction L with
  | zero => simp [localTerm]
  | succ L ih =>
      have hrec :
          (segment C (Nat.zero_le (L + 1))).comp (T (L + 1)) -
              (T 0).comp (segment C (Nat.zero_le (L + 1))) =
            ((segment C (Nat.zero_le L)).comp (T L) -
              (T 0).comp (segment C (Nat.zero_le L))).comp (C L) +
              (segment C (Nat.zero_le L)).comp (defect (C L) (T (L + 1)) (T L)) := by
        rw [segment_succ C (Nat.zero_le L)]
        ext x
        simp only [LinearMap.comp_apply, LinearMap.sub_apply,
          LinearMap.add_apply, defect, map_sub]
        abel
      rw [hrec, ih, Fin.sum_univ_castSucc]
      congr 1
      · ext x
        simp only [LinearMap.comp_apply, LinearMap.sum_apply]
        apply Finset.sum_congr rfl
        intro k hk
        simp only [localTerm, Fin.val_castSucc]
        rw [segment_succ C (Nat.succ_le_of_lt k.isLt)]
        rfl
      · simp [localTerm]

/-- Zero local defects imply a zero total defect. -/
theorem multilevel_compatible (C : ∀ n, X (n + 1) →ₗ[R] X n)
    (T : ∀ n, Module.End R (X n)) (L : ℕ)
    (h : ∀ k : Fin L, defect (C k.val) (T (k.val + 1)) (T k.val) = 0) :
    (segment C (Nat.zero_le L)).comp (T L) =
      (T 0).comp (segment C (Nat.zero_le L)) := by
  apply sub_eq_zero.mp
  rw [multilevel_defect]
  apply Finset.sum_eq_zero
  intro k hk
  simp [localTerm, h k]
/-- The polynomial consequence at arbitrary tower depth. -/
theorem multilevel_polynomial_compatible
    {S : Type*} [CommSemiring S]
    {Y : ℕ → Type*} [∀ n, AddCommGroup (Y n)] [∀ n, Module S (Y n)]
    (C : ∀ n, Y (n + 1) →ₗ[S] Y n) (T : ∀ n, Module.End S (Y n))
    (L : ℕ) (h : ∀ k : Fin L, defect (C k.val) (T (k.val + 1)) (T k.val) = 0)
    (p : Polynomial S) :
    (segment C (Nat.zero_le L)).comp (polynomialAction p (T L)) =
      (polynomialAction p (T 0)).comp (segment C (Nat.zero_le L)) := by
  apply polynomialAction_compatible_of_defect_eq_zero
  exact sub_eq_zero.mpr (multilevel_compatible C T L h)
end Algebraic

section Continuous
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {X : ℕ → Type v}
variable [∀ n, NormedAddCommGroup (X n)] [∀ n, NormedSpace 𝕜 (X n)]

/-- The bounded actual segment composite in a typed tower. -/
def continuousSegment (C : ∀ n, X (n + 1) →L[𝕜] X n) {a b : ℕ} (h : a ≤ b) :
    X b →L[𝕜] X a :=
  Nat.leRecOn (C := fun n => X n →L[𝕜] X a) h
    (fun {n} f => f.comp (C n)) (ContinuousLinearMap.id 𝕜 (X a))

@[simp] theorem continuousSegment_self
    (C : ∀ n, X (n + 1) →L[𝕜] X n) (a : ℕ) :
    continuousSegment C (Nat.le_refl a) = ContinuousLinearMap.id 𝕜 (X a) := by
  exact Nat.leRecOn_self _

theorem continuousSegment_succ (C : ∀ n, X (n + 1) →L[𝕜] X n)
    {a b : ℕ} (h : a ≤ b) (hs : a ≤ b + 1) :
    continuousSegment C hs = (continuousSegment C h).comp (C b) := by
  exact Nat.leRecOn_succ h _

@[simp] theorem continuousSegment_toLinearMap
    (C : ∀ n, X (n + 1) →L[𝕜] X n) {a b : ℕ} (h : a ≤ b) :
    (continuousSegment C h).toLinearMap = segment (fun n => (C n).toLinearMap) h := by
  induction b, h using Nat.le_induction with
  | base => simp
  | succ b hab ih =>
      rw [continuousSegment_succ C hab, segment_succ _ hab]
      simp only [ContinuousLinearMap.toLinearMap_comp, ih]

/-- Normed local contribution with the same ordered factors as the manuscript. -/
def continuousLocalTerm (C : ∀ n, X (n + 1) →L[𝕜] X n)
    (T : ∀ n, X n →L[𝕜] X n) (L : ℕ) (k : Fin L) : X L →L[𝕜] X 0 :=
  (continuousSegment C (Nat.zero_le k.val)).comp
    ((continuousDefect (C k.val) (T (k.val + 1)) (T k.val)).comp
      (continuousSegment C (Nat.succ_le_of_lt k.isLt)))

/-- Continuous-map version of the arbitrary-length typed telescope. -/
theorem continuous_multilevel_defect (C : ∀ n, X (n + 1) →L[𝕜] X n)
    (T : ∀ n, X n →L[𝕜] X n) (L : ℕ) :
    (continuousSegment C (Nat.zero_le L)).comp (T L) -
        (T 0).comp (continuousSegment C (Nat.zero_le L)) =
      ∑ k : Fin L, continuousLocalTerm C T L k := by
  apply ContinuousLinearMap.coe_injective
  simpa only [ContinuousLinearMap.toLinearMap_sub,
    ContinuousLinearMap.toLinearMap_comp, ContinuousLinearMap.toLinearMap_sum,
    continuousSegment_toLinearMap, continuousLocalTerm, localTerm,
    continuousDefect_toLinearMap] using
    (multilevel_defect (fun n => (C n).toLinearMap) (fun n => (T n).toLinearMap) L)

/-- The multilevel norm estimate retains norms of the actual whole composites. -/
theorem continuous_norm_multilevel_defect_le
    (C : ∀ n, X (n + 1) →L[𝕜] X n)
    (T : ∀ n, X n →L[𝕜] X n) (L : ℕ) :
    ‖(continuousSegment C (Nat.zero_le L)).comp (T L) -
        (T 0).comp (continuousSegment C (Nat.zero_le L))‖ ≤
      ∑ k : Fin L, ‖continuousSegment C (Nat.zero_le k.val)‖ *
        ‖continuousDefect (C k.val) (T (k.val + 1)) (T k.val)‖ *
        ‖continuousSegment C (Nat.succ_le_of_lt k.isLt)‖ := by
  rw [continuous_multilevel_defect]
  refine (norm_sum_le _ _).trans ?_
  apply Finset.sum_le_sum
  intro k hk
  unfold continuousLocalTerm
  calc
    _ ≤ ‖continuousSegment C (Nat.zero_le k.val)‖ *
        ‖(continuousDefect (C k.val) (T (k.val + 1)) (T k.val)).comp
          (continuousSegment C (Nat.succ_le_of_lt k.isLt))‖ :=
      ContinuousLinearMap.opNorm_comp_le _ _
    _ ≤ ‖continuousSegment C (Nat.zero_le k.val)‖ *
        (‖continuousDefect (C k.val) (T (k.val + 1)) (T k.val)‖ *
          ‖continuousSegment C (Nat.succ_le_of_lt k.isLt)‖) :=
      mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _)
    _ = _ := (mul_assoc _ _ _).symm
/-- Vanishing local continuous defects imply exact total compatibility. -/
theorem continuous_multilevel_compatible
    (C : ∀ n, X (n + 1) →L[𝕜] X n) (T : ∀ n, X n →L[𝕜] X n)
    (L : ℕ) (h : ∀ k : Fin L,
      continuousDefect (C k.val) (T (k.val + 1)) (T k.val) = 0) :
    (continuousSegment C (Nat.zero_le L)).comp (T L) =
      (T 0).comp (continuousSegment C (Nat.zero_le L)) := by
  apply sub_eq_zero.mp
  rw [continuous_multilevel_defect]
  apply Finset.sum_eq_zero
  intro k hk
  simp [continuousLocalTerm, h k]

/-- Arbitrary-depth continuous polynomial compatibility. -/
theorem continuous_multilevel_polynomial_compatible
    (C : ∀ n, X (n + 1) →L[𝕜] X n) (T : ∀ n, X n →L[𝕜] X n)
    (L : ℕ) (h : ∀ k : Fin L,
      continuousDefect (C k.val) (T (k.val + 1)) (T k.val) = 0)
    (p : Polynomial 𝕜) :
    (continuousSegment C (Nat.zero_le L)).comp (continuousPolynomialAction p (T L)) =
      (continuousPolynomialAction p (T 0)).comp (continuousSegment C (Nat.zero_le L)) := by
  apply continuousPolynomialAction_compatible_of_defect_eq_zero
  exact sub_eq_zero.mpr (continuous_multilevel_compatible C T L h)

/-- Arbitrary-depth resolvent compatibility with explicit one-sided witnesses. -/
theorem continuous_multilevel_resolvents_compatible
    (C : ∀ n, X (n + 1) →L[𝕜] X n) (T : ∀ n, X n →L[𝕜] X n)
    (L : ℕ) (h : ∀ k : Fin L,
      continuousDefect (C k.val) (T (k.val + 1)) (T k.val) = 0)
    (z : 𝕜) (Rf : X L →L[𝕜] X L) (Rc : X 0 →L[𝕜] X 0)
    (hf : (continuousScalarShift z (T L)).comp Rf = 1)
    (hc : Rc.comp (continuousScalarShift z (T 0)) = 1) :
    (continuousSegment C (Nat.zero_le L)).comp Rf =
      Rc.comp (continuousSegment C (Nat.zero_le L)) := by
  apply continuous_resolvents_compatible_of_defect_eq_zero z _ (T L) Rf (T 0) Rc hf hc
  exact sub_eq_zero.mpr (continuous_multilevel_compatible C T L h)
end Continuous
end Komorebi.PaperII.ReleaseDefectTower
