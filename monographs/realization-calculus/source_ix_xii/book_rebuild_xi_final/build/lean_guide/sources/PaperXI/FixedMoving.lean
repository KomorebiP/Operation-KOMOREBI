import Mathlib.LinearAlgebra.BilinearForm.Orthogonal
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-! Actual fixed and moving subspaces, restricted symplectic forms and
the restricted moving automorphism. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FixedMoving

variable {F V : Type*} [Field F] [AddCommGroup V] [Module F V]

/-- The actual fixed subspace of the given automorphism. -/
def fixed (g : V ≃ₗ[F] V) : Submodule F V := LinearMap.ker (g.toLinearMap - LinearMap.id)

/-- The actual moving subspace, the image of `g - 1`. -/
def moving (g : V ≃ₗ[F] V) : Submodule F V := LinearMap.range (g.toLinearMap - LinearMap.id)

@[simp] theorem mem_fixed (g : V ≃ₗ[F] V) (v : V) : v ∈ fixed g ↔ g v = v := by
  simp [fixed, sub_eq_zero]

theorem mem_moving (g : V ≃ₗ[F] V) (v : V) :
    v ∈ moving g ↔ ∃ w : V, g w - w = v := Iff.rfl

/-- A fixed vector is orthogonal to every actual moving vector. -/
theorem orthogonal (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V)
    (hg : ∀ x y, b (g x) (g y) = b x y)
    {x y : V} (hx : x ∈ fixed g) (hy : y ∈ moving g) : b x y = 0 := by
  obtain ⟨z, rfl⟩ := hy
  have hfix : g x = x := (mem_fixed g x).mp hx
  change b x (g z - z) = 0
  rw [map_sub]
  have h := hg x z
  rw [hfix] at h
  rw [h, sub_self]

/-- Alternation gives orthogonality in the other order as well. -/
theorem orthogonal_reverse (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V)
    (hb : b.IsAlt) (hg : ∀ x y, b (g x) (g y) = b x y)
    {x y : V} (hx : x ∈ moving g) (hy : y ∈ fixed g) : b x y = 0 := by
  rw [← hb.neg_eq y x, orthogonal g b hg hy hx, neg_zero]

/-- The actual form restricted to the fixed subspace. -/
def fixedForm (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V) := b.restrict (fixed g)

/-- The actual form restricted to the moving image. -/
def movingForm (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V) := b.restrict (moving g)

theorem fixedForm_alt (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V) (hb : b.IsAlt) :
    (fixedForm g b).IsAlt := fun x => hb x

theorem movingForm_alt (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V) (hb : b.IsAlt) :
    (movingForm g b).IsAlt := fun x => hb x

