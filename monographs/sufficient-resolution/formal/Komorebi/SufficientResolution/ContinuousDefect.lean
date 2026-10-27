import Komorebi.SufficientResolution.VariationOfConstants
import Mathlib.Tactic.Abel

/-!
# Continuous approximate intertwining

The integral representation is derived by differentiating the two-sided
propagator. All exact identities hold for every real time (oriented integrals).
The analytic norm bounds in later modules restrict to nonnegative times.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousDefect

open ContinuousFlow
variable {X Z Y W : Type*}
variable [NormedAddCommGroup X] [NormedSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z] [CompleteSpace Z]
variable [NormedAddCommGroup Y] [NormedSpace ℝ Y]
variable [NormedAddCommGroup W] [NormedSpace ℝ W] [CompleteSpace W]

def generatorDefect (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) : X →L[ℝ] Z :=
  q.comp L - A.comp q

def evolutionDefect (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (t : ℝ) : X →L[ℝ] Z := q.comp (flow L t) - (flow A t).comp q

def transportKernel (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (t s : ℝ) : X →L[ℝ] Z :=
  (flow A (t-s)).comp ((generatorDefect q L A).comp (flow L s))

omit [CompleteSpace X] [CompleteSpace Z] in
@[simp] theorem evolutionDefect_zero (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) :
    evolutionDefect q L A 0 = 0 := by
  ext x
  simp [evolutionDefect]

theorem continuous_transportKernel (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (t : ℝ) : Continuous (transportKernel q L A t) :=
  ((continuous_flow A).comp (continuous_const.sub continuous_id)).clm_comp
    (continuous_const.clm_comp (continuous_flow L))

theorem continuous_evolutionDefect (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) : Continuous (evolutionDefect q L A) :=
  (continuous_const.clm_comp (continuous_flow L)).sub
    ((continuous_flow A).clm_comp continuous_const)

/-- The generator defect is the actual derivative of the evolution discrepancy at zero. -/
theorem derivative_at_zero (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) :
    HasDerivAt (evolutionDefect q L A) (generatorDefect q L A) 0 := by
  change HasDerivAt (fun t => q.comp (flow L t) - (flow A t).comp q)
    (q.comp L - A.comp q) 0
  simpa using!
    ((hasDerivAt_const (0:ℝ) q).clm_comp (hasDerivAt_flow L 0)).sub
      ((hasDerivAt_flow A 0).clm_comp (hasDerivAt_const (0:ℝ) q))

/-- Differentiated backward propagation; the middle discrepancy is derived. -/
theorem backward_derivative (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (t s : ℝ) :
    HasDerivAt (fun u => (flow A (t-u)).comp (q.comp (flow L u)))
      (transportKernel q L A t s) s := by
  have h := (hasDerivAt_backward_flow A t s).clm_comp
    ((hasDerivAt_const s q).clm_comp (hasDerivAt_flow L s))
  convert h using 1
  ext x
  simp [transportKernel, generatorDefect]
  abel

/-- Exact operator-valued Duhamel identity, with no assumed integral equation. -/
theorem duhamel (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) (t : ℝ) :
    evolutionDefect q L A t = ∫ s in (0:ℝ)..t, transportKernel q L A t s := by
  have h := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun s _ => backward_derivative q L A t s)
    ((continuous_transportKernel q L A t).intervalIntegrable 0 t)
  simpa [evolutionDefect, ContinuousLinearMap.one_def] using h.symm

/-- Exactness follows from a zero generator defect. -/
theorem exact_of_generatorDefect_zero (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (h : generatorDefect q L A = 0) (t : ℝ) :
    evolutionDefect q L A t = 0 := by
  rw [duhamel]
  simp [transportKernel, h]

/-- Conversely, all-time exactness forces the generator defect to vanish. -/
theorem generatorDefect_zero_iff (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) :
    generatorDefect q L A = 0 ↔ ∀ t, evolutionDefect q L A t = 0 := by
  constructor
  · exact fun h t => exact_of_generatorDefect_zero q L A h t
  · intro h
    have he : evolutionDefect q L A = fun _ => 0 := funext h
    exact (derivative_at_zero q L A).unique (he ▸ hasDerivAt_const (0:ℝ) (0 : X →L[ℝ] Z))

/-- Two consecutive intervals retain both sources of discrepancy. -/
theorem evolutionDefect_add (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (s t : ℝ) :
    evolutionDefect q L A (s+t) =
      (evolutionDefect q L A s).comp (flow L t) +
      (flow A s).comp (evolutionDefect q L A t) := by
  ext x
  simp only [evolutionDefect, flow_add, ContinuousLinearMap.comp_apply,
    sub_apply, add_apply, map_sub, mul_apply_eq_comp]
  abel

def outputDefect (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y) (t : ℝ) : X →L[ℝ] Y :=
  O.comp (flow L t) - V.comp ((flow A t).comp q)

omit [CompleteSpace X] [CompleteSpace Z] in
theorem output_decomposition (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y) (t : ℝ) :
    outputDefect q L A O V t = (O - V.comp q).comp (flow L t) +
      V.comp (evolutionDefect q L A t) := by
  ext x
  simp only [outputDefect, evolutionDefect, ContinuousLinearMap.comp_apply,
    sub_apply, add_apply, map_sub]
  abel

omit [CompleteSpace X] [CompleteSpace Z] in
theorem initialization_decomposition (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y) (t : ℝ) (x : X) (z : Z) :
    O (flow L t x) - V (flow A t z) = outputDefect q L A O V t x +
      V (flow A t (q x - z)) := by
  simp only [outputDefect, ContinuousLinearMap.comp_apply, sub_apply, map_sub]
  abel

omit [CompleteSpace X] [CompleteSpace Z] [CompleteSpace W] in
theorem generatorDefect_composite (q : X →L[ℝ] Z) (p : Z →L[ℝ] W)
    (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) (B : W →L[ℝ] W) :
    generatorDefect (p.comp q) L B = p.comp (generatorDefect q L A) +
      (generatorDefect p A B).comp q := by
  ext x
  simp only [generatorDefect, ContinuousLinearMap.comp_apply, sub_apply, add_apply, map_sub]
  abel

omit [CompleteSpace X] [CompleteSpace Z] [CompleteSpace W] in
theorem evolutionDefect_composite (q : X →L[ℝ] Z) (p : Z →L[ℝ] W)
    (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) (B : W →L[ℝ] W) (t : ℝ) :
    evolutionDefect (p.comp q) L B t = p.comp (evolutionDefect q L A t) +
      (evolutionDefect p A B t).comp q := by
  ext x
  simp only [evolutionDefect, ContinuousLinearMap.comp_apply, sub_apply, add_apply, map_sub]
  abel

end Komorebi.SufficientResolution.ContinuousDefect
