import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# A nontrivial cocycle model

For G = (Z/2Z)^2, c(x,y) = x₂ y₁ is an additive Z/2Z-valued 2-cocycle.
It cannot be a scalar coboundary: scalar coboundaries on an abelian group are
symmetric, while this cocycle is not. This is a finite exact obstruction model,
not a theorem identifying any Galois group or proving Langlands descent.
-/
namespace KomorebiSpace
namespace ProjectiveExample
abbrev G := (ZMod 2) × (ZMod 2)

def phase (x y : G) : ZMod 2 := x.2 * y.1

@[simp] theorem phase_zero_left (y : G) : phase 0 y = 0 := by simp [phase]
@[simp] theorem phase_zero_right (x : G) : phase x 0 = 0 := by simp [phase]

theorem cocycle (x y z : G) :
    phase x y + phase (x+y) z = phase y z + phase x (y+z) := by
  simp only [phase, Prod.fst_add, Prod.snd_add]
  ring

def coboundary (a : G → ZMod 2) (x y : G) : ZMod 2 := a x + a y - a (x+y)

theorem coboundary_symmetric (a : G → ZMod 2) (x y : G) :
    coboundary a x y = coboundary a y x := by
  unfold coboundary
  rw [add_comm x y, add_comm (a x) (a y)]

theorem phase_asymmetric : phase (1,0) (0,1) ≠ phase (0,1) (1,0) := by
  norm_num [phase]

theorem no_scalar_flattening : ¬ ∃ a : G → ZMod 2, ∀ x y, phase x y = coboundary a x y := by
  rintro ⟨a, ha⟩
  apply phase_asymmetric
  rw [ha, ha, coboundary_symmetric]
end ProjectiveExample
end KomorebiSpace
