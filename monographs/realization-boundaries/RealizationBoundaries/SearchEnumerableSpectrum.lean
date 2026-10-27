import RealizationBoundaries.ComputableNormalCodes
import RealizationBoundaries.SpectrumComputability

/-!
# Actual spectrum copies from positive enumerable witnesses

The enumeration contract is a total oracle-computable candidate test with an
existential natural witness. It neither decides negative membership nor assumes
that a classical selector definition is computable.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 1000000
noncomputable section
open scoped BigOperators
namespace RealizationBoundaries
attribute [local instance] Classical.propDecidable

/-- Standard positive-search enumeration semantics. -/
structure OracleSearchEnumeration (X : ℕ → Bool) (A : Set ℕ) where
  test : ℕ → ℕ
  test_computable : OracleComputable X test
  test_spec : ∀ n, n ∈ A ↔ ∃ t, test (Nat.pair n t) = 0

/-- Product of the first `s` candidate-test results; zero means discovered. -/
def discoveryProduct (test : ℕ → ℕ) (n s : ℕ) : ℕ :=
  Nat.rec 1 (fun t r => r * test (Nat.pair n t)) s

theorem discoveryProduct_zero_iff (test : ℕ → ℕ) (n s : ℕ) :
    discoveryProduct test n s = 0 ↔ ∃ t < s, test (Nat.pair n t) = 0 := by
  induction s with
  | zero => simp [discoveryProduct]
  | succ s ih =>
    change discoveryProduct test n s * test (Nat.pair n s) = 0 ↔ _
    rw [mul_eq_zero, ih]
    constructor
    · rintro (⟨t, ht, he⟩ | he)
      · exact ⟨t, Nat.lt_succ_of_lt ht, he⟩
      · exact ⟨s, Nat.lt_succ_self s, he⟩
    · rintro ⟨t, ht, he⟩
      rcases Nat.lt_succ_iff_lt_or_eq.mp ht with ht | rfl
      · exact Or.inl ⟨t, ht, he⟩
      · exact Or.inr he

theorem discoveryProduct_zero_mono (test : ℕ → ℕ) (n : ℕ) {s t : ℕ}
    (hst : s ≤ t) (hs : discoveryProduct test n s = 0) :
    discoveryProduct test n t = 0 := by
  obtain ⟨k, hk, he⟩ := (discoveryProduct_zero_iff test n s).mp hs
  exact (discoveryProduct_zero_iff test n t).mpr ⟨k, hk.trans_le hst, he⟩

theorem discoveryProduct_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) :
    OracleComputable X (fun k => discoveryProduct test k.unpair.1 k.unpair.2) := by
  have he := ht.comp (OracleComputable.left.pair
    (OracleComputable.left.comp OracleComputable.right))
  exact OracleComputable.prec (step := fun n t r => r * test (Nat.pair n t))
    (OracleComputable.const 1) ((OracleComputable.right.comp OracleComputable.right).mul he)

/-- Raw code is a stage together with a finite residue list. A cell is admitted
only after that prime's positive membership witness has actually appeared. -/
def spectrumDiscoveryCell (test : ℕ → ℕ) (k : ℕ) : ℕ :=
  if discoveryProduct test (Nat.count Nat.Prime k.unpair.2) k.unpair.1.unpair.1 = 0
  then (decodeResidues k.unpair.1.unpair.2).getD k.unpair.2 0 else 0

def spectrumDiscoveryResidues (test : ℕ → ℕ) (c : ℕ) : List ℕ :=
  residueLoop (spectrumDiscoveryCell test) c (decodeResidues c.unpair.2).length

