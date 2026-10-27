import MachineTheory.SafeEnding

/-! Core 8.3 with genuine history-dependent policies and all-path semantics.
A configuration retains past state/action pairs and its current observed state.
An ending guarantee includes both local safety/legality at every finite prefix
and the absence of an infinite non-ending execution. Thus deadlock cannot win
by making the set of infinite paths empty. The stop input is observed before
selection of the next action and retains the full pre-command history.
-/
namespace Komorebi.MachineTheory.SafeEnding

universe u v w
variable {Z : Type u} {A : Type v}

abbrev Config (Z : Type u) (A : Type v) := List (Z × A) × Z
abbrev Strategy (Z : Type u) (A : Type v) := Config Z A → Option A

def start (x : Z) : Config Z A := ([], x)

/-- Finite reachability contains all legal adversarial successors. -/
inductive Reach {C : Type w} (r : C → C → Prop) (c : C) : C → Prop
  | refl : Reach r c c
  | tail {d e : C} : Reach r c d → r d e → Reach r c e

/-- The policy selects one action from the full history before the successor. -/
def edge (M : Model Z A) (catalogue : Z → Finset A) (σ : Strategy Z A)
    (c d : Config Z A) : Prop :=
  ∃ a, σ c = some a ∧ a ∈ catalogue c.2 ∧
    d.1 = (c.2, a) :: c.1 ∧ d.2 ∈ M.post c.2 a

def endEdge (M : Model Z A) (σ : Strategy Z A) (c d : Config Z A) : Prop :=
  c.2 ∉ M.goal ∧ edge M M.finish σ c d

def runEdge (M : Model Z A) (σ : Strategy Z A) := edge M M.run σ

/-- Universal total correctness until the first goal arrival. -/
structure EndingGuarantee (M : Model Z A) (σ : Strategy Z A) (x : Z) : Prop where
  total : ∀ c, Reach (endEdge M σ) (start x) c →
    c.2 ∈ M.safe ∧ (c.2 ∉ M.goal → ∃ a, σ c = some a ∧ a ∈ M.finish c.2)
  noInfinite : ∀ p : ℕ → Config Z A, p 0 = start x →
    (∀ n, endEdge M σ (p n) (p (n + 1))) → False

/-- The running guarantee is local at every legal prefix, so it forbids deadlock. -/
def RunningGuarantee (M : Model Z A) (σ : Strategy Z A) (x : Z) : Prop :=
  ∀ c, Reach (runEdge M σ) (start x) c →
    c.2 ∈ M.safe ∧ ∃ a, σ c = some a ∧ a ∈ M.run c.2

/-- One observable policy input. In ending mode it retains the command epoch's
configuration as well as the entire subsequent state/action history. -/
inductive PolicyInput (Z : Type u) (A : Type v)
  | running (current : Config Z A)
  | ending (atCommand : Config Z A) (current : Config Z A)

abbrev Policy (Z : Type u) (A : Type v) := PolicyInput Z A → Option A

def before (P : Policy Z A) : Strategy Z A := fun c => P (.running c)
def after (P : Policy Z A) (anchor : Config Z A) : Strategy Z A :=
  fun c => P (.ending anchor c)

/-- Any command epoch may switch the same policy to a surely terminating ending.
No assumption of memorylessness is imposed on the supplied policy. -/
structure SwitchingGuarantee (M : Model Z A) (P : Policy Z A) (x : Z) : Prop where
  run_total : RunningGuarantee M (before P) x
  end_on_command : ∀ c, Reach (runEdge M (before P)) (start x) c →
    EndingGuarantee M (after P c) c.2

noncomputable section

/-- The rank-decreasing strategy ignores history, but its specification quantifies
all histories and every successor of the selected action. -/
def rankedStrategy [Fintype Z] (M : Model Z A) : Strategy Z A :=
  fun c => endingAction M c.2

theorem ranked_edge [Fintype Z] (M : Model Z A) {c d : Config Z A}
    (hc : c.2 ∈ endingRegion M) (he : endEdge M (rankedStrategy M) c d) :
    d.2 ∈ endingRegion M ∧ endRank M d.2 < endRank M c.2 := by
  obtain ⟨hg, a, hσ, _, _, hp⟩ := he
  obtain ⟨b, hb, _, hdesc⟩ := endingAction_spec M hc hg
  have hab : a = b := Option.some.inj (hσ.symm.trans hb)
  subst b
  exact hdesc d.2 hp

