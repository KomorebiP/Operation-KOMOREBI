import PaperX.SeedConsequences

/-!
The finite-graph hypothesis cannot be dropped. One isolated source plus an
infinite descending chain has exactly one source component but no finite cover.
-/
set_option autoImplicit false
namespace PaperX.SeedBoundary

open PaperX.DirectedSeeds

def descendingEdge (a b : Option ℕ) : Prop :=
  ∃ n : ℕ, a = some (n+1) ∧ b = some n

def height : Option ℕ → ℕ
  | none => 0
  | some n => n+1

theorem height_injective : Function.Injective height := by
  intro a b h
  cases a <;> cases b <;> simp_all [height]

theorem reach_height {a b : Option ℕ} (h : Reach descendingEdge a b) :
    height b ≤ height a := by
  induction h with
  | refl => exact le_rfl
  | @tail b c _ hbc ih =>
    obtain ⟨n, rfl, rfl⟩ := hbc
    simp only [height] at *
    omega

theorem component_singleton (a b : Option ℕ) :
    component descendingEdge a = component descendingEdge b ↔ a = b := by
  constructor
  · intro h
    obtain ⟨hab, hba⟩ := (component_eq_iff descendingEdge a b).1 h
    exact height_injective (Nat.le_antisymm (reach_height hba) (reach_height hab))
  · rintro rfl
    rfl

theorem source_exactly_none (v : Option ℕ) :
    IsSource descendingEdge (component descendingEdge v) ↔ v = none := by
  rw [source_iff]
  constructor
  · intro h
    cases v with
    | none => rfl
    | some n =>
      have hpath : Reach descendingEdge (some (n+1)) (some n) :=
        .single ⟨n, rfl, rfl⟩
      have hh := reach_height (h _ hpath)
      simp only [height] at hh
      omega
  · rintro rfl a ha
    rcases ha.cases_tail with h | ⟨c, _, n, _, impossible⟩
    · subst a
      exact .refl
    · cases impossible

def isolatedSource : Source descendingEdge :=
  ⟨component descendingEdge none, (source_exactly_none none).2 rfl⟩

theorem only_source (c : Source descendingEdge) : c = isolatedSource := by
  have hrep := component_representative descendingEdge c.val
  have hs : IsSource descendingEdge
      (component descendingEdge (representative descendingEdge c.val)) := by
    rw [hrep]
    exact c.property
  have hn := (source_exactly_none _).1 hs
  apply Subtype.ext
  change c.val = component descendingEdge none
  rw [← hrep, hn]

def sourceEquivUnit : Source descendingEdge ≃ Unit where
  toFun := fun _ => ()
  invFun := fun _ => isolatedSource
  left_inv := fun c => (only_source c).symm
  right_inv := fun x => by cases x; rfl

theorem exactly_one_source : Nat.card (Source descendingEdge) = 1 := by
  rw [Nat.card_congr sourceEquivUnit]
  simp

/-- There is no finite generating set, despite the unique source component. -/
theorem no_finite_cover (S : Finset (Option ℕ)) : ¬ Covers descendingEdge S := by
  intro hcover
  let N := ∑ v ∈ S, height v
  obtain ⟨s, hs, hpath⟩ := hcover (some N)
  have hupper : height s ≤ N := Finset.single_le_sum (fun v _ => Nat.zero_le (height v)) hs
  have hlower := reach_height hpath
  change N+1 ≤ height s at hlower
  omega

theorem no_universal_seed : ¬ ∃ s : Option ℕ, ∀ v, Reach descendingEdge s v := by
  rintro ⟨s, hs⟩
  exact no_finite_cover {s} (fun v => ⟨s, by simp, hs v⟩)

end PaperX.SeedBoundary
