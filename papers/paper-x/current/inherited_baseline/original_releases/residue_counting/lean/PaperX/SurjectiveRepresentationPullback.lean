import PaperX.CompatibleSystemRigidity

/-! Pullback along a surjective monoid homomorphism preserves and reflects the
actual representation structure: invariant subspaces, equivariant linear
isomorphisms, irreducibility, and characters. No finite-group or topological
assumption is needed for these algebraic statements. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.SurjectiveRepresentationPullback

section Algebra
variable {K G H V W : Type*} [Field K] [Monoid G] [Monoid H]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
variable (f : G →* H) (hf : Function.Surjective f)
variable (ρ : Representation K H V) (τ : Representation K H W)

include hf in
/-- Equivariance on a surjective pullback is exactly equivariance for the
original action. This applies to arbitrary linear maps, including projectors. -/
theorem intertwines_iff (u : V →ₗ[K] W) :
    (∀ g, u.comp ((ρ.comp f) g) = ((τ.comp f) g).comp u) ↔
      ∀ h, u.comp (ρ h) = (τ h).comp u := by
  constructor
  · intro hu h
    obtain ⟨g, rfl⟩ := hf h
    exact hu g
  · intro hu g
    exact hu (f g)

/-- Pull back an actual equivariant linear isomorphism. Surjectivity is not
needed in this direction. -/
def pullbackEquiv (e : ρ.Equiv τ) : Representation.Equiv (ρ.comp f) (τ.comp f) :=
  Representation.Equiv.mk e.toLinearEquiv (fun g => e.isIntertwining' (f g))

/-- Descend an actual equivariant linear isomorphism through a surjective
homomorphism. The underlying linear isomorphism does not change. -/
def equivOfPullback (e : Representation.Equiv (ρ.comp f) (τ.comp f)) : ρ.Equiv τ :=
  Representation.Equiv.mk e.toLinearEquiv
    ((intertwines_iff f hf ρ τ e.toLinearMap).mp e.isIntertwining')

@[simp]
theorem pullbackEquiv_apply (e : ρ.Equiv τ) (v : V) :
    pullbackEquiv f ρ τ e v = e v := rfl

@[simp]
theorem equivOfPullback_apply (e : Representation.Equiv (ρ.comp f) (τ.comp f)) (v : V) :
    equivOfPullback f hf ρ τ e v = e v := rfl

include hf in
/-- Surjective pullback preserves and reflects isomorphism of representations,
even on different coefficient modules. -/
theorem nonempty_equiv_iff :
    Nonempty (Representation.Equiv (ρ.comp f) (τ.comp f)) ↔ Nonempty (ρ.Equiv τ) := by
  constructor
  · rintro ⟨e⟩
    exact ⟨equivOfPullback f hf ρ τ e⟩
  · rintro ⟨e⟩
    exact ⟨pullbackEquiv f ρ τ e⟩

/-- The invariant-subspace lattices agree exactly under surjective pullback.
Both directions keep the underlying submodule. -/
def subrepresentationOrderIso : Subrepresentation (ρ.comp f) ≃o Subrepresentation ρ where
  toFun S :=
    { toSubmodule := S.toSubmodule
      apply_mem_toSubmodule := by
        intro h v hv
        obtain ⟨g, rfl⟩ := hf h
        exact S.apply_mem_toSubmodule g hv }
  invFun S :=
    { toSubmodule := S.toSubmodule
      apply_mem_toSubmodule := fun g _ hv => S.apply_mem_toSubmodule (f g) hv }
  left_inv S := by ext v; rfl
  right_inv S := by ext v; rfl
  map_rel_iff' := Iff.rfl

@[simp]
theorem subrepresentationOrderIso_toSubmodule (S : Subrepresentation (ρ.comp f)) :
    (subrepresentationOrderIso f hf ρ S).toSubmodule = S.toSubmodule := rfl

include hf in
/-- Irreducibility is preserved and reflected, including its nontriviality
requirement. No finite-dimensional hypothesis is required. -/
theorem isIrreducible_iff : Representation.IsIrreducible (ρ.comp f) ↔ ρ.IsIrreducible :=
  (subrepresentationOrderIso f hf ρ).isSimpleOrder_iff

/-- The character of a pullback is the original character evaluated at the
image of the acting element. -/
theorem character_pullback (g : G) :
    Representation.character (ρ.comp f) g = ρ.character (f g) := rfl

/-- A prescribed image identifies the actual character at every lift. -/
theorem character_of_image (g : G) (h : H) (hg : f g = h) :
    Representation.character (ρ.comp f) g = ρ.character h := by
  rw [character_pullback, hg]

end Algebra

section Systems
variable {Λ I G H : Type*} [Group G] [Group H]
variable {K : Λ → Type*} [∀ l, Field (K l)]
variable {W : Λ → I → Type*} [∀ l i, AddCommGroup (W l i)]
  [∀ l i, Module (K l) (W l i)]

/-- Pulling every member back through a surjection preserves and reflects the
componentwise equivalence relation used for compatible systems. -/
theorem memberwiseEquiv_iff (f : G →* H) (hf : Function.Surjective f)
    (ρ : (l : Λ) → (i : I) → Representation (K l) H (W l i)) (i j : I) :
    PaperX.CompatibleSystemRigidity.MemberwiseEquiv (fun l i => (ρ l i).comp f) i j ↔
      PaperX.CompatibleSystemRigidity.MemberwiseEquiv ρ i j := by
  constructor <;> intro h l
  · exact (nonempty_equiv_iff f hf (ρ l i) (ρ l j)).mp (h l)
  · exact (nonempty_equiv_iff f hf (ρ l i) (ρ l j)).mpr (h l)

end Systems
end PaperX.SurjectiveRepresentationPullback
