import KTG.SafeAbstraction

/-!
# Hodge-theater-inspired reduct and reconstruction obstructions

This is an elementary algebraic shadow of the non-scheme-theoretic links in
IUT I-II. It is NOT a construction of an IUT Hodge theater or theta link.
In particular, an IUT theta link need not be a map of the entire ring carrier.
The purpose of this file is to isolate the mathematical meaning of retaining
multiplication while losing a justified additive comparison.
-/

namespace KTG
namespace HodgeBridge

universe u v w

/-- A bare arithmetic environment on a labelled carrier. No ring laws are
postulated by this record: those laws must be checked in particular models. -/
structure ArithmeticLayer (S : Type u) where
  zero : S
  one : S
  add : S → S → S
  mul : S → S → S

/-- A deliberately strong toy version of a reduct link: a multiplicative
bijection preserving zero and one, but NOT assumed to preserve addition. -/
structure MultiplicativeLink {S : Type u} {T : Type v}
    (A : ArithmeticLayer S) (B : ArithmeticLayer T) where
  toFun : S → T
  invFun : T → S
  left_inv : ∀ x, invFun (toFun x) = x
  right_inv : ∀ y, toFun (invFun y) = y
  map_mul : ∀ x y, toFun (A.mul x y) = B.mul (toFun x) (toFun y)
  map_zero : toFun A.zero = B.zero
  map_one : toFun A.one = B.one


/-- The reduct link is injective by its recorded inverse. -/
theorem MultiplicativeLink.injective
    {S : Type u} {T : Type v}
    {A : ArithmeticLayer S} {B : ArithmeticLayer T}
    (L : MultiplicativeLink A B) : Function.Injective L.toFun := by
  intro x y hxy
  calc
    x = L.invFun (L.toFun x) := (L.left_inv x).symm
    _ = L.invFun (L.toFun y) := congrArg L.invFun hxy
    _ = y := L.left_inv y

/-- Powers expressed only through multiplication and the unit. -/
def multiplicativePower {S : Type u}
    (A : ArithmeticLayer S) (x : S) : Nat → S
  | 0 => A.one
  | n + 1 => A.mul (multiplicativePower A x n) x

/-- Every certified multiplicative link transports its entire power grammar. -/
theorem link_preserves_multiplicative_powers
    {S : Type u} {T : Type v}
    {A : ArithmeticLayer S} {B : ArithmeticLayer T}
    (L : MultiplicativeLink A B) (x : S) (n : Nat) :
    L.toFun (multiplicativePower A x n) =
      multiplicativePower B (L.toFun x) n := by
  induction n with
  | zero =>
      exact L.map_one
  | succ n ih =>
      simp only [multiplicativePower]
      rw [L.map_mul, ih]

/-- Torsion equations x^n=1 survive the link in BOTH directions. This is a
positive preservation theorem to contrast with additive non-preservation. -/
theorem link_preserves_torsion_equation
    {S : Type u} {T : Type v}
    {A : ArithmeticLayer S} {B : ArithmeticLayer T}
    (L : MultiplicativeLink A B) (x : S) (n : Nat) :
    multiplicativePower A x n = A.one ↔
      multiplicativePower B (L.toFun x) n = B.one := by
  constructor
  · intro h
    calc
      multiplicativePower B (L.toFun x) n =
          L.toFun (multiplicativePower A x n) :=
        (link_preserves_multiplicative_powers L x n).symm
      _ = L.toFun A.one := congrArg L.toFun h
      _ = B.one := L.map_one
  · intro h
    apply L.injective
    rw [link_preserves_multiplicative_powers, L.map_one]
    exact h

/-- Additive compatibility is a new theorem obligation, not a link premise. -/
def AdditiveCompatible {S : Type u} {T : Type v}
    {A : ArithmeticLayer S} {B : ArithmeticLayer T}
    (L : MultiplicativeLink A B) : Prop :=
  ∀ x y, L.toFun (A.add x y) = B.add (L.toFun x) (L.toFun y)

/-- A direct, checkable witness that the reduct link does not lift to the
specified additive structure. -/
def AdditiveObstruction {S : Type u} {T : Type v}
    {A : ArithmeticLayer S} {B : ArithmeticLayer T}
    (L : MultiplicativeLink A B) : Prop :=
  ∃ x y, L.toFun (A.add x y) ≠ B.add (L.toFun x) (L.toFun y)

