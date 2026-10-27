import KomorebiPaperV.CompletePrunings
import KomorebiPaperV.HilbertPackets

/-! Author: Komorebi P. Literal finite node sums, synthesis and stable antichain selection. -/
namespace KomorebiPaperV.PruningSums
open KomorebiPaperV.FiniteAdaptive KomorebiPaperV.CompletePrunings
variable {A E : Type*}

def leafNodeEquiv (a : A) : Node (.leaf a) ≃ Unit where
  toFun _ := ()
  invFun _ := .root _
  left_inv v := by cases v; rfl
  right_inv u := by cases u; rfl

def branchNodeEquiv (a : A) (n : ℕ) (ch : Fin (n+1) → FiniteAdaptive.Tree A) :
    Node (.branch a n ch) ≃ Unit ⊕ (Σ i, Node (ch i)) where
  toFun v := match v with
    | .root _ => .inl ()
    | .down i w => .inr ⟨i,w⟩
  invFun v := match v with
    | .inl _ => .root _
    | .inr ⟨i,w⟩ => .down i w
  left_inv v := by cases v <;> rfl
  right_inv v := by cases v with
    | inl u => cases u; rfl
    | inr v => cases v; rfl

@[instance_reducible]
noncomputable def nodeFintype : (t : FiniteAdaptive.Tree A) → Fintype (Node t)
  | .leaf a => Fintype.ofEquiv Unit (leafNodeEquiv a).symm
  | .branch a n ch =>
      letI : ∀ i, Fintype (Node (ch i)) := fun i => nodeFintype (ch i)
      Fintype.ofEquiv (Unit ⊕ (Σ i, Node (ch i))) (branchNodeEquiv a n ch).symm

noncomputable instance (t : FiniteAdaptive.Tree A) : Fintype (Node t) := nodeFintype t

def nodeLabel : {t : FiniteAdaptive.Tree A} → Node t → A
  | t, .root _ => label t
  | _, .down _ v => nodeLabel v

theorem node_sum_branch [AddCommMonoid E] (a : A) (n : ℕ)
    (ch : Fin (n+1) → FiniteAdaptive.Tree A) (f : Node (.branch a n ch) → E) :
    ∑ v, f v = f (.root _) + ∑ i, ∑ v, f (.down i v) := by
  rw [← Equiv.sum_comp (branchNodeEquiv a n ch).symm]
  rw [Fintype.sum_sum_type, Fintype.sum_sigma]
  simp [branchNodeEquiv]

noncomputable def selectedNodes {t : FiniteAdaptive.Tree A} (q : Cut t) : Finset (Node t) :=
  {v | Selected q v}.toFinite.toFinset

theorem mem_selectedNodes {t : FiniteAdaptive.Tree A} (q : Cut t) (v : Node t) :
    v ∈ selectedNodes q ↔ Selected q v := Set.Finite.mem_toFinset _

theorem cutSum_eq_nodeSum [AddCommMonoid E] (p : A → E) {t : FiniteAdaptive.Tree A} (q : Cut t) :
    cutSum p q = ∑ v ∈ selectedNodes q, p (nodeLabel v) := by
  classical
  have hsum : ∑ v ∈ selectedNodes q, p (nodeLabel v) =
      ∑ v, if Selected q v then p (nodeLabel v) else 0 := by
    rw [← Finset.sum_filter]
    congr 1
    ext v
    simp [mem_selectedNodes]
  rw [hsum]
  clear hsum
  induction q with
  | stop t => simp [selected_stop_iff, cutSum, nodeLabel]
  | @split a n ch q ih =>
    rw [node_sum_branch]
    simp only [selected_split_root_false, ↓reduceIte, zero_add,
      selected_split_down_iff, nodeLabel, cutSum]
    exact Finset.sum_congr rfl (fun i _ => ih i)

