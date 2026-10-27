import KomorebiLSM.FiniteInstrument
import Mathlib.LinearAlgebra.FiniteDimensional.Basic

/-! P27: the canonical behavior space is built from actual future-test columns.
A shift on the full test-function space restricts to their span. -/
set_option autoImplicit false
namespace Komorebi.LSM.Behavior
open scoped BigOperators
open FiniteInstruments
variable {S : Type*}

/-- Chronological history followed by a prescribed future test. -/
def column (f : List S → ℝ) (h : List S) : List S → ℝ := fun t => f (h ++ t)

/-- The state space is a span of columns, not a supplied latent representation. -/
noncomputable def space (f : List S → ℝ) : Submodule ℝ (List S → ℝ) :=
  Submodule.span ℝ (Set.range (column f))

noncomputable def history (f : List S → ℝ) (h : List S) : space f :=
  ⟨column f h, Submodule.subset_span ⟨h,rfl⟩⟩

@[simp] theorem history_apply (f : List S → ℝ) (h t : List S) :
    (history f h : List S → ℝ) t = f (h ++ t) := rfl

/-- Prepending a symbol to a test appends that symbol to its history column. -/
def shift (s : S) : (List S → ℝ) →ₗ[ℝ] (List S → ℝ) where
  toFun v t := v (s :: t)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

@[simp] theorem shift_column (f : List S → ℝ) (s : S) (h : List S) :
    shift s (column f h) = column f (h ++ [s]) := by
  funext t
  simp [shift, column, List.append_assoc]

theorem shift_mem (f : List S → ℝ) (s : S) (v : List S → ℝ)
    (hv : v ∈ space f) : shift s v ∈ space f := by
  induction hv using Submodule.span_induction with
  | mem v hv =>
    obtain ⟨h,rfl⟩ := hv
    rw [shift_column]
    exact Submodule.subset_span ⟨h ++ [s],rfl⟩
  | zero => simp
  | add x y hx hy ihx ihy => simpa using (space f).add_mem ihx ihy
  | smul a x hx ih => simpa using (space f).smul_mem a ih

noncomputable def branch (f : List S → ℝ) (s : S) : space f →ₗ[ℝ] space f :=
  (shift s).restrict (shift_mem f s)

@[simp] theorem branch_apply (f : List S → ℝ) (s : S) (v : space f) (t : List S) :
    (branch f s v : List S → ℝ) t = (v : List S → ℝ) (s :: t) := rfl

@[simp] theorem branch_history (f : List S → ℝ) (s : S) (h : List S) :
    branch f s (history f h) = history f (h ++ [s]) := by
  apply Subtype.ext
  exact shift_column f s h

noncomputable def mass (f : List S → ℝ) : space f →ₗ[ℝ] ℝ :=
  (LinearMap.proj []).comp (space f).subtype

@[simp] theorem mass_apply (f : List S → ℝ) (v : space f) :
    mass f v = (v : List S → ℝ) [] := rfl

@[simp] theorem mass_history (f : List S → ℝ) (h : List S) :
    mass f (history f h) = f h := by simp

/-- The head of a word acts first. -/
theorem word_history (f : List S → ℝ) (w h : List S) :
    wordAction (branch f) w (history f h) = history f (h ++ w) := by
  induction w generalizing h with
  | nil => simp
  | cons s w ih =>
    simp only [wordAction_cons, LinearMap.comp_apply, branch_history, ih]
    congr 1
    simp [List.append_assoc]

theorem word_probability (f : List S → ℝ) (w : List S) :
    mass f (wordAction (branch f) w (history f [])) = f w := by
  rw [word_history]
  simp

/-- Every coordinate is a declared future-test readout. -/
theorem test_evaluation (f : List S → ℝ) (w : List S) (v : space f) :
    mass f (wordAction (branch f) w v) = (v : List S → ℝ) w := by
  induction w generalizing v with
  | nil => rfl
  | cons s w ih =>
    change mass f (wordAction (branch f) w (branch f s v)) = _
    exact ih (branch f s v)

/-- A normalized behavior state gives conditional test values. -/
theorem conditional_test (f : List S → ℝ) (h t : List S) :
    mass f (wordAction (branch f) t ((f h)⁻¹ • history f h)) =
      f (h ++ t) / f h := by
  rw [map_smul, map_smul, word_history, mass_history]
  simp [div_eq_mul_inv, mul_comm]

theorem conditional_mass (f : List S → ℝ) (h : List S) (hf : f h ≠ 0) :
    mass f ((f h)⁻¹ • history f h) = 1 := by simp [hf]

/-- Equal normalized columns are exactly equal conditional predictions. -/
theorem conditional_equivalence (f : List S → ℝ) (h k : List S) :
    (f h)⁻¹ • history f h = (f k)⁻¹ • history f k ↔
      ∀ t, f (h ++ t) / f h = f (k ++ t) / f k := by
  constructor
  · intro he t
    have hv := congrArg (fun v : space f => mass f (wordAction (branch f) t v)) he
    simpa only [conditional_test] using hv
  · intro he
    apply Subtype.ext
    funext t
    simpa only [Submodule.coe_smul, Pi.smul_apply, history_apply, smul_eq_mul,
      div_eq_mul_inv, mul_comm] using he t

/-- Exact linear models have operators and boundary vectors, not assumed states. -/
structure Realization (f : List S → ℝ) (E : Type*) [AddCommGroup E] [Module ℝ E] where
  initial : E
  operator : S → E →ₗ[ℝ] E
  readout : E →ₗ[ℝ] ℝ
  correct : ∀ w, readout (wordAction operator w initial) = f w

