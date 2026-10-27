import PaperXII.ResidualAugmentation
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.Algebra.CharP.Algebra
import Mathlib.Algebra.MvPolynomial.CommRing
import Mathlib.RingTheory.MvPolynomial.Basic
import Mathlib.RingTheory.MvPolynomial.Ideal
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Pi

set_option autoImplicit false

/-! Paper XII, Theorem 5.2: explicit multivariable residual group-algebra presentation. -/
namespace PaperXII.TruncatedGroupAlgebra

open scoped BigOperators MonoidAlgebra

variable {k ι : Type*} [CommRing k] [Fintype ι] [DecidableEq ι]
variable (p : ℕ) [Fact p.Prime] [CharP k p] (n : ι → ℕ)

/-- The actual product of cyclic groups in the chosen decomposition. -/
abbrev Delta := ∀ i, Multiplicative (ZMod (p ^ n i))

/-- The standard generator of the indicated cyclic factor. -/
def gamma (i : ι) : Delta p n := Pi.mulSingle i (Multiplicative.ofAdd 1)

/-- The ideal of the actual multivariable truncation relations. -/
noncomputable def relations : Ideal (MvPolynomial ι k) :=
  Ideal.span (Set.range fun i => (MvPolynomial.X i : MvPolynomial ι k) ^ (p ^ n i))

abbrev Truncated := MvPolynomial ι k ⧸ relations (k := k) p n

omit [Fintype ι] [Fact p.Prime] in
theorem gamma_pow (i : ι) : gamma p n i ^ (p ^ n i) = 1 := by
  rw [gamma, ← Pi.mulSingle_pow]
  have h : Multiplicative.ofAdd (1 : ZMod (p ^ n i)) ^ (p ^ n i) = 1 := by
    change (p ^ n i) • (1 : ZMod (p ^ n i)) = 0
    simp [nsmul_eq_mul]
  rw [h, Pi.mulSingle_one]

/-- Polynomial evaluation at the augmentation generators. -/
noncomputable def presentation : MvPolynomial ι k →ₐ[k] k[Delta p n] :=
  MvPolynomial.aeval fun i => MonoidAlgebra.single (gamma p n i) 1 - 1

omit [Fintype ι] [Fact p.Prime] [CharP k p] in
theorem presentation_X (i : ι) :
    presentation (k := k) p n (MvPolynomial.X i) =
      MonoidAlgebra.single (gamma p n i) 1 - 1 := by
  simp [presentation]

omit [Fintype ι] in
theorem presentation_relation (i : ι) :
    presentation (k := k) p n (MvPolynomial.X i ^ (p ^ n i)) = 0 := by
  let : CharP k[Delta p n] p := charP_of_injective_algebraMap' k p
  rw [map_pow, presentation_X, sub_pow_char_pow]
  simp [MonoidAlgebra.single_pow, gamma_pow, ← MonoidAlgebra.one_def]

omit [Fintype ι] in
theorem relations_le_ker :
    relations (k := k) p n ≤ RingHom.ker (presentation (k := k) p n).toRingHom := by
  rw [relations, Ideal.span_le]
  rintro _ ⟨i, rfl⟩
  exact presentation_relation p n i

/-- The forward map from the actual truncated polynomial quotient. -/
noncomputable def forward : Truncated (k := k) p n →ₐ[k] k[Delta p n] :=
  Ideal.Quotient.liftₐ _ (presentation p n) (fun _ h => relations_le_ker p n h)

omit [Fintype ι] in
theorem forward_mk (f : MvPolynomial ι k) :
    forward p n (Ideal.Quotient.mk _ f) = presentation p n f := rfl

/-- The image of one plus a polynomial variable. -/
noncomputable def onePlusX (i : ι) : Truncated (k := k) p n :=
  1 + Ideal.Quotient.mk _ (MvPolynomial.X i)

omit [Fintype ι] [DecidableEq ι] in
theorem onePlusX_pow (i : ι) : onePlusX (k := k) p n i ^ (p ^ n i) = 1 := by
  rw [onePlusX, ← map_one (Ideal.Quotient.mk (relations (k := k) p n)),
    ← map_add, ← map_pow, add_pow_char_pow, one_pow, map_add, map_one]
  have h : (MvPolynomial.X i : MvPolynomial ι k) ^ (p ^ n i) ∈ relations p n :=
    Ideal.subset_span ⟨i, rfl⟩
  rw [Ideal.Quotient.eq_zero_iff_mem.mpr h, add_zero]