/-- The full additive lift exists exactly when no pair witnesses an obstruction.
This theorem is intentionally about a specified link, not arbitrary IUT links. -/
theorem compatible_iff_no_additive_obstruction
    {S : Type u} {T : Type v}
    {A : ArithmeticLayer S} {B : ArithmeticLayer T}
    (L : MultiplicativeLink A B) :
    AdditiveCompatible L ↔ ¬ AdditiveObstruction L := by
  constructor
  · intro h hobs
    obtain ⟨x, y, hxy⟩ := hobs
    exact hxy (h x y)
  · intro h x y
    exact Classical.byContradiction (fun bad => h ⟨x, y, bad⟩)

/-- Pull an additive law back across a reduct automorphism. -/
def transportedAdd {S : Type u}
    (A : ArithmeticLayer S) (L : MultiplicativeLink A A)
    (x y : S) : S :=
  L.invFun (A.add (L.toFun x) (L.toFun y))

/-- Transport changes the addition while keeping multiplication fixed as
an operation on the labelled carrier. -/
def transportedLayer {S : Type u}
    (A : ArithmeticLayer S) (L : MultiplicativeLink A A) :
    ArithmeticLayer S where
  zero := A.zero
  one := A.one
  mul := A.mul
  add := transportedAdd A L

/-- The construction has exactly the intended additive intertwining. -/
theorem transported_add_intertwines {S : Type u}
    (A : ArithmeticLayer S) (L : MultiplicativeLink A A)
    (x y : S) :
    L.toFun (transportedAdd A L x y) =
      A.add (L.toFun x) (L.toFun y) := by
  exact L.right_inv _

/-- The original reduct automorphism becomes a full additive-compatible link
from the transported structure to the original. -/
def liftedTransportLink {S : Type u}
    (A : ArithmeticLayer S) (L : MultiplicativeLink A A) :
    MultiplicativeLink (transportedLayer A L) A where
  toFun := L.toFun
  invFun := L.invFun
  left_inv := L.left_inv
  right_inv := L.right_inv
  map_mul := L.map_mul
  map_zero := L.map_zero
  map_one := L.map_one

/-- The transported addition is not arbitrary: the recovered full lift really
preserves it. -/
theorem lifted_transport_is_additive {S : Type u}
    (A : ArithmeticLayer S) (L : MultiplicativeLink A A) :
    AdditiveCompatible (liftedTransportLink A L) := by
  intro x y
  exact transported_add_intertwines A L x y

/-- A concrete pair of indistinguishable reducts with different observables
rules out any uniform reconstruction of that observable from the reduct. -/
theorem differing_fiber_blocks_reconstruction
    {X : Type u} {Y : Type v} {Z : Type w}
    (forget : X → Y) (obs : X → Z)
    {a b : X}
    (hforget : forget a = forget b)
    (hobs : obs a ≠ obs b) :
    ¬ Nonempty (FactorsThrough forget obs) := by
  rintro ⟨h⟩
  exact hobs (KTG.same_fiber_same_value h hforget)


/-- Exact observational descent criterion. If the observable is constant on
fibers of the reduct, then it can be computed from the reduct alone. `Inhabited`
is needed to assign a harmless value outside the observed image. -/
theorem factor_iff_constant_on_fibers
    {X : Type u} {Y : Type v} {Z : Type w}
    [Inhabited Z]
    (forget : X → Y) (obs : X → Z) :
    Nonempty (FactorsThrough forget obs) ↔
      (∀ x y, forget x = forget y → obs x = obs y) := by
  constructor
  · rintro ⟨h⟩ x y hxy
    exact KTG.same_fiber_same_value h hxy
  · intro h
    classical
    let f : Y → Z := fun y =>
      if hy : ∃ x, forget x = y then obs (Classical.choose hy) else default
    have hf : ∀ x : X, obs x = f (forget x) := by
      intro x
      dsimp [f]
      rw [dite_eq_left (show ∃ a : X, forget a = forget x from ⟨x, rfl⟩)]
      apply (h (Classical.choose (show ∃ a : X, forget a = forget x from ⟨x, rfl⟩)) x ?_).symm
      exact Classical.choose_spec (show ∃ a : X, forget a = forget x from ⟨x, rfl⟩)
    exact ⟨⟨f, hf⟩⟩

end HodgeBridge
end KTG