theorem spectrumDiscoveryResidues_formula (test : ℕ → ℕ) (c : ℕ) (p : Prime) :
    finiteCodeValue (spectrumDiscoveryResidues test c) p =
      if discoveryProduct test (Nat.count Nat.Prime p.val) c.unpair.1 = 0
      then finiteCodeValue (decodeResidues c.unpair.2) p else 0 := by
  by_cases hp : p.val < (decodeResidues c.unpair.2).length
  · rw [spectrumDiscoveryResidues, residueLoop_eq_ofFn]
    simp only [finiteCodeValue, List.getElem?_ofFn, hp, dite_true, Option.getD_some]
    simp only [spectrumDiscoveryCell, Nat.unpair_pair]
    split <;> simp [← List.getD_eq_getElem?_getD]
  · have hl : (spectrumDiscoveryResidues test c).length = (decodeResidues c.unpair.2).length := by
      rw [spectrumDiscoveryResidues, residueLoop_eq_ofFn, List.length_ofFn]
    rw [finiteCodeValue_eq_zero _ p (hl.symm ▸ Nat.le_of_not_gt hp),
      finiteCodeValue_eq_zero _ p (Nat.le_of_not_gt hp)]
    split <;> rfl

/-- Every raw name denotes an element of the actual selected subgroup. -/
def spectrumDiscoveryValue {X : ℕ → Bool} {B : Set Prime}
    (E : OracleSearchEnumeration X {n | primeAt n ∈ B}) (c : ℕ) : spectrumSubgroup B := by
  refine ⟨finiteResidues (spectrumDiscoveryResidues E.test c), ?_⟩
  intro p hp
  have hseen : discoveryProduct E.test (Nat.count Nat.Prime p.val) c.unpair.1 = 0 := by
    by_contra hn
    exact hp (by simp [finiteResidues, spectrumDiscoveryResidues_formula, hn])
  obtain ⟨t, _, ht⟩ := (discoveryProduct_zero_iff _ _ _).mp hseen
  have hb := (E.test_spec (Nat.count Nat.Prime p.val)).mpr ⟨t, ht⟩
  have hindex : primeAt (Nat.count Nat.Prime p.val) = p := Subtype.ext (Nat.nth_count p.property)
  simpa only [Set.mem_ofPred_eq, hindex] using hb

theorem spectrumDiscoveryCell_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) : OracleComputable X (spectrumDiscoveryCell test) := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have hi := OracleComputable.of_computable (X := X)
    (primrec_prime_count.comp hr).to_comp
  have hs := OracleComputable.of_computable (X := X) (hl.comp hl).to_comp
  have hz := ((discoveryProduct_computable ht).comp (hi.pair hs)).isZero
  have hd : OracleComputable X (fun k : ℕ => (decodeResidues k.unpair.1.unpair.2).getD k.unpair.2 0) :=
    OracleComputable.of_computable (((Primrec.list_getD 0).comp
      (primrec_decodeResidues.comp (hr.comp hl)) hr).to_comp)
  exact (hz.mul hd).of_eq (fun k => by
    simp only [spectrumDiscoveryCell]
    split <;> simp_all)

theorem spectrumDiscoveryResidues_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) :
    OracleComputable X (fun c => Encodable.encode (spectrumDiscoveryResidues test c)) := by
  have hlen : Computable (fun c : ℕ => (decodeResidues c.unpair.2).length) :=
    (Primrec.list_length.comp (primrec_decodeResidues.comp (Primrec.snd.comp Primrec.unpair))).to_comp
  exact (residueLoop_oracleComputable (spectrumDiscoveryCell_computable ht)).comp
    (OracleComputable.id.pair (OracleComputable.of_computable hlen)) |>.of_eq
      (fun c => by simp [spectrumDiscoveryResidues])

