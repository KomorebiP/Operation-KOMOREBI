import Std

namespace Komorebi.AVOC.Synthesis

/-- Three precomputed decision flags. Computing the flags is outside the node meter. -/
structure Input where
  first : Bool
  second : Bool
  third : Bool
  deriving Repr, DecidableEq

inductive Variable where
  | first | second | third
  deriving Repr, DecidableEq

def Input.get (s : Input) : Variable → Bool
  | .first => s.first
  | .second => s.second
  | .third => s.third

/-- Finite pure program DATA; no imports, tactics or executable source are accepted. -/
inductive Program where
  | literal (value : Bool)
  | variable (index : Variable)
  | neg (child : Program)
  | conjunction (left right : Program)
  | disjunction (left right : Program)
  | exclusive (left right : Program)
  deriving Repr, DecidableEq

def run : Program → Input → Bool
  | .literal b, _ => b
  | .variable x, s => s.get x
  | .neg p, s => !(run p s)
  | .conjunction p q, s => run p s && run q s
  | .disjunction p q, s => run p s || run q s
  | .exclusive p q, s => xor (run p s) (run q s)

def nodes : Program → Nat
  | .literal _ | .variable _ => 1
  | .neg p => nodes p + 1
  | .conjunction p q | .disjunction p q | .exclusive p q => nodes p + nodes q + 1

/-- Instrumented eager AST evaluation. Visits are NOT wall time or short-circuit cost. -/
def runCount : Program → Input → Bool × Nat
  | .literal b, _ => (b, 1)
  | .variable x, s => (s.get x, 1)
  | .neg p, s => let r := runCount p s; (!r.1, r.2 + 1)
  | .conjunction p q, s =>
    let l := runCount p s; let r := runCount q s
    (l.1 && r.1, l.2 + r.2 + 1)
  | .disjunction p q, s =>
    let l := runCount p s; let r := runCount q s
    (l.1 || r.1, l.2 + r.2 + 1)
  | .exclusive p q, s =>
    let l := runCount p s; let r := runCount q s
    (xor l.1 r.1, l.2 + r.2 + 1)

theorem runCount_value (p : Program) (s : Input) : (runCount p s).1 = run p s := by
  induction p <;> simp_all [runCount, run]

theorem runCount_visits (p : Program) (s : Input) : (runCount p s).2 = nodes p := by
  induction p <;> simp_all [runCount, nodes]

theorem nodes_positive (p : Program) : 0 < nodes p := by cases p <;> simp [nodes]

def inputs : List Input :=
  [⟨false,false,false⟩, ⟨false,false,true⟩, ⟨false,true,false⟩, ⟨false,true,true⟩,
   ⟨true,false,false⟩, ⟨true,false,true⟩, ⟨true,true,false⟩, ⟨true,true,true⟩]

theorem input_complete (s : Input) : s ∈ inputs := by
  rcases s with ⟨a,b,c⟩
  cases a <;> cases b <;> cases c <;> decide

@[simp] theorem inputs_length : inputs.length = 8 := by rfl

def Equivalent (p q : Program) : Prop := ∀ s, run p s = run q s

def check (p q : Program) : Bool :=
  inputs.all (fun s => decide (run p s = run q s))

theorem check_sound (p q : Program) (h : check p q = true) : Equivalent p q := by
  intro s
  have hx := List.all_eq_true.mp h s (input_complete s)
  exact of_decide_eq_true hx

theorem check_complete (p q : Program) (h : Equivalent p q) : check p q = true := by
  apply List.all_eq_true.mpr
  intro s _
  exact decide_eq_true (h s)

theorem check_iff (p q : Program) : check p q = true ↔ Equivalent p q :=
  ⟨check_sound p q, check_complete p q⟩

theorem equivalent_refl (p : Program) : Equivalent p p := fun _ => rfl

theorem equivalent_trans {p q r : Program} (h : Equivalent p q) (k : Equivalent q r) :
    Equivalent p r := fun s => (h s).trans (k s)

@[simp] theorem check_self (p : Program) : check p p = true :=
  check_complete p p (equivalent_refl p)

theorem non_equivalent_rejected (p q : Program) (s : Input) (h : run p s ≠ run q s) :
    check p q = false := by
  cases hc : check p q with
  | false => rfl
  | true => exact False.elim (h (check_sound p q hc s))

/-- Grammar seeds do not contain a preselected complete replacement. -/
def atoms : List Program :=
  [.literal false, .literal true, .variable .first, .variable .second, .variable .third]

def pairs (op : Program → Program → Program) (xs ys : List Program) : List Program :=
  xs.flatMap (fun x => ys.map (op x))

theorem pairs_length (op : Program → Program → Program) (xs ys : List Program) :
    (pairs op xs ys).length = xs.length * ys.length := by
  induction xs with
  | nil => simp [pairs]
  | cons x xs ih => simp_all [pairs, Nat.add_mul, Nat.add_comm]

theorem mem_pairs (op : Program → Program → Program) (xs ys : List Program) (p : Program) :
    p ∈ pairs op xs ys ↔ ∃ x ∈ xs, ∃ y ∈ ys, op x y = p := by
  simp [pairs]

def expand (xs : List Program) : List Program :=
  xs ++ xs.map Program.neg ++ pairs .conjunction xs xs ++
    pairs .disjunction xs xs ++ pairs .exclusive xs xs

def programs : Nat → List Program
  | 0 => atoms
  | n + 1 => expand (programs n)

