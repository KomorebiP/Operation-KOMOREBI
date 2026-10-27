import KomorebiSpace.LinearExactification
import Mathlib.Analysis.Normed.Operator.NormedSpace
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# Constructed semantic-preserving repair dynamics

A bounded correction operator constructs the approximation sequence. Residual
contraction is only required on residuals actually produced by candidates.
Existence of that operator is an explicit hypothesis, not a universal claim.
-/
universe u v w z
noncomputable section
namespace KomorebiSpace
namespace RepairDynamics
open Filter
open scoped Topology
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {E : Type v} {R : Type w} {S : Type z}
variable [NormedAddCommGroup E] [NormedSpace 𝕜 E]
variable [NormedAddCommGroup R] [NormedSpace 𝕜 R]
variable [NormedAddCommGroup S] [NormedSpace 𝕜 S]

def step (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E) : E := x - A (d x)

def orbit (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E) : ℕ → E
  | 0 => x
  | n+1 => step d A (orbit d A x n)

@[simp] theorem orbit_zero (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E) :
    orbit d A x 0 = x := rfl

@[simp] theorem orbit_succ (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E) (n : ℕ) :
    orbit d A x (n+1) = step d A (orbit d A x n) := rfl

@[simp] theorem step_residual (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E) :
    d (step d A x) = d x - d (A (d x)) := map_sub d _ _

theorem step_semantics (d : E →L[𝕜] R) (p : E →L[𝕜] S) (A : R →L[𝕜] E)
    (hp : ∀ r, p (A r) = 0) (x : E) : p (step d A x) = p x := by
  simp [step, hp]

theorem step_movement (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E) :
    dist x (step d A x) ≤ ‖A‖ * ‖d x‖ := by
  calc
    dist x (step d A x) = ‖A (d x)‖ := by simp [step]
    _ ≤ ‖A‖ * ‖d x‖ := A.le_opNorm _

theorem orbit_semantics (d : E →L[𝕜] R) (p : E →L[𝕜] S) (A : R →L[𝕜] E)
    (hp : ∀ r, p (A r) = 0) (x : E) (n : ℕ) : p (orbit d A x n) = p x := by
  induction n with
  | zero => rfl
  | succ n ih => exact (step_semantics d p A hp _).trans ih

theorem step_fixes_exact (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E)
    (hx : d x = 0) : step d A x = x := by
  simp [step, hx]

theorem orbit_fixes_exact (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x : E)
    (hx : d x = 0) (n : ℕ) : orbit d A x n = x := by
  induction n with
  | zero => rfl
  | succ n ih => simpa only [orbit_succ, ih] using step_fixes_exact d A x hx

variable [CompleteSpace E]

/-- The correction procedure constructs a convergent sequence and its exact limit. -/
theorem exactification_from_correction_operator
    (d : E →L[𝕜] R) (p : E →L[𝕜] S) (A : R →L[𝕜] E)
    (q : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1)
    (hp : ∀ r, p (A r) = 0)
    (hcontract : ∀ x, ‖d x - d (A (d x))‖ ≤ q * ‖d x‖) (x : E) :
    ∃ y, Tendsto (orbit d A x) atTop (𝓝 y) ∧ d y = 0 ∧ p y = p x ∧
      ∀ n, dist (orbit d A x n) y ≤ (‖A‖ / (1-q)) * ‖d (orbit d A x n)‖ := by
  apply LinearExactification.geometric_semantic_exactification d p (orbit d A x)
    q ‖A‖ hq₀ hq₁ (norm_nonneg A)
  · intro n
    rw [orbit_succ, step_residual]
    exact hcontract _
  · intro n
    exact step_movement d A _
  · intro n
    exact orbit_semantics d p A hp x n

/-- Error bound and exact semantic repair without separately supplying an orbit. -/
theorem repair_exists
    (d : E →L[𝕜] R) (p : E →L[𝕜] S) (A : R →L[𝕜] E)
    (q : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1)
    (hp : ∀ r, p (A r) = 0)
    (hcontract : ∀ x, ‖d x - d (A (d x))‖ ≤ q * ‖d x‖) (x : E) :
    ∃ y, d y = 0 ∧ p y = p x ∧ dist x y ≤ (‖A‖ / (1-q)) * ‖d x‖ := by
  obtain ⟨y, _, hd, hy, hb⟩ :=
    exactification_from_correction_operator d p A q hq₀ hq₁ hp hcontract x
  exact ⟨y, hd, hy, hb 0⟩

/-- A semantic obstruction rules out a bounded correction operator of this strength. -/
theorem obstruction_vanishes
    (d : E →L[𝕜] R) (p : E →L[𝕜] S) (A : R →L[𝕜] E)
    (q : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1)
    (hp : ∀ r, p (A r) = 0)
    (hcontract : ∀ x, ‖d x - d (A (d x))‖ ≤ q * ‖d x‖) (x : E) :
    (LinearExactification.problem d p).obstruction x = 0 := by
  obtain ⟨y, hd, hy, _⟩ := repair_exists d p A q hq₀ hq₁ hp hcontract x
  exact ((LinearExactification.problem d p).flatten_iff x).mpr ⟨y, hd, hy⟩

/-- Uniqueness requires semantic separation on exact elements, not just contraction. -/
theorem unique_repair
    (d : E →L[𝕜] R) (p : E →L[𝕜] S) (A : R →L[𝕜] E)
    (q : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1)
    (hp : ∀ r, p (A r) = 0)
    (hcontract : ∀ x, ‖d x - d (A (d x))‖ ≤ q * ‖d x‖)
    (hsep : ∀ a b, d a = 0 → d b = 0 → p a = p b → a = b) (x : E) :
    ∃! y, d y = 0 ∧ p y = p x := by
  obtain ⟨y, hd, hy, _⟩ := repair_exists d p A q hq₀ hq₁ hp hcontract x
  refine ⟨y, ⟨hd, hy⟩, ?_⟩
  intro z hz
  exact hsep z y hz.1 hd (hz.2.trans hy.symm)

end RepairDynamics
end KomorebiSpace
end
