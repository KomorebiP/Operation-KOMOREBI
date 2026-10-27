import PaperIRelease.CategoryPackets
import PaperIRelease.TopologyTransport

/-!
# Continuous packet and seeded-system categories

The operator algebras are concrete algebras of individually continuous
linear operators; no additional topology on the operator algebra itself is
declared. Carrier morphisms and packet projectors are continuous. The seeded
condition uses the closure of the actual algebraic generated hull.
-/

noncomputable section
open Set Function CategoryTheory

namespace Komorebi.PaperIRelease.TopologyCategories

open Foundation
open PacketNaturalityCompletion.StrictNaturality

universe u
variable (K : Type u) [Field K] [TopologicalSpace K]

structure PacketObject extends CategoryPackets.PacketObject K where
  [topology : TopologicalSpace carrier]
  [topologicalAdd : IsTopologicalAddGroup carrier]
  [scalarContinuous : ContinuousSMul K carrier]
  [hausdorff : T2Space carrier]
  operator_continuous : ∀ T : algebra, Continuous T.val
  packet_continuous : ∀ i, Continuous (packets.proj i)

attribute [instance] PacketObject.topology PacketObject.topologicalAdd
  PacketObject.scalarContinuous PacketObject.hausdorff

variable {K}

structure PacketMorphism (X Y : PacketObject K) extends
    CategoryPackets.PacketMorphism X.toPacketObject Y.toPacketObject where
  continuous : Continuous linearMap

@[ext]
theorem PacketMorphism.ext {X Y : PacketObject K} (f g : PacketMorphism X Y)
    (h : f.toPacketMorphism = g.toPacketMorphism) : f = g := by
  cases f
  cases g
  cases h
  rfl

def PacketMorphism.identity (X : PacketObject K) : PacketMorphism X X where
  toPacketMorphism := CategoryPackets.PacketMorphism.identity X.toPacketObject
  continuous := continuous_id

def PacketMorphism.comp {X Y Z : PacketObject K}
    (f : PacketMorphism X Y) (g : PacketMorphism Y Z) : PacketMorphism X Z where
  toPacketMorphism := f.toPacketMorphism.comp g.toPacketMorphism
  continuous := g.continuous.comp f.continuous

instance packetCategory : Category (PacketObject K) where
  Hom := PacketMorphism
  id := PacketMorphism.identity
  comp := PacketMorphism.comp
  id_comp f := by apply PacketMorphism.ext; apply CategoryPackets.PacketMorphism.ext <;> rfl
  comp_id f := by apply PacketMorphism.ext; apply CategoryPackets.PacketMorphism.ext <;> rfl
  assoc f g h := by apply PacketMorphism.ext; apply CategoryPackets.PacketMorphism.ext <;> rfl

/-- Closure of the actual algebraic operator-generated hull. -/
def closedHull (X : PacketObject K) (S : Set X.carrier) : Submodule K X.carrier :=
  (AlgebraGeneratedHull X.algebra S).topologicalClosure

/-- The closed hull is invariant under every individually continuous
operator of the acting algebra. -/
theorem operator_mem_closedHull (X : PacketObject K) (S : Set X.carrier)
    (T : X.algebra) {x : X.carrier} (hx : x ∈ closedHull X S) :
    T.val x ∈ closedHull X S := by
  have hsmall : T.val '' (AlgebraGeneratedHull X.algebra S : Set X.carrier) ⊆
      (AlgebraGeneratedHull X.algebra S : Set X.carrier) := by
    rintro y ⟨x, hx, rfl⟩
    rw [CategoryPackets.hull_eq_span X.toPacketObject S] at hx ⊢
    exact Submodule.smul_mem _ T hx
  change T.val x ∈ closure (AlgebraGeneratedHull X.algebra S : Set X.carrier)
  exact closure_mono hsmall
    (image_closure_subset_closure_image (X.operator_continuous T) ⟨x, hx, rfl⟩)

structure SeedObject extends toContinuousPacketObject : PacketObject K where
  seeds : Set carrier

structure SeedMorphism (X Y : SeedObject (K := K)) extends
    toContinuousPacketMorphism : PacketMorphism X.toContinuousPacketObject Y.toContinuousPacketObject where
  seed_condition : ∀ s ∈ X.seeds, linearMap s ∈ closedHull Y.toContinuousPacketObject Y.seeds

