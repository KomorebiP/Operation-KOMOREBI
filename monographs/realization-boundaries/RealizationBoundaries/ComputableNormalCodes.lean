import RealizationBoundaries.ComputablePresentations
import RealizationBoundaries.RootAlgorithm
import RealizationBoundaries.RationalComputability
import RealizationBoundaries.ComputableQuotientCodes

/-! # Native oracle computations on finite normal-form codes -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- The actual paired-prime mask, expressed using the prime-counting index. -/
def pairedMask (a : ℕ → Bool) (p : ℕ) : ℕ :=
  if (if a (Nat.count Nat.Prime p / 2) then 1 else 0) = Nat.count Nat.Prime p % 2
  then 1 else 0

theorem pairedMask_exact (a : ℕ → Bool) (p : Prime) :
    pairedMask a p.val = 1 ↔ p ∈ pairedSelector a := by
  have hindex : primeAt (Nat.count Nat.Prime p.val) = p :=
    Subtype.ext (Nat.nth_count p.property)
  constructor
  · intro h
    have hm : (if a (Nat.count Nat.Prime p.val / 2) then 1 else 0) =
        Nat.count Nat.Prime p.val % 2 := by
      by_contra hm
      simp [pairedMask, hm] at h
    refine ⟨Nat.count Nat.Prime p.val / 2, ?_⟩
    have he : chosenIndex a (Nat.count Nat.Prime p.val / 2) = Nat.count Nat.Prime p.val := by
      unfold chosenIndex
      cases ha : a (Nat.count Nat.Prime p.val / 2) <;> simp [ha] at hm ⊢ <;> omega
    change primeAt (chosenIndex a (Nat.count Nat.Prime p.val / 2)) = p
    rw [he, hindex]
  · rintro ⟨n, hn⟩
    have hi : Nat.count Nat.Prime p.val = chosenIndex a n := by
      rw [← hn]
      exact Nat.count_nth_of_infinite Nat.infinite_setOfPred_prime _
    have hdiv : chosenIndex a n / 2 = n := by
      unfold chosenIndex
      split <;> omega
    have hmod : chosenIndex a n % 2 = if a n then 1 else 0 := by
      unfold chosenIndex
      split <;> omega
    simp [pairedMask, hi, hdiv, hmod]

namespace OracleComputable
variable {X : ℕ → Bool} {f g : ℕ → ℕ}

theorem ncAdd (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => f n + g n) :=
  (of_computable ((Primrec.nat_add.comp (Primrec.fst.comp Primrec.unpair)
    (Primrec.snd.comp Primrec.unpair)).to_comp)).comp (hf.pair hg) |>.of_eq
    (fun n => by simp)

theorem ncSub (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => f n - g n) :=
  (of_computable ((Primrec.nat_sub.comp (Primrec.fst.comp Primrec.unpair)
    (Primrec.snd.comp Primrec.unpair)).to_comp)).comp (hf.pair hg) |>.of_eq
    (fun n => by simp)

theorem ncMod (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => f n % g n) :=
  (of_computable ((Primrec.nat_mod.comp (Primrec.fst.comp Primrec.unpair)
    (Primrec.snd.comp Primrec.unpair)).to_comp)).comp (hf.pair hg) |>.of_eq
    (fun n => by simp)

theorem ncEq (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => if f n = g n then 1 else 0) := by
  have he : Computable (fun k : ℕ => if k.unpair.1 = k.unpair.2 then 1 else 0) :=
    (Primrec.ite (Primrec.eq.comp (Primrec.fst.comp Primrec.unpair)
      (Primrec.snd.comp Primrec.unpair)) (Primrec.const 1) (Primrec.const 0)).to_comp
  exact (of_computable he).comp (hf.pair hg) |>.of_eq (fun n => by simp)

/-- Native primitive recursion with a parameter and a total state. -/
theorem ncRec {b s : ℕ → ℕ} (hb : OracleComputable X b) (hs : OracleComputable X s) :
    OracleComputable X (fun z => Nat.rec (b z.unpair.1)
      (fun k r => s (Nat.pair z.unpair.1 (Nat.pair k r))) z.unpair.2) := by
  apply (Nat.RecursiveIn.prec hb hs).of_eq
  intro n
  dsimp
  induction n.unpair.2 with
  | zero => rfl
  | succ k ih =>
    dsimp only
    rw [ih]
    simp

