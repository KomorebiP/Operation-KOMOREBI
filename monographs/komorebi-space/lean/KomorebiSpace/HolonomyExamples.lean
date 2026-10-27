import KomorebiSpace.HolonomyViews
import Mathlib.Tactic.FinCases

set_option autoImplicit false

/-!
# A nontrivial reflection loop with a nonzero exact core

Three views, sup-norm plane values. Two overlaps are identity and the third
reflects the second coordinate. Parallel data are precisely constant horizontal
vectors. The explicitly constructed repair has sharp residual gain 3/2.
-/
noncomputable section
namespace KomorebiSpace
namespace HolonomyTransport
namespace ReflectionTriangle

abbrev Plane := ℝ × ℝ

def reflection : Plane ≃ₗᵢ[ℝ] Plane where
  toFun z := (z.1,-z.2)
  invFun z := (z.1,-z.2)
  left_inv := by intro z; simp
  right_inv := by intro z; simp
  map_add' := by
    intro z w
    apply Prod.ext
    · rfl
    · change -(z.2+w.2) = -z.2 + -w.2
      abel
  map_smul' := by intro c z; simp
  norm_map' := by
    intro z
    change ‖(z.1,-z.2)‖=‖z‖
    simp only [Prod.norm_def, norm_neg]

def twisted (i j : Fin 3) : Prop := (i=0 ∧ j=2) ∨ (i=2 ∧ j=0)

instance (i j : Fin 3) : Decidable (twisted i j) := by unfold twisted; infer_instance

def edgeTransport (i j : Fin 3) : Plane ≃ₗᵢ[ℝ] Plane :=
  if twisted i j then reflection else LinearIsometryEquiv.refl ℝ Plane

def connection : Connection (Fin 3) Plane where
  transport := edgeTransport
  self_apply := by intro i z; fin_cases i <;> rfl
  reverse_apply := by intro i j z; fin_cases i <;> fin_cases j <;> simp [edgeTransport, twisted, reflection, Fin.ext_iff]

abbrev graph : SimpleGraph (Fin 3) := ⊤

def routing : OverlapTransport.Routing graph (0 : Fin 3) where
  path i := by
    by_cases h : (0 : Fin 3)=i
    · subst i; exact .nil
    · exact (show graph.Adj 0 i from h).toWalk
  at_anchor := rfl

def loop : graph.Walk (0 : Fin 3) 0 :=
  .cons (by decide : graph.Adj 0 1)
    (.cons (by decide : graph.Adj 1 2) (.cons (by decide : graph.Adj 2 0) .nil))

@[simp] theorem loop_transport (z : Plane) : connection.walkTransport loop z = reflection z := rfl

theorem loop_nontrivial : connection.walkTransport loop (0,1) ≠ (0,1) := by
  intro he
  have h := congrArg Prod.snd he
  norm_num [loop_transport, reflection] at h

@[simp] theorem edgeTransport_fst (i j : Fin 3) (z : Plane) :
    (connection.transport i j z).1 = z.1 := by
  change ((if twisted i j then reflection else LinearIsometryEquiv.refl ℝ Plane) z).1 = _
  split <;> rfl

@[simp] theorem edgeTransport_horizontal (i j : Fin 3) (a : ℝ) :
    connection.transport i j (a,0) = (a,0) := by
  change (if twisted i j then reflection else LinearIsometryEquiv.refl ℝ Plane) (a,0) = _
  split <;> simp [reflection]

theorem parallel_iff (x : Fin 3 → Plane) :
    connection.Parallel graph x ↔ ∃ a : ℝ, ∀ i, x i = (a,0) := by
  constructor
  · intro hx
    have h10 : x 1 = x 0 := hx 0 1 (by decide)
    have h21 : x 2 = x 1 := hx 1 2 (by decide)
    have h20 := h21.trans h10
    have hr := hx 0 2 (by decide)
    have hv : (x 0).2 = 0 := by
      have he := congrArg Prod.snd hr
      change -(x 2).2 = (x 0).2 at he
      rw [h20] at he
      linarith
    refine ⟨(x 0).1, ?_⟩
    intro i
    have hz : x 0 = ((x 0).1,0) := Prod.ext rfl hv
    fin_cases i
    · exact hz
    · exact h10.trans hz
    · exact h20.trans hz
  · rintro ⟨a,ha⟩
    intro i j _hij
    rw [ha i, ha j, edgeTransport_horizontal]

theorem fixedSpace_iff (z : Plane) :
    z ∈ Rooted.fixedSpace connection routing ↔ z.2=0 := by
  rw [← Rooted.anchor_extendable_iff]
  constructor
  · rintro ⟨x,hx,he⟩
    obtain ⟨a,ha⟩ := (parallel_iff x).mp hx
    rw [← he, ha 0]
  · intro hz
    refine ⟨fun _ => z, (parallel_iff _).mpr ?_, rfl⟩
    exact ⟨z.1, fun _ => Prod.ext rfl hz⟩

theorem nonzero_exact_section :
    connection.Parallel graph (fun _ => (7,0)) ∧
      (fun _ : Fin 3 => ((7,0) : Plane)) ≠ 0 := by
  constructor
  · exact (parallel_iff _).mpr ⟨7,fun _ => rfl⟩
  · intro h; have he := congrArg (fun x : Fin 3 → Plane => (x 0).1) h; norm_num at he

theorem inadmissible_anchor :
    ¬ ∃ x : Fin 3 → Plane, connection.Parallel graph x ∧ x 0=(7,1) := by
  intro h
  have hf := (Rooted.anchor_extendable_iff connection routing (7,1)).mp h
  have he := (fixedSpace_iff (7,1)).mp hf
  norm_num at he

