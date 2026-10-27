import PaperX.CarrierSummands

/-!
Paper X Claim 9.2: finite-copy closure of an explicit Tate-weight splitting.

This is the algebraic decomposition layer needed after an actual p-adic period
comparison has been supplied.  A certificate consists of a finite coordinate
set, an integer weight for every coordinate, and an equivariant linear
isomorphism to scalar Tate-character coordinates.  The theorem below constructs
such a certificate for arbitrary finite selected copies of certified
constituents.

This file does not construct `C_p`, a semilinear Galois action, a period ring, or
the comparison isomorphism that proves an arithmetic representation is
Hodge--Tate.  It proves the exact finite-direct-sum preservation statement once
that genuine comparison has produced the stated Tate-weight certificate.
-/
set_option autoImplicit false
noncomputable section

namespace PaperX.TateWeightCopies

open PaperX.CarrierSummands

variable {K G : Type*} [Field K] [Group G]
variable (tate : ℤ → G →* Kˣ)
variable {V : Type*} [AddCommGroup V] [Module K V]

/-- A finite equivariant splitting into one-dimensional Tate-character
coordinates.  Repeated weights are represented by distinct coordinates rather
than quotienting by a chosen basis of an isotypic component. -/
structure Certificate (ρ : Representation K G V) where
  Index : Type
  finiteIndex : Fintype Index
  weight : Index → ℤ
  equiv : V ≃ₗ[K] (Index → K)
  action_eq : ∀ g x j,
    equiv (ρ g x) j = ((tate (weight j)) g : K) * equiv x j




namespace Certificate

variable {tate}
variable {U X : Type*} [AddCommGroup U] [Module K U]
  [AddCommGroup X] [Module K X]
variable {σ : Representation K G U} {ρ : Representation K G X}

/-- Transport a Tate-weight certificate across an actual equivariant linear
isomorphism.  This allows the direct-sum certificate to be carried back into a
supplied carrier or any other isomorphic presentation. -/
def ofEquiv (e : U ≃ₗ[K] X)
    (he : ∀ g x, e (σ g x) = ρ g (e x))
    (C : Certificate tate ρ) : Certificate tate σ where
  Index := C.Index
  finiteIndex := C.finiteIndex
  weight := C.weight
  equiv := e.trans C.equiv
  action_eq := by
    intro g x j
    change C.equiv (e (σ g x)) j =
      ((tate (C.weight j)) g : K) * C.equiv (e x) j
    rw [he]
    exact C.action_eq g (e x) j

end Certificate