def poolSize : Nat → Nat
  | 0 => 5
  | n + 1 => 2 * poolSize n + 3 * poolSize n * poolSize n

/-- Conservative emitted-list-entry meter, including construction of earlier layers. -/
def generationCharge : Nat → Nat
  | 0 => 5
  | n + 1 => generationCharge n + poolSize (n + 1)

def nodeBound : Nat → Nat
  | 0 => 1
  | n + 1 => 2 * nodeBound n + 1

theorem expand_length (xs : List Program) :
    (expand xs).length = 2 * xs.length + 3 * xs.length * xs.length := by
  simp only [expand, List.length_append, List.length_map, pairs_length, Nat.mul_assoc]
  omega

theorem programs_length (n : Nat) : (programs n).length = poolSize n := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [programs, expand_length, ih, poolSize]

theorem pair_nodes_bound (op : Program → Program → Program)
    (hop : ∀ p q, nodes (op p q) ≤ nodes p + nodes q + 1)
    (xs : List Program) (b : Nat) (h : ∀ p ∈ xs, nodes p ≤ b)
    (p : Program) (hp : p ∈ pairs op xs xs) : nodes p ≤ 2*b+1 := by
  obtain ⟨x,hx,y,hy,he⟩ := (mem_pairs op xs xs p).mp hp
  subst p
  have ha := h x hx; have hb := h y hy; have hc := hop x y
  omega

theorem expand_nodes_bound (xs : List Program) (b : Nat)
    (h : ∀ p ∈ xs, nodes p ≤ b) (p : Program) (hp : p ∈ expand xs) :
    nodes p ≤ 2*b+1 := by
  simp only [expand, List.mem_append] at hp
  rcases hp with (((hp | hp) | hp) | hp) | hp
  · have := h p hp; omega
  · obtain ⟨q,hq,he⟩ := List.mem_map.mp hp
    subst p
    have := h q hq
    simp only [nodes]; omega
  · exact pair_nodes_bound .conjunction (fun _ _ => Nat.le_refl _) xs b h p hp
  · exact pair_nodes_bound .disjunction (fun _ _ => Nat.le_refl _) xs b h p hp
  · exact pair_nodes_bound .exclusive (fun _ _ => Nat.le_refl _) xs b h p hp

theorem programs_nodes_bound (n : Nat) (p : Program) (h : p ∈ programs n) :
    nodes p ≤ nodeBound n := by
  induction n generalizing p with
  | zero => simp [programs, atoms] at h; rcases h with h|h|h|h|h <;> subst p <;> decide
  | succ n ih => exact expand_nodes_bound _ _ (fun q hq => ih q hq) p h

def height : Program → Nat
  | .literal _ | .variable _ => 0
  | .neg p => height p + 1
  | .conjunction p q | .disjunction p q | .exclusive p q => max (height p) (height q) + 1

theorem programs_step_contains (n : Nat) (p : Program) (h : p ∈ programs n) :
    p ∈ programs (n+1) := by
  simp only [programs, expand, List.mem_append]
  exact Or.inl (Or.inl (Or.inl (Or.inl h)))

theorem programs_mono (m n : Nat) (h : m ≤ n) (p : Program) (hp : p ∈ programs m) :
    p ∈ programs n := by
  obtain ⟨k,rfl⟩ := Nat.exists_eq_add_of_le h
  clear h
  induction k with
  | zero => exact hp
  | succ k ih => exact programs_step_contains _ _ ih

theorem grammar_complete (p : Program) : p ∈ programs (height p) := by
  induction p with
  | literal b => cases b <;> simp [height, programs, atoms]
  | «variable» v => cases v <;> simp [height, programs, atoms]
  | neg p ih =>
    simp only [height, programs, expand, List.mem_append]
    exact Or.inl (Or.inl (Or.inl (Or.inr (List.mem_map.mpr ⟨p,ih,rfl⟩))))
  | conjunction p q ihp ihq =>
    have hp := programs_mono _ _ (Nat.le_max_left (height p) (height q)) p ihp
    have hq := programs_mono _ _ (Nat.le_max_right (height p) (height q)) q ihq
    simp only [height, programs, expand, List.mem_append]
    exact Or.inl (Or.inl (Or.inr ((mem_pairs _ _ _ _).mpr ⟨p,hp,q,hq,rfl⟩)))
  | disjunction p q ihp ihq =>
    have hp := programs_mono _ _ (Nat.le_max_left (height p) (height q)) p ihp
    have hq := programs_mono _ _ (Nat.le_max_right (height p) (height q)) q ihq
    simp only [height, programs, expand, List.mem_append]
    exact Or.inl (Or.inr ((mem_pairs _ _ _ _).mpr ⟨p,hp,q,hq,rfl⟩))
  | exclusive p q ihp ihq =>
    have hp := programs_mono _ _ (Nat.le_max_left (height p) (height q)) p ihp
    have hq := programs_mono _ _ (Nat.le_max_right (height p) (height q)) q ihq
    simp only [height, programs, expand, List.mem_append]
    exact Or.inr ((mem_pairs _ _ _ _).mpr ⟨p,hp,q,hq,rfl⟩)

theorem bounded_grammar_complete (d : Nat) (p : Program) (h : height p ≤ d) :
    p ∈ programs d := programs_mono _ _ h p (grammar_complete p)

end Komorebi.AVOC.Synthesis