end OracleComputable

/-- A true oracle query, followed by primitive prime indexing and parity. -/
theorem pairedMask_oracleComputable (a X : ℕ → Bool) (ha : SelectorReducible a X) :
    OracleComputable X (pairedMask a) := by
  have hb : OracleComputable X (fun n => if a n then 1 else 0) := RecursiveIn.iff_nat.mp ha
  have hc : Primrec (fun n => Nat.count Nat.Prime n) := primrec_prime_count
  have hi : OracleComputable X (fun n => Nat.count Nat.Prime n / 2) :=
    OracleComputable.of_computable ((Primrec.nat_div.comp hc (Primrec.const 2)).to_comp)
  have hp : OracleComputable X (fun n => Nat.count Nat.Prime n % 2) :=
    OracleComputable.of_computable ((Primrec.nat_mod.comp hc (Primrec.const 2)).to_comp)
  exact (hb.comp hi).ncEq hp

/-- A total decoder of finite residue lists from native natural codes. -/
def decodeResidues (n : ℕ) : List ℕ := (Encodable.decode (α := List ℕ) n).getD []

@[simp] theorem decodeResidues_encode (d : List ℕ) : decodeResidues (Encodable.encode d) = d := by
  simp [decodeResidues]

theorem primrec_decodeResidues : Primrec decodeResidues :=
  Primrec.option_getD.comp Primrec.decode (Primrec.const [])

/-- Native oracle finite-loop construction; output codes are ordinary finite lists. -/
def residueLoop (f : ℕ → ℕ) (input : ℕ) (N : ℕ) : List ℕ :=
  Nat.rec [] (fun i xs => xs ++ [f (Nat.pair input i)]) N

theorem residueLoop_eq_ofFn (f : ℕ → ℕ) (input N : ℕ) :
    residueLoop f input N = List.ofFn (fun i : Fin N => f (Nat.pair input i.val)) := by
  induction N with
  | zero => rfl
  | succ N ih =>
    change residueLoop f input N ++ [f (Nat.pair input N)] = _
    rw [ih, List.ofFn_succ_last]
    rfl

/-- Every cell may query the oracle; primitive recursion certifies the complete bounded loop. -/
theorem residueLoop_oracleComputable {X : ℕ → Bool} {f : ℕ → ℕ}
    (hf : OracleComputable X f) :
    OracleComputable X (fun z => Encodable.encode (residueLoop f z.unpair.1 z.unpair.2)) := by
  have hcat : Computable (fun n : ℕ => Encodable.encode
      (decodeResidues n.unpair.1 ++ [n.unpair.2])) :=
    Primrec.encode.to_comp.comp ((Primrec.list_concat.comp
      (primrec_decodeResidues.comp (Primrec.fst.comp Primrec.unpair))
      (Primrec.snd.comp Primrec.unpair)).to_comp)
  have hstep : OracleComputable X (fun z => Encodable.encode
      (decodeResidues z.unpair.2.unpair.2 ++
        [f (Nat.pair z.unpair.1 z.unpair.2.unpair.1)])) := by
    exact (OracleComputable.of_computable hcat).comp
      ((OracleComputable.right.comp OracleComputable.right).pair
        (hf.comp (OracleComputable.left.pair
          (OracleComputable.left.comp OracleComputable.right)))) |>.of_eq
      (fun n => by simp)
  apply ((OracleComputable.const (Encodable.encode ([] : List ℕ))).ncRec hstep).of_eq
  intro n
  dsimp
  induction n.unpair.2 with
  | zero => rfl
  | succ k ih =>
    simp only [Nat.unpair_pair] at ih ⊢
    rw [ih, decodeResidues_encode]
    rfl

/-- Finite residue-list equality uses only bounded prime-coordinate tests. -/
def ResiduesEqual (d e : List ℕ) : Prop :=
  ∀ p < max d.length e.length, p.Prime → d.getD p 0 % p = e.getD p 0 % p

instance residuesEqual_decidable : DecidableRel ResiduesEqual := by
  unfold ResiduesEqual
  infer_instance