noncomputable def canonical (f : List S → ℝ) : Realization f (space f) where
  initial := history f []
  operator := branch f
  readout := mass f
  correct := word_probability f

namespace Realization
variable {f : List S → ℝ} {E : Type*} [AddCommGroup E] [Module ℝ E]

noncomputable def state (r : Realization f E) (h : List S) : E :=
  wordAction r.operator h r.initial

noncomputable def reachable (r : Realization f E) : Submodule ℝ E :=
  Submodule.span ℝ (Set.range r.state)

def IsReachable (r : Realization f E) : Prop := r.reachable = ⊤

noncomputable def observe (r : Realization f E) : E →ₗ[ℝ] (List S → ℝ) :=
  LinearMap.pi (fun t => r.readout.comp (wordAction r.operator t))

def IsObservable (r : Realization f E) : Prop := Function.Injective r.observe

@[simp] theorem observe_apply (r : Realization f E) (x : E) (t : List S) :
    r.observe x t = r.readout (wordAction r.operator t x) := rfl

@[simp] theorem observe_state (r : Realization f E) (h : List S) :
    r.observe (r.state h) = column f h := by
  funext t
  simpa only [observe_apply, state, column, wordAction_append, LinearMap.comp_apply]
    using r.correct (h ++ t)

@[simp] theorem observe_operator (r : Realization f E) (s : S) (x : E) :
    r.observe (r.operator s x) = shift s (r.observe x) := rfl

theorem observe_mem (r : Realization f E) (x : E) (hx : x ∈ r.reachable) :
    r.observe x ∈ space f := by
  induction hx using Submodule.span_induction with
  | mem x hx =>
    obtain ⟨h,rfl⟩ := hx
    rw [observe_state]
    exact Submodule.subset_span ⟨h,rfl⟩
  | zero => simp
  | add x y hx hy ihx ihy => simpa using (space f).add_mem ihx ihy
  | smul a x hx ih => simpa using (space f).smul_mem a ih

noncomputable def toBehavior (r : Realization f E) : r.reachable →ₗ[ℝ] space f :=
  (r.observe.domRestrict r.reachable).codRestrict (space f) (fun x => r.observe_mem x x.property)

/-- Every behavior vector has a preimage in the reachable part of any realization. -/
theorem toBehavior_surjective (r : Realization f E) : Function.Surjective r.toBehavior := by
  intro v
  obtain ⟨v,hv⟩ := v
  have hpre : ∃ x : r.reachable, r.observe x = v := by
    induction hv using Submodule.span_induction with
    | mem v hv =>
      obtain ⟨h,rfl⟩ := hv
      exact ⟨⟨r.state h,Submodule.subset_span ⟨h,rfl⟩⟩,r.observe_state h⟩
    | zero => exact ⟨0,map_zero _⟩
    | add x y hx hy ihx ihy =>
      obtain ⟨a,ha⟩ := ihx
      obtain ⟨b,hb⟩ := ihy
      exact ⟨a+b,by simpa using (map_add r.observe (a : E) (b : E)).trans (congrArg₂ (·+·) ha hb)⟩
    | smul c x hx ih =>
      obtain ⟨a,ha⟩ := ih
      exact ⟨c • a,by simpa using (map_smul r.observe c (a : E)).trans (congrArg (c • ·) ha)⟩
  obtain ⟨x,hx⟩ := hpre
  exact ⟨x,Subtype.ext hx⟩

/-- The rank of the complete history/test behavior cannot exceed any finite model. -/
theorem behavior_dimension_le [FiniteDimensional ℝ E] (r : Realization f E) :
    Module.finrank ℝ (space f) ≤ Module.finrank ℝ E := by
  exact (LinearMap.finrank_le_finrank_of_surjective r.toBehavior_surjective).trans
    (Submodule.finrank_le r.reachable)

/-- A reachable observable model is linearly isomorphic to the canonical space. -/
noncomputable def equiv (r : Realization f E) (hr : r.IsReachable) (ho : r.IsObservable) :
    E ≃ₗ[ℝ] space f :=
  LinearEquiv.ofBijective
    (r.observe.codRestrict (space f) (fun x => r.observe_mem x (by rw [hr]; trivial)))
    ⟨fun x y h => ho (congrArg Subtype.val h), by
      intro v
      obtain ⟨x,hx⟩ := r.toBehavior_surjective v
      exact ⟨x, hx⟩⟩

@[simp] theorem equiv_apply (r : Realization f E) (hr : r.IsReachable) (ho : r.IsObservable)
    (x : E) (t : List S) :
    (r.equiv hr ho x : List S → ℝ) t = r.readout (wordAction r.operator t x) := rfl

theorem equiv_initial (r : Realization f E) (hr : r.IsReachable) (ho : r.IsObservable) :
    r.equiv hr ho r.initial = history f [] := by
  apply Subtype.ext
  funext t
  exact r.correct t

theorem equiv_operator (r : Realization f E) (hr : r.IsReachable) (ho : r.IsObservable)
    (s : S) (x : E) : r.equiv hr ho (r.operator s x) = branch f s (r.equiv hr ho x) := by
  apply Subtype.ext
  rfl

theorem equiv_mass (r : Realization f E) (hr : r.IsReachable) (ho : r.IsObservable)
    (x : E) : mass f (r.equiv hr ho x) = r.readout x := rfl

end Realization
end Komorebi.LSM.Behavior
