import RealizationBoundaries.ObservationSystems
import RealizationBoundaries.PrimeComputability
import Mathlib.Data.ZMod.QuotientRing
import Mathlib.Data.Nat.Squarefree
import Mathlib.CategoryTheory.Whiskering

/-!
# A fixed computable cofinal finite-observation system

All algorithms below depend only on natural stage and residue codes. No
selector, dense source, named source element, or oracle is an algorithm input.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
open CategoryTheory
open scoped BigOperators
namespace RealizationBoundaries

/-- The first `n` actual prime coordinates. -/
def observationPrimes (n : ℕ) : Finset Prime := (Finset.range n).image primeAt

theorem observationPrimes_mono {m n : ℕ} (h : m ≤ n) :
    observationPrimes m ⊆ observationPrimes n :=
  Finset.image_subset_image (Finset.range_mono h)

theorem primeAt_not_mem_observationPrimes (n : ℕ) : primeAt n ∉ observationPrimes n := by
  rintro h
  obtain ⟨i, hi, he⟩ := Finset.mem_image.mp h
  have hin := primeAt_injective he
  exact (Nat.ne_of_lt (Finset.mem_range.mp hi)) hin

@[simp] theorem observationPrimes_zero : observationPrimes 0 = ∅ := by
  simp [observationPrimes]

@[simp] theorem observationPrimes_succ (n : ℕ) :
    observationPrimes (n+1) = insert (primeAt n) (observationPrimes n) := by
  simp only [observationPrimes, Finset.range_add_one, Finset.image_insert]

/-- The fixed finite cyclic group at stage `n` has this squarefree order. -/
def observationModulus (n : ℕ) : ℕ := ∏ p ∈ observationPrimes n, p.val

@[simp] theorem observationModulus_zero : observationModulus 0 = 1 := by
  simp [observationModulus]

@[simp] theorem observationModulus_succ (n : ℕ) :
    observationModulus (n+1) = observationModulus n * (primeAt n).val := by
  classical
  rw [observationModulus, observationPrimes_succ,
    Finset.prod_insert (primeAt_not_mem_observationPrimes n)]
  exact Nat.mul_comm _ _

theorem observationModulus_pos (n : ℕ) : 0 < observationModulus n :=
  Finset.prod_pos (fun p _ => p.property.pos)

instance observationModulus_neZero (n : ℕ) : NeZero (observationModulus n) :=
  ⟨(observationModulus_pos n).ne'⟩

theorem observationModulus_dvd {m n : ℕ} (h : m ≤ n) :
    observationModulus m ∣ observationModulus n :=
  Finset.prod_dvd_prod_of_subset _ _ _ (observationPrimes_mono h)

theorem observationModulus_squarefree (n : ℕ) : Squarefree (observationModulus n) := by
  apply Finset.squarefree_prod_of_pairwise_isCoprime
  · intro p _ q _ hpq
    change IsRelPrime p.val q.val
    rw [← Nat.coprime_iff_isRelPrime]
    exact (Nat.coprime_primes p.property q.property).mpr
      (fun h => hpq (Subtype.ext h))
  · intro p _
    exact p.property.squarefree

/-- Prime values are proved computable independently. Primitive recursion then
computes the full stage size, rather than assuming a prime-product oracle. -/
theorem computable_observationModulus : Computable observationModulus := by
  have hstep : Computable₂ (fun (_ : ℕ) (p : ℕ × ℕ) => p.2 * (primeAt p.1).val) :=
    Primrec.nat_mul.to_comp.comp (Computable.snd.comp Computable.snd)
      (computable_primeAt_value.comp (Computable.fst.comp Computable.snd))
  refine (Computable.nat_rec Computable.id (Computable.const 1) hstep).of_eq ?_
  intro n
  induction n with
  | zero => exact observationModulus_zero.symm
  | succ n ih =>
    change (Nat.rec 1 (fun i r => r * (primeAt i).val) n) * (primeAt n).val = _
    change Nat.rec 1 (fun i r => r * (primeAt i).val) n = observationModulus n at ih
    rw [ih, observationModulus_succ]

