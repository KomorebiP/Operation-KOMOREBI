import KomorebiSpace.ResolutionViews
import KomorebiSpace.SplitTowerRepair

set_option autoImplicit false

/-!
# The checked Banach-tower repair acts on coherent ambient sections

This bridge keeps the actual bonding functions and coordinate actions. It
adds no effective-descent or unrestricted realization assumption.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace BanachTower
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)

def viewSystem : ViewSystem ℕ :=
  (Resolution.Adjacent.resolution X.Obj (fun n => X.down n)).views

def ambientPointEquiv : X.Point ≃ X.viewSystem.Ambient :=
  (Resolution.Adjacent.pointEquiv X.Obj (fun n => X.down n)).trans
    (Resolution.ambientEquiv _).symm

@[simp] theorem ambientPointEquiv_coordinate (x : X.Point) (n : ℕ) :
    (X.ambientPointEquiv x).val n = x.val n := rfl

def exactAmbientMorphism (f : Candidates X Y) (hf : Exact X Y f) :
    ViewSystem.Morphism X.viewSystem Y.viewSystem :=
  (Resolution.Adjacent.map (fun n => f n) (fun n x =>
    congrArg (fun T : X.Obj (n+1) →L[𝕜] Y.Obj n => T x) (hf n))).viewMorphism

theorem exactAmbient_agrees (f : Candidates X Y) (hf : Exact X Y f) (x : X.Point) :
    (exactAmbientMorphism X Y f hf).onAmbient (X.ambientPointEquiv x) =
      Y.ambientPointEquiv (onLimit X Y f hf x) := rfl

def repairedAmbientMorphism (L : Splitting Y)
    (hgap : (L.bound : ℝ) * X.bound < 1) (f : Candidates X Y) :
    ViewSystem.Morphism X.viewSystem Y.viewSystem :=
  exactAmbientMorphism X Y (L.repair X hgap f) (L.repair_exact X hgap f)

@[simp] theorem repairedAmbient_coordinate (L : Splitting Y)
    (hgap : (L.bound : ℝ) * X.bound < 1) (f : Candidates X Y)
    (x : X.viewSystem.Ambient) (n : ℕ) :
    ((repairedAmbientMorphism X Y L hgap f).onAmbient x).val n =
      (L.repair X hgap f) n (x.val n) := rfl

theorem repairedAmbient_agrees (L : Splitting Y)
    (hgap : (L.bound : ℝ) * X.bound < 1) (f : Candidates X Y) (x : X.Point) :
    (repairedAmbientMorphism X Y L hgap f).onAmbient (X.ambientPointEquiv x) =
      Y.ambientPointEquiv
        (onLimit X Y (L.repair X hgap f) (L.repair_exact X hgap f) x) := rfl

/-- Matching finite-prefix realizations glue to the existing Banach point type. -/
def prefixAmbientEquiv :
    X.Point ≃ ViewSystem.Matching X.viewSystem Resolution.prefixViews :=
  X.ambientPointEquiv.trans
    (X.viewSystem.gluingEquiv Resolution.prefixViews Resolution.prefixViews_transitionCover)

end BanachTower
end KomorebiSpace
end
