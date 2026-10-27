import RealizationBoundaries.ComputableQuotientCodes
import RealizationBoundaries.OraclePartialRecursionTraces
import RealizationBoundaries.OraclePartialMinimizationTraces
import Mathlib.Data.List.OfFn

/-! # Finite witnesses for native oracle recursion -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

namespace OracleComputable
variable {X : ℕ → Bool} {f g : ℕ → ℕ}

theorem eqFail (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => if f n = g n then 0 else 1) := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have he : Computable (fun k : ℕ => if k.unpair.1 = k.unpair.2 then 0 else 1) :=
    (Primrec.ite (Primrec.eq.comp hl hr) (Primrec.const 0) (Primrec.const 1)).to_comp
  exact (of_computable he).comp (hf.pair hg) |>.of_eq (fun k => by simp)

/-- A finite sum of total oracle tests. -/
def boundedSum (test : ℕ → ℕ) (a n : ℕ) : ℕ :=
  Nat.rec 0 (fun m r => r + test (Nat.pair a m)) n

theorem boundedSum_computable (ht : OracleComputable X f) :
    OracleComputable X (fun k => boundedSum f k.unpair.1 k.unpair.2) := by
  have he := ht.comp (left.pair (left.comp right))
  exact prec (step := fun a m r => r + f (Nat.pair a m)) (const 0)
    ((right.comp right).add he)

theorem boundedSum_zero_iff (test : ℕ → ℕ) (a n : ℕ) :
    boundedSum test a n = 0 ↔ ∀ m < n, test (Nat.pair a m) = 0 := by
  induction n with
  | zero => simp [boundedSum]
  | succ n ih =>
    change boundedSum test a n + test (Nat.pair a n) = 0 ↔ _
    rw [Nat.add_eq_zero_iff, ih]
    constructor
    · rintro ⟨h, hn⟩ m hm
      rcases Nat.lt_succ_iff_lt_or_eq.mp hm with hm | rfl
      · exact h m hm
      · exact hn
    · intro h
      exact ⟨fun m hm => h m (Nat.lt_succ_of_lt hm), h n (Nat.lt_succ_self n)⟩

end OracleComputable

/-- A total oracle-computable finite witness verifier for the graph of a partial
function. A successful witness is a natural number, not an oracle for the graph. -/
structure OracleGraphSearch (X : ℕ → Bool) (f : ℕ →. ℕ) where
  test : ℕ → ℕ
  computable : OracleComputable X test
  correct : ∀ n y, y ∈ f n ↔ ∃ t, test (Nat.pair n (Nat.pair y t)) = 0

namespace OracleGraphSearch
variable {X : ℕ → Bool} {f g : ℕ →. ℕ}

abbrev inp (k : ℕ) : ℕ := k.unpair.1
abbrev out (k : ℕ) : ℕ := k.unpair.2.unpair.1
abbrev wit (k : ℕ) : ℕ := k.unpair.2.unpair.2

theorem comp_inp : OracleComputable X inp := OracleComputable.left

theorem comp_out : OracleComputable X out :=
  OracleComputable.left.comp OracleComputable.right

theorem comp_wit : OracleComputable X wit :=
  OracleComputable.right.comp OracleComputable.right

/-- Total oracle functions have a trivial finite graph verifier. -/
def of_total (q : ℕ → ℕ) (hq : OracleComputable X q) :
    OracleGraphSearch X (fun n => Part.some (q n)) where
  test := fun k => if q (inp k) = out k then 0 else 1
  computable := (hq.comp comp_inp).eqFail comp_out
  correct := by intro n y; simp [inp, out, eq_comm]

