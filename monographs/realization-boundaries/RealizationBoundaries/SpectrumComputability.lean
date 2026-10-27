import RealizationBoundaries.ComputablePresentations
import Mathlib.Computability.Halting

/-! # The halting-complement prime spectrum and its actual presentation obstruction -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- The actual diagonal halting set for Mathlib's partial-recursive program codes. -/
def diagonalHalting (n : ℕ) : Prop :=
  ((Denumerable.ofNat Nat.Partrec.Code n).eval n).Dom

/-- Relative computable enumeration is closed under ordinary computable preimages. -/
theorem oracleEnumerable_computable_preimage (X : ℕ → Bool) (A : Set ℕ)
    (hA : OracleEnumerable X A) (g : ℕ → ℕ) (hg : Computable g) :
    OracleEnumerable X {n | g n ∈ A} := by
  obtain ⟨f, hf, hdom⟩ := hA
  have hcomp : Nat.RecursiveIn {selectorOracle X} (fun n => f (g n)) := by
    apply (Nat.RecursiveIn.comp hf (OracleComputable.of_computable hg)).of_eq
    intro n
    simp
  exact ⟨_, hcomp, fun n => hdom (g n)⟩

/-- The empty-information membership oracle contributes only a computable constant. -/
theorem recursiveIn_empty_selector_partrec {f : ℕ →. ℕ}
    (hf : Nat.RecursiveIn {selectorOracle (fun _ => false)} f) : Nat.Partrec f := by
  apply hf.partrec_of_oracle
  intro g hg
  rw [Set.mem_singleton_iff.mp hg]
  change Nat.Partrec (fun _ : ℕ => Part.some (0 : ℕ))
  exact Partrec.nat_iff.mp (Computable.const 0).partrec

/-- The complement of the actual diagonal halting set is not computably enumerable.
The proof uses a code for the putative semidecision procedure on its own code. -/
theorem diagonalHalting_complement_not_enumerable :
    ¬ OracleEnumerable (fun _ => false) {n | ¬ diagonalHalting n} := by
  rintro ⟨f, hf, hdom⟩
  obtain ⟨c, rfl⟩ := Nat.Partrec.Code.exists_code.mp (recursiveIn_empty_selector_partrec hf)
  have h := hdom (Encodable.encode c)
  have hh : (c.eval (Encodable.encode c)).Dom ↔ ¬ (c.eval (Encodable.encode c)).Dom := by
    simpa only [Set.mem_ofPred_eq, diagonalHalting, Denumerable.ofNat_encode] using h
  by_cases hc : (c.eval (Encodable.encode c)).Dom
  · exact hh.mp hc hc
  · exact hc (hh.mpr hc)

/-- The literal index spectrum printed in Monograph 3.4. -/
def haltingIndexSpectrum : Set ℕ :=
  {i | ∃ n, i = 2*n ∨ (i = 2*n+1 ∧ ¬ diagonalHalting n)}

/-- Its actual prime-coordinate selector. -/
def haltingPrimeSpectrum : Set Prime := primeAt '' haltingIndexSpectrum

@[simp] theorem even_mem_haltingIndexSpectrum (n : ℕ) : 2*n ∈ haltingIndexSpectrum :=
  ⟨n, Or.inl rfl⟩

@[simp] theorem odd_mem_haltingIndexSpectrum_iff (n : ℕ) :
    2*n+1 ∈ haltingIndexSpectrum ↔ ¬ diagonalHalting n := by
  constructor
  · rintro ⟨m, h | ⟨h, hm⟩⟩
    · omega
    · have hmn : m = n := by omega
      simpa [hmn] using hm
  · intro h
    exact ⟨n, Or.inr ⟨rfl, h⟩⟩

@[simp] theorem primeAt_mem_haltingPrimeSpectrum_iff (n : ℕ) :
    primeAt n ∈ haltingPrimeSpectrum ↔ n ∈ haltingIndexSpectrum := by
  constructor
  · rintro ⟨m, hm, hmn⟩
    exact primeAt_injective hmn ▸ hm
  · intro hn
    exact ⟨n, hn, rfl⟩

