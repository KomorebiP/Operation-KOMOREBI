import KomorebiVerification.PacketNaturalityCompletion
import Mathlib.CategoryTheory.Category.Basic

/-!
Arbitrary-label packet morphisms, their naturality, and the category of algebraic
seeded packet systems.  Packet maps may merge labels and need not be surjective.
-/

set_option autoImplicit false
set_option maxHeartbeats 1600000
set_option linter.unnecessarySimpa false
set_option linter.unusedVariables false

noncomputable section

namespace Komorebi.PaperIRelease.CategoryPackets

open scoped BigOperators
open Foundation CategoryTheory
open PacketNaturalityCompletion.StrictNaturality
attribute [local instance] Classical.propDecidable

universe u

variable (K : Type u) [Field K]

/-- A finite packet-resolved concrete operator module. -/
structure PacketObject where
  carrier : Type u
  [addCommGroup : AddCommGroup carrier]
  [module : Module K carrier]
  index : Type u
  [fintype : Fintype index]
  algebra : Subalgebra K (Module.End K carrier)
  packets : LinearProjectorFamily K carrier index
  packet_nonzero : ∀ i, packets.proj i ≠ 0

attribute [instance] PacketObject.addCommGroup PacketObject.module PacketObject.fintype

variable {K}

/-- Empty fibres contribute zero, as required in the manuscript definition. -/
def fiberProjector (X : PacketObject K) {J : Type u} (σ : X.index → J) (j : J) :
    Module.End K X.carrier := by
  classical
  exact ∑ i, if σ i = j then X.packets.proj i else 0

@[simp] theorem fiberProjector_apply (X : PacketObject K) {J : Type u}
    (σ : X.index → J) (j : J) (x : X.carrier) :
    fiberProjector X σ j x = ∑ i, if σ i = j then X.packets.proj i x else 0 := by
  classical
  simp only [fiberProjector, LinearMap.sum_apply]
  apply Finset.sum_congr rfl
  intro i hi
  split <;> rfl

/-- PSC-I-D-PACKET-MORPHISM, with no injectivity constraint on the labels. -/
structure PacketMorphism (X Y : PacketObject K) where
  linearMap : X.carrier →ₗ[K] Y.carrier
  algebraMap : X.algebra →ₐ[K] Y.algebra
  packetMap : X.index → Y.index
  operator_natural : ∀ T : X.algebra,
    linearMap.comp T.1 = (algebraMap T).1.comp linearMap
  packet_natural : ∀ j : Y.index,
    (Y.packets.proj j).comp linearMap = linearMap.comp (fiberProjector X packetMap j)

theorem PacketMorphism.operator_apply {X Y : PacketObject K}
    (f : PacketMorphism X Y) (T : X.algebra) (x : X.carrier) :
    f.linearMap (T.1 x) = (f.algebraMap T).1 (f.linearMap x) :=
  LinearMap.congr_fun (f.operator_natural T) x

theorem PacketMorphism.packet_apply {X Y : PacketObject K}
    (f : PacketMorphism X Y) (j : Y.index) (x : X.carrier) :
    Y.packets.proj j (f.linearMap x) = f.linearMap (fiberProjector X f.packetMap j x) :=
  LinearMap.congr_fun (f.packet_natural j) x

@[ext] theorem PacketMorphism.ext {X Y : PacketObject K}
    (f g : PacketMorphism X Y) (hl : f.linearMap = g.linearMap)
    (ha : f.algebraMap = g.algebraMap) (hp : f.packetMap = g.packetMap) : f = g := by
  cases f
  cases g
  cases hl
  cases ha
  cases hp
  rfl

theorem sum_fibers {I J L V : Type u} [Fintype I] [Fintype J]
    [AddCommMonoid V] (σ : I → J) (τ : J → L) (v : I → V) (k : L) :
    (∑ j, if τ j = k then ∑ i, if σ i = j then v i else 0 else 0) =
      ∑ i, if τ (σ i) = k then v i else 0 := by
  classical
  calc
    _ = ∑ j, ∑ i, if σ i = j then (if τ j = k then v i else 0) else 0 := by
      apply Finset.sum_congr rfl
      intro j hj
      by_cases h : τ j = k <;> simp [h]
    _ = ∑ i, ∑ j, if σ i = j then (if τ j = k then v i else 0) else 0 :=
      Finset.sum_comm
    _ = _ := by simp

