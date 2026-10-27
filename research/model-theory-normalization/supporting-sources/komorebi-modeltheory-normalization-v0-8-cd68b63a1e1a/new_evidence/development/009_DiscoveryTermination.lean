module
public import DiscoveryWorklist

@[expose] public section
namespace Komorebi.Discovery

universe u v
variable {R : Type u} {M : Type v} [Semiring R] [AddCommMonoid M] [Module R M]
variable {k o : ℕ}

/-- Removing a candidate lowers this potential even when an accepted candidate
spawns k new candidates. The rank is a proof measure, not computed by the loop. -/
theorem queue_potential_decreases (k B s t q : ℕ) (hst : s < t) (ht : t ≤ B) :
    q+k+k*(B-t) < q+1+k*(B-s) := by
  have hd : B-t+1 ≤ B-s := by omega
  have hm := Nat.mul_le_mul_left k hd
  simp only [Nat.mul_add, Nat.mul_one] at hm
  omega

theorem worklist_terminates (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) (rank : Submodule R M → ℕ) (B : ℕ)
    (hstrict : StrictMono rank) (hbound : ∀ U, rank U ≤ B)
    (fuel : ℕ) (ts pending : List (Test k o))
    (hbudget : pending.length + k*(B-rank (testSpan A O ts)) < fuel) :
    ∃ result, worklist A O oracle fuel ts pending = some result := by
  induction fuel generalizing ts pending with
  | zero => omega
  | succ n ih =>
    cases pending with
    | nil => exact ⟨ts,rfl⟩
    | cons t pending =>
      by_cases hmem : oracle.contains ts (testValue A O t) = true
      · have hb : pending.length + k*(B-rank (testSpan A O ts)) < n := by
          simp only [List.length_cons] at hbudget
          omega
        obtain ⟨result,hr⟩ := ih ts pending hb
        exact ⟨result,by simpa only [worklist,hmem,ite_true] using hr⟩
      · have hnot : testValue A O t ∉ testSpan A O ts :=
          fun h => hmem ((oracle.correct _ _).mpr h)
        have hs := hstrict (testSpan_strict A O ts t hnot)
        have hd := queue_potential_decreases k B _ _ pending.length hs
          (hbound (testSpan A O (ts++[t])))
        have hb : (pending++children t).length + k*(B-rank (testSpan A O (ts++[t]))) < n := by
          simp only [List.length_cons] at hbudget
          simp only [List.length_append, children, List.length_ofFn]
          omega
        obtain ⟨result,hr⟩ := ih (ts++[t]) (pending++children t) hb
        exact ⟨result,by simpa only [worklist,hmem,ite_false] using hr⟩

/-- A generic resource contract: o roots, at most B acceptances, k children each. -/
def discover (A : Fin k → M →ₗ[R] M) (O : Fin o → M) (oracle : SpanOracle A O)
    (B : ℕ) : Option (List (Test k o)) :=
  worklist A O oracle (o+k*B+1) [] (roots k o)

theorem discover_total (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) (rank : Submodule R M → ℕ) (B : ℕ)
    (hstrict : StrictMono rank) (hbound : ∀ U, rank U ≤ B) :
    ∃ result, discover A O oracle B = some result := by
  apply worklist_terminates A O oracle rank B hstrict hbound
  simp only [roots,List.length_ofFn]
  have hh := Nat.mul_le_mul_left k (Nat.sub_le B (rank (testSpan A O [])))
  omega

theorem worklist_size (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) (rank : Submodule R M → ℕ) (hstrict : StrictMono rank)
    (fuel : ℕ) (ts pending result : List (Test k o))
    (hsize : ts.length ≤ rank (testSpan A O ts))
    (hres : worklist A O oracle fuel ts pending = some result) :
    result.length ≤ rank (testSpan A O result) := by
  induction fuel generalizing ts pending result with
  | zero => simp [worklist] at hres
  | succ n ih =>
    cases pending with
    | nil =>
      simp only [worklist, Option.some.injEq] at hres
      simpa [← hres] using hsize
    | cons t pending =>
      simp only [worklist] at hres
      split at hres
      next _ => exact ih _ _ _ hsize hres
      next hmem =>
        have hnot : testValue A O t ∉ testSpan A O ts :=
          fun h => hmem ((oracle.correct _ _).mpr h)
        have hs := hstrict (testSpan_strict A O ts t hnot)
        apply ih _ _ _ ?_ hres
        simp only [List.length_append, List.length_singleton]
        omega

/-- A nonempty returned test has fewer prefix operations than the total number
of accepted tests. This is not a claim of shortest test-list minimality. -/
theorem worklist_horizon (A : Fin k → M →ₗ[R] M) (O : Fin o → M)
    (oracle : SpanOracle A O) (fuel : ℕ) (ts pending result : List (Test k o))
    (ha : ∀ t ∈ ts, t.1.length < ts.length)
    (hq : ∀ t ∈ pending, t.1.length ≤ ts.length)
    (hres : worklist A O oracle fuel ts pending = some result) :
    ∀ t ∈ result, t.1.length < result.length := by
  induction fuel generalizing ts pending result with
  | zero => simp [worklist] at hres
  | succ n ih =>
    cases pending with
    | nil =>
      simp only [worklist, Option.some.injEq] at hres
      simpa [← hres] using ha
    | cons t pending =>
      simp only [worklist] at hres
      split at hres
      next _ =>
        exact ih _ _ _ ha (fun v hv => hq v (List.mem_cons_of_mem t hv)) hres
      next _ =>
        have ht := hq t (List.mem_cons_self)
        apply ih _ _ _ ?_ ?_ hres
        · intro v hv
          simp only [List.length_append,List.length_singleton]
          rcases List.mem_append.mp hv with hv | hv
          · exact Nat.lt_trans (ha v hv) (Nat.lt_succ_self _)
          · have he : v=t := by simpa using hv
            subst v
            omega
        · intro v hv
          simp only [List.length_append,List.length_singleton]
          rcases List.mem_append.mp hv with hv | hv
          · exact (hq v (List.mem_cons_of_mem t hv)).trans (Nat.le_succ _)
          · obtain ⟨a,rfl⟩ := List.mem_ofFn.mp hv
            simp only [List.length_cons]
            omega

theorem prime_discover_total_exact (p r d : ℕ) (hp : Nat.Prime p)
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) (oracle : SpanOracle A O) :
    ∃ result, discover A O oracle (r*d) = some result ∧
      testSpan A O result = observableSpan A O ∧
      result.length ≤ r*d ∧ (∀ t ∈ result, t.1.length < r*d) := by
  obtain ⟨result,hr⟩ := discover_total A O oracle (primeRank p r d) (r*d)
    (primeRank_strictMono p r d hp) (primeRank_bound p r d hp)
  have hsize := worklist_size A O oracle (primeRank p r d) (primeRank_strictMono p r d hp)
    (o+k*(r*d)+1) [] (roots k o) result (by simp) hr
  have hlen := hsize.trans (primeRank_bound p r d hp _)
  refine ⟨result,hr,worklist_exact A O oracle _ result hr,hlen,?_⟩
  have hh := worklist_horizon A O oracle (o+k*(r*d)+1) [] (roots k o) result
    (by simp) (by intro t ht; obtain ⟨j,rfl⟩ := List.mem_ofFn.mp ht; simp) hr
  intro t ht
  exact (hh t ht).trans_le hlen

end Komorebi.Discovery
