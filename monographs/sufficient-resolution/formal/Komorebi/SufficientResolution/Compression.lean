import Komorebi.SufficientResolution.ExactResolution
import Mathlib.Tactic.Abel

/-!
# Split compression, hidden return, and composition defects

Composition is written in operator order: `(S * T) x = S (T x)`.
The splitting need not be orthogonal.  Every identity below is exact.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution

universe uR uX uZ uW

variable (R : Type uR) [CommRing R]
variable (X : Type uX) [AddCommGroup X] [Module R X]
variable (Z : Type uZ) [AddCommGroup Z] [Module R Z]

/-- A coarse observation with a chosen right inverse. -/
structure SplitCompression where
  compress : X →ₗ[R] Z
  lift : Z →ₗ[R] X
  compress_lift : compress.comp lift = LinearMap.id

namespace SplitCompression

variable {R X Z}
variable (c : SplitCompression R X Z)

@[simp] theorem compress_lift_apply (z : Z) :
    c.compress (c.lift z) = z :=
  LinearMap.congr_fun c.compress_lift z

/-- Retained fine-state projector. -/
def retained : X →ₗ[R] X := c.lift.comp c.compress

/-- Discarded fine-state projector. -/
def hidden : X →ₗ[R] X := LinearMap.id - c.retained

/-- Coarse representation of a fine operator. -/
def coarse (T : X →ₗ[R] X) : Z →ₗ[R] Z :=
  c.compress.comp (T.comp c.lift)

/-- Failure of compression to preserve two-step composition. -/
def defect (S T : X →ₗ[R] X) : Z →ₗ[R] Z :=
  c.coarse (S * T) - c.coarse S * c.coarse T

@[simp] theorem retained_apply (x : X) :
    c.retained x = c.lift (c.compress x) := rfl

@[simp] theorem hidden_apply (x : X) :
    c.hidden x = x - c.lift (c.compress x) := rfl

@[simp] theorem retained_idempotent : c.retained * c.retained = c.retained := by
  ext x
  simp [Module.End.mul_apply]

@[simp] theorem hidden_idempotent : c.hidden * c.hidden = c.hidden := by
  ext x
  simp [Module.End.mul_apply, map_sub]

@[simp] theorem compress_hidden : c.compress.comp c.hidden = 0 := by
  ext x
  simp [map_sub]

@[simp] theorem hidden_lift : c.hidden.comp c.lift = 0 := by
  ext z
  simp

@[simp] theorem coarse_one : c.coarse 1 = 1 := by
  ext z
  simp [coarse]

@[simp] theorem coarse_zero : c.coarse 0 = 0 := by
  ext z
  simp [coarse]

 theorem coarse_add (S T : X →ₗ[R] X) :
    c.coarse (S + T) = c.coarse S + c.coarse T := by
  ext z
  simp [coarse]

 theorem coarse_sub (S T : X →ₗ[R] X) :
    c.coarse (S - T) = c.coarse S - c.coarse T := by
  ext z
  simp [coarse, map_sub]

/-- The defect is precisely an excursion through discarded state. -/
 theorem defect_factorization (S T : X →ₗ[R] X) :
    c.defect S T = c.compress.comp (S.comp (c.hidden.comp (T.comp c.lift))) := by
  ext z
  simp [defect, coarse, Module.End.mul_apply, map_sub]

 theorem multiplicative_iff_hidden_return_zero (S T : X →ₗ[R] X) :
    c.coarse (S * T) = c.coarse S * c.coarse T ↔
      c.compress.comp (S.comp (c.hidden.comp (T.comp c.lift))) = 0 := by
  rw [← c.defect_factorization]
  exact (sub_eq_zero : c.coarse (S * T) - c.coarse S * c.coarse T = 0 ↔ _).symm

/-- Associativity forces a coherence identity for the defects. -/
 theorem defect_coherence (S T U : X →ₗ[R] X) :
    c.defect S T * c.coarse U + c.defect (S * T) U =
      c.coarse S * c.defect T U + c.defect S (T * U) := by
  simp only [defect, sub_mul, mul_sub, mul_assoc]
  abel

/-- Exact defect of compressed powers, with no continuous-time assumptions. -/
 theorem power_defect (T : X →ₗ[R] X) (m n : ℕ) :
    c.coarse (T ^ (m + n)) - c.coarse (T ^ m) * c.coarse (T ^ n) =
      c.compress.comp ((T ^ m).comp (c.hidden.comp ((T ^ n).comp c.lift))) := by
  rw [pow_add]
  exact c.defect_factorization (T ^ m) (T ^ n)

/-- Intertwining the lifted coarse state implies exact powers at every depth. -/
 theorem powers_exact_of_lift_intertwining (T : X →ₗ[R] X)
    (h : T.comp c.lift = c.lift.comp (c.coarse T)) :
    ∀ n : ℕ, c.coarse (T ^ n) = (c.coarse T) ^ n := by
  have hp : ∀ n : ℕ, (T ^ n).comp c.lift = c.lift.comp ((c.coarse T) ^ n) := by
    intro n
    induction n with
    | zero =>
      ext z
      simp
    | succ n ih =>
      ext z
      have hh (y : Z) : T (c.lift y) = c.lift (c.coarse T y) :=
        LinearMap.congr_fun h y
      have hi (y : Z) : (T ^ n) (c.lift y) = c.lift (((c.coarse T) ^ n) y) :=
        LinearMap.congr_fun ih y
      simp [pow_succ', Module.End.mul_apply, hi, hh]
  intro n
  ext z
  have hi := LinearMap.congr_fun (hp n) z
  simpa [coarse] using congrArg c.compress hi

variable {W : Type uW} [AddCommGroup W] [Module R W]

/-- First compress by `c`, then by `d`. -/
def compose (d : SplitCompression R Z W) : SplitCompression R X W where
  compress := d.compress.comp c.compress
  lift := c.lift.comp d.lift
  compress_lift := by
    ext w
    simp

 theorem coarse_then (d : SplitCompression R Z W) (T : X →ₗ[R] X) :
    (c.compose d).coarse T = d.coarse (c.coarse T) := by
  ext w
  rfl

/-- Two-stage compression transports, rather than hides, the first-stage defect. -/
 theorem defect_then (d : SplitCompression R Z W) (S T : X →ₗ[R] X) :
    (c.compose d).defect S T =
      d.coarse (c.defect S T) + d.defect (c.coarse S) (c.coarse T) := by
  simp only [defect, coarse_then, coarse_sub]
  abel

 theorem defect_then_zero (d : SplitCompression R Z W) (S T : X →ₗ[R] X)
    (h₁ : c.defect S T = 0) (h₂ : d.defect (c.coarse S) (c.coarse T) = 0) :
    (c.compose d).defect S T = 0 := by
  rw [defect_then, h₁, h₂, coarse_zero, add_zero]

end SplitCompression
end Komorebi.SufficientResolution
