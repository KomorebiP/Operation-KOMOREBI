import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.Data.Int.Basic

set_option autoImplicit false

/-!
# Semantic constraints and a genuine obstruction quotient

A raw linear defect d(f) is always removable by subtracting f. A nontrivial
problem must restrict admissible corrections. Here p records semantics and
corrections must lie in ker p. The obstruction is [d(f)] in R / d(ker p).
-/
universe u v w z
namespace KomorebiSpace

structure CorrectionProblem (E : Type u) (R : Type v) (S : Type w)
    [AddCommGroup E] [AddCommGroup R] [AddCommGroup S] where
  residual : E →+ R
  semantics : E →+ S

namespace CorrectionProblem
variable {E : Type u} {R : Type v} {S : Type w}
variable [AddCommGroup E] [AddCommGroup R] [AddCommGroup S]

def boundaries (P : CorrectionProblem E R S) : AddSubgroup R :=
  P.semantics.ker.map P.residual

abbrev Obstruction (P : CorrectionProblem E R S) := R ⧸ P.boundaries

def obstruction (P : CorrectionProblem E R S) (x : E) : P.Obstruction :=
  (P.residual x : R ⧸ P.boundaries)

/-- Quotient vanishing is precisely solvability by an admissible correction. -/
theorem obstruction_zero_iff (P : CorrectionProblem E R S) (x : E) :
    P.obstruction x = 0 ↔
      ∃ a : E, P.semantics a = 0 ∧ P.residual a = P.residual x := by
  change (P.residual x : R ⧸ P.boundaries) = 0 ↔ _
  rw [QuotientAddGroup.eq_zero_iff]
  rfl

/-- Main constrained exactification equivalence, with semantics preserved. -/
theorem flatten_iff (P : CorrectionProblem E R S) (x : E) :
    P.obstruction x = 0 ↔
      ∃ y : E, P.residual y = 0 ∧ P.semantics y = P.semantics x := by
  rw [P.obstruction_zero_iff]
  constructor
  · rintro ⟨a, ha, hd⟩
    refine ⟨x-a, ?_, ?_⟩
    · rw [map_sub, hd, sub_self]
    · rw [map_sub, ha, sub_zero]
  · rintro ⟨y, hy, hs⟩
    refine ⟨x-y, ?_, ?_⟩
    · rw [map_sub, hs, sub_self]
    · rw [map_sub, hy, sub_zero]

theorem obstruction_invariant (P : CorrectionProblem E R S) (x a : E)
    (ha : P.semantics a = 0) : P.obstruction (x-a) = P.obstruction x := by
  have hz : (P.residual a : R ⧸ P.boundaries) = 0 :=
    (QuotientAddGroup.eq_zero_iff _).2 ⟨a, ha, rfl⟩
  change (P.residual (x-a) : R ⧸ P.boundaries) = (P.residual x : R ⧸ P.boundaries)
  rw [map_sub, QuotientAddGroup.mk_sub, hz, sub_zero]

/-- A dual witness rules out every semantics-preserving exact correction. -/
theorem nonzero_certificate (P : CorrectionProblem E R S)
    {D : Type z} [AddCommGroup D] (L : R →+ D) (x : E)
    (annihilate : ∀ a, P.semantics a = 0 → L (P.residual a) = 0)
    (witness : L (P.residual x) ≠ 0) : P.obstruction x ≠ 0 := by
  intro h
  rcases (P.obstruction_zero_iff x).1 h with ⟨a, ha, he⟩
  apply witness
  rw [← he]
  exact annihilate a ha

/-- With no semantic restriction every linear primary defect is correctable. -/
theorem unrestricted_correction (d : E →+ R) (x : E) :
    ∃ a : E, d x - d a = 0 := ⟨x, sub_self _⟩

/-- An explicit nontrivial model: the residual itself is the protected semantics. -/
def rigidInteger : CorrectionProblem ℤ ℤ ℤ :=
  ⟨AddMonoidHom.id ℤ, AddMonoidHom.id ℤ⟩

theorem rigid_one_obstructed : rigidInteger.obstruction 1 ≠ 0 := by
  intro h
  have hx := (rigidInteger.flatten_iff 1).1 h
  change ∃ y : ℤ, y = 0 ∧ y = 1 at hx
  obtain ⟨y, h0, h1⟩ := hx
  omega

end CorrectionProblem
end KomorebiSpace