/-- Enumeration of the printed spectrum would enumerate the halting complement
by filtering the odd positions through an ordinary primitive recursive map. -/
theorem haltingPrimeSpectrum_not_enumerable :
    ¬ OracleEnumerable (fun _ => false) {n | primeAt n ∈ haltingPrimeSpectrum} := by
  intro h
  have hg : Computable (fun n : ℕ => 2*n+1) :=
    (Primrec.nat_add.comp (Primrec.nat_mul.comp (Primrec.const 2) Primrec.id)
      (Primrec.const 1)).to_comp
  obtain ⟨f, hf, hdom⟩ := oracleEnumerable_computable_preimage (fun _ => false)
    {n | primeAt n ∈ haltingPrimeSpectrum} h (fun n => 2*n+1) hg
  apply diagonalHalting_complement_not_enumerable
  exact ⟨f, hf, fun n => (hdom n).trans (by simp)⟩

/-- Monograph 3.4's no-computable-copy conclusion, for the actual infinite prime
support subgroup and the native ordinary-computability oracle convention. -/
theorem haltingSpectrum_no_computable_copy :
    IsEmpty (OracleGroupCopy (fun _ => false) (spectrumSubgroup haltingPrimeSpectrum)) := by
  constructor
  intro c
  exact haltingPrimeSpectrum_not_enumerable
    (oracle_spectrum_copy_implies_enumerable _ _ c)

/-- Every production prime coordinate has an actual natural index. -/
theorem primeAt_surjective : Function.Surjective primeAt := by
  intro p
  refine ⟨Nat.count Nat.Prime p.val, ?_⟩
  exact Subtype.ext (Nat.nth_count p.property)

/-- Infinitely many even coordinates survive in the halting-complement group. -/
def haltingSpectrumEvenSeed (n : ℕ) : spectrumSubgroup haltingPrimeSpectrum :=
  ⟨primeSeed (primeAt (2*n)), (primeSeed_mem_spectrumSubgroup _ _).mpr
    ((primeAt_mem_haltingPrimeSpectrum_iff _).mpr (even_mem_haltingIndexSpectrum n))⟩

theorem haltingSpectrumEvenSeed_injective : Function.Injective haltingSpectrumEvenSeed := by
  intro n m h
  have hp := primeAt_injective (primeSeed_injective
    (congrArg (fun z : spectrumSubgroup haltingPrimeSpectrum => z.val) h))
  omega

instance haltingSpectrum_infinite : Infinite (spectrumSubgroup haltingPrimeSpectrum) :=
  Infinite.of_injective haltingSpectrumEvenSeed haltingSpectrumEvenSeed_injective

/-- Native semidecision of the actual diagonal halting set. -/
theorem diagonalHalting_re : REPred diagonalHalting :=
  (Nat.Partrec.Code.eval_part.comp (Computable.ofNat Nat.Partrec.Code) Computable.id).dom_re

/-- The prime coordinates killed by the extra effectively enumerable relators. -/
def killedHaltingPrimes : Set Prime :=
  {p | ∃ n, diagonalHalting n ∧ primeAt (2*n+1) = p}

theorem haltingPrimeSpectrum_complement : haltingPrimeSpectrum = killedHaltingPrimesᶜ := by
  classical
  ext p
  obtain ⟨i, rfl⟩ := primeAt_surjective p
  rw [primeAt_mem_haltingPrimeSpectrum_iff]
  change (∃ n, i = 2*n ∨ (i = 2*n+1 ∧ ¬ diagonalHalting n)) ↔
    ¬ ∃ n, diagonalHalting n ∧ primeAt (2*n+1) = primeAt i
  simp only [primeAt_injective.eq_iff]
  constructor
  · rintro ⟨n, hi | ⟨hi, hn⟩⟩ ⟨m, hm, hmi⟩
    · omega
    · have : m = n := by omega
      exact hn (this ▸ hm)
  · intro h
    by_cases hi : i % 2 = 0
    · exact ⟨i/2, Or.inl (by omega)⟩
    · have he : i = 2*(i/2)+1 := by omega
      refine ⟨i/2, Or.inr ⟨he, ?_⟩⟩
      intro hk
      exact h ⟨i/2, hk, he.symm⟩

/-- Keep precisely the selected coordinates of an actual finitely supported vector. -/
def spectrumProjection (B : Set Prime) : finiteSupport →+ spectrumSubgroup B where
  toFun x := by
    classical
    let y : Ambient := fun p => if p ∈ B then x.val p else 0
    have hy : y ∈ finiteSupport := x.property.subset (by
      intro p hp
      by_contra hx
      exact hp (by simp [y, show x.val p = 0 from not_not.mp hx]))
    refine ⟨⟨y, hy⟩, ?_⟩
    intro p hp
    by_contra hn
    exact hp (by simp [y, hn])
  map_zero' := by
    classical
    apply Subtype.ext
    apply Subtype.ext
    funext p
    simp
  map_add' x y := by
    classical
    apply Subtype.ext
    apply Subtype.ext
    funext p
    by_cases hp : p ∈ B <;> simp [hp]

