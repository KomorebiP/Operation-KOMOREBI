import AVOC.BoundedSynthesis

namespace Komorebi.AVOC.SemanticSynthesis

open Synthesis

/-- Complete semantics, not a sampled test signature. -/
def signature (p : Program) : List Bool := inputs.map (run p)

theorem signature_eq_iff (p q : Program) : signature p = signature q ↔ Equivalent p q := by
  constructor
  · intro h s
    exact List.map_eq_map_iff.mp h s (input_complete s)
  · intro h
    exact List.map_congr_left (fun s _ => h s)

/-- Cached semantics and size carry equations to the retained expression. -/
structure Entry where
  code : Program
  bits : List Bool
  size : Nat
  bits_correct : bits = signature code
  size_correct : size = nodes code

def pack (p : Program) : Entry := ⟨p, signature p, nodes p, rfl, rfl⟩

def Dominates (p q : Entry) : Prop := Equivalent p.code q.code ∧ p.size ≤ q.size

theorem dominates_refl (p : Entry) : Dominates p p := ⟨equivalent_refl _, Nat.le_refl _⟩

theorem dominates_trans {p q r : Entry} (hp : Dominates p q) (hq : Dominates q r) :
    Dominates p r := ⟨equivalent_trans hp.1 hq.1, Nat.le_trans hp.2 hq.2⟩

theorem equal_bits_equivalent (p q : Entry) (h : p.bits = q.bits) : Equivalent p.code q.code := by
  apply (signature_eq_iff _ _).mp
  simpa only [p.bits_correct, q.bits_correct] using h

def pick (p q : Entry) : Entry := if p.size < q.size then p else q

theorem pick_origin (p q : Entry) : pick p q = p ∨ pick p q = q := by
  unfold pick
  split <;> simp

theorem pick_dominates_left (p q : Entry) (h : p.bits = q.bits) : Dominates (pick p q) p := by
  unfold pick
  split
  · exact dominates_refl p
  next hn =>
    exact ⟨equal_bits_equivalent q p h.symm, by omega⟩

theorem pick_dominates_right (p q : Entry) (h : p.bits = q.bits) : Dominates (pick p q) q := by
  unfold pick
  split
  next hn => exact ⟨equal_bits_equivalent p q h, Nat.le_of_lt hn⟩
  · exact dominates_refl q

/-- Insert by exact signature. Only the smaller representative can replace a match. -/
def insert (p : Entry) : List Entry → List Entry
  | [] => [p]
  | q :: qs => if p.bits = q.bits then pick p q :: qs else q :: insert p qs

theorem insert_origin (p : Entry) (xs : List Entry) (r : Entry) (h : r ∈ insert p xs) :
    r = p ∨ r ∈ xs := by
  induction xs with
  | nil => simp [insert] at h; exact Or.inl h
  | cons q qs ih =>
    by_cases he : p.bits = q.bits
    · simp only [insert, he, ↓reduceIte, List.mem_cons] at h
      rcases h with h | h
      · rcases pick_origin p q with hp | hp
        · exact Or.inl (h.trans hp)
        · exact Or.inr (List.mem_cons.mpr (Or.inl (h.trans hp)))
      · exact Or.inr (List.mem_cons_of_mem q h)
    · simp only [insert, he, ↓reduceIte, List.mem_cons] at h
      rcases h with h | h
      · exact Or.inr (List.mem_cons.mpr (Or.inl h))
      · rcases ih h with h | h
        · exact Or.inl h
        · exact Or.inr (List.mem_cons_of_mem q h)

theorem insert_covers_new (p : Entry) (xs : List Entry) :
    ∃ r ∈ insert p xs, Dominates r p := by
  induction xs with
  | nil => exact ⟨p, by simp [insert], dominates_refl p⟩
  | cons q qs ih =>
    by_cases he : p.bits = q.bits
    · exact ⟨pick p q, by simp [insert, he], pick_dominates_left p q he⟩
    · obtain ⟨r, hr, hd⟩ := ih
      exact ⟨r, by simp [insert, he, hr], hd⟩

