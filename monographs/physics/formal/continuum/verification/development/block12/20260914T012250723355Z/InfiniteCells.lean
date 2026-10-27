module

public import KomorebiPhysics.CountableAtlas
public import Mathlib.Topology.Algebra.InfiniteSum.Constructions

/-!
Section 6.5: actual coarse projections onto arbitrary, possibly infinite cells.
All sums are unconditional finite-subset limits. Completeness is explicit.
No generator or domain-invariance assertion enters this Hilbert-space layer.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace StrongAtlas
open Filter
open scoped BigOperators Topology
variable {H I J : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable [CompleteSpace H] (P : StrongAtlas H I)

def cellValue (C : Set I) (x : H) : H := ∑' i : C, P.proj i x

theorem cell_hasSum (C : Set I) (x : H) :
    HasSum (fun i : C => P.proj i x) (P.cellValue C x) :=
  ((P.strong x).summable.subtype C).hasSum

theorem cell_finite_norm_le (C : Set I) (s : Finset C) (x : H) :
    ‖∑ i ∈ s, P.proj i x‖ ≤ ‖x‖ := by
  classical
  have h := P.partial_norm_le (s.map (Function.Embedding.subtype C)) x
  simpa only [partialSum, Finset.sum_map, Function.Embedding.subtype_apply] using h

theorem cellValue_norm_le (C : Set I) (x : H) : ‖P.cellValue C x‖ ≤ ‖x‖ :=
  le_of_tendsto (P.cell_hasSum C x).norm
    (Filter.Eventually.of_forall (fun s => P.cell_finite_norm_le C s x))

/-- Construct a bounded linear operator from the actual strongly summed vectors. -/
def cell (C : Set I) : H →L[ℂ] H :=
  LinearMap.mkContinuous
    { toFun := P.cellValue C
      map_add' := fun x y => by
        simp only [cellValue, map_add]
        exact tsum_add ((P.strong x).summable.subtype C) ((P.strong y).summable.subtype C)
      map_smul' := fun c x => by
        simp only [cellValue, map_smul]
        exact tsum_smul c (fun i : C => P.proj i x) }
    1 (fun x => by simpa using P.cellValue_norm_le C x)

theorem cell_apply (C : Set I) (x : H) : P.cell C x = ∑' i : C, P.proj i x := rfl

theorem cell_sum (C : Set I) (x : H) :
    HasSum (fun i : C => P.proj i x) (P.cell C x) := P.cell_hasSum C x

theorem cell_norm_le (C : Set I) (x : H) : ‖P.cell C x‖ ≤ ‖x‖ := P.cellValue_norm_le C x

theorem cell_opNorm_le (C : Set I) : ‖P.cell C‖ ≤ 1 :=
  (P.cell C).opNorm_le_bound (by norm_num) (fun x => by simpa using P.cell_norm_le C x)

theorem eq_of_proj_eq {x y : H} (h : ∀ i, P.proj i x = P.proj i y) : x = y :=
  (P.strong x).unique ((P.strong y).congr_fun h)

theorem proj_cell (C : Set I) (j : I) (x : H) :
    P.proj j (P.cell C x) = if j ∈ C then P.proj j x else 0 := by
  classical
  rw [cell_apply, (P.proj j).map_tsum ((P.strong x).summable.subtype C)]
  by_cases hj : j ∈ C
  · rw [if_pos hj]
    rw [tsum_eq_single (⟨j,hj⟩ : C)]
    · exact P.idempotent j x
    · intro i hi
      exact P.orthogonal j i (fun h => hi (Subtype.ext h.symm)) x
  · rw [if_neg hj]
    apply tsum_eq_zero
    intro i
    exact P.orthogonal j i (fun h => hj (h ▸ i.property)) x

theorem cell_proj (C : Set I) (j : I) (x : H) :
    P.cell C (P.proj j x) = if j ∈ C then P.proj j x else 0 := by
  classical
  apply P.eq_of_proj_eq
  intro k
  rw [P.proj_cell]
  by_cases hj : j ∈ C <;> by_cases hk : k ∈ C <;> simp only [hj, hk, ite_true, ite_false, map_zero]
  · exact P.orthogonal k j (fun h => hk (h ▸ hj)) x
  · exact (P.orthogonal k j (fun h => hj (h ▸ hk)) x).symm

theorem cell_selfAdjoint (C : Set I) (x y : H) :
    inner ℂ (P.cell C x) y = inner ℂ x (P.cell C y) := by
  have hleft := (P.cell_sum C x).mapL (innerSLFlip ℂ y)
  have hright := (P.cell_sum C y).mapL (innerSL ℂ x)
  exact hleft.unique (hright.congr_fun (fun i => P.selfAdjoint i x y))

theorem cell_inter (C D : Set I) (x : H) :
    P.cell C (P.cell D x) = P.cell (C ∩ D) x := by
  classical
  apply P.eq_of_proj_eq
  intro i
  simp only [P.proj_cell, Set.mem_inter_iff]
  by_cases hc : i ∈ C <;> by_cases hd : i ∈ D <;> simp [hc, hd]

theorem cell_idempotent (C : Set I) (x : H) :
    P.cell C (P.cell C x) = P.cell C x := by rw [P.cell_inter, Set.inter_self]

theorem cell_empty : P.cell ∅ = 0 := by
  ext x
  apply P.eq_of_proj_eq
  intro i
  simp [P.proj_cell]

theorem cell_univ : P.cell Set.univ = ContinuousLinearMap.id ℂ H := by
  ext x
  apply P.eq_of_proj_eq
  intro i
  simp [P.proj_cell]

theorem cell_disjoint {C D : Set I} (h : Disjoint C D) (x : H) :
    P.cell C (P.cell D x) = 0 := by
  rw [P.cell_inter, Set.disjoint_iff_inter_eq_empty.mp h, P.cell_empty]
  rfl

/-- Every fiber is allowed to be infinite or empty. -/
def coarsenInfinite (f : I → J) : StrongAtlas H J where
  proj a := P.cell (f ⁻¹' {a})
  idempotent a x := P.cell_idempotent _ x
  orthogonal a b hab x := P.cell_disjoint (Set.disjoint_left.mpr (by
    intro i hi hj
    exact hab (hi.symm.trans hj))) x
  selfAdjoint a x y := P.cell_selfAdjoint _ x y
  strong x := (P.strong x).tsum_fiberwise f

theorem coarsenInfinite_proj (f : I → J) (a : J) :
    (P.coarsenInfinite f).proj a = P.cell (f ⁻¹' {a}) := rfl

theorem cell_energy_hasSum (C : Set I) (x : H) :
    HasSum (fun i : C => P.energy x i) (‖P.cell C x‖ ^ 2) := by
  have hn := (P.cell_sum C x).norm.pow 2
  change Tendsto (fun s : Finset C => ∑ i ∈ s, P.energy x i) atTop (𝓝 _)
  convert hn using 1
  funext s
  classical
  have h := P.partial_norm_sq (s.map (Function.Embedding.subtype C)) x
  simpa only [partialSum, Finset.sum_map, Function.Embedding.subtype_apply] using h.symm

theorem cell_energy_tsum (C : Set I) (x : H) :
    (∑' i : C, P.energy x i) = ‖P.cell C x‖ ^ 2 := (P.cell_energy_hasSum C x).tsum_eq

theorem coarsenInfinite_energy (f : I → J) (x : H) (a : J) :
    (P.coarsenInfinite f).energy x a = ∑' i : f ⁻¹' {a}, P.energy x i :=
  (P.cell_energy_tsum _ x).symm

end StrongAtlas
end KomorebiPhysics
