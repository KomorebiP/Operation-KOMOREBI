import CircuitObstructions.Gates

/-!
# Boolean degree certificates

`DegreeLE d f` says that f is an XOR of monomials of length at most d.
Repeated input variables are permitted in a representation. Their Boolean
idempotence can only lower multilinear degree. Zero has degree bound zero.
This is a semantic polynomial representation, not a syntactic circuit weight.
-/
namespace CircuitObstructions

abbrev BFun (n : Nat) := (Fin n → Bool) → Bool

def bprod {W : Type} : List W → State W → Bool
  | [], _ => true
  | i :: is, s => s i && bprod is s

@[simp] theorem bprod_nil {W : Type} (s : State W) : bprod [] s = true := rfl
@[simp] theorem bprod_cons {W : Type} (i : W) (is : List W) (s : State W) :
    bprod (i :: is) s = (s i && bprod is s) := rfl

theorem bprod_append {W : Type} (l k : List W) (s : State W) :
    bprod (l ++ k) s = (bprod l s && bprod k s) := by
  induction l with
  | nil => simp [bprod]
  | cons i is ih => simp [bprod, ih, Bool.and_assoc]

theorem xor_and_right (a b c : Bool) :
    ((Bool.xor a b) && c) = Bool.xor (a && c) (b && c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem and_xor_right (a b c : Bool) :
    (a && Bool.xor b c) = Bool.xor (a && b) (a && c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem not_as_xor_one (a : Bool) : (!a) = Bool.xor a true := by
  cases a <;> rfl

inductive DegreeLE {n : Nat} (d : Nat) : BFun n → Prop where
  | zero : DegreeLE d (fun _ => false)
  | monomial (l : List (Fin n)) (bound : l.length ≤ d) :
      DegreeLE d (fun x => bprod l x)
  | add {f g : BFun n} : DegreeLE d f → DegreeLE d g →
      DegreeLE d (fun x => Bool.xor (f x) (g x))

theorem DegreeLE.mono {n d e : Nat} {f : BFun n}
    (h : DegreeLE d f) (hde : d ≤ e) : DegreeLE e f := by
  induction h with
  | zero => exact .zero
  | monomial l hl => exact .monomial l (Nat.le_trans hl hde)
  | add _ _ ihf ihg => exact .add ihf ihg

theorem DegreeLE.one (n d : Nat) : DegreeLE (n := n) d (fun _ => true) := by
  exact .monomial [] (Nat.zero_le d)

theorem DegreeLE.constant (n d : Nat) (b : Bool) :
    DegreeLE (n := n) d (fun _ => b) := by
  cases b
  · exact .zero
  · exact DegreeLE.one n d

theorem DegreeLE.variable {n : Nat} (i : Fin n) :
    DegreeLE 1 (fun x => x i) := by
  simpa using DegreeLE.monomial (d := 1) [i] (by simp)

theorem DegreeLE.xor {n d e : Nat} {f g : BFun n}
    (hf : DegreeLE d f) (hg : DegreeLE e g) :
    DegreeLE (max d e) (fun x => Bool.xor (f x) (g x)) := by
  exact .add (hf.mono (Nat.le_max_left d e)) (hg.mono (Nat.le_max_right d e))

theorem DegreeLE.not {n d : Nat} {f : BFun n} (hf : DegreeLE d f) :
    DegreeLE d (fun x => ! f x) := by
  simpa only [not_as_xor_one] using DegreeLE.add hf (DegreeLE.one n d)

theorem DegreeLE.monomial_mul {n d e : Nat} (l : List (Fin n)) (hl : l.length ≤ d)
    {g : BFun n} (hg : DegreeLE e g) :
    DegreeLE (d + e) (fun x => bprod l x && g x) := by
  induction hg with
  | zero => simpa using (DegreeLE.zero (n := n) (d := d + e))
  | monomial k hk =>
      have hlen : (l ++ k).length ≤ d + e := by simp only [List.length_append]; omega
      simpa only [bprod_append] using DegreeLE.monomial (l ++ k) hlen
  | add _ _ ihf ihg =>
      simpa only [and_xor_right] using DegreeLE.add ihf ihg

theorem DegreeLE.mul {n d e : Nat} {f g : BFun n}
    (hf : DegreeLE d f) (hg : DegreeLE e g) :
    DegreeLE (d + e) (fun x => f x && g x) := by
  induction hf with
  | zero => simpa using (DegreeLE.zero (n := n) (d := d + e))
  | monomial l hl => exact DegreeLE.monomial_mul l hl hg
  | add _ _ ihf ihg =>
      simpa only [xor_and_right] using DegreeLE.add ihf ihg

theorem DegreeLE.product {n : Nat} {W : Type} (l : List W) (s : (Fin n → Bool) → State W)
    (h : ∀ i, DegreeLE 1 (fun x => s x i)) :
    DegreeLE l.length (fun x => bprod l (s x)) := by
  induction l with
  | nil => exact DegreeLE.one n 0
  | cons i is ih =>
      simpa only [List.length_cons, bprod_cons, Nat.add_comm 1] using (h i).mul ih

/-- A concrete XOR-list representation, retained for a direct polynomial witness. -/
def polyEval {n : Nat} : List (List (Fin n)) → BFun n
  | [], _ => false
  | l :: p, x => Bool.xor (bprod l x) (polyEval p x)

theorem polyEval_append {n : Nat} (p q : List (List (Fin n))) (x : Fin n → Bool) :
    polyEval (p ++ q) x = Bool.xor (polyEval p x) (polyEval q x) := by
  induction p with
  | nil => simp [polyEval]
  | cons l ls ih => simp [polyEval, ih]

theorem DegreeLE.polynomial_witness {n d : Nat} {f : BFun n} (h : DegreeLE d f) :
    ∃ p : List (List (Fin n)), (∀ l ∈ p, l.length ≤ d) ∧ polyEval p = f := by
  induction h with
  | zero => exact ⟨[], by simp, rfl⟩
  | monomial l hl =>
      refine ⟨[l], by simpa using hl, ?_⟩
      funext x
      simp [polyEval]
  | add _ _ ihf ihg =>
      obtain ⟨p, hp, hpf⟩ := ihf
      obtain ⟨q, hq, hqg⟩ := ihg
      refine ⟨p ++ q, ?_, ?_⟩
      · intro l hl
        rcases List.mem_append.mp hl with hl | hl
        · exact hp l hl
        · exact hq l hl
      · funext x
        rw [polyEval_append, hpf, hqg]

theorem polynomial_degree_certificate {n d : Nat} (p : List (List (Fin n)))
    (hp : ∀ l ∈ p, l.length ≤ d) : DegreeLE d (polyEval p) := by
  induction p with
  | nil => exact .zero
  | cons l ls ih =>
      exact .add (.monomial l (hp l (by simp)))
        (ih (fun k hk => hp k (by simp [hk])))

theorem degreeLE_iff_polynomial {n d : Nat} (f : BFun n) :
    DegreeLE d f ↔ ∃ p : List (List (Fin n)),
      (∀ l ∈ p, l.length ≤ d) ∧ polyEval p = f := by
  constructor
  · exact DegreeLE.polynomial_witness
  · rintro ⟨p, hp, rfl⟩
    exact polynomial_degree_certificate p hp

end CircuitObstructions