/-- An executable terminating prime search, identified with the actual
mathematical enumeration. Its existence proof is erased at runtime. -/
def observationPrimeProgram (n : ℕ) : ℕ := Nat.find (primeIndexRelation_total n)

theorem observationPrimeProgram_eq (n : ℕ) : observationPrimeProgram n = (primeAt n).val := by
  have ht := Nat.find_spec (primeIndexRelation_total n)
  have he := Nat.nth_count ht.1
  rw [ht.2] at he
  exact he.symm

/-- Executable stage-size computation, with no classical finite-set operation
in its runtime path. -/
def observationModulusProgram (n : ℕ) : ℕ :=
  Nat.rec 1 (fun i r => r * observationPrimeProgram i) n

theorem observationModulusProgram_eq (n : ℕ) :
    observationModulusProgram n = observationModulus n := by
  induction n with
  | zero => exact observationModulus_zero.symm
  | succ n ih =>
    change observationModulusProgram n * observationPrimeProgram n = _
    rw [ih, observationPrimeProgram_eq, observationModulus_succ]

/-- Every actual finite prime set is contained in a prefix. -/
theorem observationPrimes_cofinal (s : Finset Prime) :
    ∃ n, s ⊆ observationPrimes n := by
  classical
  induction s using Finset.induction_on with
  | empty => exact ⟨0, Finset.empty_subset _⟩
  | @insert p s hp ih =>
    obtain ⟨n, hn⟩ := ih
    let i := Nat.count Nat.Prime p.val
    have hi : primeAt i = p := Subtype.ext (Nat.nth_count p.property)
    refine ⟨max n (i+1), ?_⟩
    intro q hq
    rcases Finset.mem_insert.mp hq with rfl | hqs
    · apply observationPrimes_mono (Nat.le_max_right n (i+1))
      exact Finset.mem_image.mpr ⟨i, Finset.mem_range.mpr (Nat.lt_succ_self i), hi⟩
    · exact observationPrimes_mono (Nat.le_max_left n (i+1)) (hn hqs)

/-- The natural residue codes of a stage form a finite decidable domain. -/
def observationValid (n x : ℕ) : Prop := x < observationModulus n

instance observationValid_decidable : DecidableRel observationValid := by
  unfold observationValid
  infer_instance

def observationAddCode (n x y : ℕ) : ℕ := (x+y) % observationModulus n

def observationNegCode (n x : ℕ) : ℕ :=
  (observationModulus n - x % observationModulus n) % observationModulus n

def observationRestrictionCode (m x : ℕ) : ℕ := x % observationModulus m

/-- Executable companions of every finite table. -/
def observationValidProgram (n x : ℕ) : Bool := decide (x < observationModulusProgram n)
def observationAddProgram (n x y : ℕ) : ℕ := (x+y) % observationModulusProgram n
def observationNegProgram (n x : ℕ) : ℕ :=
  (observationModulusProgram n - x % observationModulusProgram n) % observationModulusProgram n
def observationRestrictionProgram (m x : ℕ) : ℕ := x % observationModulusProgram m

theorem observationValidProgram_eq (n x : ℕ) :
    observationValidProgram n x = decide (observationValid n x) := by
  simp only [observationValidProgram, observationValid, observationModulusProgram_eq]

theorem observationAddProgram_eq (n x y : ℕ) :
    observationAddProgram n x y = observationAddCode n x y := by
  simp only [observationAddProgram, observationAddCode, observationModulusProgram_eq]

theorem observationNegProgram_eq (n x : ℕ) :
    observationNegProgram n x = observationNegCode n x := by
  simp only [observationNegProgram, observationNegCode, observationModulusProgram_eq]

theorem observationRestrictionProgram_eq (m x : ℕ) :
    observationRestrictionProgram m x = observationRestrictionCode m x := by
  simp only [observationRestrictionProgram, observationRestrictionCode, observationModulusProgram_eq]

/-- All validity, group-table and transition-table algorithms are ordinary
computable and have no selector or oracle parameter. -/
theorem computable_observationIndexRelation : Computable (fun k : ℕ =>
    decide (k.unpair.2 ≤ k.unpair.1)) :=
  Primrec.nat_le.decide.to_comp.comp
    (Computable.snd.comp Computable.unpair) (Computable.fst.comp Computable.unpair)

