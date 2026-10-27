/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIII.Transport
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-!
# Reversible connections, gauge covariance, and finite holonomy blocks

This module strengthens the minimal homogeneous connection in `Transport` to
a family of possibly heterogeneous fibres.  Pair transport is normalized and
reverses by inversion, but no cocycle law is included in the structure.

All paths and packet resolutions in this file are finite.  The gauge results
are purely algebraic conjugation identities; no topology or smooth structure
is assumed.
-/

set_option autoImplicit false

namespace Komorebi.PaperIII.Transport

open scoped BigOperators

universe u v w z

/--
A normalized reversible pair connection on a family of linear fibres.

`transport a b` maps the fibre at `a` to the fibre at `b`.  Normalization and
reverse-edge inversion are data, while the cocycle law is deliberately not.
-/
structure ReversibleConnection
    (R : Type u) (X : Type v) (F : X → Type w)
    [CommRing R] [∀ a, AddCommGroup (F a)] [∀ a, Module R (F a)] where
  transport : ∀ a b, F a ≃ₗ[R] F b
  transport_self : ∀ a, transport a a = LinearEquiv.refl R (F a)
  transport_reverse : ∀ a b, transport b a = (transport a b).symm

namespace ReversibleConnection

variable {R : Type u} {X : Type v} {F : X → Type w}
variable [CommRing R] [∀ a, AddCommGroup (F a)] [∀ a, Module R (F a)]
variable (C : ReversibleConnection R X F)

/-- A gauge is a fibrewise family of linear automorphisms. -/
abbrev Gauge := ∀ a, F a ≃ₗ[R] F a

/-- The exact pair-cocycle condition at one ordered triple. -/
def CocycleAt (a b c : X) : Prop :=
  (C.transport a b).trans (C.transport b c) = C.transport a c

/-- Algebraic flatness is the pair-cocycle condition at every triple. -/
def Flat : Prop := ∀ a b c, C.CocycleAt a b c

/--
The additive cocycle defect from the fibre at `a` to the fibre at `c`.
The indices are written in traversal order `a → b → c`.
-/
def cocycleDefect (a b c : X) : F a →ₗ[R] F c :=
  (C.transport b c).toLinearMap.comp (C.transport a b).toLinearMap -
    (C.transport a c).toLinearMap

/-- Triangle holonomy based at `a`, traversing `a → b → c → a`. -/
def triangleHolonomy (a b c : X) : F a ≃ₗ[R] F a :=
  ((C.transport a b).trans (C.transport b c)).trans (C.transport c a)

/-- The additive triangle obstruction `H - id` on the base fibre. -/
def triangleObstruction (a b c : X) : F a →ₗ[R] F a :=
  (C.triangleHolonomy a b c).toLinearMap - LinearMap.id

/-- Vanishing additive defect is exactly the cocycle equation at a triple. -/
theorem cocycleDefect_eq_zero_iff_cocycleAt (a b c : X) :
    C.cocycleDefect a b c = 0 ↔ C.CocycleAt a b c := by
  constructor
  · intro h
    apply LinearEquiv.ext
    intro x
    have hx := congrArg (fun L : F a →ₗ[R] F c ↦ L x) h
    change C.transport b c (C.transport a b x) = C.transport a c x
    change C.transport b c (C.transport a b x) - C.transport a c x = 0 at hx
    exact sub_eq_zero.mp hx
  · intro h
    ext x
    have hx := congrArg (fun e : F a ≃ₗ[R] F c ↦ e x) h
    change C.transport b c (C.transport a b x) - C.transport a c x = 0
    rw [sub_eq_zero]
    simpa [CocycleAt] using hx

/--
Defect--holonomy identity:
`H - id = transport(c,a) ∘ Δ`.
-/
theorem triangleHolonomy_sub_id (a b c : X) :
    C.triangleObstruction a b c =
      (C.transport c a).toLinearMap.comp (C.cocycleDefect a b c) := by
  ext x
  simp only [triangleObstruction, triangleHolonomy, cocycleDefect,
    LinearMap.sub_apply, LinearMap.id_apply, LinearMap.comp_apply,
    LinearEquiv.coe_toLinearMap, LinearEquiv.trans_apply, map_sub]
  rw [C.transport_reverse a c]
  simp

/-- The triangle obstruction vanishes exactly when the additive defect does. -/
theorem triangleObstruction_eq_zero_iff_cocycleDefect_eq_zero (a b c : X) :
    C.triangleObstruction a b c = 0 ↔ C.cocycleDefect a b c = 0 := by
  rw [C.triangleHolonomy_sub_id a b c]
  constructor
  · intro h
    ext x
    apply (C.transport c a).injective
    have hx := congrArg (fun L : F a →ₗ[R] F a ↦ L x) h
    simpa using hx
  · intro h
    simp [h]

