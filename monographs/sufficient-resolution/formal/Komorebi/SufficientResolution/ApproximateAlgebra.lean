import Komorebi.SufficientResolution.Behavioral
import Mathlib.Tactic.Abel

/-!
# Exact telescoping identities for imperfect behavioral models

Words are chronological, as in `Behavioral.wordOp`. No norm or smallness premise
is used in this module. A defect is a difference of actual linear maps.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.ApproximateAlgebra

open Behavioral

universe uR uX uZ uY uW uI
variable {R : Type uR} [CommRing R]
variable {X : Type uX} [AddCommGroup X] [Module R X]
variable {Z : Type uZ} [AddCommGroup Z] [Module R Z]
variable {Y : Type uY} [AddCommGroup Y] [Module R Y]
variable {W : Type uW} [AddCommGroup W] [Module R W]
variable {I : Type uI}

/-- Difference between compressing a true trajectory and evolving its compressed start. -/
def wordDefect (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (w : List I) : X →ₗ[R] Z :=
  q.comp (wordOp T w) - (wordOp U w).comp q

/-- One-step intertwining defect. -/
def stepDefect (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (i : I) : X →ₗ[R] Z :=
  q.comp (T i) - (U i).comp q

@[simp] theorem wordDefect_nil (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) : wordDefect q T U [] = 0 := by
  ext x
  simp [wordDefect]

@[simp] theorem wordDefect_singleton (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (i : I) : wordDefect q T U [i] = stepDefect q T U i := by
  ext x
  simp [wordDefect, stepDefect]

/-- First operation acts first; the tail propagates its injected defect. -/
theorem wordDefect_cons (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (i : I) (w : List I) :
    wordDefect q T U (i :: w) =
      (wordDefect q T U w).comp (T i) + (wordOp U w).comp (stepDefect q T U i) := by
  ext x
  simp only [wordDefect, stepDefect, wordOp_cons, LinearMap.sub_apply,
    LinearMap.add_apply, LinearMap.comp_apply, Module.End.mul_apply, map_sub]
  abel

/-- Concatenation gives a two-sided defect propagation law. -/
theorem wordDefect_append (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (u v : List I) :
    wordDefect q T U (u ++ v) =
      (wordDefect q T U v).comp (wordOp T u) +
        (wordOp U v).comp (wordDefect q T U u) := by
  ext x
  simp only [wordDefect, wordOp_append, LinearMap.sub_apply,
    LinearMap.add_apply, LinearMap.comp_apply, Module.End.mul_apply, map_sub]
  abel

/-- One transported contribution per operation; represented without choosing a default letter. -/
def transportTerms (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) : List I → List (X →ₗ[R] Z)
  | [] => []
  | i :: w =>
    (transportTerms q T U w).map (fun d => d.comp (T i)) ++
      [(wordOp U w).comp (stepDefect q T U i)]

theorem transportTerms_length (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (w : List I) :
    (transportTerms q T U w).length = w.length := by
  induction w with
  | nil => rfl
  | cons i w ih => simp [transportTerms, ih]

theorem sum_comp_right (ds : List (X →ₗ[R] Z)) (t : X →ₗ[R] X) :
    (ds.map (fun d => d.comp t)).sum = ds.sum.comp t := by
  induction ds with
  | nil => simp
  | cons d ds ih =>
    simp only [List.map_cons, List.sum_cons, ih]
    ext x
    rfl

/-- Exact finite telescoping sum, for every finite word and arbitrary noncommuting operations. -/
theorem wordDefect_eq_sum (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (w : List I) :
    wordDefect q T U w = (transportTerms q T U w).sum := by
  induction w with
  | nil => simp [transportTerms]
  | cons i w ih =>
    rw [wordDefect_cons, transportTerms, List.sum_append, sum_comp_right, ← ih]
    simp

theorem wordDefect_eq_zero_of_steps (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (h : ∀ i, stepDefect q T U i = 0) (w : List I) :
    wordDefect q T U w = 0 := by
  induction w with
  | nil => simp
  | cons i w ih => simp [wordDefect_cons, ih, h]

/-- Readout error and state-model error are different summands. -/
theorem output_defect_decomposition (q : X →ₗ[R] Z) (T : I → X →ₗ[R] X)
    (U : I → Z →ₗ[R] Z) (O : X →ₗ[R] Y) (V : Z →ₗ[R] Y) (w : List I) :
    O.comp (wordOp T w) - V.comp ((wordOp U w).comp q) =
      (O - V.comp q).comp (wordOp T w) + V.comp (wordDefect q T U w) := by
  ext x
  simp only [wordDefect, LinearMap.sub_apply, LinearMap.add_apply,
    LinearMap.comp_apply, map_sub]
  abel

/-- Comparison maps can themselves be composed without hiding intermediate defects. -/
theorem wordDefect_two_stage (q : X →ₗ[R] Z) (p : Z →ₗ[R] W)
    (T : I → X →ₗ[R] X) (U : I → Z →ₗ[R] Z) (S : I → W →ₗ[R] W) (w : List I) :
    wordDefect (p.comp q) T S w =
      p.comp (wordDefect q T U w) + (wordDefect p U S w).comp q := by
  ext x
  simp only [wordDefect, LinearMap.sub_apply, LinearMap.add_apply,
    LinearMap.comp_apply, map_sub]
  abel

theorem stepDefect_two_stage (q : X →ₗ[R] Z) (p : Z →ₗ[R] W)
    (T : I → X →ₗ[R] X) (U : I → Z →ₗ[R] Z) (S : I → W →ₗ[R] W) (i : I) :
    stepDefect (p.comp q) T S i =
      p.comp (stepDefect q T U i) + (stepDefect p U S i).comp q := by
  simpa using wordDefect_two_stage q p T U S [i]

/-- Splitting need not be orthogonal: the state defect is the discarded-input return map. -/
theorem split_step_defect (C : X →ₗ[R] Z) (R' : Z →ₗ[R] X) (t : X →ₗ[R] X) :
    C.comp t - (C.comp (t.comp R')).comp C =
      C.comp (t.comp (LinearMap.id - R'.comp C)) := by
  ext x
  simp [map_sub]

end Komorebi.SufficientResolution.ApproximateAlgebra
