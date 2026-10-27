import RealizationBoundaries.ComputablePresentations
import Mathlib.Data.Nat.Nth

/-! # From redundant computable codes to an actual computable copy -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- Redundant natural codes are permitted, but equality of their actual meanings
must be oracle computable. This is stronger than a merely enumerable relator
presentation. -/
structure OracleRawGroupCodes (X : ℕ → Bool) (H : Type*) [AddGroup H] where
  names : ℕ → H
  names_surjective : Function.Surjective names
  zero : ℕ
  add : ℕ → ℕ → ℕ
  equal : ℕ → ℕ → ℕ
  zero_spec : names zero = 0
  add_spec : ∀ i j, names (add i j) = names i + names j
  equal_spec : ∀ i j, equal i j = 0 ↔ names i = names j
  add_computable : OracleComputable X (fun k => add k.unpair.1 k.unpair.2)
  equal_computable : OracleComputable X (fun k => equal k.unpair.1 k.unpair.2)

namespace OracleRawGroupCodes
variable {X : ℕ → Bool} {H : Type*} [AddGroup H]

/-- The least natural code of its equality class. -/
def Canonical (c : OracleRawGroupCodes X H) (n : ℕ) : Prop :=
  ∀ m < n, c.names m ≠ c.names n

instance canonical_decidable (c : OracleRawGroupCodes X H) : DecidablePred c.Canonical := by
  intro n
  exact Classical.propDecidable _

theorem canonical_code_exists (c : OracleRawGroupCodes X H) (x : H) :
    ∃ n, c.Canonical n ∧ c.names n = x := by
  classical
  let h := c.names_surjective x
  refine ⟨Nat.find h, ?_, Nat.find_spec h⟩
  intro m hm he
  exact Nat.find_min h hm (he.trans (Nat.find_spec h))

