import PaperXI.InteractionPolynomial

/-! Invariant-space and restricted-operator comparison for a supplied finite
inertia quotient. No finite quotient is embedded into the original group. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InertiaQuotient
open Polynomial
open scoped Classical
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.InvariantPolynomial
variable {K V G H : Type*} [Field K] [AddCommGroup V] [Module K V] [Group G] [Group H]

theorem invariants_comp_of_surjective (ρ : Representation K G V) (s : H →* G)
    (hs : Function.Surjective s) : (Representation.invariants (ρ.comp s)) = ρ.invariants := by
  ext v
  constructor
  · intro hv g
    obtain ⟨x, rfl⟩ := hs g
    exact hv x
  · intro hv x
    exact hv (s x)

def invariantEquiv (ρ : Representation K G V) (s : H →* G) (hs : Function.Surjective s) :
    (Representation.invariants (ρ.comp s)) ≃ₗ[K] ρ.invariants :=
  LinearEquiv.ofEq _ _ (invariants_comp_of_surjective ρ s hs)

theorem invariantEquiv_apply (ρ : Representation K G V) (s : H →* G)
    (hs : Function.Surjective s) (v : (Representation.invariants (ρ.comp s))) :
    (invariantEquiv ρ s hs v : V) = v := rfl

variable {U I : Type*} [AddCommGroup U] [Module ℂ U] [Group I]
variable {M : ℕ} [NeZero M]

def factoredFrobenius (ρ : Action (K := ℂ) (V := U) (M := M))
    (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s) :
    (Representation.invariants (ρ.comp s)) ≃ₗ[ℂ] (Representation.invariants (ρ.comp s)) :=
  ((invariantEquiv ρ s hs).trans (fixedFrobenius ρ F q h)).trans (invariantEquiv ρ s hs).symm

/-- The transported map is exactly F on the original inertia-fixed vectors. -/
theorem factoredFrobenius_apply (ρ : Action (K := ℂ) (V := U) (M := M))
    (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s)
    (v : (Representation.invariants (ρ.comp s))) : (factoredFrobenius ρ F q h s hs v : U) = F v := by
  simp [factoredFrobenius, invariantEquiv, fixedFrobenius]

theorem factored_polynomial_eq [FiniteDimensional ℂ U]
    (ρ : Action (K := ℂ) (V := U) (M := M)) (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s) :
    operatorPolynomial (factoredFrobenius ρ F q h s hs).toLinearMap = localPolynomial ρ F q h := by
  change operatorPolynomial ((invariantEquiv ρ s hs).symm.conj
    (fixedFrobenius ρ F q h).toLinearMap) = _
  exact operatorPolynomial_conj _ _

theorem factored_local_polynomial [FiniteDimensional ℂ U]
    (ρ : Action (K := ℂ) (V := U) (M := M)) (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s)
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) ℂ U) (j : ZMod M) {v : U}
    (hv : v ∈ packet ρ j) (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v)
    (c : ℂ) (hclose : (F ^ n) v = c • v) :
    operatorPolynomial (factoredFrobenius ρ F q h s hs).toLinearMap =
      if j = 0 then 1 - C c * X ^ n else 1 := by
  rw [factored_polynomial_eq]
  exact PaperXI.InteractionPolynomial.local_polynomial ρ F q h hn b j hv hb c hclose

theorem factored_character_trivial_iff
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s) (j : ZMod M) :
    (∀ x : I, ZMod.stdAddChar (j * (s x).toAdd) = (1 : ℂ)) ↔ j = 0 := by
  constructor
  · intro h
    apply (PaperXI.InteractionPolynomial.character_trivial_iff j).mp
    intro a
    obtain ⟨x, hx⟩ := hs (Multiplicative.ofAdd a)
    simpa [hx] using h x
  · rintro rfl
    simp

/-- The literal determinant on the original inertia-fixed space, in any basis. -/
theorem factored_determinant [FiniteDimensional ℂ U]
    (ρ : Action (K := ℂ) (V := U) (M := M)) (F : U ≃ₗ[ℂ] U) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s)
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) ℂ U) (j : ZMod M) {v : U}
    (hv : v ∈ packet ρ j) (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v)
    (c : ℂ) (hclose : (F ^ n) v = c • v)
    {κ : Type*} [Fintype κ] [DecidableEq κ] (B : Module.Basis κ ℂ (Representation.invariants (ρ.comp s))) :
    Matrix.det (1 - (X : ℂ[X]) •
      (LinearMap.toMatrix B B (factoredFrobenius ρ F q h s hs).toLinearMap).map C) =
      if (∀ x : I, ZMod.stdAddChar (j * (s x).toAdd) = (1 : ℂ))
      then 1 - C c * X ^ n else 1 := by
  rw [← operatorPolynomial_eq_det _ B, factored_local_polynomial ρ F q h s hs hn b j hv hb c hclose]
  simp only [factored_character_trivial_iff s hs]

end PaperXI.InertiaQuotient
