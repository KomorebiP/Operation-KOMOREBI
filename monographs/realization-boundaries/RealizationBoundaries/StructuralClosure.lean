import RealizationBoundaries.Countability
import RealizationBoundaries.RationalFG
import RealizationBoundaries.CyclicFiniteTargets
import Mathlib.GroupTheory.FiniteAbelian.Basic
import Mathlib.LinearAlgebra.Basis.Defs
import Mathlib.Data.Finsupp.Encodable
import Mathlib.LinearAlgebra.Dimension.Free
import Mathlib.LinearAlgebra.Basis.VectorSpace
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.Data.Rat.Lemmas
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-! # Structural closure of the ambient-preimage and cocycle statements -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- A rational vector space is countable exactly when an actual basis is countable.
The reverse implication uses the finite-support coefficient representation. -/
theorem rational_countable_iff_basis_countable {ι : Type} (W : Submodule ℚ TailSpace)
    (b : Module.Basis ι ℚ W) : Countable W ↔ Countable ι := by
  constructor
  · intro h
    let := h
    exact b.injective.countable
  · intro h
    let := h
    exact Countable.of_equiv (ι →₀ ℚ) b.repr.toEquiv.symm

/-- Monograph 4.6: countability of the original preimage is equivalent to countable
rational dimension, expressed through any chosen basis of its actual quotient. -/
theorem preimage_countable_iff_basis_countable {ι : Type} (W : Submodule ℚ TailSpace)
    (b : Module.Basis ι ℚ W) : Countable (preimage W) ↔ Countable ι :=
  (preimage_countable_iff W).trans (rational_countable_iff_basis_countable W b)

/-- The dimension formulation in the printed structural proposition. -/
theorem preimage_countable_iff_rational_rank (W : Submodule ℚ TailSpace) :
    Countable (preimage W) ↔ Module.rank ℚ W ≤ Cardinal.aleph0 := by
  rw [Module.Free.rank_eq_card_chooseBasisIndex]
  exact (preimage_countable_iff_basis_countable W
    (Module.Free.chooseBasis ℚ W)).trans Cardinal.mk_le_aleph0_iff.symm

/-- Finite or countably infinite rational dimension, including the zero subspace. -/
theorem preimage_countable_iff_dimension_finite_or_countably_infinite
    (W : Submodule ℚ TailSpace) :
    Countable (preimage W) ↔
      Module.rank ℚ W < Cardinal.aleph0 ∨ Module.rank ℚ W = Cardinal.aleph0 := by
  rw [preimage_countable_iff_rational_rank, le_iff_lt_or_eq]

/-- Reduction does not cancel a prime denominator when the numerator is coprime. -/
theorem rational_prime_fraction_den (p : Prime) (a : ℕ) (ha : Nat.Coprime a p.val) :
    ((a : ℚ) / (p.val : ℚ)).den = p.val := by
  have h := Rat.den_div_eq_of_coprime (a := (a : ℤ)) (b := (p.val : ℤ))
    (by exact_mod_cast p.property.pos) (by simpa using ha)
  change ((((a : ℚ) / (p.val : ℚ)).den : ℤ)) = (p.val : ℤ) at h
  exact Int.ofNat_inj.mp h

/-- At a prime denominator, a reduced fraction has the section's specified zero value. -/
theorem rationalSection_prime_fraction_zero (S : Set Prime) (p : Prime) (a : ℕ)
    (ha : Nat.Coprime a p.val) :
    rationalSection S ((a : ℚ) / (p.val : ℚ)) p = 0 := by
  apply rationalSection_denominator_zero
  rw [rational_prime_fraction_den p a ha]

