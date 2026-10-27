import PaperX.GeneralCharacters

/-! Character rigidity for actual finite-dimensional irreducible representations.
The monoid need not be finite, and the characteristic-zero coefficient field need
not be algebraically closed. The topological consequence retains density of the
conjugacy-saturated samples as an explicit hypothesis. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.IrreducibleCharacterRigidity
universe u

section Algebra
variable {K G : Type*} {V W : Type u} [Field K] [Monoid G]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

/-- An actual equivariant linear isomorphism preserves the actual character. -/
theorem character_eq_of_equiv (ρ : Representation K G V) (τ : Representation K G W)
    (h : Nonempty (ρ.Equiv τ)) : ρ.character = τ.character := by
  obtain ⟨e⟩ := h
  exact Representation.char_iso e

variable [CharZero K] [FiniteDimensional K V] [FiniteDimensional K W]

/-- Character equality detects equivalence of irreducible representations on
possibly different vector spaces, for an arbitrary acting monoid. -/
theorem equiv_iff_character_eq (ρ : Representation K G V) (τ : Representation K G W)
    [ρ.IsIrreducible] [τ.IsIrreducible] :
    Nonempty (ρ.Equiv τ) ↔ ρ.character = τ.character := by
  constructor
  · exact character_eq_of_equiv ρ τ
  intro hchar
  by_contra hno
  let U : Bool → Type _ := fun b => match b with
    | false => V
    | true => W
  let (b : Bool) : AddCommGroup (U b) := by
    cases b <;> dsimp [U] <;> infer_instance
  let (b : Bool) : Module K (U b) := by
    cases b <;> dsimp [U] <;> infer_instance
  let (b : Bool) : FiniteDimensional K (U b) := by
    cases b <;> dsimp [U] <;> infer_instance
  let R : (b : Bool) → Representation K G (U b) := fun b => match b with
    | false => ρ
    | true => τ
  let (b : Bool) : (R b).IsIrreducible := by
    cases b <;> dsimp [R] <;> infer_instance
  have hne : ∀ i j, Nonempty ((R i).Equiv (R j)) → i = j := by
    intro i j hij
    cases i <;> cases j
    · rfl
    · exact False.elim (hno hij)
    · obtain ⟨e⟩ := hij
      exact False.elim (hno ⟨e.symm⟩)
    · rfl
  have hi := PaperX.GeneralCharacters.independent_irreducible_characters R hne
  have hbad : false = true := hi.injective hchar
  cases hbad

end Algebra

section Topological
variable {K G X : Type*} {V W : Type u} [Field K] [CharZero K] [Group G]
variable [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable [AddCommGroup W] [Module K W] [FiniteDimensional K W]
variable [TopologicalSpace G] [TopologicalSpace K] [T2Space K]

omit [CharZero K] [FiniteDimensional K V] [FiniteDimensional K W] in
/-- Continuous actual characters agreeing on samples agree everywhere when
the conjugacy saturation of those samples is dense. -/
theorem character_eq_of_dense_samples
    (ρ : Representation K G V) (τ : Representation K G W)
    (hρ : Continuous ρ.character) (hτ : Continuous τ.character) (s : X → G)
    (hd : DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹))
    (he : ∀ x, ρ.character (s x) = τ.character (s x)) :
    ρ.character = τ.character := by
  apply hd.equalizer hρ hτ
  funext p
  simpa only [Function.comp_apply, Representation.char_conj] using he p.1

/-- Dense conjugacy samples determine the equivalence class of an actual
irreducible representation. Arithmetic density is an input to this theorem. -/
theorem equiv_of_dense_character_eq
    (ρ : Representation K G V) (τ : Representation K G W)
    [ρ.IsIrreducible] [τ.IsIrreducible]
    (hρ : Continuous ρ.character) (hτ : Continuous τ.character) (s : X → G)
    (hd : DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹))
    (he : ∀ x, ρ.character (s x) = τ.character (s x)) :
    Nonempty (ρ.Equiv τ) :=
  (equiv_iff_character_eq ρ τ).mpr
    (character_eq_of_dense_samples ρ τ hρ hτ s hd he)

end Topological
end PaperX.IrreducibleCharacterRigidity
