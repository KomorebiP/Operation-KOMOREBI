import Std

namespace Komorebi.AVOC.Certificate

/-- A deliberately small, data-only intuitionistic propositional language. -/
inductive Formula where
  | atom : Nat → Formula
  | truth : Formula
  | falsity : Formula
  | conj : Formula → Formula → Formula
  | disj : Formula → Formula → Formula
  | impl : Formula → Formula → Formula
  deriving DecidableEq, Repr

/-- Atoms can denote arbitrary Lean propositions, not merely Boolean constants. -/
def Denote (v : Nat → Prop) : Formula → Prop
  | .atom n => v n
  | .truth => True
  | .falsity => False
  | .conj p q => Denote v p ∧ Denote v q
  | .disj p q => Denote v p ∨ Denote v q
  | .impl p q => Denote v p → Denote v q

def Satisfies (v : Nat → Prop) (ctx : List Formula) : Prop :=
  ∀ f ∈ ctx, Denote v f

/-- Proof syntax is data. No tactics, imports, macros, IO, or external code occur. -/
inductive Derivation where
  | use : Formula → Derivation
  | truth : Derivation
  | pair : Derivation → Derivation → Derivation
  | first : Derivation → Derivation
  | second : Derivation → Derivation
  | abstract : Formula → Derivation → Derivation
  | apply : Derivation → Derivation → Derivation
  | left : Formula → Derivation → Derivation
  | right : Formula → Derivation → Derivation
  | cases : Derivation → Derivation → Derivation → Derivation
  | absurd : Formula → Derivation → Derivation
  deriving DecidableEq, Repr

def infer (ctx : List Formula) : Derivation → Option Formula
  | .use f => if f ∈ ctx then some f else none
  | .truth => some .truth
  | .pair p q => match infer ctx p, infer ctx q with
      | some f, some g => some (.conj f g)
      | _, _ => none
  | .first p => match infer ctx p with
      | some (.conj f _) => some f
      | _ => none
  | .second p => match infer ctx p with
      | some (.conj _ g) => some g
      | _ => none
  | .abstract f p => match infer (f :: ctx) p with
      | some g => some (.impl f g)
      | _ => none
  | .apply p q => match infer ctx p, infer ctx q with
      | some (.impl f g), some f' => if f = f' then some g else none
      | _, _ => none
  | .left g p => match infer ctx p with
      | some f => some (.disj f g)
      | _ => none
  | .right f p => match infer ctx p with
      | some g => some (.disj f g)
      | _ => none
  | .cases p q r => match infer ctx p with
      | some (.disj f g) => match infer (f :: ctx) q, infer (g :: ctx) r with
          | some h, some h' => if h = h' then some h else none
          | _, _ => none
      | _ => none
  | .absurd f p => match infer ctx p with
      | some .falsity => some f
      | _ => none

def check (ctx : List Formula) (target : Formula) (proof : Derivation) : Bool :=
  decide (infer ctx proof = some target)

theorem satisfies_cons (v : Nat → Prop) (ctx : List Formula) (f : Formula)
    (hf : Denote v f) (hc : Satisfies v ctx) : Satisfies v (f :: ctx) := by
  intro g hg
  rcases List.mem_cons.mp hg with h | h
  · subst g; exact hf
  · exact hc g h

