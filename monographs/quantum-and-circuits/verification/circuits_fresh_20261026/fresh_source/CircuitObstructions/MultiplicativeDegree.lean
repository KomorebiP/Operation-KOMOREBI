import CircuitObstructions.Degree
import CircuitObstructions.CutComparison

/-!
# Degree growth with sharing

The invariant covers products of arbitrary lists of register coordinates.
Boolean idempotence removes repeated occurrences of an updated target before
expansion. One Toffoli can therefore add at most one to the degree budget,
independently of fan-out, workspace, and output feedback.
-/
namespace CircuitObstructions

def withoutWire {W : Type} [DecidableEq W] (l : List W) (t : W) : List W :=
  l.filter (fun i => decide (i ≠ t))

theorem withoutWire_length_le {W : Type} [DecidableEq W] (l : List W) (t : W) :
    (withoutWire l t).length ≤ l.length := by
  exact List.length_filter_le _ _

theorem withoutWire_length_lt {W : Type} [DecidableEq W]
    (l : List W) (t : W) (ht : t ∈ l) :
    (withoutWire l t).length + 1 ≤ l.length := by
  induction l with
  | nil => simp at ht
  | cons i is ih =>
      by_cases hit : i = t
      · subst i
        simpa [withoutWire] using Nat.add_le_add_right (withoutWire_length_le is t) 1
      · have htail : t ∈ is := by simpa [hit, Ne.symm hit] using ht
        simpa [withoutWire, hit] using Nat.add_le_add_right (ih htail) 1

theorem bprod_write {W : Type} [DecidableEq W]
    (l : List W) (s : State W) (t : W) (b : Bool) :
    bprod l (write s t b) =
      ((if t ∈ l then b else true) && bprod (withoutWire l t) s) := by
  induction l with
  | nil => simp [bprod, withoutWire]
  | cons i is ih =>
      by_cases hit : i = t
      · subst i
        by_cases hm : t ∈ is <;>
          simp [bprod, withoutWire, write, ih, hm]
      · by_cases hm : t ∈ is <;>
          simp [bprod, withoutWire, write, ih, hit, Ne.symm hit, hm,
                Bool.and_left_comm]

theorem bprod_write_absent {W : Type} [DecidableEq W]
    (l : List W) (s : State W) (t : W) (b : Bool) (ht : t ∉ l) :
    bprod l (write s t b) = bprod l s := by
  induction l with
  | nil => rfl
  | cons i is ih =>
      have hi : i ≠ t := by intro h; subst i; exact ht (by simp)
      have his : t ∉ is := by intro h; exact ht (by simp [h])
      simp only [bprod_cons, write_other s t i b hi, ih his]

def WorkspaceDegree {n : Nat} {W : Type}
    (s : (Fin n → Bool) → State W) (t : Nat) : Prop :=
  ∀ l : List W, DegreeLE (t + l.length) (fun x => bprod l (s x))

theorem workspaceDegree_initial {n : Nat} {W : Type}
    (s : (Fin n → Bool) → State W)
    (h : ∀ i, DegreeLE 1 (fun x => s x i)) : WorkspaceDegree s 0 := by
  intro l
  simpa using DegreeLE.product l s h

def toggleProduct {n : Nat} {W : Type} [DecidableEq W]
    (s : (Fin n → Bool) → State W) (t : W) (controls : List W) :
    (Fin n → Bool) → State W :=
  fun x => write (s x) t (Bool.xor (s x t) (bprod controls (s x)))

theorem workspaceDegree_toggle {n : Nat} {W : Type} [DecidableEq W]
    (s : (Fin n → Bool) → State W) (t : W) (controls : List W)
    (k : Nat) (h : WorkspaceDegree s k) :
    WorkspaceDegree (toggleProduct s t controls) (k + (controls.length - 1)) := by
  intro l
  by_cases ht : t ∈ l
  · let rest := withoutWire l t
    have hlen : rest.length + 1 ≤ l.length := withoutWire_length_lt l t ht
    have hfirst := h (t :: rest)
    have hsecond := h (controls ++ rest)
    have hb1 : k + (t :: rest).length ≤ k + (controls.length - 1) + l.length := by
      simp only [List.length_cons]; omega
    have hb2 : k + (controls ++ rest).length ≤ k + (controls.length - 1) + l.length := by
      simp only [List.length_append]; omega
    have hb := DegreeLE.add (hfirst.mono hb1) (hsecond.mono hb2)
    have heq : (fun x => bprod l (toggleProduct s t controls x)) =
        (fun x => Bool.xor (bprod (t :: rest) (s x))
          (bprod (controls ++ rest) (s x))) := by
      funext x
      simp only [toggleProduct, bprod_write, ite_eq_left ht, xor_and_right,
                 bprod_cons, bprod_append]
      rfl
    rw [heq]
    exact hb
  · have heq : (fun x => bprod l (toggleProduct s t controls x)) =
        (fun x => bprod l (s x)) := by
      funext x
      exact bprod_write_absent l (s x) t _ ht
    rw [heq]
    exact (h l).mono (by omega)

