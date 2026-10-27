/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiVerification.ExactCoordinates
import KomorebiVerification.PaperIBlockCompletion
import KomorebiVerification.PaperITransport
import KomorebiVerification.SeedRankBasics

/-!
# Paper I: packet, block, reachability, and naturality completion

This module closes the remaining finite algebraic content of the packet and
naturality portions of Paper I.  It supplies the literal packetwise equality
equivalence, a recursive path expansion for every packet power, an exact
equivalence between endomorphisms and arbitrary packet-to-packet linear maps,
the associated dimension and support laws, an algebraic reachability
obstruction, coordinate invariance of transfer edges, a fully typed strict
morphism, and the finite two-vertex quiver certificate from the paper.
-/

set_option autoImplicit false

-- Suppress only style/unused lints in the frozen completion proofs; warnings remain fatal.
set_option linter.unnecessarySeqFocus false
set_option linter.unnecessarySimpa false
set_option linter.unusedSectionVars false
set_option linter.unusedVariables false
set_option maxHeartbeats 4000000
set_option maxRecDepth 100000

namespace Komorebi.PacketNaturalityCompletion

open scoped BigOperators

namespace Packets

open Foundation
open Foundation.LinearProjectorFamily

universe u v w

variable {R : Type u} {M : Type v} {ι : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M]
variable [Fintype ι] [DecidableEq ι]

/-- Literal `if and only if` form of packetwise equality. -/
theorem eq_iff_projectors_eq
    (P : LinearProjectorFamily R M ι) (x y : M) :
    x = y ↔ ∀ i, P.proj i x = P.proj i y := by
  constructor
  · rintro rfl i
    rfl
  · exact P.eq_of_projectors_eq

/--
The recursively expanded sum of all length-`m` packet paths from `a` to `b`.
At a successor step, the final factor is a one-step transfer block.
-/
noncomputable def packetPathSum
    (P : LinearProjectorFamily R M ι) (T : Module.End R M) :
    ℕ → ι → ι → Module.End R M
  | 0, b, a => if b = a then P.proj a else 0
  | m + 1, b, a =>
      ∑ c, (packetPathSum P T m b c).comp (transferBlock P P T c a)

@[simp] theorem packetPathSum_zero_same
    (P : LinearProjectorFamily R M ι) (T : Module.End R M) (a : ι) :
    packetPathSum P T 0 a a = P.proj a := by
  simp [packetPathSum]

theorem packetPathSum_zero_ne
    (P : LinearProjectorFamily R M ι) (T : Module.End R M)
    {b a : ι} (h : b ≠ a) :
    packetPathSum P T 0 b a = 0 := by
  simp [packetPathSum, h]

/-- The zero-th power has the expected diagonal packet blocks. -/
theorem transferBlock_pow_zero
    (P : LinearProjectorFamily R M ι) (T : Module.End R M) (b a : ι) :
    transferBlock P P ((1 : Module.End R M)) b a =
      packetPathSum P T 0 b a := by
  classical
  ext x
  by_cases h : b = a
  · subst b
    simp [transferBlock, packetPathSum, P.idempotent]
  · simp [transferBlock, packetPathSum, h, P.orthogonal h]

/--
Full packet-power path expansion, including the diagonal length-zero case.
The successor clause of `packetPathSum` is precisely the sum over all choices
of the first intermediate packet after the input packet.
-/
theorem transferBlock_pow_eq_packetPathSum
    (P : LinearProjectorFamily R M ι) (T : Module.End R M) :
    ∀ m b a, transferBlock P P (T ^ m) b a = packetPathSum P T m b a := by
  classical
  intro m
  induction m with
  | zero =>
      intro b a
      simpa using transferBlock_pow_zero P T b a
  | succ m ih =>
      intro b a
      rw [pow_succ]
      change transferBlock P P ((T ^ m).comp T) b a = _
      rw [Foundation.transferBlock_comp_end]
      simp only [packetPathSum]
      apply Finset.sum_congr rfl
      intro c hc
      rw [ih]

end Packets

namespace FullBlocks

open Foundation
open Foundation.LinearProjectorFamily

universe u v w

variable {R : Type u} {M : Type v} {ι : Type w}
variable [CommSemiring R] [AddCommMonoid M] [Module R M]
variable [Fintype ι] [DecidableEq ι]

/-- A fully arbitrary heterogeneous matrix of packet-to-packet linear maps. -/
abbrev PacketBlocks (P : LinearProjectorFamily R M ι) : Type max v w :=
  (b : ι) → (a : ι) →
    LinearMap.range (P.proj a) →ₗ[R] LinearMap.range (P.proj b)

/-- Projection from the ambient module onto a certified packet range. -/
def packetProjection (P : LinearProjectorFamily R M ι) (a : ι) :
    M →ₗ[R] LinearMap.range (P.proj a) where
  toFun x := ⟨P.proj a x, ⟨x, rfl⟩⟩
  map_add' x y := by
    apply Subtype.ext
    exact (P.proj a).map_add x y
  map_smul' c x := by
    apply Subtype.ext
    exact (P.proj a).map_smul c x

/-- Inclusion of a packet range into the ambient module. -/
def packetInclusion (P : LinearProjectorFamily R M ι) (a : ι) :
    LinearMap.range (P.proj a) →ₗ[R] M :=
  Submodule.subtype _

@[simp] theorem packetProjection_apply_coe
    (P : LinearProjectorFamily R M ι) (a : ι)
    (x : LinearMap.range (P.proj a)) :
    packetProjection P a (x : M) = x := by
  apply Subtype.ext
  rcases x.property with ⟨y, hy⟩
  change P.proj a (x : M) = (x : M)
  rw [← hy]
  exact P.idempotent a y

theorem packetProjection_inclusion_ne
    (P : LinearProjectorFamily R M ι) {a b : ι} (h : a ≠ b)
    (x : LinearMap.range (P.proj b)) :
    packetProjection P a (packetInclusion P b x) = 0 := by
  apply Subtype.ext
  change P.proj a (x : M) = 0
  rcases x.property with ⟨y, hy⟩
  rw [← hy]
  exact P.orthogonal h y

/-- Restrict an ambient endomorphism to each input and output packet. -/
def restrictBlocks (P : LinearProjectorFamily R M ι)
    (T : Module.End R M) : PacketBlocks P :=
  fun b a => (packetProjection P b).comp (T.comp (packetInclusion P a))

/-- Synthesize an ambient endomorphism from an arbitrary family of blocks. -/
def synthesizeBlocks (P : LinearProjectorFamily R M ι)
    (B : PacketBlocks P) : Module.End R M :=
  ∑ b, ∑ a,
    (packetInclusion P b).comp ((B b a).comp (packetProjection P a))

/-- Packet projection of a synthesized operator selects its output row. -/
theorem packetProjection_synthesizeBlocks
    (P : LinearProjectorFamily R M ι) (B : PacketBlocks P)
    (b : ι) (x : M) :
    packetProjection P b (synthesizeBlocks P B x) =
      ∑ a, B b a (packetProjection P a x) := by
  classical
  apply Subtype.ext
  simp only [synthesizeBlocks, LinearMap.sum_apply, map_sum,
    Submodule.coe_sum]
  rw [Finset.sum_eq_single b]
  · apply Finset.sum_congr rfl
    intro a ha
    exact congrArg Subtype.val
      (packetProjection_apply_coe P b (B b a (packetProjection P a x)))
  · intro d _ hdb
    apply Finset.sum_eq_zero
    intro a ha
    exact congrArg Subtype.val
      (packetProjection_inclusion_ne P hdb.symm
        (B d a (packetProjection P a x)))
  · simp

