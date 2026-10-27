import Mathlib.Analysis.InnerProductSpace.l2Space
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.Normed.Lp.lpSpace
import KomorebiPaperV.IntegerPolyphase

/-!
Author: Komorebi P.
Square-summable signals: bounded packet maps, exact synthesis, and isometric
integer address coordinates. The channel target uses the joint l2 norm on
Fin N × Z, rather than the supremum norm on a function space of channels.
-/

open scoped BigOperators
namespace KomorebiPaperV.HilbertPackets

abbrev Signal (I : Type*) : Type _ := lp (fun _ : I => ℂ) 2

variable {I R S J : Type*}

noncomputable def projection [DecidableEq R] (phase : I → R) (r : R)
    (x : Signal I) : Signal I :=
  ⟨KomorebiPaperV.packet phase r x, (lp.memℓp x).mono' (by
    intro i
    by_cases h : phase i = r <;> simp [KomorebiPaperV.packet, h])⟩

theorem projection_apply [DecidableEq R] (phase : I → R) (r : R)
    (x : Signal I) (i : I) :
    projection phase r x i = if phase i = r then x i else 0 := rfl

theorem projection_norm_le [DecidableEq R] (phase : I → R) (r : R)
    (x : Signal I) : ‖projection phase r x‖ ≤ ‖x‖ := by
  apply lp.norm_mono (by norm_num)
  intro i
  by_cases h : phase i = r <;> simp [projection_apply, h]

noncomputable def projectionLinear [DecidableEq R] (phase : I → R) (r : R) :
    Signal I →ₗ[ℂ] Signal I where
  toFun := projection phase r
  map_add' x y := by
    ext i
    by_cases h : phase i = r <;> simp [projection_apply, h]
  map_smul' a x := by
    ext i
    by_cases h : phase i = r <;> simp [projection_apply, h]

noncomputable def projector [DecidableEq R] (phase : I → R) (r : R) :
    Signal I →L[ℂ] Signal I :=
  (projectionLinear phase r).mkContinuous 1 (by
    intro x
    change ‖projection phase r x‖ ≤ 1 * ‖x‖
    simpa using projection_norm_le phase r x)

theorem projector_apply [DecidableEq R] (phase : I → R) (r : R)
    (x : Signal I) : projector phase r x = projection phase r x := rfl

theorem projector_idempotent [DecidableEq R] (phase : I → R) (r : R) :
    (projector phase r).comp (projector phase r) = projector phase r := by
  ext x i
  by_cases h : phase i = r <;>
    simp [projector_apply, projection_apply, h]

theorem projector_annihilate [DecidableEq R] (phase : I → R) (r s : R) (h : r ≠ s) :
    (projector phase r).comp (projector phase s) = 0 := by
  ext x i
  by_cases hr : phase i = r
  · simp [projector_apply, projection_apply, hr, h]
  · simp [projector_apply, projection_apply, hr]

theorem projector_complete [Fintype R] [DecidableEq R] (phase : I → R) :
    (∑ r : R, projector phase r) = ContinuousLinearMap.id ℂ (Signal I) := by
  apply ContinuousLinearMap.ext
  intro x
  simp only [sum_apply, ContinuousLinearMap.id_apply, projector_apply]
  apply lp.ext
  funext i
  simp only [lp.coeFn_sum, Finset.sum_apply, projection_apply]
  exact KomorebiPaperV.packet_complete phase (fun j => x j) i

theorem projector_refinement [Fintype S] [DecidableEq S] [DecidableEq R]
    (fine : I → S) (coarsen : S → R) (r : R) :
    projector (coarsen ∘ fine) r =
      ∑ s : S, if coarsen s = r then projector fine s else 0 := by
  apply ContinuousLinearMap.ext
  intro x
  simp only [sum_apply, projector_apply]
  apply lp.ext
  funext i
  rw [lp.coeFn_sum, Finset.sum_apply]
  calc
    _ = ∑ s : S, if coarsen s = r then projection fine s x i else 0 :=
      KomorebiPaperV.packet_refinement fine coarsen r (fun j => x j) i
    _ = _ := by
      apply Finset.sum_congr rfl
      intro s _
      by_cases h : coarsen s = r <;> simp [h, projector_apply]

noncomputable def reindex (e : I ≃ J) (x : Signal I) : Signal J :=
  ⟨fun j => x (e.symm j), memℓp_gen (by
    simpa only [Function.comp_def] using
      e.symm.summable_iff.mpr ((lp.memℓp x).summable (by norm_num)))⟩

theorem reindex_norm (e : I ≃ J) (x : Signal I) : ‖reindex e x‖ = ‖x‖ := by
  rw [lp.norm_eq_tsum_rpow (by norm_num), lp.norm_eq_tsum_rpow (by norm_num)]
  congr 1
  exact e.symm.tsum_eq (fun i => ‖x i‖ ^ (2 : ENNReal).toReal)

noncomputable def reindexIsometry (e : I ≃ J) : Signal I ≃ₗᵢ[ℂ] Signal J where
  toFun := reindex e
  invFun := reindex e.symm
  left_inv x := by ext i; simp [reindex]
  right_inv x := by ext j; simp [reindex]
  map_add' x y := by ext j; rfl
  map_smul' a x := by ext j; rfl
  norm_map' := reindex_norm e

noncomputable def polyphase (N : ℕ) (hN : 0 < N) :
    Signal ℤ ≃ₗᵢ[ℂ] Signal (Fin N × ℤ) :=
  reindexIsometry (KomorebiPaperV.IntegerPolyphase.addressEquiv N hN)