/-- Pairing combines two finite witness verifiers. -/
def pair (sf : OracleGraphSearch X f) (sg : OracleGraphSearch X g) :
    OracleGraphSearch X (fun n => (f n).bind (fun u => (g n).map (Nat.pair u))) where
  test := fun k => sf.test (Nat.pair (inp k) (Nat.pair (out k).unpair.1 (wit k).unpair.1)) +
    sg.test (Nat.pair (inp k) (Nat.pair (out k).unpair.2 (wit k).unpair.2))
  computable := by
    exact (sf.computable.comp (comp_inp.pair
      ((OracleComputable.left.comp comp_out).pair (OracleComputable.left.comp comp_wit)))).add
      (sg.computable.comp (comp_inp.pair
        ((OracleComputable.right.comp comp_out).pair (OracleComputable.right.comp comp_wit))))
  correct := by
    intro n y
    simp only [Part.mem_bind_iff, Part.mem_map_iff]
    constructor
    · rintro ⟨u, hu, v, hv, hy⟩
      obtain ⟨tf, htf⟩ := (sf.correct n u).mp hu
      obtain ⟨tg, htg⟩ := (sg.correct n v).mp hv
      subst y
      exact ⟨Nat.pair tf tg, by simp [inp, out, wit, htf, htg]⟩
    · rintro ⟨t, ht⟩
      have hh : sf.test (Nat.pair n (Nat.pair y.unpair.1 t.unpair.1)) = 0 ∧
          sg.test (Nat.pair n (Nat.pair y.unpair.2 t.unpair.2)) = 0 := by
        simpa [inp, out, wit] using ht
      exact ⟨y.unpair.1, (sf.correct n _).mpr ⟨t.unpair.1, hh.1⟩,
        y.unpair.2, (sg.correct n _).mpr ⟨t.unpair.2, hh.2⟩, Nat.pair_unpair y⟩

/-- Composition stores the intermediate result and both child certificates. -/
def comp (sf : OracleGraphSearch X f) (sg : OracleGraphSearch X g) :
    OracleGraphSearch X (fun n => (g n).bind f) where
  test := fun k => sg.test (Nat.pair (inp k)
      (Nat.pair (wit k).unpair.1 (wit k).unpair.2.unpair.1)) +
    sf.test (Nat.pair (wit k).unpair.1 (Nat.pair (out k) (wit k).unpair.2.unpair.2))
  computable := by
    have hm : OracleComputable X (fun k => (wit k).unpair.1) := OracleComputable.left.comp comp_wit
    have htf : OracleComputable X (fun k => (wit k).unpair.2.unpair.2) :=
      OracleComputable.right.comp (OracleComputable.right.comp comp_wit)
    have htg : OracleComputable X (fun k => (wit k).unpair.2.unpair.1) :=
      OracleComputable.left.comp (OracleComputable.right.comp comp_wit)
    exact (sg.computable.comp (comp_inp.pair (hm.pair htg))).add
      (sf.computable.comp (hm.pair (comp_out.pair htf)))
  correct := by
    intro n y
    rw [Part.mem_bind_iff]
    constructor
    · rintro ⟨m, hm, hy⟩
      obtain ⟨tg, htg⟩ := (sg.correct n m).mp hm
      obtain ⟨tf, htf⟩ := (sf.correct m y).mp hy
      exact ⟨Nat.pair m (Nat.pair tg tf), by simp [inp, out, wit, htg, htf]⟩
    · rintro ⟨t, ht⟩
      have hh : sg.test (Nat.pair n (Nat.pair t.unpair.1 t.unpair.2.unpair.1)) = 0 ∧
          sf.test (Nat.pair t.unpair.1 (Nat.pair y t.unpair.2.unpair.2)) = 0 := by
        simpa [inp, out, wit] using ht
      exact ⟨t.unpair.1, (sg.correct _ _).mpr ⟨_, hh.1⟩,
        (sf.correct _ _).mpr ⟨_, hh.2⟩⟩

/-- Natural decoding of a finite list of paired state/certificate entries. -/
def traceList (t : ℕ) : List ℕ := (Encodable.decode t).getD []

def traceEntry (t i : ℕ) : ℕ := (traceList t).getD i 0

def traceState (t i : ℕ) : ℕ := (traceEntry t i).unpair.1

def traceProof (t i : ℕ) : ℕ := (traceEntry t i).unpair.2

theorem primrec_traceList : Primrec traceList :=
  Primrec.option_getD.comp Primrec.decode (Primrec.const [])

theorem primrec_traceEntry : Primrec₂ traceEntry :=
  (Primrec.list_getD 0).comp (primrec_traceList.comp Primrec.fst) Primrec.snd

