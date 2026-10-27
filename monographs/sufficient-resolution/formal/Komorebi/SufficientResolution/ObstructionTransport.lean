import Komorebi.SufficientResolution.Globalization

/-!
# Transport of globalization obstructions

A correspondence must respect both realization and compatibility maps.
Such a correspondence induces a map on the actual obstruction quotients.
A vanishing target obstruction need not imply a vanishing source obstruction;
reflection requires an additional injectivity hypothesis, explicitly stated.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.Globalization

universe uR uG uV uW uG' uV' uW' uG'' uV'' uW''

variable {R : Type uR} [CommRing R]
variable {G : Type uG} [AddCommGroup G] [Module R G]
variable {V : Type uV} [AddCommGroup V] [Module R V]
variable {W : Type uW} [AddCommGroup W] [Module R W]
variable {G' : Type uG'} [AddCommGroup G'] [Module R G']
variable {V' : Type uV'} [AddCommGroup V'] [Module R V']
variable {W' : Type uW'} [AddCommGroup W'] [Module R W']
variable {G'' : Type uG''} [AddCommGroup G''] [Module R G'']
variable {V'' : Type uV''} [AddCommGroup V''] [Module R V'']
variable {W'' : Type uW''} [AddCommGroup W''] [Module R W'']

/-- A typed correspondence of local/global presentation diagrams. -/
structure PresentationMap (A : G →ₗ[R] V) (delta : V →ₗ[R] W)
    (A' : G' →ₗ[R] V') (delta' : V' →ₗ[R] W') where
  globalMap : G →ₗ[R] G'
  localMap : V →ₗ[R] V'
  residualMap : W →ₗ[R] W'
  realization_commutes : localMap.comp A = A'.comp globalMap
  compatibility_commutes : delta'.comp localMap = residualMap.comp delta

namespace PresentationMap

variable {A : G →ₗ[R] V} {delta : V →ₗ[R] W}
variable {A' : G' →ₗ[R] V'} {delta' : V' →ₗ[R] W'}
variable {A'' : G'' →ₗ[R] V''} {delta'' : V'' →ₗ[R] W''}

variable (f : PresentationMap A delta A' delta')

/-- The local map really restricts to compatible data. -/
def kernelMap : LinearMap.ker delta →ₗ[R] LinearMap.ker delta' where
  toFun v := ⟨f.localMap v, by
    change delta' (f.localMap v) = 0
    have h := LinearMap.congr_fun f.compatibility_commutes (v : V)
    change delta' (f.localMap v) = f.residualMap (delta v) at h
    rw [h, (show delta (v : V) = 0 from v.2), map_zero]⟩
  map_add' x y := Subtype.ext (f.localMap.map_add x y)
  map_smul' a x := Subtype.ext (f.localMap.map_smul a x)

 theorem kernelMap_preserves_realizability :
    realizationsInKernel A delta ≤
      (realizationsInKernel A' delta').comap f.kernelMap := by
  intro v hv
  obtain ⟨g, hg⟩ := hv
  change ∃ g' : G', A' g' = f.localMap (v : V)
  refine ⟨f.globalMap g, ?_⟩
  have h := LinearMap.congr_fun f.realization_commutes g
  change f.localMap (A g) = A' (f.globalMap g) at h
  rw [← h, hg]
  rfl

/-- The induced map on compatible-but-unrealizable classes. -/
def obstructionMap : ObstructionSpace A delta →ₗ[R] ObstructionSpace A' delta' :=
  (realizationsInKernel A delta).mapQ (realizationsInKernel A' delta')
    f.kernelMap f.kernelMap_preserves_realizability

 theorem obstructionMap_class (v : LinearMap.ker delta) :
    f.obstructionMap (obstructionClass A delta v) =
      obstructionClass A' delta' (f.kernelMap v) := rfl

 theorem transports_zero_obstruction (v : LinearMap.ker delta)
    (hv : obstructionClass A delta v = 0) :
    obstructionClass A' delta' (f.kernelMap v) = 0 := by
  rw [← f.obstructionMap_class, hv, map_zero]

/-- Reflection is conditional on injectivity, not silently inferred from compatibility. -/
 theorem reflects_zero_obstruction (hf : Function.Injective f.obstructionMap)
    (v : LinearMap.ker delta) :
    obstructionClass A' delta' (f.kernelMap v) = 0 ↔
      obstructionClass A delta v = 0 := by
  constructor
  · intro h
    apply hf
    rw [f.obstructionMap_class, h, map_zero]
  · exact f.transports_zero_obstruction v

/-- Compose correspondences without identifying their underlying domains. -/
def compose (g : PresentationMap A' delta' A'' delta'') :
    PresentationMap A delta A'' delta'' where
  globalMap := g.globalMap.comp f.globalMap
  localMap := g.localMap.comp f.localMap
  residualMap := g.residualMap.comp f.residualMap
  realization_commutes := by
    ext x
    have hf := LinearMap.congr_fun f.realization_commutes x
    have hg := LinearMap.congr_fun g.realization_commutes (f.globalMap x)
    change g.localMap (f.localMap (A x)) = A'' (g.globalMap (f.globalMap x))
    change f.localMap (A x) = A' (f.globalMap x) at hf
    change g.localMap (A' (f.globalMap x)) = A'' (g.globalMap (f.globalMap x)) at hg
    rw [hf, hg]
  compatibility_commutes := by
    ext x
    have hf := LinearMap.congr_fun f.compatibility_commutes x
    have hg := LinearMap.congr_fun g.compatibility_commutes (f.localMap x)
    change delta'' (g.localMap (f.localMap x)) = g.residualMap (f.residualMap (delta x))
    change delta' (f.localMap x) = f.residualMap (delta x) at hf
    change delta'' (g.localMap (f.localMap x)) = g.residualMap (delta' (f.localMap x)) at hg
    rw [hg, hf]

 theorem obstructionMap_compose (g : PresentationMap A' delta' A'' delta'') :
    (f.compose g).obstructionMap = g.obstructionMap.comp f.obstructionMap := by
  ext v
  rfl

end PresentationMap
end Komorebi.SufficientResolution.Globalization
