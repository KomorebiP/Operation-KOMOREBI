import PaperXI.SemisimpleDetection

/-! Primitive central character blocks in the literal finite group algebra.
Primitivity means absence of nontrivial central sub-idempotents, not rank one. -/
set_option autoImplicit false
noncomputable section
open scoped MonoidAlgebra BigOperators Classical
namespace PaperXI.PrimitiveCharacterBlock
open PaperXI.CharacterProjector PaperXI.SemisimpleDetection
universe u v w
variable {G : Type u} [Group G] [Fintype G]
variable {V : Type v} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
variable {W : Type w} [AddCommGroup W] [Module ℂ W]

omit [Fintype G] [FiniteDimensional ℂ V] in
/-- Representation equivalences intertwine the full group-algebra action. -/
theorem equiv_algebra_action (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    (e : Representation.Equiv ρ σ) (a : MonoidAlgebra ℂ G) (x : V) :
    e (ρ.asAlgebraHom a x) = σ.asAlgebraHom a (e x) := by
  induction a using MonoidAlgebra.induction_on with
  | of g => simpa using Representation.IntertwiningMap.isIntertwining ρ σ e.toIntertwiningMap g x
  | add a b ha hb => simp [ha, hb]
  | smul c a ha => simp [ha]

/-- The character element is nonzero. -/
theorem nonzero (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ] :
    element ρ ≠ 0 := by
  have := nontrivial_space ρ
  intro h
  have he : Nonempty (Representation.Equiv ρ ρ) := ⟨Representation.Equiv.refl ρ⟩
  have hi := irreducible_action ρ ρ
  simp [h, he] at hi

/-- Idempotence is an equality in C[G], detected through all simple modules. -/
theorem idempotent (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ] :
    element ρ * element ρ = element ρ := by
  apply eq_of_irreducible_actions
  intro W _ _ _ σ _
  rw [map_mul, irreducible_action ρ σ]
  split_ifs <;> simp

/-- The target irreducible detects every element supported on its central block. -/
theorem supported_eq_zero (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (a : MonoidAlgebra ℂ G) (hs : a * element ρ = a)
    (ha : ρ.asAlgebraHom a = 0) : a = 0 := by
  apply eq_zero_of_irreducible_actions
  intro W _ _ _ σ _
  by_cases he : Nonempty (Representation.Equiv ρ σ)
  · let e := Classical.choice he
    ext y
    obtain ⟨x, rfl⟩ := e.toLinearEquiv.surjective y
    change σ.asAlgebraHom a (e x) = 0
    rw [← equiv_algebra_action ρ σ e a x, ha]
    simp
  · calc
      σ.asAlgebraHom a = σ.asAlgebraHom (a * element ρ) := congrArg σ.asAlgebraHom hs.symm
      _ = 0 := by simp [irreducible_action ρ σ, he]

/-- Faithfulness on the designated block, not on the whole group algebra. -/
theorem block_action_injective (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (a b : MonoidAlgebra ℂ G) (ha : a * element ρ = a) (hb : b * element ρ = b)
    (hab : ρ.asAlgebraHom a = ρ.asAlgebraHom b) : a = b := by
  apply sub_eq_zero.mp
  apply supported_eq_zero ρ (a - b)
  · simp [sub_mul, ha, hb]
  · simp [hab]

/-- The standard central-primitive condition, stated directly. -/
def IsPrimitiveCentral {A : Type*} [Ring A] (e : A) : Prop :=
  e ≠ 0 ∧ e * e = e ∧ e ∈ Submonoid.center A ∧
    ∀ p : A, p ∈ Submonoid.center A → p * p = p → p * e = p → p = 0 ∨ p = e

/-- Proposition 4.2 for every finite group and irreducible complex representation. -/
theorem primitive_central (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ] :
    IsPrimitiveCentral (element ρ) := by
  refine ⟨nonzero ρ, idempotent ρ, central ρ, ?_⟩
  intro p hp hpp hpe
  have := nontrivial_space ρ
  obtain ⟨c, hc⟩ := central_scalar ρ hp
  have hmul := congrArg ρ.asAlgebraHom hpp
  rw [map_mul, hc] at hmul
  have hcc : c * c = c := by
    apply smul_left_injective ℂ (one_ne_zero : (1 : Module.End ℂ V) ≠ 0)
    simpa only [smul_mul_assoc, mul_smul_comm, one_mul, smul_smul] using hmul
  have hz : c * (c - 1) = 0 := by
    calc
      c * (c - 1) = c * c - c := by ring
      _ = 0 := by rw [hcc, sub_self]
  rcases mul_eq_zero.mp hz with hc0 | hc1
  · left
    exact supported_eq_zero ρ p hpe (by simp [hc, hc0])
  · right
    have hc1' : c = 1 := sub_eq_zero.mp hc1
    apply block_action_injective ρ p (element ρ) hpe (idempotent ρ)
    have he : Nonempty (Representation.Equiv ρ ρ) := ⟨Representation.Equiv.refl ρ⟩
    simp [hc, hc1', irreducible_action ρ ρ, he]

/-- A decomposition into orthogonal central sub-idempotents has a zero summand. -/
theorem no_nontrivial_central_split (ρ : Representation ℂ G V)
    [Representation.IsIrreducible ρ] (p q : MonoidAlgebra ℂ G)
    (hp : p ∈ Submonoid.center (MonoidAlgebra ℂ G))
    (hpp : p * p = p) (hpq : p * q = 0) (hs : p + q = element ρ) :
    p = 0 ∨ q = 0 := by
  have hpe : p * element ρ = p := by rw [← hs, mul_add, hpp, hpq, add_zero]
  rcases (primitive_central ρ).2.2.2 p hp hpp hpe with hz | he
  · exact Or.inl hz
  · right
    have hq : element ρ + q = element ρ + 0 := by simpa [he] using hs
    exact add_left_cancel hq

/-- Nonisomorphic irreducible characters give orthogonal central idempotents. -/
theorem orthogonal [FiniteDimensional ℂ W]
    (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (h : ¬Nonempty (Representation.Equiv ρ σ)) :
    element ρ * element σ = 0 := by
  apply supported_eq_zero σ
  · rw [mul_assoc, idempotent σ]
  · simp [irreducible_action ρ σ, h]

omit [FiniteDimensional ℂ V] in
/-- An isomorphic presentation does not change the literal character element. -/
theorem presentation_invariant
    (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    (e : Representation.Equiv ρ σ) : element ρ = element σ := by
  simp only [element, e.toLinearEquiv.finrank_eq, Representation.char_iso e]

end PaperXI.PrimitiveCharacterBlock
