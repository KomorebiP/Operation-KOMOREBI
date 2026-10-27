import KomorebiSpace.ViewPullback

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false

/-!
# Invariance of the cocycle groupoid under equivalence of view categories

The forward functor is actual pullback. The inverse transports coefficients
along the inverse counit; no coefficient groups are identified by fiat.
-/
universe u₁ u₂ v₁ v₂ w
namespace KomorebiSpace
open CategoryTheory
namespace GroupViewSystem
variable {V : Type u₁} [Category.{v₁} V]
variable {W : Type u₂} [Category.{v₂} W]
variable {G : W → Type w} [∀ a, Group (G a)]
variable (F : GroupViewSystem W G) (e : V ≌ W)

/-- The inverse counit supplies the comparison arrow with explicit endpoints. -/
abbrev returnArrow (a : W) : a ⟶ e.functor.obj (e.inverse.obj a) :=
  e.counitIso.inv.app a

/-- Naturality, with coefficient transport written out. -/
theorem return_pull_natural {a b : W} (f : a ⟶ b)
    (x : G (e.functor.obj (e.inverse.obj b))) :
    F.pull (returnArrow e a) (F.pull (e.functor.map (e.inverse.map f)) x) =
      F.pull f (F.pull (returnArrow e b) x) := by
  rw [← F.pull_comp, ← F.pull_comp]
  exact congrArg (fun k => F.pull k x) (e.counitIso.inv.naturality f).symm

/-- Extend a pulled-back cocycle using the supplied categorical equivalence. -/
def returnCocycle (c : (F.reindex e.functor).Cocycle) : F.Cocycle where
  edge := fun {a b} f => F.pull (returnArrow e a) (c.edge (e.inverse.map f))
  edge_id := by intro a; rw [e.inverse.map_id, c.edge_id, map_one]
  edge_comp := by
    intro a b z f g
    rw [e.inverse.map_comp, c.edge_comp, map_mul]
    congr 1
    exact F.return_pull_natural e f (c.edge (e.inverse.map g))

@[simp] theorem returnCocycle_edge (c : (F.reindex e.functor).Cocycle)
    {a b : W} (f : a ⟶ b) :
    (F.returnCocycle e c).edge f =
      F.pull (returnArrow e a) (c.edge (e.inverse.map f)) := rfl

/-- The inverse also transports gauge witnesses, not just cocycle classes. -/
def returnFunctor : (F.reindex e.functor).GaugeObject ∅ ⥤ F.GaugeObject ∅ where
  obj c := ⟨F.returnCocycle e c.labels⟩
  map := fun {c d} a =>
    { change := ⟨fun v => F.pull (returnArrow e v) (a.change.val (e.inverse.obj v)), by
        intro v; exact False.elim v.property⟩
      target := by
        apply Cocycle.ext
        intro v w f
        have h := congrArg (fun c => c.edge (e.inverse.map f)) a.target
        change a.change.val (e.inverse.obj v) * c.labels.edge (e.inverse.map f) *
          (F.pull (e.functor.map (e.inverse.map f)) (a.change.val (e.inverse.obj w)))⁻¹ =
            d.labels.edge (e.inverse.map f) at h
        change F.pull (returnArrow e v) (a.change.val (e.inverse.obj v)) *
          F.pull (returnArrow e v) (c.labels.edge (e.inverse.map f)) *
          (F.pull f (F.pull (returnArrow e w) (a.change.val (e.inverse.obj w))))⁻¹ = _
        rw [← F.return_pull_natural e f]
        rw [← map_inv, ← map_mul, ← map_mul, h]
        rfl }
  map_id := by
    intro c
    apply GaugeObject.Hom.ext
    apply Subtype.ext
    funext v
    exact map_one _
  map_comp := by
    intro c d k a b
    apply GaugeObject.Hom.ext
    apply Subtype.ext
    funext v
    exact map_mul _ _ _

/-- Comparison of the global round trip to the original cocycle. -/
def globalComparison (c : F.GaugeObject ∅) :
    ((F.reindexFunctor e.functor) ⋙ F.returnFunctor e).obj c ⟶ c where
  change := ⟨fun v => c.labels.edge (returnArrow e v), by
    intro v; exact False.elim v.property⟩
  target := by
    apply Cocycle.ext
    intro a b f
    exact F.natural_comparison (e.inverse ⋙ e.functor) (returnArrow e)
      (fun g => (e.counitIso.inv.naturality g).symm) c.labels f

/-- The global comparison is natural on all gauge arrows. -/
def globalComparisonIso :
    (F.reindexFunctor e.functor) ⋙ F.returnFunctor e ≅ 𝟭 (F.GaugeObject ∅) :=
  NatIso.ofComponents
    (fun c => (Groupoid.isoEquivHom _ _).symm (F.globalComparison e c)) (by
      intro c d a
      apply GaugeObject.Hom.ext
      apply Subtype.ext
      funext v
      exact F.gauge_comparison_naturality a (returnArrow e v))

/-- The triangle law identifies the two actual arrows used in the other round trip. -/
theorem mapped_unit_eq_return (v : V) :
    e.functor.map (e.unitIso.hom.app v) = returnArrow e (e.functor.obj v) := by
  exact (e.counitInv_app_functor v).symm