theorem residuesEqual_iff (d e : List ℕ) :
    ResiduesEqual d e ↔ finiteCodeValue d = finiteCodeValue e := by
  constructor
  · intro h
    funext p
    by_cases hp : p.val < max d.length e.length
    · apply (ZMod.natCast_eq_natCast_iff _ _ p.val).mpr
      exact h p.val hp p.property
    · have hd : d.length ≤ p.val := (le_max_left _ _).trans (Nat.le_of_not_gt hp)
      have he : e.length ≤ p.val := (le_max_right _ _).trans (Nat.le_of_not_gt hp)
      rw [finiteCodeValue_eq_zero d p hd, finiteCodeValue_eq_zero e p he]
  · intro h p _ hp
    have hh := congrArg (fun x : Ambient => (x ⟨p, hp⟩).val) h
    simpa only [finiteCodeValue, ZMod.val_natCast, ← List.getD_eq_getElem?_getD] using hh

theorem primrec_residuesEqual : PrimrecRel ResiduesEqual := by
  let dl : Primrec (fun z : ℕ × (List ℕ × List ℕ) => z.2.1) := Primrec.fst.comp Primrec.snd
  let el : Primrec (fun z : ℕ × (List ℕ × List ℕ) => z.2.2) := Primrec.snd.comp Primrec.snd
  have hr : PrimrecRel (fun p : ℕ => fun de : List ℕ × List ℕ =>
      p.Prime → de.1.getD p 0 % p = de.2.getD p 0 % p) :=
    ((primrec_prime_predicate.comp Primrec.fst).not.or
      (Primrec.eq.comp
        (Primrec.nat_mod.comp ((Primrec.list_getD 0).comp dl Primrec.fst) Primrec.fst)
        (Primrec.nat_mod.comp ((Primrec.list_getD 0).comp el Primrec.fst) Primrec.fst))).of_eq
          (fun _ => by simp only [or_iff_not_imp_left, not_not])
  exact hr.forall_mem_list.comp
    (Primrec.list_range.comp (Primrec.nat_max.comp (Primrec.list_length.comp Primrec.fst)
      (Primrec.list_length.comp Primrec.snd))) Primrec.id |>.of_eq
        (fun _ => by simp only [List.mem_range, id_eq, ResiduesEqual])

/-- The actual finite-support correction represented by one native list. -/
def finiteResidues (d : List ℕ) : finiteSupport := by
  refine ⟨finiteCodeValue d, ?_⟩
  apply (Set.finite_Iio d.length).preimage Subtype.val_injective.injOn |>.subset
  intro p hp
  by_contra hn
  exact hp (finiteCodeValue_eq_zero d p (Nat.le_of_not_gt hn))

abbrev NativeNormalCode := RationalCode × List ℕ

/-- The names denote the original ambient paired-prime group, with no abstract replacement. -/
def nativeNormalValue (a : ℕ → Bool) (c : NativeNormalCode) : pairedGroup a :=
  ⟨rationalSection (pairedSelector a) (RationalCode.value c.1) + finiteCodeValue c.2,
    (pairedGroup a).add_mem (rationalSection_mem _ _)
      (finiteSupport_le_preimage _ (finiteResidues c.2).property)⟩

theorem nativeNormalValue_surjective (a : ℕ → Bool) :
    Function.Surjective (nativeNormalValue a) := by
  intro x
  obtain ⟨r, d, hd⟩ := normalForm_exists (pairedSelector a) x
  obtain ⟨q, hq⟩ := RationalCode.value_surjective r
  obtain ⟨code, hc⟩ := finiteCodeValue_represents d
  refine ⟨(q, code), Subtype.ext ?_⟩
  change rationalSection (pairedSelector a) (RationalCode.value q) + finiteCodeValue code = x.val
  rw [hq, hc, ← hd]

def nativeNormalEqual (c e : NativeNormalCode) : Bool :=
  RationalCode.equal c.1 e.1 && decide (ResiduesEqual c.2 e.2)

