import Mathlib.Order.KonigLemma

/-! Finite nonempty levels suffice for a compatible branch. Transition maps need
not be surjective. This is a predicate-preserving form of Mathlib's Koenig lemma. -/
noncomputable section
namespace Komorebi.StrongArtin.ResonantBranch
universe u

variable {A : ℕ → Type u} [∀ r, Finite (A r)]

/-- Exact reduction data for a finite inverse tower. -/
structure FiniteTower (A : ℕ → Type u) where
  project : {i j : ℕ} → i ≤ j → A j → A i
  project_refl : ∀ {i} (a : A i), project (le_refl i) a = a
  project_trans : ∀ {i j k} (hij : i ≤ j) (hjk : j ≤ k) (a : A k),
    project hij (project hjk a) = project (hij.trans hjk) a

/-- Membership at each level must be preserved by genuine reduction. -/
def DownwardClosed (T : FiniteTower A) (P : ∀ r, A r → Prop) : Prop :=
  ∀ {i j} (h : i ≤ j) {a : A j}, P j a → P i (T.project h a)

/-- No chosen corrections or surjectivity of reduction on solution sets is assumed. -/
theorem exists_compatible_branch (T : FiniteTower A) (P : ∀ r, A r → Prop)
    (hP : DownwardClosed T P) (hne : ∀ r, ∃ a, P r a) :
    ∃ f : ∀ r, A r, (∀ r, P r (f r)) ∧
      ∀ {i j} (h : i ≤ j), T.project h (f j) = f i := by
  let C : ℕ → Type u := fun r => {a : A r // P r a}
  let : ∀ r, Nonempty (C r) := fun r => ⟨⟨(hne r).choose, (hne r).choose_spec⟩⟩
  let pr : {i j : ℕ} → i ≤ j → C j → C i :=
    fun h a => ⟨T.project h a.val, hP h a.property⟩
  obtain ⟨f, hf⟩ := exists_seq_forall_proj_of_forall_finite pr
    (fun _ a => Subtype.ext (T.project_refl a.val))
    (fun _ _ _ hij hjk a => Subtype.ext (T.project_trans hij hjk a.val))
    (fun _ _ => Set.toFinite _)
  refine ⟨fun r => (f r).val, fun r => (f r).property, ?_⟩
  intro i j h
  exact congrArg Subtype.val (hf h)

/-- The converse is immediate; together these give the exact existence criterion. -/
theorem compatible_branch_iff (T : FiniteTower A) (P : ∀ r, A r → Prop)
    (hP : DownwardClosed T P) :
    (∃ f : ∀ r, A r, (∀ r, P r (f r)) ∧
      ∀ {i j} (h : i ≤ j), T.project h (f j) = f i) ↔
    ∀ r, ∃ a, P r a := by
  constructor
  · rintro ⟨f, hf, _⟩ r
    exact ⟨f r, hf r⟩
  · exact exists_compatible_branch T P hP

/-- A failed infinite branch has a finite empty level. No effective bound is claimed. -/
theorem no_branch_iff_finite_obstruction (T : FiniteTower A) (P : ∀ r, A r → Prop)
    (hP : DownwardClosed T P) :
    (¬ ∃ f : ∀ r, A r, (∀ r, P r (f r)) ∧
      ∀ {i j} (h : i ≤ j), T.project h (f j) = f i) ↔
    ∃ r, ∀ a, ¬ P r a := by
  rw [compatible_branch_iff T P hP]
  simp only [not_forall, not_exists]

end Komorebi.StrongArtin.ResonantBranch
