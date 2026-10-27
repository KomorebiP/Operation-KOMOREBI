import PaperXI.CliffordDatum

/-! Invertible operators on the actual space of subgroup intertwiners. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordMultiplicity
open CliffordDatum

variable {G W X : Type*} [Group G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]

/-- The actual multiplicity space, with no tensor identification supplied. -/
abbrev Space (N : Subgroup G) (ρ : Representation ℂ N W) (π : Representation ℂ G X) :=
  Representation.IntertwiningMap ρ (restriction N π)

theorem space_intertwines (N : Subgroup G) (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (f : Space N ρ π) (n : N) (w : W) :
    f (ρ n w) = π (n : G) (f w) := congrArg (fun F : W →ₗ[ℂ] X => F w) (f.isIntertwining' n)

theorem inverse_intertwines (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (g : G) (I : Representation.Equiv ρ (conjugate N ρ g)) (n : N) (w : W) :
    I.symm (ρ n w) = ρ (conjugation N g⁻¹ n) (I.symm w) := by
  have hi := congrArg (fun F : W →ₗ[ℂ] W => F w) (I.symm.isIntertwining' (conjugation N g⁻¹ n))
  change I.symm (ρ (conjugation N g (conjugation N g⁻¹ n)) w) = _ at hi
  simpa using hi

theorem action_conjugation (N : Subgroup G) [N.Normal] (π : Representation ℂ G X)
    (g : G) (n : N) (x : X) :
    π g (π (conjugation N g⁻¹ n : G) x) = π (n : G) (π g x) := by
  change (π g * π (conjugation N g⁻¹ n : G)) x = (π (n : G) * π g) x
  rw [← map_mul, ← map_mul]
  simp [mul_assoc]

/-- Literal forward operator; subgroup equivariance is proved in the definition. -/
def operatorMap (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) : Space N ρ π →ₗ[ℂ] Space N ρ π where
  toFun f :=
    { toLinearMap := (π g).comp (f.toLinearMap.comp I.symm.toLinearMap)
      isIntertwining' n := by
        apply LinearMap.ext
        intro w
        change π g (f (I.symm (ρ n w))) = π (n : G) (π g (f (I.symm w)))
        rw [inverse_intertwines, space_intertwines, action_conjugation] }
  map_add' f h := by ext w; simp
  map_smul' c f := by ext w; simp

@[simp] theorem operatorMap_apply (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) (f : Space N ρ π) (w : W) :
    operatorMap N ρ π g I f w = π g (f (I.symm w)) := rfl

/-- Literal inverse operator, proved to preserve the same actual Hom space. -/
def inverseMap (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) : Space N ρ π →ₗ[ℂ] Space N ρ π where
  toFun f :=
    { toLinearMap := (π g⁻¹).comp (f.toLinearMap.comp I.toLinearMap)
      isIntertwining' n := by
        apply LinearMap.ext
        intro w
        change π g⁻¹ (f (I (ρ n w))) = π (n : G) (π g⁻¹ (f (I w)))
        have hi := congrArg (fun F : W →ₗ[ℂ] W => F w) (I.isIntertwining' n)
        change I (ρ n w) = ρ (conjugation N g n) (I w) at hi
        rw [hi]
        change π g⁻¹ (f (ρ (conjugation N g n) (I w))) = _
        rw [space_intertwines]
        have ha := action_conjugation N π g⁻¹ n (f (I w))
        simp only [inv_inv] at ha
        exact ha }
  map_add' f h := by ext w; simp
  map_smul' c f := by ext w; simp

@[simp] theorem inverseMap_apply (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) (f : Space N ρ π) (w : W) :
    inverseMap N ρ π g I f w = π g⁻¹ (f (I w)) := rfl

/-- The invertible Clifford multiplicity operator. -/
def operator (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) : Space N ρ π ≃ₗ[ℂ] Space N ρ π where
  __ := operatorMap N ρ π g I
  invFun := inverseMap N ρ π g I
  left_inv f := by
    ext w
    change π g⁻¹ (π g (f (I.symm (I w)))) = f w
    rw [Representation.Equiv.symm_apply_apply]
    change (π g⁻¹ * π g) (f w) = f w
    rw [← map_mul, inv_mul_cancel, map_one]
    rfl
  right_inv f := by
    ext w
    change π g (π g⁻¹ (f (I (I.symm w)))) = f w
    rw [Representation.Equiv.apply_symm_apply]
    change (π g * π g⁻¹) (f w) = f w
    rw [← map_mul, mul_inv_cancel, map_one]
    rfl

@[simp] theorem operator_apply (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) (f : Space N ρ π) (w : W) :
    operator N ρ π g I f w = π g (f (I.symm w)) := rfl

@[simp] theorem operator_symm_apply (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) (f : Space N ρ π) (w : W) :
    (operator N ρ π g I).symm f w = π g⁻¹ (f (I w)) := rfl

/-- The normalized family obtained from the actual quotient section and invariance. -/
def sectionOperator (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (hρ : Invariant N ρ) (a : G ⧸ N) :
    Space N ρ π ≃ₗ[ℂ] Space N ρ π :=
  operator N ρ π (sectionMap N a) (sectionIntertwiner N ρ hρ a)

theorem sectionOperator_one (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (hρ : Invariant N ρ) :
    sectionOperator N ρ π hρ 1 = LinearEquiv.refl ℂ (Space N ρ π) := by
  ext f w
  change π (sectionMap N 1) (f ((sectionIntertwiner N ρ hρ 1).symm w)) = f w
  have hi : (sectionIntertwiner N ρ hρ 1).symm w = w := by
    calc
      _ = (sectionIntertwiner N ρ hρ 1).symm (sectionIntertwiner N ρ hρ 1 w) := by rw [sectionIntertwiner_one]
      _ = w := (sectionIntertwiner N ρ hρ 1).symm_apply_apply w
  simp [hi]

/-- Pointwise form of an actual conjugation intertwiner. -/
theorem intertwiner_apply (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (g : G) (I : Representation.Equiv ρ (conjugate N ρ g)) (n : N) (w : W) :
    I (ρ n w) = ρ (conjugation N g n) (I w) :=
  congrArg (fun F : W →ₗ[ℂ] W => F w) (I.isIntertwining' n)

/-- Compose the actual conjugation intertwiners in the source convention. -/
def productIntertwiner (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (g h : G) (I : Representation.Equiv ρ (conjugate N ρ g))
    (J : Representation.Equiv ρ (conjugate N ρ h)) :
    Representation.Equiv ρ (conjugate N ρ (g * h)) :=
  Representation.Equiv.mk (J.toLinearEquiv.trans I.toLinearEquiv) (by
    intro n
    apply LinearMap.ext
    intro w
    change I (J (ρ n w)) = ρ (conjugation N (g * h) n) (I (J w))
    rw [intertwiner_apply, intertwiner_apply, conjugation_mul])

@[simp] theorem productIntertwiner_apply (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) (g h : G)
    (I : Representation.Equiv ρ (conjugate N ρ g))
    (J : Representation.Equiv ρ (conjugate N ρ h)) (w : W) :
    productIntertwiner N ρ g h I J w = I (J w) := rfl

/-- Any group action operator, with its actual inverse action. -/
def actionEquiv {K Y : Type*} [Group K] [AddCommGroup Y] [Module ℂ Y]
    (τ : Representation ℂ K Y) (k : K) : Y ≃ₗ[ℂ] Y where
  __ := τ k
  invFun := τ k⁻¹
  left_inv y := by
    change (τ k⁻¹ * τ k) y = y
    rw [← map_mul, inv_mul_cancel, map_one]
    rfl
  right_inv y := by
    change (τ k * τ k⁻¹) y = y
    rw [← map_mul, mul_inv_cancel, map_one]
    rfl

@[simp] theorem actionEquiv_apply {K Y : Type*} [Group K] [AddCommGroup Y] [Module ℂ Y]
    (τ : Representation ℂ K Y) (k : K) (y : Y) : actionEquiv τ k y = τ k y := rfl

/-- The adjusted intertwiner for multiplication of a representative by `n ∈ N`. -/
def subgroupIntertwiner (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (n : N) (g : G) (I : Representation.Equiv ρ (conjugate N ρ g)) :
    Representation.Equiv ρ (conjugate N ρ ((n : G) * g)) :=
  Representation.Equiv.mk (I.toLinearEquiv.trans (actionEquiv ρ n)) (by
    intro m
    apply LinearMap.ext
    intro w
    change ρ n (I (ρ m w)) = ρ (conjugation N ((n : G) * g) m) (ρ n (I w))
    rw [intertwiner_apply]
    change (ρ n * ρ (conjugation N g m)) (I w) =
      (ρ (conjugation N ((n : G) * g) m) * ρ n) (I w)
    rw [← map_mul, ← map_mul]
    congr 2
    apply Subtype.ext
    simp [mul_assoc])

@[simp] theorem subgroupIntertwiner_apply (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) (n : N) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) (w : W) :
    subgroupIntertwiner N ρ n g I w = ρ n (I w) := rfl

/-- The section-defect-adjusted intertwiner with exactly the product representative target. -/
def defectIntertwiner (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (hρ : Invariant N ρ) (a b : G ⧸ N) :
    Representation.Equiv ρ (conjugate N ρ (sectionMap N a * sectionMap N b)) :=
  Representation.Equiv.mk
    (subgroupIntertwiner N ρ (defect N a b) (sectionMap N (a * b))
      (sectionIntertwiner N ρ hρ (a * b))).toLinearEquiv (by
    intro n
    apply LinearMap.ext
    intro w
    have hi := intertwiner_apply N ρ
      ((defect N a b : G) * sectionMap N (a * b))
      (subgroupIntertwiner N ρ (defect N a b) (sectionMap N (a * b))
        (sectionIntertwiner N ρ hρ (a * b))) n w
    change ρ (defect N a b) (sectionIntertwiner N ρ hρ (a * b) (ρ n w)) =
      ρ (conjugation N ((defect N a b : G) * sectionMap N (a * b)) n)
        (ρ (defect N a b) (sectionIntertwiner N ρ hρ (a * b) w)) at hi
    rw [← section_mul] at hi
    exact hi)

@[simp] theorem defectIntertwiner_apply (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) (hρ : Invariant N ρ) (a b : G ⧸ N) (w : W) :
    defectIntertwiner N ρ hρ a b w = ρ (defect N a b) (sectionIntertwiner N ρ hρ (a * b) w) := rfl

/-- Multiplicity composition follows the reversed inverse composition on `W`. -/
theorem operator_product (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (g h : G)
    (I : Representation.Equiv ρ (conjugate N ρ g))
    (J : Representation.Equiv ρ (conjugate N ρ h)) :
    (operator N ρ π g I).toLinearMap * (operator N ρ π h J).toLinearMap =
      (operator N ρ π (g * h) (productIntertwiner N ρ g h I J)).toLinearMap := by
  ext f w
  change π g (π h (f (J.symm (I.symm w)))) = π (g * h) (f (J.symm (I.symm w)))
  rw [map_mul]
  rfl

/-- Changing the representative by an actual subgroup factor cancels on `Hom_N`. -/
theorem operator_subgroup_mul (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (π : Representation ℂ G X) (n : N) (g : G)
    (I : Representation.Equiv ρ (conjugate N ρ g)) :
    operator N ρ π ((n : G) * g) (subgroupIntertwiner N ρ n g I) = operator N ρ π g I := by
  ext f w
  let T := operator N ρ π g I f
  change π ((n : G) * g) (f (I.symm (ρ n⁻¹ w))) = π g (f (I.symm w))
  rw [map_mul]
  change π (n : G) (T (ρ n⁻¹ w)) = T w
  rw [space_intertwines]
  change (π (n : G) * π (n⁻¹ : N)) (T w) = T w
  rw [← map_mul]
  simp

end PaperXI.CliffordMultiplicity
