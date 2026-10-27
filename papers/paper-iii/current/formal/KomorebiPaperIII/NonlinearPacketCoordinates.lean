/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIII.PacketCoordinates
import KomorebiPaperIII.CoordinateNaturality
import Mathlib.Logic.Function.Iterate

/-!
# Nonlinear maps in constructed packet coordinates

Paper III, Definition 16.1, Theorem 16.2, Corollary 16.3 and Proposition 16.4.
Every coordinate equivalence here is obtained from actual projector ranges by
`PacketCoordinates.System.coordinateEquiv`. The ambient maps are arbitrary
functions and may couple every input packet to every output packet.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperIII.PacketCoordinates
universe u v w x y z t
variable {R : Type u} [Semiring R]
variable {M : Type v} {N : Type w} {O : Type x}
variable [AddCommMonoid M] [Module R M]
variable [AddCommMonoid N] [Module R N]
variable [AddCommMonoid O] [Module R O]
variable {I : Type y} {J : Type z} {K : Type t}
variable [Fintype I] [Fintype J] [Fintype K]

/-- Exact packet representation: analyze the output after applying the map to the full sum. -/
def coordinateMap (P : System R M I) (Q : System R N J) (f : M → N) :
    P.Coordinates → Q.Coordinates := fun x => Q.analysis (f (P.synthesis x))

@[simp] theorem coordinateMap_analysis (P : System R M I) (Q : System R N J)
    (f : M → N) (x : M) : coordinateMap P Q f (P.analysis x) = Q.analysis (f x) := by
  simp only [coordinateMap, P.synthesis_analysis]

/-- The new construction instantiates the existing arbitrary-equivalence API literally. -/
theorem coordinateMap_eq_existing (P : System R M I) (Q : System R N J) (f : M → N) :
    coordinateMap P Q f = Transport.exactCoordinateMap
      P.coordinateEquiv.toEquiv Q.coordinateEquiv.toEquiv f := rfl

/-- Theorem 16.2, first identity: reconstruct the original arbitrary map. -/
theorem coordinateMap_reconstruction (P : System R M I) (Q : System R N J) (f : M → N) :
    Q.synthesis ∘ coordinateMap P Q f ∘ P.analysis = f := by
  funext x
  simp only [Function.comp_apply, coordinateMap_analysis, Q.synthesis_analysis]

/-- Theorem 16.2, second identity: exact representation preserves composition. -/
theorem coordinateMap_comp (P : System R M I) (Q : System R N J) (S : System R O K)
    (f : M → N) (g : N → O) :
    coordinateMap P S (g ∘ f) = coordinateMap Q S g ∘ coordinateMap P Q f := by
  funext x
  simp only [coordinateMap, Function.comp_apply, Q.synthesis_analysis]

/-- Exact representation preserves the identity function. -/
@[simp] theorem coordinateMap_id (P : System R M I) : coordinateMap P P id = id := by
  funext x
  exact P.analysis_synthesis x

/-- No two distinct ambient maps become equal after exact packet representation. -/
theorem coordinateMap_injective (P : System R M I) (Q : System R N J) :
    Function.Injective (coordinateMap P Q) := by
  intro f g h
  have hh := congrArg (fun k => Q.synthesis ∘ k ∘ P.analysis) h
  simpa only [coordinateMap_reconstruction] using hh

/-- Corollary 16.3: injectivity of the underlying map is preserved and reflected. -/
theorem injective_iff (P : System R M I) (Q : System R N J) (f : M → N) :
    Function.Injective (coordinateMap P Q f) ↔ Function.Injective f := by
  constructor
  · intro h x y hxy
    apply P.analysis_injective
    apply h
    simpa only [coordinateMap_analysis] using congrArg Q.analysis hxy
  · intro h x y hxy
    apply P.coordinateEquiv.symm.injective
    exact h (Q.analysis_injective hxy)

/-- Corollary 16.3: surjectivity of the underlying map is preserved and reflected. -/
theorem surjective_iff (P : System R M I) (Q : System R N J) (f : M → N) :
    Function.Surjective (coordinateMap P Q f) ↔ Function.Surjective f := by
  constructor
  · intro h y
    rcases h (Q.analysis y) with ⟨x, hx⟩
    exact ⟨P.synthesis x, Q.analysis_injective hx⟩
  · intro h y
    rcases h (Q.synthesis y) with ⟨x, hx⟩
    refine ⟨P.analysis x, ?_⟩
    rw [coordinateMap_analysis, hx, Q.analysis_synthesis]

/-- Corollary 16.3: bijectivity is preserved and reflected. -/
theorem bijective_iff (P : System R M I) (Q : System R N J) (f : M → N) :
    Function.Bijective (coordinateMap P Q f) ↔ Function.Bijective f := by
  exact and_congr (injective_iff P Q f) (surjective_iff P Q f)

