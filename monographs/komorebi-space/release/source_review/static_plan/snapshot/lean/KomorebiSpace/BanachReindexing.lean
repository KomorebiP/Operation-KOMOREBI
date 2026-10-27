import KomorebiSpace.AdjacentResolution
import KomorebiSpace.CofinalTransports
import KomorebiSpace.FiniteObservation
import KomorebiSpace.SplitTowerRepair

set_option autoImplicit false

/-!
# Actual Banach tower repairs enter the cofinal transport category

This is a forgetful bridge: all bonding functions and coordinate actions are
preserved, but no invariance of sup norms, operator bounds, or residual norms
under resampling is asserted.
-/

universe u v
noncomputable section
namespace KomorebiSpace
namespace BanachTower
open CategoryTheory
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)

def underlyingResolution : Resolution.{v} :=
  Resolution.Adjacent.resolution X.Obj (fun n => X.down n)

def resolutionPointEquiv : X.Point ≃ X.underlyingResolution.Point :=
  Resolution.Adjacent.pointEquiv X.Obj (fun n => X.down n)

@[simp] theorem resolutionPointEquiv_coordinate (x : X.Point) (n : ℕ) :
    (X.resolutionPointEquiv x).val n = x.val n := rfl

def exactResolutionMap (f : Candidates X Y) (hf : Exact X Y f) :
    Resolution.Map X.underlyingResolution Y.underlyingResolution :=
  Resolution.Adjacent.map (fun n => f n) (fun n x =>
    congrArg (fun T : X.Obj (n+1) →L[𝕜] Y.Obj n => T x) (hf n))

def exactEventualHom (f : Candidates X Y) (hf : Exact X Y f) :
    X.underlyingResolution ⟶ Y.underlyingResolution :=
  Resolution.EventualHom.ofMap (exactResolutionMap X Y f hf)

/-- Agreement with the already proved analytic-tower realization, coordinate by coordinate. -/
theorem exactEventualHom_onLimit (f : Candidates X Y) (hf : Exact X Y f)
    (x : X.Point) :
    (exactEventualHom X Y f hf).onLimit (X.resolutionPointEquiv x) =
    Y.resolutionPointEquiv (onLimit X Y f hf x) := rfl

variable (φ ψ : ℕ → ℕ) (hφ : Monotone φ) (hψ : Monotone ψ)
    (hφcof : Resolution.UnboundedSchedule φ) (hψcof : Resolution.UnboundedSchedule ψ)

/-- The underlying exact transport class on independently resampled presentations. -/
def sampledExactHom (f : Candidates X Y) (hf : Exact X Y f) :
    X.underlyingResolution.reindex φ hφ ⟶ Y.underlyingResolution.reindex ψ hψ :=
  Resolution.cofinalHomEquiv X.underlyingResolution Y.underlyingResolution
    φ ψ hφ hψ hφcof hψcof (exactEventualHom X Y f hf)

theorem sampledExactHom_onLimit (f : Candidates X Y) (hf : Exact X Y f)
    (x : (X.underlyingResolution.reindex φ hφ).Point) :
    (sampledExactHom X Y φ ψ hφ hψ hφcof hψcof f hf).onLimit x =
    Resolution.cofinalEquiv Y.underlyingResolution ψ hψ hψcof
      ((exactEventualHom X Y f hf).onLimit
        ((Resolution.cofinalEquiv X.underlyingResolution φ hφ hφcof).symm x)) :=
  Resolution.cofinalHomEquiv_onLimit X.underlyingResolution Y.underlyingResolution
    φ ψ hφ hψ hφcof hψcof (exactEventualHom X Y f hf) x

/-- A transparent output-coordinate statement of the preceding conjugacy. -/
theorem sampledExactHom_coordinate (f : Candidates X Y) (hf : Exact X Y f)
    (x : (X.underlyingResolution.reindex φ hφ).Point) (n : ℕ) :
    ((sampledExactHom X Y φ ψ hφ hψ hφcof hψcof f hf).onLimit x).val n =
    f (ψ n) (((Resolution.cofinalEquiv X.underlyingResolution φ hφ hφcof).symm x).val
      (ψ n)) := by
  rw [sampledExactHom_onLimit]
  rfl

/-- Reindexing an already exact repair gives the same realized global action. -/
def sampledRepair (L : Splitting Y) (hgap : (L.bound : ℝ) * X.bound < 1)
    (f : Candidates X Y) :
    X.underlyingResolution.reindex φ hφ ⟶ Y.underlyingResolution.reindex ψ hψ :=
  sampledExactHom X Y φ ψ hφ hψ hφcof hψcof
    (L.repair X hgap f) (L.repair_exact X hgap f)

theorem sampledRepair_coordinate (L : Splitting Y)
    (hgap : (L.bound : ℝ) * X.bound < 1) (f : Candidates X Y)
    (x : (X.underlyingResolution.reindex φ hφ).Point) (n : ℕ) :
    ((sampledRepair X Y φ ψ hφ hψ hφcof hψcof L hgap f).onLimit x).val n =
    (L.repair X hgap f) (ψ n)
      (((Resolution.cofinalEquiv X.underlyingResolution φ hφ hφcof).symm x).val
        (ψ n)) :=
  sampledExactHom_coordinate X Y φ ψ hφ hψ hφcof hψcof
    (L.repair X hgap f) (L.repair_exact X hgap f) x n

/-- Split source bonding maps make every finite input extendible to a coherent input. -/
theorem underlying_projection_surjective (L : Splitting X) :
    X.underlyingResolution.ProjectionSurjective := by
  apply Resolution.projectionSurjective_of_sections X.underlyingResolution (fun n => L.up n)
  intro n x
  have hs := Resolution.Adjacent.restrict_succ X.Obj (fun n => X.down n)
    (Nat.le_refl n) (Nat.le_succ n) (L.up n x)
  have hr := Resolution.Adjacent.restrict_refl X.Obj (fun n => X.down n) n
    (X.down n (L.up n x))
  exact (hs.trans hr).trans (L.down_up_apply n x)

/-- With split source bonding maps, equality of realized functions reflects equality of classes. -/
theorem eventual_eq_iff_realization_eq (L : Splitting X)
    (f g : X.underlyingResolution ⟶ Y.underlyingResolution) :
    f = g ↔ f.onLimit = g.onLimit :=
  Resolution.EventualHom.eq_iff_onLimit_eq (underlying_projection_surjective X L) f g

/-- All eventual transports are exactly the finite-observation functions in this source class. -/
def underlyingFiniteObservationEquiv (L : Splitting X) :
    (X.underlyingResolution ⟶ Y.underlyingResolution) ≃
    {F : X.underlyingResolution.Point → Y.underlyingResolution.Point //
      Resolution.FinitelyObserved F} :=
  Resolution.finiteObservationEquiv (underlying_projection_surjective X L)

@[simp] theorem underlyingFiniteObservationEquiv_apply (L : Splitting X)
    (f : X.underlyingResolution ⟶ Y.underlyingResolution) :
    (underlyingFiniteObservationEquiv X Y L f).val = f.onLimit := rfl

end BanachTower
end KomorebiSpace
end