/-- Monograph 5.4: the negative selected indicator at one prime.
The equality is in the actual finite-support subgroup of the unrestricted product. -/
theorem cocycle_reads_coordinate (S : Set Prime) (p : Prime) :
    cocycle S ((1 : ℚ) / (p.val : ℚ)) (((p.val - 1 : ℕ) : ℚ) / (p.val : ℚ)) =
      -(⟨cut {p} (indicator S), cut_mem_finiteSupport {p} (indicator S)⟩ : finiteSupport) := by
  classical
  have hc : Nat.Coprime (p.val - 1) p.val :=
    (Nat.coprime_self_sub_left (m := 1) p.property.one_lt.le).mpr
      (Nat.coprime_one_left p.val)
  have hs : (1 : ℚ) / (p.val : ℚ) + ((p.val - 1 : ℕ) : ℚ) / (p.val : ℚ) = 1 := by
    rw [Nat.cast_sub p.property.one_lt.le]
    have hp : (p.val : ℚ) ≠ 0 := Nat.cast_ne_zero.mpr p.property.ne_zero
    field_simp
    ring
  apply Subtype.ext
  funext q
  by_cases hqp : q = p
  · subst q
    change rationalSection S ((1 : ℚ) / (p.val : ℚ)) p +
      rationalSection S (((p.val - 1 : ℕ) : ℚ) / (p.val : ℚ)) p -
      rationalSection S (_ + _) p = _
    have h1 : rationalSection S ((1 : ℚ) / (p.val : ℚ)) p = 0 := by
      simpa only [Nat.cast_one] using
        rationalSection_prime_fraction_zero S p 1 (Nat.coprime_one_left p.val)
    have h2 := rationalSection_prime_fraction_zero S p (p.val - 1) hc
    rw [hs, h1, h2]
    change 0 + 0 - rationalSection S 1 p = -(cut {p} (indicator S) p)
    simp [cut]
  · have hz : sectionDefect S ((1 : ℚ) / (p.val : ℚ))
        (((p.val - 1 : ℕ) : ℚ) / (p.val : ℚ)) q = 0 := by
      by_contra hn
      have hd := sectionDefect_support S ((1 : ℚ) / (p.val : ℚ))
        (((p.val - 1 : ℕ) : ℚ) / (p.val : ℚ)) hn
      change q.val ∣ _ at hd
      rw [show (1 : ℚ) / (p.val : ℚ) = ((1 : ℕ) : ℚ) / (p.val : ℚ) from rfl,
        rational_prime_fraction_den p 1 (Nat.coprime_one_left p.val),
        rational_prime_fraction_den p (p.val - 1) hc] at hd
      have hdiv : q.val ∣ p.val := (q.property.dvd_mul.mp hd).elim id id
      exact hqp (Subtype.ext ((p.property.dvd_iff_eq q.property.ne_one).mp hdiv).symm)
    change sectionDefect S _ _ q = _
    change sectionDefect S _ _ q = -(cut {p} (indicator S) q)
    rw [hz]
    simp [cut, hqp]

/-- The single cocycle value recovers whether the prime was selected. -/
theorem cocycle_coordinate_nonzero_iff (S : Set Prime) (p : Prime) :
    (cocycle S ((1 : ℚ) / (p.val : ℚ))
      (((p.val - 1 : ℕ) : ℚ) / (p.val : ℚ))).val p ≠ 0 ↔ p ∈ S := by
  classical
  rw [cocycle_reads_coordinate]
  change -(cut {p} (indicator S) p) ≠ 0 ↔ p ∈ S
  by_cases h : p ∈ S <;> simp [cut, indicator, h]