@[simp] theorem spectrumProjection_apply_mem (B : Set Prime) (x : finiteSupport)
    (p : Prime) (hp : p ∈ B) : (spectrumProjection B x).val.val p = x.val p := by
  classical
  simp [spectrumProjection, hp]

@[simp] theorem spectrumProjection_apply_not_mem (B : Set Prime) (x : finiteSupport)
    (p : Prime) (hp : p ∉ B) : (spectrumProjection B x).val.val p = 0 := by
  classical
  simp [spectrumProjection, hp]

theorem spectrumProjection_surjective (B : Set Prime) :
    Function.Surjective (spectrumProjection B) := by
  intro x
  refine ⟨x.val, ?_⟩
  apply Subtype.ext
  apply Subtype.ext
  funext p
  by_cases hp : p ∈ B
  · exact spectrumProjection_apply_mem B x.val p hp
  · rw [spectrumProjection_apply_not_mem B x.val p hp]
    symm
    by_contra hn
    exact hp (x.property hn)

theorem spectrumProjection_ker (B : Set Prime) :
    (spectrumProjection B).ker = spectrumSubgroup Bᶜ := by
  classical
  ext x
  constructor
  · intro hx p hp
    by_contra hn
    have hb : p ∈ B := not_not.mp hn
    have he := congrArg (fun z : spectrumSubgroup B => z.val.val p) hx
    rw [spectrumProjection_apply_mem B x p hb] at he
    exact hp he
  · intro hx
    apply Subtype.ext
    apply Subtype.ext
    funext p
    by_cases hp : p ∈ B
    · rw [spectrumProjection_apply_mem B x p hp]
      by_contra hn
      exact hx hn hp
    · exact spectrumProjection_apply_not_mem B x p hp

/-- The quotient by the omitted actual coordinates is exactly the retained support group. -/
def spectrumQuotientEquiv (B : Set Prime) :
    (finiteSupport ⧸ spectrumSubgroup Bᶜ) ≃+ spectrumSubgroup B :=
  (QuotientAddGroup.quotientAddEquivOfEq (spectrumProjection_ker B).symm).trans
    (QuotientAddGroup.quotientKerEquivOfSurjective (spectrumProjection B)
      (spectrumProjection_surjective B))

/-- Actual support subgroups are generated by precisely their retained prime seeds. -/
theorem spectrumSubgroup_eq_seedClosure (B : Set Prime) :
    spectrumSubgroup B = AddSubgroup.closure (primeSeed '' B) := by
  classical
  apply le_antisymm
  · intro x hx
    rw [finiteSupport_primeSeed_decomposition x]
    apply AddSubgroup.sum_mem
    intro p hp
    apply AddSubgroup.nsmul_mem
    apply AddSubgroup.subset_closure
    exact ⟨p, hx (by simpa using hp), rfl⟩
  · apply (AddSubgroup.closure_le _).mpr
    rintro _ ⟨p, hp, rfl⟩
    exact (primeSeed_mem_spectrumSubgroup B p).mpr hp

/-- The extra relators are the literal odd prime generators whose programs halt. -/
def haltingSeedRelators : Set finiteSupport :=
  {x | ∃ n, diagonalHalting n ∧ primeSeed (primeAt (2*n+1)) = x}

theorem haltingSeedRelators_eq :
    haltingSeedRelators = primeSeed '' killedHaltingPrimes := by
  ext x
  constructor
  · rintro ⟨n, hn, rfl⟩
    exact ⟨primeAt (2*n+1), ⟨n, hn, rfl⟩, rfl⟩
  · rintro ⟨p, ⟨n, hn, rfl⟩, rfl⟩
    exact ⟨n, hn, rfl⟩

/-- Quotienting the actual direct sum by the actual extra relators gives H. -/
def haltingRelatorQuotientEquiv :
    (finiteSupport ⧸ AddSubgroup.closure haltingSeedRelators) ≃+
      spectrumSubgroup haltingPrimeSpectrum := by
  have he : AddSubgroup.closure haltingSeedRelators =
      spectrumSubgroup haltingPrimeSpectrumᶜ := by
    rw [haltingSeedRelators_eq, ← spectrumSubgroup_eq_seedClosure,
      haltingPrimeSpectrum_complement, compl_compl]
  exact (QuotientAddGroup.quotientAddEquivOfEq he).trans
    (spectrumQuotientEquiv haltingPrimeSpectrum)