/-- A cyclic factor acts by powers of any element with the required relation. -/
noncomputable def cyclicMap {A : Type*} [Monoid A] (N : ℕ) [NeZero N]
    (b : A) (h : b ^ N = 1) : Multiplicative (ZMod N) →* A where
  toFun g := b ^ g.toAdd.val
  map_one' := by simp
  map_mul' g h' := by
    change b ^ (g.toAdd + h'.toAdd).val = b ^ g.toAdd.val * b ^ h'.toAdd.val
    rw [ZMod.val_add, ← pow_eq_pow_mod _ h, pow_add]

theorem cyclicMap_generator {A : Type*} [Monoid A] (N : ℕ) [NeZero N]
    (b : A) (h : b ^ N = 1) : cyclicMap N b h (Multiplicative.ofAdd 1) = b := by
  change b ^ (1 : ZMod N).val = b
  rw [ZMod.val_one_eq_one_mod, ← pow_eq_pow_mod _ h, pow_one]

/-- The explicit monoid map underlying the inverse presentation. -/
noncomputable def groupMap : Delta p n →* Truncated (k := k) p n where
  toFun g := ∏ i, cyclicMap (p ^ n i) (onePlusX p n i) (onePlusX_pow p n i) (g i)
  map_one' := by simp
  map_mul' g h := by simp [Finset.prod_mul_distrib]

theorem groupMap_gamma (i : ι) :
    groupMap (k := k) p n (gamma p n i) = onePlusX p n i := by
  change (∏ j, cyclicMap (p ^ n j) (onePlusX p n j) (onePlusX_pow p n j)
    (gamma p n i j)) = _
  rw [Finset.prod_eq_single i]
  · rw [gamma, Pi.mulSingle_eq_same, cyclicMap_generator]
  · intro j _ hj
    rw [gamma, Pi.mulSingle_eq_of_ne hj, map_one]
  · simp

/-- The inverse sends each group basis element to its explicit product of powers. -/
noncomputable def backward : k[Delta p n] →ₐ[k] Truncated (k := k) p n :=
  MonoidAlgebra.lift k _ _ (groupMap p n)

omit [DecidableEq ι] in
theorem backward_single (g : Delta p n) (a : k) :
    backward p n (MonoidAlgebra.single g a) = a • groupMap p n g := by
  simp [backward]

theorem backward_presentation :
    (backward (k := k) p n).comp (presentation p n) =
      Ideal.Quotient.mkₐ k (relations p n) := by
  ext i
  simp [AlgHom.comp_apply, presentation_X, backward_single, groupMap_gamma, onePlusX]

/-- Every group element is the product of the selected generators to its residue exponents. -/
theorem group_decomposition (g : Delta p n) :
    (∏ i, gamma p n i ^ (g i).toAdd.val) = g := by
  ext j
  simp only [Finset.prod_apply, Pi.pow_apply]
  rw [Finset.prod_eq_single j]
  · simp only [gamma, Pi.mulSingle_eq_same]
    change Multiplicative.ofAdd ((g j).toAdd.val • (1 : ZMod (p ^ n j))) = g j
    simp [nsmul_eq_mul]
  · intro i _ hij
    rw [gamma, Pi.mulSingle_eq_of_ne (Ne.symm hij), one_pow]
  · simp

omit [Fintype ι] in
theorem forward_onePlusX (i : ι) :
    forward (k := k) p n (onePlusX p n i) = MonoidAlgebra.single (gamma p n i) 1 := by
  simp [onePlusX, forward_mk, presentation_X]

theorem forward_groupMap (g : Delta p n) :
    forward (k := k) p n (groupMap p n g) = MonoidAlgebra.single g 1 := by
  change forward p n (∏ i, onePlusX p n i ^ (g i).toAdd.val) = _
  simp only [map_prod, map_pow, forward_onePlusX, MonoidAlgebra.single_pow, one_pow]
  rw [MonoidAlgebra.prod_single, group_decomposition]
  simp

theorem forward_backward :
    (forward (k := k) p n).comp (backward p n) = AlgHom.id k k[Delta p n] := by
  apply MonoidAlgebra.algHom_ext
  · intro g
    simp [AlgHom.comp_apply, backward_single, forward_groupMap]
  · ext

theorem backward_forward :
    (backward (k := k) p n).comp (forward p n) =
      AlgHom.id k (Truncated (k := k) p n) := by
  ext x
  obtain ⟨f, rfl⟩ := Ideal.Quotient.mk_surjective x
  exact DFunLike.congr_fun (backward_presentation (k := k) p n) f

/-- The full multivariable quotient presentation, with an explicitly proved inverse. -/
noncomputable def truncatedPolynomialEquiv :
    Truncated (k := k) p n ≃ₐ[k] k[Delta p n] :=
  AlgEquiv.ofAlgHom (forward p n) (backward p n) (forward_backward p n) (backward_forward p n)

/-- The presentation sends each actual residue variable to the selected group generator minus one. -/
theorem truncatedPolynomialEquiv_X (i : ι) :
    truncatedPolynomialEquiv (k := k) p n (Ideal.Quotient.mk _ (MvPolynomial.X i)) =
      MonoidAlgebra.single (gamma p n i) 1 - 1 := by
  exact presentation_X p n i

omit [Fintype ι] [DecidableEq ι] in
/-- Zero constant coefficient is equivalent to membership in the variable ideal. -/
theorem constantCoeff_ker :
    RingHom.ker (MvPolynomial.constantCoeff : MvPolynomial ι k →+* k) =
      Ideal.span (Set.range (MvPolynomial.X : ι → MvPolynomial ι k)) := by
  classical
  ext f
  rw [← Set.image_univ, MvPolynomial.mem_ideal_span_X_image]
  change f.coeff 0 = 0 ↔ _
  constructor
  · intro hf m hm
    have hm0 : m ≠ 0 := by
      intro heq
      subst m
      exact (MvPolynomial.mem_support_iff.mp hm) hf
    obtain ⟨i, hi⟩ := Finsupp.ne_iff.mp hm0
    exact ⟨i, Set.mem_univ _, hi⟩
  · intro hf
    by_contra h
    obtain ⟨i, _, hi⟩ := hf 0 (MvPolynomial.mem_support_iff.mpr h)
    exact hi rfl

omit [Fintype ι] [Fact p.Prime] [CharP k p] in
/-- Augmentation after polynomial presentation is the actual constant-coefficient map. -/
theorem augmentation_presentation :
    (AuxiliaryGroupAlgebra.augmentation (R := k) (G := Delta p n)).toRingHom.comp
      (presentation p n).toRingHom = MvPolynomial.constantCoeff := by
  apply MvPolynomial.ringHom_ext
  · intro a
    simp [presentation, AuxiliaryGroupAlgebra.augmentation_single]
  · intro i
    simp [presentation_X, AuxiliaryGroupAlgebra.augmentation_single]

/-- The selected augmentation generators generate the whole augmentation ideal. -/
theorem augmentationIdeal_eq :
    AuxiliaryGroupAlgebra.augmentationIdeal (R := k) (G := Delta p n) =
      Ideal.span (Set.range fun i => (MonoidAlgebra.single (gamma p n i) 1 - 1 : k[Delta p n])) := by
  have hs : Function.Surjective (presentation (k := k) p n) := by
    intro x
    obtain ⟨y, hy⟩ := (truncatedPolynomialEquiv (k := k) p n).surjective x
    obtain ⟨f, rfl⟩ := Ideal.Quotient.mk_surjective y
    exact ⟨f, hy⟩
  have hc : (AuxiliaryGroupAlgebra.augmentationIdeal (R := k) (G := Delta p n)).comap
      (presentation p n).toRingHom = Ideal.span (Set.range (MvPolynomial.X : ι → MvPolynomial ι k)) := by
    rw [AuxiliaryGroupAlgebra.augmentationIdeal, RingHom.comap_ker,
      augmentation_presentation, constantCoeff_ker]
  rw [← Ideal.map_comap_of_surjective (presentation p n).toRingHom hs
    (AuxiliaryGroupAlgebra.augmentationIdeal (R := k) (G := Delta p n)), hc,
    Ideal.map_span, ← Set.range_comp]
  congr 2
  funext i
  exact presentation_X p n i

/-- The canonical finite product has the required p-power order. -/
theorem delta_isPGroup : IsPGroup p (Delta p n) := by
  apply IsPGroup.of_card (n := ∑ i, n i)
  simp [Nat.card_eq_fintype_card, Delta, Fintype.card_pi, ← Finset.prod_pow_eq_pow_sum]

variable {G : Type*} [CommGroup G]

/-- Transport the explicit presentation along the supplied product decomposition. -/
noncomputable def equivalenceOfDecomposition (e : G ≃* Delta p n) :
    Truncated (k := k) p n ≃ₐ[k] k[G] :=
  (truncatedPolynomialEquiv p n).trans (MonoidAlgebra.domCongr k k e.symm)

/-- The transported variables are precisely the chosen generators minus one. -/
theorem equivalenceOfDecomposition_X (e : G ≃* Delta p n) (i : ι) :
    equivalenceOfDecomposition (k := k) p n e (Ideal.Quotient.mk _ (MvPolynomial.X i)) =
      MonoidAlgebra.single (e.symm (gamma p n i)) 1 - 1 := by
  simp [equivalenceOfDecomposition, truncatedPolynomialEquiv_X]

omit [Fintype ι] [DecidableEq ι] [Fact p.Prime] [CharP k p] in
/-- Augmentation commutes with the chosen decomposition. -/
theorem augmentation_decomposition (e : G ≃* Delta p n) :
    (AuxiliaryGroupAlgebra.augmentation (R := k) (G := G)).toRingHom.comp
      (MonoidAlgebra.domCongr k k e.symm).toRingHom =
        (AuxiliaryGroupAlgebra.augmentation (R := k) (G := Delta p n)).toRingHom := by
  have h := AuxiliaryGroupAlgebra.augmentation_transfer (R := k) e.symm.toMonoidHom
  exact congrArg AlgHom.toRingHom h

/-- The chosen generators span the augmentation kernel after transport. -/
theorem augmentationIdeal_eq_of_decomposition (e : G ≃* Delta p n) :
    AuxiliaryGroupAlgebra.augmentationIdeal (R := k) (G := G) =
      Ideal.span (Set.range fun i => (MonoidAlgebra.single (e.symm (gamma p n i)) 1 - 1 : k[G])) := by
  have hc : (AuxiliaryGroupAlgebra.augmentationIdeal (R := k) (G := G)).comap
      (MonoidAlgebra.domCongr k k e.symm).toRingHom =
        AuxiliaryGroupAlgebra.augmentationIdeal (R := k) (G := Delta p n) := by
    rw [AuxiliaryGroupAlgebra.augmentationIdeal, RingHom.comap_ker,
      augmentation_decomposition]
  rw [← Ideal.map_comap_of_surjective (MonoidAlgebra.domCongr k k e.symm).toRingHom
    (MonoidAlgebra.domCongr k k e.symm).surjective
    (AuxiliaryGroupAlgebra.augmentationIdeal (R := k) (G := G)), hc,
    augmentationIdeal_eq, Ideal.map_span, ← Set.range_comp]
  congr 2
  funext i
  simp

variable {K : Type*} [Field K] [CharP K p]

/-- Locality for the actual group algebra with the supplied cyclic decomposition. -/
theorem isLocalRing_of_decomposition (e : G ≃* Delta p n) : IsLocalRing K[G] :=
  ResidualAugmentation.isLocalRing ((delta_isPGroup p n).of_equiv e.symm)

/-- Paper XII, Theorem 5.2: the full presentation, chosen-generator identities,
augmentation-ideal equality, and locality. No positive-rank or nontrivial-factor hypothesis
is needed. The inverse equivalence is proved above rather than supplied as an assumption. -/
theorem residual_augmentation_algebra (e : G ≃* Delta p n) :
    (∃ E : Truncated (k := K) p n ≃ₐ[K] K[G],
      ∀ i, E (Ideal.Quotient.mk _ (MvPolynomial.X i)) =
        MonoidAlgebra.single (e.symm (gamma p n i)) 1 - 1) ∧
    AuxiliaryGroupAlgebra.augmentationIdeal (R := K) (G := G) =
      Ideal.span (Set.range fun i =>
        (MonoidAlgebra.single (e.symm (gamma p n i)) 1 - 1 : K[G])) ∧
    IsLocalRing K[G] := by
  refine ⟨⟨equivalenceOfDecomposition p n e, equivalenceOfDecomposition_X p n e⟩, ?_,
    isLocalRing_of_decomposition p n e⟩
  exact augmentationIdeal_eq_of_decomposition p n e

end PaperXII.TruncatedGroupAlgebra
