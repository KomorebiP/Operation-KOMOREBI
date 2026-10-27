import RepresentationCore

namespace Komorebi.Representation
universe u v w z
variable {X Y Z : Type u} {A : Type v} {O : Type w} {V : Type z}

def Horizon (S : System X A O V) : Nat → X → X → Prop
  | 0, x, y => ∀ j, S.observe j x = S.observe j y
  | n+1, x, y => (∀ j, S.observe j x = S.observe j y) ∧
      ∀ a, Horizon S n (S.step a x) (S.step a y)

theorem obsEq_horizon (S : System X A O V) {x y : X} (h : ObsEq S x y)
    (n : Nat) : Horizon S n x y := by
  induction n generalizing x y with
  | zero => exact h []
  | succ n ih => exact ⟨h [], fun a => ih (obsEq_step S h a)⟩

theorem horizon_observe (S : System X A O V) (n : Nat) {x y : X}
    (h : Horizon S n x y) : ∀ j, S.observe j x = S.observe j y := by
  cases n with
  | zero => exact h
  | succ n => exact h.1

theorem stable_horizon_exact (S : System X A O V) (n : Nat)
    (stable : ∀ x y, Horizon S n x y → Horizon S (n+1) x y) (x y : X) :
    Horizon S n x y ↔ ObsEq S x y := by
  constructor
  · intro h
    apply invariant_relation_sound S (Horizon S n)
    · intro a b hab; exact horizon_observe S n hab
    · intro a b hab c; exact (stable a b hab).2 c
    · exact h
  · intro h; exact obsEq_horizon S h n

theorem horizon_counterexample (S : System X A O V) (n : Nat) (x y : X)
    (h : ¬ Horizon S n x y) :
    ∃ w : List A, w.length ≤ n ∧ ∃ j, behavior S x w j ≠ behavior S y w j := by
  classical
  induction n generalizing x y with
  | zero =>
    have hh : ∃ j, S.observe j x ≠ S.observe j y := by
      apply Classical.byContradiction
      intro hnone
      apply h
      intro j
      apply Classical.byContradiction
      intro hj
      exact hnone ⟨j,hj⟩
    obtain ⟨j,hj⟩ := hh
    exact ⟨[], Nat.le_refl 0, j, hj⟩
  | succ n ih =>
    by_cases ho : ∀ j, S.observe j x = S.observe j y
    · have ha : ∃ a, ¬ Horizon S n (S.step a x) (S.step a y) := by
        apply Classical.byContradiction
        intro hnone
        apply h
        refine ⟨ho, ?_⟩
        intro a
        apply Classical.byContradiction
        intro hh
        exact hnone ⟨a,hh⟩
      obtain ⟨a,ha⟩ := ha
      obtain ⟨w,hw,j,hj⟩ := ih (S.step a x) (S.step a y) ha
      exact ⟨a::w,Nat.succ_le_succ hw,j,hj⟩
    · have hh : ∃ j, S.observe j x ≠ S.observe j y := by
        apply Classical.byContradiction
        intro hnone
        apply ho
        intro j
        apply Classical.byContradiction
        intro hj
        exact hnone ⟨j,hj⟩
      obtain ⟨j,hj⟩ := hh
      exact ⟨[], Nat.zero_le _, j, hj⟩

def testEncoding {I : Type u} (S : System X A O V)
    (tests : I → List A × O) (x : X) : I → V :=
  fun i => behavior S x (tests i).1 (tests i).2

theorem sufficient_tests_exact {I : Type u} (S : System X A O V)
    (tests : I → List A × O)
    (hout : ∀ x y, testEncoding S tests x = testEncoding S tests y →
      ∀ j, S.observe j x = S.observe j y)
    (hstep : ∀ x y, testEncoding S tests x = testEncoding S tests y →
      ∀ a, testEncoding S tests (S.step a x) = testEncoding S tests (S.step a y))
    (x y : X) : testEncoding S tests x = testEncoding S tests y ↔ ObsEq S x y := by
  constructor
  · intro h; exact invariant_relation_sound S (fun x y => testEncoding S tests x = testEncoding S tests y) hout hstep h
  · intro h; funext i; exact h (tests i).1 (tests i).2