/-- A genuine finite-stage program for the extra relator indices. Each natural
stage decodes a program index and fuel, returning its odd generator exactly
when the bounded universal evaluator has observed termination. -/
def haltingRelatorIndexStage (k : ℕ) : Option ℕ :=
  if ((Denumerable.ofNat Nat.Partrec.Code k.unpair.1).evaln k.unpair.2
      k.unpair.1).isSome then some (2*k.unpair.1+1) else none

theorem primrec_haltingRelatorIndexStage : Primrec haltingRelatorIndexStage := by
  have hl : Primrec (fun k : ℕ => k.unpair.1) := Primrec.fst.comp Primrec.unpair
  have hr : Primrec (fun k : ℕ => k.unpair.2) := Primrec.snd.comp Primrec.unpair
  have he : Primrec (fun k : ℕ => (Denumerable.ofNat Nat.Partrec.Code k.unpair.1).evaln
      k.unpair.2 k.unpair.1) :=
    Nat.Partrec.Code.primrec_evaln.comp ((hr.pair ((Primrec.ofNat _).comp hl)).pair hl)
  have hn : Primrec (fun k : ℕ => 2*k.unpair.1+1) :=
    Primrec.nat_add.comp (Primrec.nat_mul.comp (Primrec.const 2) hl) (Primrec.const 1)
  exact Primrec.ite (Primrec.eq.comp (Primrec.option_isSome.comp he) (Primrec.const true))
    (Primrec.option_some.comp hn) (Primrec.const none)

theorem haltingRelatorIndexStage_correct (i : ℕ) :
    (∃ k, haltingRelatorIndexStage k = some i) ↔
      ∃ n, diagonalHalting n ∧ 2*n+1 = i := by
  constructor
  · rintro ⟨k, hk⟩
    unfold haltingRelatorIndexStage at hk
    split_ifs at hk with h
    · have hn : 2*k.unpair.1+1 = i := Option.some.inj hk
      refine ⟨k.unpair.1, ?_, hn⟩
      obtain ⟨v, hv⟩ := Option.isSome_iff_exists.mp h
      exact (Nat.Partrec.Code.evaln_sound hv).1
  · rintro ⟨n, hn, rfl⟩
    obtain ⟨v, hv⟩ := Part.dom_iff_mem.mp hn
    obtain ⟨t, ht⟩ := Nat.Partrec.Code.evaln_complete.mp hv
    refine ⟨Nat.pair n t, ?_⟩
    simp [haltingRelatorIndexStage, Option.isSome_iff_exists.mpr ⟨v, ht⟩]

/-- The computably emitted labels denote exactly the actual extra relators,
so enumeration and the quotient identification refer to the same objects. -/
theorem haltingRelatorIndexStage_exact :
    haltingSeedRelators =
      (fun i => primeSeed (primeAt i)) '' {i | ∃ k, haltingRelatorIndexStage k = some i} := by
  ext x
  constructor
  · rintro ⟨n, hn, rfl⟩
    exact ⟨2*n+1, (haltingRelatorIndexStage_correct _).mpr ⟨n, hn, rfl⟩, rfl⟩
  · rintro ⟨i, hi, rfl⟩
    obtain ⟨n, hn, rfl⟩ := (haltingRelatorIndexStage_correct i).mp hi
    exact ⟨n, hn, rfl⟩

/-- A genuine computable copy on a finite initial segment. This branch is
necessary because finite groups cannot have bijective names on all of Nat. -/
structure FiniteGroupCopy (H : Type*) [AddGroup H] where
  size : ℕ
  names : Fin size ≃ H
  zero : Fin size
  add : Fin size → Fin size → Fin size
  zero_spec : names zero = 0
  add_spec : ∀ i j, names (add i j) = names i + names j
  add_computable : Computable (fun k : Fin size × Fin size => add k.1 k.2)

/-- All entries of each fixed finite operation table are ordinary computable.
This is existence of a finite copy, not a uniform stopping rule for an enumeration. -/
def finiteGroupCopy (H : Type*) [AddGroup H] [Finite H] : FiniteGroupCopy H := by
  classical
  letI := Fintype.ofFinite H
  let e : Fin (Fintype.card H) ≃ H := (Fintype.equivFin H).symm
  refine ⟨Fintype.card H, e, e.symm 0, fun i j => e.symm (e i + e j), ?_, ?_, ?_⟩
  · exact e.apply_symm_apply 0
  · intro i j
    exact e.apply_symm_apply _
  · exact (Primrec.dom_finite _).to_comp

