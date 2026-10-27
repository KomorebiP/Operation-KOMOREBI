import RealizationBoundaries.SelectorClassification
import RealizationBoundaries.PrimeComputability
import RealizationBoundaries.SubgroupSpectrum
import Mathlib.Computability.TuringDegree

/-!
# Genuine oracle computations and paired positive search

Oracle computability below is Mathlib's closure of the partial recursive
functions under an actual oracle call, primitive recursion and minimization.
A classical definition is never accepted as a computation without a proof in
that inductive semantics.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section

namespace RealizationBoundaries

/-- The total, zero/one membership oracle for a binary selector. -/
def selectorOracle (a : ℕ → Bool) : ℕ →. ℕ :=
  fun n => Part.some (if a n then 1 else 0)

/-- Relative total computability, using the native oracle-recursion semantics. -/
def OracleComputable (X : ℕ → Bool) (f : ℕ → ℕ) : Prop :=
  Nat.RecursiveIn {selectorOracle X} (fun n => Part.some (f n))

/-- Selector reducibility is the actual Mathlib Turing reducibility relation. -/
def SelectorReducible (a X : ℕ → Bool) : Prop :=
  TuringReducible (selectorOracle a) (selectorOracle X)

namespace OracleComputable

variable {X : ℕ → Bool} {f g : ℕ → ℕ}

theorem of_computable (hf : Computable f) : OracleComputable X f := by
  exact RecursiveIn.iff_nat.mp hf.computableIn

/-- Substitution of one genuine oracle reduction into another. -/
theorem change_oracle {a : ℕ → Bool} (hf : OracleComputable a f)
    (ha : SelectorReducible a X) : OracleComputable X f := by
  apply hf.subst
  intro g hg
  have he : g = selectorOracle a := Set.mem_singleton_iff.mp hg
  rw [he]
  exact RecursiveIn.iff_nat.mp ha

theorem of_eq (hf : OracleComputable X f) (h : ∀ n, f n = g n) :
    OracleComputable X g :=
  Nat.RecursiveIn.of_eq hf (fun n => congrArg Part.some (h n))

theorem comp (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => f (g n)) := by
  apply (Nat.RecursiveIn.comp hf hg).of_eq
  intro n
  simp

theorem pair (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => Nat.pair (f n) (g n)) := by
  apply (Nat.RecursiveIn.pair hf hg).of_eq
  intro n
  apply Part.eq_some_iff.mpr
  exact ⟨⟨trivial, trivial⟩, rfl⟩

theorem id : OracleComputable X id := of_computable Computable.id

theorem const (k : ℕ) : OracleComputable X (fun _ => k) :=
  of_computable (Computable.const k)

theorem oracle : OracleComputable X (fun n => if X n then 1 else 0) :=
  Nat.RecursiveIn.oracle (selectorOracle X) (by simp)

/-- Total primitive recursion with a coded parameter. -/
theorem prec {initial : ℕ → ℕ} {step : ℕ → ℕ → ℕ → ℕ}
    (hf : OracleComputable X initial)
    (hg : OracleComputable X
      (fun k => step k.unpair.1 k.unpair.2.unpair.1 k.unpair.2.unpair.2)) :
    OracleComputable X (fun k =>
      Nat.rec (initial k.unpair.1) (fun n r => step k.unpair.1 n r) k.unpair.2) := by
  apply (Nat.RecursiveIn.prec hf hg).of_eq
  intro k
  dsimp
  induction k.unpair.2 with
  | zero => rfl
  | succ n ih =>
    simp only [Nat.unpair_pair] at ih ⊢
    rw [ih]
    simp

/-- Total minimization is justified by an explicit termination witness at every input. -/
theorem find (hf : OracleComputable X f)
    (h : ∀ n, ∃ t, f (Nat.pair n t) = 0) :
    OracleComputable X (fun n => Nat.find (h n)) := by
  apply (Nat.RecursiveIn.rfind hf).of_eq_tot
  intro n
  apply Nat.mem_rfind.mpr
  constructor
  · simp [Nat.find_spec (h n)]
  · intro m hm
    have hn : f (Nat.pair n m) ≠ 0 := Nat.find_min (h n) hm
    simp [hn]