/-- `H - id` vanishes exactly when the triangle holonomy is the identity. -/
theorem triangleObstruction_eq_zero_iff_triangleHolonomy_eq_refl (a b c : X) :
    C.triangleObstruction a b c = 0 ↔
      C.triangleHolonomy a b c = LinearEquiv.refl R (F a) := by
  constructor
  · intro h
    apply LinearEquiv.ext
    intro x
    have hx := congrArg (fun L : F a →ₗ[R] F a ↦ L x) h
    change C.triangleHolonomy a b c x = x
    change C.triangleHolonomy a b c x - x = 0 at hx
    exact sub_eq_zero.mp hx
  · intro h
    ext x
    have hx := congrArg (fun e : F a ≃ₗ[R] F a ↦ e x) h
    change C.triangleHolonomy a b c x - x = 0
    rw [sub_eq_zero]
    simpa using hx

/-- Additive flatness at a triple is equivalent to identity holonomy. -/
theorem cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl (a b c : X) :
    C.cocycleDefect a b c = 0 ↔
      C.triangleHolonomy a b c = LinearEquiv.refl R (F a) := by
  rw [← C.triangleObstruction_eq_zero_iff_cocycleDefect_eq_zero a b c,
    C.triangleObstruction_eq_zero_iff_triangleHolonomy_eq_refl]

/-- Flatness is equivalent to identity holonomy on every ordered triangle. -/
theorem flat_iff_triangleHolonomy_eq_refl :
    C.Flat ↔ ∀ a b c,
      C.triangleHolonomy a b c = LinearEquiv.refl R (F a) := by
  constructor
  · intro hflat a b c
    rw [← C.cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl a b c,
      C.cocycleDefect_eq_zero_iff_cocycleAt]
    exact hflat a b c
  · intro hhol a b c
    rw [← C.cocycleDefect_eq_zero_iff_cocycleAt,
      C.cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl]
    exact hhol a b c

/-! ## Canonical reversible transport from a family of frames -/

variable {M : Type z} [AddCommGroup M] [Module R M]

/-- Canonical transport from fibre `a` to fibre `b` through the ambient frame. -/
def canonicalTransport (frame : ∀ a, F a ≃ₗ[R] M) (a b : X) :
    F a ≃ₗ[R] F b :=
  (frame a).trans (frame b).symm

/--
The canonical reversible connection induced by fibre-to-ambient frames.
-/
def canonicalConnection (frame : ∀ a, F a ≃ₗ[R] M) :
    ReversibleConnection R X F where
  transport := canonicalTransport frame
  transport_self a := by
    apply LinearEquiv.ext
    intro x
    simp [canonicalTransport]
  transport_reverse _ _ := rfl

/-- Canonical frame transport satisfies the pair-cocycle law. -/
theorem canonicalConnection_flat (frame : ∀ a, F a ≃ₗ[R] M) :
    (canonicalConnection frame).Flat := by
  intro a b c
  apply LinearEquiv.ext
  intro x
  simp [canonicalConnection, canonicalTransport]

/-- Canonical frame transport has zero additive connection defect. -/
theorem canonicalTransport_zero_connectionDefect
    (frame : ∀ a, F a ≃ₗ[R] M) (a b c : X) :
    (canonicalConnection frame).cocycleDefect a b c = 0 := by
  rw [cocycleDefect_eq_zero_iff_cocycleAt]
  exact canonicalConnection_flat frame a b c

/-- Canonical frame transport has identity triangle holonomy. -/
theorem canonicalTransport_triangleHolonomy_eq_refl
    (frame : ∀ a, F a ≃ₗ[R] M) (a b c : X) :
    (canonicalConnection frame).triangleHolonomy a b c =
      LinearEquiv.refl R (F a) := by
  rw [← cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl]
  exact canonicalTransport_zero_connectionDefect frame a b c

/--
The fibrewise gauge comparing a flat connection with canonical transport,
based at a chosen vertex `o`.
-/
def flatGauge (frame : ∀ a, F a ≃ₗ[R] M) (o : X) :
    Gauge (R := R) (F := F) :=
  fun a ↦ (canonicalTransport frame a o).trans (C.transport o a)

