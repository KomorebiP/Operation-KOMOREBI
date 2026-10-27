import KomorebiVerification.PaperII.NestedRefinement

/-!
# Supported common refinements

Explicit constructions for the expanded Paper II common-refinement theorem.
The inherited `LinearProjectorFamily` permits zero members. Nonzero hypotheses
are therefore stated, and zero products are removed by an actual subtype.
No arithmetic, spectral, analytic or executable-algorithm conclusion is claimed.
-/

set_option autoImplicit false

noncomputable section

namespace Komorebi.PaperII.CommonRefinement

open Komorebi.Foundation Komorebi.PaperII.NestedRefinement

universe u v w x y
variable {R : Type u} {M : Type v} [Semiring R] [AddCommMonoid M] [Module R M]
variable {ι : Type w} {κ : Type x} {τ : Type y}
variable [Fintype ι] [Fintype κ] [Fintype τ]

/-- Nonzero members, not a nonzero ambient-module assumption. -/
def Nonzero (P : LinearProjectorFamily R M ι) : Prop := ∀ i, P.proj i ≠ 0

/-- All cross pairs commute, stated pointwise on the original module. -/
def CrossCommutes (P : LinearProjectorFamily R M ι)
    (Q : LinearProjectorFamily R M κ) : Prop :=
  ∀ i j z, P.proj i (Q.proj j z) = Q.proj j (P.proj i z)