/-- Positive enumeration witnesses eventually admit every finitely supported
selected vector. No membership decision for an undiscovered prime is needed. -/
theorem spectrumDiscoveryValue_surjective {X : ℕ → Bool} {B : Set Prime}
    (E : OracleSearchEnumeration X {n | primeAt n ∈ B}) :
    Function.Surjective (spectrumDiscoveryValue E) := by
  classical
  intro x
  obtain ⟨d, hd⟩ := finiteCodeValue_represents x.val
  let F := x.val.property.toFinset
  have hw : ∀ p : {p : Prime // p ∈ F},
      ∃ t, E.test (Nat.pair (Nat.count Nat.Prime p.val.val) t) = 0 := by
    intro p
    have hp : p.val ∈ support x.val.val := x.val.property.mem_toFinset.mp p.property
    have hB : p.val ∈ B := x.property hp
    apply (E.test_spec (Nat.count Nat.Prime p.val.val)).mp
    have he : primeAt (Nat.count Nat.Prime p.val.val) = p.val :=
      Subtype.ext (Nat.nth_count p.val.property)
    change primeAt (Nat.count Nat.Prime p.val.val) ∈ B
    rw [he]
    exact hB
  choose w hw using hw
  let s := Finset.univ.sup (fun p : {p : Prime // p ∈ F} => w p + 1)
  refine ⟨Nat.pair s (Encodable.encode d), ?_⟩
  apply Subtype.ext
  apply Subtype.ext
  funext p
  change finiteCodeValue (spectrumDiscoveryResidues E.test (Nat.pair s (Encodable.encode d))) p = x.val.val p
  rw [spectrumDiscoveryResidues_formula]
  simp only [Nat.unpair_pair, decodeResidues_encode]
  by_cases hp : x.val.val p = 0
  · rw [hd]
    split <;> simp [hp]
  · have hpF : p ∈ F := x.val.property.mem_toFinset.mpr hp
    have hbound : w ⟨p, hpF⟩ < s := by
      have hb : w ⟨p, hpF⟩ + 1 ≤ s := Finset.le_sup (f := fun q : {p : Prime // p ∈ F} => w q + 1)
        (Finset.mem_univ (⟨p, hpF⟩ : {p : Prime // p ∈ F}))
      omega
    have hs : discoveryProduct E.test (Nat.count Nat.Prime p.val) s = 0 :=
      (discoveryProduct_zero_iff _ _ _).mpr ⟨w ⟨p, hpF⟩, hbound, hw ⟨p, hpF⟩⟩
    rw [ite_eq_left hs, hd]

/-- One cell of addition uses only the two already discovered finite vectors. -/
def spectrumDiscoveryAddCell (test : ℕ → ℕ) (k : ℕ) : ℕ :=
  spectrumDiscoveryCell test (Nat.pair k.unpair.1.unpair.1 k.unpair.2) +
    spectrumDiscoveryCell test (Nat.pair k.unpair.1.unpair.2 k.unpair.2)

def spectrumDiscoveryAddResidues (test : ℕ → ℕ) (c d : ℕ) : List ℕ :=
  residueLoop (spectrumDiscoveryAddCell test) (Nat.pair c d)
    (max (decodeResidues c.unpair.2).length (decodeResidues d.unpair.2).length)

def spectrumDiscoveryAdd (test : ℕ → ℕ) (c d : ℕ) : ℕ :=
  Nat.pair (max c.unpair.1 d.unpair.1)
    (Encodable.encode (spectrumDiscoveryAddResidues test c d))

theorem spectrumDiscoveryAddResidues_exact (test : ℕ → ℕ) (c d : ℕ) :
    finiteCodeValue (spectrumDiscoveryAddResidues test c d) =
      finiteCodeValue (spectrumDiscoveryResidues test c) +
        finiteCodeValue (spectrumDiscoveryResidues test d) := by
  funext p
  by_cases hp : p.val < max (decodeResidues c.unpair.2).length (decodeResidues d.unpair.2).length
  · rw [spectrumDiscoveryAddResidues, residueLoop_eq_ofFn]
    simp only [finiteCodeValue, List.getElem?_ofFn, hp, dite_true, Option.getD_some]
    simp only [spectrumDiscoveryAddCell, Nat.unpair_pair]
    rw [Nat.cast_add]
    change (spectrumDiscoveryCell test (Nat.pair c p.val) : Coordinate p) +
      (spectrumDiscoveryCell test (Nat.pair d p.val) : Coordinate p) = _
    rw [Pi.add_apply, spectrumDiscoveryResidues_formula, spectrumDiscoveryResidues_formula]
    simp only [spectrumDiscoveryCell, Nat.unpair_pair]
    split <;> split <;> simp [finiteCodeValue, ← List.getD_eq_getElem?_getD]
  · have hc : (decodeResidues c.unpair.2).length ≤ p.val := (le_max_left _ _).trans (Nat.le_of_not_gt hp)
    have hd : (decodeResidues d.unpair.2).length ≤ p.val := (le_max_right _ _).trans (Nat.le_of_not_gt hp)
    have hlen : (spectrumDiscoveryAddResidues test c d).length =
        max (decodeResidues c.unpair.2).length (decodeResidues d.unpair.2).length := by
      rw [spectrumDiscoveryAddResidues, residueLoop_eq_ofFn, List.length_ofFn]
    rw [finiteCodeValue_eq_zero _ p (hlen.symm ▸ Nat.le_of_not_gt hp)]
    rw [Pi.add_apply, spectrumDiscoveryResidues_formula, spectrumDiscoveryResidues_formula,
      finiteCodeValue_eq_zero _ p hc, finiteCodeValue_eq_zero _ p hd]
    split <;> split <;> simp

theorem spectrumDiscoveryValue_add {X : ℕ → Bool} {B : Set Prime}
    (E : OracleSearchEnumeration X {n | primeAt n ∈ B}) (c d : ℕ) :
    spectrumDiscoveryValue E (spectrumDiscoveryAdd E.test c d) =
      spectrumDiscoveryValue E c + spectrumDiscoveryValue E d := by
  apply Subtype.ext
  apply Subtype.ext
  funext p
  change finiteCodeValue (spectrumDiscoveryResidues E.test (spectrumDiscoveryAdd E.test c d)) p = _
  rw [spectrumDiscoveryResidues_formula]
  simp only [spectrumDiscoveryAdd, Nat.unpair_pair, decodeResidues_encode]
  rw [spectrumDiscoveryAddResidues_exact]
  by_cases hs : discoveryProduct E.test (Nat.count Nat.Prime p.val) (max c.unpair.1 d.unpair.1) = 0
  · rw [ite_eq_left hs]
    rfl
  · rw [ite_eq_right hs]
    have hc : discoveryProduct E.test (Nat.count Nat.Prime p.val) c.unpair.1 ≠ 0 :=
      fun h => hs (discoveryProduct_zero_mono _ _ (le_max_left _ _) h)
    have hd : discoveryProduct E.test (Nat.count Nat.Prime p.val) d.unpair.1 ≠ 0 :=
      fun h => hs (discoveryProduct_zero_mono _ _ (le_max_right _ _) h)
    change 0 = finiteCodeValue (spectrumDiscoveryResidues E.test c) p +
      finiteCodeValue (spectrumDiscoveryResidues E.test d) p
    rw [spectrumDiscoveryResidues_formula, spectrumDiscoveryResidues_formula, ite_eq_right hc, ite_eq_right hd, add_zero]

theorem spectrumDiscoveryAddCell_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) : OracleComputable X (spectrumDiscoveryAddCell test) := by
  have hcell := spectrumDiscoveryCell_computable ht
  exact ((hcell.comp ((OracleComputable.left.comp OracleComputable.left).pair OracleComputable.right)).add
    (hcell.comp ((OracleComputable.right.comp OracleComputable.left).pair OracleComputable.right)))

theorem spectrumDiscoveryAdd_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) :
    OracleComputable X (fun k => spectrumDiscoveryAdd test k.unpair.1 k.unpair.2) := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have hlen : Computable (fun k : ℕ =>
      max (decodeResidues k.unpair.1.unpair.2).length (decodeResidues k.unpair.2.unpair.2).length) :=
    (Primrec.nat_max.comp
      (Primrec.list_length.comp (primrec_decodeResidues.comp (hr.comp hl)))
      (Primrec.list_length.comp (primrec_decodeResidues.comp (hr.comp hr)))).to_comp
  have hmax : Computable (fun k : ℕ => max k.unpair.1.unpair.1 k.unpair.2.unpair.1) :=
    (Primrec.nat_max.comp (hl.comp hl) (hl.comp hr)).to_comp
  have hloop := (residueLoop_oracleComputable (spectrumDiscoveryAddCell_computable ht)).comp
    (OracleComputable.id.pair (OracleComputable.of_computable hlen))
  exact ((OracleComputable.of_computable hmax).pair hloop).of_eq
    (fun k => by simp [spectrumDiscoveryAdd, spectrumDiscoveryAddResidues])

def spectrumDiscoveryEqual (test : ℕ → ℕ) (c d : ℕ) : ℕ :=
  if ResiduesEqual (spectrumDiscoveryResidues test c) (spectrumDiscoveryResidues test d) then 0 else 1

theorem spectrumDiscoveryEqual_exact {X : ℕ → Bool} {B : Set Prime}
    (E : OracleSearchEnumeration X {n | primeAt n ∈ B}) (c d : ℕ) :
    spectrumDiscoveryEqual E.test c d = 0 ↔ spectrumDiscoveryValue E c = spectrumDiscoveryValue E d := by
  simp only [spectrumDiscoveryEqual, ite_eq_left_iff, one_ne_zero, imp_false, not_not,
    residuesEqual_iff, Subtype.ext_iff]
  rfl

theorem spectrumDiscoveryEqual_computable {X : ℕ → Bool} {test : ℕ → ℕ}
    (ht : OracleComputable X test) :
    OracleComputable X (fun k => spectrumDiscoveryEqual test k.unpair.1 k.unpair.2) := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have he : Computable (fun k : ℕ =>
      if ResiduesEqual (decodeResidues k.unpair.1) (decodeResidues k.unpair.2) then 0 else 1) :=
    (Primrec.ite (primrec_residuesEqual.comp (primrec_decodeResidues.comp hl)
      (primrec_decodeResidues.comp hr)) (Primrec.const 0) (Primrec.const 1)).to_comp
  have hm := spectrumDiscoveryResidues_computable ht
  exact (OracleComputable.of_computable he).comp
    ((hm.comp OracleComputable.left).pair (hm.comp OracleComputable.right)) |>.of_eq
      (fun k => by simp [spectrumDiscoveryEqual])

/-- The complete raw-code presentation has proved surjectivity, exact equality,
and native oracle algorithms for both equality and addition. -/
def spectrumDiscoveryRawCodes {X : ℕ → Bool} {B : Set Prime}
    (E : OracleSearchEnumeration X {n | primeAt n ∈ B}) : OracleRawGroupCodes X (spectrumSubgroup B) where
  names := spectrumDiscoveryValue E
  names_surjective := spectrumDiscoveryValue_surjective E
  zero := Nat.pair 0 (Encodable.encode ([] : List ℕ))
  add := spectrumDiscoveryAdd E.test
  equal := spectrumDiscoveryEqual E.test
  zero_spec := by
    apply Subtype.ext
    apply Subtype.ext
    funext p
    change finiteCodeValue (spectrumDiscoveryResidues E.test (Nat.pair 0 (Encodable.encode ([] : List ℕ)))) p = 0
    rw [spectrumDiscoveryResidues_formula]
    simp [discoveryProduct]
  add_spec := spectrumDiscoveryValue_add E
  equal_spec := spectrumDiscoveryEqual_exact E
  add_computable := spectrumDiscoveryAdd_computable E.test_computable
  equal_computable := spectrumDiscoveryEqual_computable E.test_computable

/-- An infinite selected direct sum obtains an actual bijective Nat-domain copy
from positive enumeration witnesses, with no membership oracle for the selector. -/
theorem oracle_spectrum_copy_of_searchEnumeration {X : ℕ → Bool} {B : Set Prime}
    [Infinite (spectrumSubgroup B)]
    (E : OracleSearchEnumeration X {n | primeAt n ∈ B}) :
    Nonempty (OracleGroupCopy X (spectrumSubgroup B)) :=
  (spectrumDiscoveryRawCodes E).oracleGroupCopy_of_rawCodes

/-- The explicit witness-test semantics implies the native partial-domain
semantics by actual oracle minimization. No converse normal form is assumed. -/
theorem OracleSearchEnumeration.toOracleEnumerable {X : ℕ → Bool} {A : Set ℕ}
    (E : OracleSearchEnumeration X A) : OracleEnumerable X A := by
  obtain ⟨f, hf, hdom⟩ := oracleEnumerable_of_test X E.test E.test_computable
  exact ⟨f, hf, fun n => (hdom n).trans (E.test_spec n).symm⟩

/-- A fixed finite set has a total ordinary candidate test. This does not infer
when a finite enumeration has stopped. -/
def finiteSearchEnumeration (X : ℕ → Bool) (A : Set ℕ) (hA : A.Finite) :
    OracleSearchEnumeration X A where
  test := fun k => if k.unpair.1 ∈ A then 0 else 1
  test_computable := OracleComputable.of_computable
    ((Primrec.ite ((finite_set_primrec_membership A hA).comp
      (Primrec.fst.comp Primrec.unpair)) (Primrec.const 0) (Primrec.const 1)).to_comp)
  test_spec := by
    intro n
    simp

/-- Candidate positive torsion tests give the witness-test enumeration semantics
from an actual infinite copy, rather than only an abstract partial domain. -/
def spectrumSearchEnumeration_of_copy (X : ℕ → Bool) (B : Set Prime)
    (c : OracleGroupCopy X (spectrumSubgroup B)) :
    OracleSearchEnumeration X {n | primeAt n ∈ B} where
  test := c.torsionTest
  test_computable := c.torsionTest_computable
  test_spec := by
    intro n
    constructor
    · intro hn
      obtain ⟨x, hx⟩ := (spectrumSubgroup_hasPrimeTorsion_iff B (primeAt n)).mpr hn
      refine ⟨c.names.symm x, (c.torsionTest_correct n _).mpr ?_⟩
      simpa only [c.names.apply_symm_apply] using hx
    · rintro ⟨t, ht⟩
      exact (spectrumSubgroup_hasPrimeTorsion_iff B (primeAt n)).mp
        ⟨c.names t, (c.torsionTest_correct n t).mp ht⟩

/-- Finite and infinite copied domains both provide positive enumeration tests. -/
theorem spectrumSearchEnumeration_of_any_copy (X : ℕ → Bool) (B : Set Prime)
    (h : HasOracleGroupCopy X (spectrumSubgroup B)) :
    Nonempty (OracleSearchEnumeration X {n | primeAt n ∈ B}) := by
  rcases h with hf | hi
  · obtain ⟨c⟩ := hf
    let : Finite (spectrumSubgroup B) := Finite.of_equiv (Fin c.size) c.names
    have hA : {n | primeAt n ∈ B}.Finite := by
      simpa only [spectrumSubgroup_hasPrimeTorsion_iff] using
        finite_group_primeSpectrum_indices (spectrumSubgroup B)
    exact ⟨finiteSearchEnumeration X _ hA⟩
  · obtain ⟨c⟩ := hi
    exact ⟨spectrumSearchEnumeration_of_copy X B c⟩

/-- Positive enumeration gives an actual copy in the finite-or-infinite naming
convention. The finite branch uses its fixed finite table nonuniformly. -/
theorem oracle_any_spectrum_copy_of_searchEnumeration (X : ℕ → Bool) (B : Set Prime)
    (E : OracleSearchEnumeration X {n | primeAt n ∈ B}) :
    HasOracleGroupCopy X (spectrumSubgroup B) := by
  rcases finite_or_infinite (spectrumSubgroup B) with hfinite | hinfinite
  · let := hfinite
    exact hasOracleGroupCopy_of_finite X _
  · let := hinfinite
    exact Or.inr (oracle_spectrum_copy_of_searchEnumeration E)

/-- Exact prime-spectrum criterion with explicit standard positive-search
semantics: finite and infinite copied domains are both covered. -/
theorem oracle_spectrum_copy_iff_searchEnumeration (X : ℕ → Bool) (B : Set Prime) :
    HasOracleGroupCopy X (spectrumSubgroup B) ↔
      Nonempty (OracleSearchEnumeration X {n | primeAt n ∈ B}) := by
  constructor
  · exact spectrumSearchEnumeration_of_any_copy X B
  · rintro ⟨E⟩
    exact oracle_any_spectrum_copy_of_searchEnumeration X B E

end RealizationBoundaries
