import KomorebiVerification.TopologicalCompletion

/-! # The unique finite packet split on a dense completion -/

noncomputable section
open scoped BigOperators
open Set Function

namespace PaperIRelease.TopologyFiniteCompletion

open KomorebiVerification.TopologicalCompletion

variable {𝕜 X ι : Type*} [NontriviallyNormedField 𝕜]
variable [NormedAddCommGroup X] [NormedSpace 𝕜 X] [Fintype ι]

/-- Bounded operators whose restrictions form a packet system on a dense
submodule form the same packet system on the ambient normed space. -/
def extendPacketFamily
    (M : Submodule 𝕜 X) (hM : M.topologicalClosure = ⊤)
    (P : ι → X →L[𝕜] X) (Q : BoundedProjectorFamily 𝕜 M ι)
    (hext : ∀ i (x : M), P i x = (Q.proj i x : X)) :
    BoundedProjectorFamily 𝕜 X ι where
  proj := P
  idempotent i x := by
    have hd : DenseRange (fun y : M ↦ (y : X)) := by
      exact (Submodule.dense_iff_topologicalClosure_eq_top.mpr hM).denseRange_val
    have he : (fun y : X ↦ P i (P i y)) = (fun y : X ↦ P i y) := by
      apply hd.equalizer (by fun_prop) (by fun_prop)
      funext y
      change P i (P i (y : X)) = P i (y : X)
      rw [hext i y, hext i (Q.proj i y), Q.idempotent i y]
    exact congrFun he x
  annihilate := by
    intro i j hij x
    have hd : DenseRange (fun y : M ↦ (y : X)) := by
      exact (Submodule.dense_iff_topologicalClosure_eq_top.mpr hM).denseRange_val
    have he : (fun y : X ↦ P i (P j y)) = (fun _ : X ↦ (0 : X)) := by
      apply hd.equalizer (by fun_prop) continuous_const
      funext y
      change P i (P j (y : X)) = 0
      rw [hext j y, hext i (Q.proj j y), Q.annihilate hij y]
      rfl
    exact congrFun he x
  complete x := by
    have hd : DenseRange (fun y : M ↦ (y : X)) := by
      exact (Submodule.dense_iff_topologicalClosure_eq_top.mpr hM).denseRange_val
    have he : (fun y : X ↦ ∑ i, P i y) = (fun y : X ↦ y) := by
      apply hd.equalizer (by fun_prop) continuous_id
      funext y
      change (∑ i, P i (y : X)) = (y : X)
      simp_rw [hext]
      exact_mod_cast Q.complete y
    exact congrFun he x

/-- Each extended packet is exactly the closure of its dense-subspace
packet. No closedness or completeness of the dense subspace is required. -/
theorem extended_packet_range
    (M : Submodule 𝕜 X) (hM : M.topologicalClosure = ⊤)
    (P : ι → X →L[𝕜] X) (Q : BoundedProjectorFamily 𝕜 M ι)
    (hext : ∀ i (x : M), P i x = (Q.proj i x : X)) (i : ι) :
    (M.map (P i).toLinearMap).topologicalClosure = (P i).range :=
  BoundedProjectorFamily.idempotentRange_eq_closure_map (P i)
    ((extendPacketFamily M hM P Q hext).idempotent i) M hM

/-- There is at most one continuous ambient extension of every projector
in the dense packet system. This is uniqueness of the whole split, rather
than merely uniqueness of one extracted range. -/
theorem extension_unique
    (M : Submodule 𝕜 X) (hM : M.topologicalClosure = ⊤)
    (P R : ι → X →L[𝕜] X) (Q : BoundedProjectorFamily 𝕜 M ι)
    (hP : ∀ i (x : M), P i x = (Q.proj i x : X))
    (hR : ∀ i (x : M), R i x = (Q.proj i x : X)) : P = R := by
  have hd : DenseRange (fun y : M ↦ (y : X)) := by
    exact (Submodule.dense_iff_topologicalClosure_eq_top.mpr hM).denseRange_val
  funext i
  apply DFunLike.coe_injective
  apply hd.equalizer (P i).continuous (R i).continuous
  funext x
  exact (hP i x).trans (hR i x).symm

end PaperIRelease.TopologyFiniteCompletion
