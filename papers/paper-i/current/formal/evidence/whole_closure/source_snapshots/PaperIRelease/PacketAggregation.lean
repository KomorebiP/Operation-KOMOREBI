import KomorebiVerification.ExactCoordinates

set_option autoImplicit false
set_option linter.unusedSectionVars false
noncomputable section
namespace Komorebi.PaperIRelease.PacketAggregation
open Komorebi.Foundation Komorebi.Foundation.LinearProjectorFamily
universe u v w x
variable {R : Type u} [CommSemiring R]
variable {M : Type v} [AddCommMonoid M] [Module R M]
variable {ι : Type w} [Fintype ι] {κ : Type x} [Fintype κ] [DecidableEq κ]
variable (P : LinearProjectorFamily R M ι) (σ : ι → κ)

/-- Actual sum of the original projectors in a fibre. -/
def groupedProjection (j : κ) : Module.End R M := ∑ i with σ i = j, P.proj i

theorem proj_groupedProjection (a : ι) (j : κ) (m : M) :
    P.proj a (groupedProjection P σ j m) = if σ a = j then P.proj a m else 0 := by
  classical
  simp only [groupedProjection, LinearMap.sum_apply, map_sum]
  by_cases ha : σ a = j
  · rw [ite_eq_left ha, Finset.sum_eq_single a]
    · exact P.idempotent a m
    · intro b _ hba
      exact P.orthogonal hba.symm m
    · simp [ha]
  · rw [ite_eq_right ha]
    apply Finset.sum_eq_zero
    intro b hb
    have hba : a ≠ b := by
      intro hab
      exact ha (hab ▸ (Finset.mem_filter.mp hb).2)
    exact P.orthogonal hba m

/-- Finite fibre sums form a complete orthogonal projector family. -/
def groupedFamily : LinearProjectorFamily R M κ where
  proj := groupedProjection P σ
  idempotent j m := by
    simp only [groupedProjection, LinearMap.sum_apply]
    apply Finset.sum_congr rfl
    intro a ha
    have h := proj_groupedProjection P σ a j m
    simpa only [groupedProjection, LinearMap.sum_apply, ite_eq_left (Finset.mem_filter.mp ha).2] using h
  orthogonal {j k} hjk m := by
    change (∑ a with σ a = j, P.proj a) (groupedProjection P σ k m) = 0
    rw [LinearMap.sum_apply]
    apply Finset.sum_eq_zero
    intro a ha
    rw [proj_groupedProjection, ite_eq_right]
    exact fun hak => hjk ((Finset.mem_filter.mp ha).2.symm.trans hak)
  complete m := by
    simp only [groupedProjection, LinearMap.sum_apply]
    have h := Finset.sum_fiberwise_eq_sum_filter Finset.univ Finset.univ σ (fun i => P.proj i m)
    simpa only [Finset.mem_univ, Finset.filter_true_of_mem, Finset.sum_const_zero] using h.trans (by simpa using P.complete m)

/-- An original packet lies in its grouped range. -/
theorem original_mem_grouped (a : ι) (m : (P.proj a).range) :
    (m : M) ∈ ((groupedFamily P σ).proj (σ a)).range := by
  classical
  refine ⟨m, ?_⟩
  change groupedProjection P σ (σ a) m = m
  simp only [groupedProjection, LinearMap.sum_apply]
  rw [Finset.sum_eq_single a]
  · obtain ⟨x, hx⟩ := m.property
    rw [← hx]
    exact P.idempotent a x
  · intro b _ hba
    obtain ⟨x, hx⟩ := m.property
    rw [← hx]
    exact P.orthogonal hba x
  · simp

/-- Surjective grouping preserves nonzero packets. -/
theorem grouped_nonzero (hP : ∀ i, P.proj i ≠ 0) (hσ : Function.Surjective σ) :
    ∀ j, (groupedFamily P σ).proj j ≠ 0 := by
  intro j hj
  obtain ⟨i, rfl⟩ := hσ j
  apply hP i
  ext m
  have h := original_mem_grouped P σ i ⟨P.proj i m, ⟨m, rfl⟩⟩
  rw [hj] at h
  simpa using h


