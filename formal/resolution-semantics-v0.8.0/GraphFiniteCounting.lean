import GraphCounting

/-! Finite fiber counting. Lists carry completeness and no-duplicate proofs. -/

namespace KRS.Graph

universe u v

theorem indicator_sum {A : Type u} [DecidableEq A] (l : List A) (hl : l.Nodup)
    (a : A) : (l.map (fun b => if a = b then 1 else 0)).sum =
      if a ∈ l then 1 else 0 := by
  induction l with
  | nil => simp
  | cons b l ih =>
    obtain ⟨hb, ht⟩ := List.nodup_cons.mp hl
    by_cases h : a = b
    · subst a
      simp [ih ht, hb]
    · simp [h, ih ht]

theorem sum_map_add {A : Type u} (l : List A) (f g : A → Nat) :
    (l.map (fun a => f a + g a)).sum = (l.map f).sum + (l.map g).sum := by
  induction l with
  | nil => simp
  | cons a l ih => simp [ih, Nat.add_assoc, Nat.add_left_comm]

theorem sum_map_const {A : Type u} (l : List A) (k : Nat) :
    (l.map (fun _ => k)).sum = l.length * k := by
  induction l with
  | nil => simp
  | cons a l ih => simp [ih, Nat.add_mul, Nat.add_comm]

theorem fiber_partition_length {A : Type u} {B : Type v} [DecidableEq B]
    (xs : List A) (ys : List B) (f : A → B) (hy : ys.Nodup)
    (hc : ∀ x, x ∈ xs → f x ∈ ys) :
    xs.length = (ys.map (fun y => (xs.filter (fun x => f x == y)).length)).sum := by
  induction xs with
  | nil => simp [sum_map_const]
  | cons x xs ih =>
    have hi := ih (fun a ha => hc a (by simp [ha]))
    have hx := indicator_sum ys hy (f x)
    have hm := hc x (by simp)
    have hf (y : B) : ((x :: xs).filter (fun x => f x == y)).length =
        (if f x = y then 1 else 0) + (xs.filter (fun x => f x == y)).length := by
      by_cases h : f x = y <;> simp [h, Nat.add_comm]
    simp only [List.length_cons, hf, sum_map_add]
    simp only [hm, ↓reduceIte] at hx
    omega

theorem constant_fiber_count {A : Type u} {B : Type v} [DecidableEq B]
    (xs : List A) (ys : List B) (f : A → B) (hy : ys.Nodup)
    (hc : ∀ x, x ∈ xs → f x ∈ ys) (k : Nat)
    (hk : ∀ y, y ∈ ys → (xs.filter (fun x => f x == y)).length = k) :
    xs.length = ys.length * k := by
  rw [fiber_partition_length xs ys f hy hc]
  have hmap : ys.map (fun y => (xs.filter (fun x => f x == y)).length) =
      ys.map (fun _ => k) := List.map_congr_left hk
  rw [hmap, sum_map_const]

end KRS.Graph