/-- A synthesized arbitrary block family restricts back to itself. -/
theorem restrictBlocks_synthesizeBlocks
    (P : LinearProjectorFamily R M ι) (B : PacketBlocks P) :
    restrictBlocks P (synthesizeBlocks P B) = B := by
  funext b a
  ext x
  classical
  simp only [restrictBlocks, LinearMap.comp_apply]
  rw [packetProjection_synthesizeBlocks]
  rw [Finset.sum_eq_single a]
  · exact congrArg Subtype.val
      (congrArg (B b a) (packetProjection_apply_coe P a x))
  · intro c _ hca
    rw [packetProjection_inclusion_ne P hca]
    simp
  · simp

/-- Each synthesized restricted block is the corresponding ambient transfer block. -/
theorem synthesized_restricted_block
    (P : LinearProjectorFamily R M ι) (T : Module.End R M)
    (b a : ι) :
    (packetInclusion P b).comp
        (((restrictBlocks P T) b a).comp (packetProjection P a)) =
      transferBlock P P T b a := by
  ext x
  rfl

/-- Restricting all blocks and synthesizing reconstructs the operator exactly. -/
@[simp] theorem synthesizeBlocks_restrictBlocks
    (P : LinearProjectorFamily R M ι) (T : Module.End R M) :
    synthesizeBlocks P (restrictBlocks P T) = T := by
  classical
  simp only [synthesizeBlocks, synthesized_restricted_block]
  exact Foundation.transferBlock_reconstruction_end P T

/-- Restriction is injective because all packet blocks reconstruct the operator. -/
theorem restrictBlocks_injective
    (P : LinearProjectorFamily R M ι) :
    Function.Injective (restrictBlocks P) := by
  intro S T h
  calc
    S = synthesizeBlocks P (restrictBlocks P S) :=
      (synthesizeBlocks_restrictBlocks P S).symm
    _ = synthesizeBlocks P (restrictBlocks P T) := congrArg _ h
    _ = T := synthesizeBlocks_restrictBlocks P T

/-- Every arbitrary family of packet maps is realized by a unique operator. -/
theorem restrictBlocks_surjective
    (P : LinearProjectorFamily R M ι) :
    Function.Surjective (restrictBlocks P) := by
  intro B
  exact ⟨synthesizeBlocks P B, restrictBlocks_synthesizeBlocks P B⟩

/-- Restriction as a linear map. -/
def restrictBlocksLinear (P : LinearProjectorFamily R M ι) :
    Module.End R M →ₗ[R] PacketBlocks P where
  toFun := restrictBlocks P
  map_add' S T := by
    funext b a
    ext x
    simp [restrictBlocks, packetProjection, packetInclusion]
  map_smul' c T := by
    funext b a
    ext x
    simp [restrictBlocks, packetProjection, packetInclusion]

/-- The exact linear equivalence underlying the algebraic full-block representation. -/
noncomputable def fullBlockLinearEquiv
    (P : LinearProjectorFamily R M ι) :
    Module.End R M ≃ₗ[R] PacketBlocks P :=
  LinearEquiv.ofBijective (restrictBlocksLinear P)
    ⟨restrictBlocks_injective P, restrictBlocks_surjective P⟩

/--
A type synonym carrying the genuine dependent packet-block algebra structure.
The structure is transported from ambient endomorphisms across the proved
block equivalence, avoiding any homogeneous-matrix surrogate.
-/
def PacketBlockAlgebra (P : LinearProjectorFamily R M ι) := PacketBlocks P

/-- The inverse block equivalence, used to transport the algebra structure. -/
noncomputable def packetBlockEquivToEnd
    (P : LinearProjectorFamily R M ι) :
    PacketBlockAlgebra P ≃ Module.End R M :=
  (fullBlockLinearEquiv P).symm.toEquiv

noncomputable instance packetBlockAlgebraSemiring
    (P : LinearProjectorFamily R M ι) : Semiring (PacketBlockAlgebra P) :=
  Equiv.semiring (packetBlockEquivToEnd P)

noncomputable instance packetBlockAlgebraAlgebra
    (P : LinearProjectorFamily R M ι) : Algebra R (PacketBlockAlgebra P) :=
  Equiv.algebra R (packetBlockEquivToEnd P)

/-- The full dependent block representation as an algebra equivalence. -/
noncomputable def fullBlockAlgEquiv
    (P : LinearProjectorFamily R M ι) :
    Module.End R M ≃ₐ[R] PacketBlockAlgebra P :=
  (Equiv.algEquiv R (packetBlockEquivToEnd P)).symm

@[simp] theorem fullBlockAlgEquiv_apply
    (P : LinearProjectorFamily R M ι) (T : Module.End R M) :
    fullBlockAlgEquiv P T = restrictBlocks P T :=
  rfl

/-- Operator-valued matrix multiplication on arbitrary packet blocks. -/
def blockMul (P : LinearProjectorFamily R M ι)
    (B C : PacketBlocks P) : PacketBlocks P :=
  fun b a => ∑ c, (B b c).comp (C c a)

/-- Restriction carries composition to operator-valued matrix multiplication. -/
theorem restrictBlocks_comp
    (P : LinearProjectorFamily R M ι) (S T : Module.End R M) :
    restrictBlocks P (S.comp T) =
      blockMul P (restrictBlocks P S) (restrictBlocks P T) := by
  funext b a
  ext x
  classical
  rcases x.property with ⟨y, hy⟩
  have hx : P.proj a (x : M) = (x : M) := by
    rw [← hy]
    exact P.idempotent a y
  simpa [restrictBlocks, blockMul, packetProjection, packetInclusion, hx,
    LinearMap.sum_apply, Submodule.coe_sum] using
      Foundation.transferBlock_comp P P P T S b a (x : M)

/-- The transported algebra multiplication is exactly packet block multiplication. -/
theorem packetBlockAlgebra_mul_eq_blockMul
    (P : LinearProjectorFamily R M ι)
    (B C : PacketBlockAlgebra P) :
    B * C = blockMul P B C := by
  obtain ⟨S, rfl⟩ := (fullBlockAlgEquiv P).surjective B
  obtain ⟨T, rfl⟩ := (fullBlockAlgEquiv P).surjective C
  rw [← map_mul]
  change restrictBlocks P (S.comp T) =
    blockMul P (restrictBlocks P S) (restrictBlocks P T)
  exact restrictBlocks_comp P S T

/-- The block-space dimension is exactly the ambient endomorphism dimension. -/
theorem finrank_end_eq_finrank_blocks
    {K : Type u} {V : Type v} [Field K]
    [AddCommGroup V] [Module K V]
    [FiniteDimensional K V]
    (P : LinearProjectorFamily K V ι) :
    Module.finrank K (Module.End K V) =
      Module.finrank K (PacketBlocks P) :=
  (fullBlockLinearEquiv P).finrank_eq

/-- The dimension of the ambient module is the sum of its packet dimensions. -/
theorem finrank_eq_sum_packet_finrank
    {K : Type u} {V : Type v} [Field K]
    [AddCommGroup V] [Module K V]
    [FiniteDimensional K V]
    (P : LinearProjectorFamily K V ι) :
    Module.finrank K V =
      ∑ a, Module.finrank K (LinearMap.range (P.proj a)) := by
  rw [← Module.finrank_pi_fintype]
  exact (P.exactPacketCoordinates.finrank_eq)

/-- The full block space has the expected double-sum dimension. -/
theorem finrank_blocks_eq_sum_products
    {K : Type u} {V : Type v} [Field K]
    [AddCommGroup V] [Module K V]
    [FiniteDimensional K V]
    (P : LinearProjectorFamily K V ι) :
    Module.finrank K (PacketBlocks P) =
      ∑ b, ∑ a,
        Module.finrank K (LinearMap.range (P.proj a)) *
          Module.finrank K (LinearMap.range (P.proj b)) := by
  rw [Module.finrank_pi_fintype]
  apply Finset.sum_congr rfl
  intro b hb
  rw [Module.finrank_pi_fintype]
  apply Finset.sum_congr rfl
  intro a ha
  exact Module.finrank_linearMap K K _ _

