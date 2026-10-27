import KomorebiSpace.ViewDuplication

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Literal full framing is not invariant under duplicated views

This is a counterexample using the actual old based-gauge groupoid. Both
framing domains are the whole view category, hence saturated. Duplicating
isomorphic representatives introduces separate frozen trivializations. The
resulting pullback functor need not be full. Identified-boundary fibers do
not freeze these redundant choices independently.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem W G)

/-- Pullback exists for all framing domains, but is not always an equivalence. -/
def reindexFramedFunctor (H : V ⥤ W) (U : Set W) :
    F.GaugeObject U ⥤ (F.reindex H).GaugeObject (H.obj ⁻¹' U) where
  obj c := ⟨F.reindexCocycle H c.labels⟩
  map a :=
    { change := ⟨fun v => a.change.val (H.obj v),
        fun v => a.change.property ⟨H.obj v.val,v.property⟩⟩
      target := by
        apply Cocycle.ext
        intro v w f
        exact congrArg (fun c => c.edge (H.map f)) a.target }
  map_id := by intro c; rfl
  map_comp := by intro c d k a b; rfl

/-- Freezing every view forces every allowed gauge to be pointwise identity. -/
theorem fully_framed_gauge (a : F.basedGauge Set.univ) : a.val = 1 := by
  funext v
  exact a.property ⟨v,Set.mem_univ v⟩

theorem fully_framed_equivalent_iff (c d : F.Cocycle) :
    F.GaugeEquivalent Set.univ c d ↔ c = d := by
  constructor
  · rintro ⟨a,ha⟩
    rw [F.fully_framed_gauge a, F.gauge_one] at ha
    exact ha
  · intro h
    exact ⟨1, (F.gauge_one c).trans h⟩

end GroupViewSystem

namespace FramingBoundaryExamples
variable (V : Type u₁) [Category.{v₁} V]
variable {H : Type w} [Group H]

/-- Give the redundant copy a different trivialization. -/
def copyFrame (g : H) : ViewDuplication.Duplicated V → H :=
  fun x => if x.2 then g else 1

def copyCocycle (g : H) : (ViewDuplication.constantGroups V H).Cocycle :=
  (ViewDuplication.constantGroups V H).gauge (copyFrame V g)
    (ViewDuplication.constantGroups V H).trivial

/-- This is not a change in the gauge orbit, but it is a change of strict cocycle labels. -/
theorem copyCocycle_ne_trivial (v : V) (g : H) (hg : g ≠ 1) :
    copyCocycle V g ≠ (ViewDuplication.constantGroups V H).trivial := by
  intro h
  have he := congrArg (fun c => c.edge (ViewDuplication.copyIso V v true false).hom) h
  change g * 1 * (1 : H)⁻¹ = 1 at he
  exact hg (by simpa using he)

/-- Choosing the representative copy forgets those extra trivializations. -/
@[simp] theorem copyCocycle_pullback (g : H) :
    (ViewDuplication.constantGroups V H).reindexCocycle (ViewDuplication.embed V)
      (copyCocycle V g) =
    ((ViewDuplication.constantGroups V H).reindex (ViewDuplication.embed V)).trivial := by
  apply GroupViewSystem.Cocycle.ext
  intro v w f
  change (1 : H) * 1 * 1⁻¹ = 1
  simp

/-- Both framing domains in the counterexample are saturated. -/
theorem full_domain_isoClosed : CompositionSite.IsoClosed (Set.univ : Set (ViewDuplication.Duplicated V)) := by
  intro a b i ha
  exact Set.mem_univ b

/-- Distinct fully framed cocycles acquire an arrow after pullback along an equivalence. -/
theorem full_framing_not_full (v : V) (g : H) (hg : g ≠ 1) :
    ¬ ((ViewDuplication.constantGroups V H).reindexFramedFunctor
      (ViewDuplication.embed V) Set.univ).Full := by
  let F := ViewDuplication.constantGroups V H
  let P := F.reindexFramedFunctor (ViewDuplication.embed V) Set.univ
  let c : F.GaugeObject Set.univ := ⟨copyCocycle V g⟩
  let d : F.GaugeObject Set.univ := ⟨F.trivial⟩
  have he : F.reindexCocycle (ViewDuplication.embed V) c.labels =
      F.reindexCocycle (ViewDuplication.embed V) d.labels := by
    exact copyCocycle_pullback V g
  let a : P.obj c ⟶ P.obj d :=
    ⟨1, by
      change (F.reindex (ViewDuplication.embed V)).gauge 1
        (F.reindexCocycle (ViewDuplication.embed V) c.labels) =
        F.reindexCocycle (ViewDuplication.embed V) d.labels
      rw [(F.reindex (ViewDuplication.embed V)).gauge_one]
      exact he⟩
  intro hf
  let : P.Full := hf
  let k : c ⟶ d := P.preimage a
  have hk : F.GaugeEquivalent Set.univ c.labels d.labels := ⟨k.change,k.target⟩
  have eqc := (F.fully_framed_equivalent_iff c.labels d.labels).mp hk
  exact copyCocycle_ne_trivial V v g hg eqc

/-- In particular the actual fully framed pullback is not an equivalence. -/
theorem full_framing_not_equivalence (v : V) (g : H) (hg : g ≠ 1) :
    ¬ ((ViewDuplication.constantGroups V H).reindexFramedFunctor
      (ViewDuplication.embed V) Set.univ).IsEquivalence := by
  intro h
  let := h
  exact full_framing_not_full V v g hg inferInstance

end FramingBoundaryExamples
end KomorebiSpace
