import RealizationBoundaries.SearchEnumerableSpectrum

/-! # Equivalence of positive witness tests and actual oracle stage listings -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries
attribute [local instance] Classical.propDecidable

/-- An actual listing emits a finite list at every natural stage, with native
oracle computation of its encoded list and exact eventual membership. Repeated
emissions are permitted. -/
structure OracleStageListing (X : ℕ → Bool) (A : Set ℕ) where
  stage : ℕ → List ℕ
  stage_computable : OracleComputable X (fun s => Encodable.encode (stage s))
  stage_spec : ∀ n, n ∈ A ↔ ∃ s, n ∈ stage s

/-- A positive test result emits its candidate index plus one; zero is a blank. -/
def listingSuccessCell (test : ℕ → ℕ) (k : ℕ) : ℕ :=
  if test k.unpair.2 = 0 then k.unpair.2.unpair.1 + 1 else 0

/-- Remove blank emissions and undo the positive coding. -/
def cleanListing (L : List ℕ) : List ℕ :=
  L.filterMap (fun n => if n = 0 then none else some (n-1))

def searchStageListing (test : ℕ → ℕ) (s : ℕ) : List ℕ :=
  cleanListing (residueLoop (listingSuccessCell test) 0 s)

theorem searchStageListing_mem (test : ℕ → ℕ) (s n : ℕ) :
    n ∈ searchStageListing test s ↔
      ∃ k < s, k.unpair.1 = n ∧ test k = 0 := by
  constructor
  · intro hn
    obtain ⟨v, hv, hout⟩ := List.mem_filterMap.mp hn
    rw [residueLoop_eq_ofFn] at hv
    obtain ⟨i, hi⟩ := List.mem_ofFn.mp hv
    have hc : v = if test i.val = 0 then i.val.unpair.1+1 else 0 := by
      simpa only [listingSuccessCell, Nat.unpair_pair] using hi.symm
    by_cases ht : test i.val = 0
    · rw [hc, ite_eq_left ht] at hout
      have hn' : i.val.unpair.1 = n := by simpa using hout
      exact ⟨i.val, i.isLt, hn', ht⟩
    · rw [hc, ite_eq_right ht] at hout
      simp at hout
  · rintro ⟨k, hk, hkn, ht⟩
    apply List.mem_filterMap.mpr
    refine ⟨k.unpair.1+1, ?_, ?_⟩
    · rw [residueLoop_eq_ofFn]
      apply List.mem_ofFn.mpr
      refine ⟨⟨k, hk⟩, ?_⟩
      simp [listingSuccessCell, ht]
    · simp [hkn]

theorem listingSuccessCell_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) : OracleComputable X (listingSuccessCell test) := by
  have hs := (ht.comp OracleComputable.right).isZero
  have hv : OracleComputable X (fun k : ℕ => k.unpair.2.unpair.1+1) :=
    OracleComputable.of_computable ((Primrec.succ.comp
      ((Primrec.fst.comp Primrec.unpair).comp (Primrec.snd.comp Primrec.unpair))).to_comp)
  exact (hs.mul hv).of_eq (fun k => by
    simp only [listingSuccessCell]
    split <;> simp_all)

theorem primrec_cleanListing : Primrec cleanListing := by
  have hcell : Primrec (fun p : List ℕ × ℕ => if p.2 = 0 then none else some (p.2-1)) :=
    Primrec.ite (Primrec.eq.comp Primrec.snd (Primrec.const 0)) (Primrec.const none)
      (Primrec.option_some.comp (Primrec.nat_sub.comp Primrec.snd (Primrec.const 1)))
  exact Primrec.listFilterMap Primrec.id hcell

theorem searchStageListing_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) :
    OracleComputable X (fun s => Encodable.encode (searchStageListing test s)) := by
  have hloop := (residueLoop_oracleComputable (listingSuccessCell_computable ht)).comp
    ((OracleComputable.const 0).pair OracleComputable.id)
  have hclean : Computable (fun c : ℕ => Encodable.encode (cleanListing (decodeResidues c))) :=
    (Primrec.encode.comp (primrec_cleanListing.comp primrec_decodeResidues)).to_comp
  exact (OracleComputable.of_computable hclean).comp hloop |>.of_eq
    (fun s => by simp [searchStageListing])

/-- A total positive test gives a literal oracle-computable listing of exactly
its selected elements. Every witness appears at a finite stage. -/
def OracleSearchEnumeration.toStageListing {X : ℕ → Bool} {A : Set ℕ}
    (E : OracleSearchEnumeration X A) : OracleStageListing X A where
  stage := searchStageListing E.test
  stage_computable := searchStageListing_computable E.test_computable
  stage_spec := by
    intro n
    rw [E.test_spec]
    constructor
    · rintro ⟨t, ht⟩
      refine ⟨Nat.pair n t + 1, (searchStageListing_mem E.test _ _).mpr ?_⟩
      exact ⟨Nat.pair n t, Nat.lt_succ_self _, by simp, ht⟩
    · rintro ⟨s, hs⟩
      obtain ⟨k, _, hk, ht⟩ := (searchStageListing_mem E.test s n).mp hs
      refine ⟨k.unpair.2, ?_⟩
      rw [← hk, Nat.pair_unpair]
      exact ht

/-- Membership in each finite emitted list is an oracle-computable positive
candidate test, so listing semantics gives positive-witness semantics. -/
def OracleStageListing.toSearchEnumeration {X : ℕ → Bool} {A : Set ℕ}
    (L : OracleStageListing X A) : OracleSearchEnumeration X A where
  test := fun k => if k.unpair.1 ∈ L.stage k.unpair.2 then 0 else 1
  test_computable := by
    have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
    have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
    have hmem : Computable (fun k : ℕ =>
        if k.unpair.1 ∈ decodeResidues k.unpair.2 then 0 else 1) :=
      (Primrec.ite ((Primrec.eq.exists_mem_list).comp
          (primrec_decodeResidues.comp hr) hl) (Primrec.const 0) (Primrec.const 1)).to_comp.of_eq
        (fun k => by simp)
    exact (OracleComputable.of_computable hmem).comp
      (OracleComputable.left.pair (L.stage_computable.comp OracleComputable.right)) |>.of_eq
        (fun k => by simp)
  test_spec := by
    intro n
    simp only [Nat.unpair_pair, ite_eq_left_iff, one_ne_zero, imp_false, not_not]
    exact L.stage_spec n

/-- Explicit positive search and literal native oracle stage listings are the
same enumeration contract. -/
theorem oracle_searchEnumeration_iff_stageListing (X : ℕ → Bool) (A : Set ℕ) :
    Nonempty (OracleSearchEnumeration X A) ↔ Nonempty (OracleStageListing X A) := by
  constructor
  · rintro ⟨E⟩
    exact ⟨E.toStageListing⟩
  · rintro ⟨L⟩
    exact ⟨L.toSearchEnumeration⟩

/-- Monograph 3.3 with literal enumeration semantics and actual finite or
infinite computable copies of the selected prime subgroup. -/
theorem oracle_spectrum_copy_iff_stageListing (X : ℕ → Bool) (B : Set Prime) :
    HasOracleGroupCopy X (spectrumSubgroup B) ↔
      Nonempty (OracleStageListing X {n | primeAt n ∈ B}) :=
  (oracle_spectrum_copy_iff_searchEnumeration X B).trans
    (oracle_searchEnumeration_iff_stageListing X {n | primeAt n ∈ B})

end RealizationBoundaries