/-- Paper I's complete dimension count, including both displayed equalities. -/
theorem end_finrank_eq_packet_sum_eq_square
    {K : Type u} {V : Type v} [Field K]
    [AddCommGroup V] [Module K V]
    [FiniteDimensional K V]
    (P : LinearProjectorFamily K V ι) :
    Module.finrank K (Module.End K V) =
        ∑ b, ∑ a,
          Module.finrank K (LinearMap.range (P.proj a)) *
            Module.finrank K (LinearMap.range (P.proj b)) ∧
      (∑ b, ∑ a,
          Module.finrank K (LinearMap.range (P.proj a)) *
            Module.finrank K (LinearMap.range (P.proj b))) =
        (∑ a, Module.finrank K (LinearMap.range (P.proj a))) ^ 2 := by
  constructor
  · exact (finrank_end_eq_finrank_blocks P).trans
      (finrank_blocks_eq_sum_products P)
  · rw [pow_two, Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro b hb
    rw [Finset.sum_mul]

/-! ### Arbitrary packet-Hom support patterns -/

/-- A heterogeneous block family is supported on an input-to-output relation. -/
def BlocksSupported (P : LinearProjectorFamily R M ι)
    (rel : ι → ι → Prop) (B : PacketBlocks P) : Prop :=
  ∀ b a, ¬ rel a b → B b a = 0

/-- Universal closure of arbitrary packet-Hom matrices under block multiplication. -/
def BlockMulClosed (P : LinearProjectorFamily R M ι)
    (rel : ι → ι → Prop) : Prop :=
  ∀ B C : PacketBlocks P,
    BlocksSupported P rel B → BlocksSupported P rel C →
      BlocksSupported P rel (blockMul P B C)

/-- A single heterogeneous packet block. -/
def singleBlock (P : LinearProjectorFamily R M ι)
    (b a : ι)
    (f : LinearMap.range (P.proj a) →ₗ[R] LinearMap.range (P.proj b)) :
    PacketBlocks P :=
  Pi.single b (Pi.single a f)

theorem singleBlock_supported
    (P : LinearProjectorFamily R M ι) (rel : ι → ι → Prop)
    {b a : ι} (hab : rel a b)
    (f : LinearMap.range (P.proj a) →ₗ[R] LinearMap.range (P.proj b)) :
    BlocksSupported P rel (singleBlock P b a f) := by
  intro d c hdc
  classical
  by_cases hd : d = b
  · subst d
    by_cases hc : c = a
    · subst c
      exact (hdc hab).elim
    · simp [singleBlock, hc]
  · simp [singleBlock, hd]

/-- Transitivity is sufficient for closure of every allowed packet-Hom family. -/
theorem blockMulClosed_of_transitive
    (P : LinearProjectorFamily R M ι) (rel : ι → ι → Prop)
    (htrans : ∀ a c b, rel a c → rel c b → rel a b) :
    BlockMulClosed P rel := by
  intro B C hB hC b a hab
  classical
  apply LinearMap.ext
  intro x
  simp only [blockMul, LinearMap.sum_apply]
  apply Finset.sum_eq_zero
  intro c hc
  by_cases hac : rel a c
  · have hcb : ¬ rel c b := fun h => hab (htrans a c b hac h)
    rw [hB b c hcb]
    simp
  · rw [hC c a hac]
    simp

/-- Nonzero packet spaces possess two maps with nonzero composite. -/
theorem exists_packet_maps_nonzero_comp
    {K : Type u} {V : Type v} [Field K]
    [AddCommGroup V] [Module K V]
    (P : LinearProjectorFamily K V ι)
    [hpacket : ∀ i, Nontrivial (LinearMap.range (P.proj i))]
    (a c b : ι) :
    ∃ f : LinearMap.range (P.proj a) →ₗ[K] LinearMap.range (P.proj c),
      ∃ g : LinearMap.range (P.proj c) →ₗ[K] LinearMap.range (P.proj b),
        g.comp f ≠ 0 := by
  obtain ⟨x, hx⟩ := exists_ne (0 : LinearMap.range (P.proj a))
  obtain ⟨y, hy⟩ := exists_ne (0 : LinearMap.range (P.proj c))
  obtain ⟨z, hz⟩ := exists_ne (0 : LinearMap.range (P.proj b))
  have hxbot : x ∉ (⊥ : Submodule K (LinearMap.range (P.proj a))) := by
    simpa using hx
  have hybot : y ∉ (⊥ : Submodule K (LinearMap.range (P.proj c))) := by
    simpa using hy
  obtain ⟨lx, hlx0, hlx⟩ :=
    LinearMap.exists_extend_of_notMem
      (K := K) (0 : (⊥ : Submodule K (LinearMap.range (P.proj a))) →ₗ[K] K)
      hxbot 1
  obtain ⟨ly, hly0, hly⟩ :=
    LinearMap.exists_extend_of_notMem
      (K := K) (0 : (⊥ : Submodule K (LinearMap.range (P.proj c))) →ₗ[K] K)
      hybot 1
  let f := LinearMap.smulRight lx y
  let g := LinearMap.smulRight ly z
  refine ⟨f, g, ?_⟩
  intro hzero
  have h := LinearMap.congr_fun hzero x
  simp [f, g, hlx, hly] at h
  exact hz h

/--
For arbitrary maps between nonzero packet spaces, multiplication closure is
equivalent to transitivity of the packet support relation.
-/
theorem blockMulClosed_iff_transitive
    {K : Type u} {V : Type v} [Field K]
    [AddCommGroup V] [Module K V]
    (P : LinearProjectorFamily K V ι)
    [∀ i, Nontrivial (LinearMap.range (P.proj i))]
    (rel : ι → ι → Prop) :
    BlockMulClosed P rel ↔
      ∀ a c b, rel a c → rel c b → rel a b := by
  constructor
  · intro hclosed a c b hac hcb
    by_contra hab
    obtain ⟨f, g, hgf⟩ := exists_packet_maps_nonzero_comp P a c b
    let C := singleBlock P c a f
    let B := singleBlock P b c g
    have hC : BlocksSupported P rel C :=
      singleBlock_supported P rel hac f
    have hB : BlocksSupported P rel B :=
      singleBlock_supported P rel hcb g
    have hzero := hclosed B C hB hC b a hab
    have hentry : blockMul P B C b a = g.comp f := by
      classical
      simp only [blockMul, B, C, singleBlock, Pi.single_eq_same]
      rw [Fintype.sum_eq_single c]
      · simp
      · intro d hdc
        simp [Pi.single_eq_of_ne hdc]
    exact hgf (hentry ▸ hzero)
  · exact blockMulClosed_of_transitive P rel

/-- The block identity is supported exactly when the relation is reflexive. -/
theorem identity_blocks_supported_iff_reflexive
    {K : Type u} {V : Type v} [Field K]
    [AddCommGroup V] [Module K V]
    (P : LinearProjectorFamily K V ι)
    [∀ i, Nontrivial (LinearMap.range (P.proj i))]
    (rel : ι → ι → Prop) :
    BlocksSupported P rel (restrictBlocks P 1) ↔ ∀ a, rel a a := by
  constructor
  · intro h a
    by_contra haa
    have hzero := h a a haa
    obtain ⟨x, hx⟩ := exists_ne (0 : LinearMap.range (P.proj a))
    have happ := LinearMap.congr_fun hzero x
    have : x = 0 := by
      calc
        x = packetProjection P a (packetInclusion P a x) :=
          (packetProjection_apply_coe P a x).symm
        _ = 0 := by simpa [restrictBlocks] using happ
    exact hx this
  · intro hrefl b a hab
    have hba : b ≠ a := by
      intro h
      subst b
      exact hab (hrefl a)
    ext x
    exact congrArg Subtype.val (packetProjection_inclusion_ne P hba x)

end FullBlocks

namespace Reachability

open Foundation

universe u v w

variable {R : Type u} {M : Type v} {ι : Type w}
variable [Semiring R] [AddCommMonoid M] [Module R M]
variable [Fintype ι]

/-- A vector has no packet component outside `S`. -/
def VectorSupported (P : LinearProjectorFamily R M ι)
    (S : Set ι) (x : M) : Prop :=
  ∀ b, b ∉ S → P.proj b x = 0

/-- The vectors supported on `S` form a submodule. -/
def supportedSubmodule (P : LinearProjectorFamily R M ι)
    (S : Set ι) : Submodule R M where
  carrier := {x | VectorSupported P S x}
  zero_mem' := by
    intro b hb
    simp
  add_mem' := by
    intro x y hx hy b hb
    simp [hx b hb, hy b hb]
  smul_mem' := by
    intro c x hx b hb
    simp [hx b hb]

/-- The transfer edge relation generated by a declared operator family. -/
def TransferEdge (P : LinearProjectorFamily R M ι)
    (ops : Set (Module.End R M)) (a b : ι) : Prop :=
  ∃ T ∈ ops, transferBlock P P T b a ≠ 0

/-- Packet `b` is reachable from at least one declared source packet. -/
def ReachableFrom (P : LinearProjectorFamily R M ι)
    (ops : Set (Module.End R M)) (S₀ : Set ι) (b : ι) : Prop :=
  ∃ a ∈ S₀, Relation.ReflTransGen (TransferEdge P ops) a b

theorem reachable_forward
    (P : LinearProjectorFamily R M ι) (ops : Set (Module.End R M))
    (S₀ : Set ι) {a b : ι}
    (ha : ReachableFrom P ops S₀ a) (hab : TransferEdge P ops a b) :
    ReachableFrom P ops S₀ b := by
  rcases ha with ⟨s, hs, hsa⟩
  exact ⟨s, hs, hsa.tail hab⟩

/-- Every source packet is reachable by a path of length zero. -/
theorem source_reachable
    (P : LinearProjectorFamily R M ι) (ops : Set (Module.End R M))
    (S₀ : Set ι) {a : ι} (ha : a ∈ S₀) :
    ReachableFrom P ops S₀ a :=
  ⟨a, ha, Relation.ReflTransGen.refl⟩

/-- Every declared operator preserves support on the reachable packet set. -/
theorem operator_preserves_reachable_support
    (P : LinearProjectorFamily R M ι) (ops : Set (Module.End R M))
    (S₀ : Set ι) {T : Module.End R M} (hT : T ∈ ops)
    {x : M} (hx : VectorSupported P (ReachableFrom P ops S₀) x) :
    VectorSupported P (ReachableFrom P ops S₀) (T x) := by
  intro b hb
  classical
  calc
    P.proj b (T x) = P.proj b (T (∑ a, P.proj a x)) := by
      rw [P.complete]
    _ = ∑ a, P.proj b (T (P.proj a x)) := by simp
    _ = 0 := by
      apply Finset.sum_eq_zero
      intro a ha
      by_cases hra : ReachableFrom P ops S₀ a
      · have hblock : transferBlock P P T b a = 0 := by
          by_contra hne
          exact hb (reachable_forward P ops S₀ hra ⟨T, hT, hne⟩)
        exact LinearMap.congr_fun hblock x
      · rw [hx a hra]
        simp

/-- A typed word in the declared operator family. -/
abbrev OperatorWord (ops : Set (Module.End R M)) :=
  List {T : Module.End R M // T ∈ ops}

/-- Apply an operator word from left to right. -/
def wordApply {ops : Set (Module.End R M)} : OperatorWord ops → M → M
  | [], x => x
  | T :: word, x => wordApply word (T.1 x)

theorem wordApply_preserves_reachable_support
    (P : LinearProjectorFamily R M ι) (ops : Set (Module.End R M))
    (S₀ : Set ι) (word : OperatorWord ops) {x : M}
    (hx : VectorSupported P (ReachableFrom P ops S₀) x) :
    VectorSupported P (ReachableFrom P ops S₀) (wordApply word x) := by
  induction word generalizing x with
  | nil => exact hx
  | cons T word ih =>
      exact ih (operator_preserves_reachable_support P ops S₀ T.property hx)

/-- The orbit set of seeds under all finite declared operator words. -/
def OrbitSet (ops : Set (Module.End R M)) (seeds : Set M) : Set M :=
  {y | ∃ s ∈ seeds, ∃ word : OperatorWord ops, y = wordApply word s}

/-- The algebraic generated hull of a seed family under declared operators. -/
def algebraicOrbitHull (ops : Set (Module.End R M))
    (seeds : Set M) : Submodule R M :=
  Submodule.span R (OrbitSet ops seeds)

/--
The complete algebraic reachability theorem: the generated hull is contained
in the direct sum of packets reachable from the seed support.
-/
theorem algebraicOrbitHull_le_reachable_support
    (P : LinearProjectorFamily R M ι) (ops : Set (Module.End R M))
    (S₀ : Set ι) (seeds : Set M)
    (hseeds : ∀ s ∈ seeds, VectorSupported P S₀ s) :
    algebraicOrbitHull ops seeds ≤
      supportedSubmodule P (ReachableFrom P ops S₀) := by
  rw [algebraicOrbitHull, Submodule.span_le]
  rintro y ⟨s, hs, word, rfl⟩
  apply wordApply_preserves_reachable_support P ops S₀ word
  intro b hb
  exact hseeds s hs b (fun hbS => hb (source_reachable P ops S₀ hbS))

/-- A nonzero unreachable packet prevents algebraic generation of the ambient module. -/
theorem unreachable_nonzero_packet_obstruction
    (P : LinearProjectorFamily R M ι) (ops : Set (Module.End R M))
    (S₀ : Set ι) (seeds : Set M)
    (hseeds : ∀ s ∈ seeds, VectorSupported P S₀ s)
    (b : ι) (hb : ¬ ReachableFrom P ops S₀ b)
    [Nontrivial (LinearMap.range (P.proj b))] :
    algebraicOrbitHull ops seeds ≠ ⊤ := by
  intro htop
  obtain ⟨z, hz⟩ := exists_ne (0 : LinearMap.range (P.proj b))
  have hzmem : (z : M) ∈ algebraicOrbitHull ops seeds := by
    rw [htop]
    trivial
  have hsupp := algebraicOrbitHull_le_reachable_support P ops S₀ seeds hseeds hzmem
  have hzero : P.proj b (z : M) = 0 := hsupp b hb
  rcases z.property with ⟨x, hx⟩
  have hfixed : P.proj b (z : M) = (z : M) := by
    rw [← hx]
    exact P.idempotent b x
  exact hz (Subtype.ext (hfixed.symm.trans hzero))

/-! ### Coordinate invariance of the transfer graph -/

variable {N : Type*} [AddCommMonoid N] [Module R N]

theorem conjugateEnd_eq_zero_iff (U : M ≃ₗ[R] N) (T : Module.End R M) :
    Foundation.conjugateEnd U T = 0 ↔ T = 0 := by
  constructor
  · intro h
    ext x
    have hx := LinearMap.congr_fun h (U x)
    apply U.injective
    simpa [Foundation.conjugateEnd] using hx
  · rintro rfl
    ext y
    simp [Foundation.conjugateEnd]

theorem conjugate_transferBlock_ne_zero_iff
    (P : LinearProjectorFamily R M ι) (U : M ≃ₗ[R] N)
    (T : Module.End R M) (b a : ι) :
    transferBlock (P.conjugate U) (P.conjugate U)
        (Foundation.conjugateEnd U T) b a ≠ 0 ↔
      transferBlock P P T b a ≠ 0 := by
  rw [Foundation.conjugate_transferBlock]
  exact not_congr (conjugateEnd_eq_zero_iff U _)

/-- The complete transfer-edge relation is unchanged by coordinate conjugation. -/
theorem conjugate_transferEdge_iff
    (P : LinearProjectorFamily R M ι) (U : M ≃ₗ[R] N)
    (ops : Set (Module.End R M)) (a b : ι) :
    TransferEdge (P.conjugate U)
        (Foundation.conjugateEnd U '' ops) a b ↔
      TransferEdge P ops a b := by
  constructor
  · rintro ⟨T', ⟨T, hT, rfl⟩, hblock⟩
    exact ⟨T, hT, (conjugate_transferBlock_ne_zero_iff P U T b a).mp hblock⟩
  · rintro ⟨T, hT, hblock⟩
    exact ⟨Foundation.conjugateEnd U T, ⟨T, hT, rfl⟩,
      (conjugate_transferBlock_ne_zero_iff P U T b a).mpr hblock⟩

/-- Coordinate transport preserves all finite packet reachability statements. -/
theorem conjugate_reachableFrom_iff
    (P : LinearProjectorFamily R M ι) (U : M ≃ₗ[R] N)
    (ops : Set (Module.End R M)) (S₀ : Set ι) (b : ι) :
    ReachableFrom (P.conjugate U) (Foundation.conjugateEnd U '' ops) S₀ b ↔
      ReachableFrom P ops S₀ b := by
  have hedge : TransferEdge (P.conjugate U)
      (Foundation.conjugateEnd U '' ops) = TransferEdge P ops := by
    funext a c
    exact propext (conjugate_transferEdge_iff P U ops a c)
  simp only [ReachableFrom, hedge]

end Reachability

namespace StrictNaturality

open Foundation

universe u v w x y

variable {K : Type u} {M : Type v} {N : Type w}
variable {ι : Type x} {κ : Type y}
variable [Field K]
variable [AddCommGroup M] [Module K M]
variable [AddCommGroup N] [Module K N]
variable [Fintype ι] [Fintype κ]

/--
A fully typed strict morphism of finite packet seed systems.  The acting
algebras are concrete subalgebras of endomorphisms, so the intertwining law is
well-typed without applying an abstract algebra map to an unrelated operator.
-/
structure StrictSeedMorphism
    (A : Subalgebra K (Module.End K M))
    (B : Subalgebra K (Module.End K N))
    (P : LinearProjectorFamily K M ι)
    (Q : LinearProjectorFamily K N κ) where
  linearMap : M →ₗ[K] N
  algebraMap : A →ₐ[K] B
  packetMap : ι → κ
  packetMap_injective : Function.Injective packetMap
  operator_natural : ∀ T : A,
    linearMap.comp T.1 = (algebraMap T).1.comp linearMap
  packet_natural : ∀ a : ι,
    linearMap.comp (P.proj a) = (Q.proj (packetMap a)).comp linearMap

variable {A : Subalgebra K (Module.End K M)}
variable {B : Subalgebra K (Module.End K N)}
variable {P : LinearProjectorFamily K M ι}
variable {Q : LinearProjectorFamily K N κ}

/-- The ordinary algebraic orbit of a seed set under a concrete algebra. -/
def AlgebraOrbitSet (A : Subalgebra K (Module.End K M))
    (S : Set M) : Set M :=
  {x | ∃ T : A, ∃ s ∈ S, x = T.1 s}

/-- Algebraic generated hull, expressed as the scalar span of the algebra orbit. -/
def AlgebraGeneratedHull (A : Subalgebra K (Module.End K M))
    (S : Set M) : Submodule K M :=
  Submodule.span K (AlgebraOrbitSet A S)

/-- Orbit in the target under exactly the image of the source algebra. -/
def MappedOrbitSet
    (F : StrictSeedMorphism A B P Q) (S : Set M) : Set N :=
  {y | ∃ T : A, ∃ s ∈ S,
    y = (F.algebraMap T).1 (F.linearMap s)}

/-- Target hull under exactly the image algebra, rather than all of `B`. -/
def MappedGeneratedHull
    (F : StrictSeedMorphism A B P Q) (S : Set M) : Submodule K N :=
  Submodule.span K (MappedOrbitSet F S)

/-! ### Seed-rank functoriality -/

/-- Intertwining converts the source-algebra scalar action into the target action. -/
theorem linearMap_smul_of_intertwining
    (Φ : M →ₗ[K] N) (φ : A →ₐ[K] B)
    (hnat : ∀ T : A, Φ.comp T.1 = (φ T).1.comp Φ)
    (T : A) (x : M) :
    Φ (T • x) = φ T • Φ x := by
  exact LinearMap.congr_fun (hnat T) x

/-- The image of an `A`-span lies in the `B`-span of the image seeds. -/
theorem map_mem_span_image_of_intertwining
    (Φ : M →ₗ[K] N) (φ : A →ₐ[K] B)
    (hnat : ∀ T : A, Φ.comp T.1 = (φ T).1.comp Φ)
    (S : Set M) {x : M} (hx : x ∈ Submodule.span A S) :
    Φ x ∈ Submodule.span B (Φ '' S) := by
  induction hx using Submodule.span_induction with
  | mem x hx =>
      exact Submodule.subset_span ⟨x, hx, rfl⟩
  | zero => simp
  | add x y hx hy ihx ihy =>
      simpa using (Submodule.add_mem _ ihx ihy)
  | smul T x hx ih =>
      rw [linearMap_smul_of_intertwining Φ φ hnat]
      exact Submodule.smul_mem _ (φ T) ih

/-- A surjective intertwiner sends generators to generators. -/
theorem image_generates_of_surjective_intertwining
    (Φ : M →ₗ[K] N) (φ : A →ₐ[K] B)
    (hnat : ∀ T : A, Φ.comp T.1 = (φ T).1.comp Φ)
    (hΦ : Function.Surjective Φ) (S : Set M)
    (hS : SeedRankBasics.Generates A M S) :
    SeedRankBasics.Generates B N (Φ '' S) := by
  rw [SeedRankBasics.Generates]
  apply top_unique
  intro y hy
  obtain ⟨x, rfl⟩ := hΦ y
  apply map_mem_span_image_of_intertwining Φ φ hnat S
  rw [hS]
  trivial

/-- Seed rank cannot increase through a surjective algebra intertwiner. -/
theorem seedRank_le_of_surjective_intertwining
    (Φ : M →ₗ[K] N) (φ : A →ₐ[K] B)
    (hnat : ∀ T : A, Φ.comp T.1 = (φ T).1.comp Φ)
    (hΦ : Function.Surjective Φ) :
    Cardinal.lift.{v} (SeedRankBasics.seedRank B N) ≤
      Cardinal.lift.{w} (SeedRankBasics.seedRank A M) := by
  obtain ⟨S, hS, hcard⟩ :=
    SeedRankBasics.exists_generating_set_card_eq_seedRank A M
  have himage : SeedRankBasics.Generates B N (Φ '' S) :=
    image_generates_of_surjective_intertwining Φ φ hnat hΦ S hS
  have hrank := SeedRankBasics.seedRank_le_mk_of_generates B N himage
  calc
    Cardinal.lift.{v} (SeedRankBasics.seedRank B N) ≤
        Cardinal.lift.{v} (Cardinal.mk (Φ '' S)) := Cardinal.lift_le.2 hrank
    _ ≤ Cardinal.lift.{w} (Cardinal.mk S) := Cardinal.mk_image_le_lift
    _ = Cardinal.lift.{w} (SeedRankBasics.seedRank A M) :=
      congrArg Cardinal.lift hcard

/-- Paper I's seed-rank inequality for a surjective strict morphism. -/
theorem strict_seedRank_le
    (F : StrictSeedMorphism A B P Q)
    (hΦ : Function.Surjective F.linearMap) :
    Cardinal.lift.{v} (SeedRankBasics.seedRank B N) ≤
      Cardinal.lift.{w} (SeedRankBasics.seedRank A M) :=
  seedRank_le_of_surjective_intertwining F.linearMap F.algebraMap
    F.operator_natural hΦ

/--
If the realization map is bijective and the acting-algebra map is an
isomorphism, seed rank is preserved exactly.
-/
theorem strict_seedRank_eq_of_bijective
    (F : StrictSeedMorphism A B P Q)
    (hΦ : Function.Bijective F.linearMap)
    (hφ : Function.Bijective F.algebraMap) :
    Cardinal.lift.{w} (SeedRankBasics.seedRank A M) =
      Cardinal.lift.{v} (SeedRankBasics.seedRank B N) := by
  let Φe : M ≃ₗ[K] N := LinearEquiv.ofBijective F.linearMap hΦ
  let φe : A ≃ₐ[K] B := AlgEquiv.ofBijective F.algebraMap hφ
  have hreverse : ∀ T : B,
      Φe.symm.toLinearMap.comp T.1 =
        (φe.symm T).1.comp Φe.symm.toLinearMap := by
    intro T
    ext y
    change Φe.symm (T.1 y) = (φe.symm T).1 (Φe.symm y)
    apply Φe.injective
    rw [Φe.apply_symm_apply]
    symm
    have hφinv : F.algebraMap (φe.symm T) = T := by
      change φe (φe.symm T) = T
      exact φe.apply_symm_apply T
    calc
      Φe ((φe.symm T).1 (Φe.symm y)) =
          (F.algebraMap (φe.symm T)).1 (Φe (Φe.symm y)) := by
        exact LinearMap.congr_fun (F.operator_natural (φe.symm T)) (Φe.symm y)
      _ = T.1 y := by rw [hφinv, Φe.apply_symm_apply]
  apply le_antisymm
  · exact seedRank_le_of_surjective_intertwining
      Φe.symm.toLinearMap φe.symm.toAlgHom hreverse Φe.symm.surjective
  · exact strict_seedRank_le F hΦ.2

theorem map_algebraOrbitSet
    (F : StrictSeedMorphism A B P Q) (S : Set M) :
    F.linearMap '' AlgebraOrbitSet A S = MappedOrbitSet F S := by
  ext y
  constructor
  · rintro ⟨x, ⟨T, s, hs, rfl⟩, rfl⟩
    refine ⟨T, s, hs, ?_⟩
    have h := LinearMap.congr_fun (F.operator_natural T) s
    simpa using h
  · rintro ⟨T, s, hs, rfl⟩
    refine ⟨T.1 s, ⟨T, s, hs, rfl⟩, ?_⟩
    have h := LinearMap.congr_fun (F.operator_natural T) s
    simpa using h

/-- Exact naturality of the algebraically generated hull. -/
theorem generatedHull_natural
    (F : StrictSeedMorphism A B P Q) (S : Set M) :
    Submodule.map F.linearMap (AlgebraGeneratedHull A S) =
      MappedGeneratedHull F S := by
  rw [AlgebraGeneratedHull, MappedGeneratedHull, Submodule.map_span]
  exact congrArg (Submodule.span K) (map_algebraOrbitSet F S)

/-- A generating source family maps to a generator for the image algebra when `Φ` is onto. -/
theorem mappedGeneratedHull_eq_top
    (F : StrictSeedMorphism A B P Q) (S : Set M)
    (hS : AlgebraGeneratedHull A S = ⊤)
    (hΦ : Function.Surjective F.linearMap) :
    MappedGeneratedHull F S = ⊤ := by
  rw [← generatedHull_natural F S, hS, Submodule.map_top,
    LinearMap.range_eq_top.mpr hΦ]

/-- Packet analysis commutes with every strict morphism. -/
theorem packet_natural_apply
    (F : StrictSeedMorphism A B P Q) (a : ι) (x : M) :
    F.linearMap (P.proj a x) =
      Q.proj (F.packetMap a) (F.linearMap x) := by
  exact LinearMap.congr_fun (F.packet_natural a) x

/-- Type-correct block naturality for any separately intertwined operators. -/
theorem transferBlock_natural_general
    (F : StrictSeedMorphism A B P Q)
    (T : Module.End K M) (T' : Module.End K N)
    (hT : F.linearMap.comp T = T'.comp F.linearMap)
    (b a : ι) :
    F.linearMap.comp (transferBlock P P T b a) =
      (transferBlock Q Q T' (F.packetMap b) (F.packetMap a)).comp
        F.linearMap := by
  ext x
  have hb (z : M) :
      F.linearMap (P.proj b z) = Q.proj (F.packetMap b) (F.linearMap z) :=
    packet_natural_apply F b z
  have ha :
      F.linearMap (P.proj a x) = Q.proj (F.packetMap a) (F.linearMap x) :=
    packet_natural_apply F a x
  have hTx (z : M) : F.linearMap (T z) = T' (F.linearMap z) := by
    exact LinearMap.congr_fun hT z
  change F.linearMap (P.proj b (T (P.proj a x))) =
    Q.proj (F.packetMap b)
      (T' (Q.proj (F.packetMap a) (F.linearMap x)))
  rw [hb, hTx, ha]

/-- Block naturality for an operator belonging to the source acting algebra. -/
theorem transferBlock_natural_algebra
    (F : StrictSeedMorphism A B P Q) (T : A) (b a : ι) :
    F.linearMap.comp (transferBlock P P T.1 b a) =
      (transferBlock Q Q (F.algebraMap T).1
        (F.packetMap b) (F.packetMap a)).comp F.linearMap :=
  transferBlock_natural_general F T.1 (F.algebraMap T).1
    (F.operator_natural T) b a

/-- Under a bijective realization map, corresponding blocks vanish simultaneously. -/
theorem transferBlock_eq_zero_iff_of_bijective
    (F : StrictSeedMorphism A B P Q)
    (hbij : Function.Bijective F.linearMap)
    (T : A) (b a : ι) :
    transferBlock P P T.1 b a = 0 ↔
      transferBlock Q Q (F.algebraMap T).1
        (F.packetMap b) (F.packetMap a) = 0 := by
  let S := transferBlock P P T.1 b a
  let S' := transferBlock Q Q (F.algebraMap T).1
    (F.packetMap b) (F.packetMap a)
  have hnat : F.linearMap.comp S = S'.comp F.linearMap :=
    transferBlock_natural_algebra F T b a
  constructor
  · intro hS
    apply LinearMap.ext
    intro y
    obtain ⟨x, rfl⟩ := hbij.2 y
    have h := LinearMap.congr_fun hnat x
    simpa [S, S', hS] using h.symm
  · intro hS'
    apply LinearMap.ext
    intro x
    apply hbij.1
    have h := LinearMap.congr_fun hnat x
    simpa [S, S', hS'] using h

/-- An input-output packet pair is an edge for at least one algebra operator. -/
def AlgebraTransferEdge
    (A : Subalgebra K (Module.End K M))
    (P : LinearProjectorFamily K M ι) (a b : ι) : Prop :=
  ∃ T : A, transferBlock P P T.1 b a ≠ 0

/-- Every algebra operator has a zero block at the given input-output pair. -/
def AlgebraZeroAt
    (A : Subalgebra K (Module.End K M))
    (P : LinearProjectorFamily K M ι) (a b : ι) : Prop :=
  ∀ T : A, transferBlock P P T.1 b a = 0

/-- The complete edge pattern of the acting algebra. -/
def AlgebraTransferPattern
    (A : Subalgebra K (Module.End K M))
    (P : LinearProjectorFamily K M ι) : Set (ι × ι) :=
  {ab | AlgebraTransferEdge A P ab.1 ab.2}

/-- The complete universal-zero pattern of the acting algebra. -/
def AlgebraZeroPattern
    (A : Subalgebra K (Module.End K M))
    (P : LinearProjectorFamily K M ι) : Set (ι × ι) :=
  {ab | AlgebraZeroAt A P ab.1 ab.2}

theorem algebraTransferEdge_iff_of_bijective
    (F : StrictSeedMorphism A B P Q)
    (hΦ : Function.Bijective F.linearMap)
    (hφ : Function.Surjective F.algebraMap)
    (a b : ι) :
    AlgebraTransferEdge A P a b ↔
      AlgebraTransferEdge B Q (F.packetMap a) (F.packetMap b) := by
  constructor
  · rintro ⟨T, hT⟩
    refine ⟨F.algebraMap T, ?_⟩
    exact (not_congr (transferBlock_eq_zero_iff_of_bijective F hΦ T b a)).mp hT
  · rintro ⟨T', hT'⟩
    obtain ⟨T, rfl⟩ := hφ T'
    refine ⟨T, ?_⟩
    exact (not_congr (transferBlock_eq_zero_iff_of_bijective F hΦ T b a)).mpr hT'

theorem algebraZeroAt_iff_of_bijective
    (F : StrictSeedMorphism A B P Q)
    (hΦ : Function.Bijective F.linearMap)
    (hφ : Function.Surjective F.algebraMap)
    (a b : ι) :
    AlgebraZeroAt A P a b ↔
      AlgebraZeroAt B Q (F.packetMap a) (F.packetMap b) := by
  constructor
  · intro hsource T'
    obtain ⟨T, rfl⟩ := hφ T'
    exact (transferBlock_eq_zero_iff_of_bijective F hΦ T b a).mp (hsource T)
  · intro htarget T
    exact (transferBlock_eq_zero_iff_of_bijective F hΦ T b a).mpr
      (htarget (F.algebraMap T))

/--
A bijective strict morphism identifies the entire transfer-edge pattern and
the entire universal-zero pattern.  Bijectivity of `packetMap` makes the pair
map a bijection, while surjectivity of the algebra map ensures that no target
operator is omitted.
-/
theorem full_transfer_edge_zero_pattern_correspondence
    (F : StrictSeedMorphism A B P Q)
    (hΦ : Function.Bijective F.linearMap)
    (hφ : Function.Bijective F.algebraMap)
    (hpacket : Function.Bijective F.packetMap) :
    Function.Bijective (Prod.map F.packetMap F.packetMap) ∧
      (Prod.map F.packetMap F.packetMap) ⁻¹'
          AlgebraTransferPattern B Q = AlgebraTransferPattern A P ∧
      (Prod.map F.packetMap F.packetMap) ⁻¹'
          AlgebraZeroPattern B Q = AlgebraZeroPattern A P := by
  refine ⟨hpacket.prodMap hpacket, ?_, ?_⟩
  · ext ab
    change AlgebraTransferEdge B Q (F.packetMap ab.1) (F.packetMap ab.2) ↔
      AlgebraTransferEdge A P ab.1 ab.2
    exact (algebraTransferEdge_iff_of_bijective F hΦ hφ.2 ab.1 ab.2).symm
  · ext ab
    change AlgebraZeroAt B Q (F.packetMap ab.1) (F.packetMap ab.2) ↔
      AlgebraZeroAt A P ab.1 ab.2
    exact (algebraZeroAt_iff_of_bijective F hΦ hφ.2 ab.1 ab.2).symm

/-- A compact theorem bundling generation, packets, blocks, and label injectivity. -/
theorem strict_naturality_package
    (F : StrictSeedMorphism A B P Q) (S : Set M) :
    Submodule.map F.linearMap (AlgebraGeneratedHull A S) =
        MappedGeneratedHull F S ∧
      (∀ a x, F.linearMap (P.proj a x) =
        Q.proj (F.packetMap a) (F.linearMap x)) ∧
      (∀ (T : A) b a,
        F.linearMap.comp (transferBlock P P T.1 b a) =
          (transferBlock Q Q (F.algebraMap T).1
            (F.packetMap b) (F.packetMap a)).comp F.linearMap) ∧
      Function.Injective F.packetMap := by
  exact ⟨generatedHull_natural F S, packet_natural_apply F,
    transferBlock_natural_algebra F, F.packetMap_injective⟩

end StrictNaturality

namespace TypedQuiver

open Reachability

universe u

variable {K : Type u} [Field K]

/-- The two-dimensional source vertex in the displayed quiver. -/
abbrev U (K : Type u) := Fin 2 → K

/-- The three-dimensional target vertex in the displayed quiver. -/
abbrev V (K : Type u) := Fin 3 → K

/-- The total vertex-graded representation space. -/
abbrev X (K : Type u) := U K × V K

def eU₁ : U K := ![1, 0]
def eU₂ : U K := ![0, 1]
def eV₁ : V K := ![1, 0, 0]
def eV₂ : V K := ![0, 1, 0]
def eV₃ : V K := ![0, 0, 1]

/-- The rotation `R(u₁,u₂)=(-u₂,u₁)`. -/
def rotation : U K →ₗ[K] U K where
  toFun u := ![-u 1, u 0]
  map_add' u v := by
    funext i
    fin_cases i <;> simp <;> ring
  map_smul' c u := by
    funext i
    fin_cases i <;> simp

/-- The arrow `A(u₁,u₂)=(u₁,u₂,0)`. -/
def arrowA : U K →ₗ[K] V K where
  toFun u := ![u 0, u 1, 0]
  map_add' u v := by
    funext i
    fin_cases i <;> simp
  map_smul' c u := by
    funext i
    fin_cases i <;> simp

/-- The arrow `B(v₁,v₂,v₃)=(v₁,v₂)`. -/
def arrowB : V K →ₗ[K] U K where
  toFun v := ![v 0, v 1]
  map_add' v w := by
    funext i
    fin_cases i <;> simp
  map_smul' c v := by
    funext i
    fin_cases i <;> simp

/-- The bound-quiver relation `BA=e_U` holds exactly. -/
theorem arrowB_comp_arrowA :
    (arrowB (K := K)).comp (arrowA (K := K)) = LinearMap.id := by
  ext u i
  fin_cases i <;> rfl

@[simp] theorem rotation_eU₁ : rotation (K := K) eU₁ = eU₂ := by
  funext i
  fin_cases i <;> simp [rotation, eU₁, eU₂]

@[simp] theorem arrowA_eU₁ : arrowA (K := K) eU₁ = eV₁ := by
  funext i
  fin_cases i <;> simp [arrowA, eU₁, eV₁]

@[simp] theorem arrowA_eU₂ : arrowA (K := K) eU₂ = eV₂ := by
  funext i
  fin_cases i <;> simp [arrowA, eU₂, eV₂]

@[simp] theorem arrowB_eV₃ : arrowB (K := K) eV₃ = 0 := by
  funext i
  fin_cases i <;> simp [arrowB, eV₃]

theorem eV₃_ne_zero : eV₃ (K := K) ≠ 0 := by
  intro h
  have := congrFun h 2
  simpa [eV₃] using this

/-- The missing third direction is a nonzero vector in `ker B`. -/
theorem eV₃_mem_ker_arrowB :
    eV₃ (K := K) ∈ LinearMap.ker (arrowB (K := K)) := by
  simp

/-- Every vector in `im A` has zero third coordinate. -/
theorem range_arrowA_third_zero
    {v : V K} (hv : v ∈ LinearMap.range (arrowA (K := K))) :
    v 2 = 0 := by
  rcases hv with ⟨u, rfl⟩
  rfl

/-- The kernel direction is not reachable through the arrow `A`. -/
theorem eV₃_not_mem_range_arrowA :
    eV₃ (K := K) ∉ LinearMap.range (arrowA (K := K)) := by
  intro h
  have := range_arrowA_third_zero h
  simpa [eV₃] using this

/-- `R` acting on the source vertex and zero on the target vertex. -/
def totalR : Module.End K (X K) where
  toFun x := (rotation x.1, 0)
  map_add' x y := by
    ext <;> simp
  map_smul' c x := by
    ext <;> simp

/-- The typed arrow `A`, extended by zero away from its source vertex. -/
def totalA : Module.End K (X K) where
  toFun x := (0, arrowA x.1)
  map_add' x y := by
    ext <;> simp
  map_smul' c x := by
    ext <;> simp

/-- The typed arrow `B`, extended by zero away from its source vertex. -/
def totalB : Module.End K (X K) where
  toFun x := (arrowB x.2, 0)
  map_add' x y := by
    ext <;> simp
  map_smul' c x := by
    ext <;> simp

/-- The three primitive operators of the finite typed quiver. -/
def quiverOps : Set (Module.End K (X K)) :=
  {totalR, totalA, totalB}

/-- The invariant proper subrepresentation reachable from the `U` vertex. -/
def uReachableSubmodule : Submodule K (X K) where
  carrier := {x | x.2 2 = 0}
  zero_mem' := by simp
  add_mem' := by
    intro x y hx hy
    change x.2 2 + y.2 2 = 0
    change x.2 2 = 0 at hx
    change y.2 2 = 0 at hy
    rw [hx, hy, add_zero]
  smul_mem' := by
    intro c x hx
    change c * x.2 2 = 0
    change x.2 2 = 0 at hx
    rw [hx, mul_zero]

theorem quiverOp_preserves_uReachable
    {T : Module.End K (X K)} (hT : T ∈ quiverOps)
    {x : X K} (hx : x ∈ uReachableSubmodule) :
    T x ∈ uReachableSubmodule := by
  simp only [quiverOps, Set.mem_insert_iff, Set.mem_singleton_iff] at hT
  rcases hT with rfl | rfl | rfl
  · simp [uReachableSubmodule, totalR]
  · simp [uReachableSubmodule, totalA, arrowA]
  · simp [uReachableSubmodule, totalB]

theorem quiverWord_preserves_uReachable
    (word : OperatorWord (quiverOps (K := K)))
    {x : X K} (hx : x ∈ uReachableSubmodule) :
    wordApply word x ∈ uReachableSubmodule := by
  induction word generalizing x with
  | nil => exact hx
  | cons T word ih =>
      exact ih (quiverOp_preserves_uReachable T.property hx)

/-- Every seed family supported at `U` generates only the proper `U ⊕ im A` plane. -/
theorem u_supported_hull_le_uReachable
    (seeds : Set (X K)) (hseeds : ∀ s ∈ seeds, s.2 = 0) :
    algebraicOrbitHull (quiverOps (K := K)) seeds ≤ uReachableSubmodule := by
  rw [algebraicOrbitHull, Submodule.span_le]
  rintro y ⟨s, hs, word, rfl⟩
  apply quiverWord_preserves_uReachable word
  simpa [uReachableSubmodule, hseeds s hs]

/-- No family supported solely at `U` generates the full quiver representation. -/
theorem no_u_supported_seeds_generate
    (seeds : Set (X K)) (hseeds : ∀ s ∈ seeds, s.2 = 0) :
    algebraicOrbitHull (quiverOps (K := K)) seeds ≠ ⊤ := by
  intro htop
  let missing : X K := (0, eV₃)
  have hmem : missing ∈ algebraicOrbitHull (quiverOps (K := K)) seeds := by
    rw [htop]
    trivial
  have hplane := u_supported_hull_le_uReachable seeds hseeds hmem
  have : (1 : K) = 0 := by
    simpa [missing, uReachableSubmodule, eV₃] using hplane
  exact one_ne_zero this

/-- The two displayed seeds `e₁ ∈ U` and `e₃ ∈ V`. -/
def sourceSeed : X K := (eU₁, 0)
def missingSeed : X K := (0, eV₃)
def certificateSeeds : Set (X K) := {sourceSeed, missingSeed}

theorem orbit_mem_hull
    {seeds : Set (X K)} {s : X K} (hs : s ∈ seeds)
    (word : OperatorWord (quiverOps (K := K))) :
    wordApply word s ∈ algebraicOrbitHull (quiverOps (K := K)) seeds := by
  exact Submodule.subset_span ⟨s, hs, word, rfl⟩

/-- The two certified seeds generate all five coordinate directions. -/
theorem certificateSeeds_generate :
    algebraicOrbitHull (quiverOps (K := K))
      (certificateSeeds (K := K)) = ⊤ := by
  apply top_unique
  rintro ⟨u, v⟩ htop
  let rOp : {T : Module.End K (X K) // T ∈ quiverOps} :=
    ⟨totalR, by simp [quiverOps]⟩
  let aOp : {T : Module.End K (X K) // T ∈ quiverOps} :=
    ⟨totalA, by simp [quiverOps]⟩
  have hsU : sourceSeed (K := K) ∈ certificateSeeds := by
    simp [certificateSeeds]
  have hsV : missingSeed (K := K) ∈ certificateSeeds := by
    simp [certificateSeeds]
  have hu₁ : sourceSeed (K := K) ∈
      algebraicOrbitHull (quiverOps (K := K)) certificateSeeds :=
    orbit_mem_hull hsU []
  have hu₂ : totalR (sourceSeed (K := K)) ∈
      algebraicOrbitHull (quiverOps (K := K)) certificateSeeds :=
    orbit_mem_hull hsU [rOp]
  have hv₁ : totalA (sourceSeed (K := K)) ∈
      algebraicOrbitHull (quiverOps (K := K)) certificateSeeds :=
    orbit_mem_hull hsU [aOp]
  have hv₂ : totalA (totalR (sourceSeed (K := K))) ∈
      algebraicOrbitHull (quiverOps (K := K)) certificateSeeds :=
    orbit_mem_hull hsU [rOp, aOp]
  have hv₃ : missingSeed (K := K) ∈
      algebraicOrbitHull (quiverOps (K := K)) certificateSeeds :=
    orbit_mem_hull hsV []
  have hdecomp :
      (u, v) =
        u 0 • sourceSeed +
        u 1 • totalR sourceSeed +
        v 0 • totalA sourceSeed +
        v 1 • totalA (totalR sourceSeed) +
        v 2 • missingSeed := by
    apply Prod.ext
    · funext i
      fin_cases i <;>
        simp [sourceSeed, missingSeed, totalR, totalA, rotation, arrowA,
          eU₁, eV₃]
    · funext i
      fin_cases i <;>
        simp [sourceSeed, missingSeed, totalR, totalA, rotation, arrowA,
          eU₁, eV₃]
  rw [hdecomp]
  apply Submodule.add_mem
  · apply Submodule.add_mem
    · apply Submodule.add_mem
      · apply Submodule.add_mem
        · exact Submodule.smul_mem _ (u 0) hu₁
        · exact Submodule.smul_mem _ (u 1) hu₂
      · exact Submodule.smul_mem _ (v 0) hv₁
    · exact Submodule.smul_mem _ (v 1) hv₂
  · exact Submodule.smul_mem _ (v 2) hv₃

/-- The complete finite typed-quiver certificate from Paper I. -/
theorem typed_reachability_certificate :
    (arrowB (K := K)).comp arrowA = LinearMap.id ∧
      eV₃ (K := K) ∈ LinearMap.ker arrowB ∧
      eV₃ (K := K) ∉ LinearMap.range arrowA ∧
      (∀ seeds : Set (X K), (∀ s ∈ seeds, s.2 = 0) →
        algebraicOrbitHull (quiverOps (K := K)) seeds ≠ ⊤) ∧
      algebraicOrbitHull (quiverOps (K := K)) certificateSeeds = ⊤ := by
  exact ⟨arrowB_comp_arrowA, eV₃_mem_ker_arrowB,
    eV₃_not_mem_range_arrowA, no_u_supported_seeds_generate,
    certificateSeeds_generate⟩

end TypedQuiver

end Komorebi.PacketNaturalityCompletion
