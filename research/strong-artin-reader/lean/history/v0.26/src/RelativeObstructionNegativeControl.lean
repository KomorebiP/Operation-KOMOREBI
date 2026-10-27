import FixedRestrictionObstruction
import Mathlib.Data.ZMod.Basic

/-! Absolute liftability need not imply liftability with a prescribed subgroup lift.
C4 has a trivial representation mod 2; the specified order-two subgroup maps
nontrivially into (Z/4)^*. No extension of that specified map exists. -/
namespace Komorebi.StrongArtin.SquareZeroH2.RelativeExample

abbrev G := Multiplicative (ZMod 4)
abbrev A := ZMod 4
abbrev B := ZMod 2

def q : A →+* B := ZMod.castHom (by decide : 2 ∣ 4) B

def gen : G := Multiplicative.ofAdd (1 : ZMod 4)
def middle : G := Multiplicative.ofAdd (2 : ZMod 4)

def H : Subgroup G where
  carrier := {g | g=1 ∨ g=middle}
  one_mem' := Or.inl rfl
  mul_mem' := by decide
  inv_mem' := by decide

def chosen (g : G) : Aˣ :=
  if g=middle then ZMod.unitOfCoprime 3 (by decide : Nat.Coprime 3 4) else 1

def datum : Datum G A B where
  q := q
  squareZero := by decide
  rho := 1
  lift := chosen
  lift_one := by decide
  lift_residue := by decide

theorem prescribed_subgroup_multiplicative :
    ∀ g ∈ H, ∀ h ∈ H, datum.lift (g*h) = datum.lift g * datum.lift h := by
  change ∀ g, (g=1 ∨ g=middle) → ∀ h, (h=1 ∨ h=middle) → chosen (g*h) = chosen g * chosen h
  decide

theorem every_unit_square_one : ∀ u : Aˣ, (u : A)^2=1 := by decide

/-- The absolute obstruction vanishes: the trivial lift already exists. -/
theorem absolute_obstruction_zero : datum.obstruction=0 := by
  apply datum.representation_lifts_iff_obstruction_zero.mp
  refine ⟨1, ?_⟩
  intro g
  change q 1 = 1
  exact map_one q

/-- But no lift can preserve the chosen nontrivial order-two subgroup map. -/
theorem no_fixed_subgroup_lift :
    ¬ ∃ lift : G →* Aˣ, ∀ g ∈ H, lift g = datum.lift g := by
  rintro ⟨lift,hfixed⟩
  have hm : gen^2=middle := by decide
  have hh : middle ∈ H := Or.inr rfl
  have hv : (lift gen)^2 = chosen middle := by
    rw [← map_pow,hm,hfixed middle hh]
    rfl
  have hv' := congrArg (fun u : Aˣ => (u : A)) hv
  have hs := every_unit_square_one (lift gen)
  have hb : (1 : A)=3 := by
    calc
      (1 : A) = (lift gen : A)^2 := hs.symm
      _ = 3 := hv'
  exact (by decide : (1 : A) ≠ 3) hb

/-- A nonzero relative obstruction despite zero absolute obstruction. -/
theorem relative_obstruction_nonzero :
    datum.relativeObstruction H prescribed_subgroup_multiplicative ≠ 0 := by
  intro hz
  obtain ⟨lift,_,hfixed⟩ :=
    (datum.fixed_restriction_lifts_iff_relativeObstruction_zero H
      prescribed_subgroup_multiplicative).mpr hz
  exact no_fixed_subgroup_lift ⟨lift,hfixed⟩

end Komorebi.StrongArtin.SquareZeroH2.RelativeExample