/-- The actual support of a finite projector family. -/
abbrev Support (P : LinearProjectorFamily R M ι) := {i : ι // P.proj i ≠ 0}

instance supportFintype (P : LinearProjectorFamily R M ι) : Fintype (Support P) := by
  classical
  unfold Support
  infer_instance

/-- Removing zero projectors preserves the identity decomposition. -/
theorem support_complete (P : LinearProjectorFamily R M ι) (z : M) :
    (∑ i : Support P, P.proj i.val z) = z := by
  classical
  change (∑ i : {i : ι // P.proj i ≠ 0}, P.proj i.val z) = z
  rw [← Finset.sum_subtype (Finset.univ.filter (fun i => P.proj i ≠ 0))
    (by intro i; simp) (fun i => P.proj i z), Finset.sum_filter]
  calc
    (∑ i, if P.proj i ≠ 0 then P.proj i z else 0) = ∑ i, P.proj i z := by
      apply Finset.sum_congr rfl
      intro i _
      by_cases h : P.proj i = 0 <;> simp [h]
    _ = z := P.complete z

/-- A zero-free family on its supported index subtype. -/
def supported (P : LinearProjectorFamily R M ι) :
    LinearProjectorFamily R M (Support P) where
  proj i := P.proj i.val
  idempotent i := P.idempotent i.val
  orthogonal := by
    intro i j h z
    exact P.orthogonal (fun hij => h (Subtype.ext hij)) z
  complete := support_complete P

theorem supported_nonzero (P : LinearProjectorFamily R M ι) : Nonzero (supported P) :=
  fun i => i.property

/-- The full binary product family, before removing zero members. -/
def product (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) : LinearProjectorFamily R M (ι × κ) where
  proj k := (P.proj k.1).comp (Q.proj k.2)
  idempotent := by
    intro k z
    change P.proj k.1 (Q.proj k.2 (P.proj k.1 (Q.proj k.2 z))) = _
    rw [← h k.1 k.2 (Q.proj k.2 z), P.idempotent, Q.idempotent]
    rfl
  orthogonal := by
    intro k l hkl z
    change P.proj k.1 (Q.proj k.2 (P.proj l.1 (Q.proj l.2 z))) = 0
    rw [← h l.1 k.2 (Q.proj l.2 z)]
    by_cases hi : k.1 = l.1
    · have hj : k.2 ≠ l.2 := fun hj => hkl (Prod.ext hi hj)
      rw [hi, P.idempotent, Q.orthogonal hj, map_zero]
    · exact P.orthogonal hi _
  complete := by
    intro z
    simp only [Fintype.sum_prod_type, LinearMap.comp_apply]
    simp_rw [← map_sum, Q.complete]
    exact P.complete z

/-- The nonzero product family that appears in the manuscript. -/
def common (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) := supported (product P Q h)

/-- Construct a refinement from absorption; nonzero coarse members force surjectivity. -/
theorem refines_of_absorption [DecidableEq ι]
    (P : LinearProjectorFamily R M ι) (S : LinearProjectorFamily R M κ)
    (hn : Nonzero P) (parent : κ → ι)
    (ha : ∀ i a z, P.proj i (S.proj a z) = if parent a = i then S.proj a z else 0) :
    Refines P S parent := by
  classical
  have hf : ∀ i, P.proj i = ∑ a ∈ children parent i, S.proj a := by
    intro i
    ext z
    simp only [LinearMap.sum_apply]
    calc
      P.proj i z = P.proj i (∑ a, S.proj a z) := by rw [S.complete]
      _ = ∑ a, P.proj i (S.proj a z) := by rw [map_sum]
      _ = ∑ a, if parent a = i then S.proj a z else 0 := by
        apply Finset.sum_congr rfl
        intro a _
        exact ha i a z
      _ = ∑ a ∈ children parent i, S.proj a z := by
        simp only [children, Finset.sum_filter]
        apply Finset.sum_congr rfl
        intro a _
        split_ifs <;> rfl
  refine ⟨?_, hf⟩
  intro i
  by_contra he
  have he' : ∀ a, parent a ≠ i := by simpa only [not_exists] using he
  have hc : children parent i = ∅ := by
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro a ha'
    exact he' a ((mem_children parent i a).mp ha')
  exact hn i (by rw [hf i, hc, Finset.sum_empty])

/-- The first coordinate is an onto parent map, including support pruning. -/
theorem common_refines_left
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) (hn : Nonzero P) :
    Refines P (common P Q h) (fun k => k.val.1) := by
  classical
  apply refines_of_absorption P (common P Q h) hn
  intro i k z
  change P.proj i (P.proj k.val.1 (Q.proj k.val.2 z)) =
    if k.val.1 = i then P.proj k.val.1 (Q.proj k.val.2 z) else 0
  by_cases hk : k.val.1 = i
  · simp only [hk, ↓reduceIte]
    exact P.idempotent i _
  · simp only [hk, ↓reduceIte]
    exact P.orthogonal (Ne.symm hk) _

/-- The second coordinate is an onto parent map, including support pruning. -/
theorem common_refines_right
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) (hn : Nonzero Q) :
    Refines Q (common P Q h) (fun k => k.val.2) := by
  classical
  apply refines_of_absorption Q (common P Q h) hn
  intro j k z
  change Q.proj j (P.proj k.val.1 (Q.proj k.val.2 z)) =
    if k.val.2 = j then P.proj k.val.1 (Q.proj k.val.2 z) else 0
  rw [← h k.val.1 j (Q.proj k.val.2 z)]
  by_cases hk : k.val.2 = j
  · simp only [hk, ↓reduceIte, Q.idempotent]
  · simp only [hk, ↓reduceIte]
    rw [Q.orthogonal (Ne.symm hk), map_zero]

/-- The joint parent has nonzero product because it absorbs the nonzero child. -/
theorem joint_product_nonzero
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (S : LinearProjectorFamily R M τ) (hn : Nonzero S)
    (p : τ → ι) (q : τ → κ) (hp : Refines P S p) (hq : Refines Q S q) (a : τ) :
    (P.proj (p a)).comp (Q.proj (q a)) ≠ 0 := by
  intro hz
  have hab : ((P.proj (p a)).comp (Q.proj (q a))).comp (S.proj a) = S.proj a := by
    ext z
    simp only [LinearMap.comp_apply]
    rw [hq.coarse_fine_apply_eq_self, hp.coarse_fine_apply_eq_self]
  rw [hz, LinearMap.zero_comp] at hab
  exact hn a hab.symm

/-- Construct the unique joint parent as an element of the supported product subtype. -/
def jointParent
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) (S : LinearProjectorFamily R M τ) (hn : Nonzero S)
    (p : τ → ι) (q : τ → κ) (hp : Refines P S p) (hq : Refines Q S q) :
    τ → Support (product P Q h) :=
  fun a => ⟨(p a, q a), joint_product_nonzero P Q S hn p q hp hq a⟩

