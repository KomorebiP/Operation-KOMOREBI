import Komorebi.SufficientResolution.ExactResolution
import Mathlib.LinearAlgebra.Quotient.Basic

/-!
# Exact behavioral quotient for arbitrary families of linear transformations

Words are chronological: `i :: w` applies `T i` first and then `w`.
The invisible submodule contains exactly the states producing zero observation
under every finite future word.  No finite-state truncation is used.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.Behavioral

universe uR uX uY uZ uI

variable {R : Type uR} [CommRing R]
variable {X : Type uX} [AddCommGroup X] [Module R X]
variable {Y : Type uY} [AddCommGroup Y] [Module R Y]
variable {I : Type uI}

/-- Chronological interpretation of a finite word. -/
def wordOp (T : I → X →ₗ[R] X) : List I → X →ₗ[R] X
  | [] => 1
  | i :: w => wordOp T w * T i

@[simp] theorem wordOp_nil (T : I → X →ₗ[R] X) : wordOp T [] = 1 := rfl

@[simp] theorem wordOp_cons (T : I → X →ₗ[R] X) (i : I) (w : List I) :
    wordOp T (i :: w) = wordOp T w * T i := rfl

 theorem wordOp_append (T : I → X →ₗ[R] X) (u v : List I) :
    wordOp T (u ++ v) = wordOp T v * wordOp T u := by
  induction u with
  | nil => simp
  | cons i u ih => simp [ih, mul_assoc]

variable (T : I → X →ₗ[R] X) (O : X →ₗ[R] Y)

/-- Permanently unobservable state, quantified over all future finite words. -/
def invisible : Submodule R X where
  carrier := {x | ∀ w : List I, O (wordOp T w x) = 0}
  zero_mem' := by simp
  add_mem' := by
    intro x y hx hy w
    simp only [map_add, hx w, hy w, add_zero]
  smul_mem' := by
    intro a x hx w
    simp only [map_smul, hx w, smul_zero]

 theorem mem_invisible_iff (x : X) :
    x ∈ invisible T O ↔ ∀ w : List I, O (wordOp T w x) = 0 := Iff.rfl

 theorem invisible_le_ker : invisible T O ≤ LinearMap.ker O := by
  intro x hx
  have h := hx []
  simpa using h

 theorem invisible_invariant (i : I) :
    invisible T O ≤ (invisible T O).comap (T i) := by
  intro x hx
  change ∀ w : List I, O (wordOp T w (T i x)) = 0
  intro w
  exact hx (i :: w)

/-- Every invariant submodule invisible now is invisible for every future. -/
 theorem invariant_submodule_le_invisible (M : Submodule R X)
    (hO : M ≤ LinearMap.ker O)
    (hT : ∀ i : I, M ≤ M.comap (T i)) : M ≤ invisible T O := by
  intro x hx
  change ∀ w : List I, O (wordOp T w x) = 0
  intro w
  have hi : ∀ (w : List I) (y : X), y ∈ M → wordOp T w y ∈ M := by
    intro w
    induction w with
    | nil => intro y hy; simpa using hy
    | cons i w ih =>
      intro y hy
      exact ih (T i y) (hT i hy)
  exact hO (hi w x hx)

/-- The quotient is an actual module, not only an observational equivalence relation. -/
abbrev State := X ⧸ invisible T O

/-- Canonical state quotient. -/
def quotientMap : X →ₗ[R] State T O := (invisible T O).mkQ

/-- Each allowed operation descends to the behavioral quotient. -/
def induced (i : I) : State T O →ₗ[R] State T O :=
  (invisible T O).mapQ (invisible T O) (T i) (invisible_invariant T O i)

/-- Observation descends as well. -/
def observation : State T O →ₗ[R] Y :=
  (invisible T O).liftQ O (invisible_le_ker T O)

@[simp] theorem induced_quotient (i : I) (x : X) :
    induced T O i (quotientMap T O x) = quotientMap T O (T i x) := rfl

@[simp] theorem observation_quotient (x : X) :
    observation T O (quotientMap T O x) = O x := rfl

 theorem induced_word_quotient (w : List I) (x : X) :
    wordOp (induced T O) w (quotientMap T O x) = quotientMap T O (wordOp T w x) := by
  induction w generalizing x with
  | nil => rfl
  | cons i w ih =>
    simp only [wordOp_cons, Module.End.mul_apply, induced_quotient, ih]

/-- Full observational fidelity holds at every finite future depth. -/
 theorem all_future_observations_preserved (w : List I) (x : X) :
    observation T O (wordOp (induced T O) w (quotientMap T O x)) =
      O (wordOp T w x) := by
  rw [induced_word_quotient, observation_quotient]

 theorem quotient_eq_iff_same_future (x y : X) :
    quotientMap T O x = quotientMap T O y ↔
      ∀ w : List I, O (wordOp T w x) = O (wordOp T w y) := by
  change (Submodule.Quotient.mk x : State T O) = Submodule.Quotient.mk y ↔ _
  rw [Submodule.Quotient.eq]
  change (∀ w : List I, O (wordOp T w (x - y)) = 0) ↔ _
  simp only [map_sub, sub_eq_zero]

variable {Z : Type uZ} [AddCommGroup Z] [Module R Z]

/-- Any exact linear model can discard only states in the invisible submodule. -/
 theorem exact_model_kernel_le (q : X →ₗ[R] Z) (U : I → Z →ₗ[R] Z)
    (V : Z →ₗ[R] Y) (hT : ∀ i : I, q.comp (T i) = (U i).comp q)
    (hO : V.comp q = O) : LinearMap.ker q ≤ invisible T O := by
  apply invariant_submodule_le_invisible T O (LinearMap.ker q)
  · intro x hx
    change O x = 0
    have hi : V (q x) = O x := LinearMap.congr_fun hO x
    rw [← hi, (show q x = 0 from hx), map_zero]
  · intro i x hx
    change q (T i x) = 0
    have hi : q (T i x) = U i (q x) := LinearMap.congr_fun (hT i) x
    rw [hi, (show q x = 0 from hx), map_zero]

/-- Universal comparison from any such kernel quotient to the minimal state. -/
def modelQuotientComparison (q : X →ₗ[R] Z) (U : I → Z →ₗ[R] Z)
    (V : Z →ₗ[R] Y) (hT : ∀ i : I, q.comp (T i) = (U i).comp q)
    (hO : V.comp q = O) :
    (X ⧸ LinearMap.ker q) →ₗ[R] State T O :=
  (LinearMap.ker q).mapQ (invisible T O) LinearMap.id (by
    simpa using exact_model_kernel_le T O q U V hT hO)

 theorem modelQuotientComparison_mk (q : X →ₗ[R] Z) (U : I → Z →ₗ[R] Z)
    (V : Z →ₗ[R] Y) (hT : ∀ i : I, q.comp (T i) = (U i).comp q)
    (hO : V.comp q = O) (x : X) :
    modelQuotientComparison T O q U V hT hO (Submodule.Quotient.mk x) =
      quotientMap T O x := rfl

end Komorebi.SufficientResolution.Behavioral
