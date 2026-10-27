import KTG.HodgeReduct
import KTG.Transport

/-!
# A five-element arithmetic separation experiment

The carrier is `Fin 5`. Its ordinary addition and multiplication are mod 5.
The map x |-> x^3 is an involutive multiplicative bijection, but NOT additive.
Transporting addition through this bijection gives a second field law on the
same labelled carrier with exactly the same multiplication.

This example certifies an algebraic reconstruction obstruction. It does not
construct IUT's theta links, Frobenioids, elliptic curves or log volumes.
-/

namespace KTG
namespace HodgeBridge

/-- Over F5 this map fixes 0 and sends every nonzero x to x^{-1}. -/
def inversion5 (x : Fin 5) : Fin 5 := x ^ 3

theorem inversion5_involution :
    ∀ x : Fin 5, inversion5 (inversion5 x) = x := by decide

theorem inversion5_multiplicative :
    ∀ x y : Fin 5, inversion5 (x * y) = inversion5 x * inversion5 y := by decide

theorem inversion5_preserves_zero : inversion5 0 = 0 := by decide

theorem inversion5_preserves_one : inversion5 1 = 1 := by decide

def standard5 : ArithmeticLayer (Fin 5) where
  zero := 0
  one := 1
  add := fun x y => x + y
  mul := fun x y => x * y

/-- A strong common-reduct link that does not preserve the old addition. -/
def inversionLink5 : MultiplicativeLink standard5 standard5 where
  toFun := inversion5
  invFun := inversion5
  left_inv := inversion5_involution
  right_inv := inversion5_involution
  map_mul := inversion5_multiplicative
  map_zero := inversion5_preserves_zero
  map_one := inversion5_preserves_one

def alien5 : ArithmeticLayer (Fin 5) :=
  transportedLayer standard5 inversionLink5

theorem standard_one_plus_one : standard5.add 1 1 = 2 := by decide

theorem alien_one_plus_one : alien5.add 1 1 = 3 := by decide

/-- The additive obstruction is witnessed by (1,1) without any assumed fact
about the field structures. -/
theorem inversionLink5_additive_obstruction :
    AdditiveObstruction inversionLink5 := by
  refine ⟨1, 1, ?_⟩
  decide

theorem inversionLink5_not_additive :
    ¬ AdditiveCompatible inversionLink5 := by
  intro h
  obtain ⟨x, y, hbad⟩ := inversionLink5_additive_obstruction
  exact hbad (h x y)

/-- A finite verification of the pulled-back additive group laws. -/
theorem alien_add_associative :
    ∀ x y z : Fin 5,
      alien5.add (alien5.add x y) z = alien5.add x (alien5.add y z) := by decide

theorem alien_add_commutative :
    ∀ x y : Fin 5, alien5.add x y = alien5.add y x := by decide

theorem alien_add_zero :
    ∀ x : Fin 5, alien5.add x 0 = x ∧ alien5.add 0 x = x := by decide

theorem alien_additive_inverses :
    ∀ x : Fin 5, ∃ y : Fin 5, alien5.add x y = 0 := by decide

/-- The original multiplication distributes over the transported addition. -/
theorem alien_left_distributive :
    ∀ x y z : Fin 5,
      x * alien5.add y z = alien5.add (x * y) (x * z) := by decide

theorem alien_right_distributive :
    ∀ x y z : Fin 5,
      alien5.add x y * z = alien5.add (x * z) (y * z) := by decide

theorem alien_nonzero_multiplicative_inverses :
    ∀ x : Fin 5, x ≠ 0 → ∃ y : Fin 5, x * y = 1 := by decide

/-- Both environments expose exactly the same multiplication to an observer. -/
def forgetMul (A : ArithmeticLayer (Fin 5)) := A.mul

def observeOnePlusOne (A : ArithmeticLayer (Fin 5)) : Fin 5 := A.add 1 1

theorem same_multiplicative_reduct : forgetMul standard5 = forgetMul alien5 := rfl

theorem different_additive_observation :
    observeOnePlusOne standard5 ≠ observeOnePlusOne alien5 := by decide

/-- Machine-checked impossibility: no reconstruction function of the public
multiplication table alone can always recover the labelled sum of 1 and 1. -/
theorem no_uniform_additive_reconstruction :
    ¬ Nonempty (FactorsThrough forgetMul observeOnePlusOne) := by
  exact differing_fiber_blocks_reconstruction
    forgetMul observeOnePlusOne
    same_multiplicative_reduct different_additive_observation


/-- A concrete Komorebi context whose objects are fully labelled arithmetic
layers, and whose comparison measurements are literal values in F5. -/
def fin5RealizationContext : KContext where
  Obj := ArithmeticLayer (Fin 5)
  MeasureObj := Fin 5
  le := Eq
  le_refl := fun _ => rfl
  le_trans := fun h₁ h₂ => h₁.trans h₂

/-- The `KTransport` observable view forgets addition and keeps only the
multiplication table. Its relation is literal equality of public views. -/
def fin5MultiplicativeTransport :
    KTransport fin5RealizationContext fin5RealizationContext where
  Carrier := Fin 5 → Fin 5 → Fin 5
  leftRep := forgetMul
  rightRep := forgetMul
  related := Eq
  Obstruction := Fin 5 × Fin 5

/-- Two fully valid arithmetic structures are indistinguishable through this
specific Komorebi transport, but differ at the additive observable 1+1. -/
theorem related_without_additive_reconstruction :
    fin5MultiplicativeTransport.Related standard5 alien5 ∧
      observeOnePlusOne standard5 ≠ observeOnePlusOne alien5 := by
  exact ⟨same_multiplicative_reduct, different_additive_observation⟩

/-- Positive control: the transformed law is genuinely compatible with the
multiplicative transport when the correct additive structure is specified. -/
theorem transported_link_additive :
    AdditiveCompatible (liftedTransportLink standard5 inversionLink5) :=
  lifted_transport_is_additive standard5 inversionLink5

end HodgeBridge
end KTG