/-- Coordinates of a certificate carrying one specified integer weight. -/
def WeightFiber {ρ : Representation K G V} (C : Certificate tate ρ) (z : ℤ) :=
  {j : C.Index // C.weight j = z}

noncomputable instance weightFiberFintype {ρ : Representation K G V}
    (C : Certificate tate ρ) (z : ℤ) : Fintype (WeightFiber tate C z) := by
  classical
  letI : Fintype C.Index := C.finiteIndex
  change Fintype {j : C.Index // C.weight j = z}
  exact Fintype.ofFinite _

/-- Multiplicity of one integer weight in a supplied finite Tate splitting. -/
def weightMultiplicity {ρ : Representation K G V}
    (C : Certificate tate ρ) (z : ℤ) : ℕ :=
  Fintype.card (WeightFiber tate C z)

variable {I : Type} [Fintype I]
variable {W : I → Type*}
variable [∀ i, AddCommGroup (W i)] [∀ i, Module K (W i)]
variable (ρ : ∀ i, Representation K G (W i))
variable (C : ∀ i, Certificate tate (ρ i))
variable (m : I → ℕ)

/-- Coordinate labels for the finite-copy splitting: constituent, selected
copy, then the constituent's own Tate coordinate. -/
abbrev CopiesIndex := Σ i, Fin (m i) × (C i).Index

/-- Flatten the constituent splittings into one actual linear equivalence. -/
def copiesEquiv : Copies W m ≃ₗ[K] (CopiesIndex tate ρ C m → K) where
  toFun x j := (C j.1).equiv (x j.1 j.2.1) j.2.2
  invFun y i k := (C i).equiv.symm (fun a => y ⟨i, k, a⟩)
  left_inv x := by
    funext i k
    exact (C i).equiv.symm_apply_apply (x i k)
  right_inv y := by
    funext j
    exact congrFun ((C j.1).equiv.apply_symm_apply
      (fun a => y ⟨j.1, j.2.1, a⟩)) j.2.2
  map_add' x y := by
    funext j
    exact congrFun ((C j.1).equiv.map_add (x j.1 j.2.1) (y j.1 j.2.1)) j.2.2
  map_smul' a x := by
    funext j
    exact congrFun ((C j.1).equiv.map_smul a (x j.1 j.2.1)) j.2.2

include C in
/-- Finite selected copies of Tate-split constituents are Tate-split.  The
output retains every coordinate, so no choice of basis inside repeated equal
weights is introduced. -/
def copiesCertificate : Certificate tate (copiesRep ρ m) where
  Index := CopiesIndex tate ρ C m
  finiteIndex := by
    classical
    letI (i : I) : Fintype (C i).Index := (C i).finiteIndex
    show Fintype (CopiesIndex tate ρ C m)
    infer_instance
  weight j := (C j.1).weight j.2.2
  equiv := copiesEquiv tate ρ C m
  action_eq := by
    intro g x j
    change (C j.1).equiv (ρ j.1 g (x j.1 j.2.1)) j.2.2 =
      ((tate ((C j.1).weight j.2.2)) g : K) *
        (C j.1).equiv (x j.1 j.2.1) j.2.2
    exact (C j.1).action_eq g (x j.1 j.2.1) j.2.2

include C in
/-- Existence form of finite-copy Tate-weight closure. -/
theorem copies_certificate_exists :
    Nonempty (Certificate tate (copiesRep ρ m)) :=
  ⟨copiesCertificate tate ρ C m⟩

@[simp] theorem copiesCertificate_weight (j : CopiesIndex tate ρ C m) :
    (copiesCertificate tate ρ C m).weight j = (C j.1).weight j.2.2 := rfl

@[simp] theorem copiesCertificate_equiv_apply
    (x : Copies W m) (j : CopiesIndex tate ρ C m) :
    (copiesCertificate tate ρ C m).equiv x j =
      (C j.1).equiv (x j.1 j.2.1) j.2.2 := rfl

/-- The multiset of output weights is literally obtained by retaining each
constituent weight once for every selected copy. -/
theorem copies_weight_occurs
    (i : I) (k : Fin (m i)) (a : (C i).Index) :
    (copiesCertificate tate ρ C m).weight ⟨i, k, a⟩ = (C i).weight a := rfl

/-- The fiber of one weight in the selected-copy certificate is exactly the
sigma type of constituent, selected copy, and constituent weight fiber. -/
def copiesWeightFiberEquiv (z : ℤ) :
    WeightFiber tate (copiesCertificate tate ρ C m) z ≃
      Σ i, Fin (m i) × WeightFiber tate (C i) z where
  toFun x := ⟨x.val.1, x.val.2.1, ⟨x.val.2.2, x.property⟩⟩
  invFun x := ⟨⟨x.1, x.2.1, x.2.2.val⟩, x.2.2.property⟩
  left_inv x := by cases x; rfl
  right_inv x := by cases x; rfl

/-- Exact weight census for finite selected copies.  Equal weights from different
constituents are counted with their full selected multiplicities. -/
theorem copies_weightMultiplicity (z : ℤ) :
    weightMultiplicity tate (copiesCertificate tate ρ C m) z =
      ∑ i, m i * weightMultiplicity tate (C i) z := by
  classical
  unfold weightMultiplicity
  rw [Fintype.card_congr (copiesWeightFiberEquiv tate ρ C m z)]
  rw [Fintype.card_sigma]
  apply Finset.sum_congr rfl
  intro i hi
  rw [Fintype.card_prod, Fintype.card_fin]

end PaperX.TateWeightCopies
