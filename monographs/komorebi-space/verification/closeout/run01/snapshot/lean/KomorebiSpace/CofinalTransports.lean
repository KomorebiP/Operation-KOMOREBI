import KomorebiSpace.EventualCategory
import Mathlib.Data.Nat.Find

set_option autoImplicit false

/-!
# Cofinal schedules are isomorphisms of the eventual transport category

The forward and inverse representatives are explicit. Inverse laws hold by
finite-stage eventual agreement and do not appeal to faithfulness of realization.
-/

universe u v
namespace KomorebiSpace
namespace Resolution
open CategoryTheory

/-- Least sampled input stage reaching a requested original level. -/
noncomputable def ceilingIndex {φ : ℕ → ℕ} (hcof : UnboundedSchedule φ)
    (n : ℕ) : ℕ := Nat.find (hcof n)

theorem ceilingIndex_spec {φ : ℕ → ℕ} (hcof : UnboundedSchedule φ) (n : ℕ) :
    n ≤ φ (ceilingIndex hcof n) := Nat.find_spec (hcof n)

theorem ceilingIndex_monotone {φ : ℕ → ℕ} (hcof : UnboundedSchedule φ) :
    Monotone (ceilingIndex hcof) := by
  intro i j hij
  exact Nat.find_min' (hcof i) (hij.trans (ceilingIndex_spec hcof j))

def sampleTransport (X : Resolution.{u}) (φ : ℕ → ℕ) (hφ : Monotone φ) :
    ReindexedMap X (X.reindex φ hφ) where
  level := φ
  monotone := hφ
  app := fun _ x => x
  naturality := by intros; rfl

