import RealizationBoundaries.ComputableNormalCodes

/-! # Denominator-local selector queries for the actual cocycle arithmetic -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- The condition under which the cocycle cell can need a selector bit. -/
def localCocycleException (z : ℕ) : Prop :=
  z.unpair.2.Prime ∧ z.unpair.2 ∣
    RationalCode.normalDenominator (decodeNormalCode z.unpair.1.unpair.1).1 *
      RationalCode.normalDenominator (decodeNormalCode z.unpair.1.unpair.2).1

instance localCocycleException_decidable : DecidablePred localCocycleException := by
  unfold localCocycleException
  infer_instance

theorem primrec_localCocycleException : PrimrecPred localCocycleException := by
  let l : Primrec (fun z : ℕ => decodeNormalCode z.unpair.1.unpair.1) :=
    primrec_decodeNormalCode.comp
      ((Primrec.fst.comp Primrec.unpair).comp (Primrec.fst.comp Primrec.unpair))
  let r : Primrec (fun z : ℕ => decodeNormalCode z.unpair.1.unpair.2) :=
    primrec_decodeNormalCode.comp
      ((Primrec.snd.comp Primrec.unpair).comp (Primrec.fst.comp Primrec.unpair))
  let p : Primrec (fun z : ℕ => z.unpair.2) := Primrec.snd.comp Primrec.unpair
  exact (primrec_prime_predicate.comp p).and (primrec_nat_dvd.comp p
    (Primrec.nat_mul.comp
      (RationalCode.primrec_normalDenominator.comp (Primrec.fst.comp l))
      (RationalCode.primrec_normalDenominator.comp (Primrec.fst.comp r))))

/-- The selector-independent sum of the two finite corrections. -/
def normalAddBaseCell (z : ℕ) : ℕ :=
  ((decodeNormalCode z.unpair.1.unpair.1).2.getD z.unpair.2 0 +
    (decodeNormalCode z.unpair.1.unpair.2).2.getD z.unpair.2 0) % z.unpair.2

theorem primrec_normalAddBaseCell : Primrec normalAddBaseCell := by
  let l : Primrec (fun z : ℕ => decodeNormalCode z.unpair.1.unpair.1) :=
    primrec_decodeNormalCode.comp
      ((Primrec.fst.comp Primrec.unpair).comp (Primrec.fst.comp Primrec.unpair))
  let r : Primrec (fun z : ℕ => decodeNormalCode z.unpair.1.unpair.2) :=
    primrec_decodeNormalCode.comp
      ((Primrec.snd.comp Primrec.unpair).comp (Primrec.fst.comp Primrec.unpair))
  let p : Primrec (fun z : ℕ => z.unpair.2) := Primrec.snd.comp Primrec.unpair
  exact Primrec.nat_mod.comp
    (Primrec.nat_add.comp ((Primrec.list_getD 0).comp (Primrec.snd.comp l) p)
      ((Primrec.list_getD 0).comp (Primrec.snd.comp r) p)) p

/-- The old arithmetic cell takes one supplied bit and makes no oracle calls. -/
def normalAddCellUsingBit (b : Bool) (z : ℕ) : ℕ :=
  let c := decodeNormalCode z.unpair.1.unpair.1
  let e := decodeNormalCode z.unpair.1.unpair.2
  let p := z.unpair.2
  let mask := if (if b then 1 else 0) = Nat.count Nat.Prime p % 2 then 1 else 0
  (c.2.getD p 0 + e.2.getD p 0 + mask *
    (RationalCode.primeResidue c.1 p + RationalCode.primeResidue e.1 p + p -
      RationalCode.primeResidue (RationalCode.add c.1 e.1) p)) % p

/-- Exactly one selector lookup is supplied to an exceptional prime's cell.
All other cells are independent of the selector. -/
def localNormalAddCell (a : ℕ → Bool) (z : ℕ) : ℕ :=
  if localCocycleException z then
    normalAddCellUsingBit (a (Nat.count Nat.Prime z.unpair.2 / 2)) z
  else normalAddBaseCell z

theorem localNormalAddCell_eq (a : ℕ → Bool) (z : ℕ) :
    localNormalAddCell a z =
      if localCocycleException z then normalAddCell a z else normalAddBaseCell z := by
  rfl

