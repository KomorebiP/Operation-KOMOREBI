import Std

namespace Komorebi.Representation.Cardinality
universe u v

structure Bijection (X : Type u) (Y : Type v) where
  toFun : X → Y
  invFun : Y → X
  left_inv : ∀ x, invFun (toFun x) = x
  right_inv : ∀ y, toFun (invFun y) = y

theorem bijection_injective {X : Type u} {Y : Type v} (b : Bijection X Y)
    (x y : X) (h : b.toFun x = b.toFun y) : x = y := by
  have hh := congrArg b.invFun h
  rw [b.left_inv, b.left_inv] at hh
  exact hh

theorem ofFn_nodup_of_injective {X : Type u} (n : Nat) (f : Fin n → X)
    (hf : ∀ i j, f i = f j → i = j) : (List.ofFn f).Nodup := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [List.ofFn_succ, List.nodup_cons]
    constructor
    · intro hmem
      obtain ⟨i, hi⟩ := List.mem_ofFn.mp hmem
      exact Fin.succ_ne_zero i (hf i.succ 0 hi)
    · apply ih
      intro i j hij
      exact Fin.succ_inj.mp (hf i.succ j.succ hij)

theorem fin_injection_bound {n m : Nat} (f : Fin n → Fin m)
    (hf : ∀ i j, f i = f j → i = j) : n ≤ m := by
  have hnodup := ofFn_nodup_of_injective n f hf
  have hsub : List.ofFn f ⊆ List.ofFn (fun i : Fin m => i) := by
    intro a _
    exact List.mem_ofFn.mpr ⟨a, rfl⟩
  simpa only [List.length_ofFn] using hnodup.length_le_of_subset hsub

theorem at_most_one_coordinate_pack {m n : Nat} [NeZero m] (hn : n < 2) :
    ∃ f : (Fin n → Fin m) → Fin m, ∀ x y, f x = f y → x = y := by
  cases n with
  | zero =>
    refine ⟨fun _ => 0, ?_⟩
    intro x y _; funext i; exact Fin.elim0 i
  | succ n =>
    have h : n = 0 := by omega
    subst n
    refine ⟨fun x => x 0, ?_⟩
    intro x y hxy
    funext i
    have hi : i = (0 : Fin 1) := by apply Fin.ext; omega
    rw [hi]; exact hxy

end Komorebi.Representation.Cardinality
