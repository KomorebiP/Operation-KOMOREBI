import Komorebi.SufficientResolution.ExponentialTransfer
import Komorebi.SufficientResolution.SplitMemory

/-!
# Continuous certificates for arbitrary bounded split representations

Only the actual discarded space ker C must be finite-dimensional. Orthogonality
is not assumed. Coefficient identities are transported from the preserved
algebraic split-compression theorem through the analytic exponential bridge.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousFlow
variable {X Z : Type*}
variable [NormedAddCommGroup X] [NormedSpace ℝ X]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z]

 theorem compressed_power_eq_iff_linear (C : X →L[ℝ] Z) (R : Z →L[ℝ] X)
    (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) (n : ℕ) :
    C.comp ((L^n).comp R) = A^n ↔
      C.toLinearMap.comp ((L.toLinearMap^n).comp R.toLinearMap) = A.toLinearMap^n := by
  rw [← ContinuousLinearMap.coe_inj]
  simp only [ContinuousLinearMap.toLinearMap_comp, ContinuousLinearMap.toLinearMap_pow]

/-- The bounded representation has the same algebraic split as the original core. -/
def algebraicSplit (C : X →L[ℝ] Z) (R : Z →L[ℝ] X)
    (h : C.comp R = 1) : SplitCompression ℝ X Z where
  compress := C.toLinearMap
  lift := R.toLinearMap
  compress_lift := congrArg ContinuousLinearMap.toLinearMap h

variable [CompleteSpace X] [CompleteSpace Z]

/-- The finite certificate is sized by ker C, even for nonorthogonal splitting. -/
 theorem compressed_flow_iff_finite_generator (C : X →L[ℝ] Z) (R : Z →L[ℝ] X)
    (h : C.comp R = 1) (L : X →L[ℝ] X)
    [FiniteDimensional ℝ (LinearMap.ker C.toLinearMap)] :
    (∀ t, C.comp ((flow L t).comp R) = flow (C.comp (L.comp R)) t) ↔
      (∀ n ≤ Module.finrank ℝ (LinearMap.ker C.toLinearMap) + 1,
        C.comp ((L^n).comp R) = (C.comp (L.comp R))^n) := by
  rw [compressed_flow_iff_powers]
  simp only [compressed_power_eq_iff_linear, ContinuousLinearMap.toLinearMap_comp]
  let : FiniteDimensional ℝ (algebraicSplit C R h).HiddenSpace :=
    inferInstanceAs (FiniteDimensional ℝ (LinearMap.ker C.toLinearMap))
  exact (algebraicSplit C R h).exact_powers_iff_canonical_finite_horizon L.toLinearMap

omit [CompleteSpace X] [CompleteSpace Z] in
/-- An exact all-state intertwiner is automatically an intertwiner of every power. -/
 theorem intertwines_powers (C : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (h : C.comp L = A.comp C) (n : ℕ) : C.comp (L^n) = (A^n).comp C := by
  induction n with
  | zero => ext x; rfl
  | succ n ih =>
    ext x
    have hh := congrArg (fun F : X →L[ℝ] Z => F ((L^n) x)) h
    have hi := congrArg (fun F : X →L[ℝ] Z => F x) ih
    change C ((L^n) x) = (A^n) (C x) at hi
    change C (L ((L^n) x)) = A (C ((L^n) x)) at hh
    rw [hi] at hh
    simpa only [pow_succ', mul_apply_eq_comp, ContinuousLinearMap.comp_apply] using hh

/-- Exact all-state closure is equivalent to the generator intertwining equation. -/
 theorem intertwines_flow_iff_generators (C : X →L[ℝ] Z)
    (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) :
    (∀ t, C.comp (flow L t) = (flow A t).comp C) ↔ C.comp L = A.comp C := by
  have he := mapped_flow_eq_iff_powers_eq L A
    (sandwich C (ContinuousLinearMap.id ℝ X)) (sandwich (ContinuousLinearMap.id ℝ Z) C)
  simp only [sandwich_apply, ContinuousLinearMap.comp_id, ContinuousLinearMap.id_comp] at he
  constructor
  · intro h
    have hn := he.mp h 1
    simpa using hn
  · intro h
    exact he.mpr (intertwines_powers C L A h)

end Komorebi.SufficientResolution.ContinuousFlow
