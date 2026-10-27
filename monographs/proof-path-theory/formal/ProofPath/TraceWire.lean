import ProofPath.Trace
import Lean.Data.Json.Basic
import Mathlib.Data.List.Nodup

/-!
A strict, versioned JSON value codec. Positional arrays have exact lengths and
natural numbers use nonnegative, exponent-zero JSON number nodes. Round trips
are proved at the Json syntax-tree boundary, not assumed from sample tests.
The JSON text parser/printer and file I/O remain separately stated trust layers.
-/
namespace ProofPath.Trace.Wire
open Lean

-- Small structural decoders make the accepted syntax explicit.
def encodeNat (n : Nat) : Json := .num ⟨Int.ofNat n, 0⟩
def decodeNat : Json → Option Nat
  | .num ⟨Int.ofNat n, 0⟩ => some n
  | _ => none

def encodeBool (b : Bool) : Json := .bool b
def decodeBool : Json → Option Bool
  | .bool b => some b
  | _ => none

def decodeItems {α : Type*} (d : Json → Option α) : List Json → Option (List α)
  | [] => some []
  | j :: js => do
    let x ← d j
    let xs ← decodeItems d js
    pure (x :: xs)

def encodeArray {α : Type*} (e : α → Json) (xs : List α) : Json :=
  .arr ((xs.map e).toArray)

def decodeArray {α : Type*} (d : Json → Option α) : Json → Option (List α)
  | .arr a => decodeItems d a.toList
  | _ => none

@[simp] theorem nat_roundtrip (n : Nat) : decodeNat (encodeNat n) = some n := rfl
@[simp] theorem bool_roundtrip (b : Bool) : decodeBool (encodeBool b) = some b := rfl

theorem items_roundtrip {α : Type*} (e : α → Json) (d : Json → Option α)
    (hd : ∀ x, d (e x) = some x) (xs : List α) :
    decodeItems d (xs.map e) = some xs := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp [decodeItems, hd, ih]

theorem array_roundtrip {α : Type*} (e : α → Json) (d : Json → Option α)
    (hd : ∀ x, d (e x) = some x) (xs : List α) :
    decodeArray d (encodeArray e xs) = some xs := by
  simpa [decodeArray, encodeArray] using items_roundtrip e d hd xs

@[simp] theorem natArray_roundtrip (xs : List Nat) :
    decodeArray decodeNat (encodeArray encodeNat xs) = some xs :=
  array_roundtrip encodeNat decodeNat nat_roundtrip xs

def encodeRule (r : Rule) : Json :=
  .arr #[encodeArray encodeNat r.premises, encodeNat r.conclusion]

def decodeRule : Json → Option Rule
  | .arr a =>
    match a.toList with
    | [ps, co] => do
      let premises ← decodeArray decodeNat ps
      let conclusion ← decodeNat co
      pure ⟨premises, conclusion⟩
    | _ => none
  | _ => none

@[simp] theorem rule_roundtrip (r : Rule) : decodeRule (encodeRule r) = some r := by
  cases r
  simp [decodeRule, encodeRule]

@[simp] theorem ruleArray_roundtrip (xs : List Rule) :
    decodeArray decodeRule (encodeArray encodeRule xs) = some xs :=
  array_roundtrip encodeRule decodeRule rule_roundtrip xs

def encodeProblem (p : Problem) : Json :=
  .arr #[.str "proof-path/problem/1", encodeNat p.nodeCount,
    encodeArray encodeNat p.leaves, encodeArray encodeRule p.rules,
    encodeArray encodeNat p.positive, encodeArray encodeNat p.negative]

def decodeProblem : Json → Option Problem
  | .arr a =>
    match a.toList with
    | [.str "proof-path/problem/1", n, l, r, s, f] => do
      let nodeCount ← decodeNat n
      let leaves ← decodeArray decodeNat l
      let rules ← decodeArray decodeRule r
      let positive ← decodeArray decodeNat s
      let negative ← decodeArray decodeNat f
      pure ⟨nodeCount, leaves, rules, positive, negative⟩
    | _ => none
  | _ => none

@[simp] theorem problem_roundtrip (p : Problem) :
    decodeProblem (encodeProblem p) = some p := by
  cases p
  simp [decodeProblem, encodeProblem]

def encodeWitness (w : Witness) : Json :=
  .arr #[encodeNat w.target, encodeArray encodeNat w.trace]

def decodeWitness : Json → Option Witness
  | .arr a =>
    match a.toList with
    | [t, tr] => do
      let target ← decodeNat t
      let trace ← decodeArray decodeNat tr
      pure ⟨target, trace⟩
    | _ => none
  | _ => none

@[simp] theorem witness_roundtrip (w : Witness) :
    decodeWitness (encodeWitness w) = some w := by
  cases w
  simp [decodeWitness, encodeWitness]

def encodeObstruction : Option Witness → Json
  | none => .null
  | some w => encodeWitness w

def decodeObstruction : Json → Option (Option Witness)
  | .null => some none
  | j => (decodeWitness j).map some

@[simp] theorem obstruction_roundtrip (w : Option Witness) :
    decodeObstruction (encodeObstruction w) = some w := by
  cases w with
  | none => rfl
  | some w => simp [decodeObstruction, encodeObstruction, encodeWitness,
      decodeWitness]

