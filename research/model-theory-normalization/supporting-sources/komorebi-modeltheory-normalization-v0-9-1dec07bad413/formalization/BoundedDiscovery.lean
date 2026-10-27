module
public import EchelonTemporaryBounds
public import NormalizedDiscovery

@[expose] public section
namespace Komorebi.Discovery.BoundedBackend
open Komorebi.Echelon Komorebi.Echelon.Cost
open Komorebi.Discovery.EchelonBackend Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard

variable {d k o : Nat}

/-- The same FIFO policy, with the bounded-coefficient Euclidean update. -/
def boundedRun (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) :
    Nat → Basis d → List (Test k o) → List (Test k o) → Option (Basis d × List (Test k o))
  | 0, _, _, _ => none
  | _+1, B, ts, [] => some (B,ts)
  | fuel+1, B, ts, t::pending =>
    let v := lift m (testValue A O t)
    if (coordinates B v).isSome then
      boundedRun m A O fuel B ts pending
    else
      boundedRun m A O fuel (boundedNormalizedInsert B v) (ts++[t]) (pending++children t)

/-- The complete cache and test list coincide at every fuel budget. -/
theorem boundedRun_eq (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (fuel : Nat)
    (B : Basis d) (ts pending : List (Test k o)) :
    boundedRun m A O fuel B ts pending=normalizedRun m A O fuel B ts pending := by
  induction fuel generalizing B ts pending with
  | zero => rfl
  | succ fuel ih =>
    cases pending with
    | nil => rfl
    | cons t pending =>
      simp only [boundedRun,normalizedRun,boundedNormalizedInsert_eq]
      split
      · exact ih _ _ _
      · exact ih _ _ _

def boundedPrimeDiscover (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) : Option (List (Test k o)) :=
  (boundedRun (p^r) A O (o+k*(r*d)+1)
    (normalize (initial (p^r) d)) [] (roots k o)).map Prod.snd

theorem boundedPrimeDiscover_eq_normalized (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    boundedPrimeDiscover p r d A O=normalizedPrimeDiscover p r d A O := by
  simp only [boundedPrimeDiscover, normalizedPrimeDiscover, boundedRun_eq]

theorem boundedPrimeDiscover_eq_reference (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    boundedPrimeDiscover p r d A O=finitePrimeDiscover p r d A O := by
  rw [boundedPrimeDiscover_eq_normalized,normalizedPrimeDiscover_eq_reference]

theorem boundedPrimeDiscover_total_correct (p r d : Nat) (hp : p.Prime) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    ∃ tests, boundedPrimeDiscover p r d A O=some tests ∧
      testSpan A O tests=observableSpan A O ∧ tests.length≤r*d ∧
      (∀t∈tests,t.1.length<r*d) := by
  rw [boundedPrimeDiscover_eq_normalized]
  exact normalizedPrimeDiscover_total_correct p r d hp A O

theorem boundedPrimeDiscover_defines_behavior (p r d : Nat) (hp : p.Prime)
    [NeZero (p^r)] (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    ∃ tests, boundedPrimeDiscover p r d (fun a => rowRight (A a)) O=some tests ∧
      tests.length≤r*d ∧ (∀t∈tests,t.1.length<r*d) ∧
      FiniteCodeCertificate (linearSystem A O) tests ∧
      (guardedCodeFormula (V := ZMod (p^r)) tests).IsQF ∧
      (∀e : Fin 2 → TaggedCarrier (Fin d → ZMod (p^r)) (ZMod (p^r)),
        taggedRealize (linearSystem A O) (guardedCodeFormula tests) e ↔
          e ∈ taggedBehaviorSet (linearSystem A O)) := by
  rw [boundedPrimeDiscover_eq_normalized]
  exact normalizedPrimeDiscover_defines_behavior p r d hp A O

/-- Coefficient-arithmetic peak along the same branch decisions.
It does not model allocation, proof checking, or internals of machine arithmetic. -/
def runPeak (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) :
    Nat → Basis d → List (Test k o) → List (Test k o) → ℤ
  | 0, _, _, _ => 0
  | _+1, _, _, [] => 0
  | fuel+1, B, ts, t::pending =>
    let v := lift m (testValue A O t)
    max (residuePeak B v)
      (if (coordinates B v).isSome then runPeak m A O fuel B ts pending
       else max (updatePeak B v)
         (runPeak m A O fuel (boundedNormalizedInsert B v) (ts++[t]) (pending++children t)))

theorem lift_vectorPeak_le (m : Nat) [NeZero m] (v : Fin d → ZMod m) :
    vectorPeak (lift m v)≤(m:ℤ) := by
  apply vectorPeak_le _ _ (by positivity)
  intro j
  change |((v j).val:ℤ)|≤(m:ℤ)
  rw [abs_of_nonneg (by positivity)]
  exact_mod_cast (Nat.le_of_lt (ZMod.val_lt (v j)))

/-- All queue decisions have the same coefficient bound, independent of iteration count. -/
theorem runPeak_bound (m : Nat) [NeZero m]
    (A : Fin k → (Fin d → ZMod m) →ₗ[ZMod m] (Fin d → ZMod m))
    (O : Fin o → (Fin d → ZMod m)) (fuel : Nat)
    (B : Basis d) (ts pending : List (Test k o))
    (hB : StateCorrect m A O B ts) (hred : Reduced B) :
    runPeak m A O fuel B ts pending≤(m:ℤ)*(2*(m:ℤ)*(m+1))^d := by
  have hm : (1:ℤ)≤(m:ℤ) := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne m)
  have hcap : (0:ℤ)≤(m:ℤ)*(2*(m:ℤ)*(m+1))^d := by positivity
  induction fuel generalizing B ts pending with
  | zero => exact hcap
  | succ fuel ih =>
    cases pending with
    | nil => exact hcap
    | cons t pending =>
      let v := lift m (testValue A O t)
      have hmod := stateCorrect_containsModulus m A O B ts hB
      have hu := uniform_of_reduced (m:ℤ) (by omega) B hmod hred
      have hv := lift_vectorPeak_le m (testValue A O t)
      have hr := residuePeak_bound (m:ℤ) (m:ℤ) hm (le_refl _) B hu v hv
      have hs : ((m:ℤ)+1)^d*(m:ℤ)≤(m:ℤ)*(2*(m:ℤ)*(m+1))^d := by
        rw [mul_comm]
        gcongr
        nlinarith
      have hup := updatePeak_bound (m:ℤ) hm B hmod hred v hv
      simp only [runPeak]
      apply max_le (le_trans hr hs)
      split
      · exact ih B ts pending hB hred
      · apply max_le hup
        apply ih
        · rw [boundedNormalizedInsert_eq]
          exact stateCorrect_normalizedInsert m A O B ts hB t
        · rw [boundedNormalizedInsert_eq]
          exact normalize_reduced _

/-- A power-of-two bound makes the linear dependence of bit length explicit. -/
theorem coefficient_cap_power_two (m : ℤ) (hm : 1≤m) (bits dim : Nat)
    (hbits : m≤(2:ℤ)^bits) :
    m*(2*m*(m+1))^dim≤(2:ℤ)^(bits+(2*bits+2)*dim) := by
  have hs : 2*m*(m+1)≤(2:ℤ)^(2*bits+2) := by
    have hp : (0:ℤ)≤(2:ℤ)^bits := by positivity
    have hsq : m*m≤(2:ℤ)^bits*(2:ℤ)^bits := by nlinarith
    rw [show 2*bits+2=bits+bits+2 by omega,pow_add,pow_add]
    norm_num
    nlinarith
  calc m*(2*m*(m+1))^dim≤(2:ℤ)^bits*((2:ℤ)^(2*bits+2))^dim := by gcongr
       _ = (2:ℤ)^(bits+(2*bits+2)*dim) := by rw [←pow_mul,←pow_add]

theorem boundedPrimeDiscover_code (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d)
    (result : List (Test k o))
    (h : boundedPrimeDiscover p r d (fun a => rowRight (A a)) O=some result) :
    FiniteCodeCertificate (linearSystem A O) result := by
  rw [boundedPrimeDiscover_eq_normalized] at h
  exact normalizedPrimeDiscover_code p r d A O result h

def discoveryPeak (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) : ℤ :=
  runPeak (p^r) A O (o+k*(r*d)+1)
    (normalize (initial (p^r) d)) [] (roots k o)

theorem discoveryPeak_bound (p r d : Nat) [NeZero (p^r)]
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    discoveryPeak p r d A O≤((p^r:Nat):ℤ)*(2*((p^r:Nat):ℤ)*(((p^r:Nat):ℤ)+1))^d := by
  apply runPeak_bound
  · exact stateCorrect_normalize (p^r) A O _ _ (stateCorrect_initial (p^r) A O)
  · exact normalize_reduced _

theorem discoveryPeak_bit_budget (p r d bits : Nat) [NeZero (p^r)]
    (hbits : p^r≤2^bits)
    (A : Fin k → (Fin d → ZMod (p^r)) →ₗ[ZMod (p^r)] (Fin d → ZMod (p^r)))
    (O : Fin o → (Fin d → ZMod (p^r))) :
    discoveryPeak p r d A O≤(2:ℤ)^(bits+(2*bits+2)*d) := by
  apply le_trans (discoveryPeak_bound p r d A O)
  apply coefficient_cap_power_two
  · exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne (p^r))
  · exact_mod_cast hbits

end Komorebi.Discovery.BoundedBackend