theorem primrec_traceState : Primrec₂ traceState :=
  ((Primrec.fst.comp Primrec.unpair).comp primrec_traceEntry)

theorem primrec_traceProof : Primrec₂ traceProof :=
  ((Primrec.snd.comp Primrec.unpair).comp primrec_traceEntry)

theorem finiteTrace_exists (states proofs : ℕ → ℕ) (N : ℕ) :
    ∃ t, ∀ i < N, traceState t i = states i ∧ traceProof t i = proofs i := by
  refine ⟨Encodable.encode (List.ofFn (fun i : Fin N => Nat.pair (states i) (proofs i))), ?_⟩
  intro i hi
  simp [traceState, traceProof, traceEntry, traceList, List.getD_eq_getElem?_getD, hi]

theorem primrec_inp : Primrec inp := Primrec.fst.comp Primrec.unpair

theorem primrec_out : Primrec out :=
  (Primrec.fst.comp Primrec.unpair).comp (Primrec.snd.comp Primrec.unpair)

theorem primrec_wit : Primrec wit :=
  (Primrec.snd.comp Primrec.unpair).comp (Primrec.snd.comp Primrec.unpair)

theorem primrec_triple {a b c : ℕ → ℕ} (ha : Primrec a) (hb : Primrec b) (hc : Primrec c) :
    Primrec (fun k => Nat.pair (a k) (Nat.pair (b k) (c k))) :=
  Primrec₂.natPair.comp ha (Primrec₂.natPair.comp hb hc)

def recBaseCode (k : ℕ) : ℕ :=
  Nat.pair (inp k).unpair.1 (Nat.pair (traceState (wit k) 0) (traceProof (wit k) 0))

def recStepCode (z : ℕ) : ℕ :=
  let k := z.unpair.1
  let i := z.unpair.2
  Nat.pair (Nat.pair (inp k).unpair.1 (Nat.pair i (traceState (wit k) i)))
    (Nat.pair (traceState (wit k) (i+1)) (traceProof (wit k) (i+1)))

theorem primrec_recBaseCode : Primrec recBaseCode :=
  primrec_triple ((Primrec.fst.comp Primrec.unpair).comp primrec_inp)
    (primrec_traceState.comp primrec_wit (Primrec.const 0))
    (primrec_traceProof.comp primrec_wit (Primrec.const 0))

theorem primrec_recStepCode : Primrec recStepCode := by
  have hl : Primrec (fun z : ℕ => z.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun z : ℕ => z.unpair.2) := Primrec.snd.comp Primrec.unpair
  have ha := hl.comp (primrec_inp.comp hl)
  have ht := primrec_wit.comp hl
  exact primrec_triple (primrec_triple ha hr (primrec_traceState.comp ht hr))
    (primrec_traceState.comp ht (Primrec.succ.comp hr))
    (primrec_traceProof.comp ht (Primrec.succ.comp hr))

def recTest (sf : OracleGraphSearch X f) (sg : OracleGraphSearch X g) (k : ℕ) : ℕ :=
  sf.test (recBaseCode k) +
    OracleComputable.boundedSum (fun z => sg.test (recStepCode z)) k (inp k).unpair.2 +
      if traceState (wit k) (inp k).unpair.2 = out k then 0 else 1

theorem recTest_computable (sf : OracleGraphSearch X f) (sg : OracleGraphSearch X g) :
    OracleComputable X (recTest sf sg) := by
  have hb := sf.computable.comp (OracleComputable.of_computable primrec_recBaseCode.to_comp)
  have hs := sg.computable.comp (OracleComputable.of_computable primrec_recStepCode.to_comp)
  have hn : Primrec (fun k => (inp k).unpair.2) :=
    (Primrec.snd.comp Primrec.unpair).comp primrec_inp
  have ht := (OracleComputable.boundedSum_computable hs).comp
    (OracleComputable.id.pair (OracleComputable.of_computable hn.to_comp))
  have he : OracleComputable X (fun k => if traceState (wit k) (inp k).unpair.2 = out k then 0 else 1) :=
    (OracleComputable.of_computable
      (primrec_traceState.comp primrec_wit hn).to_comp).eqFail comp_out
  exact (hb.add ht).add he |>.of_eq (fun k => by simp [recTest])