@[ext]
theorem SeedMorphism.ext {X Y : SeedObject (K := K)} (f g : SeedMorphism X Y)
    (h : f.toContinuousPacketMorphism = g.toContinuousPacketMorphism) : f = g := by
  cases f
  cases g
  cases h
  rfl

/-- A continuous seeded morphism carries the algebraic hull into the
target closed hull. The action-invariance step uses operator continuity. -/
theorem SeedMorphism.map_hull {X Y : SeedObject (K := K)}
    (f : SeedMorphism X Y) {x : X.carrier}
    (hx : x ∈ AlgebraGeneratedHull X.algebra X.seeds) :
    f.linearMap x ∈ closedHull Y.toContinuousPacketObject Y.seeds := by
  induction hx using Submodule.span_induction with
  | mem x hx =>
    rcases hx with ⟨T, s, hs, rfl⟩
    rw [f.toContinuousPacketMorphism.toPacketMorphism.operator_apply T s]
    exact operator_mem_closedHull Y.toContinuousPacketObject Y.seeds (f.algebraMap T) (f.seed_condition s hs)
  | zero => simp
  | add x y hx hy ihx ihy => simpa using Submodule.add_mem _ ihx ihy
  | smul a x hx ih => simpa using Submodule.smul_mem _ a ih

/-- Closure transport is derived from actual continuity and the proved
algebraic hull inclusion. -/
theorem SeedMorphism.map_closedHull {X Y : SeedObject (K := K)}
    (f : SeedMorphism X Y) {x : X.carrier}
    (hx : x ∈ closedHull X.toContinuousPacketObject X.seeds) :
    f.linearMap x ∈ closedHull Y.toContinuousPacketObject Y.seeds := by
  have hsmall : f.linearMap '' (AlgebraGeneratedHull X.algebra X.seeds : Set X.carrier) ⊆
      (closedHull Y.toContinuousPacketObject Y.seeds : Set Y.carrier) := by
    rintro y ⟨x, hx, rfl⟩
    exact f.map_hull hx
  have him := image_closure_subset_closure_image f.continuous ⟨x, hx, rfl⟩
  exact closure_minimal hsmall (Submodule.isClosed_topologicalClosure _) him

def SeedMorphism.identity (X : SeedObject (K := K)) : SeedMorphism X X where
  toContinuousPacketMorphism := PacketMorphism.identity X.toContinuousPacketObject
  seed_condition s hs := by
    change s ∈ closedHull X.toContinuousPacketObject X.seeds
    apply Submodule.le_topologicalClosure
    exact Submodule.subset_span ⟨1, s, hs, by simp⟩

def SeedMorphism.comp {X Y Z : SeedObject (K := K)}
    (f : SeedMorphism X Y) (g : SeedMorphism Y Z) : SeedMorphism X Z where
  toContinuousPacketMorphism := f.toContinuousPacketMorphism.comp g.toContinuousPacketMorphism
  seed_condition s hs := g.map_closedHull (f.seed_condition s hs)

instance seedCategory : Category (SeedObject (K := K)) where
  Hom := SeedMorphism
  id := SeedMorphism.identity
  comp := SeedMorphism.comp
  id_comp f := by apply SeedMorphism.ext; apply PacketMorphism.ext; apply CategoryPackets.PacketMorphism.ext <;> rfl
  comp_id f := by apply SeedMorphism.ext; apply PacketMorphism.ext; apply CategoryPackets.PacketMorphism.ext <;> rfl
  assoc f g h := by apply SeedMorphism.ext; apply PacketMorphism.ext; apply CategoryPackets.PacketMorphism.ext <;> rfl

/-- A continuous surjective seeded morphism from a densely generated
system has densely generating target seeds. -/
theorem seeded_surjection_generates {X Y : SeedObject (K := K)}
    (f : SeedMorphism X Y) (hf : Surjective f.linearMap)
    (hX : closedHull X.toContinuousPacketObject X.seeds = ⊤) :
    closedHull Y.toContinuousPacketObject Y.seeds = ⊤ := by
  apply top_unique
  intro y _
  obtain ⟨x, rfl⟩ := hf y
  apply f.map_closedHull
  rw [hX]
  trivial

end Komorebi.PaperIRelease.TopologyCategories
