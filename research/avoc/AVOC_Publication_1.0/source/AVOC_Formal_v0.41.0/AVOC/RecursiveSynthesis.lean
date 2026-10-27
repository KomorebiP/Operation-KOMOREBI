import AVOC.SemanticIndex

namespace Komorebi.AVOC.SemanticSynthesis

open Synthesis

/-- Every source expression has a semantically identical, no-larger representative. -/
def Covers (xs ys : List Program) : Prop :=
  ∀ p ∈ xs, ∃ q ∈ ys, Equivalent q p ∧ nodes q ≤ nodes p

theorem covers_refl (xs : List Program) : Covers xs xs :=
  fun p hp => ⟨p, hp, equivalent_refl p, Nat.le_refl _⟩

theorem covers_trans {xs ys zs : List Program} (h : Covers xs ys) (k : Covers ys zs) :
    Covers xs zs := by
  intro p hp
  obtain ⟨q, hq, he, hn⟩ := h p hp
  obtain ⟨r, hr, hf, hm⟩ := k q hq
  exact ⟨r, hr, equivalent_trans hf he, Nat.le_trans hm hn⟩

theorem compact_covers_all (xs : List Program) : Covers xs (codes (compact xs)) :=
  compact_covers xs

theorem equivalent_neg {p q : Program} (h : Equivalent p q) : Equivalent (.neg p) (.neg q) :=
  fun s => by simp only [run, h s]

theorem equivalent_conjunction {p q r t : Program} (h : Equivalent p q) (k : Equivalent r t) :
    Equivalent (.conjunction p r) (.conjunction q t) :=
  fun s => by simp only [run, h s, k s]

theorem equivalent_disjunction {p q r t : Program} (h : Equivalent p q) (k : Equivalent r t) :
    Equivalent (.disjunction p r) (.disjunction q t) :=
  fun s => by simp only [run, h s, k s]

theorem equivalent_exclusive {p q r t : Program} (h : Equivalent p q) (k : Equivalent r t) :
    Equivalent (.exclusive p r) (.exclusive q t) :=
  fun s => by simp only [run, h s, k s]

theorem pairs_covers (op : Program → Program → Program)
    (heq : ∀ p q r t, Equivalent p q → Equivalent r t → Equivalent (op p r) (op q t))
    (hsize : ∀ p q, nodes (op p q) = nodes p + nodes q + 1)
    {xs ys : List Program} (h : Covers xs ys) :
    Covers (pairs op xs xs) (pairs op ys ys) := by
  intro p hp
  obtain ⟨a, ha, b, hb, hab⟩ := (mem_pairs _ _ _ _).mp hp
  subst p
  obtain ⟨a', ha', hea, hna⟩ := h a ha
  obtain ⟨b', hb', heb, hnb⟩ := h b hb
  refine ⟨op a' b', (mem_pairs _ _ _ _).mpr ⟨a', ha', b', hb', rfl⟩,
    heq _ _ _ _ hea heb, ?_⟩
  simp only [hsize]
  omega

theorem expand_covers {xs ys : List Program} (h : Covers xs ys) : Covers (expand xs) (expand ys) := by
  intro p hp
  simp only [expand, List.mem_append] at hp
  rcases hp with (((hp | hp) | hp) | hp) | hp
  · obtain ⟨q, hq, he, hn⟩ := h p hp
    exact ⟨q, by simp [expand, hq], he, hn⟩
  · obtain ⟨p', hp', he⟩ := List.mem_map.mp hp
    subst p
    obtain ⟨q, hq, he, hn⟩ := h p' hp'
    refine ⟨.neg q, ?_, equivalent_neg he, ?_⟩
    · simp only [expand, List.mem_append]
      exact Or.inl (Or.inl (Or.inl (Or.inr (List.mem_map.mpr ⟨q,hq,rfl⟩))))
    · simp only [nodes]; omega
  · obtain ⟨q, hq, he, hn⟩ := pairs_covers .conjunction
      (fun _ _ _ _ => equivalent_conjunction) (fun _ _ => rfl) h p hp
    exact ⟨q, by simp [expand, hq], he, hn⟩
  · obtain ⟨q, hq, he, hn⟩ := pairs_covers .disjunction
      (fun _ _ _ _ => equivalent_disjunction) (fun _ _ => rfl) h p hp
    exact ⟨q, by simp [expand, hq], he, hn⟩
  · obtain ⟨q, hq, he, hn⟩ := pairs_covers .exclusive
      (fun _ _ _ _ => equivalent_exclusive) (fun _ _ => rfl) h p hp
    exact ⟨q, by simp [expand, hq], he, hn⟩

