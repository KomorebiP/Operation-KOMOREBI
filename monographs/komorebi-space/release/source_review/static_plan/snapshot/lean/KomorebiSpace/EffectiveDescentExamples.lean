import KomorebiSpace.DescentEquivalence
import KomorebiSpace.CocycleExamples
import Mathlib.CategoryTheory.Category.Preorder

set_option autoImplicit false

/-!
# Nontrivial overlap data and the necessity of the triple-overlap law

Four proper patches of four ordered views give a composition cover. The local
cocycles are deliberately unequal on a common arrow, and their overlap gauges
use noncommuting permutations. A separate group-theoretic obstruction shows
that pairwise overlap arrows cannot replace the triple-overlap condition.
-/
universe u v w z
namespace KomorebiSpace
open CategoryTheory GroupViewSystem
namespace EffectiveDescentExamples

section Frames
variable {V : Type u} [Category.{v} V]
variable {G : V → Type w} [∀ a, Group (G a)]
variable {I : Type z} {F : GroupViewSystem V G} {U : I → Set V}

/-- Benchmark descent data made from arbitrary local changes of frame. -/
def fromFrames (c : F.Cocycle) (k : ∀ i, ∀ x : U i, G x.val) :
    F.CocycleDescentData U where
  patch := fun i => (F.restrictCocycle c (U i)).gauge (k i)
  change := fun i j x hi hj => k j ⟨x,hj⟩ * (k i ⟨x,hi⟩)⁻¹
  change_edge := by
    intro i j x y hxi hyi hxj hyj f
    simp only [PatchCocycle.gauge_edge, restrictCocycle, map_mul, map_inv]
    group
  change_comp := by intros; group

/-- The benchmark's known global answer, independent of the gluing algorithm. -/
def framesEffectuation (c : F.Cocycle) (k : ∀ i, ∀ x : U i, G x.val) :
    (fromFrames c k).Effectuation where
  global := c
  compare := k
  local_eq := by intros; rfl
  overlap := by intros; change _ = (_ * _⁻¹) * _; group
end Frames

abbrev S3 := CocycleExamples.S3
abbrev t : S3 := CocycleExamples.transposition
abbrev uperm : S3 := CocycleExamples.otherTransposition

def fourCoefficients : GroupViewSystem (Fin 4) (fun _ => S3) where
  pull := fun _ => MonoidHom.id S3
  pull_id := by intros; rfl
  pull_comp := by intros; rfl

def patches (i : Fin 4) : Set (Fin 4) := {x | x ≠ i}

instance (i x : Fin 4) : Decidable (x ∈ patches i) :=
  inferInstanceAs (Decidable (x ≠ i))

theorem patches_proper (i : Fin 4) : ∃ x, x ∉ patches i := ⟨i, by simp [patches]⟩

theorem patches_compositionCover : CompositionCover patches := by
  have h : ∀ a b c : Fin 4, ∃ i : Fin 4, a ≠ i ∧ b ≠ i ∧ c ≠ i := by decide
  intro a b c f g
  exact h a b c

/-- Patches zero and three deliberately use distinct permutations at view one. -/
def localFrames (i : Fin 4) (x : patches i) : S3 :=
  if x.val = 1 then if i = 0 then t else if i = 3 then uperm else 1 else 1

def data : fourCoefficients.CocycleDescentData patches :=
  fromFrames fourCoefficients.trivial localFrames

def edge12 : (1 : Fin 4) ⟶ (2 : Fin 4) := homOfLE (by decide)

/-- Strict label agreement does not hold for this valid descent datum. -/
theorem local_labels_differ :
    (data.patch 0).edge (a := ⟨1,by decide⟩) (b := ⟨2,by decide⟩) edge12 ≠
      (data.patch 3).edge (a := ⟨1,by decide⟩) (b := ⟨2,by decide⟩) edge12 := by decide

theorem overlap_nonidentity :
    data.change 0 3 1 (by decide) (by decide) ≠ 1 := by decide

/-- Reversing the required multiplication order produces the wrong overlap. -/
theorem overlap_order_matters :
    data.change 0 3 1 (by decide) (by decide) ≠
      data.change 0 2 1 (by decide) (by decide) *
        data.change 2 3 1 (by decide) (by decide) := by decide

noncomputable def reconstructed : data.Effectuation := data.effectuate patches_compositionCover

theorem reconstructed_local (i : Fin 4) (x y : patches i) (f : x.val ⟶ y.val) :
    reconstructed.compare i x * reconstructed.global.edge f *
      (fourCoefficients.pull f (reconstructed.compare i y))⁻¹ = (data.patch i).edge f :=
  reconstructed.local_eq i x y f

/-- The independent benchmark and the constructed answer agree up to the required gauge. -/
noncomputable def reconstructedIso :
    reconstructed.object ≅ (framesEffectuation fourCoefficients.trivial localFrames).object :=
  reconstructed.comparisonIso (framesEffectuation fourCoefficients.trivial localFrames)
    patches_compositionCover.transitionCover

/-- Actual groupoid equivalence on a proper-patch cover with unequal local cocycles. -/
noncomputable def exampleEquivalence :
    fourCoefficients.GaugeObject ∅ ≌ fourCoefficients.CocycleDescentData patches :=
  CocycleDescentData.descentEquivalence fourCoefficients patches patches_compositionCover

section Necessity
variable {H : Type u} [Group H]

/-- Any effectuation's local identifications force the triple-overlap law. -/
theorem comparisons_force_triple (b0 b1 b2 a01 a12 a02 : H)
    (h01 : b1 = a01 * b0) (h12 : b2 = a12 * b1) (h02 : b2 = a02 * b0) :
    a02 = a12 * a01 := by
  apply mul_right_cancel (b := b0)
  calc
    a02 * b0 = b2 := h02.symm
    _ = a12 * b1 := h12
    _ = (a12 * a01) * b0 := by rw [h01, mul_assoc]
end Necessity

/-- Three individually invertible overlap gauges can still be incompatible. -/
theorem inconsistent_triple_no_frames :
    ¬ ∃ b0 b1 b2 : S3, b1 = t * b0 ∧ b2 = t * b1 ∧ b2 = t * b0 := by
  rintro ⟨b0,b1,b2,h01,h12,h02⟩
  have he := comparisons_force_triple b0 b1 b2 t t t h01 h12 h02
  exact CocycleExamples.transposition_nontrivial
    (he.trans CocycleExamples.transposition_square)

end EffectiveDescentExamples
end KomorebiSpace