theorem nativeNormalEqual_exact (a : ℕ → Bool) (c e : NativeNormalCode) :
    nativeNormalEqual c e = true ↔ nativeNormalValue a c = nativeNormalValue a e := by
  rw [nativeNormalEqual, Bool.and_eq_true, RationalCode.equal_iff, decide_eq_true_eq,
    residuesEqual_iff]
  constructor
  · rintro ⟨hr, hd⟩
    apply Subtype.ext
    change rationalSection _ _ + _ = rationalSection _ _ + _
    rw [hr, hd]
  · intro h
    have hh := normalForm_unique (pairedSelector_infinite a) _ _
      (finiteResidues c.2) (finiteResidues e.2) (congrArg Subtype.val h)
    exact ⟨hh.1, congrArg Subtype.val hh.2⟩

theorem primrec_nativeNormalEqual : Primrec₂ nativeNormalEqual :=
  Primrec.and.comp
    (RationalCode.primrec_equal.comp (Primrec.fst.comp Primrec.fst) (Primrec.fst.comp Primrec.snd))
    ((primrec_residuesEqual.comp (Primrec.snd.comp Primrec.fst)
      (Primrec.snd.comp Primrec.snd)).decide)

/-- Total decoding admits redundant raw natural codes, with native decidable equality. -/
def decodeNormalCode (n : ℕ) : NativeNormalCode :=
  (Encodable.decode (α := NativeNormalCode) n).getD default

@[simp] theorem decodeNormalCode_encode (c : NativeNormalCode) :
    decodeNormalCode (Encodable.encode c) = c := by
  rw [decodeNormalCode, Encodable.encodek]
  rfl

theorem primrec_decodeNormalCode : Primrec decodeNormalCode :=
  Primrec.option_getD.comp Primrec.decode (Primrec.const default)

/-- A primitive bound containing both torsion inputs and all cocycle denominator primes. -/
def normalAddBound (c e : NativeNormalCode) : ℕ :=
  max (max c.2.length e.2.length)
    (RationalCode.normalDenominator c.1 * RationalCode.normalDenominator e.1 + 1)

theorem primrec_normalAddBound : Primrec₂ normalAddBound :=
  Primrec.nat_max.comp
    (Primrec.nat_max.comp (Primrec.list_length.comp (Primrec.snd.comp Primrec.fst))
      (Primrec.list_length.comp (Primrec.snd.comp Primrec.snd)))
    (Primrec.succ.comp (Primrec.nat_mul.comp
      (RationalCode.primrec_normalDenominator.comp (Primrec.fst.comp Primrec.fst))
      (RationalCode.primrec_normalDenominator.comp (Primrec.fst.comp Primrec.snd))))

/-- One exact natural-number residue cell for normal-form addition. -/
def normalAddCell (a : ℕ → Bool) (z : ℕ) : ℕ :=
  let c := decodeNormalCode z.unpair.1.unpair.1
  let e := decodeNormalCode z.unpair.1.unpair.2
  let p := z.unpair.2
  (c.2.getD p 0 + e.2.getD p 0 + pairedMask a p *
    (RationalCode.primeResidue c.1 p + RationalCode.primeResidue e.1 p + p -
      RationalCode.primeResidue (RationalCode.add c.1 e.1) p)) % p

theorem normalAddCell_cast (a : ℕ → Bool) (c e : NativeNormalCode) (p : Prime) :
    (normalAddCell a (Nat.pair (Nat.pair (Encodable.encode c) (Encodable.encode e)) p.val) :
      Coordinate p) = finiteCodeValue c.2 p + finiteCodeValue e.2 p +
        sectionDefect (pairedSelector a) (RationalCode.value c.1) (RationalCode.value e.1) p := by
  have hb : RationalCode.primeResidue (RationalCode.add c.1 e.1) p.val ≤
      RationalCode.primeResidue c.1 p.val + RationalCode.primeResidue e.1 p.val + p.val :=
    (RationalCode.primeResidue_lt _ p.property).le.trans (Nat.le_add_left _ _)
  simp only [normalAddCell, Nat.unpair_pair, decodeNormalCode_encode, ZMod.natCast_mod,
    Nat.cast_add, Nat.cast_mul, Nat.cast_sub hb, ZMod.natCast_self, add_zero,
    RationalCode.primeResidue_cast, RationalCode.value_add]
  by_cases hp : p ∈ pairedSelector a
  · have hm := (pairedMask_exact a p).mpr hp
    simp only [hm, Nat.cast_one, one_mul, sectionDefect, Pi.sub_apply, Pi.add_apply,
      rationalSection, ite_eq_left hp, finiteCodeValue, ← List.getD_eq_getElem?_getD]
  · have hm : pairedMask a p.val = 0 := by
      have hn : pairedMask a p.val ≠ 1 := (pairedMask_exact a p).not.mpr hp
      have h01 : pairedMask a p.val = 0 ∨ pairedMask a p.val = 1 := by
        unfold pairedMask
        split_ifs <;> simp
      exact h01.resolve_right hn
    simp [hm, sectionDefect, rationalSection, hp, finiteCodeValue,
      ← List.getD_eq_getElem?_getD]