noncomputable def recoverTransport (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    ReindexedMap (X.reindex φ hφ) X where
  level := ceilingIndex hcof
  monotone := ceilingIndex_monotone hcof
  app := fun n x => X.restrict (ceilingIndex_spec hcof n) x
  naturality := by
    intro i j hij x
    change X.restrict hij (X.restrict (ceilingIndex_spec hcof j) x) =
      X.restrict (ceilingIndex_spec hcof i)
        (X.restrict (hφ (ceilingIndex_monotone hcof hij)) x)
    exact (X.restrict_trans hij (ceilingIndex_spec hcof j) x).trans
      (X.restrict_trans (ceilingIndex_spec hcof i)
        (hφ (ceilingIndex_monotone hcof hij)) x).symm

theorem sample_recover_eventually (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    ReindexedMap.EventuallyEq
      ((sampleTransport X φ hφ).comp (recoverTransport X φ hφ hcof))
      (ReindexedMap.id X) := by
  intro n
  refine ⟨φ (ceilingIndex hcof n), le_refl _, ceilingIndex_spec hcof n, ?_⟩
  intro x
  change X.restrict (ceilingIndex_spec hcof n) (X.restrict (le_refl _) x) =
    X.restrict (ceilingIndex_spec hcof n) x
  rw [X.restrict_refl]

theorem recover_sample_eventually (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    ReindexedMap.EventuallyEq
      ((recoverTransport X φ hφ hcof).comp (sampleTransport X φ hφ))
      (ReindexedMap.id (X.reindex φ hφ)) := by
  intro n
  refine ⟨max (ceilingIndex hcof (φ n)) n,
    Nat.le_max_left _ _, Nat.le_max_right _ _, ?_⟩
  intro x
  change X.restrict (ceilingIndex_spec hcof (φ n))
    (X.restrict (hφ (Nat.le_max_left _ _)) x) =
    X.restrict (hφ (Nat.le_max_right _ _)) x
  exact X.restrict_trans (ceilingIndex_spec hcof (φ n))
    (hφ (Nat.le_max_left _ _)) x

/-- Actual isomorphism in the newly defined category of eventual transports. -/
noncomputable def cofinalIso (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    X ≅ X.reindex φ hφ where
  hom := EventualHom.mk (sampleTransport X φ hφ)
  inv := EventualHom.mk (recoverTransport X φ hφ hcof)
  hom_inv_id := Quotient.sound (sample_recover_eventually X φ hφ hcof)
  inv_hom_id := Quotient.sound (recover_sample_eventually X φ hφ hcof)

@[simp] theorem sampleTransport_onLimit (X : Resolution.{u})
    (φ : ℕ → ℕ) (hφ : Monotone φ) :
    (sampleTransport X φ hφ).onLimit = sample X φ hφ := rfl

theorem recoverTransport_onLimit (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    (recoverTransport X φ hφ hcof).onLimit = extend X φ hφ hcof := by
  funext x
  apply Point.ext
  intro n
  exact (recoveredCoordinate_eq X φ hφ hcof x n (ceilingIndex hcof n)
    (ceilingIndex_spec hcof n)).symm

/-- The new categorical equivalence realizes the previous concrete sampling map. -/
@[simp] theorem cofinalIso_hom_onLimit (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    (cofinalIso X φ hφ hcof).hom.onLimit = cofinalEquiv X φ hφ hcof := rfl

theorem cofinalIso_inv_onLimit (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    (cofinalIso X φ hφ hcof).inv.onLimit = (cofinalEquiv X φ hφ hcof).symm :=
  recoverTransport_onLimit X φ hφ hcof

/-- Hom-set equivalence, not only point equivalence, under independent schedules. -/
noncomputable def cofinalHomEquiv (X Y : Resolution.{u})
    (φ ψ : ℕ → ℕ) (hφ : Monotone φ) (hψ : Monotone ψ)
    (hφcof : UnboundedSchedule φ) (hψcof : UnboundedSchedule ψ) :
    (X ⟶ Y) ≃ (X.reindex φ hφ ⟶ Y.reindex ψ hψ) where
  toFun := fun f => (cofinalIso X φ hφ hφcof).inv ≫ f ≫
    (cofinalIso Y ψ hψ hψcof).hom
  invFun := fun f => (cofinalIso X φ hφ hφcof).hom ≫ f ≫
    (cofinalIso Y ψ hψ hψcof).inv
  left_inv := by intro f; simp [Category.assoc]
  right_inv := by intro f; simp [Category.assoc]

theorem cofinalHomEquiv_onLimit (X Y : Resolution.{u})
    (φ ψ : ℕ → ℕ) (hφ : Monotone φ) (hψ : Monotone ψ)
    (hφcof : UnboundedSchedule φ) (hψcof : UnboundedSchedule ψ)
    (f : X ⟶ Y) (x : (X.reindex φ hφ).Point) :
    (cofinalHomEquiv X Y φ ψ hφ hψ hφcof hψcof f).onLimit x =
    cofinalEquiv Y ψ hψ hψcof
      (f.onLimit ((cofinalEquiv X φ hφ hφcof).symm x)) := by
  change EventualHom.onLimit
    (EventualHom.comp (cofinalIso X φ hφ hφcof).inv
      (EventualHom.comp f (cofinalIso Y ψ hψ hψcof).hom)) x = _
  simp only [EventualHom.onLimit_comp, cofinalIso_inv_onLimit, cofinalIso_hom_onLimit]

namespace Map
variable {X Y : Resolution.{u}}

@[ext] theorem ext {f g : Map X Y} (h : ∀ n x, f.app n x = g.app n x) : f = g := by
  cases f with
  | mk f hf => cases g with
    | mk g hg =>
      have hfg : f = g := by
        cases f; cases g
        congr
        funext n x
        exact h n x
      cases hfg
      rfl

def sample (f : Map X Y) (φ : ℕ → ℕ) (hφ : Monotone φ) :
    Map (X.reindex φ hφ) (Y.reindex φ hφ) where
  app := fun n => f.app (φ n)
  exact := fun i j h x => f.exact (φ i) (φ j) (hφ h) x

@[simp] theorem sample_onLimit (f : Map X Y) (φ : ℕ → ℕ) (hφ : Monotone φ)
    (x : X.Point) :
    (sample f φ hφ).onLimit (Resolution.sample X φ hφ x) =
    Resolution.sample Y φ hφ (f.onLimit x) := rfl

theorem sample_square (f : Map X Y) (φ : ℕ → ℕ) (hφ : Monotone φ)
    (hcof : UnboundedSchedule φ) :
    EventualHom.ofMap f ≫ (cofinalIso Y φ hφ hcof).hom =
    (cofinalIso X φ hφ hcof).hom ≫ EventualHom.ofMap (sample f φ hφ) := rfl

theorem sample_class (f : Map X Y) (φ : ℕ → ℕ) (hφ : Monotone φ)
    (hcof : UnboundedSchedule φ) :
    cofinalHomEquiv X Y φ φ hφ hφ hcof hcof (EventualHom.ofMap f) =
    EventualHom.ofMap (sample f φ hφ) := by
  change (cofinalIso X φ hφ hcof).inv ≫
    (EventualHom.ofMap f ≫ (cofinalIso Y φ hφ hcof).hom) = _
  rw [sample_square f φ hφ hcof]
  simp

end Map

end Resolution
end KomorebiSpace
