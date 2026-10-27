import PaperX.SemilinearScalarExtension
import PaperX.TateWeightCopies

/-! Finite Tate comparisons on the actual scalar extension, with the coefficient
Galois action retained. A comparison of an individual representation is input;
the comparison for finite selected copies is constructed, not postulated.
No Tate--Sen theorem, arithmetic admissibility theorem or WD functor is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SemilinearTateComparison
open TensorProduct PaperX.CarrierSummands
open PaperX.SemilinearScalarExtension
variable {R B G : Type*} [Field R] [Field B] [Algebra R B] [Group G]
variable (σ : G →* (B ≃ₐ[R] B)) (tate : ℤ → G →* Rˣ)
variable {V : Type*} [AddCommGroup V] [Module R V]

/-- A finite B-linear Tate splitting of B tensor_R V, equivariant for the
sigma-semilinear action. The coefficient action in action_eq is essential. -/
structure Comparison (ρ : Representation R G V) where
  Index : Type
  finiteIndex : Fintype Index
  weight : Index → ℤ
  equiv : B ⊗[R] V ≃ₗ[B] (Index → B)
  action_eq : ∀ g x j,
    equiv (tensorRep σ ρ g x) j =
      algebraMap R B ((tate (weight j)) g : R) * σ g (equiv x j)

