module
public import DiscoveryTermination

@[expose] public section
namespace Komorebi.Discovery
open scoped BigOperators
universe u v
variable {R : Type u} {M : Type v} [Semiring R] [AddCommMonoid M] [Module R M]
variable {k o : ℕ}

theorem testSpan_eq_fin_range (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (ts : List (Test k o)) :
    testSpan A O ts = Submodule.span R
      (Set.range (fun i : Fin ts.length => testValue A O ts[i])) := by
  unfold testSpan
  congr 1
  ext v
  constructor
  · rintro ⟨t,ht,rfl⟩
    obtain ⟨i,hi,he⟩ := List.mem_iff_getElem.mp ht
    exact ⟨⟨i,hi⟩,congrArg (testValue A O) he⟩
  · rintro ⟨i,rfl⟩
    exact ⟨ts[i],List.getElem_mem i.isLt,rfl⟩

/-- Deliberately simple executable reference membership procedure. It enumerates
scalar coefficient tuples, not the source states. Exponential cost is explicit. -/
def enumerationOracle [Fintype R] [DecidableEq M]
    (A : Fin k → M →ₗ[R] M) (O : Fin o → M) : SpanOracle A O where
  contains ts v := decide (∃ c : Fin ts.length → R,
    ∑ i, c i • testValue A O ts[i] = v)
  correct ts v := by
    rw [decide_eq_true_eq, testSpan_eq_fin_range]
    exact (Submodule.mem_span_range_iff_exists_fun R).symm

/-- The executable algorithm does not compute the proof rank or cardinality.
Its numerical fuel is o + k*r*d + 1. -/
def finitePrimeDiscover (p r d : ℕ) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) : Option (List (Test k o)) :=
  discover A O (enumerationOracle A O) (r*d)

theorem finitePrimeDiscover_total_correct (p r d : ℕ) (hp : Nat.Prime p)
    [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    ∃ tests, finitePrimeDiscover p r d A O = some tests ∧
      testSpan A O tests = observableSpan A O ∧
      tests.length ≤ r*d ∧ (∀ t ∈ tests, t.1.length < r*d) :=
  prime_discover_total_exact p r d hp A O (enumerationOracle A O)

end Komorebi.Discovery