theorem computable_observationEquality : Computable (fun k : ℕ =>
    decide (k.unpair.1 = k.unpair.2)) :=
  Primrec.eq.decide.to_comp.comp
    (Computable.fst.comp Computable.unpair) (Computable.snd.comp Computable.unpair)

theorem computable_observationValid : Computable (fun k : ℕ =>
    decide (observationValid k.unpair.1 k.unpair.2)) := by
  have hlt : Computable₂ (fun a b : ℕ => decide (a < b)) := Primrec.nat_lt.decide.to_comp
  exact hlt.comp (Computable.snd.comp Computable.unpair)
    (computable_observationModulus.comp (Computable.fst.comp Computable.unpair))

theorem computable_observationAddCode : Computable (fun k : ℕ =>
    observationAddCode k.unpair.1 k.unpair.2.unpair.1 k.unpair.2.unpair.2) := by
  have hl : Computable (fun k : ℕ => k.unpair.1) := Computable.fst.comp Computable.unpair
  have hr : Computable (fun k : ℕ => k.unpair.2) := Computable.snd.comp Computable.unpair
  exact Primrec.nat_mod.to_comp.comp
    (Primrec.nat_add.to_comp.comp (hl.comp hr) (hr.comp hr))
    (computable_observationModulus.comp hl)

theorem computable_observationNegCode : Computable (fun k : ℕ =>
    observationNegCode k.unpair.1 k.unpair.2) := by
  have hl : Computable (fun k : ℕ => k.unpair.1) := Computable.fst.comp Computable.unpair
  have hr : Computable (fun k : ℕ => k.unpair.2) := Computable.snd.comp Computable.unpair
  have hM := computable_observationModulus.comp hl
  exact Primrec.nat_mod.to_comp.comp
    (Primrec.nat_sub.to_comp.comp hM (Primrec.nat_mod.to_comp.comp hr hM)) hM

theorem computable_observationRestrictionCode : Computable (fun k : ℕ =>
    observationRestrictionCode k.unpair.1 k.unpair.2) := by
  exact Primrec.nat_mod.to_comp.comp (Computable.snd.comp Computable.unpair)
    (computable_observationModulus.comp (Computable.fst.comp Computable.unpair))

theorem observationAddCode_valid (n x y : ℕ) :
    observationValid n (observationAddCode n x y) := Nat.mod_lt _ (observationModulus_pos n)

theorem observationNegCode_valid (n x : ℕ) :
    observationValid n (observationNegCode n x) := Nat.mod_lt _ (observationModulus_pos n)

theorem observationRestrictionCode_valid (m x : ℕ) :
    observationValid m (observationRestrictionCode m x) := Nat.mod_lt _ (observationModulus_pos m)

/-- Finite natural names are bijective with the actual finite cyclic group. -/
def observationNames (n : ℕ) : Fin (observationModulus n) ≃ ZMod (observationModulus n) :=
  Equiv.ofBijective (fun x => (x.val : ZMod (observationModulus n))) (by
    constructor
    · intro x y h
      apply Fin.ext
      have he := congrArg ZMod.val h
      simpa only [ZMod.val_natCast, Nat.mod_eq_of_lt x.isLt, Nat.mod_eq_of_lt y.isLt] using he
    · intro x
      exact ⟨⟨x.val, x.val_lt⟩, ZMod.natCast_zmod_val x⟩)

@[simp] theorem observationNames_apply (n : ℕ) (x : Fin (observationModulus n)) :
    observationNames n x = (x.val : ZMod (observationModulus n)) := rfl

theorem observationZeroCode_valid (n : ℕ) : observationValid n 0 := observationModulus_pos n

theorem observationAddCode_spec (n x y : ℕ) :
    (observationAddCode n x y : ZMod (observationModulus n)) =
      (x : ZMod (observationModulus n)) + (y : ZMod (observationModulus n)) := by
  simp only [observationAddCode, ZMod.natCast_mod, Nat.cast_add]

