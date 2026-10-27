import AVOC.AttemptAccounting
import Lean

namespace Komorebi.AVOC.Attempts
open Lean

def CheckSafe (lim : Limits) (l : Ledger) : Prop :=
  l.charged ≤ lim.credits ∧ l.reserved ≤ lim.attempts ∧
  l.confirmed + held l ≤ l.charged ∧
  (match l.current with | none => True | some t => t.generation < l.reserved) ∧
  (l.published = true → l.current.isSome = true)

instance (lim : Limits) (l : Ledger) : Decidable (CheckSafe lim l) := by
  unfold CheckSafe
  cases l.current <;> infer_instance

theorem checkSafe_iff (lim : Limits) (l : Ledger) : CheckSafe lim l ↔ Safe lim l := by
  cases hc : l.current <;> simp [CheckSafe,Safe,hc]

def checkedStep (lim : Limits) (l : Ledger) (e : Event) : Except String Ledger :=
  if CheckSafe lim l then step lim l e else .error "invalid attempt ledger"

theorem checkedStep_sound (lim : Limits) (l r : Ledger) (e : Event)
    (h : checkedStep lim l e = .ok r) : Safe lim r := by
  by_cases hs : CheckSafe lim l
  · exact step_safe lim l r e ((checkSafe_iff lim l).1 hs)
      (by simpa [checkedStep,hs] using h)
  · simp [checkedStep,hs] at h

def parseTicket (w : Json) : Except String Ticket := do
  match (← w.getArr?).toList with
  | [a,b,c] => return ⟨← a.getNat?,← b.getNat?,← c.getNat?⟩
  | _ => throw "invalid attempt ticket"

def parseLedger (w : Json) : Except String Ledger := do
  match (← w.getArr?).toList with
  | [c,f,n,t,.bool p,.bool h] =>
      let ticket ← match t with
        | .null => pure none
        | _ => some <$> parseTicket t
      return ⟨← c.getNat?,← f.getNat?,← n.getNat?,ticket,p,h⟩
  | _ => throw "invalid attempt ledger"

def parseEvent (w : Json) : Except String Event := do
  match (← w.getArr?).toList with
  | [.str "reserve",op,c] => return .reserve (← op.getNat?) (← c.getNat?)
  | [.str "renew",t] => return .renew (← parseTicket t)
  | [.str "publish",t] => return .publish (← parseTicket t)
  | [.str "settle",t] => return .settle (← parseTicket t)
  | [.str "abandon",t] => return .abandon (← parseTicket t)
  | _ => throw "invalid attempt event"

def ticketJson (t : Ticket) : Json := toJson [t.operation,t.generation,t.fee]

def ledgerJson (l : Ledger) : Json := .arr #[toJson l.charged,toJson l.confirmed,toJson l.reserved,
  (match l.current with | none => .null | some t => ticketJson t),.bool l.published,.bool l.terminal]

def execute (wire : Json) : Except String Json := do
  match (← wire.getArr?).toList with
  | [.str "avoc-attempt-v1",lims,book,ev] =>
      let lim ← match (← lims.getArr?).toList with
        | [c,n] => pure (⟨← c.getNat?,← n.getNat?⟩ : Limits)
        | _ => throw "invalid attempt limits"
      let l ← parseLedger book
      let e ← parseEvent ev
      let r ← checkedStep lim l e
      return Json.mkObj [("status",.str "ok"),("backend",.str "AVOC-v0.21-attempt-gate"),
        ("ledger",ledgerJson r)]
  | _ => throw "invalid attempt-gate request"

end Komorebi.AVOC.Attempts
