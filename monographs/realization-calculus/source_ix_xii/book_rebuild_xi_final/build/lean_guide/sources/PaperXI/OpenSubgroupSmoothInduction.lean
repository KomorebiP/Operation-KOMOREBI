import PaperXI.SmoothDegreeQuotient
import Mathlib.RepresentationTheory.FiniteIndex
import Mathlib.Topology.Algebra.OpenSubgroup
import Mathlib.Algebra.BigOperators.Finprod

/-!
# Smooth induction from an open subgroup, with no finite-index hypothesis

The target is the actual algebraic induced representation `Representation.ind`.
For an open subgroup and a smooth inducing action, its finite-sum vectors are
smooth even when the subgroup has infinite index. This is an existence step
towards compact induction, not an irreducibility or local-factor theorem.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OpenSubgroupSmoothInduction

open Representation PaperXI.SmoothDegreeQuotient

variable {k G V : Type*} [Field k] [Group G]
  [TopologicalSpace G] [IsTopologicalGroup G]
  [AddCommGroup V] [Module k V]

/-- Smooth vectors in any algebraic representation form a linear subspace. -/
def smoothSubmodule (ρ : Representation k G V) : Submodule k V where
  carrier := {v | IsOpen (vectorStabilizer ρ v : Set G)}
  zero_mem' := by
    change IsOpen (vectorStabilizer ρ 0 : Set G)
    have h : (vectorStabilizer ρ 0 : Set G) = Set.univ := by
      ext g
      simp
    rw [h]
    exact isOpen_univ
  add_mem' := by
    intro v w hv hw
    apply Subgroup.isOpen_mono (H₁ := vectorStabilizer ρ v ⊓ vectorStabilizer ρ w)
      _ (hv.inter hw)
    intro g hg
    change ρ g (v + w) = v + w
    rw [map_add, hg.1, hg.2]
  smul_mem' := by
    intro a v hv
    apply Subgroup.isOpen_mono (H₁ := vectorStabilizer ρ v) _ hv
    intro g hg
    change ρ g (a • v) = a • v
    rw [map_smul, hg]

@[simp] theorem mem_smoothSubmodule (ρ : Representation k G V) (v : V) :
    v ∈ smoothSubmodule ρ ↔ IsOpen (vectorStabilizer ρ v : Set G) := Iff.rfl

variable (H : Subgroup G) (σ : Representation k H V)

local instance : DecidableRel (QuotientGroup.rightRel H) := Classical.decRel _

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The actual coinvariant relation, with the subgroup action kept explicit. -/
theorem mk_subgroup (h : H) (g : G) (v : V) :
    IndV.mk H.subtype σ ((h : G)⁻¹ * g) v = IndV.mk H.subtype σ g (σ h v) := by
  have hh := Coinvariants.mk_inv_tmul
    ((Representation.leftRegular k G).comp H.subtype)
    σ (MonoidAlgebra.single g 1) v h
  simpa using hh

