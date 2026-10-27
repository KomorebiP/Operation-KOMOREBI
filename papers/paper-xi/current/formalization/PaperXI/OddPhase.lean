import Mathlib.NumberTheory.LegendreSymbol.QuadraticChar.Basic
import Mathlib.LinearAlgebra.Charpoly.Basic
import Mathlib.Tactic

/-! Determinant-defined finite-field phases. These declarations do not identify
the phase with a Weil trace or assume any Weil normalization theorem. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OddPhase

variable {p : ℕ} [Fact p.Prime]
variable {V : Type*} [AddCommGroup V] [Module (ZMod p) V]

/-- The actual difference between an automorphism and the identity. -/
def difference (g : V ≃ₗ[ZMod p] V) : Module.End (ZMod p) V := g.toLinearMap - 1

@[simp] theorem difference_apply (g : V ≃ₗ[ZMod p] V) (v : V) :
    difference g v = g v - v := rfl

/-- Fixed-point-free means that there is no nonzero fixed vector. -/
def FixedPointFree (g : V ≃ₗ[ZMod p] V) : Prop := ∀ v, g v = v → v = 0

theorem fixedPointFree_iff_ker (g : V ≃ₗ[ZMod p] V) :
    FixedPointFree g ↔ LinearMap.ker (difference g) = ⊥ := by
  rw [LinearMap.ker_eq_bot']
  simp only [FixedPointFree, difference_apply, sub_eq_zero]

theorem fixedPointFree_iff_injective (g : V ≃ₗ[ZMod p] V) :
    FixedPointFree g ↔ Function.Injective (difference g) := by
  rw [fixedPointFree_iff_ker, LinearMap.ker_eq_bot]

section FiniteDimensional
variable [FiniteDimensional (ZMod p) V]

theorem fixedPointFree_iff_bijective (g : V ≃ₗ[ZMod p] V) :
    FixedPointFree g ↔ Function.Bijective (difference g) := by
  rw [fixedPointFree_iff_injective]
  exact ⟨fun h => ⟨h, LinearMap.injective_iff_surjective.mp h⟩, fun h => h.1⟩

theorem fixedPointFree_iff_det_ne_zero (g : V ≃ₗ[ZMod p] V) :
    FixedPointFree g ↔ LinearMap.det (difference g) ≠ 0 := by
  rw [fixedPointFree_iff_ker, ne_eq, LinearMap.det_eq_zero_iff_ker_ne_bot, not_not]

/-- The difference is an actual linear equivalence under the fixed-point-free hypothesis. -/
def differenceEquiv (g : V ≃ₗ[ZMod p] V) (hg : FixedPointFree g) : V ≃ₗ[ZMod p] V :=
  LinearEquiv.ofBijective (difference g) ((fixedPointFree_iff_bijective g).mp hg)

@[simp] theorem differenceEquiv_apply (g : V ≃ₗ[ZMod p] V) (hg : FixedPointFree g) (v : V) :
    differenceEquiv g hg v = g v - v := rfl

/-- The source determinant phase. Its trace interpretation is a separate external fact. -/
def phase (g : V ≃ₗ[ZMod p] V) : ℤ :=
  quadraticChar (ZMod p) (-1) ^ (Module.finrank (ZMod p) V / 2) *
    quadraticChar (ZMod p) (LinearMap.det (difference g))

theorem phase_sq_one (g : V ≃ₗ[ZMod p] V) (hg : FixedPointFree g) : phase g ^ 2 = 1 := by
  rw [phase, mul_pow, ← pow_mul, Nat.mul_comm _ 2, pow_mul]
  rw [quadraticChar_sq_one (neg_ne_zero.mpr one_ne_zero), one_pow,
    quadraticChar_sq_one ((fixedPointFree_iff_det_ne_zero g).mp hg), one_mul]

theorem phase_sign (g : V ≃ₗ[ZMod p] V) (hg : FixedPointFree g) :
    phase g = 1 ∨ phase g = -1 := sq_eq_one_iff.mp (phase_sq_one g hg)

theorem phase_ne_zero (g : V ≃ₗ[ZMod p] V) (hg : FixedPointFree g) : phase g ≠ 0 := by
  rcases phase_sign g hg with h | h <;> simp [h]

omit [FiniteDimensional (ZMod p) V] in
/-- The zero space has phase one, including its vacuous fixed-point-free condition. -/
theorem phase_zero_space [Subsingleton V] (g : V ≃ₗ[ZMod p] V) : phase g = 1 := by
  have hg : difference g = 1 := Subsingleton.elim _ _
  simp [phase, hg, Module.finrank_zero_of_subsingleton]

omit [FiniteDimensional (ZMod p) V] in
theorem fixedPointFree_zero_space [Subsingleton V] (g : V ≃ₗ[ZMod p] V) : FixedPointFree g :=
  fun v _ => Subsingleton.elim v 0


/-- Outside the fixed-point-free domain, the determinant-defined extension of
the phase is zero. This is not a formula for the full Weil trace there. -/
theorem phase_eq_zero_iff (g : V ≃ₗ[ZMod p] V) : phase g = 0 ↔ ¬FixedPointFree g := by
  have hneg : quadraticChar (ZMod p) (-1) ≠ 0 := by
    rw [ne_eq, quadraticChar_eq_zero_iff]
    exact neg_ne_zero.mpr one_ne_zero
  rw [phase, mul_eq_zero]
  simp only [pow_ne_zero _ hneg, false_or, quadraticChar_eq_zero_iff,
    fixedPointFree_iff_det_ne_zero, not_not]

end FiniteDimensional
end PaperXI.OddPhase