theorem recTest_correct (sf : OracleGraphSearch X f) (sg : OracleGraphSearch X g)
    (a n y t : ℕ) : recTest sf sg (Nat.pair (Nat.pair a n) (Nat.pair y t)) = 0 ↔
      sf.test (Nat.pair a (Nat.pair (traceState t 0) (traceProof t 0))) = 0 ∧
      (∀ i < n, sg.test (Nat.pair (Nat.pair a (Nat.pair i (traceState t i)))
        (Nat.pair (traceState t (i+1)) (traceProof t (i+1)))) = 0) ∧ traceState t n = y := by
  simp [recTest, recBaseCode, recStepCode, inp, out, wit,
    OracleComputable.boundedSum_zero_iff, and_assoc]

/-- Primitive recursion is verified by a finite trace of child computations. -/
def prec (sf : OracleGraphSearch X f) (sg : OracleGraphSearch X g) :
    OracleGraphSearch X (fun p => oraclePartialRec f g p.unpair.1 p.unpair.2) where
  test := recTest sf sg
  computable := recTest_computable sf sg
  correct := by
    intro p y
    have hp := Nat.pair_unpair p
    conv_lhs => rw [← hp]
    conv_rhs => rw [← hp]
    simp only [Nat.unpair_pair]
    rw [oraclePartialRec_mem_iff_trace]
    constructor
    · rintro ⟨states, hlast, hb, hs⟩
      obtain ⟨b, hbase⟩ := (sf.correct _ _).mp hb
      have hh : ∀ i, ∃ c, i < p.unpair.2 →
          sg.test (Nat.pair (Nat.pair p.unpair.1 (Nat.pair i (states i)))
            (Nat.pair (states (i+1)) c)) = 0 := by
        intro i
        by_cases hi : i < p.unpair.2
        · obtain ⟨c, hc⟩ := (sg.correct _ _).mp (hs i hi)
          exact ⟨c, fun _ => hc⟩
        · exact ⟨0, fun h => False.elim (hi h)⟩
      choose cs hcs using hh
      let proofs := fun i => if i = 0 then b else cs (i-1)
      obtain ⟨t, ht⟩ := finiteTrace_exists states proofs (p.unpair.2+1)
      refine ⟨t, (recTest_correct sf sg _ _ _ _).mpr ?_⟩
      have h0 := ht 0 (Nat.zero_lt_succ _)
      have hn := ht p.unpair.2 (Nat.lt_succ_self _)
      refine ⟨?_, ?_, hn.1.trans hlast⟩
      · simpa [h0.1, h0.2, proofs] using hbase
      · intro i hi
        have hi0 := ht i (Nat.lt_succ_of_lt hi)
        have hi1 := ht (i+1) (Nat.succ_lt_succ hi)
        simpa [hi0.1, hi1.1, hi1.2, proofs] using hcs i hi
    · rintro ⟨t, ht⟩
      obtain ⟨hb, hs, hlast⟩ := (recTest_correct sf sg _ _ _ _).mp ht
      refine ⟨traceState t, hlast, (sf.correct _ _).mpr ⟨_, hb⟩, ?_⟩
      intro i hi
      exact (sg.correct _ _).mpr ⟨_, hs i hi⟩

def minStepCode (z : ℕ) : ℕ :=
  let k := z.unpair.1
  let i := z.unpair.2
  Nat.pair (Nat.pair (inp k) i) (Nat.pair (traceState (wit k) i) (traceProof (wit k) i))

def minNonzeroTest (z : ℕ) : ℕ :=
  if traceState (wit z.unpair.1) z.unpair.2 = 0 then 1 else 0

theorem primrec_minStepCode : Primrec minStepCode := by
  have hl : Primrec (fun z : ℕ => z.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun z : ℕ => z.unpair.2) := Primrec.snd.comp Primrec.unpair
  have ht := primrec_wit.comp hl
  exact primrec_triple (Primrec₂.natPair.comp (primrec_inp.comp hl) hr)
    (primrec_traceState.comp ht hr) (primrec_traceProof.comp ht hr)