/-- The actual proposed inverse is transported, not merely its existence. -/
theorem leftInverse_iff (P : System R M I) (Q : System R N J)
    (f : M → N) (g : N → M) :
    Function.LeftInverse (coordinateMap Q P g) (coordinateMap P Q f) ↔
      Function.LeftInverse g f := by
  constructor
  · intro h x
    apply P.analysis_injective
    simpa only [coordinateMap_analysis] using h (P.analysis x)
  · intro h x
    change P.analysis (g (Q.synthesis (Q.analysis (f (P.synthesis x))))) = x
    rw [Q.synthesis_analysis, h, P.analysis_synthesis]

/-- Right inverses obey the same exact transport law. -/
theorem rightInverse_iff (P : System R M I) (Q : System R N J)
    (f : M → N) (g : N → M) :
    Function.RightInverse (coordinateMap Q P g) (coordinateMap P Q f) ↔
      Function.RightInverse g f := leftInverse_iff Q P g f

/-- Corollary 16.3, displayed fixed-point equivalence. -/
theorem fixedPoint_iff (P : System R M I) (f : M → M) (x : M) :
    coordinateMap P P f (P.analysis x) = P.analysis x ↔ f x = x := by
  rw [coordinateMap_analysis]
  exact P.analysis_injective.eq_iff

/-- All finite iterates, including the zero iterate, are exactly conjugate. -/
theorem iterate_analysis (P : System R M I) (f : M → M) (n : Nat) (x : M) :
    (coordinateMap P P f)^[n] (P.analysis x) = P.analysis ((f^[n]) x) := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [Function.iterate_succ_apply', Function.iterate_succ_apply', ih,
        coordinateMap_analysis]

/-- A point returns after exactly the same prescribed numbers of steps in either description. -/
theorem periodicPoint_iff (P : System R M I) (f : M → M) (n : Nat) (x : M) :
    (coordinateMap P P f)^[n] (P.analysis x) = P.analysis x ↔ (f^[n]) x = x := by
  rw [iterate_analysis]
  exact P.analysis_injective.eq_iff

/-- The entire set of return times is preserved; this also identifies least positive periods. -/
theorem returnTimes_eq (P : System R M I) (f : M → M) (x : M) :
    {n : Nat | (coordinateMap P P f)^[n] (P.analysis x) = P.analysis x} =
      {n : Nat | (f^[n]) x = x} := by
  ext n
  exact periodicPoint_iff P f n x

/-- Actual change between two projector coordinate systems on one ambient module. -/
def coordinateTransport (P : System R M I) (Q : System R M J) :
    P.Coordinates ≃ₗ[R] Q.Coordinates := P.coordinateEquiv.symm.trans Q.coordinateEquiv

@[simp] theorem coordinateTransport_apply (P : System R M I) (Q : System R M J)
    (x : P.Coordinates) : coordinateTransport P Q x = Q.analysis (P.synthesis x) := rfl

/-- Actual projector coordinate changes satisfy the cocycle law. -/
theorem coordinateTransport_cocycle (P : System R M I) (Q : System R M J)
    (S : System R M K) :
    (coordinateTransport P Q).trans (coordinateTransport Q S) = coordinateTransport P S := by
  ext x
  simp only [LinearEquiv.trans_apply, coordinateTransport_apply, Q.synthesis_analysis]

/-- Actual projector coordinate loops are identities. This does not assert flatness of a connection. -/
theorem coordinateTransport_triangle (P : System R M I) (Q : System R M J)
    (S : System R M K) :
    ((coordinateTransport P Q).trans (coordinateTransport Q S)).trans
      (coordinateTransport S P) = LinearEquiv.refl R P.Coordinates := by
  ext x
  simp only [LinearEquiv.trans_apply, coordinateTransport_apply, Q.synthesis_analysis,
    S.synthesis_analysis, P.analysis_synthesis, LinearEquiv.refl_apply]

universe s r
variable {I' : Type s} {J' : Type r} [Fintype I'] [Fintype J']

/-- Proposition 16.4: changes of both input and output packet systems commute with arbitrary maps. -/
theorem change_coordinates (P : System R M I) (P' : System R M I')
    (Q : System R N J) (Q' : System R N J') (f : M → N) :
    coordinateMap P' Q' f = coordinateTransport Q Q' ∘ coordinateMap P Q f ∘
      coordinateTransport P' P := by
  funext x
  simp only [Function.comp_apply, coordinateMap, coordinateTransport_apply,
    P.synthesis_analysis, Q.synthesis_analysis]

end Komorebi.PaperIII.PacketCoordinates
