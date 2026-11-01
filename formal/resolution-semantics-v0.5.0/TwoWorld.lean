import KRSCore

/-!
# The two-world symmetry obstruction

Formal companion to Resolution Semantics 0.1.0, Theorem 7.3
(`thm:nocanonical`). The ambient Boolean ring is `Bool × Bool`, with
coordinatewise xor and conjunction. The invariant sector is the diagonal.
The theorem quantifies over arbitrary functions satisfying the stated laws;
it does not enumerate a finite list of candidate projectors.
-/

set_option autoImplicit false

namespace KRS.TwoWorld

abbrev TruthPair := Bool × Bool

def xor (x y : TruthPair) : TruthPair :=
  (Bool.xor x.1 y.1, Bool.xor x.2 y.2)

def meet (x y : TruthPair) : TruthPair :=
  (x.1 && y.1, x.2 && y.2)

def complement (x : TruthPair) : TruthPair := (!x.1, !x.2)

def swap (x : TruthPair) : TruthPair := (x.2, x.1)

def Diagonal (x : TruthPair) : Prop := x.1 = x.2

def SwapEquivariant (P : TruthPair → TruthPair) : Prop :=
  ∀ x, P (swap x) = swap (P x)

theorem xor_self (x : TruthPair) : xor x x = (false, false) := by
  rcases x with ⟨a, b⟩
  cases a <;> cases b <;> rfl

theorem swap_eq_self_of_diagonal (x : TruthPair) (h : Diagonal x) :
    swap x = x := by
  rcases x with ⟨a, b⟩
  change a = b at h
  cases h
  rfl

/-- An additive retraction onto the diagonal, represented as an ambient
endomorphism with an explicit image condition. Fixing every diagonal point
is stronger than merely being idempotent, and is required here. -/
structure AdditiveRetraction where
  toFun : TruthPair → TruthPair
  range_diagonal : ∀ x, Diagonal (toFun x)
  map_xor : ∀ x y, toFun (xor x y) = xor (toFun x) (toFun y)
  fixes_diagonal : ∀ b, toFun (b, b) = (b, b)

/-- Theorem 7.3, additive assertion: the diagonal has no swap-equivariant
additive retraction over the two-element field. -/
theorem no_swap_equivariant_additive_retraction (P : AdditiveRetraction) :
    ¬ SwapEquivariant P.toFun := by
  intro hEquivariant
  have hSame : P.toFun (false, true) = P.toFun (true, false) := by
    calc
      P.toFun (false, true) = P.toFun (swap (true, false)) := rfl
      _ = swap (P.toFun (true, false)) := hEquivariant (true, false)
      _ = P.toFun (true, false) :=
        swap_eq_self_of_diagonal _ (P.range_diagonal (true, false))
  have hOne : P.toFun (true, true) = (false, false) := by
    calc
      P.toFun (true, true) = P.toFun (xor (true, false) (false, true)) := rfl
      _ = xor (P.toFun (true, false)) (P.toFun (false, true)) := P.map_xor _ _
      _ = xor (P.toFun (true, false)) (P.toFun (true, false)) := by rw [hSame]
      _ = (false, false) := xor_self _
  have hFalse : (false : Bool) = true :=
    congrArg Prod.fst (hOne.symm.trans (P.fixes_diagonal true))
  cases hFalse

/-- Boolean-ring retractions are additive retractions that also preserve
conjunction. Fixing the diagonal already includes preservation of zero and one. -/
structure BooleanRetraction extends AdditiveRetraction where
  map_meet : ∀ x y, toFun (meet x y) = meet (toFun x) (toFun y)

/-- Complement preservation follows from additivity and preservation of one. -/
theorem BooleanRetraction.map_complement (P : BooleanRetraction) (x : TruthPair) :
    P.toFun (complement x) = complement (P.toFun x) := by
  have hComplement (y : TruthPair) : complement y = xor (true, true) y := by
    rcases y with ⟨a, b⟩
    cases a <;> cases b <;> rfl
  rw [hComplement, P.map_xor, P.fixes_diagonal, ← hComplement]

/-- Theorem 7.3, Boolean assertion, as a consequence of the stronger
additive obstruction. -/
theorem no_swap_equivariant_boolean_retraction (P : BooleanRetraction) :
    ¬ SwapEquivariant P.toFun :=
  no_swap_equivariant_additive_retraction P.toAdditiveRetraction

/-- Choosing the first world supplies a valid, asymmetric Boolean retraction. -/
def leftProjection : BooleanRetraction where
  toFun x := (x.1, x.1)
  range_diagonal _ := rfl
  map_xor _ _ := rfl
  fixes_diagonal _ := rfl
  map_meet _ _ := rfl

/-- Choosing the second world supplies the other coordinate retraction. -/
def rightProjection : BooleanRetraction where
  toFun x := (x.2, x.2)
  range_diagonal _ := rfl
  map_xor _ _ := rfl
  fixes_diagonal _ := rfl
  map_meet _ _ := rfl

theorem leftProjection_not_equivariant : ¬ SwapEquivariant leftProjection.toFun :=
  no_swap_equivariant_boolean_retraction leftProjection

theorem rightProjection_not_equivariant : ¬ SwapEquivariant rightProjection.toFun :=
  no_swap_equivariant_boolean_retraction rightProjection

/-- Without additivity, a symmetric diagonal retraction does exist. -/
def lowerSummary (x : TruthPair) : TruthPair := (x.1 && x.2, x.1 && x.2)

theorem lowerSummary_diagonal (x : TruthPair) : Diagonal (lowerSummary x) := rfl

theorem lowerSummary_fixes_diagonal (b : Bool) : lowerSummary (b, b) = (b, b) := by
  cases b <;> rfl

theorem lowerSummary_equivariant : SwapEquivariant lowerSummary := by
  intro x
  rcases x with ⟨a, b⟩
  cases a <;> cases b <;> rfl

theorem lowerSummary_not_additive :
    lowerSummary (xor (true, false) (false, true)) ≠
      xor (lowerSummary (true, false)) (lowerSummary (false, true)) := by
  decide

/-- Without the image condition, the identity map satisfies all other laws. -/
theorem identity_additive (x y : TruthPair) : id (xor x y) = xor (id x) (id y) := rfl

theorem identity_fixes_diagonal (b : Bool) : id (b, b) = (b, b) := rfl

theorem identity_equivariant : SwapEquivariant id := by intro x; rfl

theorem identity_not_diagonal : ¬ Diagonal (id (true, false)) := by
  change (true : Bool) ≠ false
  decide

/-- Without the retraction condition, the constant-zero map satisfies the
image, additive and equivariance conditions. -/
def zeroSummary (_ : TruthPair) : TruthPair := (false, false)

theorem zeroSummary_diagonal (x : TruthPair) : Diagonal (zeroSummary x) := rfl

theorem zeroSummary_additive (x y : TruthPair) :
    zeroSummary (xor x y) = xor (zeroSummary x) (zeroSummary y) := rfl

theorem zeroSummary_equivariant : SwapEquivariant zeroSummary := by intro x; rfl

theorem zeroSummary_not_retraction : zeroSummary (true, true) ≠ (true, true) := by
  decide

end KRS.TwoWorld