theorem primrec_minNonzeroTest : Primrec minNonzeroTest := by
  have hl : Primrec (fun z : ℕ => z.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun z : ℕ => z.unpair.2) := Primrec.snd.comp Primrec.unpair
  exact Primrec.ite (Primrec.eq.comp
    (primrec_traceState.comp (primrec_wit.comp hl) hr) (Primrec.const 0))
    (Primrec.const 1) (Primrec.const 0)

def minTest (sf : OracleGraphSearch X f) (k : ℕ) : ℕ :=
  OracleComputable.boundedSum (fun z => sf.test (minStepCode z)) k (out k+1) +
    OracleComputable.boundedSum minNonzeroTest k (out k) + traceState (wit k) (out k)

theorem minTest_computable (sf : OracleGraphSearch X f) :
    OracleComputable X (minTest sf) := by
  have hs : OracleComputable X (fun z => sf.test (minStepCode z)) :=
    sf.computable.comp (OracleComputable.of_computable primrec_minStepCode.to_comp)
  have hc : OracleComputable X (fun k =>
      OracleComputable.boundedSum (fun z => sf.test (minStepCode z)) k (out k+1)) := by
    exact ((OracleComputable.boundedSum_computable hs).comp
      (OracleComputable.id.pair
        (OracleComputable.of_computable (Primrec.succ.comp primrec_out).to_comp))).of_eq
          (fun k => by simp)
  have hp : OracleComputable X minNonzeroTest :=
    OracleComputable.of_computable primrec_minNonzeroTest.to_comp
  have hn : OracleComputable X (fun k =>
      OracleComputable.boundedSum minNonzeroTest k (out k)) := by
    exact ((OracleComputable.boundedSum_computable hp).comp
      (OracleComputable.id.pair comp_out)).of_eq (fun k => by simp)
  have hz : OracleComputable X (fun k => traceState (wit k) (out k)) :=
    OracleComputable.of_computable (primrec_traceState.comp primrec_wit primrec_out).to_comp
  exact (hc.add hn).add hz

theorem minTest_correct (sf : OracleGraphSearch X f) (a y t : ℕ) :
    minTest sf (Nat.pair a (Nat.pair y t)) = 0 ↔
      (∀ i ≤ y, sf.test (Nat.pair (Nat.pair a i)
        (Nat.pair (traceState t i) (traceProof t i))) = 0) ∧
      (∀ i < y, traceState t i ≠ 0) ∧ traceState t y = 0 := by
  simp [minTest, minStepCode, minNonzeroTest, inp, out, wit,
    OracleComputable.boundedSum_zero_iff, and_assoc]

/-- Native minimization is certified by all earlier defined nonzero child
outputs and the final zero, verified on one finite trace. -/
def rfind (sf : OracleGraphSearch X f) :
    OracleGraphSearch X (fun a => Nat.rfind
      (fun i => (fun m => decide (m = 0)) <$> f (Nat.pair a i))) where
  test := minTest sf
  computable := minTest_computable sf
  correct := by
    intro a y
    rw [oracle_partial_minimization_trace]
    constructor
    · rintro ⟨states, hlast, hs, hn⟩
      have hh : ∀ i, ∃ c, i ≤ y →
          sf.test (Nat.pair (Nat.pair a i) (Nat.pair (states i) c)) = 0 := by
        intro i
        by_cases hi : i ≤ y
        · obtain ⟨c, hc⟩ := (sf.correct _ _).mp (hs i hi)
          exact ⟨c, fun _ => hc⟩
        · exact ⟨0, fun h => False.elim (hi h)⟩
      choose proofs hproofs using hh
      obtain ⟨t, ht⟩ := finiteTrace_exists states proofs (y+1)
      refine ⟨t, (minTest_correct sf _ _ _).mpr ⟨?_, ?_, ?_⟩⟩
      · intro i hi
        have hti := ht i (Nat.lt_succ_iff.mpr hi)
        simpa [hti.1, hti.2] using hproofs i hi
      · intro i hi
        rw [(ht i (Nat.lt_succ_of_lt hi)).1]
        exact hn i hi
      · exact (ht y (Nat.lt_succ_self _)).1.trans hlast
    · rintro ⟨t, ht⟩
      obtain ⟨hs, hn, hlast⟩ := (minTest_correct sf _ _ _).mp ht
      refine ⟨traceState t, hlast, ?_, hn⟩
      intro i hi
      exact (sf.correct _ _).mpr ⟨_, hs i hi⟩

