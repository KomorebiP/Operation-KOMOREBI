import KomorebiSpace.HolonomyProjection
import KomorebiSpace.CayleyHolonomyConditioning
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Tactic.FinCases

set_option autoImplicit false

/-!
# The nonuniform gain family on an actual fixed three-view graph

All connections are inverse-consistent real linear isometries of C. Only one
edge carries the varying Cayley rotation. The graph and real fiber dimension
stay fixed. Thus no graph-size or dimension growth explains the diverging
correction gain.
-/
noncomputable section
namespace KomorebiSpace
namespace HolonomyTransport
namespace ConditioningTriangle

abbrev graph : SimpleGraph (Fin 3) := ⊤

def edgeTransport (t : ℝ) (i j : Fin 3) : ℂ ≃ₗᵢ[ℝ] ℂ :=
  if i=0 ∧ j=2 then CayleyHolonomy.rotation t
  else if i=2 ∧ j=0 then (CayleyHolonomy.rotation t).symm
  else LinearIsometryEquiv.refl ℝ ℂ

def connection (t : ℝ) : Connection (Fin 3) ℂ where
  transport := edgeTransport t
  self_apply := by intro i z; fin_cases i <;> rfl
  reverse_apply := by
    intro i j z
    fin_cases i <;> fin_cases j
    all_goals first
      | rfl
      | exact (CayleyHolonomy.rotation t).symm_apply_apply z
      | exact (CayleyHolonomy.rotation t).apply_symm_apply z

def routing : OverlapTransport.Routing graph (0 : Fin 3) where
  path i := by
    by_cases h : (0 : Fin 3)=i
    · subst i; exact .nil
    · exact (show graph.Adj 0 i from h).toWalk
  at_anchor := rfl

theorem parallel_iff_zero (t : ℝ) (x : Fin 3 → ℂ) :
    (connection t).Parallel graph x ↔ x=0 := by
  constructor
  · intro hx
    have h10 : x 1=x 0 := hx 0 1 (by decide)
    have h21 : x 2=x 1 := hx 1 2 (by decide)
    have hr : CayleyHolonomy.rotation t (x 2)=x 0 := hx 0 2 (by decide)
    rw [h21,h10] at hr
    have hz := (CayleyHolonomy.fixed_iff_zero t (x 0)).mp hr
    funext i
    fin_cases i
    · exact hz
    · exact h10.trans hz
    · exact h21.trans (h10.trans hz)
  · intro hx
    subst x
    intro i j _hij
    exact map_zero _

theorem fixed_iff_zero (t : ℝ) (z : ℂ) :
    z ∈ Rooted.fixedSpace (connection t) routing ↔ z=0 := by
  rw [← Rooted.anchor_extendable_iff]
  constructor
  · rintro ⟨x,hx,ho⟩
    have hz := (parallel_iff_zero t x).mp hx
    rw [hz] at ho
    exact ho.symm
  · intro hz
    subst z
    exact ⟨0,(parallel_iff_zero t 0).mpr rfl,rfl⟩

theorem orthogonalRepair_zero (t : ℝ) (x : Fin 3 → ℂ) :
    Rooted.orthogonalRepair (connection t) routing x=0 :=
  (parallel_iff_zero t _).mp (Rooted.orthogonalRepair_parallel (connection t) routing x)

theorem inverse_displacement_norm (t : ℝ) (z : ℂ) :
    ‖(CayleyHolonomy.rotation t).symm z-z‖ = ‖CayleyHolonomy.rotation t z-z‖ := by
  rw [← (CayleyHolonomy.rotation t).norm_map, map_sub,
    LinearIsometryEquiv.apply_symm_apply, norm_sub_rev]

theorem constant_residual_norm (t : ℝ) (z : ℂ) :
    ‖(connection t).differential graph (fun _ => z)‖ = ‖CayleyHolonomy.rotation t z-z‖ := by
  apply le_antisymm
  · apply (pi_norm_le_iff_of_nonneg (norm_nonneg _)).mpr
    intro a
    change ‖edgeTransport t a.val.1 a.val.2 z-z‖ ≤ _
    unfold edgeTransport
    split
    · exact le_rfl
    · split
      · exact le_of_eq (inverse_displacement_norm t z)
      · change ‖z-z‖ ≤ _
        rw [sub_self,norm_zero]
        exact norm_nonneg (CayleyHolonomy.rotation t z-z)
  · have hb := norm_le_pi_norm ((connection t).differential graph (fun _ => z))
        (⟨(0,2),by decide⟩ : OverlapTransport.Edges graph)
    exact hb

/-- Every global repair gain on this fixed graph must be at least |t-i|/2. -/
theorem necessary_global_gain (t C : ℝ)
    (hb : ∀ x : Fin 3 → ℂ,
      ‖x-Rooted.orthogonalRepair (connection t) routing x‖ ≤
        C * ‖(connection t).differential graph x‖) : CayleyHolonomy.sharpGain t ≤ C := by
  apply CayleyHolonomy.necessary_gain t C
  intro z
  have hx := hb (fun _ => z)
  rw [orthogonalRepair_zero, sub_zero, constant_residual_norm] at hx
  simpa only [pi_norm_const] using hx

/-- Failure of a universal constant already occurs with three vertices and real dimension two. -/
theorem no_uniform_global_gain :
    ¬ ∃ C : ℝ, ∀ t : ℝ, ∀ x : Fin 3 → ℂ,
      ‖x-Rooted.orthogonalRepair (connection t) routing x‖ ≤
        C * ‖(connection t).differential graph x‖ := by
  rintro ⟨C,hC⟩
  obtain ⟨t,ht⟩ := CayleyHolonomy.gain_unbounded C
  exact (not_le_of_gt ht) (necessary_global_gain t C (hC t))

end ConditioningTriangle
end HolonomyTransport
end KomorebiSpace
end