/--
Every flat normalized reversible pair connection is a gauge transform of the
canonical connection induced by any family of ambient frames.
-/
theorem flat_isGaugeOfCanonical
    (hflat : C.Flat) (frame : ∀ a, F a ≃ₗ[R] M) (o a b : X) :
    C.transport a b =
      ((C.flatGauge frame o a).symm.trans
        ((canonicalConnection frame).transport a b)).trans
          (C.flatGauge frame o b) := by
  apply LinearEquiv.ext
  intro x
  have hg : (C.flatGauge frame o a).symm =
      (C.transport o a).symm.trans (canonicalTransport frame a o).symm := rfl
  rw [hg]
  have hcanonical_symm (p q : X) :
      (canonicalTransport frame p q).symm = canonicalTransport frame q p := rfl
  rw [hcanonical_symm]
  simp only [flatGauge, canonicalConnection, LinearEquiv.trans_apply]
  rw [show (C.transport o a).symm = C.transport a o by
    rw [C.transport_reverse o a]]
  simp only [canonicalTransport, LinearEquiv.trans_apply,
    LinearEquiv.symm_apply_apply, LinearEquiv.apply_symm_apply]
  have hao : (C.transport a o).trans (C.transport o b) = C.transport a b :=
    hflat a o b
  exact (congrArg (fun e : F a ≃ₗ[R] F b ↦ e x) hao).symm

/-! ## Finite path transport -/

/-- Transport along a finite list of successive vertices. -/
def pathTransport (C : ReversibleConnection R X F) (start : X) :
    (vertices : List X) → F start ≃ₗ[R] F (pathEndpoint start vertices)
  | [] => LinearEquiv.refl R (F start)
  | next :: rest =>
      (C.transport start next).trans (pathTransport C next rest)

/-- A finite path in a flat pair connection depends only on its endpoints. -/
theorem pathTransport_eq_direct_of_flat
    (hflat : C.Flat) (start : X) (vertices : List X) :
    C.pathTransport start vertices =
      C.transport start (pathEndpoint start vertices) := by
  induction vertices generalizing start with
  | nil =>
      change LinearEquiv.refl R (F start) = C.transport start start
      exact (C.transport_self start).symm
  | cons next rest ih =>
      simp only [pathTransport, pathEndpoint]
      rw [ih (start := next)]
      exact hflat start next (pathEndpoint next rest)

/-- A finite vertex path indexed by its source and target. -/
inductive VertexPath (X : Type v) : X → X → Type v where
  | nil (a : X) : VertexPath X a a
  | cons (a b c : X) (rest : VertexPath X b c) : VertexPath X a c

/-- Transport along a source-and-target-indexed finite path. -/
def indexedPathTransport :
    {a b : X} → VertexPath X a b → F a ≃ₗ[R] F b
  | _, _, .nil _ => LinearEquiv.refl R _
  | _, _, .cons a b _ rest =>
      (C.transport a b).trans (indexedPathTransport rest)

/-- Indexed finite path transport in a flat connection is endpoint-only. -/
theorem indexedPathTransport_eq_direct_of_flat (hflat : C.Flat) :
    ∀ {a b : X} (path : VertexPath X a b),
      indexedPathTransport C path = C.transport a b := by
  intro a b path
  induction path with
  | nil a => exact (C.transport_self a).symm
  | cons a b c rest ih =>
      simp only [indexedPathTransport]
      rw [ih]
      exact hflat a b c

/-- Every indexed finite loop in a flat connection has identity holonomy. -/
theorem indexedLoopTransport_eq_refl_of_flat
    (hflat : C.Flat) {a : X} (path : VertexPath X a a) :
    indexedPathTransport C path = LinearEquiv.refl R (F a) := by
  rw [indexedPathTransport_eq_direct_of_flat C hflat path, C.transport_self]

/-! ## Gauge action and covariance -/

/-- Gauge action: `Γᴳ(a,b) = G(b) ∘ Γ(a,b) ∘ G(a)⁻¹`. -/
def gauge (G : Gauge (R := R) (F := F)) : ReversibleConnection R X F where
  transport a b := ((G a).symm.trans (C.transport a b)).trans (G b)
  transport_self a := by
    apply LinearEquiv.ext
    intro x
    rw [C.transport_self]
    simp
  transport_reverse a b := by
    rw [C.transport_reverse a b]
    apply LinearEquiv.ext
    intro x
    simp

/-- The additive cocycle defect is gauge covariant. -/
theorem gauge_cocycleDefect
    (G : Gauge (R := R) (F := F)) (a b c : X) :
    (C.gauge G).cocycleDefect a b c =
      (G c).toLinearMap.comp
        ((C.cocycleDefect a b c).comp (G a).symm.toLinearMap) := by
  ext x
  simp [gauge, cocycleDefect]

