module
public import DiscoveryRank

@[expose] public section
namespace Komorebi.Discovery

universe u v
variable {R : Type u} {M : Type v} [Semiring R] [AddCommMonoid M] [Module R M]
variable {k o : ℕ}

abbrev Test (k o : ℕ) := List (Fin k) × Fin o

/-- Prepending a input digit is right multiplication of the observation row. -/
def testValue (A : Fin k → M →ₗ[R] M) (O : Fin o → M) : Test k o → M
  | ([], j) => O j
  | (a :: w, j) => A a (testValue A O (w,j))

def children (t : Test k o) : List (Test k o) :=
  List.ofFn (fun a : Fin k => (a :: t.1, t.2))

def roots (k o : ℕ) : List (Test k o) :=
  List.ofFn (fun j : Fin o => ([], j))

def testSpan (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) : Submodule R M :=
  Submodule.span R (testValue A O '' {t | t ∈ ts})

def observableSpan (A : Fin k → M →ₗ[R] M) (O : Fin o → M) : Submodule R M :=
  Submodule.span R (Set.range (testValue A O))

theorem test_mem_span (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    {ts : List (Test k o)} {t : Test k o} (ht : t ∈ ts) :
    testValue A O t ∈ testSpan A O ts :=
  Submodule.subset_span ⟨t,ht,rfl⟩

theorem testSpan_mono (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    {ts us : List (Test k o)} (h : ts ⊆ us) : testSpan A O ts ≤ testSpan A O us := by
  apply Submodule.span_mono
  rintro _ ⟨t,ht,rfl⟩
  exact ⟨t,h ht,rfl⟩

theorem testSpan_append (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) (t : Test k o) :
    testSpan A O ts ≤ testSpan A O (ts ++ [t]) :=
  testSpan_mono A O (by intro x hx; exact List.mem_append_left _ hx)

theorem testSpan_strict (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) (t : Test k o)
    (h : testValue A O t ∉ testSpan A O ts) :
    testSpan A O ts < testSpan A O (ts ++ [t]) := by
  apply lt_of_le_of_ne (testSpan_append A O ts t)
  intro he
  apply h
  rw [he]
  exact test_mem_span A O (List.mem_append_right _ (by simp))

theorem testSpan_le_observable (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) : testSpan A O ts ≤ observableSpan A O := by
  apply Submodule.span_le.mpr
  rintro _ ⟨t,_,rfl⟩
  exact Submodule.subset_span ⟨t,rfl⟩

/-- Exact membership is a proof-bearing interface. It is instantiated by finite
coefficient enumeration in DiscoveryFinite; no abstract membership axiom is added. -/
structure SpanOracle (A : Fin k → M →ₗ[R] M) (O : Fin o → M) where
  contains : List (Test k o) → M → Bool
  correct : ∀ ts v, contains ts v = true ↔ v ∈ testSpan A O ts

/-- Fuel counts actual queue removals. Only newly independent tests spawn children. -/
def worklist (A : Fin k → M →ₗ[R] M) (O : Fin o → M) (oracle : SpanOracle A O) :
    ℕ → List (Test k o) → List (Test k o) → Option (List (Test k o))
  | 0, _, _ => none
  | n+1, ts, [] => some ts
  | n+1, ts, t::pending =>
    if oracle.contains ts (testValue A O t) then
      worklist A O oracle n ts pending
    else
      worklist A O oracle n (ts ++ [t]) (pending ++ children t)

/-- Every root and every successor of an accepted test is either already spanned
or still literally present in the pending worklist. -/
def Frontier (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts pending : List (Test k o)) : Prop :=
  (∀ j, testValue A O ([],j) ∈ testSpan A O ts ∨ ([],j) ∈ pending) ∧
  (∀ t ∈ ts, ∀ a, testValue A O (a::t.1,t.2) ∈ testSpan A O ts ∨
    (a::t.1,t.2) ∈ pending)

theorem frontier_initial (A : Fin k → M →ₗ[R] M) (O : Fin o → M) :
    Frontier A O [] (roots k o) := by
  constructor
  · intro j
    right
    exact List.mem_ofFn.mpr ⟨j,rfl⟩
  · simp

theorem frontier_skip (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    {ts pending : List (Test k o)} {t : Test k o}
    (hf : Frontier A O ts (t::pending))
    (ht : testValue A O t ∈ testSpan A O ts) : Frontier A O ts pending := by
  have move (v : Test k o) (h : testValue A O v ∈ testSpan A O ts ∨ v ∈ t::pending) :
      testValue A O v ∈ testSpan A O ts ∨ v ∈ pending := by
    rcases h with h | h
    · exact Or.inl h
    · rcases List.mem_cons.mp h with he | hp
      · exact Or.inl (he ▸ ht)
      · exact Or.inr hp
  exact ⟨fun j => move _ (hf.1 j), fun v hv a => move _ (hf.2 v hv a)⟩

theorem frontier_accept (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    {ts pending : List (Test k o)} {t : Test k o}
    (hf : Frontier A O ts (t::pending)) :
    Frontier A O (ts++[t]) (pending++children t) := by
  have mono := testSpan_append A O ts t
  have newmem : testValue A O t ∈ testSpan A O (ts++[t]) :=
    test_mem_span A O (by simp)
  have move (v : Test k o) (h : testValue A O v ∈ testSpan A O ts ∨ v ∈ t::pending) :
      testValue A O v ∈ testSpan A O (ts++[t]) ∨ v ∈ pending++children t := by
    rcases h with h | h
    · exact Or.inl (mono h)
    · rcases List.mem_cons.mp h with he | hp
      · exact Or.inl (he ▸ newmem)
      · exact Or.inr (List.mem_append_left _ hp)
  constructor
  · intro j; exact move _ (hf.1 j)
  · intro v hv a
    rcases List.mem_append.mp hv with old | newh
    · exact move _ (hf.2 v old a)
    · have he : v=t := by simpa using newh
      subst v
      right
      apply List.mem_append_right
      exact List.mem_ofFn.mpr ⟨a,rfl⟩

theorem empty_frontier_closed (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) (hf : Frontier A O ts []) :
    (∀ j, O j ∈ testSpan A O ts) ∧
    (∀ a v, v ∈ testSpan A O ts → A a v ∈ testSpan A O ts) := by
  constructor
  · intro j; simpa [testValue] using hf.1 j
  · intro a v hv
    induction hv using Submodule.span_induction with
    | mem v hv =>
      obtain ⟨t,ht,rfl⟩ := hv
      simpa [testValue] using hf.2 t ht a
    | zero => simpa using (testSpan A O ts).zero_mem
    | add v w hv hw ihv ihw => simpa using (testSpan A O ts).add_mem ihv ihw
    | smul b v hv ih => simpa using (testSpan A O ts).smul_mem b ih

theorem empty_frontier_exact (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) (hf : Frontier A O ts []) :
    testSpan A O ts = observableSpan A O := by
  apply le_antisymm (testSpan_le_observable A O ts)
  apply Submodule.span_le.mpr
  rintro _ ⟨⟨w,j⟩,rfl⟩
  have hc := empty_frontier_closed A O ts hf
  induction w with
  | nil => exact hc.1 j
  | cons a w ih => exact hc.2 a _ ih

theorem worklist_frontier (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) (fuel : ℕ) (ts pending result : List (Test k o))
    (hf : Frontier A O ts pending)
    (hres : worklist A O oracle fuel ts pending = some result) :
    Frontier A O result [] := by
  induction fuel generalizing ts pending result with
  | zero => simp [worklist] at hres
  | succ n ih =>
    cases pending with
    | nil =>
      simp only [worklist, Option.some.injEq] at hres
      simpa [← hres] using hf
    | cons t pending =>
      simp only [worklist] at hres
      split at hres
      next h => exact ih _ _ _ (frontier_skip A O hf ((oracle.correct _ _).mp h)) hres
      next _ => exact ih _ _ _ (frontier_accept A O hf) hres

theorem worklist_exact (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) (fuel : ℕ) (result : List (Test k o))
    (hres : worklist A O oracle fuel [] (roots k o) = some result) :
    testSpan A O result = observableSpan A O :=
  empty_frontier_exact A O result
    (worklist_frontier A O oracle fuel [] (roots k o) result (frontier_initial A O) hres)

end Komorebi.Discovery