/-- The finite output correction for two raw natural normal-form codes. -/
def normalAddResidues (a : ℕ → Bool) (c e : NativeNormalCode) : List ℕ :=
  residueLoop (normalAddCell a) (Nat.pair (Encodable.encode c) (Encodable.encode e))
    (normalAddBound c e)

theorem normalAddResidues_exact (a : ℕ → Bool) (c e : NativeNormalCode) :
    finiteCodeValue (normalAddResidues a c e) =
      finiteCodeValue c.2 + finiteCodeValue e.2 +
        sectionDefect (pairedSelector a) (RationalCode.value c.1) (RationalCode.value e.1) := by
  funext p
  by_cases hp : p.val < normalAddBound c e
  · rw [normalAddResidues, residueLoop_eq_ofFn]
    simp only [finiteCodeValue, List.getElem?_ofFn, hp, dite_true, Option.getD_some]
    exact normalAddCell_cast a c e p
  · have hpN := Nat.le_of_not_gt hp
    have hc : c.2.length ≤ p.val :=
      (le_max_left _ _).trans ((le_max_left _ _).trans hpN)
    have he : e.2.length ≤ p.val :=
      (le_max_right _ _).trans ((le_max_left _ _).trans hpN)
    have hdef : sectionDefect (pairedSelector a) (RationalCode.value c.1)
        (RationalCode.value e.1) p = 0 := by
      by_contra hn
      have hdvd := sectionDefect_support (pairedSelector a)
        (RationalCode.value c.1) (RationalCode.value e.1) hn
      have hle := Nat.le_of_dvd
        (Nat.mul_pos (RationalCode.value c.1).den_pos (RationalCode.value e.1).den_pos) hdvd
      have hb := (le_max_right (max c.2.length e.2.length)
        (RationalCode.normalDenominator c.1 * RationalCode.normalDenominator e.1 + 1)).trans hpN
      rw [← (RationalCode.normal_fields c.1).2, ← (RationalCode.normal_fields e.1).2] at hb
      omega
    have hlen : (normalAddResidues a c e).length = normalAddBound c e := by
      rw [normalAddResidues, residueLoop_eq_ofFn, List.length_ofFn]
    rw [finiteCodeValue_eq_zero _ p (hlen.symm ▸ hpN)]
    simp only [Pi.add_apply, finiteCodeValue_eq_zero c.2 p hc,
      finiteCodeValue_eq_zero e.2 p he, hdef, add_zero]

def nativeNormalAdd (a : ℕ → Bool) (c e : NativeNormalCode) : NativeNormalCode :=
  (RationalCode.add c.1 e.1, normalAddResidues a c e)

theorem nativeNormalAdd_exact (a : ℕ → Bool) (c e : NativeNormalCode) :
    nativeNormalValue a (nativeNormalAdd a c e) = nativeNormalValue a c + nativeNormalValue a e := by
  apply Subtype.ext
  change rationalSection _ (RationalCode.value (RationalCode.add c.1 e.1)) +
    finiteCodeValue (normalAddResidues a c e) = _
  rw [RationalCode.value_add, normalAddResidues_exact]
  change rationalSection _ _ + (finiteCodeValue c.2 + finiteCodeValue e.2 +
    (rationalSection _ _ + rationalSection _ _ - rationalSection _ _)) =
    (rationalSection _ _ + finiteCodeValue c.2) + (rationalSection _ _ + finiteCodeValue e.2)
  abel