/-- Finite searches can recover a total output only after a witness is found.
Both the stopping test and output reader must themselves be oracle computable. -/
theorem search_output (hf : OracleComputable X f) (hg : OracleComputable X g)
    (h : ∀ n, ∃ t, f (Nat.pair n t) = 0) :
    OracleComputable X (fun n => g (Nat.pair n (Nat.find (h n)))) :=
  hg.comp (id.pair (find hf h))

theorem left : OracleComputable X (fun n => n.unpair.1) :=
  Nat.Primrec.left.recursiveIn

theorem right : OracleComputable X (fun n => n.unpair.2) :=
  Nat.Primrec.right.recursiveIn

theorem mul (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => f n * g n) :=
  (Nat.Primrec.mul.recursiveIn : OracleComputable X (Nat.unpaired (· * ·))).comp
    (hf.pair hg) |>.of_eq (fun n => by simp [Nat.unpaired])

theorem isZero (hf : OracleComputable X f) :
    OracleComputable X (fun n => if f n = 0 then 1 else 0) := by
  have hz : OracleComputable X (fun n : ℕ => if n = 0 then 1 else 0) :=
    (Nat.Primrec.casesOn1 1 Nat.Primrec.zero).recursiveIn |>.of_eq
      (fun n => by cases n <;> simp)
  exact hz.comp hf

/-- Relative selection uses a primitive recursive comparison of the original input. -/
theorem ite_lt (N : ℕ) (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => if n < N then f n else g n) := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have hp : Computable (fun k : ℕ =>
      if k.unpair.1 < N then k.unpair.2.unpair.1 else k.unpair.2.unpair.2) :=
    (Primrec.ite (Primrec.nat_lt.comp hl (Primrec.const N))
      (hl.comp hr) (hr.comp hr)).to_comp
  exact (of_computable hp).comp (id.pair (hf.pair hg)) |>.of_eq
    (fun n => by simp)

end OracleComputable

/-- A finite table is ordinary computable even when its fixed entries were
selected nonuniformly from a noncomputable set. -/
def finiteSelectorTable (a : ℕ → Bool) (N n : ℕ) : ℕ :=
  if a (n % (N+1)) then 1 else 0

theorem computable_finiteSelectorTable (a : ℕ → Bool) (N : ℕ) :
    Computable (finiteSelectorTable a N) := by
  let z : ℕ → Fin (N+1) := fun n => ⟨n % (N+1), Nat.mod_lt _ (Nat.succ_pos _)⟩
  have hz : Primrec z := Primrec.fin_val_iff.mp
    (Primrec.nat_mod.comp Primrec.id (Primrec.const (N+1)))
  exact ((Primrec.dom_finite (fun i : Fin (N+1) => if a i.val then 1 else 0)).comp hz).to_comp

/-- Hard-coding a finite prefix is a proved Turing reduction, not a uniform
procedure for discovering the prefix or its cutoff. -/
theorem selector_reduces_of_tail (a X : ℕ → Bool) (N : ℕ)
    (h : SelectorReducible (fun n => a (n+N)) X) : SelectorReducible a X := by
  have hb : OracleComputable X (fun n => if a (n+N) then 1 else 0) :=
    RecursiveIn.iff_nat.mp h
  have ht := hb.comp (OracleComputable.of_computable
    (Primrec.nat_sub.comp Primrec.id (Primrec.const N)).to_comp)
  have hp := OracleComputable.of_computable (X := X) (computable_finiteSelectorTable a N)
  apply RecursiveIn.iff_nat.mpr
  apply (hp.ite_lt N ht).of_eq
  intro n
  by_cases hn : n < N
  · simp [hn, finiteSelectorTable, Nat.mod_eq_of_lt (lt_trans hn (Nat.lt_succ_self N))]
  · simp [hn, Nat.sub_add_cancel (le_of_not_gt hn)]

/-- A pair of complementary positive searches. The test is zero at a successful
stage and `answer` then gives the selector bit. This interface records an
actual recursive procedure and an explicit proof that it terminates. -/
structure ComplementarySearch (a X : ℕ → Bool) where
  test : ℕ → ℕ
  answer : ℕ → ℕ
  test_computable : OracleComputable X test
  answer_computable : OracleComputable X answer
  terminates : ∀ n, ∃ t, test (Nat.pair n t) = 0
  correct : ∀ n t, test (Nat.pair n t) = 0 →
    answer (Nat.pair n t) = if a n then 1 else 0

