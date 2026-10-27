import KomorebiSpace.ObstructionRestriction
import KomorebiSpace.SectionExtensionStages
import Mathlib.CategoryTheory.Category.Preorder
import Mathlib.Order.Fin.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# Nonzero initial data, many global extensions, and a dead-end intermediate choice

The views are 0 -> 1 -> 2 with fibers Z x Z. Restriction into 0 forgets
the second coordinate. Restriction from 2 to 1 doubles it. A fixed initial
value (k,0) has Z-many global extensions, but the intermediate second value
must be even. This is stated in the actual section and obstruction objects.
-/
namespace KomorebiSpace
open CategoryTheory
namespace ExtensionChoiceExample

abbrev Pair := ℤ × ℤ

def forgetTail : Pair →+ Pair where
  toFun x := (x.1,0)
  map_zero' := rfl
  map_add' := by intro x y; rfl

def doubleTail : Pair →+ Pair where
  toFun x := (x.1,2*x.2)
  map_zero' := by simp
  map_add' := by intro x y; ext <;> simp [mul_add]

def threeViews : AdditiveViewSystem (Fin 3) (fun _ => Pair) where
  pull := fun {a b} _ =>
    if a = b then AddMonoidHom.id Pair else if a = 0 then forgetTail else doubleTail
  pull_id := by intro a x; simp
  pull_comp := by
    intro a b c f g x
    have hab := leOfHom f
    have hbc := leOfHom g
    fin_cases a <;> fin_cases b <;> fin_cases c
    all_goals simp_all [forgetTail,doubleTail]

def initialDomain : Set (Fin 3) := {0}
def middleDomain : Set (Fin 3) := {0,1}

theorem initial_subset_middle : initialDomain ⊆ middleDomain := by
  intro a ha
  exact Or.inl ha

def initialSeed (k : ℤ) : threeViews.views.Partial initialDomain :=
  ⟨fun _ => (k,0),by
    intro a b f
    have ha : a.val = 0 := a.property
    have hb : b.val = 0 := b.property
    change (if a.val = b.val then AddMonoidHom.id Pair else
      if a.val = 0 then forgetTail else doubleTail) (k,0) = (k,0)
    simp [ha,hb]⟩

def middleSeed (k m : ℤ) : threeViews.views.Partial middleDomain :=
  ⟨fun a => (k, if a.val = 0 then 0 else m),by
    rintro ⟨a,ha⟩ ⟨b,hb⟩ f
    have hab := leOfHom f
    change a = 0 ∨ a = 1 at ha
    change b = 0 ∨ b = 1 at hb
    rcases ha with rfl | rfl <;> rcases hb with rfl | rfl
    all_goals simp_all [AdditiveViewSystem.views,threeViews,forgetTail,doubleTail]⟩

def globalSection (k n : ℤ) : threeViews.views.Ambient :=
  ⟨fun a => (k,if a = 0 then 0 else if a = 1 then 2*n else n),by
    intro a b f
    have hab := leOfHom f
    fin_cases a <;> fin_cases b
    all_goals simp_all [AdditiveViewSystem.views,threeViews,forgetTail,doubleTail]⟩

@[simp] theorem globalSection_zero (k n : ℤ) : (globalSection k n).val 0 = (k,0) := rfl
@[simp] theorem globalSection_one (k n : ℤ) : (globalSection k n).val 1 = (k,2*n) := rfl
@[simp] theorem globalSection_two (k n : ℤ) : (globalSection k n).val 2 = (k,n) := rfl

theorem global_restrict_initial (k n : ℤ) :
    threeViews.views.restrict initialDomain (globalSection k n) = initialSeed k := by
  apply ViewSystem.Partial.ext
  intro a
  have ha : a.val = 0 := a.property
  change (k,if a.val = 0 then 0 else if a.val = 1 then 2*n else n) = (k,0)
  simp [ha]

theorem global_restrict_middle (k n : ℤ) :
    threeViews.views.restrict middleDomain (globalSection k n) = middleSeed k (2*n) := by
  apply ViewSystem.Partial.ext
  rintro ⟨a,ha⟩
  change a = 0 ∨ a = 1 at ha
  rcases ha with rfl | rfl <;> rfl

theorem middle_restrict_initial (k m : ℤ) :
    threeViews.views.restrictPartial initial_subset_middle (middleSeed k m) = initialSeed k := by
  apply ViewSystem.Partial.ext
  intro a
  have ha : a.val = 0 := a.property
  change (k,if a.val = 0 then 0 else m) = (k,0)
  simp [ha]

/-- Every initial seed extends, including nonzero ones. -/
theorem initial_extends (k : ℤ) :
    Nonempty (threeViews.views.Extensions initialDomain (initialSeed k)) :=
  ⟨⟨globalSection k 0,global_restrict_initial k 0⟩⟩