/-- Comparison of the pulled-back round trip to the starting pulled-back cocycle. -/
def localComparison (c : (F.reindex e.functor).GaugeObject ∅) :
    (F.returnFunctor e ⋙ F.reindexFunctor e.functor).obj c ⟶ c where
  change := ⟨fun v => c.labels.edge (a := v) (e.unitIso.hom.app v), by
    intro v; exact False.elim v.property⟩
  target := by
    apply Cocycle.ext
    intro a b f
    change c.labels.edge (a := a) (e.unitIso.hom.app a) *
      F.pull (returnArrow e (e.functor.obj a)) (c.labels.edge (e.inverse.map (e.functor.map f))) *
      (F.pull (e.functor.map f) (c.labels.edge (a := b) (e.unitIso.hom.app b)))⁻¹ = c.labels.edge f
    rw [← mapped_unit_eq_return e a]
    exact (F.reindex e.functor).natural_comparison (e.functor ⋙ e.inverse)
      (fun v => e.unitIso.hom.app v)
      (fun g => (e.unitIso.hom.naturality g).symm) c.labels f

/-- The local comparison is likewise natural on all arrows. -/
def localComparisonIso :
    F.returnFunctor e ⋙ F.reindexFunctor e.functor ≅
      𝟭 ((F.reindex e.functor).GaugeObject ∅) :=
  NatIso.ofComponents
    (fun c => (Groupoid.isoEquivHom _ _).symm (F.localComparison e c)) (by
      intro c d a
      apply GaugeObject.Hom.ext
      apply Subtype.ext
      funext v
      change d.labels.edge (a := v) (e.unitIso.hom.app v) *
        F.pull (returnArrow e (e.functor.obj v)) (a.change.val (e.inverse.obj (e.functor.obj v))) =
        a.change.val v * c.labels.edge (a := v) (e.unitIso.hom.app v)
      rw [← mapped_unit_eq_return e v]
      exact (F.reindex e.functor).gauge_comparison_naturality a (e.unitIso.hom.app v))

/-- Actual pullback is an equivalence of the existing cocycle gauge groupoids. -/
def reindexEquivalence :
    F.GaugeObject ∅ ≌ (F.reindex e.functor).GaugeObject ∅ :=
  CategoryTheory.Equivalence.mk (F.reindexFunctor e.functor) (F.returnFunctor e)
    (F.globalComparisonIso e).symm (F.localComparisonIso e)

@[simp] theorem reindexEquivalence_functor :
    (F.reindexEquivalence e).functor = F.reindexFunctor e.functor := rfl

/-- Standard equivalence predicate for the concrete pullback functor. -/
theorem reindex_isEquivalence : (F.reindexFunctor e.functor).IsEquivalence := by
  change (F.reindexEquivalence e).functor.IsEquivalence
  infer_instance

/-- Every Hom set, in particular every automorphism set, is retained. -/
def reindexHomEquiv (c d : F.GaugeObject ∅) :
    (c ⟶ d) ≃ ((F.reindexFunctor e.functor).obj c ⟶
      (F.reindexFunctor e.functor).obj d) :=
  (F.reindexEquivalence e).fullyFaithfulFunctor.homEquiv

/-- The equivalence uses the actual pullback of gauge witnesses. -/
@[simp] theorem reindexHomEquiv_apply (c d : F.GaugeObject ∅) (a : c ⟶ d) :
    F.reindexHomEquiv e c d a = (F.reindexFunctor e.functor).map a := rfl

/-- Isomorphism-class equality is both preserved and reflected. -/
theorem reindex_class_eq_iff (c d : F.Cocycle) :
    (F.reindex e.functor).orbitClass ∅ (F.reindexCocycle e.functor c) =
      (F.reindex e.functor).orbitClass ∅ (F.reindexCocycle e.functor d) ↔
    F.orbitClass ∅ c = F.orbitClass ∅ d := by
  change (F.reindex e.functor).orbitClass ∅ ((F.reindexFunctor e.functor).obj ⟨c⟩).labels =
      (F.reindex e.functor).orbitClass ∅ ((F.reindexFunctor e.functor).obj ⟨d⟩).labels ↔ _
  rw [← (F.reindex e.functor).morphism_nonempty_iff_class,
      ← F.morphism_nonempty_iff_class ∅ (⟨c⟩ : F.GaugeObject ∅) (⟨d⟩ : F.GaugeObject ∅)]
  exact (F.reindexHomEquiv e ⟨c⟩ ⟨d⟩).nonempty_congr.symm

/-- Changing to an equivalent view category does not erase an unframed obstruction. -/
theorem reindex_neutral_iff (c : F.Cocycle) :
    (F.reindex e.functor).orbitClass ∅ (F.reindexCocycle e.functor c) =
      (F.reindex e.functor).neutralClass ∅ ↔
    F.orbitClass ∅ c = F.neutralClass ∅ :=
  F.reindex_class_eq_iff e c F.trivial

end GroupViewSystem
end KomorebiSpace
