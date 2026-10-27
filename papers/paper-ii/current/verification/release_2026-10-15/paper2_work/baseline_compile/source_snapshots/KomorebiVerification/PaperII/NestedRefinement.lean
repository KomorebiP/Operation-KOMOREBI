import KomorebiVerification.ExactCoordinates

/-!
# Nested refinement of exact projector coordinates

Author: Komorebi P.

This module formalizes the algebraic nested-refinement results of Paper II.
A refinement consists of a surjective parent map together with exact recovery
of every coarse projector as the finite sum of its fine children.  The file
proves the two absorption orders, canonical reconstruction and uniqueness,
transitivity, exact cross-level range coordinates, and refinement of transfer
blocks.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.NestedRefinement

open Komorebi.Foundation
open Komorebi.Foundation.LinearProjectorFamily

universe u v w x y z

variable {R : Type u} {M : Type v}
variable {ι : Type w} {κ : Type x} {τ : Type y}
variable [Semiring R] [AddCommMonoid M] [Module R M]
variable [Fintype ι] [Fintype κ] [Fintype τ]

/-! ## Refinement data -/

/-- The finite set of fine indices having the specified coarse parent. -/
noncomputable def children (parent : κ → ι) (a : ι) : Finset κ := by
  classical
  exact Finset.univ.filter (fun b => parent b = a)

omit [Fintype ι] in
@[simp] theorem mem_children (parent : κ → ι) (a : ι) (b : κ) :
    b ∈ children parent a ↔ parent b = a := by
  classical
  simp [children]

/--
`fine` refines `coarse` along `parent` when `parent` is surjective and every
coarse projector is exactly the sum of the fine projectors over its fibre.
-/
structure Refines
    (coarse : LinearProjectorFamily R M ι)
    (fine : LinearProjectorFamily R M κ)
    (parent : κ → ι) : Prop where
  surjective : Function.Surjective parent
  coarse_eq_sum_children :
    ∀ a, coarse.proj a = ∑ b ∈ children parent a, fine.proj b

/-! ## Generic finite-packet uniqueness -/

/--
For any finite collection of mutually orthogonal projector ranges, applying the
corresponding projector recovers its summand.  No parent map, surjectivity, or
coarse-projector reconstruction is needed.
-/
theorem finitePacket_decomposition_unique
    (P : LinearProjectorFamily R M κ) (s : Finset κ) (x : M)
    (packets : κ → M)
    (hrange : ∀ b ∈ s, packets b ∈ LinearMap.range (P.proj b))
    (hsum : ∑ b ∈ s, packets b = x) :
    ∀ b ∈ s, packets b = P.proj b x := by
  classical
  intro b hb
  have hself : P.proj b (packets b) = packets b := by
    rcases hrange b hb with ⟨y, hy⟩
    rw [← hy]
    exact P.idempotent b y
  have hproject : P.proj b (∑ j ∈ s, packets j) = packets b := by
    rw [map_sum]
    calc
      (∑ j ∈ s, P.proj b (packets j)) = P.proj b (packets b) := by
        apply Finset.sum_eq_single_of_mem b hb
        intro j hj hjb
        rcases hrange j hj with ⟨y, hy⟩
        rw [← hy]
        exact P.orthogonal hjb.symm y
      _ = packets b := hself
  calc
    packets b = P.proj b (∑ j ∈ s, packets j) := hproject.symm
    _ = P.proj b x := congrArg (P.proj b) hsum