/-- Each elementary induced vector has an open conjugate stabilizer. -/
theorem mk_smooth (hH : IsOpen (H : Set G)) (hσ : IsSmooth σ) (g : G) (v : V) :
    IsOpen (vectorStabilizer (ind H.subtype σ) (IndV.mk H.subtype σ g v) : Set G) := by
  let U := (vectorStabilizer σ v).map H.subtype
  have hU : IsOpen (U : Set G) := hH.isOpenMap_subtype_val _ (hσ v)
  let C := U.comap (MulAut.conj g).toMonoidHom
  have hC : IsOpen (C : Set G) :=
    hU.preimage ((continuous_const.mul continuous_id).mul continuous_const)
  apply Subgroup.isOpen_mono (H₁ := C) _ hC
  intro t ht
  obtain ⟨h, hh, he⟩ := ht
  have he' : (h : G) = g * t * g⁻¹ := he
  have hgt : g * t⁻¹ = (h : G)⁻¹ * g := by
    rw [he']
    group
  change ind H.subtype σ t (IndV.mk H.subtype σ g v) = _
  rw [ind_mk, hgt, mk_subgroup, hh]

/-- Genuine algebraic induction from an open subgroup preserves smoothness,
without requiring finite index or a common open kernel for the inducing action. -/
theorem ind_isSmooth (hH : IsOpen (H : Set G)) (hσ : IsSmooth σ) :
    IsSmooth (ind H.subtype σ) := by
  let S := smoothSubmodule (ind H.subtype σ)
  have hq : S.mkQ = 0 := by
    apply IndV.hom_ext
    intro g
    ext v
    exact (Submodule.Quotient.mk_eq_zero S).mpr (mk_smooth H σ hH hσ g v)
  intro v
  change v ∈ S
  apply (Submodule.Quotient.mk_eq_zero S).mp
  exact LinearMap.congr_fun hq v

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The genuine induced vector is sent to its covariant function on `G`.
This Mathlib construction does not require finite index. -/
def functionModel : IndV H.subtype σ →ₗ[k] coindV H.subtype σ := by
  classical
  exact Rep.indToCoind (Rep.of σ)

omit [TopologicalSpace G] [IsTopologicalGroup G] in
@[simp] theorem functionModel_mk (g x : G) (v : V) :
    (functionModel H σ (IndV.mk H.subtype σ g v)).val x =
      Rep.indToCoindAux (Rep.of σ) g v x := by
  classical
  simp [functionModel, Rep.indToCoind]
  rfl

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- Evaluation on the supporting coset recovers the original coefficient. -/
@[simp] theorem functionModel_mk_self (g : G) (v : V) :
    (functionModel H σ (IndV.mk H.subtype σ g v)).val g = v := by
  classical
  rw [functionModel_mk]
  exact Rep.indToCoindAux_self (A := Rep.of σ) g v

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The inducing space embeds into actual induction at every group element. -/
theorem mk_injective (g : G) : Function.Injective (IndV.mk H.subtype σ g) := by
  intro v w hvw
  have h := congrArg (fun z => (functionModel H σ z).val g) hvw
  simpa only [functionModel_mk_self] using h

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- Nonzero inducing vectors remain nonzero in the actual induced module. -/
theorem mk_ne_zero (g : G) {v : V} (hv : v ≠ 0) : IndV.mk H.subtype σ g v ≠ 0 := by
  intro h
  apply hv
  apply mk_injective H σ g
  simpa using h

omit [TopologicalSpace G] [IsTopologicalGroup G] in
theorem ind_nontrivial [Nontrivial V] : Nontrivial (IndV H.subtype σ) :=
  (mk_injective H σ 1).nontrivial

/-- Covariant functions with support in finitely many right cosets of `H`. -/
def finiteCosetSupport : Submodule k (coindV H.subtype σ) := by
  classical
  exact
    { carrier := {f | ∃ s : Finset G, ∀ x, f.val x ≠ 0 →
          ∃ g ∈ s, (QuotientGroup.rightRel H).r x g}
      zero_mem' := by
        refine ⟨∅, ?_⟩
        intro x hx
        exact (hx rfl).elim
      add_mem' := by
        rintro f f' ⟨s, hs⟩ ⟨s', hs'⟩
        refine ⟨s ∪ s', ?_⟩
        intro x hx
        change f.val x + f'.val x ≠ 0 at hx
        by_cases hf : f.val x = 0
        · obtain ⟨g, hg, hr⟩ := hs' x (by simpa only [hf, zero_add] using hx)
          exact ⟨g, Finset.mem_union_right s hg, hr⟩
        · obtain ⟨g, hg, hr⟩ := hs x hf
          exact ⟨g, Finset.mem_union_left s' hg, hr⟩
      smul_mem' := by
        rintro a f ⟨s, hs⟩
        refine ⟨s, ?_⟩
        intro x hx
        apply hs x
        intro hf
        apply hx
        change a • f.val x = 0
        rw [hf, smul_zero] }

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The image of each actual induced vector has finite support modulo `H`.
This is support on the right-coset space `H\G`, without a finite-index assumption. -/
theorem functionModel_finite_support (z : IndV H.subtype σ) :
    ∃ s : Finset G, ∀ x, (functionModel H σ z).val x ≠ 0 →
      ∃ g ∈ s, (QuotientGroup.rightRel H).r x g := by
  classical
  let S := finiteCosetSupport H σ
  have hq : S.mkQ ∘ₗ functionModel H σ = 0 := by
    apply IndV.hom_ext
    intro g
    ext v
    apply (Submodule.Quotient.mk_eq_zero S).mpr
    refine ⟨{g}, ?_⟩
    intro x hx
    refine ⟨g, Finset.mem_singleton_self g, ?_⟩
    by_contra hr
    apply hx
    rw [functionModel_mk]
    exact Rep.indToCoindAux_of_not_rel (A := Rep.of σ) g x v hr
  have hz := LinearMap.congr_fun hq z
  exact (Submodule.Quotient.mk_eq_zero S).mp hz

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The literal image of the nonzero-value support in the right-coset quotient is finite. -/
theorem functionModel_finite_quotient_support (z : IndV H.subtype σ) :
    Set.Finite ((Quotient.mk (QuotientGroup.rightRel H)) ''
      Function.support (functionModel H σ z).val) := by
  obtain ⟨s, hs⟩ := functionModel_finite_support H σ z
  apply (s.finite_toSet.image (Quotient.mk (QuotientGroup.rightRel H))).subset
  rintro q ⟨x, hx, rfl⟩
  obtain ⟨g, hg, hr⟩ := hs x hx
  exact ⟨g, hg, (Quotient.sound hr).symm⟩

omit [IsTopologicalGroup G] in
/-- The support image in the actual topological right-coset quotient is compact. -/
theorem functionModel_compact_quotient_support (z : IndV H.subtype σ) :
    IsCompact ((Quotient.mk (QuotientGroup.rightRel H)) ''
      Function.support (functionModel H σ z).val) :=
  (functionModel_finite_quotient_support H σ z).isCompact

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The covariant-function construction respects the actual ambient group actions. -/
def functionIntertwiner : IntertwiningMap (ind H.subtype σ) (coind H.subtype σ) where
  toLinearMap := functionModel H σ
  isIntertwining' t := by
    apply IndV.hom_ext
    intro g
    ext v x
    change (functionModel H σ (ind H.subtype σ t (IndV.mk H.subtype σ g v))).val x =
      (functionModel H σ (IndV.mk H.subtype σ g v)).val (x * t)
    rw [ind_mk, functionModel_mk, functionModel_mk]
    exact Rep.indToCoindAux_fst_mul_inv (A := Rep.of σ) g t x v

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- Evaluation is a coefficient-extracting linear map on actual induced vectors. -/
def evaluate (x : G) : IndV H.subtype σ →ₗ[k] V :=
  (LinearMap.proj x) ∘ₗ (coindV H.subtype σ).subtype ∘ₗ functionModel H σ

omit [TopologicalSpace G] [IsTopologicalGroup G] in
@[simp] theorem evaluate_mk_self (g : G) (v : V) :
    evaluate H σ g (IndV.mk H.subtype σ g v) = v := functionModel_mk_self H σ g v

omit [TopologicalSpace G] [IsTopologicalGroup G] in
theorem evaluate_mk_of_not_rel (g x : G) (v : V)
    (h : ¬ (QuotientGroup.rightRel H).r x g) :
    evaluate H σ x (IndV.mk H.subtype σ g v) = 0 := by
  change (functionModel H σ (IndV.mk H.subtype σ g v)).val x = 0
  rw [functionModel_mk]
  exact Rep.indToCoindAux_of_not_rel (A := Rep.of σ) g x v h

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- Distinct right cosets supply linearly independent vectors in actual induction.
This prevents finite packet dimensions from being assigned to arbitrary-index induction. -/
theorem mk_linearIndependent {I : Type*} (r : I → G)
    (hr : Pairwise fun i j => ¬ (QuotientGroup.rightRel H).r (r i) (r j))
    {v : V} (hv : v ≠ 0) :
    LinearIndependent k (fun i => IndV.mk H.subtype σ (r i) v) := by
  classical
  apply linearIndependent_iff'.mpr
  intro s c hc i hi
  have he := congrArg (evaluate H σ (r i)) hc
  simp only [map_sum, map_smul, map_zero] at he
  have hs : (∑ j ∈ s, c j • evaluate H σ (r i) (IndV.mk H.subtype σ (r j) v)) =
      c i • v := by
    rw [Finset.sum_eq_single i]
    · rw [evaluate_mk_self]
    · intro j _ hji
      rw [evaluate_mk_of_not_rel H σ (r j) (r i) v (hr hji.symm), smul_zero]
    · exact fun h => (h hi).elim
  rw [hs] at he
  exact (smul_eq_zero.mp he).resolve_right hv

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- One coset contributes an induced vector independently of its representative. -/
def cosetComponent (f : coindV H.subtype σ) (q : Quotient (QuotientGroup.rightRel H)) :
    IndV H.subtype σ :=
  Quotient.liftOn q (fun g => IndV.mk H.subtype σ g (f.val g))
    fun g₁ g₂ ⟨s, (hs : _ * _ = _)⟩ =>
      (Submodule.Quotient.eq _).2 <| Coinvariants.mem_ker_of_eq s
        (MonoidAlgebra.single g₂ 1 ⊗ₜ[k] f.val g₂) _ <| by
          have := f.property s g₂
          simp_all

omit [TopologicalSpace G] [IsTopologicalGroup G] in
@[simp] theorem cosetComponent_mk (f : coindV H.subtype σ) (g : G) :
    cosetComponent H σ f (Quotient.mk (QuotientGroup.rightRel H) g) =
      IndV.mk H.subtype σ g (f.val g) := rfl

omit [TopologicalSpace G] [IsTopologicalGroup G] in
theorem cosetComponent_add (f f' : coindV H.subtype σ)
    (q : Quotient (QuotientGroup.rightRel H)) :
    cosetComponent H σ (f + f') q = cosetComponent H σ f q + cosetComponent H σ f' q := by
  induction q using Quotient.inductionOn with | h g =>
  exact map_add (IndV.mk H.subtype σ g) (f.val g) (f'.val g)

omit [TopologicalSpace G] [IsTopologicalGroup G] in
theorem cosetComponent_smul (a : k) (f : coindV H.subtype σ)
    (q : Quotient (QuotientGroup.rightRel H)) :
    cosetComponent H σ (a • f) q = a • cosetComponent H σ f q := by
  induction q using Quotient.inductionOn with | h g =>
  exact map_smul (IndV.mk H.subtype σ g) a (f.val g)

omit [TopologicalSpace G] [IsTopologicalGroup G] in
theorem cosetComponent_finite (f : finiteCosetSupport H σ) :
    Function.HasFiniteSupport (cosetComponent H σ f.val) := by
  obtain ⟨s, hs⟩ := f.property
  apply (s.finite_toSet.image (Quotient.mk (QuotientGroup.rightRel H))).subset
  rintro q hq
  induction q using Quotient.inductionOn with | h g =>
  have hfg : f.val.val g ≠ 0 := by
    intro hz
    apply hq
    change IndV.mk H.subtype σ g (f.val.val g) = 0
    rw [hz, map_zero]
  obtain ⟨g', hg', hr⟩ := hs g hfg
  exact ⟨g', hg', (Quotient.sound hr).symm⟩

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- Finite-support covariant functions reconstruct actual induced vectors. -/
def reconstruct : finiteCosetSupport H σ →ₗ[k] IndV H.subtype σ where
  toFun f := ∑ᶠ q, cosetComponent H σ f.val q
  map_add' f f' := by
    change (∑ᶠ q, cosetComponent H σ (f.val + f'.val) q) = _
    simp_rw [cosetComponent_add]
    exact finsum_add_distrib (cosetComponent_finite H σ f) (cosetComponent_finite H σ f')
  map_smul' a f := by
    change (∑ᶠ q, cosetComponent H σ (a • f.val) q) = _
    simp_rw [cosetComponent_smul]
    exact (smul_finsum' a (cosetComponent_finite H σ f)).symm

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The function map with its proved finite-support codomain. -/
def compactModel : IndV H.subtype σ →ₗ[k] finiteCosetSupport H σ :=
  (functionModel H σ).codRestrict _ (functionModel_finite_support H σ)

omit [TopologicalSpace G] [IsTopologicalGroup G] in
theorem reconstruct_compactModel :
    reconstruct H σ ∘ₗ compactModel H σ = LinearMap.id := by
  apply IndV.hom_ext
  intro g
  ext v
  change (∑ᶠ q, cosetComponent H σ (functionModel H σ (IndV.mk H.subtype σ g v)) q) = _
  rw [finsum_eq_single _ (Quotient.mk (QuotientGroup.rightRel H) g)]
  · rw [cosetComponent_mk, functionModel_mk_self]
    rfl
  · intro q hq
    induction q using Quotient.inductionOn with | h x =>
    rw [cosetComponent_mk, functionModel_mk,
      Rep.indToCoindAux_of_not_rel (A := Rep.of σ) g x v (fun hr => hq (Quotient.sound hr)),
      map_zero]

omit [TopologicalSpace G] [IsTopologicalGroup G] in
theorem compactModel_reconstruct :
    compactModel H σ ∘ₗ reconstruct H σ = LinearMap.id := by
  ext f x
  change evaluate H σ x (∑ᶠ q, cosetComponent H σ f.val q) = f.val.val x
  rw [map_finsum (evaluate H σ x) (cosetComponent_finite H σ f),
    finsum_eq_single _ (Quotient.mk (QuotientGroup.rightRel H) x)]
  · rw [cosetComponent_mk, evaluate_mk_self]
  · intro q hq
    induction q using Quotient.inductionOn with | h g =>
    rw [cosetComponent_mk]
    exact evaluate_mk_of_not_rel H σ g x (f.val.val g)
      (fun hr => hq (Quotient.sound hr).symm)

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- An actual linear equivalence with all finite-support covariant functions,
not just an injection of elementary inducing vectors. -/
def compactModelEquiv : IndV H.subtype σ ≃ₗ[k] finiteCosetSupport H σ :=
  LinearEquiv.ofLinearMap (compactModel H σ) (reconstruct H σ)
    (compactModel_reconstruct H σ) (reconstruct_compactModel H σ)

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- The function model is faithful for arbitrary subgroup index. -/
theorem functionModel_injective : Function.Injective (functionModel H σ) := by
  intro z w hzw
  apply (compactModelEquiv H σ).injective
  exact Subtype.ext hzw

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- Exactly the finite-support covariant functions occur in the function model. -/
theorem functionModel_range : LinearMap.range (functionModel H σ) = finiteCosetSupport H σ := by
  ext f
  constructor
  · rintro ⟨z, rfl⟩
    exact functionModel_finite_support H σ z
  · intro hf
    obtain ⟨z, hz⟩ := (compactModelEquiv H σ).surjective ⟨f, hf⟩
    exact ⟨z, congrArg Subtype.val hz⟩

/-- Every finite-support covariant function has an open right-translation
stabilizer. The statement is about the entire constructed function space. -/
theorem finite_functions_smooth (hH : IsOpen (H : Set G)) (hσ : IsSmooth σ)
    (f : finiteCosetSupport H σ) :
    IsOpen {t : G | ∀ x : G, f.val.val (x * t) = f.val.val x} := by
  obtain ⟨z, hz⟩ := (compactModelEquiv H σ).surjective f
  have hf : functionModel H σ z = f.val := congrArg Subtype.val hz
  rw [← hf]
  have hopen : IsOpen (vectorStabilizer (coind H.subtype σ) (functionModel H σ z) : Set G) := by
    apply Subgroup.isOpen_mono (H₁ := vectorStabilizer (ind H.subtype σ) z)
      _ (ind_isSmooth H σ hH hσ z)
    intro t ht
    have he := LinearMap.congr_fun ((functionIntertwiner H σ).isIntertwining' t) z
    change functionModel H σ (ind H.subtype σ t z) =
      coind H.subtype σ t (functionModel H σ z) at he
    rw [show ind H.subtype σ t z = z from ht] at he
    exact he.symm
  have heq : (vectorStabilizer (coind H.subtype σ) (functionModel H σ z) : Set G) =
      {t : G | ∀ x : G, (functionModel H σ z).val (x * t) =
        (functionModel H σ z).val x} := by
    ext t
    change coind H.subtype σ t (functionModel H σ z) = functionModel H σ z ↔ _
    constructor
    · intro ht x
      exact congrArg (fun u : coindV H.subtype σ => u.val x) ht
    · intro ht
      exact Subtype.ext (funext ht)
  rwa [heq] at hopen

end PaperXI.OpenSubgroupSmoothInduction