theorem insert_covers_old (p : Entry) (xs : List Entry) (q : Entry) (hq : q ∈ xs) :
    ∃ r ∈ insert p xs, Dominates r q := by
  induction xs with
  | nil => simp at hq
  | cons a as ih =>
    by_cases he : p.bits = a.bits
    · rcases List.mem_cons.mp hq with hq | hq
      · subst q
        exact ⟨pick p a, by simp [insert, he], pick_dominates_right p a he⟩
      · exact ⟨q, by simp [insert, he, hq], dominates_refl q⟩
    · rcases List.mem_cons.mp hq with hq | hq
      · subst q
        exact ⟨a, by simp [insert, he], dominates_refl a⟩
      · obtain ⟨r, hr, hd⟩ := ih hq
        exact ⟨r, by simp [insert, he, hr], hd⟩

theorem insert_length (p : Entry) (xs : List Entry) :
    (insert p xs).length ≤ xs.length + 1 := by
  induction xs with
  | nil => simp [insert]
  | cons q qs ih =>
    by_cases he : p.bits = q.bits <;> simp [insert, he] <;> omega

/-- Tail-recursive construction; previously indexed representatives are retained. -/
def collect : List Program → List Entry → List Entry
  | [], acc => acc
  | p :: ps, acc => collect ps (insert (pack p) acc)

theorem collect_covers_old (ps : List Program) (acc : List Entry) (q : Entry) (hq : q ∈ acc) :
    ∃ r ∈ collect ps acc, Dominates r q := by
  induction ps generalizing acc q with
  | nil => exact ⟨q, hq, dominates_refl q⟩
  | cons p ps ih =>
    obtain ⟨r, hr, hd⟩ := insert_covers_old (pack p) acc q hq
    obtain ⟨s, hs, he⟩ := ih (insert (pack p) acc) r hr
    exact ⟨s, hs, dominates_trans he hd⟩

theorem collect_covers_new (ps : List Program) (acc : List Entry) (q : Program) (hq : q ∈ ps) :
    ∃ r ∈ collect ps acc, Dominates r (pack q) := by
  induction ps generalizing acc with
  | nil => simp at hq
  | cons p ps ih =>
    rcases List.mem_cons.mp hq with hq | hq
    · subst q
      obtain ⟨r, hr, hd⟩ := insert_covers_new (pack p) acc
      obtain ⟨s, hs, he⟩ := collect_covers_old ps (insert (pack p) acc) r hr
      exact ⟨s, hs, dominates_trans he hd⟩
    · exact ih (insert (pack p) acc) hq

theorem collect_origin (ps : List Program) (acc : List Entry) (q : Entry) (hq : q ∈ collect ps acc) :
    q ∈ acc ∨ q.code ∈ ps := by
  induction ps generalizing acc with
  | nil => exact Or.inl hq
  | cons p ps ih =>
    rcases ih (insert (pack p) acc) hq with h | h
    · rcases insert_origin (pack p) acc q h with h | h
      · subst q; exact Or.inr (List.mem_cons.mpr (Or.inl rfl))
      · exact Or.inl h
    · exact Or.inr (List.mem_cons_of_mem p h)

theorem collect_length (ps : List Program) (acc : List Entry) :
    (collect ps acc).length ≤ acc.length + ps.length := by
  induction ps generalizing acc with
  | nil => simp [collect]
  | cons p ps ih =>
    have h := ih (insert (pack p) acc)
    have hlen := insert_length (pack p) acc
    simp only [collect, List.length_cons]
    omega

def compact (ps : List Program) : List Entry := collect ps []
def codes (xs : List Entry) : List Program := xs.map Entry.code

theorem compact_origin (ps : List Program) (q : Entry) (hq : q ∈ compact ps) : q.code ∈ ps := by
  rcases collect_origin ps [] q hq with h | h
  · simp at h
  · exact h

