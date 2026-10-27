import MachineTheory.Behavior
import Mathlib.Algebra.Module.LinearMap.End
import Mathlib.Algebra.Field.Defs

/-! Core v0.2, 2.1 and 2.3. Exact algebra and left-to-right forward transport. -/
namespace Komorebi.MachineTheory

/-- Local intertwining composes along arbitrary finite, left-to-right action words. -/
theorem forward_transport {X Y A B : Type*} (F : A → X → X) (G : B → Y → Y)
    (T : X → Y) (τ : A → B) (h : ∀ a x, T (F a x) = G (τ a) (T x))
    (word : List A) (x : X) : T (run F word x) = run G (word.map τ) (T x) := by
  induction word generalizing x with
  | nil => rfl
  | cons a word ih =>
    change T (run F word (F a x)) = run G (word.map τ) (G (τ a) (T x))
    rw [ih, h]

/-- Matched readouts must be an additional premise. -/
theorem forward_output {X Y A B O : Type*} (F : A → X → X) (G : B → Y → Y)
    (T : X → Y) (τ : A → B) (q : X → O) (qbar : Y → O)
    (h : ∀ a x, T (F a x) = G (τ a) (T x)) (hq : ∀ x, q x = qbar (T x))
    (word : List A) (x : X) : q (run F word x) = qbar (run G (word.map τ) (T x)) := by
  rw [hq, forward_transport F G T τ h]

/-- Restricting to an invariant subtype makes domain closure explicit. -/
theorem invariant_forward_transport {X Y A B : Type*} (D : Set X)
    (F : A → X → X) (G : B → Y → Y) (T : X → Y) (τ : A → B)
    (hD : ∀ a x, x ∈ D → F a x ∈ D)
    (h : ∀ a x, x ∈ D → T (F a x) = G (τ a) (T x))
    (word : List A) (x : X) (hx : x ∈ D) :
    T (run F word x) = run G (word.map τ) (T x) := by
  induction word generalizing x with
  | nil => rfl
  | cons a word ih =>
    change T (run F word (F a x)) = run G (word.map τ) (G (τ a) (T x))
    rw [ih (F a x) (hD a x hx), h a x hx]

/-- Output preservation on an invariant domain, including domain-restricted readout agreement. -/
theorem invariant_forward_output {X Y A B O : Type*} (D : Set X)
    (F : A → X → X) (G : B → Y → Y) (T : X → Y) (τ : A → B)
    (q : X → O) (qbar : Y → O)
    (hD : ∀ a x, x ∈ D → F a x ∈ D)
    (h : ∀ a x, x ∈ D → T (F a x) = G (τ a) (T x))
    (hq : ∀ x, x ∈ D → q x = qbar (T x))
    (word : List A) (x : X) (hx : x ∈ D) :
    q (run F word x) = qbar (run G (word.map τ) (T x)) := by
  have hi : ∀ (w : List A) (y : X), y ∈ D → run F w y ∈ D := by
    intro w
    induction w with
    | nil => intro y hy; exact hy
    | cons a w ih => intro y hy; exact ih (F a y) (hD a y hy)
  rw [hq _ (hi word x hx), invariant_forward_transport D F G T τ hD h word x hx]

section Split
variable {𝕜 V Z : Type*} [Field 𝕜] [AddCommGroup V] [Module 𝕜 V]
  [AddCommGroup Z] [Module 𝕜 Z]

/-- Full split encoding has the compatible-image projector as its identity. -/
theorem split_projector_idempotent (A : V →ₗ[𝕜] Z) (S : Z →ₗ[𝕜] V)
    (hSA : S.comp A = LinearMap.id) : (A.comp S).comp (A.comp S) = A.comp S := by
  ext z
  have h : ∀ v, S (A v) = v := fun v => LinearMap.congr_fun hSA v
  simp only [LinearMap.comp_apply, h]

/-- Core 2.1: whole-state encoding preserves multiplication. -/
theorem split_encoding_comp (A : V →ₗ[𝕜] Z) (S : Z →ₗ[𝕜] V)
    (hSA : S.comp A = LinearMap.id) (T U : V →ₗ[𝕜] V) :
    (A.comp (T.comp S)).comp (A.comp (U.comp S)) = A.comp ((T.comp U).comp S) := by
  ext z
  have h : ∀ v, S (A v) = v := fun v => LinearMap.congr_fun hSA v
  simp only [LinearMap.comp_apply, h]

/-- The discarded-return identity itself does not need C R = identity. -/
theorem hidden_return_identity (C : V →ₗ[𝕜] Z) (R : Z →ₗ[𝕜] V)
    (T U : V →ₗ[𝕜] V) :
    C.comp ((T.comp U).comp R) - (C.comp (T.comp R)).comp (C.comp (U.comp R)) =
      C.comp (T.comp ((LinearMap.id - R.comp C).comp (U.comp R))) := by
  ext z
  simp only [LinearMap.sub_apply, LinearMap.comp_apply, LinearMap.id_apply, map_sub]

/-- Core 2.1: exact composition iff the named discarded excursion vanishes. -/
theorem compressed_comp_iff_no_return (C : V →ₗ[𝕜] Z) (R : Z →ₗ[𝕜] V)
    (T U : V →ₗ[𝕜] V) :
    C.comp ((T.comp U).comp R) = (C.comp (T.comp R)).comp (C.comp (U.comp R)) ↔
      C.comp (T.comp ((LinearMap.id - R.comp C).comp (U.comp R))) = 0 := by
  rw [← hidden_return_identity]
  exact sub_eq_zero.symm

/-- Under the compression split, the reconstructed retained part is a projector. -/
theorem compression_projector_idempotent (C : V →ₗ[𝕜] Z) (R : Z →ₗ[𝕜] V)
    (hCR : C.comp R = LinearMap.id) : (R.comp C).comp (R.comp C) = R.comp C := by
  exact split_projector_idempotent R C hCR
end Split
end Komorebi.MachineTheory