def encodeCertificate (c : Certificate) : Json :=
  .arr #[.str "proof-path/certificate/1", encodeBool c.feasible,
    encodeArray encodeNat c.closure, encodeArray encodeNat c.trace,
    encodeObstruction c.obstruction]

def decodeCertificate : Json → Option Certificate
  | .arr a =>
    match a.toList with
    | [.str "proof-path/certificate/1", f, cl, tr, ob] => do
      let feasible ← decodeBool f
      let closure ← decodeArray decodeNat cl
      let trace ← decodeArray decodeNat tr
      let obstruction ← decodeObstruction ob
      pure ⟨feasible, closure, trace, obstruction⟩
    | _ => none
  | _ => none

@[simp] theorem certificate_roundtrip (c : Certificate) :
    decodeCertificate (encodeCertificate c) = some c := by
  cases c
  simp [decodeCertificate, encodeCertificate]

theorem encodeProblem_injective : Function.Injective encodeProblem := by
  intro a b h
  have he := congrArg decodeProblem h
  simpa using he

theorem encodeCertificate_injective : Function.Injective encodeCertificate := by
  intro a b h
  have he := congrArg decodeCertificate h
  simpa using he

def nodeListValid (n : Nat) (xs : List Nat) : Bool :=
  xs.all (fun v => decide (v < n)) && decide xs.Nodup

def problemValid (p : Problem) : Bool :=
  nodeListValid p.nodeCount p.leaves &&
  nodeListValid p.nodeCount p.positive &&
  nodeListValid p.nodeCount p.negative &&
  p.rules.all (fun r => nodeListValid p.nodeCount r.premises &&
    decide (r.conclusion < p.nodeCount))

def traceValid (p : Problem) (tr : List Nat) : Bool :=
  tr.all (fun j => decide (j < p.rules.length))

def certificateValid (p : Problem) (c : Certificate) : Bool :=
  nodeListValid p.nodeCount c.closure && traceValid p c.trace &&
  match c.obstruction with
  | none => true
  | some w => decide (w.target < p.nodeCount) && traceValid p w.trace

/-- The input problem is a separate argument; certificates cannot silently
replace it. Invalid data is rejected before mathematical replay. -/
def accept (p : Problem) (c : Certificate) : Bool :=
  problemValid p && certificateValid p c && checkCertificate p c

def acceptJson (problemJson certificateJson : Json) : Bool :=
  match decodeProblem problemJson, decodeCertificate certificateJson with
  | some p, some c => accept p c
  | _, _ => false

/-- The codec neither changes nor fabricates the executable verdict. -/
theorem encoded_acceptance (p : Problem) (c : Certificate) :
    acceptJson (encodeProblem p) (encodeCertificate c) = accept p c := by
  simp [acceptJson]

def CertifiedAnswer (p : Problem) (c : Certificate) : Prop :=
  (∀ v, v ∈ c.closure ↔ v ∈ p.exactClosure) ∧
  (c.feasible = true ↔ ∃ x, p.field.Extends p.seeds p.forbidden x)

theorem acceptance_sound (p : Problem) (c : Certificate)
    (h : accept p c = true) : CertifiedAnswer p c := by
  have hc : checkCertificate p c = true := (Bool.and_eq_true_iff.mp h).2
  exact ⟨certificate_closure p c hc, certificate_decides_feasibility p c hc⟩

/-- Soundness is about the actual decoded records, not a claimed external identity. -/
theorem json_acceptance_sound (jp jc : Json) (h : acceptJson jp jc = true) :
    ∃ p c, decodeProblem jp = some p ∧ decodeCertificate jc = some c ∧
      CertifiedAnswer p c := by
  cases hp : decodeProblem jp with
  | none => simp [acceptJson, hp] at h
  | some p =>
    cases hc : decodeCertificate jc with
    | none => simp [acceptJson, hp, hc] at h
    | some c =>
      exact ⟨p, c, rfl, rfl, acceptance_sound p c (by simpa [acceptJson, hp, hc] using h)⟩

/-- A valid finite address table cannot derive an unnamed node slot. -/
theorem valid_closure_bounded (p : Problem) (h : problemValid p = true) :
    ∀ v, v ∈ p.exactClosure → v < p.nodeCount := by
  have hall := Bool.and_eq_true_iff.mp h
  have hleft := Bool.and_eq_true_iff.mp hall.1
  have hfirst := Bool.and_eq_true_iff.mp hleft.1
  have hl := (Bool.and_eq_true_iff.mp hfirst.1).1
  have hs := (Bool.and_eq_true_iff.mp hfirst.2).1
  have hm : p.field.Model (fun v => v < p.nodeCount) := by
    constructor
    · intro v hv
      have hh := List.all_eq_true.mp hl v hv
      simpa using hh
    · intro j hj _
      cases he : lookup p.rules j with
      | none => simp [Problem.field, he] at hj
      | some r =>
        have hh := List.all_eq_true.mp hall.2 r (lookup_mem he)
        have hc := (Bool.and_eq_true_iff.mp hh).2
        simpa [Problem.field, he] using hc
  apply p.field.closure_le_model p.seeds hm
  intro v hv
  have hh := List.all_eq_true.mp hs v hv
  simpa using hh

end ProofPath.Trace.Wire