/-- Transport of an exact graph verifier across pointwise equality. -/
def of_eq (sf : OracleGraphSearch X f) (h : ∀ n, f n = g n) : OracleGraphSearch X g where
  test := sf.test
  computable := sf.computable
  correct := by intro n y; rw [← h n]; exact sf.correct n y

end OracleGraphSearch

theorem part_pair_bind_eq (a b : Part ℕ) :
    a.bind (fun u => b.map (Nat.pair u)) = Nat.pair <$> a <*> b := by
  rw [seq_eq_bind_map]
  change a.bind (fun u => b.map (Nat.pair u)) = (a.map Nat.pair).bind (fun v => b.map v)
  rw [Part.bind_map]

/-- Every native oracle-recursive partial function has a total oracle-computable
finite graph witness verifier. The proof follows every primitive-recursion and
minimization constructor; no relativized normal form is assumed. -/
theorem recursiveIn_has_graphSearch (X : ℕ → Bool) (f : ℕ →. ℕ)
    (hf : Nat.RecursiveIn {selectorOracle X} f) : Nonempty (OracleGraphSearch X f) := by
  induction hf with
  | zero => exact ⟨OracleGraphSearch.of_total (fun _ => 0) (OracleComputable.const 0)⟩
  | succ => exact ⟨OracleGraphSearch.of_total Nat.succ
      (OracleComputable.of_computable Computable.succ)⟩
  | left => exact ⟨OracleGraphSearch.of_total _ OracleComputable.left⟩
  | right => exact ⟨OracleGraphSearch.of_total _ OracleComputable.right⟩
  | oracle g hg =>
    have he : g = selectorOracle X := Set.mem_singleton_iff.mp hg
    subst g
    exact ⟨OracleGraphSearch.of_total _ OracleComputable.oracle⟩
  | pair _ _ ihf ihg =>
    obtain ⟨sf⟩ := ihf
    obtain ⟨sg⟩ := ihg
    refine ⟨(sf.pair sg).of_eq ?_⟩
    intro n
    exact part_pair_bind_eq _ _
  | comp _ _ ihf ihg =>
    obtain ⟨sf⟩ := ihf
    obtain ⟨sg⟩ := ihg
    exact ⟨sf.comp sg⟩
  | prec _ _ ihf ihg =>
    obtain ⟨sf⟩ := ihf
    obtain ⟨sg⟩ := ihg
    exact ⟨sf.prec sg⟩
  | rfind _ ihf =>
    obtain ⟨sf⟩ := ihf
    exact ⟨sf.rfind⟩

/-- Native partial-oracle-domain enumerability has an explicit total searchable
stage test. This closes the semantics gap between the domain and listing APIs. -/
theorem oracleEnumerable_has_total_search (X : ℕ → Bool) (A : Set ℕ)
    (hA : OracleEnumerable X A) :
    ∃ test : ℕ → ℕ, OracleComputable X test ∧
      ∀ n, n ∈ A ↔ ∃ t, test (Nat.pair n t) = 0 := by
  obtain ⟨f, hf, hdom⟩ := hA
  obtain ⟨s⟩ := recursiveIn_has_graphSearch X f hf
  refine ⟨s.test, s.computable, ?_⟩
  intro n
  rw [← hdom]
  constructor
  · intro hn
    obtain ⟨y, hy⟩ := Part.dom_iff_mem.mp hn
    obtain ⟨t, ht⟩ := (s.correct n y).mp hy
    exact ⟨Nat.pair y t, ht⟩
  · rintro ⟨t, ht⟩
    apply Part.dom_iff_mem.mpr
    refine ⟨t.unpair.1, (s.correct n _).mpr ⟨t.unpair.2, ?_⟩⟩
    simpa only [Nat.pair_unpair] using ht

end RealizationBoundaries