theorem polyphase_apply (N : ℕ) (hN : 0 < N) (x : Signal ℤ) (r : Fin N) (q : ℤ) :
    polyphase N hN x (r, q) = x ((N : ℤ) * q + (r.val : ℤ)) := rfl

theorem polyphase_synthesis_analysis (N : ℕ) (hN : 0 < N) (x : Signal ℤ) :
    (polyphase N hN).symm (polyphase N hN x) = x :=
  (polyphase N hN).symm_apply_apply x

theorem polyphase_analysis_synthesis (N : ℕ) (hN : 0 < N) (x : Signal (Fin N × ℤ)) :
    polyphase N hN ((polyphase N hN).symm x) = x :=
  (polyphase N hN).apply_symm_apply x

theorem polyphase_energy (N : ℕ) (hN : 0 < N) (x : Signal ℤ) :
    ‖polyphase N hN x‖ ^ 2 = ‖x‖ ^ 2 := by
  rw [(polyphase N hN).norm_map]

theorem impulse_expansion (x : Signal ℤ) :
    HasSum (fun i : ℤ => lp.single 2 i (x i)) x :=
  lp.hasSum_single (by norm_num) x

theorem projector_symmetric [DecidableEq R] (phase : I → R) (r : R)
    (x y : Signal I) :
    inner ℂ (projector phase r x) y = inner ℂ x (projector phase r y) := by
  rw [lp.inner_eq_tsum, lp.inner_eq_tsum]
  apply tsum_congr
  intro i
  by_cases h : phase i = r <;> simp [projector_apply, projection_apply, h]

theorem projector_orthogonal [DecidableEq R] (phase : I → R) (r s : R)
    (h : r ≠ s) (x y : Signal I) :
    inner ℂ (projector phase r x) (projector phase s y) = 0 := by
  rw [lp.inner_eq_tsum]
  have hz : ∀ i, inner ℂ (projector phase r x i) (projector phase s y i) = 0 := by
    intro i
    by_cases hr : phase i = r
    · simp [projector_apply, projection_apply, hr, h]
    · simp [projector_apply, projection_apply, hr]
  simp only [hz, tsum_zero]

noncomputable def impulseBasis : HilbertBasis ℤ ℂ (Signal ℤ) :=
  ⟨LinearIsometryEquiv.refl ℂ (Signal ℤ)⟩

theorem impulse_basis_apply (i : ℤ) : impulseBasis i = lp.single 2 i (1 : ℂ) := by
  rw [← impulseBasis.repr_symm_single]
  rfl

theorem impulse_dense_span :
    (Submodule.span ℂ (Set.range (fun i : ℤ => (lp.single 2 i (1 : ℂ) : Signal ℤ)))).topologicalClosure = ⊤ := by
  have hfun : (⇑impulseBasis : ℤ → Signal ℤ) = fun i => lp.single 2 i (1 : ℂ) :=
    funext impulse_basis_apply
  rw [← hfun]
  exact impulseBasis.dense_span

noncomputable def shift (d : ℤ) : Signal ℤ ≃ₗᵢ[ℂ] Signal ℤ :=
  reindexIsometry (Equiv.addRight d)

theorem shift_apply (d n : ℤ) (x : Signal ℤ) : shift d x n = x (n - d) := rfl

theorem reindex_single (e : I ≃ J) [DecidableEq I] [DecidableEq J] (i : I) (c : ℂ) :
    reindex e (lp.single 2 i c) = lp.single 2 (e i) c := by
  apply lp.ext
  funext j
  simp [reindex, lp.single_apply, Pi.single_apply, Equiv.symm_apply_eq]

theorem shift_impulse (d i : ℤ) :
    shift d (lp.single 2 i (1 : ℂ)) = lp.single 2 (i + d) (1 : ℂ) :=
  reindex_single (Equiv.addRight d) i 1

theorem residue_projector_refinement (N M : ℕ) (hN : 0 < N) (hM : 0 < M)
    (hNM : N ∣ M) (r : Fin N) :
    projector (IntegerPolyphase.phase N hN) r =
      ∑ s : Fin M, if IntegerPolyphase.phase N hN (s.val : ℤ) = r
        then projector (IntegerPolyphase.phase M hM) s else 0 := by
  have hc : (fun j : ℤ => IntegerPolyphase.phase N hN
      ((IntegerPolyphase.phase M hM j).val : ℤ)) = IntegerPolyphase.phase N hN := by
    funext j
    apply Fin.ext
    change (((IntegerPolyphase.phase M hM j).val : ℤ) % (N : ℤ)).toNat =
      (j % (N : ℤ)).toNat
    rw [IntegerPolyphase.phase_val, IntegerPolyphase.emod_coarsen N M hNM]
  have h := projector_refinement (IntegerPolyphase.phase M hM)
    (fun s : Fin M => IntegerPolyphase.phase N hN (s.val : ℤ)) r
  simpa only [Function.comp_def, hc] using h

theorem shift_generated_dense_span :
    (Submodule.span ℂ (Set.range (fun i : ℤ => shift i (lp.single 2 0 (1 : ℂ))))).topologicalClosure = ⊤ := by
  simpa only [shift_impulse, zero_add] using impulse_dense_span

theorem finite_impulse_expansion (s : Finset ℤ) (x : Signal ℤ)
    (hs : ∀ i ∉ s, x i = 0) : (∑ i ∈ s, lp.single 2 i (x i)) = x := by
  have hsum : HasSum (fun i : ℤ => (lp.single 2 i (x i) : Signal ℤ))
      (∑ i ∈ s, lp.single 2 i (x i)) :=
    hasSum_sum_of_ne_finset_zero (fun i hi => by rw [hs i hi, lp.single_zero])
  exact hsum.unique (impulse_expansion x)

end KomorebiPaperV.HilbertPackets
