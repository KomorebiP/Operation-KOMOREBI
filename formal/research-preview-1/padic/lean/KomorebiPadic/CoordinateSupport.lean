import KomorebiPadic.LeastDegreeProfile

/-! # Least coordinate support for finite linear transition families
Columns are computed from the complete transition, after routing and addition.
The least closed coordinate set need not be the support of the particular orbit,
especially over a ring with zero divisors. No domain hypothesis is used.
-/
namespace KomorebiPadic
namespace CoordinateSupport

variable {R I A : Type*} [CommRing R] [Fintype I] [DecidableEq I]

structure System (R I A : Type*) [CommRing R] where
  initial : I → R
  transition : A → (I → R) →ₗ[R] (I → R)

noncomputable def seed (M : System R I A) : Finset I := by
  classical
  exact Finset.univ.filter (fun i => M.initial i ≠ 0)

noncomputable def edge (M : System R I A) (i j : I) : Prop :=
  ∃ d : A, M.transition d (Pi.single i 1) j ≠ 0

noncomputable def step (M : System R I A) (s : Finset I) : Finset I := by
  classical
  exact s ∪ seed M ∪ Finset.univ.filter (fun j => ∃ i ∈ s, edge M i j)

def Closed (M : System R I A) (s : Finset I) : Prop :=
  seed M ⊆ s ∧ ∀ i ∈ s, ∀ j, edge M i j → j ∈ s

@[simp] theorem mem_step (M : System R I A) (s : Finset I) (j : I) :
    j ∈ step M s ↔ j ∈ s ∨ M.initial j ≠ 0 ∨ ∃ i ∈ s, edge M i j := by
  classical
  simp [step, seed]

theorem subset_step (M : System R I A) (s : Finset I) : s ⊆ step M s := by
  intro j hj
  exact (mem_step M s j).mpr (Or.inl hj)

theorem step_mono (M : System R I A) {s t : Finset I} (hst : s ⊆ t) :
    step M s ⊆ step M t := by
  intro j hj
  rcases (mem_step M s j).mp hj with h | h | ⟨i, hi, he⟩
  · exact (mem_step M t j).mpr (Or.inl (hst h))
  · exact (mem_step M t j).mpr (Or.inr (Or.inl h))
  · exact (mem_step M t j).mpr (Or.inr (Or.inr ⟨i, hst hi, he⟩))

theorem step_eq_iff (M : System R I A) (s : Finset I) : step M s = s ↔ Closed M s := by
  classical
  constructor
  · intro h
    constructor
    · intro i hi
      have hn : M.initial i ≠ 0 := by simpa [seed] using hi
      exact h ▸ (mem_step M s i).mpr (Or.inr (Or.inl hn))
    · intro i hi j he
      exact h ▸ (mem_step M s j).mpr (Or.inr (Or.inr ⟨i,hi,he⟩))
  · rintro ⟨hs, he⟩
    apply Finset.Subset.antisymm _ (subset_step M s)
    intro j hj
    rcases (mem_step M s j).mp hj with h | h | ⟨i, hi, hij⟩
    · exact h
    · exact hs (by simpa [seed] using h)
    · exact he i hi j hij

noncomputable def iterate (M : System R I A) : ℕ → Finset I
  | 0 => ∅
  | n+1 => step M (iterate M n)

theorem iterate_le_closed (M : System R I A) (s : Finset I) (hs : Closed M s) (n : ℕ) :
    iterate M n ⊆ s := by
  induction n with
  | zero => exact Finset.empty_subset _
  | succ n ih =>
    exact (step_mono M ih).trans (by rw [(step_eq_iff M s).mpr hs])