theorem observationNegCode_spec (n x : ℕ) :
    (observationNegCode n x : ZMod (observationModulus n)) =
      -(x : ZMod (observationModulus n)) := by
  have hx : x % observationModulus n ≤ observationModulus n :=
    (Nat.mod_lt _ (observationModulus_pos n)).le
  rw [observationNegCode, ZMod.natCast_mod, Nat.cast_sub hx,
    ZMod.natCast_self, ZMod.natCast_mod, zero_sub]

def observationRestriction {m n : ℕ} (h : m ≤ n) :
    ZMod (observationModulus n) →+ ZMod (observationModulus m) :=
  (ZMod.castHom (observationModulus_dvd h) (ZMod (observationModulus m))).toAddMonoidHom

theorem observationRestrictionCode_spec {m n : ℕ} (h : m ≤ n) (x : ℕ) :
    (observationRestrictionCode m x : ZMod (observationModulus m)) =
      observationRestriction h (x : ZMod (observationModulus n)) := by
  simp [observationRestrictionCode, observationRestriction]

@[simp] theorem observationRestriction_natCast {m n : ℕ} (h : m ≤ n) (x : ℕ) :
    observationRestriction h (x : ZMod (observationModulus n)) =
      (x : ZMod (observationModulus m)) :=
  map_natCast (ZMod.castHom (observationModulus_dvd h) (ZMod (observationModulus m))) x

/-- The computably indexed fixed diagram of actual finite cyclic groups. -/
def computableObservation : OrderDual ℕ ⥤ FiniteAddGrp where
  obj n := FiniteAddGrp.of (ZMod (observationModulus n.ofDual))
  map f := FiniteAddGrp.ofHom (observationRestriction f.le)
  map_id n := by
    ext x
    change observationRestriction (le_refl n.ofDual) x = x
    rw [← ZMod.natCast_zmod_val x]
    rw [observationRestriction_natCast]
  map_comp f g := by
    ext x
    change observationRestriction (le_trans g.le f.le) x =
      observationRestriction g.le (observationRestriction f.le x)
    rw [← ZMod.natCast_zmod_val x]
    rw [observationRestriction_natCast, observationRestriction_natCast,
      observationRestriction_natCast]

/-- Prefix coordinate reindexing of the actual source-free coordinate diagram. -/
def observationPrefixFunctor : OrderDual ℕ ⥤ CoordinateIndex :=
  (show OrderDual ℕ →o CoordinateIndex from
    ⟨fun n => OrderDual.toDual (observationPrimes n.ofDual),
      fun _ _ h => observationPrimes_mono h⟩).monotone.functor

instance observationPrefixFunctor_initial : observationPrefixFunctor.Initial := by
  apply (Functor.initial_iff_of_isCofiltered _).mpr
  constructor
  · intro s
    obtain ⟨n, hn⟩ := observationPrimes_cofinal s.ofDual
    exact ⟨OrderDual.toDual n, ⟨hn.hom⟩⟩
  · intro s n f g
    exact ⟨n, 𝟙 n, Subsingleton.elim _ _⟩