/-- Preserve the compatible horizontal coordinate, not an impossible full anchor. -/
def repair (x : Fin 3 → Plane) (_i : Fin 3) : Plane := ((x 0).1,0)

theorem repair_parallel (x : Fin 3 → Plane) : connection.Parallel graph (repair x) :=
  (parallel_iff _).mpr ⟨(x 0).1, fun _ => rfl⟩

@[simp] theorem repair_protected (x : Fin 3 → Plane) : (repair x 0).1=(x 0).1 := rfl

@[simp] theorem repair_idempotent (x : Fin 3 → Plane) : repair (repair x)=repair x := rfl

theorem repair_unique (x : Fin 3 → Plane) :
    ∃! y : Fin 3 → Plane, connection.Parallel graph y ∧ (y 0).1=(x 0).1 := by
  refine ⟨repair x, ⟨repair_parallel x,rfl⟩, ?_⟩
  intro y hy
  obtain ⟨a,ha⟩ := (parallel_iff y).mp hy.1
  have he : a=(x 0).1 := by simpa only [ha 0] using hy.2
  funext i
  rw [ha i,he]
  rfl

/-- Three signed differences force a 3/2 bound on every vertical value. -/
theorem vertical_estimate (a b c ε : ℝ)
    (h01 : |b-a| ≤ ε) (h02 : |-c-a| ≤ ε) (h12 : |c-b| ≤ ε) :
    |a| ≤ (3/2:ℝ)*ε ∧ |b| ≤ (3/2:ℝ)*ε ∧ |c| ≤ (3/2:ℝ)*ε := by
  obtain ⟨ha1,ha2⟩ := abs_le.mp h01
  obtain ⟨hb1,hb2⟩ := abs_le.mp h02
  obtain ⟨hc1,hc2⟩ := abs_le.mp h12
  constructor
  · apply abs_le.mpr; constructor <;> linarith
  · constructor <;> apply abs_le.mpr <;> constructor <;> linarith

theorem edge_coordinate_bounds (x : Fin 3 → Plane) (i j : Fin 3) (h : graph.Adj i j) :
    |(connection.defect x i j).1| ≤ ‖connection.differential graph x‖ ∧
    |(connection.defect x i j).2| ≤ ‖connection.differential graph x‖ := by
  have he : ‖connection.defect x i j‖ ≤ ‖connection.differential graph x‖ :=
    norm_le_pi_norm (connection.differential graph x) ⟨(i,j),h⟩
  exact ⟨(norm_fst_le _).trans he, (norm_snd_le _).trans he⟩

theorem repair_error (x : Fin 3 → Plane) :
    ‖x-repair x‖ ≤ (3/2:ℝ) * ‖connection.differential graph x‖ := by
  let ε := ‖connection.differential graph x‖
  have hε : 0 ≤ ε := norm_nonneg _
  have h01 := edge_coordinate_bounds x 0 1 (by decide)
  have h02 := edge_coordinate_bounds x 0 2 (by decide)
  have h12 := edge_coordinate_bounds x 1 2 (by decide)
  have hv := vertical_estimate (x 0).2 (x 1).2 (x 2).2 ε h01.2 h02.2 h12.2
  apply (pi_norm_le_iff_of_nonneg (mul_nonneg (by norm_num) hε)).mpr
  intro i
  change max |(x i).1-(x 0).1| |(x i).2-0| ≤ (3/2:ℝ)*ε
  rw [sub_zero]
  apply max_le
  · fin_cases i
    · simp; positivity
    · exact h01.1.trans (by linarith)
    · exact h02.1.trans (by linarith)
  · fin_cases i
    · exact hv.1
    · exact hv.2.1
    · exact hv.2.2

/-- A nonzero horizontal signal and an input attaining the full repair gain. -/
def sharpData : Fin 3 → Plane := ![(7,3/2),(7,1/2),(7,-1/2)]

theorem sharp_residual_norm : ‖connection.differential graph sharpData‖=1 := by
  apply le_antisymm
  · apply (pi_norm_le_iff_of_nonneg zero_le_one).mpr
    intro a
    rcases a with ⟨⟨i,j⟩,h⟩
    fin_cases i <;> fin_cases j <;>
      norm_num [Connection.differential_apply, Connection.defect, connection,
        edgeTransport, twisted, reflection, sharpData, Prod.norm_def, Fin.ext_iff] at *
  · have he := norm_le_pi_norm (connection.differential graph sharpData)
      (⟨(0,1),by decide⟩ : OverlapTransport.Edges graph)
    norm_num [Connection.differential_apply, Connection.defect, connection,
      edgeTransport, twisted, sharpData, Prod.norm_def, Fin.ext_iff] at he ⊢
    exact he

theorem sharp_error : ‖sharpData-repair sharpData‖=(3/2:ℝ) := by
  apply le_antisymm
  · simpa only [sharp_residual_norm, mul_one] using repair_error sharpData
  · have he := norm_le_pi_norm (sharpData-repair sharpData) 0
    norm_num [sharpData, repair, Prod.norm_def] at he ⊢
    exact he

theorem repair_bound_sharp :
    (∀ x : Fin 3 → Plane, ‖x-repair x‖ ≤ (3/2:ℝ)*‖connection.differential graph x‖) ∧
    ‖sharpData-repair sharpData‖=(3/2:ℝ)*‖connection.differential graph sharpData‖ := by
  exact ⟨repair_error, by rw [sharp_error,sharp_residual_norm,mul_one]⟩

end ReflectionTriangle
end HolonomyTransport
end KomorebiSpace
end