/-- A finite subgroup of an original preimage embeds into its actual order-torsion kernel. -/
def finiteSubgroupKernelEmbedding (W : Submodule ℚ TailSpace)
    (H : AddSubgroup (preimage W)) [Finite H] : H →+ rootKernel W (Nat.card H) where
  toFun x := ⟨x.val, by
    change Nat.card H • x.val = 0
    exact congrArg (fun z : H => z.val) (card_nsmul_eq_zero' (x := x))⟩
  map_zero' := rfl
  map_add' _ _ := rfl

theorem finiteSubgroupKernelEmbedding_injective (W : Submodule ℚ TailSpace)
    (H : AddSubgroup (preimage W)) [Finite H] :
    Function.Injective (finiteSubgroupKernelEmbedding W H) := by
  intro x y h
  exact Subtype.ext (congrArg (fun z : rootKernel W (Nat.card H) => z.val) h)

/-- Every actual finite subgroup is cyclic, not merely abstractly bounded in cardinality. -/
theorem finite_preimage_subgroup_cyclic (W : Submodule ℚ TailSpace)
    (H : AddSubgroup (preimage W)) [Finite H] : IsAddCyclic H := by
  let e : rootKernel W (Nat.card H) ≃+ ZMod (primeRadical (Nat.card H)) :=
    (rootKernelEquiv W Nat.card_pos).trans (divisorCrtEquiv Nat.card_pos).toAddEquiv.symm
  exact isAddCyclic_of_injective (e.toAddMonoidHom.comp (finiteSubgroupKernelEmbedding W H))
    (e.injective.comp (finiteSubgroupKernelEmbedding_injective W H))

/-- The order of any finite subgroup is squarefree, including the trivial subgroup of order one. -/
theorem finite_preimage_subgroup_squarefree (W : Submodule ℚ TailSpace)
    (H : AddSubgroup (preimage W)) [Finite H] : Squarefree (Nat.card H) := by
  let : Finite (rootKernel W (Nat.card H)) := rootKernel_finite W Nat.card_pos
  have hc : primeRadical (Nat.card H) = Nat.card H := by
    apply Nat.le_antisymm (Nat.le_of_dvd Nat.card_pos (primeRadical_dvd _))
    have hi := Nat.card_le_card_of_injective (finiteSubgroupKernelEmbedding W H)
      (finiteSubgroupKernelEmbedding_injective W H)
    rwa [rootKernel_card W Nat.card_pos] at hi
  rw [← hc]
  exact primeRadical_squarefree _

/-- Complete finite branch of the local subgroup classification. -/
theorem finite_preimage_subgroup_classification (W : Submodule ℚ TailSpace)
    (H : AddSubgroup (preimage W)) [Finite H] :
    ∃ m : ℕ, 0 < m ∧ Squarefree m ∧ Nonempty (H ≃+ ZMod m) := by
  exact ⟨Nat.card H, Nat.card_pos, finite_preimage_subgroup_squarefree W H,
    ⟨(zmodAddCyclicAddEquiv (finite_preimage_subgroup_cyclic W H)).symm⟩⟩

/-- The rational coordinate map on the actual nonsplit selector extension. -/
def selectorRational {S : Set Prime} (hS : S.Infinite) : selectorGroup S →+ ℚ where
  toFun x := ((NormalForm.realizationEquiv hS).symm x).rational
  map_zero' := by
    simp only [map_zero]
    rfl
  map_add' x y := by simp

/-- The coordinate map vanishes exactly on the actual torsion kernel. -/
theorem selectorRational_eq_zero_iff {S : Set Prime} (hS : S.Infinite)
    (x : selectorGroup S) : selectorRational hS x = 0 ↔ x.val ∈ finiteSupport := by
  let z := (NormalForm.realizationEquiv hS).symm x
  have hz : x.val = rationalSection S z.rational + z.finite.val := by
    have h := NormalForm.realizationEquiv_coe hS z
    simpa only [z, AddEquiv.apply_symm_apply] using h
  constructor
  · intro h
    change z.rational = 0 at h
    rw [hz, h, rationalSection_zero, zero_add]
    exact z.finite.property
  · intro h
    have hn := normalForm_unique hS z.rational 0 z.finite ⟨x.val, h⟩
      (by simpa using hz.symm)
    exact hn.1

/-- The direct product map associated to one lift of an integer quotient generator. -/
def integerSplitMap {L : Type} [AddCommGroup L] (f : L →+ ℤ) (x : L)
    (_hx : f x = 1) : ℤ × f.ker →+ L where
  toFun z := z.1 • x + z.2.val
  map_zero' := by simp
  map_add' z w := by simp only [Prod.fst_add, Prod.snd_add, add_zsmul,
    AddSubgroup.coe_add]; abel

