import AVOC.CertificateLogic
import Lean.Data.Json.Parser

namespace Komorebi.AVOC.Certificate
open Lean

/-- Bounded, data-only decoding. This parser is part of the implementation trust
boundary; infer_sound applies to its resulting syntax objects. -/
def parseFormula : Nat → Json → Except String Formula
  | 0, _ => .error "formula depth limit"
  | n + 1, .arr a => match a.toList with
      | [.str "atom", k] => return .atom (← k.getNat?)
      | [.str "true"] => return .truth
      | [.str "false"] => return .falsity
      | [.str "and", p, q] => return .conj (← parseFormula n p) (← parseFormula n q)
      | [.str "or", p, q] => return .disj (← parseFormula n p) (← parseFormula n q)
      | [.str "imp", p, q] => return .impl (← parseFormula n p) (← parseFormula n q)
      | _ => .error "invalid formula tag or arity"
  | _, _ => .error "formula must be an array"

def parseDerivation : Nat → Json → Except String Derivation
  | 0, _ => .error "proof depth limit"
  | n + 1, .arr a => match a.toList with
      | [.str "hyp", f] => return .use (← parseFormula 64 f)
      | [.str "true"] => return .truth
      | [.str "pair", p, q] => return .pair (← parseDerivation n p) (← parseDerivation n q)
      | [.str "fst", p] => return .first (← parseDerivation n p)
      | [.str "snd", p] => return .second (← parseDerivation n p)
      | [.str "intro", f, p] => return .abstract (← parseFormula 64 f) (← parseDerivation n p)
      | [.str "mp", p, q] => return .apply (← parseDerivation n p) (← parseDerivation n q)
      | [.str "left", f, p] => return .left (← parseFormula 64 f) (← parseDerivation n p)
      | [.str "right", f, p] => return .right (← parseFormula 64 f) (← parseDerivation n p)
      | [.str "cases", p, q, r] => return .cases (← parseDerivation n p) (← parseDerivation n q) (← parseDerivation n r)
      | [.str "absurd", f, p] => return .absurd (← parseFormula 64 f) (← parseDerivation n p)
      | _ => .error "invalid proof tag or arity"
  | _, _ => .error "proof must be an array"

def parseRequest (j : Json) : Except String (Formula × List Formula × Derivation) := do
  let a ← j.getArr?
  match a.toList with
  | [target, .arr ctx, proof] =>
      let t ← parseFormula 64 target
      let c ← ctx.toList.mapM (parseFormula 64)
      let p ← parseDerivation 128 proof
      return (t, c, p)
  | _ => .error "expected [target, context-array, proof]"

def checkJson (j : Json) : Except String Bool :=
  match parseRequest j with
  | .error e => .error e
  | .ok (t,c,p) => .ok (check c t p)

/-- The exact decoded sequent behind any accepted JSON request is sound. -/
theorem accepted_json_has_sound_sequent (j : Json) (h : checkJson j = .ok true) :
    ∃ t c p, parseRequest j = .ok (t,c,p) ∧
      ∀ v : Nat → Prop, Satisfies v c → Denote v t := by
  cases hp : parseRequest j with
  | error e => simp [checkJson, hp] at h
  | ok data =>
      rcases data with ⟨t,c,p⟩
      have hc : check c t p = true := by simpa [checkJson, hp] using h
      exact ⟨t,c,p,rfl,fun v hs => check_sound c t p hc v hs⟩

end Komorebi.AVOC.Certificate