/-- Soundness is proved for the executable inference function itself. -/
theorem infer_sound (proof : Derivation) (ctx : List Formula) (target : Formula)
    (hi : infer ctx proof = some target) (v : Nat → Prop) (hc : Satisfies v ctx) :
    Denote v target := by
  induction proof generalizing ctx target with
  | use f =>
      simp only [infer] at hi
      split at hi
      · cases hi; exact hc _ ‹_›
      · contradiction
  | truth => cases hi; trivial
  | pair p q ihp ihq =>
      simp only [infer] at hi
      split at hi
      · cases hi; exact ⟨ihp _ _ ‹_› hc, ihq _ _ ‹_› hc⟩
      · contradiction
  | first p ih =>
      simp only [infer] at hi
      split at hi
      · cases hi; exact (ih _ (.conj _ _) ‹_› hc).1
      · contradiction
  | second p ih =>
      simp only [infer] at hi
      split at hi
      · cases hi; exact (ih _ (.conj _ _) ‹_› hc).2
      · contradiction
  | abstract f p ih =>
      simp only [infer] at hi
      split at hi
      · cases hi
        intro hf
        exact ih _ _ ‹_› (satisfies_cons v ctx f hf hc)
      · contradiction
  | apply p q ihp ihq =>
      simp only [infer] at hi
      split at hi
      · split at hi
        · rename_i heq
          subst heq
          cases hi
          exact (ihp _ (.impl _ _) ‹_› hc) (ihq _ _ ‹_› hc)
        · contradiction
      · contradiction
  | left g p ih =>
      simp only [infer] at hi
      split at hi
      · cases hi; exact Or.inl (ih _ _ ‹_› hc)
      · contradiction
  | right f p ih =>
      simp only [infer] at hi
      split at hi
      · cases hi; exact Or.inr (ih _ _ ‹_› hc)
      · contradiction
  | cases p q r ihp ihq ihr =>
      simp only [infer] at hi
      split at hi
      · split at hi
        · split at hi
          · rename_i heq
            subst heq
            cases hi
            rcases ihp _ (.disj _ _) ‹_› hc with hf | hg
            · exact ihq _ _ ‹_› (satisfies_cons v ctx _ hf hc)
            · exact ihr _ _ ‹_› (satisfies_cons v ctx _ hg hc)
          · contradiction
        · contradiction
      · contradiction
  | absurd f p ih =>
      simp only [infer] at hi
      split at hi
      · exact False.elim (ih _ .falsity ‹_› hc)
      · contradiction

theorem check_sound (ctx : List Formula) (target : Formula) (proof : Derivation)
    (h : check ctx target proof = true) (v : Nat → Prop) (hc : Satisfies v ctx) :
    Denote v target :=
  infer_sound proof ctx target (of_decide_eq_true h) v hc

theorem no_closed_false_proof (proof : Derivation) : check [] .falsity proof = false := by
  cases h : check [] .falsity proof with
  | false => rfl
  | true =>
      have bad := check_sound [] .falsity proof h (fun _ => False)
        (by intro f hf; simp at hf)
      exact False.elim bad

theorem identity_checked (f : Formula) :
    check [] (.impl f f) (.abstract f (.use f)) = true := by
  simp [check, infer]

theorem premise_checked (ctx : List Formula) (f : Formula) (h : f ∈ ctx) :
    check ctx f (.use f) = true := by simp [check, infer, h]

theorem truth_checked (ctx : List Formula) : check ctx .truth .truth = true := rfl

theorem check_target_unique (ctx : List Formula) (p : Derivation) (f g : Formula)
    (hf : check ctx f p = true) (hg : check ctx g p = true) : f = g := by
  have h := (of_decide_eq_true hf).symm.trans (of_decide_eq_true hg)
  exact Option.some.inj h

/-- Sequential closure of a list of checked artifacts. Later claims can use only
already certified formulas, never a future or circular premise. -/
def CheckedChain : List Formula → List (Formula × Derivation) → Prop
  | _, [] => True
  | ctx, (f,p) :: rest => check ctx f p = true ∧ CheckedChain (f :: ctx) rest

def chainContext : List Formula → List (Formula × Derivation) → List Formula
  | ctx, [] => ctx
  | ctx, (f,_) :: rest => chainContext (f :: ctx) rest

theorem checked_chain_sound (ctx : List Formula) (xs : List (Formula × Derivation))
    (h : CheckedChain ctx xs) (v : Nat → Prop) (hc : Satisfies v ctx) :
    Satisfies v (chainContext ctx xs) := by
  induction xs generalizing ctx with
  | nil => exact hc
  | cons item xs ih =>
      rcases item with ⟨f,p⟩
      exact ih _ h.2 (satisfies_cons v ctx f (check_sound ctx f p h.1 v hc) hc)

theorem closed_chain_sound (xs : List (Formula × Derivation))
    (h : CheckedChain [] xs) : ∀ v : Nat → Prop, Satisfies v (chainContext [] xs) := by
  intro v
  exact checked_chain_sound [] xs h v (by intro f hf; simp at hf)

end Komorebi.AVOC.Certificate
