/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Data.Fin.Basic
import Mathlib.Data.Rat.Defs
import Mathlib.Algebra.Module.Equiv.Basic
import Mathlib.Tactic

/-!
# Exact coordinate transport and noncanonical connections

Exact coordinate changes obtained from a single family of frames telescope.
Their loop transport is therefore forced to be the identity.  A separate
`Connection` API deliberately assumes only identity transport at equal
endpoints.  It may have a cocycle defect and nontrivial holonomy.
-/

set_option autoImplicit false

namespace Komorebi.PaperIII.Transport

universe u v w

section Exact

variable {R : Type u} {M : Type v} {X : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M]

/--
Canonical coordinate transport from frame `a` to frame `b`: synthesize through
the ambient space using `frame a`, then analyze using `frame b`.
-/
def exactTransport (frame : X → M ≃ₗ[R] M) (a b : X) : M ≃ₗ[R] M :=
  (frame a).trans (frame b).symm

@[simp] theorem exactTransport_apply (frame : X → M ≃ₗ[R] M)
    (a b : X) (x : M) :
    exactTransport frame a b x = (frame b).symm (frame a x) :=
  rfl

/-- Canonical transport at one frame is the identity. -/
@[simp] theorem exactTransport_self (frame : X → M ≃ₗ[R] M) (a : X) :
    exactTransport frame a a = LinearEquiv.refl R M := by
  apply LinearEquiv.ext
  intro x
  simp [exactTransport]

/-- Canonical coordinate transport satisfies the exact cocycle law. -/
theorem exactTransport_cocycle (frame : X → M ≃ₗ[R] M) (a b c : X) :
    (exactTransport frame a b).trans (exactTransport frame b c) =
      exactTransport frame a c := by
  apply LinearEquiv.ext
  intro x
  simp [exactTransport]

/-- Every canonical two-edge round trip is trivial. -/
theorem exactTransport_roundTrip (frame : X → M ≃ₗ[R] M) (a b : X) :
    (exactTransport frame a b).trans (exactTransport frame b a) =
      LinearEquiv.refl R M := by
  rw [exactTransport_cocycle, exactTransport_self]

/-- Every canonical triangular loop is trivial. -/
theorem exactTransport_triangleLoop (frame : X → M ≃ₗ[R] M) (a b c : X) :
    ((exactTransport frame a b).trans (exactTransport frame b c)).trans
        (exactTransport frame c a) = LinearEquiv.refl R M := by
  rw [exactTransport_cocycle, exactTransport_roundTrip]

/-- Endpoint reached after traversing a finite list of successive vertices. -/
def pathEndpoint (start : X) : List X → X
  | [] => start
  | next :: rest => pathEndpoint next rest

/-- Canonical transport along a finite list of successive vertices. -/
def exactPathTransport (frame : X → M ≃ₗ[R] M) (start : X) :
    List X → M ≃ₗ[R] M
  | [] => LinearEquiv.refl R M
  | next :: rest =>
      (exactTransport frame start next).trans
        (exactPathTransport frame next rest)

/-- Any finite canonical path telescopes to transport between its endpoints. -/
theorem exactPathTransport_eq_endpoint
    (frame : X → M ≃ₗ[R] M) (start : X) (vertices : List X) :
    exactPathTransport frame start vertices =
      exactTransport frame start (pathEndpoint start vertices) := by
  induction vertices generalizing start with
  | nil =>
      simp [exactPathTransport, pathEndpoint]
  | cons next rest ih =>
      simp only [exactPathTransport, pathEndpoint]
      rw [ih, exactTransport_cocycle]

/-- Every finite canonical path returning to its start has trivial holonomy. -/
theorem exactPathTransport_loop
    (frame : X → M ≃ₗ[R] M) (start : X) (vertices : List X)
    (hloop : pathEndpoint start vertices = start) :
    exactPathTransport frame start vertices = LinearEquiv.refl R M := by
  rw [exactPathTransport_eq_endpoint, hloop, exactTransport_self]

end Exact

section Connection

variable {R : Type u} {M : Type v} {X : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M]

