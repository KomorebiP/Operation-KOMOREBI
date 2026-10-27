import Std

/-!
Finite inverse-system compactness, proved from elementary finite-list reasoning.
Levels need not have surjective transition maps. The proof uses classical choice.
Level 0 represents the manuscript's first residual level (m = 1).
-/
set_option autoImplicit false
namespace PaperX.Compactness

/-- A finite family of downward-closed height predicates has an unbounded member
if the family has witnesses at every height. -/
theorem finite_unbounded_choice {X : Type} (P : X → Nat → Prop)
    (down : ∀ x i j, i ≤ j → P x j → P x i) (xs : List X)
    (witnesses : ∀ h, ∃ x, x ∈ xs ∧ P x h) :
    ∃ x, x ∈ xs ∧ ∀ h, P x h := by
  classical
  induction xs with
  | nil =>
    obtain ⟨x, hx, _⟩ := witnesses 0
    simp at hx
  | cons a xs ih =>
    by_cases ha : ∀ h, P a h
    · exact ⟨a, by simp, ha⟩
    · have bad : ∃ k, ¬ P a k := Classical.not_forall.mp ha
      obtain ⟨k, hk⟩ := bad
      have tail : ∀ h, ∃ x, x ∈ xs ∧ P x h := by
        intro h
        obtain ⟨x, hx, hp⟩ := witnesses (k+h)
        have hx' : x = a ∨ x ∈ xs := List.mem_cons.mp hx
        rcases hx' with hxa | hxt
        · subst x
          exact False.elim (hk (down a k (k+h) (by omega) hp))
        · exact ⟨x, hxt, down x h (k+h) (by omega) hp⟩
      obtain ⟨x, hx, hp⟩ := ih tail
      exact ⟨x, List.mem_cons_of_mem a hx, hp⟩

structure Tower where
  Level : Nat → Type
  parent : (n : Nat) → Level (n+1) → Level n

structure Branch (T : Tower) where
  value : (n : Nat) → T.Level n
  compatible : ∀ n, T.parent n (value (n+1)) = value n

/-- Finiteness is supplied by a complete finite enumeration; repetitions are allowed. -/
def FiniteLevels (T : Tower) : Prop :=
  ∀ n, ∃ xs : List (T.Level n), ∀ x, x ∈ xs

def Ext (T : Tower) (n : Nat) : Nat → T.Level n → Prop
  | 0, _ => True
  | h+1, x => ∃ y : T.Level (n+1), T.parent n y = x ∧ Ext T (n+1) h y

def Live (T : Tower) (n : Nat) (x : T.Level n) : Prop := ∀ h, Ext T n h x

theorem ext_step_down (T : Tower) (h : Nat) :
    ∀ n (x : T.Level n), Ext T n (h+1) x → Ext T n h x := by
  induction h with
  | zero => intro n x _; trivial
  | succ h ih =>
    intro n x hx
    obtain ⟨y, hy, he⟩ := hx
    exact ⟨y, hy, ih (n+1) y he⟩

theorem ext_down (T : Tower) (n : Nat) (x : T.Level n)
    (i j : Nat) (hij : i ≤ j) (hj : Ext T n j x) : Ext T n i x := by
  induction j with
  | zero =>
    have hi : i = 0 := by omega
    subst i
    trivial
  | succ j ih =>
    by_cases heq : i = j+1
    · simpa [heq] using hj
    · exact ih (by omega) (ext_step_down T j n x hj)

theorem ext_somewhere (T : Tower) (nonempty : ∀ n, Nonempty (T.Level n))
    (h : Nat) : ∀ n, ∃ x : T.Level n, Ext T n h x := by
  induction h with
  | zero =>
    intro n
    obtain ⟨x⟩ := nonempty n
    exact ⟨x, trivial⟩
  | succ h ih =>
    intro n
    obtain ⟨y, hy⟩ := ih (n+1)
    exact ⟨T.parent n y, y, rfl, hy⟩

theorem live_somewhere (T : Tower) (finite : FiniteLevels T)
    (nonempty : ∀ n, Nonempty (T.Level n)) (n : Nat) :
    ∃ x : T.Level n, Live T n x := by
  obtain ⟨xs, cover⟩ := finite n
  have witnesses : ∀ h, ∃ x, x ∈ xs ∧ Ext T n h x := by
    intro h
    obtain ⟨x, hx⟩ := ext_somewhere T nonempty h n
    exact ⟨x, cover x, hx⟩
  obtain ⟨x, _, hx⟩ := finite_unbounded_choice (fun x h => Ext T n h x)
    (fun x i j hij hj => ext_down T n x i j hij hj) xs witnesses
  exact ⟨x, hx⟩

