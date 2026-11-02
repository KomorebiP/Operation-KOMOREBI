import GraphTraversalSolver

/-!
Tabulated finite path construction. Round k stores actual walks for every
pair joined by a walk of length at most k. Every reachable pair on Fin n
admits a simple walk within n rounds. No vertex labelings are enumerated.
-/

namespace KRS.Graph

universe u v

structure FiniteCache (n : Nat) (F : Fin n → Type u) where
  values : Array ((i : Fin n) × F i)
  size_eq : values.size = n
  index_eq : ∀ i : Fin n, (values[i.val]'(by rw [size_eq]; exact i.isLt)).1 = i

def cacheOfFn {n : Nat} {F : Fin n → Type u} (f : (i : Fin n) → F i) : FiniteCache n F where
  values := Array.ofFn (fun i => ⟨i, f i⟩)
  size_eq := Array.size_ofFn
  index_eq := by intro i; simp

def cacheGet {n : Nat} {F : Fin n → Type u} (values : FiniteCache n F) (i : Fin n) : F i :=
  (values.index_eq i) ▸ (values.values[i.val]'(by rw [values.size_eq]; exact i.isLt)).2

theorem transport_cache_entry {I : Type v} {F : I → Type u} (f : (i : I) → F i)
    (i : I) (entry : (j : I) × F j) (h : entry.1 = i) (he : entry = ⟨i, f i⟩) :
    h ▸ entry.2 = f i := by
  subst entry
  rfl

theorem cache_get_of_fn {n : Nat} {F : Fin n → Type u} (f : (i : Fin n) → F i) (i : Fin n) :
    cacheGet (cacheOfFn f) i = f i := by
  unfold cacheGet
  apply transport_cache_entry f i
  change (Array.ofFn (fun j : Fin n => (⟨j, f j⟩ : Sigma F)))[i.val]'(by
    simpa only [Array.size_ofFn] using i.isLt) = (⟨i, f i⟩ : Sigma F)
  rw [Array.getElem_ofFn]

def findFirstSome {A : Type u} {B : Type v} : List A → (A → Option B) → Option B
  | [], _ => none
  | a :: tail, f => match f a with
      | some b => some b
      | none => findFirstSome tail f

theorem find_first_some_is_some {A : Type u} {B : Type v} (l : List A) (f : A → Option B) :
    (findFirstSome l f).isSome = true ↔ ∃ a, a ∈ l ∧ (f a).isSome = true := by
  induction l with
  | nil => simp [findFirstSome]
  | cons a tail ih =>
    cases ha : f a with
    | none =>
      simp only [findFirstSome, ha]
      rw [ih]
      constructor
      · rintro ⟨x, hx, hf⟩
        exact ⟨x, List.mem_cons_of_mem a hx, hf⟩
      · rintro ⟨x, hx, hf⟩
        rcases List.mem_cons.mp hx with h | h
        · subst x; simp [ha] at hf
        · exact ⟨x, h, hf⟩
    | some b =>
      constructor
      · intro _; exact ⟨a, by simp, by simp [ha]⟩
      · intro _; simp [findFirstSome, ha]

def finiteVertices (n : Nat) : List (Fin n) := List.ofFn id

theorem mem_finite_vertices {n : Nat} (v : Fin n) : v ∈ finiteVertices n :=
  List.mem_ofFn.mpr ⟨v, rfl⟩

abbrev PathTable {n : Nat} (G : SimpleGraph (Fin n)) :=
  FiniteCache n (fun v => FiniteCache n (fun w => Option (Walk G v w)))

def pathAt {n : Nat} {G : SimpleGraph (Fin n)} (P : PathTable G) (v w : Fin n) :
    Option (Walk G v w) := cacheGet (cacheGet P v) w

def tabulatePaths {n : Nat} {G : SimpleGraph (Fin n)}
    (f : (v w : Fin n) → Option (Walk G v w)) : PathTable G :=
  cacheOfFn (fun v => cacheOfFn (fun w => f v w))

theorem path_at_tabulate {n : Nat} {G : SimpleGraph (Fin n)}
    (f : (v w : Fin n) → Option (Walk G v w)) (v w : Fin n) :
    pathAt (tabulatePaths f) v w = f v w := by
  simp [pathAt, tabulatePaths, cache_get_of_fn]

def emptyPath {n : Nat} (G : SimpleGraph (Fin n)) (v w : Fin n) : Option (Walk G v w) :=
  if h : v = w then by subst w; exact some (.nil v) else none

def extendPaths {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (P : PathTable G) (v w : Fin n) : Option (Walk G v w) :=
  match pathAt P v w with
  | some p => some p
  | none => findFirstSome (finiteVertices n) (fun u =>
      if h : G.Adj v u then (pathAt P u w).map (fun p => .cons h p) else none)

theorem extend_paths_keeps {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (P : PathTable G) (v w : Fin n) (h : (pathAt P v w).isSome = true) :
    (extendPaths G P v w).isSome = true := by
  cases hp : pathAt P v w with
  | none => simp [hp] at h
  | some p => simp [extendPaths, hp]

theorem extend_paths_cons {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (P : PathTable G) (v u w : Fin n) (h : G.Adj v u)
    (hp : (pathAt P u w).isSome = true) : (extendPaths G P v w).isSome = true := by
  unfold extendPaths
  cases old : pathAt P v w with
  | some p => rfl
  | none =>
    apply (find_first_some_is_some _ _).mpr
    refine ⟨u, mem_finite_vertices u, ?_⟩
    cases hs : pathAt P u w with
    | none => simp [hs] at hp
    | some p => simp [h]

def boundedPaths {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : Nat → PathTable G
  | 0 => tabulatePaths (emptyPath G)
  | k + 1 =>
      let previous := boundedPaths G k
      tabulatePaths (extendPaths G previous)

theorem bounded_paths_complete {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (k : Nat) {v w : Fin n} (p : Walk G v w) (h : p.length ≤ k) :
    (pathAt (boundedPaths G k) v w).isSome = true := by
  induction k generalizing v w with
  | zero =>
    cases p with
    | nil => simp [boundedPaths, path_at_tabulate, emptyPath]
    | cons edge tail => simp [Walk.length] at h
  | succ k ih =>
    simp only [boundedPaths, path_at_tabulate]
    cases p with
    | nil v =>
      exact extend_paths_keeps G _ v v (ih (.nil v) (by simp [Walk.length]))
    | @cons v u w edge tail =>
      apply extend_paths_cons G _ v u w edge
      exact ih tail (by simpa [Walk.length] using h)

theorem nodup_length_le_of_mem {A : Type u} [BEq A] [LawfulBEq A]
    (l s : List A) (hl : l.Nodup) (hs : ∀ a, a ∈ l → a ∈ s) : l.length ≤ s.length := by
  induction l generalizing s with
  | nil => simp
  | cons a tail ih =>
    obtain ⟨hna, hnt⟩ := List.nodup_cons.mp hl
    have ha : a ∈ s := hs a (by simp)
    have htail : ∀ x, x ∈ tail → x ∈ s.erase a := by
      intro x hx
      have hne : x ≠ a := by intro heq; subst x; exact hna hx
      exact (List.mem_erase_of_ne hne).mpr (hs x (List.mem_cons_of_mem a hx))
    have hi := ih (s.erase a) hnt htail
    have hp : 0 < s.length := by
      cases s with
      | nil => simp at ha
      | cons => simp
    rw [List.length_erase_of_mem ha] at hi
    simp only [List.length_cons]
    omega

theorem Walk.vertices_length {V : Type u} {G : SimpleGraph V} {v w : V} (p : Walk G v w) :
    p.vertices.length = p.length + 1 := by
  induction p with
  | nil => rfl
  | cons edge tail ih => simp [Walk.vertices_cons, Walk.length, ih, Nat.add_assoc]

theorem Walk.zero_integral {V : Type u} {G : SimpleGraph V} {v w : V} (p : Walk G v w) :
    p.integral (fun _ _ => false) = false := by
  induction p with
  | nil => rfl
  | cons edge tail ih => simpa [Walk.integral] using ih

theorem bounded_paths_reachable {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (v w : Fin n) : (pathAt (boundedPaths G n) v w).isSome = true ↔ Reachable G v w := by
  constructor
  · intro h
    exact ⟨(pathAt (boundedPaths G n) v w).get h⟩
  · rintro ⟨p⟩
    obtain ⟨q, hq, _⟩ := p.simple_representative (fun _ _ => false)
      (by intro _ _ _; rfl) (by intro _ walk _ _; exact walk.zero_integral)
    have hv := nodup_length_le_of_mem q.vertices (finiteVertices n) hq
      (fun v _ => mem_finite_vertices v)
    simp only [finiteVertices, List.length_ofFn, Walk.vertices_length] at hv
    exact bounded_paths_complete G n q (by omega)

end KRS.Graph