/-- Actual packet coordinates inside one grouped range. -/
def groupedAnalysis (j : κ) : ((groupedFamily P σ).proj j).range →ₗ[R]
    ((i : {i : ι // σ i = j}) → (P.proj i.val).range) where
  toFun m i := ⟨P.proj i.val m, ⟨m, rfl⟩⟩
  map_add' _ _ := by ext i; simp
  map_smul' _ _ := by ext i; simp

/-- Synthesis of the original packets in a single fibre. -/
def groupedSynthesis (j : κ) :
    ((i : {i : ι // σ i = j}) → (P.proj i.val).range) →ₗ[R]
      ((groupedFamily P σ).proj j).range where
  toFun m := ⟨∑ i, (m i : M), by
    apply Submodule.sum_mem
    intro i _
    have h := original_mem_grouped P σ i.val (m i)
    simpa only [i.property] using h⟩
  map_add' _ _ := by apply Subtype.ext; simp [Finset.sum_add_distrib]
  map_smul' _ _ := by apply Subtype.ext; simp [Finset.smul_sum]

@[simp] theorem groupedSynthesis_analysis (j : κ)
    (m : ((groupedFamily P σ).proj j).range) :
    groupedSynthesis P σ j (groupedAnalysis P σ j m) = m := by
  apply Subtype.ext
  change (∑ i : {i : ι // σ i = j}, P.proj i.val m) = m
  have hs := Finset.sum_subtype (p := fun i => σ i = j) (F := inferInstance) (Finset.univ.filter (fun i => σ i = j))
    (by intro i; simp) (fun i => P.proj i m)
  rw [← hs]
  have hm : groupedProjection P σ j m = m := by
    obtain ⟨x, hx⟩ := m.property
    rw [← hx]
    exact (groupedFamily P σ).idempotent j x
  simpa only [groupedProjection, LinearMap.sum_apply] using hm

@[simp] theorem groupedAnalysis_synthesis (j : κ)
    (m : (i : {i : ι // σ i = j}) → (P.proj i.val).range) :
    groupedAnalysis P σ j (groupedSynthesis P σ j m) = m := by
  classical
  funext a
  apply Subtype.ext
  change P.proj a.val (∑ i, (m i : M)) = m a
  rw [map_sum, Finset.sum_eq_single a]
  · obtain ⟨x, hx⟩ := (m a).property
    rw [← hx]
    exact P.idempotent a.val x
  · intro b _ hba
    obtain ⟨x, hx⟩ := (m b).property
    rw [← hx]
    exact P.orthogonal (fun hab => hba (Subtype.ext hab.symm)) x
  · simp

/-- The grouped range is canonically the product of the actual original packet ranges. -/
def groupedRangeEquiv (j : κ) : ((groupedFamily P σ).proj j).range ≃ₗ[R]
    ((i : {i : ι // σ i = j}) → (P.proj i.val).range) where
  toFun := groupedAnalysis P σ j
  invFun := groupedSynthesis P σ j
  left_inv := groupedSynthesis_analysis P σ j
  right_inv := groupedAnalysis_synthesis P σ j
  map_add' := (groupedAnalysis P σ j).map_add
  map_smul' := (groupedAnalysis P σ j).map_smul

/-- Literal finite direct-sum form of packet aggregation. -/
def groupedRangeDirectSumEquiv (j : κ) : ((groupedFamily P σ).proj j).range ≃ₗ[R]
    DirectSum {i : ι // σ i = j} (fun i => (P.proj i.val).range) := by
  classical
  exact (groupedRangeEquiv P σ j).trans
    (DirectSum.linearEquivFunOnFintype R _ _).symm

end Komorebi.PaperIRelease.PacketAggregation