/-- Triangle holonomy transforms by conjugation at its base vertex. -/
theorem gauge_triangleHolonomy
    (G : Gauge (R := R) (F := F)) (a b c : X) :
    (C.gauge G).triangleHolonomy a b c =
      ((G a).symm.trans (C.triangleHolonomy a b c)).trans (G a) := by
  apply LinearEquiv.ext
  intro x
  simp [gauge, triangleHolonomy]

/-- The cocycle equation at a fixed triple is gauge invariant. -/
theorem gauge_cocycleAt_iff
    (G : Gauge (R := R) (F := F)) (a b c : X) :
    (C.gauge G).CocycleAt a b c ↔ C.CocycleAt a b c := by
  constructor
  · intro h
    apply LinearEquiv.ext
    intro x
    have hx := congrArg
      (fun e : F a ≃ₗ[R] F c ↦ (G c).symm (e (G a x))) h
    simpa [CocycleAt, gauge] using hx
  · intro h
    apply LinearEquiv.ext
    intro x
    have hx := congrArg
      (fun e : F a ≃ₗ[R] F c ↦ G c (e ((G a).symm x))) h
    simpa [CocycleAt, gauge] using hx

/-- Algebraic flatness is gauge invariant. -/
theorem gauge_flat_iff (G : Gauge (R := R) (F := F)) :
    (C.gauge G).Flat ↔ C.Flat := by
  constructor
  · intro hflat a b c
    exact (C.gauge_cocycleAt_iff G a b c).mp (hflat a b c)
  · intro hflat a b c
    exact (C.gauge_cocycleAt_iff G a b c).mpr (hflat a b c)

/-- Identity/nonidentity of a fixed triangle holonomy is gauge invariant. -/
theorem gauge_triangleHolonomy_eq_refl_iff
    (G : Gauge (R := R) (F := F)) (a b c : X) :
    (C.gauge G).triangleHolonomy a b c = LinearEquiv.refl R (F a) ↔
      C.triangleHolonomy a b c = LinearEquiv.refl R (F a) := by
  rw [← (C.gauge G).cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl,
    ← C.cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl,
    (C.gauge G).cocycleDefect_eq_zero_iff_cocycleAt,
    C.cocycleDefect_eq_zero_iff_cocycleAt,
    C.gauge_cocycleAt_iff]

end ReversibleConnection
end Komorebi.PaperIII.Transport

namespace Komorebi.PaperIII.HolonomyBlocks

open scoped BigOperators

universe u v w

variable {R : Type u} {M : Type v} {I : Type w}
variable [CommRing R] [AddCommGroup M] [Module R M]

/--
A finite complete family of idempotent packet projectors.  Orthogonality is
not needed for exact two-sided reconstruction, so it is not assumed here.
-/
structure PacketResolution (R : Type u) (M : Type v) (I : Type w)
    [CommRing R] [AddCommGroup M] [Module R M] [Fintype I] where
  projector : I → M →ₗ[R] M
  complete : ∑ i, projector i = LinearMap.id
  idempotent : ∀ i, (projector i).comp (projector i) = projector i

namespace PacketResolution

variable [Fintype I]
variable (P : PacketResolution R M I)

/-- The packet block from input packet `nu` to output packet `mu`. -/
def block (A : M →ₗ[R] M) (mu nu : I) : M →ₗ[R] M :=
  (P.projector mu).comp (A.comp (P.projector nu))

/-- A complete finite packet family reconstructs every linear map by blocks. -/
theorem sum_blocks (A : M →ₗ[R] M) :
    ∑ mu, ∑ nu, P.block A mu nu = A := by
  have hcomplete (x : M) : ∑ i, P.projector i x = x := by
    have hx := congrArg (fun L : M →ₗ[R] M ↦ L x) P.complete
    simpa using hx
  ext x
  simp only [block, LinearMap.sum_apply, LinearMap.comp_apply]
  calc
    (∑ mu, ∑ nu, P.projector mu (A (P.projector nu x))) =
        ∑ mu, P.projector mu (A (∑ nu, P.projector nu x)) := by
          apply Finset.sum_congr rfl
          intro mu _
          calc
            (∑ nu, P.projector mu (A (P.projector nu x))) =
                P.projector mu (∑ nu, A (P.projector nu x)) := by
                  exact (map_sum (P.projector mu)
                    (fun nu ↦ A (P.projector nu x)) Finset.univ).symm
            _ = P.projector mu (A (∑ nu, P.projector nu x)) := by
                  congr 1
                  exact (map_sum A
                    (fun nu ↦ P.projector nu x) Finset.univ).symm
    _ = ∑ mu, P.projector mu (A x) := by rw [hcomplete x]
    _ = A x := hcomplete (A x)