/-- The identity preserves every packet, including in the empty-index zero-space case. -/
def PacketMorphism.identity (X : PacketObject K) : PacketMorphism X X where
  linearMap := LinearMap.id
  algebraMap := AlgHom.id K X.algebra
  packetMap := id
  operator_natural T := by simp
  packet_natural j := by
    classical
    ext x
    simp [fiberProjector]

/-- Composition aggregates the fibres of the composite label map. -/
def PacketMorphism.comp {X Y Z : PacketObject K}
    (f : PacketMorphism X Y) (g : PacketMorphism Y Z) : PacketMorphism X Z where
  linearMap := g.linearMap.comp f.linearMap
  algebraMap := g.algebraMap.comp f.algebraMap
  packetMap := g.packetMap ∘ f.packetMap
  operator_natural T := by
    ext x
    change g.linearMap (f.linearMap (T.1 x)) =
      (g.algebraMap (f.algebraMap T)).1 (g.linearMap (f.linearMap x))
    rw [f.operator_apply T x]
    exact g.operator_apply (f.algebraMap T) (f.linearMap x)
  packet_natural k := by
    classical
    ext x
    change Z.packets.proj k (g.linearMap (f.linearMap x)) =
      g.linearMap (f.linearMap (fiberProjector X (g.packetMap ∘ f.packetMap) k x))
    rw [g.packet_apply k (f.linearMap x)]
    simp only [fiberProjector_apply, map_sum]
    have hf (j : Y.index) : Y.packets.proj j (f.linearMap x) =
        ∑ i, if f.packetMap i = j then f.linearMap (X.packets.proj i x) else 0 := by
      rw [f.packet_apply j x]
      simp [fiberProjector_apply, map_sum, apply_ite]
    simp_rw [hf]
    simp only [apply_ite, map_zero, map_sum]
    exact sum_fibers f.packetMap g.packetMap
      (fun i => g.linearMap (f.linearMap (X.packets.proj i x))) k

instance packetCategory : Category (PacketObject K) where
  Hom := PacketMorphism
  id := PacketMorphism.identity
  comp := PacketMorphism.comp
  id_comp f := by apply PacketMorphism.ext <;> rfl
  comp_id f := by apply PacketMorphism.ext <;> rfl
  assoc f g h := by apply PacketMorphism.ext <;> rfl

/-- The source hull maps onto exactly the orbit span for the image algebra. -/
def ImageHull {X Y : PacketObject K} (f : PacketMorphism X Y) (S : Set X.carrier) :
    Submodule K Y.carrier :=
  Submodule.span K {y | ∃ T : X.algebra, ∃ s ∈ S,
    y = (f.algebraMap T).1 (f.linearMap s)}

theorem hull_natural {X Y : PacketObject K} (f : PacketMorphism X Y)
    (S : Set X.carrier) :
    Submodule.map f.linearMap (AlgebraGeneratedHull X.algebra S) = ImageHull f S := by
  rw [AlgebraGeneratedHull, ImageHull, Submodule.map_span]
  congr 1
  ext y
  constructor
  · rintro ⟨x, ⟨T, s, hs, rfl⟩, rfl⟩
    exact ⟨T, s, hs, LinearMap.congr_fun (f.operator_natural T) s⟩
  · rintro ⟨T, s, hs, rfl⟩
    exact ⟨T.1 s, ⟨T, s, hs, rfl⟩,
      LinearMap.congr_fun (f.operator_natural T) s⟩

theorem imageHull_le {X Y : PacketObject K} (f : PacketMorphism X Y)
    (S : Set X.carrier) :
    ImageHull f S ≤ AlgebraGeneratedHull Y.algebra (f.linearMap '' S) := by
  apply Submodule.span_le.2
  rintro y ⟨T, s, hs, rfl⟩
  exact Submodule.subset_span ⟨f.algebraMap T, f.linearMap s, ⟨s, hs, rfl⟩, rfl⟩