/-- Nondegeneracy transfers to either actual orthogonal direct summand. -/
theorem restrict_nondegenerate (b : LinearMap.BilinForm F V) (hb : b.Nondegenerate)
    (P Q : Submodule F V) (hPQ : IsCompl P Q)
    (ho : ∀ x ∈ P, ∀ y ∈ Q, b x y = 0)
    (ho' : ∀ x ∈ Q, ∀ y ∈ P, b x y = 0) : (b.restrict P).Nondegenerate := by
  constructor
  · intro x hx
    apply Subtype.ext
    apply hb.1 x
    intro v
    obtain ⟨y, z, hy, hz, rfl⟩ := Submodule.codisjoint_iff_exists_add_eq.mp hPQ.codisjoint v
    change b (x : V) (y + z) = 0
    rw [map_add, ho x x.property z hz, add_zero]
    exact hx ⟨y, hy⟩
  · intro x hx
    apply Subtype.ext
    apply hb.2 x
    intro v
    obtain ⟨y, z, hy, hz, rfl⟩ := Submodule.codisjoint_iff_exists_add_eq.mp hPQ.codisjoint v
    change b (y + z) (x : V) = 0
    rw [map_add, LinearMap.add_apply, ho' z hz x x.property, add_zero]
    exact hx ⟨y, hy⟩

theorem movingForm_nondegenerate_of_isCompl (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V)
    (hb : b.IsAlt) (hbn : b.Nondegenerate) (hg : ∀ x y, b (g x) (g y) = b x y)
    (hc : IsCompl (fixed g) (moving g)) : (movingForm g b).Nondegenerate :=
  restrict_nondegenerate b hbn (moving g) (fixed g) hc.symm
    (fun _ hx _ hy => orthogonal_reverse g b hb hg hx hy)
    (fun _ hx _ hy => orthogonal g b hg hx hy)

theorem fixedForm_nondegenerate_of_isCompl (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V)
    (hb : b.IsAlt) (hbn : b.Nondegenerate) (hg : ∀ x y, b (g x) (g y) = b x y)
    (hc : IsCompl (fixed g) (moving g)) : (fixedForm g b).Nondegenerate :=
  restrict_nondegenerate b hbn (fixed g) (moving g) hc
    (fun _ hx _ hy => orthogonal g b hg hx hy)
    (fun _ hx _ hy => orthogonal_reverse g b hb hg hx hy)

theorem moving_stable (g : V ≃ₗ[F] V) {v : V} (hv : v ∈ moving g) : g v ∈ moving g := by
  obtain ⟨w, rfl⟩ := hv
  refine ⟨g w, ?_⟩
  change g (g w) - g w = g (g w - w)
  exact (map_sub g (g w) w).symm

theorem moving_inverse_stable (g : V ≃ₗ[F] V) {v : V} (hv : v ∈ moving g) :
    g.symm v ∈ moving g := by
  obtain ⟨w, rfl⟩ := hv
  refine ⟨g.symm w, ?_⟩
  change g (g.symm w) - g.symm w = g.symm (g w - w)
  simp

/-- The actual restriction of `g` to its moving image, including its proved inverse. -/
def movingAction (g : V ≃ₗ[F] V) : moving g ≃ₗ[F] moving g where
  toFun v := ⟨g v, moving_stable g v.property⟩
  invFun v := ⟨g.symm v, moving_inverse_stable g v.property⟩
  left_inv v := by apply Subtype.ext; exact g.symm_apply_apply v
  right_inv v := by apply Subtype.ext; exact g.apply_symm_apply v
  map_add' x y := by apply Subtype.ext; exact map_add g (x : V) (y : V)
  map_smul' c x := by apply Subtype.ext; exact map_smul g c (x : V)

@[simp] theorem movingAction_coe (g : V ≃ₗ[F] V) (v : moving g) :
    (movingAction g v : V) = g v := rfl

@[simp] theorem movingAction_symm_coe (g : V ≃ₗ[F] V) (v : moving g) :
    ((movingAction g).symm v : V) = g.symm v := rfl

theorem movingAction_preserves (g : V ≃ₗ[F] V) (b : LinearMap.BilinForm F V)
    (hg : ∀ x y, b (g x) (g y) = b x y) (x y : moving g) :
    movingForm g b (movingAction g x) (movingAction g y) = movingForm g b x y := hg x y

/-- The actual restricted automorphism has no nonzero fixed vector in a direct decomposition. -/
theorem movingAction_fixedPointFree_of_isCompl (g : V ≃ₗ[F] V)
    (hc : IsCompl (fixed g) (moving g)) (v : moving g) (hv : movingAction g v = v) : v = 0 := by
  apply Subtype.ext
  have hf : (v : V) ∈ fixed g := (mem_fixed g v).mpr (congrArg Subtype.val hv)
  have hi : (v : V) ∈ fixed g ⊓ moving g := ⟨hf, v.property⟩
  rw [hc.inf_eq_bot] at hi
  exact hi

/-- The restricted difference is injective by disjointness of the actual subspaces. -/
theorem moving_difference_injective (g : V ≃ₗ[F] V)
    (hc : IsCompl (fixed g) (moving g)) :
    Function.Injective ((movingAction g).toLinearMap - (LinearMap.id : Module.End F (moving g))) := by
  apply LinearMap.ker_eq_bot.mp
  apply bot_unique
  intro v hv
  change v = 0
  apply movingAction_fixedPointFree_of_isCompl g hc v
  change movingAction g v - v = 0 at hv
  exact sub_eq_zero.mp hv

/-- An actual linear equivalence for `g-1` on the moving image. -/
def movingDifferenceEquiv [FiniteDimensional F V] (g : V ≃ₗ[F] V)
    (hc : IsCompl (fixed g) (moving g)) : moving g ≃ₗ[F] moving g :=
  LinearEquiv.ofBijective ((movingAction g).toLinearMap - LinearMap.id)
    ⟨moving_difference_injective g hc,
      LinearMap.injective_iff_surjective.mp (moving_difference_injective g hc)⟩

@[simp] theorem movingDifferenceEquiv_apply [FiniteDimensional F V]
    (g : V ≃ₗ[F] V) (hc : IsCompl (fixed g) (moving g)) (v : moving g) :
    movingDifferenceEquiv g hc v = movingAction g v - v := rfl

section Transport
variable {V' : Type*} [AddCommGroup V'] [Module F V']

/-- Conjugacy restricts to the actual moving images, with a constructed inverse. -/
def movingEquiv (g : V ≃ₗ[F] V) (g' : V' ≃ₗ[F] V') (e : V ≃ₗ[F] V')
    (he : ∀ v, e (g v) = g' (e v)) : moving g ≃ₗ[F] moving g' where
  toFun v := ⟨e v, by
    obtain ⟨w, hw⟩ := v.property
    refine ⟨e w, ?_⟩
    change g' (e w) - e w = e v
    rw [← he, ← map_sub]
    exact congrArg e hw⟩
  invFun v := ⟨e.symm v, by
    obtain ⟨w, hw⟩ := v.property
    refine ⟨e.symm w, ?_⟩
    change g (e.symm w) - e.symm w = e.symm v
    apply e.injective
    rw [map_sub, he, e.apply_symm_apply, e.apply_symm_apply]
    exact hw⟩
  left_inv v := by apply Subtype.ext; exact e.symm_apply_apply v
  right_inv v := by apply Subtype.ext; exact e.apply_symm_apply v
  map_add' x y := by apply Subtype.ext; exact map_add e (x : V) (y : V)
  map_smul' c x := by apply Subtype.ext; exact map_smul e c (x : V)

@[simp] theorem movingEquiv_coe (g : V ≃ₗ[F] V) (g' : V' ≃ₗ[F] V') (e : V ≃ₗ[F] V')
    (he : ∀ v, e (g v) = g' (e v)) (v : moving g) :
    (movingEquiv g g' e he v : V') = e v := rfl

/-- Restricted conjugacy intertwines the two actual restricted automorphisms. -/
theorem movingEquiv_intertwines (g : V ≃ₗ[F] V) (g' : V' ≃ₗ[F] V') (e : V ≃ₗ[F] V')
    (he : ∀ v, e (g v) = g' (e v)) (v : moving g) :
    movingEquiv g g' e he (movingAction g v) = movingAction g' (movingEquiv g g' e he v) := by
  apply Subtype.ext
  exact he v

/-- An ambient symplectic conjugacy preserves the actual restricted moving forms. -/
theorem movingEquiv_preserves (g : V ≃ₗ[F] V) (g' : V' ≃ₗ[F] V') (e : V ≃ₗ[F] V')
    (he : ∀ v, e (g v) = g' (e v)) (b : LinearMap.BilinForm F V)
    (b' : LinearMap.BilinForm F V') (hb : ∀ x y, b' (e x) (e y) = b x y)
    (x y : moving g) : movingForm g' b' (movingEquiv g g' e he x) (movingEquiv g g' e he y) =
      movingForm g b x y := hb x y

end Transport
end PaperXI.FixedMoving