/--
A noncanonical connection.  Only equal-endpoint transport is normalized;
neither the cocycle law nor reverse-edge inversion is assumed.
-/
structure Connection (R : Type u) (M : Type v) (X : Type w)
    [Semiring R] [AddCommMonoid M] [Module R M] where
  transport : X → X → M ≃ₗ[R] M
  transport_self : ∀ x, transport x x = LinearEquiv.refl R M

namespace Connection

variable (C : Connection R M X)

/-- The exact cocycle condition at one ordered triple. -/
def CocycleAt (a b c : X) : Prop :=
  (C.transport a b).trans (C.transport b c) = C.transport a c

/-- Flatness means the cocycle condition holds at every ordered triple. -/
def Flat : Prop := ∀ a b c, C.CocycleAt a b c

/--
The cocycle defect, based at the target coordinate space.  It compares the
two-edge route `a → b → c` with the direct route `a → c`.
-/
def cocycleDefect (a b c : X) : M ≃ₗ[R] M :=
  (C.transport a c).symm.trans
    ((C.transport a b).trans (C.transport b c))

/-- Ordered triangular holonomy: traverse `a → b → c → a`. -/
def triangleHolonomy (a b c : X) : M ≃ₗ[R] M :=
  ((C.transport a b).trans (C.transport b c)).trans (C.transport c a)

/-- A flat noncanonical connection has no triangular holonomy. -/
theorem triangleHolonomy_eq_refl_of_flat (hflat : C.Flat) (a b c : X) :
    C.triangleHolonomy a b c = LinearEquiv.refl R M := by
  rw [triangleHolonomy, hflat a b c, hflat a c a, C.transport_self]

/-- Flatness forces the cocycle defect to be the identity. -/
theorem cocycleDefect_eq_refl_of_flat (hflat : C.Flat) (a b c : X) :
    C.cocycleDefect a b c = LinearEquiv.refl R M := by
  rw [cocycleDefect, hflat a b c]
  apply LinearEquiv.ext
  intro x
  simp

end Connection
end Connection

/-! ## A concrete nontrivial loop -/

/-- Multiplication by two as a rational linear equivalence. -/
def doubleEquiv : ℚ ≃ₗ[ℚ] ℚ where
  toFun x := 2 * x
  invFun x := x / 2
  left_inv x := by ring
  right_inv x := by ring
  map_add' x y := by ring
  map_smul' c x := by
    simp only [smul_eq_mul, RingHom.id_apply]
    ring

@[simp] theorem doubleEquiv_apply (x : ℚ) : doubleEquiv x = 2 * x :=
  rfl

/--
A three-point connection with a single twisted directed transport `0 → 1`.
All other unequal endpoint transports are the identity.
-/
def twistedThreePointConnection : Connection ℚ ℚ (Fin 3) where
  transport a b :=
    if a = b then LinearEquiv.refl ℚ ℚ
    else if a = (0 : Fin 3) ∧ b = (1 : Fin 3) then doubleEquiv
    else LinearEquiv.refl ℚ ℚ
  transport_self a := by simp

/-- The loop `0 → 1 → 2 → 0` doubles the packet coordinate `1`. -/
theorem twisted_triangleHolonomy_apply_one :
    twistedThreePointConnection.triangleHolonomy
        (0 : Fin 3) (1 : Fin 3) (2 : Fin 3) (1 : ℚ) = 2 := by
  norm_num [Connection.triangleHolonomy, twistedThreePointConnection,
    doubleEquiv]

/-- The separate connection API genuinely admits nontrivial holonomy. -/
theorem twisted_triangleHolonomy_ne_refl :
    twistedThreePointConnection.triangleHolonomy
        (0 : Fin 3) (1 : Fin 3) (2 : Fin 3) ≠ LinearEquiv.refl ℚ ℚ := by
  intro h
  have happly := congrArg (fun e : ℚ ≃ₗ[ℚ] ℚ ↦ e (1 : ℚ)) h
  norm_num [Connection.triangleHolonomy, twistedThreePointConnection,
    doubleEquiv] at happly

end Komorebi.PaperIII.Transport