theorem pairs_mono (op : Program → Program → Program) {xs ys : List Program}
    (h : ∀ p ∈ xs, p ∈ ys) : ∀ p ∈ pairs op xs xs, p ∈ pairs op ys ys := by
  intro p hp
  obtain ⟨a, ha, b, hb, he⟩ := (mem_pairs _ _ _ _).mp hp
  exact (mem_pairs _ _ _ _).mpr ⟨a, h a ha, b, h b hb, he⟩

theorem expand_mono {xs ys : List Program} (h : ∀ p ∈ xs, p ∈ ys) :
    ∀ p ∈ expand xs, p ∈ expand ys := by
  intro p hp
  simp only [expand, List.mem_append] at hp ⊢
  rcases hp with (((hp | hp) | hp) | hp) | hp
  · exact Or.inl (Or.inl (Or.inl (Or.inl (h p hp))))
  · obtain ⟨q,hq,he⟩ := List.mem_map.mp hp
    exact Or.inl (Or.inl (Or.inl (Or.inr (List.mem_map.mpr ⟨q,h q hq,he⟩))))
  · exact Or.inl (Or.inl (Or.inr (pairs_mono _ h p hp)))
  · exact Or.inl (Or.inr (pairs_mono _ h p hp))
  · exact Or.inr (pairs_mono _ h p hp)

/-- The next search actually uses the previous certified representatives as its operands. -/
def representatives : Nat → List Entry
  | 0 => compact atoms
  | d + 1 => compact (expand (codes (representatives d)))

theorem representative_in_frozen (d : Nat) (p : Program) (hp : p ∈ codes (representatives d)) :
    p ∈ programs d := by
  induction d generalizing p with
  | zero => exact compact_codes_origin atoms p hp
  | succ d ih =>
    have hx := compact_codes_origin (expand (codes (representatives d))) p hp
    exact expand_mono (fun q hq => ih q hq) p hx

theorem recursive_coverage (d : Nat) : Covers (programs d) (codes (representatives d)) := by
  induction d with
  | zero => exact compact_covers_all atoms
  | succ d ih => exact covers_trans (expand_covers ih) (compact_covers_all _)

theorem retained_knowledge_not_lost (d : Nat) :
    Covers (codes (representatives d)) (codes (representatives (d+1))) := by
  intro p hp
  apply compact_covers (expand (codes (representatives d))) p
  simp [expand, hp]

def answer (reference : Program) (depth : Nat) : Program :=
  select reference reference (codes (representatives depth))

theorem answer_sound (r : Program) (d : Nat) : Equivalent (answer r d) r :=
  select_sound _ _ _ (equivalent_refl _)

theorem answer_no_larger (r : Program) (d : Nat) : nodes (answer r d) ≤ nodes r :=
  select_no_larger _ _ _

theorem answer_bounded_optimal (r : Program) (d : Nat) (p : Program)
    (hp : height p ≤ d) (he : Equivalent p r) : nodes (answer r d) ≤ nodes p := by
  obtain ⟨q,hq,hqp,hn⟩ := recursive_coverage d p (bounded_grammar_complete d p hp)
  exact Nat.le_trans (select_minimum r r _ q hq (equivalent_trans hqp he)) hn

/-- Equal optimum cost to full enumeration, for every reference and grammar depth.
The AST chosen on ties may differ. No physical-runtime speedup is asserted here. -/
theorem same_optimum_as_frozen (r : Program) (d : Nat) :
    nodes (answer r d) = nodes (select r r (programs d)) := by
  apply Nat.le_antisymm
  · rcases select_member r r (programs d) with hi | hp
    · rw [hi]; exact answer_no_larger r d
    · obtain ⟨q,hq,he,hn⟩ := recursive_coverage d _ hp
      have hs := select_sound r r (programs d) (equivalent_refl r)
      exact Nat.le_trans (select_minimum r r _ q hq (equivalent_trans he hs)) hn
  · rcases select_member r r (codes (representatives d)) with hi | hp
    · change nodes (select r r (programs d)) ≤ nodes (select r r (codes (representatives d)))
      rw [hi]; exact select_no_larger _ _ _
    · exact select_minimum r r (programs d) _ (representative_in_frozen d _ hp) (answer_sound r d)

theorem compact_preserves_query_optimum (r : Program) (xs : List Program) :
    nodes (select r r (codes (compact xs))) = nodes (select r r xs) := by
  apply Nat.le_antisymm
  · rcases select_member r r xs with hi | hp
    · rw [hi]; exact select_no_larger _ _ _
    · obtain ⟨q,hq,he,hn⟩ := compact_covers xs _ hp
      exact Nat.le_trans (select_minimum r r _ q hq
        (equivalent_trans he (select_sound _ _ _ (equivalent_refl r)))) hn
  · rcases select_member r r (codes (compact xs)) with hi | hp
    · rw [hi]; exact select_no_larger _ _ _
    · exact select_minimum r r xs _ (compact_codes_origin xs _ hp)
        (select_sound _ _ _ (equivalent_refl r))

end Komorebi.AVOC.SemanticSynthesis