/-- The optimized cell agrees with the old cell at every actual prime coordinate. -/
theorem localNormalAddCell_same_prime_residue (a : ℕ → Bool)
    (c e : NativeNormalCode) (p : Prime) :
    (localNormalAddCell a
      (Nat.pair (Nat.pair (Encodable.encode c) (Encodable.encode e)) p.val) : Coordinate p) =
    (normalAddCell a
      (Nat.pair (Nat.pair (Encodable.encode c) (Encodable.encode e)) p.val) : Coordinate p) := by
  rw [localNormalAddCell_eq]
  split_ifs with hx
  · rfl
  · have hn : ¬ p.val ∣ (RationalCode.value c.1).den * (RationalCode.value e.1).den := by
      intro hd
      apply hx
      simp only [localCocycleException, Nat.unpair_pair, decodeNormalCode_encode,
        ← (RationalCode.normal_fields c.1).2, ← (RationalCode.normal_fields e.1).2]
      exact ⟨p.property, hd⟩
    have hzero : sectionDefect (pairedSelector a) (RationalCode.value c.1)
        (RationalCode.value e.1) p = 0 := by
      by_contra hz
      exact hn (sectionDefect_support (pairedSelector a) _ _ hz)
    rw [normalAddCell_cast, hzero, add_zero]
    simp only [normalAddBaseCell, Nat.unpair_pair, decodeNormalCode_encode,
      ZMod.natCast_mod, Nat.cast_add, finiteCodeValue, ← List.getD_eq_getElem?_getD]

namespace OracleComputable
variable {X : ℕ → Bool} {f g : ℕ → ℕ}

/-- Primitive input predicates may choose between genuine oracle computations. -/
theorem localIte {P : ℕ → Prop} [DecidablePred P] (hP : PrimrecPred P)
    (hf : OracleComputable X f) (hg : OracleComputable X g) :
    OracleComputable X (fun n => if P n then f n else g n) := by
  have hs : Computable (fun n : ℕ => if P n.unpair.1
      then n.unpair.2.unpair.1 else n.unpair.2.unpair.2) :=
    (Primrec.ite (hP.comp (Primrec.fst.comp Primrec.unpair))
      ((Primrec.fst.comp Primrec.unpair).comp (Primrec.snd.comp Primrec.unpair))
      ((Primrec.snd.comp Primrec.unpair).comp (Primrec.snd.comp Primrec.unpair))).to_comp
  exact (of_computable hs).comp (id.pair (hf.pair hg)) |>.of_eq (fun n => by simp)

end OracleComputable

theorem localNormalAddCell_oracleComputable (a X : ℕ → Bool) (ha : SelectorReducible a X) :
    OracleComputable X (localNormalAddCell a) :=
  ((normalAddCell_oracleComputable a X ha).localIte primrec_localCocycleException
    (OracleComputable.of_computable primrec_normalAddBaseCell.to_comp)).of_eq
      (fun z => (localNormalAddCell_eq a z).symm)

/-- Instrumented cell: the trace records the prime whose single bit was looked up.
A composite or a non-denominator prime has an empty trace. -/
def recordedLocalCell (a : ℕ → Bool) (z : ℕ) : ℕ × List ℕ :=
  if localCocycleException z then
    (normalAddCellUsingBit (a (Nat.count Nat.Prime z.unpair.2 / 2)) z, [z.unpair.2])
  else (normalAddBaseCell z, [])

theorem recordedLocalCell_value (a : ℕ → Bool) (z : ℕ) :
    (recordedLocalCell a z).1 = localNormalAddCell a z := by
  unfold recordedLocalCell localNormalAddCell
  split <;> rfl

theorem recordedLocalCell_query_count (a : ℕ → Bool) (z : ℕ) :
    (recordedLocalCell a z).2.length = if localCocycleException z then 1 else 0 := by
  unfold recordedLocalCell
  split <;> rfl

/-- The exact finite prime-labelled query schedule for the optimized correction. -/
def localCocycleQuerySchedule (input N : ℕ) : List ℕ :=
  (List.range N).filter (fun p => decide (localCocycleException (Nat.pair input p)))

theorem localCocycleQuerySchedule_nodup (input N : ℕ) :
    (localCocycleQuerySchedule input N).Nodup :=
  List.nodup_range.filter _