theorem integerSplitMap_bijective {L : Type} [AddCommGroup L] (f : L →+ ℤ) (x : L)
    (hx : f x = 1) : Function.Bijective (integerSplitMap f x hx) := by
  constructor
  · intro z w h
    have hf := congrArg f h
    have hn : z.1 = w.1 := by
      simpa [integerSplitMap, hx, AddMonoidHom.mem_ker.mp z.2.property,
        AddMonoidHom.mem_ker.mp w.2.property] using hf
    apply Prod.ext hn
    apply Subtype.ext
    change z.1 • x + z.2.val = w.1 • x + w.2.val at h
    rw [hn] at h
    exact add_left_cancel h
  · intro z
    refine ⟨(f z, ⟨z - (f z) • x, ?_⟩), ?_⟩
    · change f (z - (f z) • x) = 0
      simp [hx]
    · change (f z) • x + (z - (f z) • x) = z
      abel

/-- A supplied actual lift gives the full split equivalence over an integer quotient. -/
def integerSplitEquiv {L : Type} [AddCommGroup L] (f : L →+ ℤ) (x : L)
    (hx : f x = 1) : L ≃+ ℤ × f.ker :=
  (AddEquiv.ofBijective (integerSplitMap f x hx) (integerSplitMap_bijective f x hx)).symm

/-- A split integer quotient of a finitely generated group has finitely generated kernel. -/
theorem integerSplitKernel_fg {L : Type} [AddCommGroup L] [AddGroup.FG L]
    (f : L →+ ℤ) (x : L) (hx : f x = 1) : AddGroup.FG f.ker := by
  let e := integerSplitEquiv f x hx
  let g : L →+ f.ker := (AddMonoidHom.snd ℤ f.ker).comp e.toAddMonoidHom
  apply AddGroup.fg_of_surjective (f := g)
  intro k
  exact ⟨e.symm (0, k), by simp [g]⟩

/-- The finite subgroup classification also applies through a supplied faithful embedding. -/
theorem finite_embedded_preimage_classification (W : Submodule ℚ TailSpace)
    (F : Type) [AddCommGroup F] [Finite F] (f : F →+ preimage W)
    (hf : Function.Injective f) :
    ∃ m : ℕ, 0 < m ∧ Squarefree m ∧ Nonempty (F ≃+ ZMod m) := by
  let e : F ≃+ f.range := AddMonoidHom.ofInjective hf
  let : Finite f.range := Finite.of_equiv F e.toEquiv
  obtain ⟨m, hm, hs, ⟨g⟩⟩ := finite_preimage_subgroup_classification W f.range
  exact ⟨m, hm, hs, ⟨e.trans g⟩⟩

/-- The kernel of an integer quotient is finite when it is exactly torsion in the ambient group. -/
theorem fg_selector_integer_kernel_finite {S : Set Prime} (hS : S.Infinite)
    (L : AddSubgroup (selectorGroup S)) [AddGroup.FG L]
    (f : L →+ ℤ) (hf : Function.Surjective f)
    (hker : ∀ x : L, f x = 0 → selectorRational hS x.val = 0) : Finite f.ker := by
  obtain ⟨x, hx⟩ := hf 1
  let : AddGroup.FG f.ker := integerSplitKernel_fg f x hx
  apply AddCommGroup.finite_of_fg_isAddTorsion
  intro k
  have hfinite : k.val.val.val ∈ finiteSupport :=
    (selectorRational_eq_zero_iff hS k.val.val).mp (hker k.val k.property)
  obtain ⟨m, hm, hzero⟩ := (preimage_torsion_iff (selectorLine S) k.val.val).mpr hfinite
  apply isOfFinAddOrder_iff_nsmul_eq_zero.mpr
  exact ⟨m, hm, Subtype.ext (Subtype.ext hzero)⟩