noncomputable def competingEncoding {S : System X A O V} {T : System Y A O V}
    {U : System Z A O V} (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (v : Transport S U) (y : Y) : Z := v.encode (Classical.choose (hs y))

theorem minimal_encoding_injective {S : System X A O V} {T : System Y A O V}
    {U : System Z A O V} (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (hsep : ∀ y z, y ≠ z → ∃ w j, behavior T y w j ≠ behavior T z w j)
    (v : Transport S U) :
    ∀ y z, competingEncoding q hs v y = competingEncoding q hs v z → y = z := by
  intro y z heq
  have h : ObsEq S (Classical.choose (hs y)) (Classical.choose (hs z)) :=
    transport_kernel_sound v heq
  have hq := (separated_encoding_exact q hsep _ _).mp h
  rw [Classical.choose_spec (hs y), Classical.choose_spec (hs z)] at hq
  exact hq


-- The minimality lower bound also covers encoders that only preserve ALL-WORD
-- semantics, without requiring them to intertwine internal target states.
noncomputable def semanticEmbedding {S : System X A O V} {T : System Y A O V}
    (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (v : X → Z) (y : Y) : Z := v (Classical.choose (hs y))

theorem minimal_word_encoding_injective {S : System X A O V} {T : System Y A O V}
    {U : System Z A O V} (q : Transport S T) (hs : ∀ y, ∃ x, q.encode x = y)
    (hsep : ∀ y z, y ≠ z → ∃ w j, behavior T y w j ≠ behavior T z w j)
    (v : X → Z) (hv : ∀ x w j, behavior S x w j = behavior U (v x) w j) :
    ∀ y z, semanticEmbedding q hs v y = semanticEmbedding q hs v z → y = z := by
  intro y z heq
  change v (Classical.choose (hs y)) = v (Classical.choose (hs z)) at heq
  have h : ObsEq S (Classical.choose (hs y)) (Classical.choose (hs z)) := by
    intro w j
    rw [hv, hv, heq]
  have hq := (separated_encoding_exact q hsep _ _).mp h
  rw [Classical.choose_spec (hs y), Classical.choose_spec (hs z)] at hq
  exact hq

-- Executable finite LOCAL checker and its generic all-word soundness theorem.
-- There are no native_decide calls; concrete uses below are kernel-reduced.
def checkLocal {n t k o v : Nat}
    (S : System (Fin n) (Fin k) (Fin o) (Fin v))
    (T : System (Fin t) (Fin k) (Fin o) (Fin v)) (q : Fin n → Fin t) : Bool :=
  decide ((∀ a x, q (S.step a x) = T.step a (q x)) ∧
          (∀ j x, S.observe j x = T.observe j (q x)))

def checkedTransport {n t k o v : Nat}
    (S : System (Fin n) (Fin k) (Fin o) (Fin v))
    (T : System (Fin t) (Fin k) (Fin o) (Fin v)) (q : Fin n → Fin t)
    (h : checkLocal S T q = true) : Transport S T where
  encode := q
  step_ok := (of_decide_eq_true h).1
  observe_ok := (of_decide_eq_true h).2

theorem checked_transport_all_words {n t k o v : Nat}
    (S : System (Fin n) (Fin k) (Fin o) (Fin v))
    (T : System (Fin t) (Fin k) (Fin o) (Fin v)) (q : Fin n → Fin t)
    (h : checkLocal S T q = true) (x : Fin n) (w : List (Fin k)) (j : Fin o) :
    behavior S x w j = behavior T (q x) w j :=
  transport_behavior (checkedTransport S T q h) w j x

end Komorebi.Representation
