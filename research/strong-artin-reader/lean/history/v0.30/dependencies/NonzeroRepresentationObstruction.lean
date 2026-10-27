import SurjectiveSquareZeroDatum
import Mathlib.Data.ZMod.Basic

/-! A genuine nonzero obstruction, not only a syntactic counterexample:
C3 -> (Z/9)^* sending its generator to 4 does not lift to (Z/27)^*.
Its compatible multiplication error represents a nonzero Mathlib H² class. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Example

abbrev G := Multiplicative (ZMod 3)
abbrev A := ZMod 27
abbrev B := ZMod 9

def q : A →+* B := ZMod.castHom (by decide : 9 ∣ 27) B

theorem q_surjective : Function.Surjective q := ZMod.castHom_surjective (by decide)

theorem q_squareZero : ∀ a b : A, q a = 0 → q b = 0 → a*b=0 := by decide

def rho : G →* Bˣ where
  toFun g := (ZMod.unitOfCoprime 4 (by decide : Nat.Coprime 4 9)) ^ g.toAdd.val
  map_one' := by decide
  map_mul' := by decide

def unitLifts (g : G) : Aˣ :=
  (ZMod.unitOfCoprime 4 (by decide : Nat.Coprime 4 27)) ^ g.toAdd.val

def datum : Datum G A B where
  q := q
  squareZero := q_squareZero
  rho := (Units.coeHom B).comp rho
  lift := unitLifts
  lift_one := by decide
  lift_residue := by decide

def generator : G := Multiplicative.ofAdd (1 : ZMod 3)

theorem generator_order_relation : generator^3=1 := by decide

theorem no_cube_one_above_four : ∀ a : A, q a = 4 → a^3≠1 := by decide

/-- No genuine representation lift exists for this small extension. -/
theorem no_representation_lift :
    ¬ ∃ lift : G →* Aˣ, ∀ g, q (lift g) = (rho g : B) := by
  rintro ⟨lift,hlift⟩
  have hpow : (lift generator)^3 = 1 := by
    rw [← map_pow, generator_order_relation, map_one]
  have hval : (↑(lift generator) : A)^3=1 := by
    have h := congrArg (fun u : Aˣ => (u : A)) hpow
    simpa using h
  have hres : q (lift generator)=4 := hlift generator
  exact no_cube_one_above_four _ hres hval

/-- The obstruction class constructed by the general theorem is genuinely nonzero. -/
theorem obstruction_nonzero : datum.obstruction ≠ 0 := by
  intro hz
  exact no_representation_lift (datum.representation_lifts_iff_obstruction_zero.mpr hz)

/-- Explicit representative: the carry across the generator's order is the kernel element 9. -/
theorem defect_at_wrap :
    (datum.normalizedDefect unitLifts datum.lift_residue (generator^2,generator) : A) = 9 := by
  decide

end Komorebi.StrongArtin.SquareZeroH2.Example