theorem compact_covers (ps : List Program) (q : Program) (hq : q ∈ ps) :
    ∃ r ∈ codes (compact ps), Equivalent r q ∧ nodes r ≤ nodes q := by
  obtain ⟨r, hr, he, hn⟩ := collect_covers_new ps [] q hq
  refine ⟨r.code, List.mem_map.mpr ⟨r, hr, rfl⟩, he, ?_⟩
  simpa only [r.size_correct, pack] using hn

theorem compact_codes_origin (ps : List Program) (q : Program) (hq : q ∈ codes (compact ps)) :
    q ∈ ps := by
  obtain ⟨r, hr, he⟩ := List.mem_map.mp hq
  subst q
  exact compact_origin ps r hr

theorem compact_length (ps : List Program) : (compact ps).length ≤ ps.length := by
  simpa [compact] using collect_length ps []

/-- There is at most one retained entry per complete semantic signature. -/
def Unique (xs : List Entry) : Prop := (xs.map Entry.bits).Nodup

theorem pick_bits (p q : Entry) (h : p.bits = q.bits) : (pick p q).bits = q.bits := by
  unfold pick
  split
  · exact h
  · rfl

theorem insert_unique (p : Entry) (xs : List Entry) (h : Unique xs) : Unique (insert p xs) := by
  induction xs with
  | nil => simp [Unique, insert]
  | cons q qs ih =>
    have hparts : q.bits ∉ qs.map Entry.bits ∧ Unique qs := by
      simpa [Unique] using h
    by_cases he : p.bits = q.bits
    · simpa [Unique, insert, he, pick_bits p q he] using h
    · simp only [insert, he, ↓reduceIte, Unique, List.map_cons]
      apply List.nodup_cons.mpr
      constructor
      · intro hx
        obtain ⟨r,hr,hbits⟩ := List.mem_map.mp hx
        rcases insert_origin p qs r hr with hp | hr
        · subst r
          exact he hbits
        · exact hparts.1 (List.mem_map.mpr ⟨r,hr,hbits⟩)
      · exact ih hparts.2

theorem collect_unique (ps : List Program) (acc : List Entry) (h : Unique acc) :
    Unique (collect ps acc) := by
  induction ps generalizing acc with
  | nil => exact h
  | cons p ps ih => exact ih _ (insert_unique _ _ h)

theorem compact_unique (ps : List Program) : Unique (compact ps) :=
  collect_unique ps [] (by simp [Unique])

def bitVectors : Nat → List (List Bool)
  | 0 => [[]]
  | n+1 => (bitVectors n).map (false :: ·) ++ (bitVectors n).map (true :: ·)

theorem bitVectors_complete (bs : List Bool) : bs ∈ bitVectors bs.length := by
  induction bs with
  | nil => simp [bitVectors]
  | cons b bs ih =>
    cases b <;> simp [bitVectors, List.mem_map, ih]

theorem bitVectors_length (n : Nat) : (bitVectors n).length = 2^n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [bitVectors, ih, Nat.pow_succ, Nat.mul_two]

theorem unique_entries_at_most_256 (xs : List Entry) (h : Unique xs) : xs.length ≤ 256 := by
  have hsub : xs.map Entry.bits ⊆ bitVectors 8 := by
    intro bs hb
    obtain ⟨e,_,he⟩ := List.mem_map.mp hb
    subst bs
    have hl : e.bits.length = 8 := by simp [e.bits_correct, signature, inputs]
    have hm := bitVectors_complete e.bits
    simpa only [hl] using hm
  have hlen := List.Nodup.length_le_of_subset h hsub
  simpa only [List.length_map, bitVectors_length] using hlen

theorem compact_at_most_256 (ps : List Program) : (compact ps).length ≤ 256 :=
  unique_entries_at_most_256 _ (compact_unique ps)

end Komorebi.AVOC.SemanticSynthesis