/-- All finite packet blocks vanish exactly when the total map vanishes. -/
theorem blocks_zero_iff (A : M →ₗ[R] M) :
    (∀ mu nu, P.block A mu nu = 0) ↔ A = 0 := by
  constructor
  · intro h
    rw [← P.sum_blocks A]
    simp [h]
  · intro h mu nu
    simp [block, h]

/-- A nonzero block supplies a vector supported in its input packet. -/
theorem exists_packetWitness_of_block_ne_zero
    (A : M →ₗ[R] M) (mu nu : I) (hne : P.block A mu nu ≠ 0) :
    ∃ x, P.projector nu x = x ∧ P.projector mu (A x) ≠ 0 := by
  classical
  have hexists : ∃ y, P.block A mu nu y ≠ 0 := by
    by_contra h
    apply hne
    ext y
    by_contra hy
    exact h ⟨y, hy⟩
  rcases hexists with ⟨y, hy⟩
  refine ⟨P.projector nu y, ?_, ?_⟩
  · have hid := congrArg (fun L : M →ₗ[R] M ↦ L y) (P.idempotent nu)
    simpa using hid
  · simpa [block] using hy

end PacketResolution

variable {X : Type w} {F : X → Type v}
variable [∀ a, AddCommGroup (F a)] [∀ a, Module R (F a)]

/-- Exact double-sum reconstruction of a fixed triangle obstruction. -/
theorem obstruction_sum_blocks
    (C : Transport.ReversibleConnection R X F)
    {I : Type w} [Fintype I] (a b c : X)
    (P : PacketResolution R (F a) I) :
    ∑ mu, ∑ nu, P.block (C.triangleObstruction a b c) mu nu =
      C.triangleObstruction a b c :=
  P.sum_blocks (C.triangleObstruction a b c)

/--
For a fixed triangle, all holonomy-obstruction blocks vanish exactly when the
additive cocycle defect vanishes.
-/
theorem obstructionBlocks_zero_iff
    (C : Transport.ReversibleConnection R X F)
    {I : Type w} [Fintype I] (a b c : X)
    (P : PacketResolution R (F a) I) :
    (∀ mu nu,
      P.block (C.triangleObstruction a b c) mu nu = 0) ↔
      C.cocycleDefect a b c = 0 := by
  rw [P.blocks_zero_iff,
    C.triangleObstruction_eq_zero_iff_cocycleDefect_eq_zero]

/--
The four vanishing criteria in the obstruction-packet theorem are mutually
equivalent: zero defect, identity holonomy, zero total obstruction, and zero
of every finite packet block.
-/
theorem obstructionDetection_equivalences
    (C : Transport.ReversibleConnection R X F)
    {I : Type w} [Fintype I] (a b c : X)
    (P : PacketResolution R (F a) I) :
    (C.cocycleDefect a b c = 0 ↔
      C.triangleHolonomy a b c = LinearEquiv.refl R (F a)) ∧
    (C.triangleHolonomy a b c = LinearEquiv.refl R (F a) ↔
      C.triangleObstruction a b c = 0) ∧
    (C.triangleObstruction a b c = 0 ↔
      ∀ mu nu, P.block (C.triangleObstruction a b c) mu nu = 0) := by
  refine ⟨C.cocycleDefect_eq_zero_iff_triangleHolonomy_eq_refl a b c, ?_⟩
  refine ⟨(C.triangleObstruction_eq_zero_iff_triangleHolonomy_eq_refl
    a b c).symm, ?_⟩
  exact (P.blocks_zero_iff (C.triangleObstruction a b c)).symm

/-- A nonzero holonomy block gives an exact packet-supported witness. -/
theorem exists_packetWitness_of_obstructionBlock_ne_zero
    (C : Transport.ReversibleConnection R X F)
    {I : Type w} [Fintype I] (a b c : X)
    (P : PacketResolution R (F a) I) (mu nu : I)
    (hne : P.block (C.triangleObstruction a b c) mu nu ≠ 0) :
    ∃ x,
      P.projector nu x = x ∧
      P.projector mu (C.triangleObstruction a b c x) ≠ 0 :=
  P.exists_packetWitness_of_block_ne_zero
    (C.triangleObstruction a b c) mu nu hne

end Komorebi.PaperIII.HolonomyBlocks
