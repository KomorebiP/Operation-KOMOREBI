module
public import DiscoveryLogic

@[expose] public section
namespace Komorebi.Discovery
open scoped BigOperators
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

universe u v
variable {R : Type u} {M : Type v} [Semiring R] [AddCommMonoid M] [Module R M]
variable {k o : ℕ}

/-- A branch-by-branch certificate for a concrete completed queue run. This
interface needs exact membership facts only at states actually visited. -/
inductive QueueTrace (A : Fin k → M →ₗ[R] M) (O : Fin o → M) :
    List (Test k o) → List (Test k o) → List (Test k o) → Prop
  | done (ts) : QueueTrace A O ts [] ts
  | skip {ts t pending result} (h : testValue A O t ∈ testSpan A O ts)
      (rest : QueueTrace A O ts pending result) : QueueTrace A O ts (t::pending) result
  | accept {ts t pending result} (h : testValue A O t ∉ testSpan A O ts)
      (rest : QueueTrace A O (ts++[t]) (pending++children t) result) :
      QueueTrace A O ts (t::pending) result

theorem queueTrace_frontier (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    {ts pending result : List (Test k o)} (tr : QueueTrace A O ts pending result)
    (hf : Frontier A O ts pending) : Frontier A O result [] := by
  induction tr with
  | done => exact hf
  | skip h rest ih => exact ih (frontier_skip A O hf h)
  | accept h rest ih => exact ih (frontier_accept A O hf)

theorem queueTrace_exact (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    {result : List (Test k o)} (tr : QueueTrace A O [] (roots k o) result) :
    testSpan A O result = observableSpan A O :=
  empty_frontier_exact A O result (queueTrace_frontier A O tr (frontier_initial A O))

/-- Exact oracle substitution: any two correct membership backends make the
same decisions, not merely outputs with isomorphic spans. -/
theorem worklist_oracle_independent (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (s t : SpanOracle A O) (fuel : ℕ) (ts pending : List (Test k o)) :
    worklist A O s fuel ts pending = worklist A O t fuel ts pending := by
  induction fuel generalizing ts pending with
  | zero => rfl
  | succ n ih =>
    cases pending with
    | nil => rfl
    | cons v pending =>
      have he : s.contains ts (testValue A O v) = t.contains ts (testValue A O v) := by
        apply Bool.eq_iff_iff.mpr
        exact (s.correct _ _).trans (t.correct _ _).symm
      simp only [worklist,he]
      split <;> apply ih

/-- Scalar tuple witnesses establish true span membership, independently of
how a proposed coefficient tuple was found. -/
theorem span_member_from_coefficients (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) (v : M) (c : Fin ts.length → R)
    (h : ∑ i, c i • testValue A O ts[i] = v) : v ∈ testSpan A O ts := by
  rw [testSpan_eq_fin_range]
  exact (Submodule.mem_span_range_iff_exists_fun R).mpr ⟨c,h⟩

/-- One linear separating functional rules out every possible coefficient tuple. -/
theorem span_nonmember_from_functional (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) (v : M) (f : M →ₗ[R] R)
    (hzero : ∀ t ∈ ts, f (testValue A O t) = 0) (hne : f v ≠ 0) :
    v ∉ testSpan A O ts := by
  intro hv
  apply hne
  have hs : testSpan A O ts ≤ f.ker := by
    apply Submodule.span_le.mpr
    rintro _ ⟨t,ht,rfl⟩
    simpa only [SetLike.mem_coe,LinearMap.mem_ker] using hzero t ht
  exact hs hv

/-- Indexed finite form of the separating certificate, convenient for literal
kernel checks without quantifying over an infinite type of test words. -/
theorem span_nonmember_from_indexed_functional (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) (v : M) (f : M →ₗ[R] R)
    (hzero : ∀ i : Fin ts.length, f (testValue A O ts[i]) = 0) (hne : f v ≠ 0) :
    v ∉ testSpan A O ts := by
  apply span_nonmember_from_functional A O ts v f ?_ hne
  intro t ht
  obtain ⟨i,hi⟩ := List.mem_iff_get.mp ht
  exact hi ▸ hzero i

/-- Complete traces replay under every exact oracle. -/
theorem queueTrace_replay (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) {ts pending result : List (Test k o)}
    (tr : QueueTrace A O ts pending result) :
    ∃ fuel, worklist A O oracle fuel ts pending = some result := by
  induction tr with
  | done ts => exact ⟨1,rfl⟩
  | @skip ts t pending result h _ ih =>
    obtain ⟨fuel,hf⟩ := ih
    refine ⟨fuel+1,?_⟩
    have ht := (oracle.correct ts (testValue A O t)).mpr h
    simp only [worklist,ht,ite_true,hf]
  | @accept ts t pending result hn _ ih =>
    obtain ⟨fuel,hf⟩ := ih
    refine ⟨fuel+1,?_⟩
    have ht : oracle.contains ts (testValue A O t) ≠ true := by
      intro he
      exact hn ((oracle.correct _ _).mp he)
    simp only [worklist,ht,Bool.false_eq_true,ite_false,hf]

/-- Extra fuel cannot change a successfully returned list. -/
theorem worklist_success_unique (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) (f g : ℕ) (ts pending : List (Test k o))
    (s t : List (Test k o))
    (hs : worklist A O oracle f ts pending = some s)
    (ht : worklist A O oracle g ts pending = some t) : s=t := by
  induction f generalizing g ts pending with
  | zero => simp [worklist] at hs
  | succ f ih =>
    cases g with
    | zero => simp [worklist] at ht
    | succ g =>
      cases pending with
      | nil => simpa only [worklist,Option.some.injEq] using hs.symm.trans ht
      | cons v pending =>
        simp only [worklist] at hs ht
        split at hs <;> rename_i he
        · simp [he] at ht
          exact ih g ts pending hs ht
        · simp [he] at ht
          exact ih g (ts++[v]) (pending++children v) hs ht

/-- Branch certificates identify the result of the verified enumerative algorithm
without evaluating its costly oracle on that source. -/
theorem prime_trace_matches_reference (p r d : ℕ) (hp : p.Prime)
    [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r)))
    (result : List (Test k o)) (tr : QueueTrace A O [] (roots k o) result) :
    finitePrimeDiscover p r d A O = some result := by
  obtain ⟨fuel,hf⟩ := queueTrace_replay A O (enumerationOracle A O) tr
  obtain ⟨result',hr,_,_,_⟩ := finitePrimeDiscover_total_correct p r d hp A O
  have he := worklist_success_unique A O (enumerationOracle A O)
    (o+k*(r*d)+1) fuel [] (roots k o) result' result hr hf
  exact he ▸ hr

variable {S : Type} [CommRing S] {d : ℕ}

theorem queueTrace_code (A : Fin k → Mat S d d) (O : Mat S o d)
    (result : List (Test k o))
    (tr : QueueTrace (fun a => rowRight (A a)) O [] (roots k o) result) :
    FiniteCodeCertificate (linearSystem A O) result := by
  have he := spanning_tests_exact A O result (queueTrace_exact _ _ tr)
  exact {
    outputs := fun x y hc j => (he x y).mp hc [] j
    steps := fun x y hc a => (he _ _).mpr (obsEq_step _ ((he x y).mp hc) a)
  }

theorem queueTrace_standard_definition (A : Fin k → Mat S d d) (O : Mat S o d)
    (result : List (Test k o))
    (tr : QueueTrace (fun a => rowRight (A a)) O [] (roots k o) result)
    (e : Fin 2 → TaggedCarrier (Fin d → S) S) :
    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  guardedCodeFormula_semantics _ _ (queueTrace_code A O result tr) e

end Komorebi.Discovery