/-- CRT identifies the actual fixed cyclic stage with exactly the corresponding
finite prime-coordinate group, not merely another group of the same cardinality. -/
def observationCrtEquiv (n : ℕ) :
    ZMod (observationModulus n) ≃+* FiniteCoordinates (OrderDual.toDual (observationPrimes n)) := by
  classical
  let s := observationPrimes n
  have hc : Pairwise (fun p q : {p : Prime // p ∈ s} => Nat.Coprime p.val.val q.val.val) := by
    intro p q hpq
    exact (Nat.coprime_primes p.val.property q.val.property).mpr
      (fun h => hpq (Subtype.ext (Subtype.ext h)))
  exact (ZMod.ringEquivCongr (Finset.prod_coe_sort s (fun p : Prime => p.val)).symm).trans
    (ZMod.prodEquivPi (fun p : {p : Prime // p ∈ s} => p.val.val) hc)

@[simp] theorem observationCrtEquiv_natCast (n x : ℕ)
    (p : {p : Prime // p ∈ observationPrimes n}) :
    observationCrtEquiv n (x : ZMod (observationModulus n)) p = (x : Coordinate p.val) := by
  exact congrArg (fun z : FiniteCoordinates (OrderDual.toDual (observationPrimes n)) => z p)
    (map_natCast (observationCrtEquiv n) x)

/-- The CRT identifications commute with all actual restriction maps. -/
theorem observationCrtEquiv_restriction {m n : ℕ} (h : m ≤ n)
    (x : ZMod (observationModulus n)) :
    finiteCoordinateRestriction (observationPrimes_mono h) (observationCrtEquiv n x) =
      observationCrtEquiv m (observationRestriction h x) := by
  rw [← ZMod.natCast_zmod_val x]
  funext p
  change observationCrtEquiv n (x.val : ZMod (observationModulus n))
      ⟨p.val, observationPrimes_mono h p.property⟩ =
    observationCrtEquiv m (observationRestriction h (x.val : ZMod (observationModulus n))) p
  have hr : observationRestriction h (x.val : ZMod (observationModulus n)) =
      (x.val : ZMod (observationModulus m)) :=
    map_natCast (ZMod.castHom (observationModulus_dvd h) (ZMod (observationModulus m))) _
  rw [hr, observationCrtEquiv_natCast, observationCrtEquiv_natCast]

/-- A compatible isomorphism of finite-group diagrams ties the native tables to
the already checked coordinate-observation inverse system. -/
def computableObservationIso : computableObservation ≅ observationPrefixFunctor ⋙ coordinateObservation :=
  NatIso.ofComponents (fun n => {
    hom := FiniteAddGrp.ofHom (observationCrtEquiv n.ofDual).toAddMonoidHom
    inv := FiniteAddGrp.ofHom (observationCrtEquiv n.ofDual).symm.toAddMonoidHom
    hom_inv_id := by ext x; exact (observationCrtEquiv n.ofDual).symm_apply_apply x
    inv_hom_id := by ext x; exact (observationCrtEquiv n.ofDual).apply_symm_apply x
  }) (by
    intro n m f
    ext x
    change observationCrtEquiv m.ofDual (observationRestriction f.le x) =
      finiteCoordinateRestriction (observationPrimes_mono f.le) (observationCrtEquiv n.ofDual x)
    exact (observationCrtEquiv_restriction f.le x).symm)

/-- For every actual rational preimage, the same native fixed system represents
its entire finite-quotient observation after certified cofinal reindexing. -/
def computableObservationQuotientIso (W : Submodule ℚ TailSpace) :
    observationPrefixFunctor ⋙ coordinateIndexFunctor W ⋙
      ProfiniteAddGrp.ProfiniteCompletion.finiteAddGrpDiagram (AddGrpCat.of (preimage W)) ≅
        computableObservation :=
  (Functor.isoWhiskerLeft observationPrefixFunctor (coordinateObservationIso W)).trans
    computableObservationIso.symm

/-- The full finite observation can be presented by this one fixed native
computable diagram, with an explicitly certified cofinal comparison. -/
def fixedComputableObservation : FiniteObservation where
  Index := OrderDual ℕ
  diagram := computableObservation

/-- The prefix index maps are cofinal in all actual finite quotients. -/
instance computableObservationIndex_initial (W : Submodule ℚ TailSpace) :
    (observationPrefixFunctor ⋙ coordinateIndexFunctor W).Initial :=
  Functor.initial_comp observationPrefixFunctor (coordinateIndexFunctor W)

theorem allFiniteObservation_fixed_computable (W : Submodule ℚ TailSpace) :
    CommonCofinalObservation (allFiniteObservation W) fixedComputableObservation := by
  refine ⟨OrderDual ℕ, inferInstance,
    observationPrefixFunctor ⋙ coordinateIndexFunctor W, 𝟭 (OrderDual ℕ),
    inferInstance, computableObservationIndex_initial W, inferInstance, ?_⟩
  exact ⟨(computableObservationQuotientIso W).trans (Functor.leftUnitor computableObservation).symm⟩

end RealizationBoundaries