theorem imageHull_eq_top {X Y : PacketObject K} (f : PacketMorphism X Y)
    (S : Set X.carrier) (hS : AlgebraGeneratedHull X.algebra S = ⊤)
    (hf : Function.Surjective f.linearMap) : ImageHull f S = ⊤ := by
  rw [← hull_natural f S, hS, Submodule.map_top, LinearMap.range_eq_top.mpr hf]

theorem sum_conditions_comm {I J V : Type u} [Fintype I] [Fintype J]
    [AddCommMonoid V] (p : I → Prop) (q : J → Prop) (v : I → J → V) :
    (∑ i, if p i then ∑ j, if q j then v i j else 0 else 0) =
      ∑ j, if q j then ∑ i, if p i then v i j else 0 else 0 := by
  calc
    _ = ∑ i, ∑ j, if p i then (if q j then v i j else 0) else 0 := by
      apply Finset.sum_congr rfl
      intro i hi
      by_cases hp : p i <;> simp [hp]
    _ = ∑ j, ∑ i, if p i then (if q j then v i j else 0) else 0 :=
      Finset.sum_comm
    _ = _ := by
      apply Finset.sum_congr rfl
      intro j hj
      by_cases hq : q j <;> simp [hq]

/-- Noninjective labels produce the exact double sum over source packet fibres. -/
theorem transferBlock_naturality_apply {X Y : PacketObject K}
    (f : PacketMorphism X Y) (T : X.algebra) (j i : Y.index) (x : X.carrier) :
    Y.packets.proj j ((f.algebraMap T).1 (Y.packets.proj i (f.linearMap x))) =
      ∑ b, if f.packetMap b = j then
        ∑ a, if f.packetMap a = i then
          f.linearMap (X.packets.proj b (T.1 (X.packets.proj a x))) else 0
        else 0 := by
  rw [f.packet_apply i x, ← f.operator_apply T, f.packet_apply j]
  simp only [fiberProjector_apply, map_sum, apply_ite, map_zero]
  exact sum_conditions_comm (fun a => f.packetMap a = i) (fun b => f.packetMap b = j)
    (fun a b => f.linearMap (X.packets.proj b (T.1 (X.packets.proj a x))))

/-- PSC-I-T-NATURALITY: equality of the actual transfer-block linear maps. -/
theorem transferBlock_naturality {X Y : PacketObject K}
    (f : PacketMorphism X Y) (T : X.algebra) (j i : Y.index) :
    (transferBlock Y.packets Y.packets (f.algebraMap T).1 j i).comp f.linearMap =
      ∑ b, if f.packetMap b = j then
        ∑ a, if f.packetMap a = i then
          f.linearMap.comp (transferBlock X.packets X.packets T.1 b a) else 0
        else 0 := by
  apply LinearMap.ext
  intro x
  have heval (p : Prop) (s t : X.carrier →ₗ[K] Y.carrier) :
      (if p then s else t) x = if p then s x else t x := by
    by_cases hp : p <;> simp [hp]
  simp only [LinearMap.sum_apply, heval, LinearMap.zero_apply]
  exact transferBlock_naturality_apply f T j i x