theorem localCocycleQuerySchedule_length_le (input N : ℕ) :
    (localCocycleQuerySchedule input N).length ≤ N := by
  exact (List.length_filter_le _ _).trans_eq (List.length_range (n := N))

/-- At the complete correction bound the schedule consists exactly of all prime
divisors of the denominator product, each once. -/
theorem localCocycleQuerySchedule_mem (c e : NativeNormalCode) (p : ℕ) :
    p ∈ localCocycleQuerySchedule (Nat.pair (Encodable.encode c) (Encodable.encode e))
      (normalAddBound c e) ↔
      p.Prime ∧ p ∣ (RationalCode.value c.1).den * (RationalCode.value e.1).den := by
  simp only [localCocycleQuerySchedule, List.mem_filter, List.mem_range, decide_eq_true_eq,
    localCocycleException, Nat.unpair_pair, decodeNormalCode_encode,
    ← (RationalCode.normal_fields c.1).2, ← (RationalCode.normal_fields e.1).2]
  constructor
  · exact fun h => h.2
  · intro h
    refine ⟨?_, h⟩
    have hp := Nat.le_of_dvd
      (Nat.mul_pos (RationalCode.value c.1).den_pos (RationalCode.value e.1).den_pos) h.2
    change p < normalAddBound c e
    unfold normalAddBound
    rw [← (RationalCode.normal_fields c.1).2, ← (RationalCode.normal_fields e.1).2]
    exact lt_of_le_of_lt hp (lt_of_lt_of_le (Nat.lt_succ_self _) (le_max_right _ _))

/-- The complete optimized finite correction uses the checked finite native loop. -/
def localNormalAddResidues (a : ℕ → Bool) (c e : NativeNormalCode) : List ℕ :=
  residueLoop (localNormalAddCell a) (Nat.pair (Encodable.encode c) (Encodable.encode e))
    (normalAddBound c e)

theorem localNormalAddResidues_same (a : ℕ → Bool) (c e : NativeNormalCode) :
    finiteCodeValue (localNormalAddResidues a c e) = finiteCodeValue (normalAddResidues a c e) := by
  funext p
  by_cases hp : p.val < normalAddBound c e
  · simp only [localNormalAddResidues, normalAddResidues, residueLoop_eq_ofFn,
      finiteCodeValue, List.getElem?_ofFn, hp, dite_true, Option.getD_some]
    exact localNormalAddCell_same_prime_residue a c e p
  · have hl : (localNormalAddResidues a c e).length = normalAddBound c e := by
      rw [localNormalAddResidues, residueLoop_eq_ofFn, List.length_ofFn]
    have hr : (normalAddResidues a c e).length = normalAddBound c e := by
      rw [normalAddResidues, residueLoop_eq_ofFn, List.length_ofFn]
    rw [finiteCodeValue_eq_zero _ p (hl.symm ▸ Nat.le_of_not_gt hp),
      finiteCodeValue_eq_zero _ p (hr.symm ▸ Nat.le_of_not_gt hp)]

/-- The optimized finite normal form performs the identical actual group addition. -/
theorem localNormalAdd_correct (a : ℕ → Bool) (c e : NativeNormalCode) :
    nativeNormalValue a (RationalCode.add c.1 e.1, localNormalAddResidues a c e) =
      nativeNormalValue a c + nativeNormalValue a e := by
  have h : nativeNormalValue a (RationalCode.add c.1 e.1, localNormalAddResidues a c e) =
      nativeNormalValue a (nativeNormalAdd a c e) := by
    apply Subtype.ext
    change rationalSection _ _ + finiteCodeValue (localNormalAddResidues a c e) = _
    rw [localNormalAddResidues_same]
    rfl
  exact h.trans (nativeNormalAdd_exact a c e)

/-- The optimized full bounded loop has genuine native oracle semantics. -/
theorem localNormalAdd_loop_oracleComputable (a X : ℕ → Bool) (ha : SelectorReducible a X) :
    OracleComputable X (fun z => Encodable.encode
      (residueLoop (localNormalAddCell a) z.unpair.1 z.unpair.2)) :=
  residueLoop_oracleComputable (localNormalAddCell_oracleComputable a X ha)

end RealizationBoundaries
