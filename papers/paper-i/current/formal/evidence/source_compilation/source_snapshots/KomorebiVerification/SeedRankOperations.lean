import KomorebiVerification.SeedRankBasics

/-!
# Seed-rank operations for Paper I

This file completes the finite algebraic seed-rank operations used in Paper I:
the finite free-presentation minimum, unrestricted cyclicity, semilinear
quotient monotonicity and image-algebra invariance, shared and independent
direct sums, the tensor-product bound for the natural operator action, and the
scalar-quotient obstruction.
-/

set_option autoImplicit false

-- Keep theorem bodies stable in this audit release while making the build warning-fatal.
set_option linter.unnecessarySimpa false
set_option linter.style.haveILetI false
set_option linter.unusedSectionVars false

namespace Komorebi.SeedRankOperations

open Cardinal Set
open Komorebi.SeedRankBasics
open scoped TensorProduct

universe u

section FiniteFreePresentation

variable (A M : Type u)
variable [Semiring A] [AddCommMonoid M] [Module A M]

/-- A finite module admits a generating family indexed by its seed finrank. -/
theorem exists_minimal_fin_family [Module.Finite A M] :
    ∃ v : Fin (seedFinrank A M) → M, FamilyGenerates A M v := by
  classical
  obtain ⟨s, hsCard, hsSpan⟩ :=
    Submodule.FG.exists_span_finset_card_eq_spanFinrank
      (R := A) (M := M) Module.Finite.fg_top
  have hcard : seedFinrank A M = s.card := by
    simpa [seedFinrank] using hsCard.symm
  let e : Fin (seedFinrank A M) ≃ s :=
    (Equiv.cast (congrArg Fin hcard)).trans s.equivFin.symm
  refine ⟨fun i ↦ (e i : M), ?_⟩
  rw [FamilyGenerates, Generates]
  have hrange : Set.range (fun i ↦ (e i : M)) = (s : Set M) := by
    ext x
    constructor
    · rintro ⟨i, rfl⟩
      exact (e i).property
    · intro hx
      have hx' : x ∈ s := by simpa using hx
      let sx : s := ⟨x, hx'⟩
      exact ⟨e.symm sx, by simp [sx]⟩
  rw [hrange]
  simpa using hsSpan

/--
The seed finrank is the least finite rank of a free module admitting a
surjective presentation map onto a finite module.
-/
theorem seedFinrank_isLeast_free_surjection [Module.Finite A M] :
    IsLeast
      {n : ℕ | ∃ f : (Fin n →₀ A) →ₗ[A] M, Function.Surjective f}
      (seedFinrank A M) := by
  constructor
  · obtain ⟨v, hv⟩ := exists_minimal_fin_family A M
    exact ⟨multiSeedMap A M v, (familyGenerates_iff_surjective A M v).mp hv⟩
  · intro n hn
    obtain ⟨f, hf⟩ := hn
    have hrank : seedRank A M ≤ seedRank A (Fin n →₀ A) :=
      seedRank_le_of_surjective f hf
    have hfree : seedRank A (Fin n →₀ A) ≤ n := by
      let v : Fin n → (Fin n →₀ A) :=
        (Finsupp.basisSingleOne : Module.Basis (Fin n) A (Fin n →₀ A))
      have hv : FamilyGenerates A (Fin n →₀ A) v := by
        rw [FamilyGenerates, Generates]
        simpa [v] using
          (Finsupp.basisSingleOne : Module.Basis (Fin n) A (Fin n →₀ A)).span_eq
      simpa using seedRank_le_mk_of_familyGenerates A (Fin n →₀ A) hv
    have hcard : (seedFinrank A M : Cardinal) ≤ n := by
      rw [← seedRank_eq_seedFinrank A M]
      exact hrank.trans hfree
    exact_mod_cast hcard

end FiniteFreePresentation

section Cyclicity

variable (A M : Type u)
variable [Semiring A] [AddCommMonoid M] [Module A M] [Nontrivial M]

