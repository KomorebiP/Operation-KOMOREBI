module
public import CostedDiscovery

@[expose] public section
namespace Komorebi.Costed
open Komorebi.Echelon Komorebi.Echelon.Cost
open Komorebi.Discovery Komorebi.Discovery.BoundedBackend
open Komorebi.Discovery.EchelonBackend Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation.Matrix

variable {d k o : Nat}

/-- Strict binary magnitude budget for every Euclidean insertion input. -/
def operandBits (bits dim : Nat) := bits+(2*bits+2)*dim+1

def updateUnitsBound (bits dim : Nat) :=
  3*dim*dim+8*dim+14*operandBits bits dim*dim+dim*dim*dim

def roundUnitsBound (bits dim horizon : Nat) :=
  2*dim*dim*horizon+(dim*dim+2*dim)+dim+1+updateUnitsBound bits dim

/-- Numeric coefficient bounds are connected to the costed insertion's real operands. -/
theorem updateEval_uniform_bound (m bits : Nat) [NeZero m] (hbits : m≤2^bits)
    (B : Basis d) (hmod : ContainsModulus (m:ℤ) B) (hred : Reduced B)
    (v : Fin d → ℤ) (hv : vectorPeak v≤(m:ℤ)) :
    (updateEval B v).2≤updateUnitsBound bits d := by
  have hm : (1:ℤ)≤(m:ℤ) := by exact_mod_cast Nat.pos_of_ne_zero (NeZero.ne m)
  have hi : insertionPeak B v≤(m:ℤ)*(2*(m:ℤ)*((m:ℤ)+1))^d :=
    le_trans (le_max_left _ _) (updatePeak_bound (m:ℤ) hm B hmod hred v hv)
  have hc := coefficient_cap_power_two (m:ℤ) hm bits d (by exact_mod_cast hbits)
  have hp : (0:ℤ)<(2:ℤ)^(bits+(2*bits+2)*d) := by positivity
  have hs : insertionPeak B v<(2:ℤ)^operandBits bits d := by
    dsimp [operandBits]
    rw [pow_succ]
    exact lt_of_le_of_lt (le_trans hi hc) (by linarith)
  exact updateEval_units_le B v (operandBits bits d) hs

theorem roundUnitsBound_mono (bits dim : Nat) {h h' : Nat} (hh : h≤h') :
    roundUnitsBound bits dim h≤roundUnitsBound bits dim h' := by
  dsimp [roundUnitsBound]
  gcongr

/-- A bound for every fuel budget, including interrupted (none) computations.
Each pending word can grow by at most one on an accepted transition. -/
theorem runEval_units_bound (m bits : Nat) [NeZero m] (hbits : m≤2^bits)
    (A : Fin k → Mat (ZMod m) d d) (O : Mat (ZMod m) o d)
    (fuel : Nat) (B : Basis d) (ts pending : List (Test k o)) (h : Nat)
    (hB : StateCorrect m (fun a => rowRight (A a)) O B ts) (hred : Reduced B)
    (hh : ∀t∈pending,t.1.length≤h) :
    (runEval m A O fuel B ts pending).2≤fuel*roundUnitsBound bits d (h+fuel) := by
  induction fuel generalizing B ts pending h with
  | zero => simp [runEval]
  | succ fuel ih =>
    cases pending with
    | nil => simp [runEval]
    | cons t pending =>
      let v := lift m (testValue (fun a => rowRight (A a)) O t)
      have ht : t.1.length≤h := hh t (by simp)
      have htail : ∀u∈pending,u.1.length≤h+1 := by
        intro u hu
        exact le_trans (hh u (List.mem_cons_of_mem t hu)) (Nat.le_succ h)
      have hnext : ∀u∈pending++children t,u.1.length≤h+1 := by
        intro u hu
        rcases List.mem_append.mp hu with hu | hu
        · exact htail u hu
        · obtain ⟨a,rfl⟩ := List.mem_ofFn.mp hu
          simpa only [List.length_cons] using Nat.succ_le_succ ht
      have hsource : (testEval A O t).2≤2*d*d*(h+(fuel+1)) := by
        rw [testEval_units]
        gcongr
        omega
      have hmem := coordinatesEval_units_le B v
      have hup := updateEval_uniform_bound m bits hbits B
        (stateCorrect_containsModulus m (fun a => rowRight (A a)) O B ts hB)
        hred v (lift_vectorPeak_le m (testValue (fun a => rowRight (A a)) O t))
      have hnB : StateCorrect m (fun a => rowRight (A a)) O
          (boundedNormalizedInsert B v) (ts++[t]) := by
        rw [boundedNormalizedInsert_eq]
        exact stateCorrect_normalizedInsert m (fun a => rowRight (A a)) O B ts hB t
      have hnred : Reduced (boundedNormalizedInsert B v) := normalize_reduced _
      have hskip := ih B ts pending (h+1) hB hred htail
      have haccept := ih (boundedNormalizedInsert B v) (ts++[t]) (pending++children t)
        (h+1) hnB hnred hnext
      have heq : h+1+fuel=h+(fuel+1) := by omega
      rw [heq] at hskip haccept
      simp only [runEval,testEval_value,coordinatesEval_value,updateEval_value]
      split
      · change (testEval A O t).2+(coordinatesEval B v).2+d+1+
            (runEval m A O fuel B ts pending).2≤_
        dsimp [roundUnitsBound] at hskip ⊢
        nlinarith
      · change (testEval A O t).2+(coordinatesEval B v).2+d+1+(updateEval B v).2+
            (runEval m A O fuel (boundedNormalizedInsert B v) (ts++[t]) (pending++children t)).2≤_
        dsimp [roundUnitsBound] at haccept ⊢
        nlinarith

/-- A polynomial in the fuel, dimension and input modulus-bit budget.
This counts the declared high-level arithmetic units, not CPU time or allocations. -/
def discoveryUnitsBound (bits dim fuel : Nat) :=
  dim*dim*dim+fuel*roundUnitsBound bits dim fuel

theorem discoverEval_units_bound (p r d bits : Nat) [NeZero (p^r)]
    (hbits : p^r≤2^bits)
    (A : Fin k → Mat (ZMod (p^r)) d d) (O : Mat (ZMod (p^r)) o d) :
    (discoverEval p r d A O).2≤discoveryUnitsBound bits d (o+k*(r*d)+1) := by
  have hh : ∀t∈roots k o,t.1.length≤0 := by
    intro t ht
    obtain ⟨j,rfl⟩ := List.mem_ofFn.mp ht
    simp
  have hr := runEval_units_bound (p^r) bits hbits A O (o+k*(r*d)+1)
    (normalize (initial (p^r) d)) [] (roots k o) 0
    (stateCorrect_normalize (p^r) (fun a => rowRight (A a)) O _ _
      (stateCorrect_initial (p^r) (fun a => rowRight (A a)) O))
    (normalize_reduced _) hh
  have hn := normalizationUnits_le d
  simp only [discoverEval,normalizeEval_units,normalizeEval_value]
  dsimp [discoveryUnitsBound]
  simpa only [Nat.zero_add] using Nat.add_le_add hn hr

/-- Explicit expansion makes the chosen (coarse) polynomial transparent. -/
theorem discoveryUnitsBound_expansion (b d f : Nat) :
    discoveryUnitsBound b d f=
      d*d*d+f*(2*d*d*f+d*d*d+4*d*d+11*d+14*operandBits b d*d+1) := by
  simp only [discoveryUnitsBound,roundUnitsBound,updateUnitsBound]
  ring

end Komorebi.Costed