namespace Comparison
variable {σ tate}
variable {U : Type*} [AddCommGroup U] [Module R U]
variable {ρ : Representation R G V} {ρ' : Representation R G U}

/-- Transport along an actual equivariant map over the original coefficient field. -/
def ofEquiv (e : V ≃ₗ[R] U) (he : ∀ g v, e (ρ g v) = ρ' g (e v))
    (C : Comparison σ tate ρ') : Comparison σ tate ρ where
  Index := C.Index
  finiteIndex := C.finiteIndex
  weight := C.weight
  equiv := (extendEquiv (B := B) e).trans C.equiv
  action_eq := by
    intro g x j
    change C.equiv (extendEquiv (B := B) e (tensorRep σ ρ g x)) j = _
    rw [extendEquiv_equivariant σ ρ ρ' e he]
    exact C.action_eq g (extendEquiv (B := B) e x) j
end Comparison

/-- The actual scalar-extended equivalence induced by an older base-field
Tate certificate. This is a one-way construction, not an identification of the
two notions of splitting. -/
def baseCertificateEquiv {ρ : Representation R G V}
    (C : PaperX.TateWeightCopies.Certificate tate ρ) :
    B ⊗[R] V ≃ₗ[B] (C.Index → B) := by
  classical
  letI : Fintype C.Index := C.finiteIndex
  exact (extendEquiv (B := B) C.equiv).trans (TensorProduct.piScalarRight R B B C.Index)

@[simp] theorem baseCertificateEquiv_tmul {ρ : Representation R G V}
    (C : PaperX.TateWeightCopies.Certificate tate ρ) (b : B) (v : V) (j : C.Index) :
    baseCertificateEquiv (B := B) tate C (b ⊗ₜ[R] v) j =
      algebraMap R B (C.equiv v j) * b := by
  simp [baseCertificateEquiv, Algebra.smul_def]

/-- A supplied R-linear Tate splitting produces a genuine semilinear comparison
after scalar extension. No converse is asserted. -/
def ofBaseCertificate {ρ : Representation R G V}
    (C : PaperX.TateWeightCopies.Certificate tate ρ) : Comparison σ tate ρ where
  Index := C.Index
  finiteIndex := C.finiteIndex
  weight := C.weight
  equiv := baseCertificateEquiv (B := B) tate C
  action_eq := by
    intro g x j
    induction x using TensorProduct.induction_on with
    | zero => simp
    | tmul b v =>
        simp only [tensorRep_tmul, baseCertificateEquiv_tmul, C.action_eq, map_mul,
          AlgEquiv.commutes]
        ring
    | add x y hx hy => simp [hx, hy, mul_add]

/-- The finite coordinate fibre for a specified integer weight. -/
def WeightFiber {ρ : Representation R G V} (C : Comparison σ tate ρ) (z : ℤ) :=
  {j : C.Index // C.weight j = z}

instance weightFiberFintype {ρ : Representation R G V} (C : Comparison σ tate ρ) (z : ℤ) :
    Fintype (WeightFiber σ tate C z) := by
  classical
  letI : Fintype C.Index := C.finiteIndex
  change Fintype {j : C.Index // C.weight j = z}
  exact Fintype.ofFinite _

/-- Coordinate multiplicity in this comparison; intrinsic independence needs
additional arithmetic results about the coefficient action. -/
def weightMultiplicity {ρ : Representation R G V} (C : Comparison σ tate ρ) (z : ℤ) : ℕ :=
  Fintype.card (WeightFiber σ tate C z)

/-- The old base-field certificate is connected to the new semilinear certificate
without changing its finite coordinate exponent census. -/
theorem ofBaseCertificate_weightMultiplicity {ρ : Representation R G V}
    (C : PaperX.TateWeightCopies.Certificate tate ρ) (z : ℤ) :
    weightMultiplicity σ tate (ofBaseCertificate σ tate C) z =
      PaperX.TateWeightCopies.weightMultiplicity tate C z := by
  unfold weightMultiplicity PaperX.TateWeightCopies.weightMultiplicity
  exact Fintype.card_congr (Equiv.refl _)

variable {I : Type} [Fintype I]
variable {W : I → Type*} [∀ i, AddCommGroup (W i)] [∀ i, Module R (W i)]
variable (ρ : ∀ i, Representation R G (W i)) (C : ∀ i, Comparison σ tate (ρ i)) (m : I → ℕ)

abbrev CopiesIndex := Σ i, Fin (m i) × (C i).Index

/-- Flatten the comparisons without identifying unequal coordinates or weights. -/
def flattenEquiv : Copies (fun i => B ⊗[R] W i) m ≃ₗ[B] (CopiesIndex σ tate ρ C m → B) where
  toFun x j := (C j.1).equiv (x j.1 j.2.1) j.2.2
  invFun y i k := (C i).equiv.symm (fun a => y ⟨i, k, a⟩)
  left_inv x := by
    funext i k
    exact (C i).equiv.symm_apply_apply (x i k)
  right_inv y := by
    funext j
    exact congrFun ((C j.1).equiv.apply_symm_apply (fun a => y ⟨j.1, j.2.1, a⟩)) j.2.2
  map_add' x y := by
    funext j
    exact congrFun ((C j.1).equiv.map_add (x j.1 j.2.1) (y j.1 j.2.1)) j.2.2
  map_smul' b x := by
    funext j
    exact congrFun ((C j.1).equiv.map_smul b (x j.1 j.2.1)) j.2.2

/-- Constructed comparison for the actual scalar extension of selected copies. -/
def copiesComparison : Comparison σ tate (copiesRep ρ m) where
  Index := CopiesIndex σ tate ρ C m
  finiteIndex := by
    classical
    letI (i : I) : Fintype (C i).Index := (C i).finiteIndex
    infer_instance
  weight j := (C j.1).weight j.2.2
  equiv := (PaperX.SemilinearScalarExtension.copiesEquiv (R := R) (B := B) m).trans
    (flattenEquiv σ tate ρ C m)
  action_eq := by
    intro g x j
    change (C j.1).equiv
      (PaperX.SemilinearScalarExtension.copiesEquiv (R := R) (B := B) m
        (tensorRep σ (copiesRep ρ m) g x) j.1 j.2.1) j.2.2 = _
    rw [copiesEquiv_equivariant σ ρ m]
    exact (C j.1).action_eq g
      (PaperX.SemilinearScalarExtension.copiesEquiv (R := R) (B := B) m x j.1 j.2.1) j.2.2

@[simp] theorem copiesComparison_weight (j : CopiesIndex σ tate ρ C m) :
    (copiesComparison σ tate ρ C m).weight j = (C j.1).weight j.2.2 := rfl

@[simp] theorem copiesComparison_tmul (b : B) (v : Copies W m) (j : CopiesIndex σ tate ρ C m) :
    (copiesComparison σ tate ρ C m).equiv (b ⊗ₜ[R] v) j =
      (C j.1).equiv (b ⊗ₜ[R] v j.1 j.2.1) j.2.2 := rfl

/-- The exact fibre equivalence for the integer-weight census. -/
def copiesWeightFiberEquiv (z : ℤ) :
    WeightFiber σ tate (copiesComparison σ tate ρ C m) z ≃
      Σ i, Fin (m i) × WeightFiber σ tate (C i) z where
  toFun x := ⟨x.val.1, x.val.2.1, ⟨x.val.2.2, x.property⟩⟩
  invFun x := ⟨⟨x.1, x.2.1, x.2.2.val⟩, x.2.2.property⟩
  left_inv x := by cases x; rfl
  right_inv x := by cases x; rfl

theorem copies_weightMultiplicity (z : ℤ) :
    weightMultiplicity σ tate (copiesComparison σ tate ρ C m) z =
      ∑ i, m i * weightMultiplicity σ tate (C i) z := by
  classical
  unfold weightMultiplicity
  rw [Fintype.card_congr (copiesWeightFiberEquiv σ tate ρ C m z), Fintype.card_sigma]
  apply Finset.sum_congr rfl
  intro i _
  rw [Fintype.card_prod, Fintype.card_fin]

end PaperX.SemilinearTateComparison