/-- Two complementary positive searches give a genuine Turing reduction. -/
theorem complementarySearch_reduces (a X : ℕ → Bool)
    (s : ComplementarySearch a X) : SelectorReducible a X := by
  apply RecursiveIn.iff_nat.mpr
  have h := OracleComputable.search_output s.test_computable s.answer_computable s.terminates
  exact h.of_eq (fun n => s.correct n _ (Nat.find_spec (s.terminates n)))

/-- An oracle-computable group copy on the coded domain ℕ. Addition and equality
are computational; the isomorphism names the mathematical structure and is not
required to be computable. -/
structure OracleGroupCopy (X : ℕ → Bool) (H : Type*) [AddGroup H] where
  names : ℕ ≃ H
  zero : ℕ
  add : ℕ → ℕ → ℕ
  zero_spec : names zero = 0
  add_spec : ∀ i j, names (add i j) = names i + names j
  add_computable : OracleComputable X (fun k => add k.unpair.1 k.unpair.2)

/-- Repeated addition on the actual coded domain. -/
def OracleGroupCopy.multiple {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) (m y : ℕ) : ℕ :=
  Nat.rec c.zero (fun _ z => c.add y z) m

@[simp] theorem OracleGroupCopy.multiple_spec {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) (m y : ℕ) : c.names (c.multiple m y) = m • c.names y := by
  induction m with
  | zero => simpa [OracleGroupCopy.multiple] using c.zero_spec
  | succ m ih =>
    change c.names (c.add y (c.multiple m y)) = (m+1) • c.names y
    rw [c.add_spec, ih, succ_nsmul']

/-- Multiplication by an arbitrary coded natural is obtained by native primitive
recursion from the copy's addition algorithm. -/
theorem OracleGroupCopy.multiple_computable {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) :
    OracleComputable X (fun k => c.multiple k.unpair.2 k.unpair.1) := by
  have step : OracleComputable X
      (fun k => c.add k.unpair.1 k.unpair.2.unpair.2) := by
    exact c.add_computable.comp (OracleComputable.left.pair
      (OracleComputable.right.comp OracleComputable.right)) |>.of_eq
        (fun n => by simp)
  apply (Nat.RecursiveIn.prec (OracleComputable.const c.zero) step).of_eq
  intro n
  dsimp
  induction n.unpair.2 with
  | zero => rfl
  | succ m ih =>
    simp only [Nat.unpair_pair] at ih ⊢
    rw [ih]
    simp [OracleGroupCopy.multiple]

/-- A decidable test for each candidate of each prime-root search in a coded copy.
The supplied bijection names every actual group element. Only finite candidate
tests are assumed computable; root existence is not assumed decidable. -/
structure RootSearchPresentation (X : ℕ → Bool) (H : Type*) [AddGroup H] where
  names : ℕ ≃ H
  target : H
  offset : ℕ
  test : ℕ → ℕ
  test_computable : OracleComputable X test
  test_correct : ∀ n side t, test (Nat.pair n (Nat.pair side t)) = 0 ↔
    (primeAt (2*(n+offset)+side)).val • names t = target

/-- The actual prime index used by a coded pair-search input. -/
def pairedSearchIndex (offset k : ℕ) : ℕ :=
  2*(k.unpair.1+offset)+k.unpair.2.unpair.1

theorem computable_pairedSearchIndex (offset : ℕ) : Computable (pairedSearchIndex offset) := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  exact (Primrec.nat_add.comp
    (Primrec.nat_mul.comp (Primrec.const 2) (Primrec.nat_add.comp hl (Primrec.const offset)))
    (hl.comp hr)).to_comp

/-- Actual oracle-computable addition yields each decidable candidate root test.
The prime computation is the proved computation of the production `primeAt`,
not an extra oracle. -/
def OracleGroupCopy.rootSearch {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) (h offset : ℕ) : RootSearchPresentation X H where
  names := c.names
  target := c.names h
  offset := offset
  test := fun k => if c.multiple (primeAt (pairedSearchIndex offset k)).val
      k.unpair.2.unpair.2 = h then 0 else 1
  test_computable := by
    have hm : OracleComputable X (fun k =>
        c.multiple (primeAt (pairedSearchIndex offset k)).val k.unpair.2.unpair.2) := by
      exact c.multiple_computable.comp
        ((OracleComputable.right.comp OracleComputable.right).pair
          (OracleComputable.of_computable
            (computable_primeAt_value.comp (computable_pairedSearchIndex offset)))) |>.of_eq
              (fun k => by simp)
    have ht : Computable (fun m : ℕ => if m = h then 0 else 1) :=
      (Primrec.ite (Primrec.eq.comp Primrec.id (Primrec.const h))
        (Primrec.const 0) (Primrec.const 1)).to_comp
    exact (OracleComputable.of_computable ht).comp hm
  test_correct := by
    intro n side t
    simp only [pairedSearchIndex, Nat.unpair_pair]
    rw [ite_eq_left_iff]
    constructor
    · intro hc
      have he : c.multiple (primeAt (2*(n+offset)+side)).val t = h := by
        by_contra hn
        exact Nat.one_ne_zero (hc hn)
      simpa only [← c.multiple_spec] using congrArg c.names he
    · intro he
      have hc := c.names.injective ((c.multiple_spec _ _).trans he)
      simp [hc]

/-- Candidate zero for the first prime of a pair. -/
def RootSearchPresentation.evenTest {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : RootSearchPresentation X H) (k : ℕ) : ℕ :=
  c.test (Nat.pair k.unpair.1 (Nat.pair 0 k.unpair.2))

/-- Candidate zero for the second prime of a pair. -/
def RootSearchPresentation.oddTest {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : RootSearchPresentation X H) (k : ℕ) : ℕ :=
  c.test (Nat.pair k.unpair.1 (Nat.pair 1 k.unpair.2))

theorem RootSearchPresentation.evenTest_computable {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : RootSearchPresentation X H) : OracleComputable X c.evenTest :=
  c.test_computable.comp (OracleComputable.left.pair
    ((OracleComputable.const 0).pair OracleComputable.right))

theorem RootSearchPresentation.oddTest_computable {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : RootSearchPresentation X H) : OracleComputable X c.oddTest :=
  c.test_computable.comp (OracleComputable.left.pair
    ((OracleComputable.const 1).pair OracleComputable.right))

/-- Dovetailing two positive root searches terminates when they carry complementary
bits. This produces native Turing reducibility from the actual root tests. -/
theorem paired_root_search_reduces (a X : ℕ → Bool) {H : Type*} [AddGroup H]
    (c : RootSearchPresentation X H)
    (he : ∀ n, (HasPrimeRoot c.target (primeAt (2*(n+c.offset))) ↔ a n = true))
    (ho : ∀ n, (HasPrimeRoot c.target (primeAt (2*(n+c.offset)+1)) ↔ a n = false)) :
    SelectorReducible a X := by
  apply complementarySearch_reduces a X
  refine {
    test := fun k => c.evenTest k * c.oddTest k
    answer := fun k => if c.evenTest k = 0 then 1 else 0
    test_computable := c.evenTest_computable.mul c.oddTest_computable
    answer_computable := c.evenTest_computable.isZero
    terminates := ?_
    correct := ?_ }
  · intro n
    cases ha : a n
    · obtain ⟨y, hy⟩ := (ho n).mpr ha
      refine ⟨c.names.symm y, ?_⟩
      have ht := (c.test_correct n 1 (c.names.symm y)).mpr (by simpa using hy)
      simp [RootSearchPresentation.oddTest, ht]
    · obtain ⟨y, hy⟩ := (he n).mpr ha
      refine ⟨c.names.symm y, ?_⟩
      have ht := (c.test_correct n 0 (c.names.symm y)).mpr (by simpa using hy)
      simp [RootSearchPresentation.evenTest, ht]
  · intro n t ht
    have hleft : c.evenTest (Nat.pair n t) = 0 ↔ a n = true := by
      constructor
      · intro h
        exact (he n).mp ⟨c.names t, (c.test_correct n 0 t).mp
          (by simpa [RootSearchPresentation.evenTest] using h)⟩
      · intro ha
        by_contra hn
        have hr : c.oddTest (Nat.pair n t) = 0 := (mul_eq_zero.mp ht).resolve_left hn
        have hab := (ho n).mp ⟨c.names t, (c.test_correct n 1 t).mp
          (by simpa [RootSearchPresentation.oddTest] using hr)⟩
        simp [ha] at hab
    cases ha : a n <;> simp_all

theorem marked_even_root_iff (a : ℕ → Bool) (n : ℕ) :
    @HasPrimeRoot (pairedGroup a) _ (markedElement (pairedSelector a))
      (primeAt (2*n)) ↔ a n = true := by
  cases ha : a n
  · simp only [Bool.false_eq_true, iff_false]
    change ¬ ∃ y : pairedGroup a, (primeAt (2*n)).val • y = markedElement (pairedSelector a)
    have h := chosen_prime_obstructs a n
    simpa only [chosenIndex, ha, Bool.false_eq_true, ↓reduceIte, add_zero] using h
  · simp only [iff_true]
    change ∃ y : pairedGroup a, (primeAt (2*n)).val • y = markedElement (pairedSelector a)
    have h := omitted_prime_has_root a n
    simpa only [omittedIndex, ha, ↓reduceIte, add_zero] using h

theorem marked_odd_root_iff (a : ℕ → Bool) (n : ℕ) :
    @HasPrimeRoot (pairedGroup a) _ (markedElement (pairedSelector a))
      (primeAt (2*n+1)) ↔ a n = false := by
  cases ha : a n
  · simp only [iff_true]
    change ∃ y : pairedGroup a, (primeAt (2*n+1)).val • y = markedElement (pairedSelector a)
    have h := omitted_prime_has_root a n
    simpa only [omittedIndex, ha, Bool.false_eq_true, ↓reduceIte] using h
  · simp only [Bool.true_eq_false, iff_false]
    change ¬ ∃ y : pairedGroup a, (primeAt (2*n+1)).val • y = markedElement (pairedSelector a)
    have h := chosen_prime_obstructs a n
    simpa only [chosenIndex, ha, ↓reduceIte] using h

/-- The named element needs no negative existential test: two positive searches
suffice and their native oracle program is proved to terminate. -/
theorem marked_root_presentation_reduces (a X : ℕ → Bool) {H : Type*} [AddGroup H]
    (c : RootSearchPresentation X H) (e : H ≃+ pairedGroup a)
    (hmark : e c.target = markedElement (pairedSelector a)) (hoffset : c.offset = 0) :
    SelectorReducible a X := by
  apply paired_root_search_reduces a X c
  · intro n
    rw [← hasPrimeRoot_equiv e c.target, hmark]
    simpa [hoffset] using marked_even_root_iff a n
  · intro n
    rw [← hasPrimeRoot_equiv e c.target, hmark]
    simpa [hoffset] using marked_odd_root_iff a n

/-- Uniform marked decoding from the actual addition algorithm and a supplied
natural name for the distinguished element (Monograph 8.2). -/
theorem oracle_marked_copy_reduces (a X : ℕ → Bool)
    (c : OracleGroupCopy X (pairedGroup a)) (h : ℕ)
    (hmark : c.names h = markedElement (pairedSelector a)) : SelectorReducible a X := by
  apply marked_root_presentation_reduces a X (c.rootSearch h 0) (AddEquiv.refl _)
  · exact hmark
  · rfl

/-- The unmarked converse of the exact oracle criterion. The abstract naming
isomorphism supplies a finite natural constant naming the marker. This theorem
does not compute that constant uniformly from an unmarked atomic diagram. -/
theorem oracle_unmarked_copy_reduces (a X : ℕ → Bool)
    (c : OracleGroupCopy X (pairedGroup a)) : SelectorReducible a X := by
  apply oracle_marked_copy_reduces a X c (c.names.symm (markedElement (pairedSelector a)))
  exact c.names.apply_symm_apply _

/-- The forward half of Monograph 8.3 with a genuine coded-presentation contract. -/
theorem oracle_copy_exists_implies_selector_reducible (a X : ℕ → Bool) :
    Nonempty (OracleGroupCopy X (pairedGroup a)) → SelectorReducible a X := by
  rintro ⟨c⟩
  exact oracle_unmarked_copy_reduces a X c

/-- Relative computable enumerability is the domain of a partial function in
Mathlib's native oracle-recursion semantics. -/
def OracleEnumerable (X : ℕ → Bool) (A : Set ℕ) : Prop :=
  ∃ f : ℕ →. ℕ, Nat.RecursiveIn {selectorOracle X} f ∧
    ∀ n, (f n).Dom ↔ n ∈ A

/-- A dovetailed positive-witness search semidecides its existential predicate. -/
theorem oracleEnumerable_of_test (X : ℕ → Bool) (test : ℕ → ℕ)
    (ht : OracleComputable X test) :
    OracleEnumerable X {n | ∃ t, test (Nat.pair n t) = 0} := by
  refine ⟨_, Nat.RecursiveIn.rfind ht, ?_⟩
  intro n
  simp [Nat.rfind_dom]

/-- Deciding whether a coded candidate is nonzero prime torsion only uses finite
addition and equality tests. -/
def OracleGroupCopy.torsionTest {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) (k : ℕ) : ℕ :=
  if c.multiple (primeAt k.unpair.1).val k.unpair.2 = c.zero ∧
      k.unpair.2 ≠ c.zero then 0 else 1

theorem OracleGroupCopy.torsionTest_computable {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) : OracleComputable X c.torsionTest := by
  have hm : OracleComputable X (fun k => c.multiple (primeAt k.unpair.1).val k.unpair.2) :=
    c.multiple_computable.comp (OracleComputable.right.pair
      ((OracleComputable.of_computable computable_primeAt_value).comp OracleComputable.left))
      |>.of_eq (fun k => by simp)
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have hp : Computable (fun k : ℕ =>
      if k.unpair.1 = c.zero ∧ k.unpair.2 ≠ c.zero then 0 else 1) :=
    (Primrec.ite ((Primrec.eq.comp hl (Primrec.const c.zero)).and
      (Primrec.eq.comp hr (Primrec.const c.zero)).not)
        (Primrec.const 0) (Primrec.const 1)).to_comp
  exact (OracleComputable.of_computable hp).comp (hm.pair OracleComputable.right)
    |>.of_eq (fun k => by simp [OracleGroupCopy.torsionTest])

theorem OracleGroupCopy.torsionTest_correct {X : ℕ → Bool} {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) (n t : ℕ) : c.torsionTest (Nat.pair n t) = 0 ↔
    c.names t ≠ 0 ∧ (primeAt n).val • c.names t = 0 := by
  have hzero : c.names t = 0 ↔ t = c.zero := by
    rw [← c.zero_spec, c.names.injective.eq_iff]
  have hmul : (primeAt n).val • c.names t = 0 ↔
      c.multiple (primeAt n).val t = c.zero := by
    rw [← c.multiple_spec, ← c.zero_spec, c.names.injective.eq_iff]
  simp only [OracleGroupCopy.torsionTest, Nat.unpair_pair, ite_eq_left_iff,
    one_ne_zero, imp_false, not_not]
  constructor
  · rintro ⟨hm, hn⟩
    exact ⟨fun he => hn (hzero.mp he), hmul.mpr hm⟩
  · rintro ⟨hn, hm⟩
    exact ⟨hmul.mp hm, fun he => hn (hzero.mpr he)⟩

/-- The prime spectrum of every genuinely oracle-computable coded copy is
computably enumerable relative to that oracle. -/
theorem oracle_copy_primeSpectrum_enumerable (X : ℕ → Bool) {H : Type*} [AddGroup H]
    (c : OracleGroupCopy X H) :
    OracleEnumerable X {n | HasPrimeTorsion H (primeAt n)} := by
  obtain ⟨f, hf, hdom⟩ := oracleEnumerable_of_test X c.torsionTest c.torsionTest_computable
  refine ⟨f, hf, ?_⟩
  intro n
  rw [hdom]
  constructor
  · rintro ⟨t, ht⟩
    exact ⟨c.names t, (c.torsionTest_correct n t).mp ht⟩
  · rintro ⟨y, hy⟩
    refine ⟨c.names.symm y, (c.torsionTest_correct n _).mpr ?_⟩
    simpa only [c.names.apply_symm_apply] using hy

/-- The forward prime-spectrum implication (Monograph 3.3) on an infinite coded
copy. Finite selector groups need the separate finite-domain convention. -/
theorem oracle_spectrum_copy_implies_enumerable (X : ℕ → Bool) (B : Set Prime)
    (c : OracleGroupCopy X (spectrumSubgroup B)) :
    OracleEnumerable X {n | primeAt n ∈ B} := by
  obtain ⟨f, hf, hdom⟩ := oracle_copy_primeSpectrum_enumerable X c
  refine ⟨f, hf, ?_⟩
  intro n
  exact (hdom n).trans (spectrumSubgroup_hasPrimeTorsion_iff B (primeAt n))

end RealizationBoundaries
