import KomorebiSpace.Cofinal
import Mathlib.CategoryTheory.Category.Basic

set_option autoImplicit false

/-!
# Sequential reindexed transports and eventual equality

An output coordinate may use a finer input coordinate. Two presentations agree
when they agree after restriction from a common sufficiently fine input level,
separately for every output coordinate. This is NOT equality of the resulting
functions on inverse limits; that weaker identification is not used here.
-/

universe u v w z
namespace KomorebiSpace
namespace Resolution

structure ReindexedMap (X : Resolution.{u}) (Y : Resolution.{v}) where
  level : ℕ → ℕ
  monotone : Monotone level
  app : ∀ n, X.Obj (level n) → Y.Obj n
  naturality : ∀ i j (h : i ≤ j) (x : X.Obj (level j)),
    Y.restrict h (app j x) = app i (X.restrict (monotone h) x)

namespace ReindexedMap
variable {X : Resolution.{u}} {Y : Resolution.{v}}
    {Z : Resolution.{w}} {W : Resolution.{z}}

def id (X : Resolution.{u}) : ReindexedMap X X where
  level := fun n => n
  monotone := fun _ _ h => h
  app := fun _ x => x
  naturality := by intros; rfl

def ofMap (f : Map X Y) : ReindexedMap X Y where
  level := fun n => n
  monotone := fun _ _ h => h
  app := f.app
  naturality := f.exact

def comp (f : ReindexedMap X Y) (g : ReindexedMap Y Z) : ReindexedMap X Z where
  level := fun n => f.level (g.level n)
  monotone := f.monotone.comp g.monotone
  app := fun n x => g.app n (f.app (g.level n) x)
  naturality := by
    intro i j h x
    rw [g.naturality, f.naturality]

@[simp] theorem id_comp (f : ReindexedMap X Y) : comp (id X) f = f := by
  cases f; rfl

@[simp] theorem comp_id (f : ReindexedMap X Y) : comp f (id Y) = f := by
  cases f; rfl

theorem comp_assoc (f : ReindexedMap X Y) (g : ReindexedMap Y Z)
    (h : ReindexedMap Z W) : comp (comp f g) h = comp f (comp g h) := rfl

/-- Agreement is witnessed at a finite stage, not postulated on realized points. -/
def EventuallyEq (f g : ReindexedMap X Y) : Prop :=
  ∀ n, ∃ k, ∃ hf : f.level n ≤ k, ∃ hg : g.level n ≤ k,
    ∀ x : X.Obj k, f.app n (X.restrict hf x) = g.app n (X.restrict hg x)

/-- Equality at a stage persists at every finer stage. -/
theorem agree_further (f g : ReindexedMap X Y) (n k l : ℕ)
    (hf : f.level n ≤ k) (hg : g.level n ≤ k)
    (hfg : ∀ x : X.Obj k, f.app n (X.restrict hf x) = g.app n (X.restrict hg x))
    (hkl : k ≤ l) (x : X.Obj l) :
    f.app n (X.restrict (hf.trans hkl) x) =
      g.app n (X.restrict (hg.trans hkl) x) := by
  rw [← X.restrict_trans hf hkl, ← X.restrict_trans hg hkl]
  exact hfg (X.restrict hkl x)

@[refl] theorem eventuallyEq_refl (f : ReindexedMap X Y) : EventuallyEq f f := by
  intro n
  exact ⟨f.level n, le_refl _, le_refl _, fun _ => rfl⟩

@[symm] theorem eventuallyEq_symm {f g : ReindexedMap X Y}
    (h : EventuallyEq f g) : EventuallyEq g f := by
  intro n
  obtain ⟨k, hf, hg, hk⟩ := h n
  exact ⟨k, hg, hf, fun x => (hk x).symm⟩

@[trans] theorem eventuallyEq_trans {f g h : ReindexedMap X Y}
    (hfg : EventuallyEq f g) (hgh : EventuallyEq g h) : EventuallyEq f h := by
  intro n
  obtain ⟨k, hf, hg, hk⟩ := hfg n
  obtain ⟨l, hg', hh, hl⟩ := hgh n
  refine ⟨max k l, hf.trans (Nat.le_max_left _ _),
    hh.trans (Nat.le_max_right _ _), ?_⟩
  intro x
  exact (agree_further f g n k (max k l) hf hg hk (Nat.le_max_left _ _) x).trans
    (agree_further g h n l (max k l) hg' hh hl (Nat.le_max_right _ _) x)

/-- Eventual equality is a congruence for composition of scheduled transports. -/
theorem comp_congr {f f' : ReindexedMap X Y} {g g' : ReindexedMap Y Z}
    (hf : EventuallyEq f f') (hg : EventuallyEq g g') :
    EventuallyEq (comp f g) (comp f' g') := by
  intro n
  obtain ⟨j, hgj, hgj', hj⟩ := hg n
  obtain ⟨k, hfk, hfk', hk⟩ := hf j
  refine ⟨k, (f.monotone hgj).trans hfk,
    (f'.monotone hgj').trans hfk', ?_⟩
  intro x
  change g.app n (f.app (g.level n) (X.restrict _ x)) =
    g'.app n (f'.app (g'.level n) (X.restrict _ x))
  calc
    g.app n (f.app (g.level n) (X.restrict _ x)) =
        g.app n (Y.restrict hgj (f.app j (X.restrict hfk x))) := by
      rw [f.naturality, X.restrict_trans]
    _ = g.app n (Y.restrict hgj (f'.app j (X.restrict hfk' x))) := by rw [hk x]
    _ = g'.app n (Y.restrict hgj' (f'.app j (X.restrict hfk' x))) :=
      hj (f'.app j (X.restrict hfk' x))
    _ = g'.app n (f'.app (g'.level n) (X.restrict _ x)) := by
      rw [f'.naturality, X.restrict_trans]

instance eventualSetoid (X : Resolution.{u}) (Y : Resolution.{v}) :
    Setoid (ReindexedMap X Y) where
  r := EventuallyEq
  iseqv := ⟨eventuallyEq_refl, eventuallyEq_symm, eventuallyEq_trans⟩

/-- Realization only uses coherent input coordinates at the selected stages. -/
def onLimit (f : ReindexedMap X Y) (x : X.Point) : Y.Point :=
  ⟨fun n => f.app n (x.val (f.level n)), by
    intro i j h
    rw [f.naturality, x.property _ _ (f.monotone h)]⟩

@[simp] theorem onLimit_apply (f : ReindexedMap X Y) (x : X.Point) (n : ℕ) :
    (f.onLimit x).val n = f.app n (x.val (f.level n)) := rfl

@[simp] theorem onLimit_id (x : X.Point) : (id X).onLimit x = x := rfl

@[simp] theorem onLimit_comp (f : ReindexedMap X Y) (g : ReindexedMap Y Z)
    (x : X.Point) : (comp f g).onLimit x = g.onLimit (f.onLimit x) := rfl

@[simp] theorem onLimit_ofMap (f : Map X Y) (x : X.Point) :
    (ofMap f).onLimit x = f.onLimit x := rfl

theorem onLimit_congr {f g : ReindexedMap X Y} (h : EventuallyEq f g) :
    f.onLimit = g.onLimit := by
  funext x
  apply Point.ext
  intro n
  obtain ⟨k, hf, hg, hk⟩ := h n
  have hx := hk (x.val k)
  rw [x.property _ _ hf, x.property _ _ hg] at hx
  exact hx

end ReindexedMap
end Resolution
end KomorebiSpace