/-- The intermediate choice obeys a genuine parity obstruction. -/
theorem middle_obstruction_iff_even (k m : ℤ) :
    threeViews.extensionClass middleDomain (middleSeed k m) = 0 ↔
      ∃ n : ℤ, m = 2*n := by
  rw [threeViews.extensionClass_zero_iff]
  constructor
  · rintro ⟨⟨x,hx⟩⟩
    have hv : x.val 1 = (k,m) :=
      congrArg (fun t : threeViews.views.Partial middleDomain => t.val ⟨1,Or.inr rfl⟩) hx
    have hc := x.property 1 2 (homOfLE (by decide))
    change doubleTail (show Pair from x.val 2) = x.val 1 at hc
    have hh := congrArg Prod.snd (hc.trans hv)
    exact ⟨(x.val 2).2,hh.symm⟩
  · rintro ⟨n,rfl⟩
    exact ⟨⟨globalSection k n,global_restrict_middle k n⟩⟩

theorem odd_middle_obstructed (k : ℤ) :
    threeViews.extensionClass middleDomain (middleSeed k 1) ≠ 0 := by
  intro h
  obtain ⟨n,hn⟩ := (middle_obstruction_iff_even k 1).mp h
  omega

/-- Restricting the obstructed middle choice loses its obstruction. -/
theorem obstruction_forgotten (k : ℤ) :
    threeViews.forgetObstruction initial_subset_middle
      (threeViews.extensionClass middleDomain (middleSeed k 1)) = 0 := by
  rw [threeViews.extensionClass_restrict,middle_restrict_initial]
  exact (threeViews.extensionClass_zero_iff _ _).mpr (initial_extends k)

theorem forgetting_not_injective :
    ¬ Function.Injective (threeViews.forgetObstruction initial_subset_middle) := by
  intro hinj
  apply odd_middle_obstructed 7
  apply hinj
  rw [obstruction_forgotten,map_zero]

/-- Every completion of the initial seed has the displayed formula. -/
theorem initial_extension_formula (k : ℤ)
    (x : threeViews.views.Extensions initialDomain (initialSeed k)) :
    x.val = globalSection k (x.val.val 2).2 := by
  have h0 : x.val.val 0 = (k,0) :=
    congrArg (fun t : threeViews.views.Partial initialDomain => t.val ⟨0,rfl⟩) x.property
  have h02 := x.val.property 0 2 (homOfLE (by decide))
  change forgetTail (show Pair from x.val.val 2) = x.val.val 0 at h02
  have hfirst : (x.val.val 2).1 = k := congrArg Prod.fst (h02.trans h0)
  have h12 := x.val.property 1 2 (homOfLE (by decide))
  change doubleTail (show Pair from x.val.val 2) = x.val.val 1 at h12
  apply ViewSystem.Ambient.ext
  intro a
  fin_cases a
  · exact h0
  · change x.val.val 1 = (k,2*(x.val.val 2).2)
    exact h12.symm.trans (Prod.ext hfirst rfl)
  · change x.val.val 2 = (k,(x.val.val 2).2)
    exact Prod.ext hfirst rfl

/-- An explicit infinite family of completions of each fixed initial seed. -/
def initialExtensionsEquiv (k : ℤ) :
    ℤ ≃ threeViews.views.Extensions initialDomain (initialSeed k) where
  toFun n := ⟨globalSection k n,global_restrict_initial k n⟩
  invFun x := (x.val.val 2).2
  left_inv _ := rfl
  right_inv x := Subtype.ext (initial_extension_formula k x).symm

@[simp] theorem initialExtensions_parameter (k n : ℤ) :
    ((initialExtensionsEquiv k n).val.val 2).2 = n := rfl

theorem initial_extensions_not_unique (k : ℤ) :
    ¬ Subsingleton (threeViews.views.Extensions initialDomain (initialSeed k)) := by
  intro hs
  have he := (initialExtensionsEquiv k).injective
    (hs.elim (initialExtensionsEquiv k 0) (initialExtensionsEquiv k 1))
  norm_num at he

/-- A nonzero initial value extends, but a coherent intermediate choice can fail. -/
theorem nonzero_seed_dead_end :
    Nonempty (threeViews.views.Extensions initialDomain (initialSeed 7)) ∧
    threeViews.views.restrictPartial initial_subset_middle (middleSeed 7 1) = initialSeed 7 ∧
    ¬ Nonempty (threeViews.views.Extensions middleDomain (middleSeed 7 1)) := by
  refine ⟨initial_extends 7,middle_restrict_initial 7 1,?_⟩
  intro h
  exact odd_middle_obstructed 7 ((threeViews.extensionClass_zero_iff _ _).mpr h)

end ExtensionChoiceExample
end KomorebiSpace