abbrev Pruning (t : FiniteAdaptive.Tree A) := {S : Set (Node t) // Complete S}

noncomputable def nodeSum [AddCommMonoid E] (p : A → E) {t : FiniteAdaptive.Tree A}
    (S : Pruning t) : E := ∑ v ∈ S.val.toFinite.toFinset, p (nodeLabel v)

theorem pruning_nodeSum [AddCommMonoid E] (p : A → E) {t : FiniteAdaptive.Tree A} (q : Cut t) :
    nodeSum p (pruningEquiv t q) = cutSum p q := (cutSum_eq_nodeSum p q).symm

theorem antichain_synthesis [AddCommMonoid E] (p : A → E) (t : FiniteAdaptive.Tree A)
    (h : conserves p t) (S : Pruning t) : nodeSum p S = p (label t) := by
  obtain ⟨q,rfl⟩ := (pruningEquiv t).surjective S
  rw [pruning_nodeSum]
  exact cutSum_eq_root p q h

/-- Applied operator identity for every complete covering antichain. -/
theorem packet_projector_synthesis {H : Type*} [NormedAddCommGroup H] [NormedSpace ℂ H]
    (p : A → H →L[ℂ] H) (t : FiniteAdaptive.Tree A)
    (h : conserves p t) (hr : p (label t) = ContinuousLinearMap.id ℂ H)
    (S : Pruning t) (x : H) :
    nodeSum p S = ContinuousLinearMap.id ℂ H ∧
      (∑ v ∈ S.val.toFinite.toFinset, p (nodeLabel v) x) = x := by
  have hs := (antichain_synthesis p t h S).trans hr
  refine ⟨hs, ?_⟩
  have hx := congrArg (fun T : H →L[ℂ] H => T x) hs
  simpa [nodeSum] using hx

noncomputable def selected (c : A → ℝ) (t : FiniteAdaptive.Tree A) : Pruning t :=
  pruningEquiv t (best c t)

theorem selected_global_minimum (c : A → ℝ) (t : FiniteAdaptive.Tree A) (S : Pruning t) :
    nodeSum c (selected c t) ≤ nodeSum c S := by
  obtain ⟨q,rfl⟩ := (pruningEquiv t).surjective S
  simp only [selected, pruning_nodeSum]
  exact best_is_global_minimum c q

theorem antichain_perturbation (c d e : A → ℝ) (h : ∀ a, |d a-c a| ≤ e a)
    (t : FiniteAdaptive.Tree A) (S : Pruning t) :
    |nodeSum d S-nodeSum c S| ≤ envelope e t := by
  obtain ⟨q,rfl⟩ := (pruningEquiv t).surjective S
  simp only [pruning_nodeSum]
  exact cut_perturbation c d e h q

theorem antichain_envelope_attained (e : A → ℝ) (t : FiniteAdaptive.Tree A) :
    ∃ S : Pruning t, nodeSum e S = envelope e t := by
  obtain ⟨q,hq⟩ := envelope_attained e t
  exact ⟨pruningEquiv t q, (pruning_nodeSum e q).trans hq⟩

theorem antichain_selector_stable (c d e : A → ℝ) (h : ∀ a, |d a-c a| ≤ e a)
    (t : FiniteAdaptive.Tree A) (γ : ℝ)
    (hg : ∀ S : Pruning t, S ≠ selected c t → γ ≤ nodeSum c S-nodeSum c (selected c t))
    (hm : 2*envelope e t < γ) : selected d t = selected c t := by
  apply congrArg (pruningEquiv t)
  apply best_unchanged_of_gap c d e h t γ _ hm
  intro q hq
  have hne : pruningEquiv t q ≠ selected c t := fun he => hq ((pruningEquiv t).injective he)
  simpa only [selected, pruning_nodeSum] using hg (pruningEquiv t q) hne

/-- The manuscript's possibly nonadditive representation/leakage/complexity criterion. -/
def objective {t : FiniteAdaptive.Tree A} (R L K : Pruning t → ℝ) (η τ : ℝ) (S : Pruning t) : ℝ :=
  R S + η * L S + τ * K S

theorem objective_minimum (t : FiniteAdaptive.Tree A) (R L K : Pruning t → ℝ) (η τ : ℝ) :
    ∃ S : Pruning t, ∀ T, objective R L K η τ S ≤ objective R L K η τ T :=
  complete_pruning_minimum t _

theorem objective_positive_gap (t : FiniteAdaptive.Tree A) (J : Pruning t → ℝ) (S : Pruning t)
    (ho : ∃ T, T ≠ S) (hu : ∀ T, T ≠ S → J S < J T) :
    ∃ γ : ℝ, 0 < γ ∧ ∀ T, T ≠ S → γ ≤ J T-J S := by
  let : Fintype (Pruning t) := Fintype.ofEquiv (Cut t) (pruningEquiv t)
  classical
  obtain ⟨T,hT⟩ := ho
  obtain ⟨γ,hγ,hg⟩ := KomorebiPaperV.positive_gap Finset.univ J S
    ⟨T, Finset.mem_erase.mpr ⟨hT, Finset.mem_univ _⟩⟩ (fun U _ hU => hu U hU)
  exact ⟨γ,hγ,fun U hU => hg U (Finset.mem_univ _) hU⟩

theorem objective_stability (t : FiniteAdaptive.Tree A) (J J' : Pruning t → ℝ)
    (S : Pruning t) (γ ε : ℝ)
    (hg : ∀ T, T ≠ S → γ ≤ J T-J S) (he : ∀ T, |J' T-J T| ≤ ε)
    (hm : 2*ε < γ) : ∀ T, T ≠ S → J' S < J' T := by
  intro T hT
  have hs := abs_le.mp (he S)
  have ht := abs_le.mp (he T)
  have hgap := hg T hT
  linarith

theorem singleton_selector (t : FiniteAdaptive.Tree A) (S : Pruning t)
    (hs : ∀ T : Pruning t, T = S) (J : Pruning t → ℝ) :
    ∀ T, J S ≤ J T := by
  intro T
  rw [hs T]

/-- The positive gap is attained by a genuine competitor, not just an arbitrary lower bound. -/
theorem objective_gap_attained (t : FiniteAdaptive.Tree A) (J : Pruning t → ℝ) (S : Pruning t)
    (ho : ∃ T, T ≠ S) (hu : ∀ T, T ≠ S → J S < J T) :
    ∃ T : Pruning t, T ≠ S ∧ 0 < J T-J S ∧ ∀ U, U ≠ S → J T-J S ≤ J U-J S := by
  let : Fintype (Pruning t) := Fintype.ofEquiv (Cut t) (pruningEquiv t)
  classical
  obtain ⟨U,hU⟩ := ho
  obtain ⟨T,hT,hmin⟩ := KomorebiPaperV.finite_minimum (fun T => J T-J S)
    (Finset.univ.erase S) ⟨U, Finset.mem_erase.mpr ⟨hU, Finset.mem_univ _⟩⟩
  have hTS := (Finset.mem_erase.mp hT).1
  exact ⟨T,hTS,sub_pos.mpr (hu T hTS),fun V hV => hmin V
    (Finset.mem_erase.mpr ⟨hV, Finset.mem_univ _⟩)⟩

end KomorebiPaperV.PruningSums
