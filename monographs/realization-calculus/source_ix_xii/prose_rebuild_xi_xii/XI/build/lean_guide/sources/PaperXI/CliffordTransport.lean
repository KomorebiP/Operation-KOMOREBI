import PaperXI.CliffordCocycle

/-! Actual transport of subgroup intertwiners and multiplicity operators
along isomorphisms of the original representation data. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordTransport
open CliffordDatum CliffordMultiplicity

variable {G G' W W' X X' : Type*} [Group G] [Group G']
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup W'] [Module ℂ W']
variable [AddCommGroup X] [Module ℂ X] [AddCommGroup X'] [Module ℂ X']

/-- The actual subgroup isomorphism induced by the group isomorphism. -/
def subgroupEquiv (N : Subgroup G) (N' : Subgroup G') (e : G ≃* G')
    (hN : N.map e.toMonoidHom = N') : N ≃* N' where
  toFun n := ⟨e n, by rw [← hN]; exact ⟨n, n.property, rfl⟩⟩
  invFun n := ⟨e.symm n, by
    have hn : (n : G') ∈ N.map e.toMonoidHom := hN.symm ▸ n.property
    obtain ⟨g, hg, he⟩ := hn
    simpa [← he] using hg⟩
  left_inv n := by apply Subtype.ext; simp
  right_inv n := by apply Subtype.ext; simp
  map_mul' n m := by apply Subtype.ext; exact map_mul e (n : G) (m : G)

@[simp] theorem subgroupEquiv_coe (N : Subgroup G) (N' : Subgroup G')
    (e : G ≃* G') (hN : N.map e.toMonoidHom = N') (n : N) :
    (subgroupEquiv N N' e hN n : G') = e n := rfl

theorem subgroupEquiv_conjugation (N : Subgroup G) [N.Normal]
    (N' : Subgroup G') [N'.Normal] (e : G ≃* G')
    (hN : N.map e.toMonoidHom = N') (g : G) (n : N) :
    subgroupEquiv N N' e hN (conjugation N g n) =
      conjugation N' (e g) (subgroupEquiv N N' e hN n) := by
  apply Subtype.ext
  simp [map_mul]

/-- The actual induced quotient group isomorphism. -/
def quotientEquiv (N : Subgroup G) [N.Normal] (N' : Subgroup G') [N'.Normal]
    (e : G ≃* G') (hN : N.map e.toMonoidHom = N') : G ⧸ N ≃* G' ⧸ N' :=
  QuotientGroup.congr N N' e hN

@[simp] theorem quotientEquiv_mk (N : Subgroup G) [N.Normal]
    (N' : Subgroup G') [N'.Normal] (e : G ≃* G')
    (hN : N.map e.toMonoidHom = N') (g : G) :
    quotientEquiv N N' e hN (QuotientGroup.mk' N g) = QuotientGroup.mk' N' (e g) :=
  QuotientGroup.congr_mk' N N' e hN g

/-- The induced quotient map preserves identity isomorphisms. -/
theorem quotientEquiv_refl (N : Subgroup G) [N.Normal]
    (hN : N.map (MulEquiv.refl G).toMonoidHom = N) :
    quotientEquiv N N (MulEquiv.refl G) hN = MulEquiv.refl (G ⧸ N) := by
  apply MulEquiv.ext
  intro a
  obtain ⟨g, rfl⟩ := QuotientGroup.mk_surjective a
  rfl

/-- The actual quotient transport respects composition of group isomorphisms. -/
theorem quotientEquiv_comp {G'' : Type*} [Group G'']
    (N : Subgroup G) [N.Normal] (N' : Subgroup G') [N'.Normal]
    (N'' : Subgroup G'') [N''.Normal] (e : G ≃* G') (e' : G' ≃* G'')
    (hN : N.map e.toMonoidHom = N') (hN' : N'.map e'.toMonoidHom = N'')
    (hNN : N.map (e.trans e').toMonoidHom = N'') (a : G ⧸ N) :
    quotientEquiv N' N'' e' hN' (quotientEquiv N N' e hN a) =
      quotientEquiv N N'' (e.trans e') hNN a := by
  obtain ⟨g, rfl⟩ := QuotientGroup.mk_surjective a
  rfl

variable (N : Subgroup G) (N' : Subgroup G') (e : G ≃* G')
variable (hN : N.map e.toMonoidHom = N')
variable (ρ : Representation ℂ N W) (ρ' : Representation ℂ N' W')
variable (π : Representation ℂ G X) (π' : Representation ℂ G' X')
variable (E : Representation.Equiv ρ (ρ'.comp (subgroupEquiv N N' e hN).toMonoidHom))
variable (F : Representation.Equiv π (π'.comp e.toMonoidHom))

theorem source_apply (n : N) (w : W) :
    E (ρ n w) = ρ' (subgroupEquiv N N' e hN n) (E w) :=
  congrArg (fun L : W →ₗ[ℂ] W' => L w) (E.isIntertwining' n)

theorem source_inverse_apply (n : N') (w : W') :
    E.symm (ρ' n w) = ρ ((subgroupEquiv N N' e hN).symm n) (E.symm w) := by
  have hi := congrArg (fun L : W' →ₗ[ℂ] W => L w)
    (E.symm.isIntertwining' ((subgroupEquiv N N' e hN).symm n))
  change E.symm (ρ' (subgroupEquiv N N' e hN ((subgroupEquiv N N' e hN).symm n)) w) = _ at hi
  rw [MulEquiv.apply_symm_apply] at hi
  exact hi

theorem target_apply (g : G) (x : X) : F (π g x) = π' (e g) (F x) :=
  congrArg (fun L : X →ₗ[ℂ] X' => L x) (F.isIntertwining' g)

theorem target_inverse_apply (g : G') (x : X') :
    F.symm (π' g x) = π (e.symm g) (F.symm x) := by
  have hi := congrArg (fun L : X' →ₗ[ℂ] X => L x) (F.symm.isIntertwining' (e.symm g))
  change F.symm (π' (e (e.symm g)) x) = _ at hi
  rw [MulEquiv.apply_symm_apply] at hi
  exact hi

/-- Transport on the literal Hom spaces. -/
def homMap : Space N ρ π →ₗ[ℂ] Space N' ρ' π' where
  toFun f :=
    { toLinearMap := F.toLinearMap.comp (f.toLinearMap.comp E.symm.toLinearMap)
      isIntertwining' n := by
        apply LinearMap.ext
        intro w
        change F (f (E.symm (ρ' n w))) = π' (n : G') (F (f (E.symm w)))
        rw [source_inverse_apply, space_intertwines, target_apply]
        congr 2
        have hh := congrArg (fun m : N' => (m : G')) ((subgroupEquiv N N' e hN).apply_symm_apply n)
        exact hh }
  map_add' f g := by ext w; simp
  map_smul' c f := by ext w; simp

@[simp] theorem homMap_apply (f : Space N ρ π) (w : W') :
    homMap N N' e hN ρ ρ' π π' E F f w = F (f (E.symm w)) := rfl

/-- The inverse transport on the literal Hom spaces. -/
def inverseHomMap : Space N' ρ' π' →ₗ[ℂ] Space N ρ π where
  toFun f :=
    { toLinearMap := F.symm.toLinearMap.comp (f.toLinearMap.comp E.toLinearMap)
      isIntertwining' n := by
        apply LinearMap.ext
        intro w
        change F.symm (f (E (ρ n w))) = π (n : G) (F.symm (f (E w)))
        rw [source_apply, space_intertwines, target_inverse_apply]
        simp }
  map_add' f g := by ext w; simp
  map_smul' c f := by ext w; simp

/-- The actual multiplicity-space isomorphism induced by an isomorphism of data. -/
def homEquiv : Space N ρ π ≃ₗ[ℂ] Space N' ρ' π' where
  __ := homMap N N' e hN ρ ρ' π π' E F
  invFun := inverseHomMap N N' e hN ρ ρ' π π' E F
  left_inv f := by
    ext w
    change F.symm (F (f (E.symm (E w)))) = f w
    rw [Representation.Equiv.symm_apply_apply, Representation.Equiv.symm_apply_apply]
  right_inv f := by
    ext w
    change F (F.symm (f (E (E.symm w)))) = f w
    rw [Representation.Equiv.apply_symm_apply, Representation.Equiv.apply_symm_apply]

@[simp] theorem homEquiv_apply (f : Space N ρ π) (w : W') :
    homEquiv N N' e hN ρ ρ' π π' E F f w = F (f (E.symm w)) := rfl

@[simp] theorem homEquiv_symm_apply (f : Space N' ρ' π') (w : W) :
    (homEquiv N N' e hN ρ ρ' π π' E F).symm f w = F.symm (f (E w)) := rfl

variable [N.Normal] [N'.Normal]

/-- The transported conjugation intertwiner, constructed from the original datum map. -/
def transportedIntertwiner (g : G) (I : Representation.Equiv ρ (conjugate N ρ g)) :
    Representation.Equiv ρ' (conjugate N' ρ' (e g)) :=
  Representation.Equiv.mk
    ((E.toLinearEquiv.symm.trans I.toLinearEquiv).trans E.toLinearEquiv) (by
    intro n
    apply LinearMap.ext
    intro w
    change E (I (E.symm (ρ' n w))) = ρ' (conjugation N' (e g) n) (E (I (E.symm w)))
    rw [source_inverse_apply, intertwiner_apply, source_apply, subgroupEquiv_conjugation]
    simp)

@[simp] theorem transportedIntertwiner_apply (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) (w : W') :
    transportedIntertwiner N N' e hN ρ ρ' E g I w = E (I (E.symm w)) := rfl

/-- Actual operators commute with the induced Hom-space map. -/
theorem operator_transport (g : G) (I : Representation.Equiv ρ (conjugate N ρ g))
    (f : Space N ρ π) :
    homEquiv N N' e hN ρ ρ' π π' E F (operator N ρ π g I f) =
      operator N' ρ' π' (e g) (transportedIntertwiner N N' e hN ρ ρ' E g I)
        (homEquiv N N' e hN ρ ρ' π π' E F f) := by
  ext w
  change F (π g (f (I.symm (E.symm w)))) =
    π' (e g) (F (f (E.symm (E (I.symm (E.symm w))))))
  rw [Representation.Equiv.symm_apply_apply, target_apply]

/-- Conjugacy of the actual multiplicity operators as endomorphisms. -/
theorem operator_transport_conj (g : G) (I : Representation.Equiv ρ (conjugate N ρ g)) :
    (operator N' ρ' π' (e g) (transportedIntertwiner N N' e hN ρ ρ' E g I)).toLinearMap =
      (homEquiv N N' e hN ρ ρ' π π' E F).conj (operator N ρ π g I).toLinearMap := by
  apply LinearMap.ext
  intro f
  have ht := operator_transport N N' e hN ρ ρ' π π' E F g I
    ((homEquiv N N' e hN ρ ρ' π π' E F).symm f)
  rw [LinearEquiv.apply_symm_apply] at ht
  exact ht.symm

/-- The transported representative has precisely the induced quotient class. -/
theorem transported_representative (a : G ⧸ N) :
    QuotientGroup.mk' N' (e (sectionMap N a)) = quotientEquiv N N' e hN a := by
  have hh := quotientEquiv_mk N N' e hN (sectionMap N a)
  rw [quotient_section] at hh
  exact hh.symm

variable [Representation.IsIrreducible ρ'] [FiniteDimensional ℂ W']

/-- The comparing cochain is obtained by Schur on the actual transported intertwiner. -/
def cochain (hρ : Invariant N ρ) (hρ' : Invariant N' ρ') (a : G ⧸ N) : ℂˣ :=
  CliffordChoices.intertwinerScalar N' ρ' (e (sectionMap N a))
    (CliffordChoices.representativeIntertwiner N' ρ' hρ'
      (quotientEquiv N N' e hN a) (e (sectionMap N a))
      (transported_representative N N' e hN a))
    (transportedIntertwiner N N' e hN ρ ρ' E (sectionMap N a) (sectionIntertwiner N ρ hρ a))

/-- Normalized section operators compare by the derived cochain and actual Hom conjugacy. -/
theorem sectionOperator_transport (hρ : Invariant N ρ) (hρ' : Invariant N' ρ')
    (a : G ⧸ N) :
    (sectionOperator N' ρ' π' hρ' (quotientEquiv N N' e hN a)).toLinearMap =
      (cochain N N' e hN ρ ρ' E hρ hρ' a : ℂ) •
        (homEquiv N N' e hN ρ ρ' π π' E F).conj (sectionOperator N ρ π hρ a).toLinearMap := by
  let J := transportedIntertwiner N N' e hN ρ ρ' E (sectionMap N a) (sectionIntertwiner N ρ hρ a)
  let K := CliffordChoices.representativeIntertwiner N' ρ' hρ'
    (quotientEquiv N N' e hN a) (e (sectionMap N a))
    (transported_representative N N' e hN a)
  have hc := CliffordChoices.operator_choice N' ρ' π' (e (sectionMap N a)) K J
  rw [CliffordChoices.operator_representative] at hc
  change (operator N' ρ' π' (e (sectionMap N a)) J).toLinearMap =
    (((cochain N N' e hN ρ ρ' E hρ hρ' a)⁻¹ : ℂˣ) : ℂ) •
      (sectionOperator N' ρ' π' hρ' (quotientEquiv N N' e hN a)).toLinearMap at hc
  have ht := operator_transport_conj N N' e hN ρ ρ' π π' E F (sectionMap N a)
    (sectionIntertwiner N ρ hρ a)
  calc
    _ = (cochain N N' e hN ρ ρ' E hρ hρ' a : ℂ) •
        (operator N' ρ' π' (e (sectionMap N a)) J).toLinearMap := by rw [hc]; simp [smul_smul]
    _ = _ := by rw [ht]; rfl

include E F

/-- The actual comparison cochain is normalized because both chosen operator families are. -/
theorem cochain_one (hρ : Invariant N ρ) (hρ' : Invariant N' ρ')
    [Nontrivial (Space N' ρ' π')] : cochain N N' e hN ρ ρ' E hρ hρ' 1 = 1 := by
  apply ProjectiveCocycle.scalar_injective (1 : Module.End ℂ (Space N' ρ' π')) one_ne_zero
  have hh := sectionOperator_transport N N' e hN ρ ρ' π π' E F hρ hρ' 1
  simpa [sectionOperator_one, Module.End.one_eq_id] using hh.symm

open scoped IsMulCommutative
open CocycleCommutator
variable [IsMulCommutative (G ⧸ N)] [IsMulCommutative (G' ⧸ N')]
variable [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
variable [Nontrivial (Space N ρ π)] [Nontrivial (Space N' ρ' π')]

/-- The actual cocycles differ by the explicitly constructed normalized coboundary. -/
theorem cocycle_transport (hρ : Invariant N ρ) (hρ' : Invariant N' ρ') (a b : G ⧸ N) :
    (CliffordCocycle.cocycle N' ρ' π' hρ').coeff
        (quotientEquiv N N' e hN a) (quotientEquiv N N' e hN b) =
      cochain N N' e hN ρ ρ' E hρ hρ' a * cochain N N' e hN ρ ρ' E hρ hρ' b /
        cochain N N' e hN ρ ρ' E hρ hρ' (a * b) * (CliffordCocycle.cocycle N ρ π hρ).coeff a b := by
  apply ProjectiveCocycle.conjugate_rescale_coefficients
    (fun a => (sectionOperator N ρ π hρ a).toLinearMap)
    (fun a => (sectionOperator N' ρ' π' hρ' (quotientEquiv N N' e hN a)).toLinearMap)
    (CliffordCocycle.sectionOperator_ne_zero N ρ π hρ)
    (CliffordCocycle.cocycle N ρ π hρ).coeff
    (fun a b => (CliffordCocycle.cocycle N' ρ' π' hρ').coeff
      (quotientEquiv N N' e hN a) (quotientEquiv N N' e hN b))
    (CliffordCocycle.sectionOperator_mul N ρ π hρ)
    _ (homEquiv N N' e hN ρ ρ' π π' E F)
    (cochain N N' e hN ρ ρ' E hρ hρ')
    (sectionOperator_transport N N' e hN ρ ρ' π π' E F hρ hρ') a b
  intro x y
  rw [map_mul]
  exact CliffordCocycle.sectionOperator_mul N' ρ' π' hρ'
    (quotientEquiv N N' e hN x) (quotientEquiv N N' e hN y)

/-- Isomorphisms of the original data preserve the intrinsic commutator pairing. -/
theorem commutator_preserved (hρ : Invariant N ρ) (hρ' : Invariant N' ρ') (a b : G ⧸ N) :
    commutator (CliffordCocycle.cocycle N' ρ' π' hρ')
      (quotientEquiv N N' e hN a) (quotientEquiv N N' e hN b) =
      commutator (CliffordCocycle.cocycle N ρ π hρ) a b := by
  exact ProjectiveCocycle.conjugate_rescale_commutator
    (fun a => (sectionOperator N ρ π hρ a).toLinearMap)
    (fun a => (sectionOperator N' ρ' π' hρ' a).toLinearMap)
    (CliffordCocycle.sectionOperator_ne_zero N ρ π hρ)
    (CliffordCocycle.cocycle N ρ π hρ) (CliffordCocycle.cocycle N' ρ' π' hρ')
    (CliffordCocycle.sectionOperator_mul N ρ π hρ)
    (CliffordCocycle.sectionOperator_mul N' ρ' π' hρ')
    (homEquiv N N' e hN ρ ρ' π π' E F) (quotientEquiv N N' e hN)
    (cochain N N' e hN ρ ρ' E hρ hρ')
    (sectionOperator_transport N N' e hN ρ ρ' π π' E F hρ hρ') a b

end PaperXI.CliffordTransport