/-- The infinite branch, once a generator of the rational image has been chosen. -/
theorem fg_selector_subgroup_integer_classification {S : Set Prime} (hS : S.Infinite)
    (L : AddSubgroup (selectorGroup S)) [AddGroup.FG L]
    (f : L →+ ℤ) (hf : Function.Surjective f)
    (hker : ∀ x : L, f x = 0 → selectorRational hS x.val = 0) :
    ∃ m : ℕ, 0 < m ∧ Squarefree m ∧ Nonempty (L ≃+ ℤ × ZMod m) := by
  let : Finite f.ker := fg_selector_integer_kernel_finite hS L f hf hker
  let j : f.ker →+ preimage (selectorLine S) := L.subtype.comp f.ker.subtype
  have hj : Function.Injective j := Subtype.val_injective.comp Subtype.val_injective
  obtain ⟨m, hm, hs, ⟨g⟩⟩ := finite_embedded_preimage_classification (selectorLine S) f.ker j hj
  obtain ⟨x, hx⟩ := hf 1
  exact ⟨m, hm, hs, ⟨(integerSplitEquiv f x hx).trans ((AddEquiv.refl ℤ).prodCongr g)⟩⟩

/-- Zero rational image forces a finitely generated selector subgroup to be finite. -/
theorem fg_selector_subgroup_finite_of_rational_zero {S : Set Prime} (hS : S.Infinite)
    (L : AddSubgroup (selectorGroup S)) [AddGroup.FG L]
    (hzero : ∀ x : L, selectorRational hS x.val = 0) : Finite L := by
  apply AddCommGroup.finite_of_fg_isAddTorsion
  intro x
  have hfinite : x.val.val ∈ finiteSupport :=
    (selectorRational_eq_zero_iff hS x.val).mp (hzero x)
  obtain ⟨m, hm, hz⟩ := (preimage_torsion_iff (selectorLine S) x.val).mpr hfinite
  exact isOfFinAddOrder_iff_nsmul_eq_zero.mpr ⟨m, hm, Subtype.ext hz⟩

/-- Full local subgroup structure for every actual infinite selector extension. -/
theorem fg_selector_subgroup_classification {S : Set Prime} (hS : S.Infinite)
    (L : AddSubgroup (selectorGroup S)) [AddGroup.FG L] :
    ∃ m : ℕ, 0 < m ∧ Squarefree m ∧
      (Nonempty (L ≃+ ZMod m) ∨ Nonempty (L ≃+ ℤ × ZMod m)) := by
  let f : L →+ ℚ := (selectorRational hS).comp L.subtype
  by_cases hzero : f.range = ⊥
  · have hz : ∀ x : L, selectorRational hS x.val = 0 := by
      intro x
      have hx : f x ∈ f.range := ⟨x, rfl⟩
      rw [hzero] at hx
      exact hx
    let : Finite L := fg_selector_subgroup_finite_of_rational_zero hS L hz
    obtain ⟨m, hm, hs, he⟩ := finite_embedded_preimage_classification
      (selectorLine S) L L.subtype Subtype.val_injective
    exact ⟨m, hm, hs, Or.inl he⟩
  · obtain ⟨e⟩ := rational_fg_equiv_int f.range hzero
    let g : L →+ ℤ := e.toAddMonoidHom.comp f.rangeRestrict
    have hg : Function.Surjective g := e.surjective.comp f.rangeRestrict_surjective
    have hker : ∀ x : L, g x = 0 → selectorRational hS x.val = 0 := by
      intro x hx
      change e (f.rangeRestrict x) = 0 at hx
      have hx' : e (f.rangeRestrict x) = e 0 := hx.trans (map_zero e).symm
      have h := congrArg (fun y : f.range => y.val) (e.injective hx')
      exact h
    obtain ⟨m, hm, hs, he⟩ := fg_selector_subgroup_integer_classification hS L g hg hker
    exact ⟨m, hm, hs, Or.inr he⟩

/-- Monograph 5.5, with C_1 represented by the trivial group ZMod 1. -/
theorem paired_fg_subgroup_classification (a : ℕ → Bool)
    (L : AddSubgroup (pairedGroup a)) (hL : L.FG) :
    ∃ m : ℕ, 0 < m ∧ Squarefree m ∧
      (Nonempty (L ≃+ ZMod m) ∨ Nonempty (L ≃+ ℤ × ZMod m)) := by
  exact @fg_selector_subgroup_classification (pairedSelector a) (pairedSelector_infinite a) L
    ((AddGroup.fg_iff_addSubgroup_fg L).mpr hL)

end RealizationBoundaries