theorem ranked_reachable [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ endingRegion M) {c : Config Z A}
    (hr : Reach (endEdge M (rankedStrategy M)) (start x) c) :
    c.2 ∈ endingRegion M := by
  induction hr with
  | refl => exact hx
  | tail _ he ih => exact (ranked_edge M ih he).1

/-- Every finite execution prefix consumes at least one unit of first-entry rank
per transition. This is a universal path theorem, not bounded enumeration. -/
theorem ending_rank_budget [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ endingRegion M) (p : ℕ → Config Z A) (h0 : p 0 = start x)
    (n : ℕ) (hp : ∀ k, k < n → endEdge M (rankedStrategy M) (p k) (p (k + 1))) :
    (p n).2 ∈ endingRegion M ∧ n + endRank M (p n).2 ≤ endRank M x := by
  induction n with
  | zero => simpa [h0, start] using hx
  | succ n ih =>
    have old := ih (fun k hk => hp k (by omega))
    have step := ranked_edge M old.1 (hp n (by omega))
    exact ⟨step.1, by omega⟩

/-- If a legal prefix reaches the full first-entry budget, its last state is a goal.
Earlier arrivals end the prefix semantics already. -/
theorem ending_rank_arrival [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ endingRegion M) (p : ℕ → Config Z A) (h0 : p 0 = start x)
    (hp : ∀ k, k < endRank M x → endEdge M (rankedStrategy M) (p k) (p (k + 1))) :
    (p (endRank M x)).2 ∈ M.goal := by
  have h := ending_rank_budget M hx p h0 (endRank M x) hp
  apply (endRank_zero_iff M h.1).mp
  omega

theorem ranked_guarantee [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ endingRegion M) : EndingGuarantee M (rankedStrategy M) x := by
  refine ⟨?_, ?_⟩
  · intro c hr
    have hc := ranked_reachable M hx hr
    refine ⟨endingRegion_safe M hc, ?_⟩
    intro hg
    obtain ⟨a, hσ, ha, _⟩ := endingAction_spec M hc hg
    exact ⟨a, hσ, ha⟩
  · intro p h0 hp
    have h := ending_rank_budget M hx p h0 (endRank M x + 1) (fun k _ => hp k)
    omega

/-- Safety and legality plus nonempty enabled successors rule out a fake ending
obtained simply by deadlocking before the goal. -/
theorem ending_prefix_extends (M : Model Z A) {σ : Strategy Z A} {x : Z}
    (h : EndingGuarantee M σ x) {c : Config Z A}
    (hr : Reach (endEdge M σ) (start x) c) (hg : c.2 ∉ M.goal) :
    ∃ d, endEdge M σ c d := by
  obtain ⟨a, hσ, ha⟩ := (h.total c hr).2 hg
  obtain ⟨y, hy⟩ := M.post_nonempty c.2 a (Or.inr ha)
  exact ⟨((c.2, a) :: c.1, y), hg, a, hσ, ha, rfl, hy⟩