theorem iterate_progress (M : System R I A) (n : ℕ)
    (hn : iterate M (n+1) ≠ iterate M n) : n+1 ≤ (iterate M (n+1)).card := by
  have hlt : (iterate M n).card < (iterate M (n+1)).card := by
    exact Finset.card_lt_card (Finset.ssubset_iff_subset_ne.mpr ⟨subset_step M _, Ne.symm hn⟩)
  induction n with
  | zero => simpa [iterate] using Nat.succ_le_of_lt hlt
  | succ n ih =>
    have hn' : iterate M (n+1) ≠ iterate M n := by
      intro h
      exact hn (congrArg (step M) h)
    have hbound := ih hn' (Finset.card_lt_card
      (Finset.ssubset_iff_subset_ne.mpr ⟨subset_step M _, Ne.symm hn'⟩))
    omega

theorem iterate_stabilizes (M : System R I A) :
    step M (iterate M (Fintype.card I)) = iterate M (Fintype.card I) := by
  by_contra hn
  have h := iterate_progress M (Fintype.card I) hn
  have hu := Finset.card_le_univ (iterate M (Fintype.card I+1))
  omega

noncomputable def least (M : System R I A) : Finset I := iterate M (Fintype.card I)

theorem least_closed (M : System R I A) : Closed M (least M) :=
  (step_eq_iff M _).mp (iterate_stabilizes M)

theorem least_subset (M : System R I A) (s : Finset I) (hs : Closed M s) : least M ⊆ s :=
  iterate_le_closed M s hs _

def Supported (s : Finset I) (x : I → R) : Prop := ∀ j, j ∉ s → x j = 0

theorem initial_supported (M : System R I A) {s : Finset I} (hs : Closed M s) :
    Supported s M.initial := by
  classical
  intro j hj
  by_contra hn
  exact hj (hs.1 (by simpa [seed] using hn))

omit [Fintype I] in
theorem single_supported {s : Finset I} {i : I} (hi : i ∈ s) :
    Supported s (Pi.single i (1 : R)) := by
  classical
  intro j hj
  have hji : j ≠ i := by intro h; subst j; exact hj hi
  simp [Ne.symm hji]

/-- Every vector is the linear combination of its coordinate columns. -/
theorem sum_single (x : I → R) : (∑ i : I, x i • Pi.single i (1 : R)) = x := by
  classical
  funext j
  simp [Finset.sum_apply, Pi.smul_apply, Pi.single_apply]

theorem transition_eq_sum (M : System R I A) (d : A) (x : I → R) (j : I) :
    M.transition d x j = ∑ i : I, x i * M.transition d (Pi.single i 1) j := by
  conv_lhs => rw [← sum_single x]
  simp only [map_sum, map_smul, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]

/-- Full coordinate-box invariance, not an assertion about one correlated orbit. -/
theorem transition_supported (M : System R I A) {s : Finset I} (hs : Closed M s)
    (d : A) {x : I → R} (hx : Supported s x) : Supported s (M.transition d x) := by
  classical
  intro j hj
  rw [transition_eq_sum]
  apply Finset.sum_eq_zero
  intro i _
  by_cases hi : i ∈ s
  · have hz : M.transition d (Pi.single i 1) j = 0 := by
      by_contra hn
      exact hj (hs.2 i hi j ⟨d, hn⟩)
    rw [hz, mul_zero]
  · rw [hx i hi, zero_mul]

/-- Column closure is exactly invariance of the entire coordinate-supported module. -/
theorem closed_iff_invariant (M : System R I A) (s : Finset I) :
    Closed M s ↔ Supported s M.initial ∧
      ∀ d x, Supported s x → Supported s (M.transition d x) := by
  classical
  constructor
  · intro hc
    exact ⟨initial_supported M hc, fun d _ hx => transition_supported M hc d hx⟩
  · rintro ⟨hi, ht⟩
    constructor
    · intro i hseed
      by_contra hn
      exact (show M.initial i ≠ 0 by simpa [seed] using hseed) (hi i hn)
    · intro i his j he
      rcases he with ⟨d, hd⟩
      by_contra hn
      exact hd (ht d _ (single_supported his) j hn)

abbrev State (s : Finset I) := {i // i ∈ s} → R

noncomputable def embed (s : Finset I) (x : State (R := R) s) : I → R := by
  classical
  exact fun i => if h : i ∈ s then x ⟨i,h⟩ else 0

def restrict (s : Finset I) (x : I → R) : State (R := R) s := fun i => x i.val

omit [Fintype I] in
@[simp] theorem restrict_embed (s : Finset I) (x : State (R := R) s) : restrict s (embed s x) = x := by
  classical
  funext i
  simp [restrict, embed, i.property]

omit [Fintype I] in
theorem embed_restrict (s : Finset I) (x : I → R) (hx : Supported s x) :
    embed s (restrict s x) = x := by
  classical
  funext i
  by_cases hi : i ∈ s
  · simp [embed, restrict, hi]
  · simp [embed, hi, hx i hi]

omit [Fintype I] in
theorem embed_injective (s : Finset I) : Function.Injective (embed (R := R) s) := by
  intro x y h
  have hh := congrArg (restrict s) h
  simpa only [restrict_embed] using hh

omit [Fintype I] in
theorem embed_supported (s : Finset I) (x : State (R := R) s) : Supported s (embed s x) := by
  classical
  intro i hi
  simp [embed, hi]

noncomputable def transition (M : System R I A) (s : Finset I) (d : A) (x : State (R := R) s) :
    State (R := R) s := restrict s (M.transition d (embed s x))

theorem transition_embedding (M : System R I A) (s : Finset I) (hs : Closed M s)
    (d : A) (x : State (R := R) s) :
    embed s (transition M s d x) = M.transition d (embed s x) :=
  embed_restrict s _ (transition_supported M hs d (embed_supported s x))

noncomputable def run (M : System R I A) : List A → (I → R) → (I → R)
  | [], x => x
  | d::ds, x => run M ds (M.transition d x)

noncomputable def runRestricted (M : System R I A) (s : Finset I) : List A → State (R := R) s → State (R := R) s
  | [], x => x
  | d::ds, x => runRestricted M s ds (transition M s d x)

theorem run_embedding (M : System R I A) (s : Finset I) (hs : Closed M s)
    (ds : List A) (x : State (R := R) s) :
    embed s (runRestricted M s ds x) = run M ds (embed s x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih =>
    simp only [runRestricted, run]
    rw [ih, transition_embedding M s hs]

theorem initial_embedding (M : System R I A) :
    embed (least M) (restrict (least M) M.initial) = M.initial :=
  embed_restrict _ _ (initial_supported M (least_closed M))

/-- Every original orbit stays in the least coordinate closure. -/
theorem run_initial_embedding (M : System R I A) (ds : List A) :
    embed (least M) (runRestricted M (least M) ds (restrict (least M) M.initial)) =
      run M ds M.initial := by
  rw [run_embedding M _ (least_closed M), initial_embedding]

/-- The least closed support is least among all invariant coordinate boxes. -/
theorem least_minimal_invariant (M : System R I A) (s : Finset I)
    (hinit : Supported s M.initial)
    (hstep : ∀ d x, Supported s x → Supported s (M.transition d x)) : least M ⊆ s :=
  least_subset M s ((closed_iff_invariant M s).mpr ⟨hinit,hstep⟩)

theorem least_unique (M : System R I A) (s : Finset I) (hs : Closed M s)
    (hmin : ∀ t, Closed M t → s ⊆ t) : s = least M :=
  Finset.Subset.antisymm (hmin _ (least_closed M)) (least_subset M s hs)

/-- No strict reduction is promised: a fully used coordinate system is possible. -/
theorem least_card_le (M : System R I A) : (least M).card ≤ Fintype.card I :=
  Finset.card_le_univ _

omit [Fintype I] in
/-- Zero-padding is exactly the restricted basis expansion. -/
theorem embed_eq_sum (s : Finset I) (x : State (R := R) s) :
    embed s x = ∑ i : {i // i ∈ s}, x i • Pi.single i.val (1 : R) := by
  classical
  funext j
  by_cases hj : j ∈ s
  · rw [Finset.sum_apply, Finset.sum_eq_single (⟨j,hj⟩ : {i // i ∈ s})]
    · simp [embed, hj]
    · intro i _ hi
      have hne : i.val ≠ j := by intro h; apply hi; exact Subtype.ext h
      simp [Pi.smul_apply, hne]
    · simp
  · rw [Finset.sum_apply]
    have hz : (∑ i : {i // i ∈ s}, (x i • Pi.single i.val (1 : R)) j) = 0 := by
      apply Finset.sum_eq_zero
      intro i _
      have hne : i.val ≠ j := by intro h; apply hj; exact h ▸ i.property
      simp [Pi.smul_apply, hne]
    simp only [embed, hj, ↓reduceDIte, hz]

omit [Fintype I] in
/-- A retained transition can be computed using only its retained matrix entries. -/
theorem transition_eq_retained_sum (M : System R I A) (s : Finset I) (d : A)
    (x : State (R := R) s) (j : {j // j ∈ s}) :
    transition M s d x j =
      ∑ i : {i // i ∈ s}, x i * M.transition d (Pi.single i.val 1) j.val := by
  unfold transition restrict
  rw [embed_eq_sum]
  simp only [map_sum, map_smul, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]

/-- A useful seed-introduction interface that does not evaluate the fixed point. -/
theorem mem_least_of_initial (M : System R I A) (i : I) (hi : M.initial i ≠ 0) : i ∈ least M := by
  classical
  exact (least_closed M).1 (by simpa [seed] using hi)

theorem mem_least_of_edge (M : System R I A) {i j : I} (hi : i ∈ least M)
    (he : edge M i j) : j ∈ least M := (least_closed M).2 i hi j he

omit [Fintype I] [DecidableEq I] in
theorem run_zero (M : System R I A) (ds : List A) : run M ds 0 = 0 := by
  induction ds with
  | nil => rfl
  | cons d ds ih => simpa only [run, map_zero] using ih

end CoordinateSupport
end KomorebiPadic
