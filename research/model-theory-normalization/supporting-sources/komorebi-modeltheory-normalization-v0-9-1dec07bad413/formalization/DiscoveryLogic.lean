module
public import DiscoveryFinite
public import MatrixLogicalBridge

@[expose] public section
namespace Komorebi.Discovery
open scoped BigOperators
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

variable {R : Type} [CommRing R] {d k o : ℕ}

/-- The inherited recursive finite sum agrees with the actual module sum. -/
theorem discovery_fsum (n : ℕ) (f : Fin n → R) : fsum n f = ∑ i, f i := by
  induction n with
  | zero => simp [fsum]
  | succ n ih => rw [fsum,ih,Fin.sum_univ_succ]

/-- Right action on real observation rows, not an uninterpreted step oracle. -/
def rowRight (A : Mat R d d) : (Fin d → R) →ₗ[R] (Fin d → R) where
  toFun v := rm v A
  map_add' x y := by
    ext j
    simp [rm,discovery_fsum,add_mul,Finset.sum_add_distrib]
  map_smul' a x := by
    ext j
    simp [rm,discovery_fsum,Finset.mul_sum,mul_assoc]

def rowEvaluate (x : Fin d → R) : (Fin d → R) →ₗ[R] R where
  toFun v := dot v x
  map_add' v w := by
    simp [dot,discovery_fsum,add_mul,Finset.sum_add_distrib]
  map_smul' a v := by
    simp [dot,discovery_fsum,Finset.mul_sum,mul_assoc]

theorem testValue_behavior (A : Fin k → Mat R d d) (O : Mat R o d)
    (t : Test k o) (x : Fin d → R) :
    dot (testValue (fun a => rowRight (A a)) O t) x =
      behavior (linearSystem A O) x t.1 t.2 := by
  rcases t with ⟨w,j⟩
  induction w generalizing x with
  | nil => rw [testValue]; rfl
  | cons a w ih =>
    rw [testValue]
    change dot (rm (testValue (fun a => rowRight (A a)) O (w,j)) (A a)) x = _
    rw [dot_rm,ih]
    rfl

theorem spanning_tests_exact (A : Fin k → Mat R d d) (O : Mat R o d)
    (tests : List (Test k o))
    (hs : testSpan (fun a => rowRight (A a)) O tests =
      observableSpan (fun a => rowRight (A a)) O) (x y : Fin d → R) :
    CodeEqual (linearSystem A O) tests x y ↔ ObsEq (linearSystem A O) x y := by
  constructor
  · intro hc
    have hspan : testSpan (fun a => rowRight (A a)) O tests ≤
        LinearMap.ker (rowEvaluate x - rowEvaluate y) := by
      apply Submodule.span_le.mpr
      rintro _ ⟨t,ht,rfl⟩
      rw [SetLike.mem_coe,LinearMap.mem_ker]
      change dot (testValue (fun a => rowRight (A a)) O t) x -
        dot (testValue (fun a => rowRight (A a)) O t) y = 0
      rw [testValue_behavior,testValue_behavior,hc t ht,sub_self]
    intro w j
    have hm : testValue (fun a => rowRight (A a)) O (w,j) ∈
        testSpan (fun a => rowRight (A a)) O tests := by
      rw [hs]
      exact Submodule.subset_span ⟨(w,j),rfl⟩
    have he := hspan hm
    rw [LinearMap.mem_ker] at he
    change dot (testValue (fun a => rowRight (A a)) O (w,j)) x -
      dot (testValue (fun a => rowRight (A a)) O (w,j)) y = 0 at he
    rw [testValue_behavior,testValue_behavior] at he
    exact sub_eq_zero.mp he
  · intro he t _; exact he t.1 t.2

theorem discoveredCodeCertificate (A : Fin k → Mat R d d) (O : Mat R o d)
    (oracle : SpanOracle (fun a => rowRight (A a)) O)
    (B : ℕ) (tests : List (Test k o))
    (hr : discover (fun a => rowRight (A a)) O oracle B = some tests) :
    FiniteCodeCertificate (linearSystem A O) tests := by
  have he := spanning_tests_exact A O tests
    (worklist_exact (fun a => rowRight (A a)) O oracle _ tests hr)
  exact {
    outputs := fun x y hc j => (he x y).mp hc [] j
    steps := fun x y hc a => (he _ _).mpr (obsEq_step _ ((he x y).mp hc) a)
  }

theorem discoveredFormula_exact (A : Fin k → Mat R d d) (O : Mat R o d)
    (oracle : SpanOracle (fun a => rowRight (A a)) O)
    (B : ℕ) (tests : List (Test k o))
    (hr : discover (fun a => rowRight (A a)) O oracle B = some tests)
    (e : Fin 2 → TaggedCarrier (Fin d → R) R) :
    taggedRealize (linearSystem A O) (guardedCodeFormula tests) e ↔
      e ∈ taggedBehaviorSet (linearSystem A O) :=
  guardedCodeFormula_semantics _ tests (discoveredCodeCertificate A O oracle B tests hr) e

theorem discovered_behavior_definable (A : Fin k → Mat R d d) (O : Mat R o d)
    (oracle : SpanOracle (fun a => rowRight (A a)) O)
    (B : ℕ) (tests : List (Test k o))
    (hr : discover (fun a => rowRight (A a)) O oracle B = some tests) :
    letI := taggedStructure (linearSystem A O)
    (∅ : Set (TaggedCarrier (Fin d → R) R)).Definable
      (observationLanguage (Fin k) (Fin o) R) (taggedBehaviorSet (linearSystem A O)) :=
  standard_behavior_definable _ tests (discoveredCodeCertificate A O oracle B tests hr)

/-- Entire discovery-to-definition theorem. No completed matrix certificate or
pre-supplied all-word equivalence is assumed. -/
theorem prime_discovery_defines_behavior (p r d : ℕ) (hp : Nat.Prime p)
    [NeZero (p^r)] (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    ∃ tests, finitePrimeDiscover p r d (fun a => rowRight (A a)) O = some tests ∧
      tests.length ≤ r*d ∧ (∀ t ∈ tests, t.1.length < r*d) ∧
      FiniteCodeCertificate (linearSystem A O) tests ∧
      (guardedCodeFormula (V := ZMod (p^r)) tests).IsQF ∧
      (∀ e : Fin 2 → TaggedCarrier (Fin d → ZMod (p^r)) (ZMod (p^r)),
        taggedRealize (linearSystem A O) (guardedCodeFormula tests) e ↔
          e ∈ taggedBehaviorSet (linearSystem A O)) := by
  obtain ⟨tests,hr,_,hlen,hh⟩ := finitePrimeDiscover_total_correct p r d hp
    (fun a => rowRight (A a)) O
  refine ⟨tests,hr,hlen,hh,?_,guardedCodeFormula_isQF tests,?_⟩
  · exact discoveredCodeCertificate A O (enumerationOracle _ O) (r*d) tests hr
  · exact discoveredFormula_exact A O (enumerationOracle _ O) (r*d) tests hr

end Komorebi.Discovery
