import KomorebiSpace.EventualCategory

set_option autoImplicit false

/-!
# When realized functions determine eventual transports

Surjectivity of all limit projections is sufficient. It is proved from
surjective adjacent bonding maps by an explicit choice-and-recursion lift.
-/

universe u v
namespace KomorebiSpace
namespace Resolution

/-- Every finite input state is the coordinate of a coherent global input. -/
def ProjectionSurjective (X : Resolution.{u}) : Prop :=
  ∀ n, Function.Surjective (fun x : X.Point => x.val n)

namespace ReindexedMap
variable {X : Resolution.{u}} {Y : Resolution.{v}}

theorem eventuallyEq_of_onLimit_eq (hX : ProjectionSurjective X)
    (f g : ReindexedMap X Y) (hfg : f.onLimit = g.onLimit) :
    EventuallyEq f g := by
  intro n
  let k := max (f.level n) (g.level n)
  refine ⟨k, Nat.le_max_left _ _, Nat.le_max_right _ _, ?_⟩
  intro a
  obtain ⟨x, hx⟩ := hX k a
  change x.val k = a at hx
  have hh := congrArg (fun F : X.Point → Y.Point => (F x).val n) hfg
  change f.app n (x.val (f.level n)) = g.app n (x.val (g.level n)) at hh
  have hxf := x.property (f.level n) k (Nat.le_max_left _ _)
  have hxg := x.property (g.level n) k (Nat.le_max_right _ _)
  rw [hx] at hxf hxg
  exact (congrArg (f.app n) hxf).trans (hh.trans (congrArg (g.app n) hxg).symm)

theorem eventuallyEq_iff_onLimit_eq (hX : ProjectionSurjective X)
    (f g : ReindexedMap X Y) : EventuallyEq f g ↔ f.onLimit = g.onLimit :=
  ⟨onLimit_congr, eventuallyEq_of_onLimit_eq hX f g⟩

end ReindexedMap

namespace EventualHom
variable {X : Resolution.{u}} {Y : Resolution.{v}}

theorem onLimit_injective (hX : ProjectionSurjective X) :
    Function.Injective (onLimit (X := X) (Y := Y)) := by
  intro f g hfg
  induction f using Quotient.inductionOn with
  | _ f => induction g using Quotient.inductionOn with
    | _ g => exact Quotient.sound (ReindexedMap.eventuallyEq_of_onLimit_eq hX f g hfg)

theorem eq_iff_onLimit_eq (hX : ProjectionSurjective X) (f g : EventualHom X Y) :
    f = g ↔ f.onLimit = g.onLimit :=
  ⟨fun h => congrArg onLimit h, fun h => onLimit_injective (X := X) (Y := Y) hX h⟩

end EventualHom

variable (X : Resolution.{u})

theorem coherent_of_adjacent (x : ∀ n, X.Obj n)
    (hx : ∀ n, X.restrict (Nat.le_succ n) (x (n+1)) = x n)
    {i j : ℕ} (h : i ≤ j) : X.restrict h (x j) = x i := by
  induction j, h using Nat.le_induction with
  | base => exact X.restrict_refl i (x i)
  | succ j hj ih =>
    exact (X.restrict_trans hj (Nat.le_succ j) (x (j+1))).symm.trans
      ((congrArg (X.restrict hj) (hx j)).trans ih)

variable (up : ∀ n, X.Obj n → X.Obj (n+1))
    (hup : ∀ n x, X.restrict (Nat.le_succ n) (up n x) = x)

def seededSequence (k : ℕ) (seed : X.Obj k) : ∀ n, X.Obj n
  | 0 => X.restrict (Nat.zero_le k) seed
  | n+1 => if h : n+1 ≤ k then X.restrict h seed else up n (seededSequence k seed n)

theorem seededSequence_below (k n : ℕ) (seed : X.Obj k) (h : n ≤ k) :
    seededSequence X up k seed n = X.restrict h seed := by
  cases n with
  | zero => rfl
  | succ n => simp only [seededSequence, dite_eq_left h]

include hup in
theorem seededSequence_coherent (k : ℕ) (seed : X.Obj k) (n : ℕ) :
    X.restrict (Nat.le_succ n) (seededSequence X up k seed (n+1)) =
    seededSequence X up k seed n := by
  by_cases hn : n+1 ≤ k
  · have hn' : n ≤ k := (Nat.le_succ n).trans hn
    rw [seededSequence_below X up k (n+1) seed hn,
      seededSequence_below X up k n seed hn']
    exact X.restrict_trans (Nat.le_succ n) hn seed
  · rw [seededSequence, dite_eq_right hn]
    exact hup n _

def seededPoint (k : ℕ) (seed : X.Obj k) : X.Point :=
  ⟨seededSequence X up k seed, fun _ _ h =>
    coherent_of_adjacent X _ (seededSequence_coherent X up hup k seed) h⟩

@[simp] theorem seededPoint_at_seed (k : ℕ) (seed : X.Obj k) :
    (seededPoint X up hup k seed).val k = seed :=
  (seededSequence_below X up k k seed (Nat.le_refl k)).trans (X.restrict_refl k seed)

include up hup in
theorem projectionSurjective_of_sections : ProjectionSurjective X := by
  intro k seed
  exact ⟨seededPoint X up hup k seed, seededPoint_at_seed X up hup k seed⟩

theorem projectionSurjective_of_surjective_bonding
    (hsurj : ∀ n, Function.Surjective (X.restrict (Nat.le_succ n))) :
    ProjectionSurjective X := by
  classical
  let lift : ∀ n, X.Obj n → X.Obj (n+1) :=
    fun n x => Classical.choose (hsurj n x)
  have hlift : ∀ n x, X.restrict (Nat.le_succ n) (lift n x) = x :=
    fun n x => Classical.choose_spec (hsurj n x)
  exact projectionSurjective_of_sections X lift hlift

end Resolution
end KomorebiSpace