/-- The finite-or-infinite convention for genuinely computable countable copies. -/
def HasOracleGroupCopy (X : ℕ → Bool) (H : Type*) [AddGroup H] : Prop :=
  Nonempty (FiniteGroupCopy H) ∨ Nonempty (OracleGroupCopy X H)

theorem hasOracleGroupCopy_of_finite (X : ℕ → Bool) (H : Type*) [AddGroup H] [Finite H] :
    HasOracleGroupCopy X H := Or.inl ⟨finiteGroupCopy H⟩

/-- A finite-domain copy cannot witness an infinite group. -/
theorem finiteGroupCopy_false_of_infinite (H : Type*) [AddGroup H] [Infinite H] :
    IsEmpty (FiniteGroupCopy H) := by
  constructor
  intro c
  let : Finite H := Finite.of_equiv (Fin c.size) c.names
  exact not_finite H

/-- The halting spectrum obstruction also rules out the broad finite-or-infinite
copy convention; the infinitely many retained even factors exclude its finite branch. -/
theorem haltingSpectrum_no_any_computable_copy :
    ¬ HasOracleGroupCopy (fun _ => false) (spectrumSubgroup haltingPrimeSpectrum) := by
  intro h
  rcases h with hf | hi
  · exact hf.elim (finiteGroupCopy_false_of_infinite _).false
  · exact hi.elim haltingSpectrum_no_computable_copy.false

/-- Every fixed finite set has an ordinary primitive-recursive membership test. -/
theorem finite_set_primrec_membership (A : Set ℕ) (hA : A.Finite) :
    PrimrecPred (fun n => n ∈ A) := by
  classical
  let L := hA.toFinset.toList
  have hm : PrimrecPred (fun n : ℕ => ∃ a ∈ L, a = n) :=
    (Primrec.eq.exists_mem_list).comp (Primrec.const L) Primrec.id
  exact hm.of_eq (fun n => by simp [L])

/-- Finite spectra are enumerable relative to every oracle, without a uniform
procedure for finding the final stage of a finite enumeration. -/
theorem oracleEnumerable_of_finite (X : ℕ → Bool) (A : Set ℕ) (hA : A.Finite) :
    OracleEnumerable X A := by
  classical
  let test : ℕ → ℕ := fun k => if k.unpair.1 ∈ A then 0 else 1
  have ht : OracleComputable X test := OracleComputable.of_computable
    ((Primrec.ite ((finite_set_primrec_membership A hA).comp
        (Primrec.fst.comp Primrec.unpair)) (Primrec.const 0) (Primrec.const 1)).to_comp)
  obtain ⟨f, hf, hdom⟩ := oracleEnumerable_of_test X test ht
  exact ⟨f, hf, fun n => (hdom n).trans (by simp [test])⟩

/-- A finite group has only finitely many intrinsic prime-torsion indices. -/
theorem finite_group_primeSpectrum_indices (H : Type*) [AddGroup H] [Finite H] :
    {n | HasPrimeTorsion H (primeAt n)}.Finite := by
  have hinj : Function.Injective (fun n : ℕ => (primeAt n).val) :=
    Subtype.val_injective.comp primeAt_injective
  apply ((Set.finite_Iic (Nat.card H)).preimage hinj.injOn).subset
  rintro n ⟨x, hx, hpx⟩
  have ho : addOrderOf x = (primeAt n).val := addOrderOf_eq_prime hpx hx
  have hd := addOrderOf_dvd_natCard x
  rw [ho] at hd
  exact Nat.le_of_dvd Nat.card_pos hd

/-- The lower prime-spectrum criterion includes both finite and infinite coded
domains, so no finite case is silently excluded by the Nat-domain convention. -/
theorem oracle_any_spectrum_copy_implies_enumerable (X : ℕ → Bool) (B : Set Prime)
    (h : HasOracleGroupCopy X (spectrumSubgroup B)) :
    OracleEnumerable X {n | primeAt n ∈ B} := by
  rcases h with hf | hi
  · obtain ⟨c⟩ := hf
    let : Finite (spectrumSubgroup B) := Finite.of_equiv (Fin c.size) c.names
    have hA : {n | primeAt n ∈ B}.Finite := by
      simpa only [spectrumSubgroup_hasPrimeTorsion_iff] using
        finite_group_primeSpectrum_indices (spectrumSubgroup B)
    exact oracleEnumerable_of_finite X _ hA
  · obtain ⟨c⟩ := hi
    exact oracle_spectrum_copy_implies_enumerable X B c

end RealizationBoundaries