/-- Native oracle computation of the actual cocycle correction at one prime value. -/
theorem normalAddCell_oracleComputable (a X : ℕ → Bool) (ha : SelectorReducible a X) :
    OracleComputable X (normalAddCell a) := by
  let l : Primrec (fun z : ℕ => decodeNormalCode z.unpair.1.unpair.1) :=
    primrec_decodeNormalCode.comp
      ((Primrec.fst.comp Primrec.unpair).comp (Primrec.fst.comp Primrec.unpair))
  let r : Primrec (fun z : ℕ => decodeNormalCode z.unpair.1.unpair.2) :=
    primrec_decodeNormalCode.comp
      ((Primrec.snd.comp Primrec.unpair).comp (Primrec.fst.comp Primrec.unpair))
  let p : Primrec (fun z : ℕ => z.unpair.2) := Primrec.snd.comp Primrec.unpair
  let q := Primrec.fst.comp l
  let t := Primrec.fst.comp r
  have hb : Primrec (fun z : ℕ =>
      (decodeNormalCode z.unpair.1.unpair.1).2.getD z.unpair.2 0 +
        (decodeNormalCode z.unpair.1.unpair.2).2.getD z.unpair.2 0) :=
    Primrec.nat_add.comp ((Primrec.list_getD 0).comp (Primrec.snd.comp l) p)
      ((Primrec.list_getD 0).comp (Primrec.snd.comp r) p)
  have hd : Primrec (fun z : ℕ =>
      RationalCode.primeResidue (decodeNormalCode z.unpair.1.unpair.1).1 z.unpair.2 +
        RationalCode.primeResidue (decodeNormalCode z.unpair.1.unpair.2).1 z.unpair.2 + z.unpair.2 -
        RationalCode.primeResidue (RationalCode.add (decodeNormalCode z.unpair.1.unpair.1).1
          (decodeNormalCode z.unpair.1.unpair.2).1) z.unpair.2) :=
    Primrec.nat_sub.comp
      (Primrec.nat_add.comp (Primrec.nat_add.comp
        (RationalCode.primrec_primeResidue.comp q p)
        (RationalCode.primrec_primeResidue.comp t p)) p)
      (RationalCode.primrec_primeResidue.comp (RationalCode.primrec_add.comp q t) p)
  exact ((OracleComputable.of_computable hb.to_comp).ncAdd
    (((pairedMask_oracleComputable a X ha).comp (OracleComputable.of_computable p.to_comp)).mul
      (OracleComputable.of_computable hd.to_comp))).ncMod
        (OracleComputable.of_computable p.to_comp)

/-- Actual finite normal-form addition, encoded as a natural output. -/
def rawNormalAdd (a : ℕ → Bool) (i j : ℕ) : ℕ :=
  Encodable.encode (nativeNormalAdd a (decodeNormalCode i) (decodeNormalCode j))

def rawNormalEqual (i j : ℕ) : ℕ :=
  if nativeNormalEqual (decodeNormalCode i) (decodeNormalCode j) then 0 else 1

theorem rawNormalAdd_oracleComputable (a X : ℕ → Bool) (ha : SelectorReducible a X) :
    OracleComputable X (fun k => rawNormalAdd a k.unpair.1 k.unpair.2) := by
  let l : Primrec (fun z : ℕ => decodeNormalCode z.unpair.1) :=
    primrec_decodeNormalCode.comp (Primrec.fst.comp Primrec.unpair)
  let r : Primrec (fun z : ℕ => decodeNormalCode z.unpair.2) :=
    primrec_decodeNormalCode.comp (Primrec.snd.comp Primrec.unpair)
  have hq : OracleComputable X (fun z : ℕ => Encodable.encode
      (RationalCode.add (decodeNormalCode z.unpair.1).1 (decodeNormalCode z.unpair.2).1)) :=
    OracleComputable.of_computable (Primrec.encode.comp
      (RationalCode.primrec_add.comp (Primrec.fst.comp l) (Primrec.fst.comp r))).to_comp
  have hi : OracleComputable X (fun z : ℕ => Nat.pair
      (Encodable.encode (decodeNormalCode z.unpair.1))
      (Encodable.encode (decodeNormalCode z.unpair.2))) :=
    (OracleComputable.of_computable (Primrec.encode.comp l).to_comp).pair
      (OracleComputable.of_computable (Primrec.encode.comp r).to_comp)
  have hn : OracleComputable X (fun z : ℕ =>
      normalAddBound (decodeNormalCode z.unpair.1) (decodeNormalCode z.unpair.2)) :=
    OracleComputable.of_computable (primrec_normalAddBound.comp l r).to_comp
  have hd : OracleComputable X (fun z : ℕ => Encodable.encode (normalAddResidues a
      (decodeNormalCode z.unpair.1) (decodeNormalCode z.unpair.2))) := by
    apply ((residueLoop_oracleComputable (normalAddCell_oracleComputable a X ha)).comp
      (hi.pair hn)).of_eq
    intro z
    simp only [Nat.unpair_pair]
    rfl
  apply (hq.pair hd).of_eq
  intro z
  exact (Encodable.encode_prod_val _ _).symm

