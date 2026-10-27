import PaperX.JointOccupancy

/-! Naturality under actual intertwiners. This includes invariance under a
change of basis, without assuming that the operators are coordinate-diagonal. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.OccupancyTransport

open LinearMap Module.End PaperX.SpectralProjectors PaperX.JointOccupancy
attribute [local instance] Classical.propDecidable
universe u v w z
variable {K : Type u} [Field K]
  {V : Type v} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
  {W : Type w} [AddCommGroup W] [Module K W] [FiniteDimensional K W]
  {I : Type z}

/-- Any intertwiner respects the actual Lagrange projectors when the source
operator is split. The target need not have the identical full spectrum. -/
theorem spectral_intertwines (T : Module.End K V) (U : Module.End K W)
    (F : V →ₗ[K] W) (hT : Split T) (hF : U.comp F = F.comp T) (a : K) :
    (spectral U a).comp F = F.comp (spectral T a) := by
  have hle : (⨆ b : K, T.eigenspace b) ≤
      LinearMap.ker ((spectral U a).comp F - F.comp (spectral T a)) := by
    refine iSup_le fun b => ?_
    intro x hx
    have hx' : T x = b • x := mem_eigenspace_iff.mp hx
    have hfx : U (F x) = b • F x := by
      have he := LinearMap.congr_fun hF x
      simpa only [LinearMap.comp_apply, hx', map_smul] using he
    change spectral U a (F x) - F (spectral T a x) = 0
    rw [spectral_on_eigenvector U a b (F x) hfx,
      spectral_on_eigenvector T a b x hx']
    split_ifs <;> simp
  rw [hT] at hle
  exact sub_eq_zero.mp (LinearMap.ker_eq_top.mp (top_unique hle))

theorem joint_intertwines (T : I → Module.End K V) (U : I → Module.End K W)
    (F : V →ₗ[K] W) (hs : ∀ i, Split (T i))
    (hF : ∀ i, (U i).comp F = F.comp (T i)) (a : I → K) (l : List I) :
    (joint U a l).comp F = F.comp (joint T a l) := by
  induction l with
  | nil => ext x; rfl
  | cons i l ih =>
    ext x
    have he := LinearMap.congr_fun (spectral_intertwines (T i) (U i) F (hs i) (hF i) (a i))
      (joint T a l x)
    have hl := LinearMap.congr_fun ih x
    change spectral (U i) (a i) (joint U a l (F x)) = F (spectral (T i) (a i) (joint T a l x))
    change joint U a l (F x) = F (joint T a l x) at hl
    rw [hl]
    exact he

theorem joint_conjugate (T : I → Module.End K V) (U : I → Module.End K W)
    (e : V ≃ₗ[K] W) (hs : ∀ i, Split (T i))
    (he : ∀ i, (U i).comp e.toLinearMap = e.toLinearMap.comp (T i))
    (a : I → K) (l : List I) :
    joint U a l = (e.toLinearMap.comp (joint T a l)).comp e.symm.toLinearMap := by
  ext x
  have h := LinearMap.congr_fun (joint_intertwines T U e.toLinearMap hs he a l) (e.symm x)
  simpa using h

/-- A basis change preserves the actual field-valued trace. -/
theorem trace_conjugate (T : I → Module.End K V) (U : I → Module.End K W)
    (e : V ≃ₗ[K] W) (hs : ∀ i, Split (T i))
    (he : ∀ i, (U i).comp e.toLinearMap = e.toLinearMap.comp (T i))
    (a : I → K) (l : List I) :
    LinearMap.trace K W (joint U a l) = LinearMap.trace K V (joint T a l) := by
  rw [joint_conjugate T U e hs he a l, LinearMap.trace_comp_comm']
  simp

end PaperX.OccupancyTransport