/-- For every nonzero module, cardinal seed rank one is exactly cyclicity. -/
theorem cyclic_iff_seedRank_eq_one :
    Cyclic A M ↔ seedRank A M = 1 := by
  constructor
  · intro hcyc
    have hle : seedRank A M ≤ 1 := by
      obtain ⟨x, hx⟩ := hcyc
      simpa using seedRank_le_mk_of_generates A M hx
    have hne : seedRank A M ≠ 0 := by
      intro hzero
      have hs : Subsingleton M := (seedRank_eq_zero_iff A M).mp hzero
      exact not_subsingleton M hs
    exact hle.antisymm (Cardinal.one_le_iff_ne_zero.mpr hne)
  · intro hrank
    have hfinite : Module.Finite A M :=
      (seedRank_lt_aleph0_iff A M).mp (by simpa [hrank])
    letI : Module.Finite A M := hfinite
    exact (seedRank_eq_one_iff_cyclic A M).mp hrank

end Cyclicity

section SemilinearFunctoriality

variable {A B M N : Type u}
variable [Semiring A] [Semiring B]
variable [AddCommMonoid M] [Module A M]
variable [AddCommMonoid N] [Module B N]
variable {σ : A →+* B}

/--
Seed rank cannot increase under a surjective semilinear map, with no
surjectivity hypothesis on the scalar homomorphism.  The image of a minimal
generating set already spans the target over `B` because its `B`-span contains
all finite combinations whose coefficients lie in the image of `σ`.
-/
theorem seedRank_le_of_surjective_semilinear (f : M →ₛₗ[σ] N)
    (hf : Function.Surjective f) :
    seedRank B N ≤ seedRank A M := by
  classical
  obtain ⟨s, hs, hsCard⟩ := exists_generating_set_card_eq_seedRank A M
  have himage : Generates B N (f '' s) := by
    rw [Generates]
    apply top_unique
    intro y _
    obtain ⟨x, rfl⟩ := hf y
    have hx : x ∈ Submodule.span A s := by
      rw [hs]
      trivial
    refine Submodule.span_induction
      (p := fun x _ ↦ f x ∈ Submodule.span B (f '' s)) ?_ ?_ ?_ ?_ hx
    · intro x hxs
      exact Submodule.subset_span ⟨x, hxs, rfl⟩
    · simpa using (Submodule.zero_mem (Submodule.span B (f '' s)))
    · intro x y _ _ hx' hy'
      simpa using (Submodule.add_mem (Submodule.span B (f '' s)) hx' hy')
    · intro a x _ hx'
      simpa using (Submodule.smul_mem (Submodule.span B (f '' s)) (σ a) hx')
  calc
    seedRank B N ≤ Cardinal.mk (f '' s) :=
      seedRank_le_mk_of_generates B N himage
    _ ≤ Cardinal.mk s := Cardinal.mk_image_le
    _ = seedRank A M := hsCard

/--
If the scalar map is onto and the semilinear intertwiner is bijective, seed
rank is invariant.  Taking `B` to be the image of an algebra map is the
image-algebra form of Paper I's invariance statement.
-/
theorem seedRank_eq_of_bijective_semilinear (f : M →ₛₗ[σ] N)
    [RingHomSurjective σ]
    (hf : Function.Bijective f) :
    seedRank A M = seedRank B N := by
  rw [seedRank, seedRank]
  calc
    (⊤ : Submodule A M).spanRank = (Submodule.map f ⊤).spanRank :=
      (Submodule.spanRank_map_eq_of_injective f hf.injective ⊤).symm
    _ = (⊤ : Submodule B N).spanRank := by
      rw [Submodule.map_top, LinearMap.range_eq_top.mpr hf.surjective]

end SemilinearFunctoriality

section ImageAlgebraInvariance

variable {k A B M N : Type u}
variable [CommSemiring k]
variable [Semiring A] [Algebra k A]
variable [Semiring B] [Algebra k B]
variable [AddCommMonoid M] [Module A M]
variable [AddCommMonoid N] [Module B N]

/--
Literal image-algebra invariance from Paper I.  The target is restricted from
`B` to the subalgebra `φ.range`; a bijective `φ`-semilinear intertwiner then
preserves seed rank exactly.  No surjectivity of `φ : A →ₐ[k] B` is assumed.
-/
theorem seedRank_imageAlgebra_eq
    (φ : A →ₐ[k] B) (f : M →ₛₗ[φ.toRingHom] N)
    (hf : Function.Bijective f) :
    letI : Module φ.range N := Module.compHom N φ.range.val.toRingHom
    seedRank A M = seedRank φ.range N := by
  letI : Module φ.range N := Module.compHom N φ.range.val.toRingHom
  let fRange : M →ₛₗ[φ.rangeRestrict.toRingHom] N :=
    { toFun := f
      map_add' := f.map_add
      map_smul' := fun a x ↦ by
        change f (a • x) = (↑(φ.rangeRestrict a) : B) • f x
        simpa using f.map_smulₛₗ a x }
  letI : RingHomSurjective φ.rangeRestrict.toRingHom :=
    ⟨φ.rangeRestrict_surjective⟩
  exact seedRank_eq_of_bijective_semilinear fRange hf

end ImageAlgebraInvariance

section SharedDirectSum

variable (A M N : Type u)
variable [Semiring A]
variable [AddCommMonoid M] [Module A M]
variable [AddCommMonoid N] [Module A N]

private theorem sharedSum_familyGenerates
    {ι κ : Type u} {v : ι → M} {w : κ → N}
    (hv : FamilyGenerates A M v) (hw : FamilyGenerates A N w) :
    FamilyGenerates A (M × N)
      (Sum.elim (fun i ↦ (v i, 0)) (fun j ↦ (0, w j))) := by
  rw [FamilyGenerates, Generates] at hv hw
  let z : ι ⊕ κ → M × N :=
    Sum.elim (fun i ↦ (v i, 0)) (fun j ↦ (0, w j))
  let p : Submodule A (M × N) := Submodule.span A (Set.range z)
  change p = ⊤
  have hleft : ∀ x : M, (x, 0) ∈ p := by
    intro x
    have hx : x ∈ Submodule.span A (Set.range v) := by simpa [hv]
    refine Submodule.span_induction (p := fun x _ ↦ (x, 0) ∈ p) ?_ ?_ ?_ ?_ hx
    · intro x hxv
      obtain ⟨i, rfl⟩ := hxv
      exact Submodule.subset_span ⟨Sum.inl i, rfl⟩
    · exact p.zero_mem
    · intro x y _ _ hx' hy'
      simpa using p.add_mem hx' hy'
    · intro a x _ hx'
      simpa using p.smul_mem a hx'
  have hright : ∀ y : N, (0, y) ∈ p := by
    intro y
    have hy : y ∈ Submodule.span A (Set.range w) := by simpa [hw]
    refine Submodule.span_induction (p := fun y _ ↦ (0, y) ∈ p) ?_ ?_ ?_ ?_ hy
    · intro y hyw
      obtain ⟨j, rfl⟩ := hyw
      exact Submodule.subset_span ⟨Sum.inr j, rfl⟩
    · exact p.zero_mem
    · intro x y _ _ hx' hy'
      simpa using p.add_mem hx' hy'
    · intro a y _ hy'
      simpa using p.smul_mem a hy'
  apply top_unique
  rintro ⟨x, y⟩ _
  simpa using p.add_mem (hleft x) (hright y)

/-- One diagonally acting algebra gives the shared direct-sum upper bound. -/
theorem seedRank_prod_le_add :
    seedRank A (M × N) ≤ seedRank A M + seedRank A N := by
  classical
  obtain ⟨s, hs, hsCard⟩ := exists_generating_set_card_eq_seedRank A M
  obtain ⟨t, ht, htCard⟩ := exists_generating_set_card_eq_seedRank A N
  let v : s → M := Subtype.val
  let w : t → N := Subtype.val
  have hv : FamilyGenerates A M v := by
    simpa [FamilyGenerates, Generates, v] using hs
  have hw : FamilyGenerates A N w := by
    simpa [FamilyGenerates, Generates, w] using ht
  have hgen := sharedSum_familyGenerates A M N hv hw
  have hbound := seedRank_le_mk_of_familyGenerates A (M × N) hgen
  simpa [Cardinal.mk_sum, hsCard, htCard] using hbound

end SharedDirectSum

section IndependentDirectSum

variable (A B M N : Type u)
variable [Semiring A] [Semiring B]
variable [AddCommMonoid M] [Module A M]
variable [AddCommMonoid N] [Module B N]

/-- The coordinatewise action of `A × B` on `M × N`. -/
local instance productModule : Module (A × B) (M × N) where
  smul r x := (r.1 • x.1, r.2 • x.2)
  one_smul x := by
    change ((1 : A) • x.1, (1 : B) • x.2) = x
    ext <;> simp
  mul_smul r s x := by
    change ((r.1 * s.1) • x.1, (r.2 * s.2) • x.2) =
      (r.1 • s.1 • x.1, r.2 • s.2 • x.2)
    ext <;> simp [mul_smul]
  smul_add r x y := by
    change (r.1 • (x.1 + y.1), r.2 • (x.2 + y.2)) =
      (r.1 • x.1 + r.1 • y.1, r.2 • x.2 + r.2 • y.2)
    ext <;> simp [smul_add]
  add_smul r s x := by
    change ((r.1 + s.1) • x.1, (r.2 + s.2) • x.2) =
      (r.1 • x.1 + s.1 • x.1, r.2 • x.2 + s.2 • x.2)
    ext <;> simp [add_smul]
  zero_smul x := by
    change ((0 : A) • x.1, (0 : B) • x.2) = 0
    ext <;> simp
  smul_zero r := by
    change (r.1 • (0 : M), r.2 • (0 : N)) = 0
    ext <;> simp

@[simp] private theorem product_smul_mk (a : A) (b : B) (x : M) (y : N) :
    (a, b) • (x, y) = (a • x, b • y) := rfl

/-- First projection as a semilinear map along `(A × B) → A`. -/
def prodFstSemilinear :
    (M × N) →ₛₗ[RingHom.fst A B] M where
  toFun := Prod.fst
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

/-- Second projection as a semilinear map along `(A × B) → B`. -/
def prodSndSemilinear :
    (M × N) →ₛₗ[RingHom.snd A B] N where
  toFun := Prod.snd
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

private theorem product_familyGenerates
    {ι : Type u} {v : ι → M} {w : ι → N}
    (hv : FamilyGenerates A M v) (hw : FamilyGenerates B N w) :
    FamilyGenerates (A × B) (M × N) (fun i ↦ (v i, w i)) := by
  rw [FamilyGenerates, Generates] at hv hw
  let z : ι → M × N := fun i ↦ (v i, w i)
  let p : Submodule (A × B) (M × N) := Submodule.span (A × B) (Set.range z)
  change p = ⊤
  have hleft : ∀ x : M, (x, 0) ∈ p := by
    intro x
    have hx : x ∈ Submodule.span A (Set.range v) := by simpa [hv]
    refine Submodule.span_induction (p := fun x _ ↦ (x, 0) ∈ p) ?_ ?_ ?_ ?_ hx
    · intro x hxv
      obtain ⟨i, rfl⟩ := hxv
      have hz : z i ∈ p := Submodule.subset_span (Set.mem_range_self i)
      have hmem := p.smul_mem (1, 0) hz
      simpa [z] using hmem
    · exact p.zero_mem
    · intro x y _ _ hx' hy'
      simpa using p.add_mem hx' hy'
    · intro a x _ hx'
      have hmem := p.smul_mem (a, 0) hx'
      simpa using hmem
  have hright : ∀ y : N, (0, y) ∈ p := by
    intro y
    have hy : y ∈ Submodule.span B (Set.range w) := by simpa [hw]
    refine Submodule.span_induction (p := fun y _ ↦ (0, y) ∈ p) ?_ ?_ ?_ ?_ hy
    · intro y hyw
      obtain ⟨i, rfl⟩ := hyw
      have hz : z i ∈ p := Submodule.subset_span (Set.mem_range_self i)
      have hmem := p.smul_mem (0, 1) hz
      simpa [z] using hmem
    · exact p.zero_mem
    · intro x y _ _ hx' hy'
      simpa using p.add_mem hx' hy'
    · intro b y _ hy'
      have hmem := p.smul_mem (0, b) hy'
      simpa using hmem
  apply top_unique
  rintro ⟨x, y⟩ _
  simpa using p.add_mem (hleft x) (hright y)

private theorem seedRank_prod_le_right_of_le
    (hMN : seedRank A M ≤ seedRank B N) :
    seedRank (A × B) (M × N) ≤ seedRank B N := by
  classical
  obtain ⟨s, hs, hsCard⟩ := exists_generating_set_card_eq_seedRank A M
  obtain ⟨t, ht, htCard⟩ := exists_generating_set_card_eq_seedRank B N
  have hst : Cardinal.mk s ≤ Cardinal.mk t := by simpa [hsCard, htCard] using hMN
  let e : s ↪ t := Classical.choice (Cardinal.lift_mk_le'.mp (by simpa using hst))
  let v : t → M := Function.extend e (fun i : s ↦ (i : M)) (fun _ ↦ 0)
  let w : t → N := fun j ↦ (j : N)
  have hv : FamilyGenerates A M v := by
    rw [FamilyGenerates, Generates]
    apply top_unique
    rw [← hs]
    apply Submodule.span_mono
    intro x hx
    let i : s := ⟨x, hx⟩
    refine ⟨e i, ?_⟩
    simpa [v, i] using
      e.injective.extend_apply (fun i : s ↦ (i : M)) (fun _ : t ↦ 0) i
  have hw : FamilyGenerates B N w := by
    simpa [FamilyGenerates, Generates, w] using ht
  have hgen := product_familyGenerates A B M N hv hw
  have hbound := seedRank_le_mk_of_familyGenerates (A × B) (M × N) hgen
  simpa [htCard] using hbound

private theorem seedRank_prod_le_left_of_le
    (hNM : seedRank B N ≤ seedRank A M) :
    seedRank (A × B) (M × N) ≤ seedRank A M := by
  classical
  obtain ⟨s, hs, hsCard⟩ := exists_generating_set_card_eq_seedRank A M
  obtain ⟨t, ht, htCard⟩ := exists_generating_set_card_eq_seedRank B N
  have hts : Cardinal.mk t ≤ Cardinal.mk s := by simpa [hsCard, htCard] using hNM
  let e : t ↪ s := Classical.choice (Cardinal.lift_mk_le'.mp (by simpa using hts))
  let v : s → M := fun i ↦ (i : M)
  let w : s → N := Function.extend e (fun j : t ↦ (j : N)) (fun _ ↦ 0)
  have hv : FamilyGenerates A M v := by
    simpa [FamilyGenerates, Generates, v] using hs
  have hw : FamilyGenerates B N w := by
    rw [FamilyGenerates, Generates]
    apply top_unique
    rw [← ht]
    apply Submodule.span_mono
    intro y hy
    let j : t := ⟨y, hy⟩
    refine ⟨e j, ?_⟩
    simpa [w, j] using
      e.injective.extend_apply (fun j : t ↦ (j : N)) (fun _ : s ↦ 0) j
  have hgen := product_familyGenerates A B M N hv hw
  have hbound := seedRank_le_mk_of_familyGenerates (A × B) (M × N) hgen
  simpa [hsCard] using hbound

/-- Under the independent product action, seed rank is the maximum. -/
theorem seedRank_prod_productAlgebra :
    seedRank (A × B) (M × N) = max (seedRank A M) (seedRank B N) := by
  apply le_antisymm
  · rcases le_total (seedRank A M) (seedRank B N) with hMN | hNM
    · simpa [max_eq_right hMN] using
        seedRank_prod_le_right_of_le A B M N hMN
    · simpa [max_eq_left hNM] using
        seedRank_prod_le_left_of_le A B M N hNM
  · apply max_le
    · exact seedRank_le_of_surjective_semilinear
        (prodFstSemilinear A B M N) (fun x ↦ ⟨(x, 0), rfl⟩)
    · exact seedRank_le_of_surjective_semilinear
        (prodSndSemilinear A B M N) (fun y ↦ ⟨(0, y), rfl⟩)

end IndependentDirectSum

section TensorProduct

variable (k A B X Y : Type u)
variable [CommSemiring k]
variable [Semiring A] [Algebra k A]
variable [Semiring B] [Algebra k B]
variable [AddCommMonoid X] [Module k X] [Module A X]
variable [IsScalarTower k A X] [SMulCommClass k A X]
variable [AddCommMonoid Y] [Module k Y] [Module B Y]
variable [IsScalarTower k B Y] [SMulCommClass k B Y]

/-- The action of `B` on the right tensor factor. -/
@[instance_reducible] private def tensorRightModule :
    Module B (TensorProduct k X Y) := by
  let e : TensorProduct k X Y ≃ₗ[k] TensorProduct k Y X :=
    TensorProduct.comm k X Y
  letI : Module B (TensorProduct k Y X) := TensorProduct.leftModule
  exact
    { smul := fun b z ↦ e.symm (b • e z)
      one_smul := fun z ↦ by
        change e.symm ((1 : B) • e z) = z
        rw [one_smul, e.symm_apply_apply]
      mul_smul := fun b c z ↦ by
        change e.symm ((b * c) • e z) =
          e.symm (b • e (e.symm (c • e z)))
        rw [mul_smul, e.apply_symm_apply]
      smul_add := fun b z w ↦ by
        change e.symm (b • e (z + w)) =
          e.symm (b • e z) + e.symm (b • e w)
        rw [e.map_add, smul_add, e.symm.map_add]
      add_smul := fun b c z ↦ by
        change e.symm ((b + c) • e z) =
          e.symm (b • e z) + e.symm (c • e z)
        rw [add_smul, e.symm.map_add]
      zero_smul := fun z ↦ by
        change e.symm ((0 : B) • e z) = 0
        rw [zero_smul, map_zero]
      smul_zero := fun b ↦ by
        change e.symm (b • e 0) = 0
        rw [map_zero, smul_zero, map_zero] }

local instance (priority := 50) tensorRightModuleInstance :
    Module B (TensorProduct k X Y) :=
  tensorRightModule k B X Y

@[simp] private theorem tensorRight_smul_tmul (b : B) (x : X) (y : Y) :
    b • (x ⊗ₜ[k] y) = x ⊗ₜ[k] (b • y) := by
  change (TensorProduct.comm k X Y).symm
      (b • (TensorProduct.comm k X Y) (x ⊗ₜ[k] y)) = _
  rw [TensorProduct.comm_tmul, TensorProduct.smul_tmul',
    TensorProduct.comm_symm_tmul]

local instance tensorRightTower :
    IsScalarTower k B (TensorProduct k X Y) where
  smul_assoc r b z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y => simp [smul_assoc]
    | add z w hz hw => simp [smul_add, hz, hw]

local instance tensorLeftTower :
    IsScalarTower k A (TensorProduct k X Y) where
  smul_assoc r a z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y => simp [TensorProduct.smul_tmul', smul_assoc]
    | add z w hz hw => simp [smul_add, hz, hw]

local instance tensorActionsCommute :
    SMulCommClass A B (TensorProduct k X Y) where
  smul_comm a b z := by
    induction z using TensorProduct.induction_on with
    | zero => simp
    | tmul x y => simp [TensorProduct.smul_tmul']
    | add z w hz hw => simp [smul_add, hz, hw]

attribute [local instance 2000] tensorLeftTower tensorRightTower tensorActionsCommute

local instance tensorLeftTowerInstalled :
    IsScalarTower k A (TensorProduct k X Y) :=
  tensorLeftTower k A X Y

local instance tensorRightTowerInstalled :
    IsScalarTower k B (TensorProduct k X Y) :=
  tensorRightTower k B X Y

local instance tensorActionsCommuteInstalled :
    SMulCommClass A B (TensorProduct k X Y) :=
  tensorActionsCommute k A B X Y

/-- The natural `(A ⊗[k] B)` action on `X ⊗[k] Y`. -/
local instance tensorOperatorModule :
    Module (A ⊗[k] B) (TensorProduct k X Y) :=
  TensorProduct.Algebra.module

/-- Pure operator tensors act componentwise on pure vector tensors. -/
@[simp] theorem tensorOperator_smul_tmul
    (a : A) (b : B) (x : X) (y : Y) :
    (a ⊗ₜ[k] b : A ⊗[k] B) • (x ⊗ₜ[k] y) =
      (a • x) ⊗ₜ[k] (b • y) := by
  change TensorProduct.Algebra.moduleAux (a ⊗ₜ[k] b) (x ⊗ₜ[k] y) = _
  rw [TensorProduct.Algebra.moduleAux_apply]
  simp [TensorProduct.smul_tmul']

private theorem tensor_familyGenerates
    {ι κ : Type u} {v : ι → X} {w : κ → Y}
    (hv : FamilyGenerates A X v) (hw : FamilyGenerates B Y w) :
    FamilyGenerates (A ⊗[k] B) (TensorProduct k X Y)
      (fun p : ι × κ ↦ v p.1 ⊗ₜ[k] w p.2) := by
  rw [FamilyGenerates, Generates] at hv hw
  let z : ι × κ → TensorProduct k X Y :=
    fun p ↦ v p.1 ⊗ₜ[k] w p.2
  let p : Submodule (A ⊗[k] B) (TensorProduct k X Y) :=
    Submodule.span (A ⊗[k] B) (Set.range z)
  change p = ⊤
  have hpure : ∀ x : X, ∀ y : Y, x ⊗ₜ[k] y ∈ p := by
    intro x
    have hx : x ∈ Submodule.span A (Set.range v) := by simpa [hv]
    refine Submodule.span_induction
      (p := fun x _ ↦ ∀ y : Y, x ⊗ₜ[k] y ∈ p) ?_ ?_ ?_ ?_ hx
    · intro x hxv y
      obtain ⟨i, rfl⟩ := hxv
      have hy : y ∈ Submodule.span B (Set.range w) := by simpa [hw]
      refine Submodule.span_induction
        (p := fun y _ ↦ v i ⊗ₜ[k] y ∈ p) ?_ ?_ ?_ ?_ hy
      · intro y hyw
        obtain ⟨j, rfl⟩ := hyw
        exact Submodule.subset_span ⟨(i, j), rfl⟩
      · simpa using p.zero_mem
      · intro y₁ y₂ _ _ h₁ h₂
        simpa [TensorProduct.tmul_add] using p.add_mem h₁ h₂
      · intro b y _ hy'
        have hmem := p.smul_mem (1 ⊗ₜ[k] b : A ⊗[k] B) hy'
        simpa using hmem
    · intro y
      simpa using p.zero_mem
    · intro x₁ x₂ _ _ h₁ h₂ y
      simpa [TensorProduct.add_tmul] using p.add_mem (h₁ y) (h₂ y)
    · intro a x _ hx' y
      have hmem := p.smul_mem (a ⊗ₜ[k] 1 : A ⊗[k] B) (hx' y)
      simpa using hmem
  apply top_unique
  intro q _
  exact TensorProduct.induction_on q p.zero_mem hpure
    (fun _ _ hq hr ↦ p.add_mem hq hr)

/--
For the natural operator-tensor action, tensor-product seed rank is bounded by
the product of the two seed ranks.
-/
theorem seedRank_tensorProduct_le_mul :
    seedRank (A ⊗[k] B) (TensorProduct k X Y) ≤
      seedRank A X * seedRank B Y := by
  classical
  obtain ⟨s, hs, hsCard⟩ := exists_generating_set_card_eq_seedRank A X
  obtain ⟨t, ht, htCard⟩ := exists_generating_set_card_eq_seedRank B Y
  let v : s → X := Subtype.val
  let w : t → Y := Subtype.val
  have hv : FamilyGenerates A X v := by
    simpa [FamilyGenerates, Generates, v] using hs
  have hw : FamilyGenerates B Y w := by
    simpa [FamilyGenerates, Generates, w] using ht
  have hgen := tensor_familyGenerates k A B X Y hv hw
  have hbound := seedRank_le_mk_of_familyGenerates
    (A ⊗[k] B) (TensorProduct k X Y) hgen
  simpa [Cardinal.mk_prod, hsCard, htCard] using hbound

end TensorProduct

section ScalarQuotient

variable (k A X Y : Type u)
variable [Field k] [Semiring A] [Algebra k A]
variable [AddCommMonoid X] [Module A X]
variable [AddCommGroup Y] [Module k Y] [Module.Finite k Y]

/-- Every algebra character onto its base field is surjective. -/
private theorem character_surjective (χ : A →ₐ[k] k) :
    Function.Surjective χ := by
  intro y
  refine ⟨algebraMap k A y, ?_⟩
  exact χ.commutes y

/--
Scalar quotient obstruction.  A character `χ : A →ₐ[k] k` records that every
operator acts on the quotient through a scalar.  Any surjective intertwiner
onto a finite-dimensional scalar module forces its dimension to be a lower
bound for the seed rank upstairs.
-/
theorem finrank_le_seedRank_of_scalar_quotient
    (χ : A →ₐ[k] k) (f : X →ₛₗ[χ.toRingHom] Y)
    (hf : Function.Surjective f) :
    (Module.finrank k Y : Cardinal) ≤ seedRank A X := by
  letI : RingHomSurjective χ.toRingHom :=
    ⟨character_surjective k A χ⟩
  have hquot : seedRank k Y ≤ seedRank A X :=
    seedRank_le_of_surjective_semilinear f hf
  have hrank : seedRank k Y = Module.finrank k Y := by
    rw [seedRank_eq_seedFinrank k Y, seedFinrank,
      ← Module.finrank_eq_spanFinrank_of_free]
  simpa [hrank] using hquot

end ScalarQuotient

end Komorebi.SeedRankOperations

#print axioms Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection
#print axioms Komorebi.SeedRankOperations.cyclic_iff_seedRank_eq_one
#print axioms Komorebi.SeedRankOperations.seedRank_le_of_surjective_semilinear
#print axioms Komorebi.SeedRankOperations.seedRank_eq_of_bijective_semilinear
#print axioms Komorebi.SeedRankOperations.seedRank_imageAlgebra_eq
#print axioms Komorebi.SeedRankOperations.seedRank_prod_le_add
#print axioms Komorebi.SeedRankOperations.seedRank_prod_productAlgebra
#print axioms Komorebi.SeedRankOperations.seedRank_tensorProduct_le_mul
#print axioms Komorebi.SeedRankOperations.finrank_le_seedRank_of_scalar_quotient