theorem rawNormalEqual_computable :
    Computable (fun k : ℕ => rawNormalEqual k.unpair.1 k.unpair.2) := by
  have he : Primrec (fun k : ℕ =>
      nativeNormalEqual (decodeNormalCode k.unpair.1) (decodeNormalCode k.unpair.2)) :=
    primrec_nativeNormalEqual.comp
      (primrec_decodeNormalCode.comp (Primrec.fst.comp Primrec.unpair))
      (primrec_decodeNormalCode.comp (Primrec.snd.comp Primrec.unpair))
  exact (Primrec.ite (Primrec.eq.comp he (Primrec.const true))
    (Primrec.const 0) (Primrec.const 1)).to_comp

/-- Genuine raw oracle codes for the original paired-prime group. -/
def pairedRawCodes (a X : ℕ → Bool) (ha : SelectorReducible a X) :
    OracleRawGroupCodes X (pairedGroup a) where
  names n := nativeNormalValue a (decodeNormalCode n)
  names_surjective := by
    intro x
    obtain ⟨c, hc⟩ := nativeNormalValue_surjective a x
    refine ⟨Encodable.encode c, ?_⟩
    change nativeNormalValue a (decodeNormalCode (Encodable.encode c)) = x
    rw [decodeNormalCode_encode]
    exact hc
  zero := Encodable.encode (((((0 : ℕ), (0 : ℕ)), (0 : ℕ)), ([] : List ℕ)) : NativeNormalCode)
  add := rawNormalAdd a
  equal := rawNormalEqual
  zero_spec := by
    rw [decodeNormalCode_encode]
    apply Subtype.ext
    change rationalSection (pairedSelector a) (RationalCode.value ((0,0),0)) +
      finiteCodeValue [] = 0
    have hr : RationalCode.value ((0,0),0) = 0 := by simp [RationalCode.value_eq,
      RationalCode.positive, RationalCode.negative, RationalCode.denominator]
    rw [hr, rationalSection_zero, zero_add]
    funext p
    simp [finiteCodeValue]
  add_spec i j := by
    change nativeNormalValue a (decodeNormalCode (Encodable.encode _)) = _
    rw [decodeNormalCode_encode]
    exact nativeNormalAdd_exact a _ _
  equal_spec i j := by
    have he := nativeNormalEqual_exact a (decodeNormalCode i) (decodeNormalCode j)
    cases hb : nativeNormalEqual (decodeNormalCode i) (decodeNormalCode j) <;>
      simp [rawNormalEqual, hb] at he ⊢
    · exact he
    · exact he
  add_computable := rawNormalAdd_oracleComputable a X ha
  equal_computable := OracleComputable.of_computable rawNormalEqual_computable

/-- Uniform construction from the genuine oracle reduction, with bijective natural names. -/
def pairedOracleCopy (a X : ℕ → Bool) (ha : SelectorReducible a X) :
    OracleGroupCopy X (pairedGroup a) :=
  (pairedRawCodes a X ha).toOracleGroupCopy

/-- Monograph 8.3: the exact oracle criterion for unmarked copies. -/
theorem paired_oracle_copy_iff (a X : ℕ → Bool) :
    Nonempty (OracleGroupCopy X (pairedGroup a)) ↔ SelectorReducible a X := by
  constructor
  · exact oracle_copy_exists_implies_selector_reducible a X
  · intro ha
    exact ⟨pairedOracleCopy a X ha⟩

end RealizationBoundaries