/-- The ordinary A-span equals the scalar span of all A-orbits. -/
theorem hull_eq_span (X : PacketObject K) (S : Set X.carrier) :
    (AlgebraGeneratedHull X.algebra S : Set X.carrier) = Submodule.span X.algebra S := by
  ext x
  constructor
  · intro hx
    induction hx using Submodule.span_induction with
    | mem x hx =>
        rcases hx with ⟨T, s, hs, rfl⟩
        exact Submodule.smul_mem _ T (Submodule.subset_span hs)
    | zero => exact Submodule.zero_mem _
    | add x y hx hy ihx ihy => exact Submodule.add_mem _ ihx ihy
    | smul c x hx ih =>
        exact Submodule.smul_mem _ (algebraMap K X.algebra c) ih
  · intro hx
    have hstable (T : X.algebra) {x : X.carrier}
        (hx : x ∈ AlgebraGeneratedHull X.algebra S) :
        T.1 x ∈ AlgebraGeneratedHull X.algebra S := by
      induction hx using Submodule.span_induction with
      | mem x hx =>
          rcases hx with ⟨U, s, hs, rfl⟩
          exact Submodule.subset_span ⟨T * U, s, hs, rfl⟩
      | zero => simpa using (Submodule.zero_mem (AlgebraGeneratedHull X.algebra S))
      | add x y hx hy ihx ihy => simpa using Submodule.add_mem _ ihx ihy
      | smul c x hx ih => simpa using Submodule.smul_mem _ c ih
    induction hx using Submodule.span_induction with
    | mem x hx => exact Submodule.subset_span ⟨1, x, hx, by simp⟩
    | zero => exact Submodule.zero_mem _
    | add x y hx hy ihx ihy => exact Submodule.add_mem _ ihx ihy
    | smul T x hx ih => exact hstable T ih

/-- Algebraic seeded packet objects retain the declared seed set. -/
structure SeedObject extends PacketObject K where
  seeds : Set carrier

/-- PSC-I-D-SEED-MORPHISM: the image seeds lie in the target generated hull. -/
structure SeedMorphism (X Y : SeedObject (K := K)) extends
    PacketMorphism X.toPacketObject Y.toPacketObject where
  seed_condition : ∀ s ∈ X.seeds, linearMap s ∈ Submodule.span Y.algebra Y.seeds

@[ext] theorem SeedMorphism.ext {X Y : SeedObject (K := K)}
    (f g : SeedMorphism X Y) (h : f.toPacketMorphism = g.toPacketMorphism) : f = g := by
  cases f
  cases g
  cases h
  rfl

def SeedMorphism.identity (X : SeedObject (K := K)) : SeedMorphism X X where
  toPacketMorphism := PacketMorphism.identity X.toPacketObject
  seed_condition s hs := Submodule.subset_span hs

def SeedMorphism.comp {X Y Z : SeedObject (K := K)}
    (f : SeedMorphism X Y) (g : SeedMorphism Y Z) : SeedMorphism X Z where
  toPacketMorphism := f.toPacketMorphism.comp g.toPacketMorphism
  seed_condition s hs := by
    have hm := map_mem_span_image_of_intertwining g.linearMap g.algebraMap
      g.operator_natural Y.seeds (f.seed_condition s hs)
    have hi : Submodule.span Z.algebra (g.linearMap '' Y.seeds) ≤
        Submodule.span Z.algebra Z.seeds := by
      apply Submodule.span_le.2
      rintro x ⟨s, hs, rfl⟩
      exact g.seed_condition s hs
    exact hi hm

instance seedCategory : Category (SeedObject (K := K)) where
  Hom := SeedMorphism
  id := SeedMorphism.identity
  comp := SeedMorphism.comp
  id_comp f := by apply SeedMorphism.ext; apply PacketMorphism.ext <;> rfl
  comp_id f := by apply SeedMorphism.ext; apply PacketMorphism.ext <;> rfl
  assoc f g h := by apply SeedMorphism.ext; apply PacketMorphism.ext <;> rfl

/-- A surjective seeded morphism out of a generated system generates the target. -/
theorem seeded_surjection_generates {X Y : SeedObject (K := K)}
    (f : SeedMorphism X Y) (hf : Function.Surjective f.linearMap)
    (hX : Submodule.span X.algebra X.seeds = ⊤) :
    Submodule.span Y.algebra Y.seeds = ⊤ := by
  have hi := image_generates_of_surjective_intertwining f.linearMap f.algebraMap
    f.operator_natural hf X.seeds hX
  apply top_unique
  rw [← hi]
  apply Submodule.span_le.2
  rintro y ⟨s, hs, rfl⟩
  exact f.seed_condition s hs

end Komorebi.PaperIRelease.CategoryPackets