/-- Every nonzero common refinement refines the explicit supported product family. -/
theorem common_coarsest
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) (S : LinearProjectorFamily R M τ) (hn : Nonzero S)
    (p : τ → ι) (q : τ → κ) (hp : Refines P S p) (hq : Refines Q S q) :
    Refines (common P Q h) S (jointParent P Q h S hn p q hp hq) := by
  classical
  apply refines_of_absorption _ S (supported_nonzero _) _
  intro k a z
  change P.proj k.val.1 (Q.proj k.val.2 (S.proj a z)) = _
  by_cases hk : jointParent P Q h S hn p q hp hq a = k
  · simp only [hk, ↓reduceIte]
    rw [← hk]
    change P.proj (p a) (Q.proj (q a) (S.proj a z)) = _
    rw [hq.coarse_fine_apply_eq_self, hp.coarse_fine_apply_eq_self]
  · simp only [hk, ↓reduceIte]
    by_cases hqk : q a = k.val.2
    · have hqa : Q.proj k.val.2 (S.proj a z) = S.proj a z := by
        simpa only [LinearMap.comp_apply] using
          LinearMap.congr_fun (hq.coarse_comp_fine_eq_self hqk) z
      rw [hqa]
      have hpk : p a ≠ k.val.1 := by
        intro hpk
        exact hk (Subtype.ext (Prod.ext hpk hqk))
      simpa only [LinearMap.comp_apply, LinearMap.zero_apply] using
        LinearMap.congr_fun (hp.coarse_comp_fine_eq_zero hpk) z
    · have hqa : Q.proj k.val.2 (S.proj a z) = 0 := by
        simpa only [LinearMap.comp_apply, LinearMap.zero_apply] using
          LinearMap.congr_fun (hq.coarse_comp_fine_eq_zero hqk) z
      rw [hqa, map_zero]

/-- Nonzero children cannot have two different parents in one packet system. -/
theorem parent_unique
    (P : LinearProjectorFamily R M ι) (S : LinearProjectorFamily R M κ)
    (hn : Nonzero S) (p q : κ → ι) (hp : Refines P S p) (hq : Refines P S q) : p = q := by
  funext a
  by_contra h
  have hself := hp.coarse_comp_fine_eq_self (a := p a) (b := a) rfl
  have hzero := hq.coarse_comp_fine_eq_zero (a := p a) (b := a) (Ne.symm h)
  exact hn a (hself.symm.trans hzero)

/-- A supplied common refinement forces all original cross pairs to commute. -/
theorem commutes_of_common_refinement
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (S : LinearProjectorFamily R M τ) (p : τ → ι) (q : τ → κ)
    (hp : Refines P S p) (hq : Refines Q S q) : CrossCommutes P Q := by
  classical
  intro i j z
  conv_lhs => rw [← S.complete z]
  conv_rhs => rw [← S.complete z]
  simp only [map_sum]
  apply Finset.sum_congr rfl
  intro a _
  have hP : P.proj i (S.proj a z) = if p a = i then S.proj a z else 0 := by
    by_cases hpi : p a = i
    · simpa only [LinearMap.comp_apply, hpi, ↓reduceIte] using
        LinearMap.congr_fun (hp.coarse_comp_fine_eq_self hpi) z
    · simpa only [LinearMap.comp_apply, hpi, ↓reduceIte, LinearMap.zero_apply] using
        LinearMap.congr_fun (hp.coarse_comp_fine_eq_zero hpi) z
  have hQ : Q.proj j (S.proj a z) = if q a = j then S.proj a z else 0 := by
    by_cases hqj : q a = j
    · simpa only [LinearMap.comp_apply, hqj, ↓reduceIte] using
        LinearMap.congr_fun (hq.coarse_comp_fine_eq_self hqj) z
    · simpa only [LinearMap.comp_apply, hqj, ↓reduceIte, LinearMap.zero_apply] using
        LinearMap.congr_fun (hq.coarse_comp_fine_eq_zero hqj) z
  by_cases hpi : p a = i <;> by_cases hqj : q a = j <;>
    simp only [hpi, hqj, ↓reduceIte] at hP hQ <;>
    simp only [hP, hQ, map_zero]

end Komorebi.PaperII.CommonRefinement