theorem workspaceDegree_gate {n : Nat} {W : Type} [DecidableEq W]
    (s : (Fin n → Bool) → State W) (g : Gate W) (k : Nat)
    (h : WorkspaceDegree s k) :
    WorkspaceDegree (fun x => g.eval (s x)) (k + g.toffoliCost) := by
  cases g with
  | not t =>
      have hh := workspaceDegree_toggle s t [] k h
      change WorkspaceDegree (fun x => write (s x) t
        (Bool.xor (s x t) (bprod [] (s x)))) (k + ([].length - 1)) at hh
      simpa only [Gate.eval, Gate.toffoliCost, bprod_nil, List.length_nil,
        Nat.zero_sub, Nat.add_zero, not_as_xor_one] using hh
  | cnot c t hct =>
      have hh := workspaceDegree_toggle s t [c] k h
      change WorkspaceDegree (fun x => write (s x) t
        (Bool.xor (s x t) (bprod [c] (s x)))) (k + ([c].length - 1)) at hh
      simpa only [Gate.eval, Gate.toffoliCost, bprod_cons, bprod_nil,
        Bool.and_true, List.length_cons, List.length_nil, Nat.add_zero, Nat.add_sub_cancel] using hh
  | toffoli a b t hab hat hbt =>
      have hh := workspaceDegree_toggle s t [a,b] k h
      change WorkspaceDegree (fun x => write (s x) t
        (Bool.xor (s x t) (bprod [a,b] (s x)))) (k + ([a,b].length - 1)) at hh
      simpa only [Gate.eval, Gate.toffoliCost, bprod_cons, bprod_nil,
        Bool.and_true, List.length_cons, List.length_nil] using hh

theorem workspaceDegree_run {n : Nat} {W : Type} [DecidableEq W]
    (c : Circuit W) (s : (Fin n → Bool) → State W) (k : Nat)
    (h : WorkspaceDegree s k) :
    WorkspaceDegree (fun x => run c (s x)) (k + toffoliCount c) := by
  induction c generalizing s k with
  | nil => simpa [toffoliCount] using h
  | cons g gs ih =>
      have hg := workspaceDegree_gate s g k h
      have hh := ih (fun x => g.eval (s x)) (k + g.toffoliCost) hg
      simpa [toffoliCount, Nat.add_assoc] using hh

theorem run_coordinate_degree {n : Nat} {W : Type} [DecidableEq W]
    (c : Circuit W) (s : (Fin n → Bool) → State W)
    (hs : ∀ i, DegreeLE 1 (fun x => s x i)) (i : W) :
    DegreeLE (toffoliCount c + 1) (fun x => run c (s x) i) := by
  have h := workspaceDegree_run c s 0 (workspaceDegree_initial s hs) [i]
  simpa [bprod] using h

theorem canonical_boundary_degree (n a : Nat) (b : Bool) (i : CanonicalWire n a) :
    DegreeLE 1 (fun x => (canonicalBoundary n a).encode x b i) := by
  cases i with
  | inl j => exact DegreeLE.variable j
  | inr j =>
      cases j with
      | inl j => exact DegreeLE.constant n 1 false
      | inr j => exact DegreeLE.constant n 1 b

theorem canonical_run_coordinate_degree (n a : Nat) (c : Circuit (CanonicalWire n a))
    (b : Bool) (i : CanonicalWire n a) :
    DegreeLE (toffoliCount c + 1)
      (fun x => run c ((canonicalBoundary n a).encode x b) i) := by
  exact run_coordinate_degree c _ (canonical_boundary_degree n a b) i

theorem canonical_cut_packet_degree (n a : Nat)
    (p q : Circuit (CanonicalWire n a)) (i : CanonicalWire n a) :
    DegreeLE (max (toffoliCount p) (toffoliCount q) + 1)
      (fun x => packet (canonicalBoundary n a) p q x i) := by
  have h := (canonical_run_coordinate_degree n a p false i).xor
    (canonical_run_coordinate_degree n a q.reverse false i)
  have hm : max (toffoliCount p + 1) (toffoliCount q + 1) =
      max (toffoliCount p) (toffoliCount q) + 1 := by omega
  simpa only [toffoliCount_reverse, hm, packet] using h

end CircuitObstructions