/-- Two finite decompositions into the same orthogonal packet ranges agree. -/
theorem finitePacket_decomposition_ext
    (P : LinearProjectorFamily R M κ) (s : Finset κ)
    (packets packets' : κ → M)
    (hrange : ∀ b ∈ s, packets b ∈ LinearMap.range (P.proj b))
    (hrange' : ∀ b ∈ s, packets' b ∈ LinearMap.range (P.proj b))
    (hsum : ∑ b ∈ s, packets b = ∑ b ∈ s, packets' b) :
    ∀ b ∈ s, packets b = packets' b := by
  intro b hb
  calc
    packets b = P.proj b (∑ j ∈ s, packets j) :=
      finitePacket_decomposition_unique P s _ packets hrange rfl b hb
    _ = P.proj b (∑ j ∈ s, packets' j) := congrArg (P.proj b) hsum
    _ = packets' b :=
      (finitePacket_decomposition_unique P s _ packets' hrange' rfl b hb).symm

namespace Refines

variable {coarse : LinearProjectorFamily R M ι}
variable {fine : LinearProjectorFamily R M κ}
variable {parent : κ → ι}

/-- Pointwise form of the defining coarse-projector reconstruction. -/
theorem coarse_proj_apply_eq_sum_children
    (h : Refines coarse fine parent) (a : ι) (x : M) :
    coarse.proj a x = ∑ b ∈ children parent a, fine.proj b x := by
  rw [h.coarse_eq_sum_children a]
  simp only [LinearMap.sum_apply]

/-! ## Absorption in both orders -/

/-- A coarse projector absorbs a fine child on the left. -/
theorem coarse_comp_fine_eq_self
    (h : Refines coarse fine parent) {a : ι} {b : κ}
    (hb : parent b = a) :
    (coarse.proj a).comp (fine.proj b) = fine.proj b := by
  classical
  ext x
  simp only [LinearMap.comp_apply]
  rw [h.coarse_proj_apply_eq_sum_children]
  have hbmem : b ∈ children parent a := (mem_children parent a b).2 hb
  calc
    (∑ j ∈ children parent a, fine.proj j (fine.proj b x)) =
        fine.proj b (fine.proj b x) := by
          apply Finset.sum_eq_single_of_mem b hbmem
          intro j _ hjb
          exact fine.orthogonal hjb x
    _ = fine.proj b x := fine.idempotent b x

/-- A non-parent coarse projector annihilates a fine packet on the left. -/
theorem coarse_comp_fine_eq_zero
    (h : Refines coarse fine parent) {a : ι} {b : κ}
    (hb : parent b ≠ a) :
    (coarse.proj a).comp (fine.proj b) = 0 := by
  classical
  ext x
  simp only [LinearMap.comp_apply, LinearMap.zero_apply]
  rw [h.coarse_proj_apply_eq_sum_children]
  apply Finset.sum_eq_zero
  intro j hj
  have hjparent : parent j = a := (mem_children parent a j).1 hj
  have hjb : j ≠ b := by
    intro hjb
    subst j
    exact hb hjparent
  exact fine.orthogonal hjb x

/-- A fine child absorbs its coarse parent on the right. -/
theorem fine_comp_coarse_eq_self
    (h : Refines coarse fine parent) {a : ι} {b : κ}
    (hb : parent b = a) :
    (fine.proj b).comp (coarse.proj a) = fine.proj b := by
  classical
  ext x
  simp only [LinearMap.comp_apply]
  rw [h.coarse_proj_apply_eq_sum_children, map_sum]
  have hbmem : b ∈ children parent a := (mem_children parent a b).2 hb
  calc
    (∑ j ∈ children parent a, fine.proj b (fine.proj j x)) =
        fine.proj b (fine.proj b x) := by
          apply Finset.sum_eq_single_of_mem b hbmem
          intro j _ hjb
          exact fine.orthogonal hjb.symm x
    _ = fine.proj b x := fine.idempotent b x

/-- A fine projector annihilates a non-parent coarse packet on the right. -/
theorem fine_comp_coarse_eq_zero
    (h : Refines coarse fine parent) {a : ι} {b : κ}
    (hb : parent b ≠ a) :
    (fine.proj b).comp (coarse.proj a) = 0 := by
  classical
  ext x
  simp only [LinearMap.comp_apply, LinearMap.zero_apply]
  rw [h.coarse_proj_apply_eq_sum_children, map_sum]
  apply Finset.sum_eq_zero
  intro j hj
  have hjparent : parent j = a := (mem_children parent a j).1 hj
  have hbj : b ≠ j := by
    intro hbj
    subst j
    exact hb hjparent
  exact fine.orthogonal hbj x

/-- Pointwise left absorption by the parent. -/
theorem coarse_fine_apply_eq_self
    (h : Refines coarse fine parent) (b : κ) (x : M) :
    coarse.proj (parent b) (fine.proj b x) = fine.proj b x := by
  exact LinearMap.congr_fun (h.coarse_comp_fine_eq_self rfl) x

/-- Pointwise right absorption by the parent. -/
theorem fine_coarse_apply_eq_self
    (h : Refines coarse fine parent) (b : κ) (x : M) :
    fine.proj b (coarse.proj (parent b) x) = fine.proj b x := by
  exact LinearMap.congr_fun (h.fine_comp_coarse_eq_self rfl) x

/-! ## Reconstruction and uniqueness -/

/-- Every vector in a coarse projector range is the sum of its fine children. -/
theorem coarse_packet_reconstruction
    (h : Refines coarse fine parent) (a : ι)
    (x : LinearMap.range (coarse.proj a)) :
    (x : M) = ∑ b ∈ children parent a, fine.proj b (x : M) := by
  have hx : coarse.proj a (x : M) = (x : M) := by
    rcases x.property with ⟨y, hy⟩
    rw [← hy]
    exact coarse.idempotent a y
  exact hx.symm.trans (h.coarse_proj_apply_eq_sum_children a (x : M))

/--
A sum of vectors belonging to distinct fine-child ranges has uniquely
determined components: the `b`-component is obtained by applying `fine.proj b`.
-/
theorem child_decomposition_unique
    (_h : Refines coarse fine parent) (a : ι) (x : M)
    (packets : κ → M)
    (hrange : ∀ b ∈ children parent a,
      packets b ∈ LinearMap.range (fine.proj b))
    (hsum : ∑ b ∈ children parent a, packets b = x) :
    ∀ b ∈ children parent a, packets b = fine.proj b x := by
  exact finitePacket_decomposition_unique
    fine (children parent a) x packets hrange hsum

/-- Two decompositions into the same fine-child ranges with the same sum agree. -/
theorem child_decomposition_ext
    (_h : Refines coarse fine parent) (a : ι)
    (packets packets' : κ → M)
    (hrange : ∀ b ∈ children parent a,
      packets b ∈ LinearMap.range (fine.proj b))
    (hrange' : ∀ b ∈ children parent a,
      packets' b ∈ LinearMap.range (fine.proj b))
    (hsum : ∑ b ∈ children parent a, packets b =
      ∑ b ∈ children parent a, packets' b) :
    ∀ b ∈ children parent a, packets b = packets' b := by
  exact finitePacket_decomposition_ext
    fine (children parent a) packets packets' hrange hrange' hsum

/-! ## Transitivity -/

variable {middle : LinearProjectorFamily R M κ}
variable {finest : LinearProjectorFamily R M τ}
variable {parent₁ : κ → ι} {parent₂ : τ → κ}

/-- Refinement is transitive, with the composite parent map. -/
theorem trans
    (h₁ : Refines coarse middle parent₁)
    (h₂ : Refines middle finest parent₂) :
    Refines coarse finest (parent₁ ∘ parent₂) := by
  classical
  refine ⟨?_, ?_⟩
  · intro a
    rcases h₁.surjective a with ⟨b, rfl⟩
    rcases h₂.surjective b with ⟨c, rfl⟩
    exact ⟨c, rfl⟩
  · intro a
    ext x
    simp only [LinearMap.sum_apply]
    calc
      coarse.proj a x = coarse.proj a (∑ c, finest.proj c x) := by
        rw [finest.complete x]
      _ = ∑ c, coarse.proj a (finest.proj c x) := by
        rw [map_sum]
      _ = ∑ c, if parent₁ (parent₂ c) = a then finest.proj c x else 0 := by
        apply Finset.sum_congr rfl
        intro c _
        by_cases hc : parent₁ (parent₂ c) = a
        · simp only [hc, ↓reduceIte]
          rw [← h₂.coarse_fine_apply_eq_self c x]
          exact LinearMap.congr_fun (h₁.coarse_comp_fine_eq_self hc) _
        · simp only [hc, ↓reduceIte]
          rw [← h₂.coarse_fine_apply_eq_self c x]
          exact LinearMap.congr_fun (h₁.coarse_comp_fine_eq_zero hc) _
      _ = ∑ c ∈ children (parent₁ ∘ parent₂) a, finest.proj c x := by
        rw [children, Finset.sum_filter]
        simp only [Function.comp_apply]

end Refines

/-! ## Exact range-coordinate transport -/

section Coordinates

variable (coarse : LinearProjectorFamily R M ι)
variable (fine : LinearProjectorFamily R M κ)

/-- Resolve coarse range coordinates by synthesis followed by fine analysis. -/
def refineCoordinates : PacketSpace coarse →ₗ[R] PacketSpace fine :=
  fine.rangeAnalysis.comp coarse.rangeSynthesis

/-- Regroup fine range coordinates by synthesis followed by coarse analysis. -/
def coarsenCoordinates : PacketSpace fine →ₗ[R] PacketSpace coarse :=
  coarse.rangeAnalysis.comp fine.rangeSynthesis

@[simp] theorem refineCoordinates_apply (packets : PacketSpace coarse) :
    refineCoordinates coarse fine packets =
      fine.rangeAnalysis (coarse.rangeSynthesis packets) := rfl

@[simp] theorem coarsenCoordinates_apply (packets : PacketSpace fine) :
    coarsenCoordinates coarse fine packets =
      coarse.rangeAnalysis (fine.rangeSynthesis packets) := rfl

/-- Refinement carries the coarse analysis of a vector to its fine analysis. -/
@[simp] theorem refineCoordinates_rangeAnalysis (x : M) :
    refineCoordinates coarse fine (coarse.rangeAnalysis x) =
      fine.rangeAnalysis x := by
  simp [refineCoordinates]

/-- Fine synthesis after refinement is the original coarse synthesis. -/
@[simp] theorem rangeSynthesis_refineCoordinates
    (packets : PacketSpace coarse) :
    fine.rangeSynthesis (refineCoordinates coarse fine packets) =
      coarse.rangeSynthesis packets := by
  simp [refineCoordinates]

/-- Coarsening carries the fine analysis of a vector to its coarse analysis. -/
@[simp] theorem coarsenCoordinates_rangeAnalysis (x : M) :
    coarsenCoordinates coarse fine (fine.rangeAnalysis x) =
      coarse.rangeAnalysis x := by
  simp [coarsenCoordinates]

/-- Coarse synthesis after coarsening is the original fine synthesis. -/
@[simp] theorem rangeSynthesis_coarsenCoordinates
    (packets : PacketSpace fine) :
    coarse.rangeSynthesis (coarsenCoordinates coarse fine packets) =
      fine.rangeSynthesis packets := by
  simp [coarsenCoordinates]

/-- Coarsening after refinement is the identity on coarse range coordinates. -/
@[simp] theorem coarsenCoordinates_refineCoordinates
    (packets : PacketSpace coarse) :
    coarsenCoordinates coarse fine (refineCoordinates coarse fine packets) =
      packets := by
  simp [coarsenCoordinates, refineCoordinates]

/-- Refinement after coarsening is the identity on fine range coordinates. -/
@[simp] theorem refineCoordinates_coarsenCoordinates
    (packets : PacketSpace fine) :
    refineCoordinates coarse fine (coarsenCoordinates coarse fine packets) =
      packets := by
  simp [coarsenCoordinates, refineCoordinates]

/-- The exact linear equivalence between the two independent range products. -/
def coordinateRefinementEquiv : PacketSpace coarse ≃ₗ[R] PacketSpace fine where
  toFun := refineCoordinates coarse fine
  invFun := coarsenCoordinates coarse fine
  left_inv := coarsenCoordinates_refineCoordinates coarse fine
  right_inv := refineCoordinates_coarsenCoordinates coarse fine
  map_add' := (refineCoordinates coarse fine).map_add
  map_smul' := (refineCoordinates coarse fine).map_smul

@[simp] theorem coordinateRefinementEquiv_apply (packets : PacketSpace coarse) :
    coordinateRefinementEquiv coarse fine packets =
      refineCoordinates coarse fine packets := rfl

@[simp] theorem coordinateRefinementEquiv_symm_apply (packets : PacketSpace fine) :
    (coordinateRefinementEquiv coarse fine).symm packets =
      coarsenCoordinates coarse fine packets := rfl

/-! ## Identity and cocycle laws -/

/-- Refining a coordinate system to itself is pointwise the identity. -/
@[simp] theorem refineCoordinates_self (packets : PacketSpace coarse) :
    refineCoordinates coarse coarse packets = packets := by
  simp [refineCoordinates]

/-- Coarsening a coordinate system to itself is pointwise the identity. -/
@[simp] theorem coarsenCoordinates_self (packets : PacketSpace coarse) :
    coarsenCoordinates coarse coarse packets = packets := by
  simp [coarsenCoordinates]

/-- Coarsening is definitionally refinement in the reverse direction. -/
theorem coarsenCoordinates_eq_refineCoordinates_reverse :
    coarsenCoordinates coarse fine = refineCoordinates fine coarse := rfl

variable (middle : LinearProjectorFamily R M τ)

/-- Exact coordinate refinement obeys the pointwise cocycle law. -/
@[simp] theorem refineCoordinates_cocycle (packets : PacketSpace coarse) :
    refineCoordinates middle fine (refineCoordinates coarse middle packets) =
      refineCoordinates coarse fine packets := by
  simp [refineCoordinates]

/-- The cocycle law as an equality of linear coordinate-change maps. -/
theorem refineCoordinates_comp :
    (refineCoordinates middle fine).comp (refineCoordinates coarse middle) =
      refineCoordinates coarse fine := by
  apply LinearMap.ext
  intro packets
  exact refineCoordinates_cocycle coarse fine middle packets

/-- Reverse coordinate transport obeys the corresponding cocycle law. -/
@[simp] theorem coarsenCoordinates_cocycle (packets : PacketSpace fine) :
    coarsenCoordinates coarse middle (coarsenCoordinates middle fine packets) =
      coarsenCoordinates coarse fine packets := by
  simp [coarsenCoordinates]

/-- The exact coordinate equivalence at one level is the identity equivalence. -/
@[simp] theorem coordinateRefinementEquiv_self :
    coordinateRefinementEquiv coarse coarse = LinearEquiv.refl R (PacketSpace coarse) := by
  apply LinearEquiv.ext
  intro packets
  simp

/-- Reversing the coordinate equivalence swaps its endpoint families. -/
theorem coordinateRefinementEquiv_symm :
    (coordinateRefinementEquiv coarse fine).symm =
      coordinateRefinementEquiv fine coarse := by
  apply LinearEquiv.ext
  intro packets
  rfl

/-- Exact coordinate equivalences compose coherently through an intermediate level. -/
theorem coordinateRefinementEquiv_trans :
    (coordinateRefinementEquiv coarse middle).trans
        (coordinateRefinementEquiv middle fine) =
      coordinateRefinementEquiv coarse fine := by
  apply LinearEquiv.ext
  intro packets
  exact refineCoordinates_cocycle coarse fine middle packets

end Coordinates

/-! ## Typed operator coordinates and naturality -/

section CoordinateNaturality

variable {N : Type z} {L : Type*}
variable [AddCommMonoid N] [Module R N]
variable [AddCommMonoid L] [Module R L]
variable {ι' : Type*} {κ' : Type*} {τ' : Type*}
variable [Fintype ι'] [Fintype κ'] [Fintype τ']

/--
The typed coordinate representation of a linear map between two independently
chosen exact packet systems.
-/
def coordinateOperator
    (source : LinearProjectorFamily R M ι)
    (target : LinearProjectorFamily R N κ')
    (T : M →ₗ[R] N) : PacketSpace source →ₗ[R] PacketSpace target :=
  target.rangeAnalysis.comp (T.comp source.rangeSynthesis)

@[simp] theorem coordinateOperator_apply
    (source : LinearProjectorFamily R M ι)
    (target : LinearProjectorFamily R N κ')
    (T : M →ₗ[R] N) (packets : PacketSpace source) :
    coordinateOperator source target T packets =
      target.rangeAnalysis (T (source.rangeSynthesis packets)) := rfl

/-- Analysis intertwines a linear map with its exact coordinate representation. -/
@[simp] theorem coordinateOperator_rangeAnalysis
    (source : LinearProjectorFamily R M ι)
    (target : LinearProjectorFamily R N κ')
    (T : M →ₗ[R] N) (x : M) :
    coordinateOperator source target T (source.rangeAnalysis x) =
      target.rangeAnalysis (T x) := by
  simp [coordinateOperator]

/-- Synthesis intertwines an exact coordinate representation with its linear map. -/
@[simp] theorem rangeSynthesis_coordinateOperator
    (source : LinearProjectorFamily R M ι)
    (target : LinearProjectorFamily R N κ')
    (T : M →ₗ[R] N) (packets : PacketSpace source) :
    target.rangeSynthesis (coordinateOperator source target T packets) =
      T (source.rangeSynthesis packets) := by
  simp [coordinateOperator]

/-- Representing the identity between two packet systems is coordinate refinement. -/
theorem coordinateOperator_id_eq_refineCoordinates
    (source : LinearProjectorFamily R M ι)
    (target : LinearProjectorFamily R M κ) :
    coordinateOperator source target LinearMap.id =
      refineCoordinates source target := by
  apply LinearMap.ext
  intro packets
  rfl

/-- In one fixed packet system, the represented identity is the identity map. -/
@[simp] theorem coordinateOperator_id
    (source : LinearProjectorFamily R M ι) :
    coordinateOperator source source LinearMap.id = LinearMap.id := by
  rw [coordinateOperator_id_eq_refineCoordinates]
  apply LinearMap.ext
  intro packets
  simp

/-- Coordinate representation preserves typed composition. -/
theorem coordinateOperator_comp
    (source : LinearProjectorFamily R M ι)
    (middle : LinearProjectorFamily R N κ')
    (target : LinearProjectorFamily R L τ')
    (T : M →ₗ[R] N) (U : N →ₗ[R] L) :
    (coordinateOperator middle target U).comp
        (coordinateOperator source middle T) =
      coordinateOperator source target (U.comp T) := by
  ext packets
  simp [coordinateOperator]

/--
Changing exact coordinates on both source and target commutes with the typed
coordinate representation of every linear map.
-/
theorem coordinateOperator_naturality
    (sourceCoarse : LinearProjectorFamily R M ι)
    (sourceFine : LinearProjectorFamily R M κ)
    (targetCoarse : LinearProjectorFamily R N ι')
    (targetFine : LinearProjectorFamily R N κ')
    (T : M →ₗ[R] N) :
    (refineCoordinates targetCoarse targetFine).comp
        (coordinateOperator sourceCoarse targetCoarse T) =
      (coordinateOperator sourceFine targetFine T).comp
        (refineCoordinates sourceCoarse sourceFine) := by
  ext packets
  simp [coordinateOperator, refineCoordinates]

/-- The pointwise commuting-square form of coordinate-operator naturality. -/
theorem coordinateOperator_naturality_apply
    (sourceCoarse : LinearProjectorFamily R M ι)
    (sourceFine : LinearProjectorFamily R M κ)
    (targetCoarse : LinearProjectorFamily R N ι')
    (targetFine : LinearProjectorFamily R N κ')
    (T : M →ₗ[R] N) (packets : PacketSpace sourceCoarse) :
    refineCoordinates targetCoarse targetFine
        (coordinateOperator sourceCoarse targetCoarse T packets) =
      coordinateOperator sourceFine targetFine T
        (refineCoordinates sourceCoarse sourceFine packets) := by
  exact LinearMap.congr_fun
    (coordinateOperator_naturality
      sourceCoarse sourceFine targetCoarse targetFine T) packets

end CoordinateNaturality

/-! ## Parent/child formulas for exact coordinates -/

namespace Refines

variable {coarse : LinearProjectorFamily R M ι}
variable {fine : LinearProjectorFamily R M κ}
variable {parent : κ → ι}

/-- A refined coordinate only sees the coarse coordinate of its parent. -/
theorem refineCoordinates_component
    (h : Refines coarse fine parent) (packets : PacketSpace coarse) (b : κ) :
    ((refineCoordinates coarse fine packets b :
      LinearMap.range (fine.proj b)) : M) =
      fine.proj b (packets (parent b) : M) := by
  classical
  change fine.proj b (∑ a, (packets a : M)) = _
  rw [map_sum]
  apply Finset.sum_eq_single_of_mem (parent b) (Finset.mem_univ _)
  intro a _ hab
  rcases (packets a).property with ⟨x, hx⟩
  rw [← hx]
  exact LinearMap.congr_fun
    (h.fine_comp_coarse_eq_zero (Ne.symm hab)) x

/-- A coarsened coordinate is the sum of the fine coordinates over its fibre. -/
theorem coarsenCoordinates_component
    (h : Refines coarse fine parent) (packets : PacketSpace fine) (a : ι) :
    ((coarsenCoordinates coarse fine packets a :
      LinearMap.range (coarse.proj a)) : M) =
      ∑ b ∈ children parent a, (packets b : M) := by
  classical
  change coarse.proj a (∑ b, (packets b : M)) = _
  rw [map_sum]
  calc
    (∑ b, coarse.proj a (packets b : M)) =
        ∑ b, if parent b = a then (packets b : M) else 0 := by
          apply Finset.sum_congr rfl
          intro b _
          rcases (packets b).property with ⟨x, hx⟩
          rw [← hx]
          by_cases hb : parent b = a
          · simp only [hb, ↓reduceIte]
            exact LinearMap.congr_fun (h.coarse_comp_fine_eq_self hb) x
          · simp only [hb, ↓reduceIte]
            exact LinearMap.congr_fun (h.coarse_comp_fine_eq_zero hb) x
    _ = ∑ b ∈ children parent a, (packets b : M) := by
      rw [children, Finset.sum_filter]

end Refines

/-! ## Transfer-block refinement -/

section TransferBlocks

variable {N : Type z} {ι' : Type*} {κ' : Type*}
variable [AddCommMonoid N] [Module R N]
variable [Fintype ι'] [Fintype κ']

variable {sourceCoarse : LinearProjectorFamily R M ι}
variable {sourceFine : LinearProjectorFamily R M κ}
variable {targetCoarse : LinearProjectorFamily R N ι'}
variable {targetFine : LinearProjectorFamily R N κ'}
variable {sourceParent : κ → ι} {targetParent : κ' → ι'}

/--
Both sides of a linear transfer block refine independently into their fine
descendants.  This is the two-module strengthening of the Paper II formula.
-/
theorem transferBlock_refinement_between
    (hsource : Refines sourceCoarse sourceFine sourceParent)
    (htarget : Refines targetCoarse targetFine targetParent)
    (T : M →ₗ[R] N) (b : ι') (a : ι) :
    transferBlock sourceCoarse targetCoarse T b a =
      ∑ β ∈ children targetParent b,
        ∑ α ∈ children sourceParent a,
          transferBlock sourceFine targetFine T β α := by
  classical
  ext x
  simp only [transferBlock, LinearMap.comp_apply, LinearMap.sum_apply]
  rw [hsource.coarse_proj_apply_eq_sum_children, map_sum]
  calc
    targetCoarse.proj b
        (∑ α ∈ children sourceParent a, T (sourceFine.proj α x)) =
      ∑ α ∈ children sourceParent a,
        targetCoarse.proj b (T (sourceFine.proj α x)) := by
          rw [map_sum]
    _ = ∑ α ∈ children sourceParent a,
        ∑ β ∈ children targetParent b,
          targetFine.proj β (T (sourceFine.proj α x)) := by
          apply Finset.sum_congr rfl
          intro α _
          exact htarget.coarse_proj_apply_eq_sum_children b _
    _ = ∑ β ∈ children targetParent b,
        ∑ α ∈ children sourceParent a,
          targetFine.proj β (T (sourceFine.proj α x)) := by
          exact Finset.sum_comm

variable {coarse : LinearProjectorFamily R M ι}
variable {fine : LinearProjectorFamily R M κ}
variable {parent : κ → ι}

/-- Every endomorphism block is the sum of all fine descendant blocks. -/
theorem transferBlock_refinement
    (h : Refines coarse fine parent) (T : Module.End R M) (b a : ι) :
    transferBlock coarse coarse T b a =
      ∑ β ∈ children parent b,
        ∑ α ∈ children parent a,
          transferBlock fine fine T β α :=
  transferBlock_refinement_between h h T b a

/--
Direct traceability wrapper for the complete transfer-block statement in the
Paper II manuscript.  It records the refined block identity together with
reconstruction of the same linear map from all coarse and all fine blocks.
-/
theorem transferBlock_refinement_and_reconstruction
    (hsource : Refines sourceCoarse sourceFine sourceParent)
    (htarget : Refines targetCoarse targetFine targetParent)
    (T : M →ₗ[R] N) (b : ι') (a : ι) :
    transferBlock sourceCoarse targetCoarse T b a =
        ∑ β ∈ children targetParent b,
          ∑ α ∈ children sourceParent a,
            transferBlock sourceFine targetFine T β α ∧
      (∀ x : M,
        (∑ β, ∑ α,
          targetCoarse.proj β (T (sourceCoarse.proj α x))) = T x) ∧
      (∀ x : M,
        (∑ β, ∑ α,
          targetFine.proj β (T (sourceFine.proj α x))) = T x) := by
  exact ⟨transferBlock_refinement_between hsource htarget T b a,
    transferBlock_reconstruction sourceCoarse targetCoarse T,
    transferBlock_reconstruction sourceFine targetFine T⟩

end TransferBlocks

end Komorebi.PaperII.NestedRefinement

#print axioms Komorebi.PaperII.NestedRefinement.Refines.trans
#print axioms Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv
#print axioms Komorebi.PaperII.NestedRefinement.finitePacket_decomposition_unique
#print axioms Komorebi.PaperII.NestedRefinement.refineCoordinates_comp
#print axioms Komorebi.PaperII.NestedRefinement.coordinateRefinementEquiv_trans
#print axioms Komorebi.PaperII.NestedRefinement.coordinateOperator_naturality
#print axioms Komorebi.PaperII.NestedRefinement.transferBlock_refinement