/-- Necessity for arbitrary history-dependent policies: outside the attractor an
adversary constructs an infinite legal non-ending play, unless safety or legality
has already failed. The action is chosen before this adversarial response. -/
theorem guarantee_mem_ending [Fintype Z] (M : Model Z A) {σ : Strategy Z A} {x : Z}
    (h : EndingGuarantee M σ x) : x ∈ endingRegion M := by
  classical
  by_contra hx
  let Bad := {c : Config Z A // Reach (endEdge M σ) (start x) c ∧ c.2 ∉ endingRegion M}
  let initial : Bad := ⟨start x, Reach.refl, hx⟩
  have extend : ∀ b : Bad, ∃ d : Bad, endEdge M σ b.val d.val := by
    intro b
    have ht := h.total b.val b.property.1
    have hg : b.val.2 ∉ M.goal := fun hg => b.property.2 (goal_subset_region M hg)
    obtain ⟨a, hσ, ha⟩ := ht.2 hg
    obtain ⟨y, hy, hn⟩ := outside_successor M ht.1 b.property.2 ha
    let c : Config Z A := ((b.val.2, a) :: b.val.1, y)
    have he : endEdge M σ b.val c := ⟨hg, a, hσ, ha, rfl, hy⟩
    exact ⟨⟨c, Reach.tail b.property.1 he, hn⟩, he⟩
  let step : Bad → Bad := fun b => Classical.choose (extend b)
  let path : ℕ → Bad := fun n => Nat.rec initial (fun _ b => step b) n
  apply h.noInfinite (fun n => (path n).val) rfl
  intro n
  exact Classical.choose_spec (extend (path n))

theorem ending_region_iff [Fintype Z] (M : Model Z A) (x : Z) :
    x ∈ endingRegion M ↔ ∃ σ : Strategy Z A, EndingGuarantee M σ x :=
  ⟨fun hx => ⟨rankedStrategy M, ranked_guarantee M hx⟩,
   fun ⟨_, h⟩ => guarantee_mem_ending M h⟩

/-- A canonical positional policy. One observed command bit changes the branch. -/
def canonicalPolicy [Fintype Z] (M : Model Z A) : Policy Z A
  | .running c => runningAction M c.2
  | .ending _ c => endingAction M c.2

theorem canonical_run_edge [Fintype Z] (M : Model Z A) {c d : Config Z A}
    (hc : c.2 ∈ runningRegion M) (he : runEdge M (before (canonicalPolicy M)) c d) :
    d.2 ∈ runningRegion M := by
  obtain ⟨a, hσ, _, _, hp⟩ := he
  obtain ⟨b, hb, _, hpost⟩ := runningAction_spec M hc
  have hab : a = b := Option.some.inj (hσ.symm.trans hb)
  subst b
  exact hpost hp

theorem canonical_run_reachable [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ runningRegion M) {c : Config Z A}
    (hr : Reach (runEdge M (before (canonicalPolicy M))) (start x) c) :
    c.2 ∈ runningRegion M := by
  induction hr with
  | refl => exact hx
  | tail _ he ih => exact canonical_run_edge M ih he

theorem canonical_guarantee [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ runningRegion M) : SwitchingGuarantee M (canonicalPolicy M) x := by
  refine ⟨?_, ?_⟩
  · intro c hr
    have hc := canonical_run_reachable M hx hr
    obtain ⟨a, hσ, ha, _⟩ := runningAction_spec M hc
    exact ⟨runningRegion_safe M hc, a, hσ, ha⟩
  · intro c hr
    exact ranked_guarantee M (runningRegion_subset_ending M (canonical_run_reachable M hx hr))

/-- The no-command condition admits actual infinite execution; it is not a
universal assertion about an empty set of legal streams. -/
theorem running_has_infinite_path (M : Model Z A) {σ : Strategy Z A} {x : Z}
    (h : RunningGuarantee M σ x) :
    ∃ p : ℕ → Config Z A, p 0 = start x ∧
      (∀ n, runEdge M σ (p n) (p (n + 1))) ∧ (∀ n, (p n).2 ∈ M.safe) := by
  classical
  let Live := {c : Config Z A // Reach (runEdge M σ) (start x) c}
  let initial : Live := ⟨start x, Reach.refl⟩
  have extend : ∀ b : Live, ∃ d : Live, runEdge M σ b.val d.val := by
    intro b
    obtain ⟨a, hσ, ha⟩ := (h b.val b.property).2
    obtain ⟨y, hy⟩ := M.post_nonempty b.val.2 a (Or.inl ha)
    let c : Config Z A := ((b.val.2, a) :: b.val.1, y)
    have he : runEdge M σ b.val c := ⟨a, hσ, ha, rfl, hy⟩
    exact ⟨⟨c, Reach.tail b.property he⟩, he⟩
  let step : Live → Live := fun b => Classical.choose (extend b)
  let path : ℕ → Live := fun n => Nat.rec initial (fun _ b => step b) n
  refine ⟨fun n => (path n).val, rfl, ?_, ?_⟩
  · intro n
    exact Classical.choose_spec (extend (path n))
  · intro n
    exact (h (path n).val (path n).property).1

/-- Any history-dependent policy with the command guarantee starts in the
computed safe-running region. Past history and the stop epoch remain accessible. -/
theorem switching_mem_running [Fintype Z] (M : Model Z A) {P : Policy Z A} {x : Z}
    (h : SwitchingGuarantee M P x) : x ∈ runningRegion M := by
  let R : Z → Prop := fun y => ∃ c : Config Z A,
    Reach (runEdge M (before P)) (start x) c ∧ c.2 = y
  have hEnd : ∀ y, R y → y ∈ endingRegion M := by
    intro y hy
    obtain ⟨c, hc, rfl⟩ := hy
    exact guarantee_mem_ending M (h.end_on_command c hc)
  have hRun : ∀ y, R y → ∃ a ∈ M.run y, ∀ z ∈ M.post y a, R z := by
    intro y hy
    obtain ⟨c, hc, rfl⟩ := hy
    obtain ⟨a, hσ, ha⟩ := (h.run_total c hc).2
    refine ⟨a, ha, ?_⟩
    intro z hz
    let d : Config Z A := ((c.2, a) :: c.1, z)
    have he : runEdge M (before P) c d := ⟨a, hσ, ha, rfl, hz⟩
    exact ⟨d, Reach.tail hc he, rfl⟩
  exact running_maximal M R hEnd hRun x ⟨start x, Reach.refl, rfl⟩

/-- Source-facing Core 8.3 equivalence. No positional or bounded-time premise is
imposed on the policy in the necessary direction. The sufficient policy is
positional and has a separately proved first-entry-rank bound. -/
theorem safe_continuation_iff [Fintype Z] (M : Model Z A) (x : Z) :
    x ∈ runningRegion M ↔ ∃ P : Policy Z A, SwitchingGuarantee M P x :=
  ⟨fun hx => ⟨canonicalPolicy M, canonical_guarantee M hx⟩,
   fun ⟨_, h⟩ => switching_mem_running M h⟩

/-- The same constructed policy retains its exact ending budget at every command
configuration reachable before the command is received. -/
theorem command_rank_bound [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ runningRegion M) {anchor : Config Z A}
    (hr : Reach (runEdge M (before (canonicalPolicy M))) (start x) anchor)
    (p : ℕ → Config Z A) (h0 : p 0 = start anchor.2)
    (n : ℕ) (hp : ∀ k, k < n →
      endEdge M (after (canonicalPolicy M) anchor) (p k) (p (k + 1))) :
    (p n).2 ∈ endingRegion M ∧ n + endRank M (p n).2 ≤ endRank M anchor.2 :=
  ending_rank_budget M (runningRegion_subset_ending M (canonical_run_reachable M hx hr)) p h0 n hp


/-- The constructed command branch reaches the goal no later than its first-entry
rank, interpreted on legal nonterminal prefixes. -/
theorem command_rank_arrival [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ runningRegion M) {anchor : Config Z A}
    (hr : Reach (runEdge M (before (canonicalPolicy M))) (start x) anchor)
    (p : ℕ → Config Z A) (h0 : p 0 = start anchor.2)
    (hp : ∀ k, k < endRank M anchor.2 →
      endEdge M (after (canonicalPolicy M) anchor) (p k) (p (k + 1))) :
    (p (endRank M anchor.2)).2 ∈ M.goal :=
  ending_rank_arrival M (runningRegion_subset_ending M (canonical_run_reachable M hx hr)) p h0 hp

/-- The full manuscript endpoint states the equivalence and the existence of the
same policy's first-entry-rank guarantee in one declaration. -/
theorem source_core83 [Fintype Z] (M : Model Z A) (x : Z) :
    x ∈ runningRegion M ↔ ∃ P : Policy Z A,
      SwitchingGuarantee M P x ∧
      ∀ anchor, Reach (runEdge M (before P)) (start x) anchor →
        ∀ p : ℕ → Config Z A, p 0 = start anchor.2 →
          ∀ n, (∀ k, k < n → endEdge M (after P anchor) (p k) (p (k + 1))) →
            n + endRank M (p n).2 ≤ endRank M anchor.2 := by
  constructor
  · intro hx
    refine ⟨canonicalPolicy M, canonical_guarantee M hx, ?_⟩
    intro anchor hr p h0 n hp
    exact (command_rank_bound M hx hr p h0 n hp).2
  · rintro ⟨P, h, _⟩
    exact switching_mem_running M h

end
end Komorebi.MachineTheory.SafeEnding