theorem live_child (T : Tower) (finite : FiniteLevels T)
    (n : Nat) (x : T.Level n) (hx : Live T n x) :
    ∃ y : T.Level (n+1), T.parent n y = x ∧ Live T (n+1) y := by
  obtain ⟨xs, cover⟩ := finite (n+1)
  let P : T.Level (n+1) → Nat → Prop :=
    fun y h => T.parent n y = x ∧ Ext T (n+1) h y
  have witnesses : ∀ h, ∃ y, y ∈ xs ∧ P y h := by
    intro h
    obtain ⟨y, hy, he⟩ := hx (h+1)
    exact ⟨y, cover y, hy, he⟩
  have down : ∀ y i j, i ≤ j → P y j → P y i := by
    intro y i j hij hj
    exact ⟨hj.1, ext_down T (n+1) y i j hij hj.2⟩
  obtain ⟨y, _, hy⟩ := finite_unbounded_choice P down xs witnesses
  exact ⟨y, (hy 0).1, fun h => (hy h).2⟩

noncomputable def chooseChild (T : Tower) (finite : FiniteLevels T)
    (n : Nat) (x : {x : T.Level n // Live T n x}) :
    {y : T.Level (n+1) // Live T (n+1) y} :=
  ⟨Classical.choose (live_child T finite n x.1 x.2),
    (Classical.choose_spec (live_child T finite n x.1 x.2)).2⟩

theorem chooseChild_parent (T : Tower) (finite : FiniteLevels T)
    (n : Nat) (x : {x : T.Level n // Live T n x}) :
    T.parent n (chooseChild T finite n x).1 = x.1 :=
  (Classical.choose_spec (live_child T finite n x.1 x.2)).1

noncomputable def branchNode (T : Tower) (finite : FiniteLevels T)
    (start : {x : T.Level 0 // Live T 0 x}) :
    (n : Nat) → {x : T.Level n // Live T n x}
  | 0 => start
  | n+1 => chooseChild T finite n (branchNode T finite start n)

/-- A finite nonempty tower of sets with total reduction maps has a compatible branch. -/
theorem finite_branch_compactness (T : Tower) (finite : FiniteLevels T)
    (nonempty : ∀ n, Nonempty (T.Level n)) : Nonempty (Branch T) := by
  classical
  obtain ⟨x, hx⟩ := live_somewhere T finite nonempty 0
  let start : {x : T.Level 0 // Live T 0 x} := ⟨x, hx⟩
  exact ⟨{
    value := fun n => (branchNode T finite start n).1
    compatible := fun n => chooseChild_parent T finite n (branchNode T finite start n)
  }⟩

/-- Any empty level prevents completion, not only an empty residual level. -/
theorem empty_level_obstruction (T : Tower) (n : Nat)
    (empty : ¬ Nonempty (T.Level n)) : ¬ Nonempty (Branch T) := by
  rintro ⟨b⟩
  exact empty ⟨b.value n⟩

/-- For finite levels, arbitrary-depth nonemptiness is equivalent to branch existence. -/
theorem branch_iff_levels_nonempty (T : Tower) (finite : FiniteLevels T) :
    Nonempty (Branch T) ↔ ∀ n, Nonempty (T.Level n) := by
  constructor
  · rintro ⟨b⟩ n
    exact ⟨b.value n⟩
  · exact finite_branch_compactness T finite

/-- Choice can assemble one compatible branch per index, without asserting that
any of the level-nonemptiness hypotheses is automatically satisfied. -/
theorem indexed_finite_completion {I : Type} (T : I → Tower)
    (finite : ∀ i, FiniteLevels (T i))
    (nonempty : ∀ i n, Nonempty ((T i).Level n)) :
    Nonempty ((i : I) → Branch (T i)) := by
  classical
  exact ⟨fun i => Classical.choice (finite_branch_compactness (T i) (finite i) (nonempty i))⟩

/-- One missing level in one required tower prevents an indexed completion. -/
theorem indexed_empty_level_obstruction {I : Type} (T : I → Tower)
    (i : I) (n : Nat) (empty : ¬ Nonempty ((T i).Level n)) :
    ¬ Nonempty ((j : I) → Branch (T j)) := by
  rintro ⟨b⟩
  exact empty ⟨(b i).value n⟩

end PaperX.Compactness
