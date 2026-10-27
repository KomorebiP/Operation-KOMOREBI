import Mathlib.Data.ZMod.Basic

namespace Komorebi.StrongArtin.CyclicSupport

variable (p : ℕ) [Fact p.Prime]

/-- A nonempty subset of the cyclic label space that is stable under the
quotient-twist generator `+1` is the entire label space. -/
theorem nonempty_add_one_stable_eq_univ (S : Set (ZMod p))
    (hne : S.Nonempty)
    (hstep : ∀ x : ZMod p, x ∈ S → x + 1 ∈ S) :
    S = Set.univ := by
  ext x
  simp only [Set.mem_univ, iff_true]
  obtain ⟨a, ha⟩ := hne
  have hiter : ∀ n : ℕ, a + (n : ZMod p) ∈ S := by
    intro n
    induction n with
    | zero => simpa using ha
    | succ n ih =>
        have hs := hstep (a + (n : ZMod p)) ih
        simpa [Nat.cast_succ, add_assoc] using hs
  have hd := hiter (x - a).val
  rw [@ZMod.natCast_zmod_val p ⟨(Fact.out : p.Prime).ne_zero⟩] at hd
  simpa [sub_eq_add_neg, add_assoc, add_comm, add_left_comm] using hd

end Komorebi.StrongArtin.CyclicSupport

#print axioms Komorebi.StrongArtin.CyclicSupport.nonempty_add_one_stable_eq_univ