theorem canonical_names_injective (c : OracleRawGroupCodes X H) :
    Function.Injective (fun n : {n // c.Canonical n} => c.names n.val) := by
  intro n m h
  apply Subtype.ext
  by_contra hn
  rcases lt_or_gt_of_ne hn with hnm | hmn
  · exact m.property n.val hnm h
  · exact n.property m.val hmn h.symm

theorem canonical_infinite (c : OracleRawGroupCodes X H) [Infinite H] :
    {n | c.Canonical n}.Infinite := by
  intro hf
  have hi : Set.Finite (Set.range c.names) := by
    apply (hf.image c.names).subset
    rintro x ⟨n, rfl⟩
    obtain ⟨m, hm, he⟩ := c.canonical_code_exists (c.names n)
    exact ⟨m, hm, he⟩
  have hu : Set.range c.names = Set.univ := Set.range_eq_univ.mpr c.names_surjective
  exact Set.infinite_univ (hu ▸ hi)

/-- Finite equality-product: nonzero exactly when no preceding code has the
same meaning as the supplied code. -/
def previousProduct (c : OracleRawGroupCodes X H) (q n : ℕ) : ℕ :=
  Nat.rec 1 (fun m r => r * c.equal m q) n

theorem previousProduct_ne_zero (c : OracleRawGroupCodes X H) (q n : ℕ) :
    c.previousProduct q n ≠ 0 ↔ ∀ m < n, c.equal m q ≠ 0 := by
  induction n with
  | zero => simp [previousProduct]
  | succ n ih =>
    change c.previousProduct q n * c.equal n q ≠ 0 ↔ _
    rw [mul_ne_zero_iff, ih]
    constructor
    · rintro ⟨h, hn⟩ m hm
      rcases Nat.lt_succ_iff_lt_or_eq.mp hm with hm | rfl
      · exact h m hm
      · exact hn
    · intro h
      exact ⟨fun m hm => h m (Nat.lt_succ_of_lt hm), h n (Nat.lt_succ_self n)⟩

/-- Zero is the successful canonical-code test. -/
def canonicalTest (c : OracleRawGroupCodes X H) (n : ℕ) : ℕ :=
  if c.previousProduct n n = 0 then 1 else 0

theorem canonicalTest_correct (c : OracleRawGroupCodes X H) (n : ℕ) :
    c.canonicalTest n = 0 ↔ c.Canonical n := by
  simp only [canonicalTest, ite_eq_right_iff, one_ne_zero, imp_false]
  change c.previousProduct n n ≠ 0 ↔ c.Canonical n
  rw [c.previousProduct_ne_zero]
  exact forall_congr' fun m => imp_congr_right fun _ => (c.equal_spec m n).not

theorem previousProduct_computable (c : OracleRawGroupCodes X H) :
    OracleComputable X (fun k => c.previousProduct k.unpair.1 k.unpair.2) := by
  have he : OracleComputable X
      (fun k => c.equal k.unpair.2.unpair.1 k.unpair.1) :=
    c.equal_computable.comp ((OracleComputable.left.comp OracleComputable.right).pair
      OracleComputable.left) |>.of_eq (fun k => by simp)
  exact OracleComputable.prec (step := fun q m r => r * c.equal m q) (OracleComputable.const 1)
    ((OracleComputable.right.comp OracleComputable.right).mul he)

theorem canonicalTest_computable (c : OracleRawGroupCodes X H) :
    OracleComputable X c.canonicalTest :=
  (c.previousProduct_computable.comp (OracleComputable.id.pair OracleComputable.id)).isZero
    |>.of_eq (fun n => by simp [canonicalTest])

end OracleRawGroupCodes

namespace OracleComputable
variable {X : ℕ → Bool} {f g : ℕ → ℕ}

theorem add (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => f n + g n) :=
  (Nat.Primrec.add.recursiveIn : OracleComputable X (Nat.unpaired (· + ·))).comp
    (hf.pair hg) |>.of_eq (fun n => by simp [Nat.unpaired])

/-- The count of successful zero tests below a finite bound. -/
def zeroCount (test : ℕ → ℕ) (n : ℕ) : ℕ :=
  Nat.rec 0 (fun m r => r + if test m = 0 then 1 else 0) n

theorem zeroCount_computable (ht : OracleComputable X f) :
    OracleComputable X (zeroCount f) := by
  have hi := (ht.comp (OracleComputable.left.comp OracleComputable.right)).isZero
  have hrec := OracleComputable.prec (step := fun _ m r => r + if f m = 0 then 1 else 0) (OracleComputable.const 0)
    ((OracleComputable.right.comp OracleComputable.right).add hi)
  exact (hrec.comp ((OracleComputable.const 0).pair OracleComputable.id)).of_eq
    (fun n => by simp [zeroCount])

theorem zeroCount_eq_count (test : ℕ → ℕ) (n : ℕ) :
    zeroCount test n = Nat.count (fun m => test m = 0) n := by
  induction n with
  | zero => simp [zeroCount]
  | succ n ih =>
    change zeroCount test n + (if test n = 0 then 1 else 0) = _
    rw [Nat.count_succ, ih]

/-- A zero test for the relation: candidate `m` is successful and has exactly
`n` successful predecessors. -/
def nthTest (test : ℕ → ℕ) (k : ℕ) : ℕ :=
  if test k.unpair.2 = 0 ∧ zeroCount test k.unpair.2 = k.unpair.1 then 0 else 1

theorem nthTest_computable (ht : OracleComputable X f) :
    OracleComputable X (nthTest f) := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have hp : Computable (fun k : ℕ =>
      if k.unpair.1 = 0 ∧ k.unpair.2.unpair.1 = k.unpair.2.unpair.2 then 0 else 1) :=
    (Primrec.ite ((Primrec.eq.comp hl (Primrec.const 0)).and
      (Primrec.eq.comp (hl.comp hr) (hr.comp hr)))
      (Primrec.const 0) (Primrec.const 1)).to_comp
  exact (of_computable hp).comp ((ht.comp right).pair
    (((zeroCount_computable ht).comp right).pair left))
      |>.of_eq (fun k => by simp [nthTest])

theorem nthTest_correct (test : ℕ → ℕ) (n m : ℕ) :
    nthTest test (Nat.pair n m) = 0 ↔
      test m = 0 ∧ Nat.count (fun t => test t = 0) m = n := by
  simp [nthTest, zeroCount_eq_count]

/-- Increasing enumeration of an infinite oracle-decidable set is an actual
terminating oracle computation. -/
theorem nth_zero_computable (test : ℕ → ℕ) (ht : OracleComputable X test)
    (hi : {n | test n = 0}.Infinite) :
    OracleComputable X (Nat.nth (fun n => test n = 0)) := by
  have total : ∀ n, ∃ m, nthTest test (Nat.pair n m) = 0 := by
    intro n
    refine ⟨Nat.nth (fun m => test m = 0) n, (nthTest_correct test _ _).mpr ?_⟩
    exact ⟨Nat.nth_mem_of_infinite hi n, Nat.count_nth_of_infinite hi n⟩
  apply (find (nthTest_computable ht) total).of_eq
  intro n
  have hm := (nthTest_correct test n _).mp (Nat.find_spec (total n))
  have he := Nat.nth_count (p := fun m => test m = 0) hm.1
  rw [hm.2] at he
  exact he.symm

end OracleComputable

namespace OracleRawGroupCodes
variable {X : ℕ → Bool} {H : Type*} [AddGroup H] [Infinite H]

theorem canonicalTest_infinite (c : OracleRawGroupCodes X H) :
    {n | c.canonicalTest n = 0}.Infinite := by
  have he : {n | c.canonicalTest n = 0} = {n | c.Canonical n} :=
    Set.ext (c.canonicalTest_correct)
  rw [he]
  exact c.canonical_infinite

/-- Increasing enumeration of the least equality-class representatives. -/
def enumCode (c : OracleRawGroupCodes X H) : ℕ → ℕ :=
  Nat.nth (fun n => c.canonicalTest n = 0)

theorem enumCode_computable (c : OracleRawGroupCodes X H) :
    OracleComputable X c.enumCode :=
  OracleComputable.nth_zero_computable c.canonicalTest c.canonicalTest_computable
    c.canonicalTest_infinite

theorem enumCode_canonical (c : OracleRawGroupCodes X H) (n : ℕ) :
    c.Canonical (c.enumCode n) :=
  (c.canonicalTest_correct _).mp (Nat.nth_mem_of_infinite c.canonicalTest_infinite n)

theorem enumNames_injective (c : OracleRawGroupCodes X H) :
    Function.Injective (fun n => c.names (c.enumCode n)) := by
  intro n m h
  have hc := c.canonical_names_injective
    (show (fun k : {n // c.Canonical n} => c.names k.val)
      ⟨c.enumCode n, c.enumCode_canonical n⟩ =
      (fun k : {n // c.Canonical n} => c.names k.val)
      ⟨c.enumCode m, c.enumCode_canonical m⟩ from h)
  exact Nat.nth_injective c.canonicalTest_infinite (congrArg Subtype.val hc)

omit [Infinite H] in
theorem enumNames_surjective (c : OracleRawGroupCodes X H) :
    Function.Surjective (fun n => c.names (c.enumCode n)) := by
  intro x
  obtain ⟨m, hm, he⟩ := c.canonical_code_exists x
  refine ⟨Nat.count (fun n => c.canonicalTest n = 0) m, ?_⟩
  unfold enumCode
  dsimp only
  rw [Nat.nth_count (p := fun n => c.canonicalTest n = 0) ((c.canonicalTest_correct m).mpr hm)]
  exact he

/-- An actual bijective naming, obtained from the computed canonical enumeration. -/
def namesEquiv (c : OracleRawGroupCodes X H) : ℕ ≃ H :=
  Equiv.ofBijective (fun n => c.names (c.enumCode n))
    ⟨c.enumNames_injective, c.enumNames_surjective⟩

/-- Search for the unique canonical name of a raw code. -/
def indexTest (c : OracleRawGroupCodes X H) (k : ℕ) : ℕ :=
  c.equal (c.enumCode k.unpair.2) k.unpair.1

theorem indexTest_computable (c : OracleRawGroupCodes X H) :
    OracleComputable X c.indexTest :=
  c.equal_computable.comp ((c.enumCode_computable.comp OracleComputable.right).pair
    OracleComputable.left) |>.of_eq (fun k => by simp [indexTest])

omit [Infinite H] in
theorem indexTest_total (c : OracleRawGroupCodes X H) (n : ℕ) :
    ∃ t, c.indexTest (Nat.pair n t) = 0 := by
  obtain ⟨t, ht⟩ := c.enumNames_surjective (c.names n)
  refine ⟨t, ?_⟩
  simpa only [indexTest, Nat.unpair_pair] using (c.equal_spec _ _).mpr ht

/-- Canonical index extraction terminates by surjectivity of the enumeration. -/
def index (c : OracleRawGroupCodes X H) (n : ℕ) : ℕ :=
  Nat.find (c.indexTest_total n)

theorem index_computable (c : OracleRawGroupCodes X H) :
    OracleComputable X c.index :=
  OracleComputable.find c.indexTest_computable c.indexTest_total

theorem index_spec (c : OracleRawGroupCodes X H) (n : ℕ) :
    c.namesEquiv (c.index n) = c.names n := by
  apply (c.equal_spec _ _).mp
  simpa only [indexTest, index, Nat.unpair_pair] using Nat.find_spec (c.indexTest_total n)

/-- Redundant codes with decidable oracle equality yield a genuine computable
Nat-domain copy of every infinite group they enumerate. No quotient equality is
silently treated as decidable. -/
def toOracleGroupCopy (c : OracleRawGroupCodes X H) : OracleGroupCopy X H where
  names := c.namesEquiv
  zero := c.index c.zero
  add := fun i j => c.index (c.add (c.enumCode i) (c.enumCode j))
  zero_spec := (c.index_spec c.zero).trans c.zero_spec
  add_spec := by
    intro i j
    exact (c.index_spec _).trans (c.add_spec _ _)
  add_computable := by
    have ha := c.add_computable.comp
      ((c.enumCode_computable.comp OracleComputable.left).pair
        (c.enumCode_computable.comp OracleComputable.right))
    exact c.index_computable.comp ha |>.of_eq (fun k => by simp)

/-- The existence form needed by concrete raw normal-form constructions. -/
theorem oracleGroupCopy_of_rawCodes (c : OracleRawGroupCodes X H) :
    Nonempty (OracleGroupCopy X H) :=
  ⟨c.toOracleGroupCopy⟩

end OracleRawGroupCodes

end RealizationBoundaries
