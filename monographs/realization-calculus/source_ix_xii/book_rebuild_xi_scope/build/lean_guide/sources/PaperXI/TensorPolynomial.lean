import PaperXI.PolynomialAssembly

/-! Corollary 5.5: actual inertia determinant and rational local-factor products. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TensorPolynomial
open scoped BigOperators Classical
open Polynomial PaperXI.CyclicAction PaperXI.PacketTransport
open PaperXI.InvariantPolynomial PaperXI.InertiaQuotient PaperXI.PolynomialAssembly
variable {I W : Type*} [Group I] [AddCommGroup W] [Module ℂ W]
variable {M : ℕ} [NeZero M]

theorem quotient_stable (ρ : Action (K := ℂ) (V := W) (M := M))
    (F : W ≃ₗ[ℂ] W) (q : (ZMod M)ˣ)
    (hrel : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s) :
    ∀ x ∈ Representation.invariants (ρ.comp s), F x ∈ Representation.invariants (ρ.comp s) := by
  rw [invariants_comp_of_surjective ρ s hs]
  intro x hx
  exact PaperXI.InertiaFixed.fixed_forward ρ F q hrel hx

theorem restricted_eq_factored (ρ : Action (K := ℂ) (V := W) (M := M))
    (F : W ≃ₗ[ℂ] W) (q : (ZMod M)ˣ)
    (hrel : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s) :
    restricted (ρ.comp s) F.toLinearMap (quotient_stable ρ F q hrel s hs) =
      (factoredFrobenius ρ F q hrel s hs).toLinearMap := by
  apply LinearMap.ext
  intro x
  apply Subtype.ext
  exact (factoredFrobenius_apply ρ F q hrel s hs x).symm

theorem cyclePolynomial_ne_zero {n : ℕ} (hn : 0 < n) (c : ℂ) :
    (1 - C c * X ^ n : ℂ[X]) ≠ 0 := by
  intro h
  have hc := congrArg (fun p : ℂ[X] => p.coeff 0) h
  simp [Ne.symm hn.ne'] at hc

variable {U : Type*} [AddCommGroup U] [Module ℂ U] [FiniteDimensional ℂ U]
variable {A : Type*} [Fintype A] {V : A → Type*}
variable [∀ a, AddCommGroup (V a)] [∀ a, Module ℂ (V a)] [∀ a, FiniteDimensional ℂ (V a)]
variable (ρ₀ : Representation ℂ I U) (ρ : ∀ a, Action (K := ℂ) (V := V a) (M := M))
variable (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s)
variable (e : U ≃ₗ[ℂ] (∀ a, V a)) (he : ∀ g x a, e (ρ₀ g x) a = ρ a (s g) (e x a))
variable (F : U ≃ₗ[ℂ] U) (T : ∀ a, V a ≃ₗ[ℂ] V a) (q : (ZMod M)ˣ)
variable (hrel : ∀ a, (T a).symm.conj (operator (ρ a) 1) = operator (ρ a) (q : ZMod M))
variable (hmap : ∀ x a, e (F x) a = T a (e x a))
variable (n : A → ℕ) (hn : ∀ a, 0 < n a) (b : ∀ a, Module.Basis (Fin (n a)) ℂ (V a))
variable (j : A → ZMod M) (v : ∀ a, V a) (hv : ∀ a, v a ∈ packet (ρ a) (j a))
variable (hb : ∀ a (i : Fin (n a)), b a i = (T a ^ (i : ℕ)) (v a))
variable (c : A → ℂ) (hclose : ∀ a, (T a ^ n a) (v a) = c a • v a)

omit [FiniteDimensional ℂ U] [Fintype A] [∀ a, FiniteDimensional ℂ (V a)] in
include he hmap hrel hs in
/-- Invariance of the total fixed space is derived from the packet action. -/
theorem total_stable : ∀ x ∈ ρ₀.invariants, F x ∈ ρ₀.invariants :=
  stable_of_decomposition ρ₀ (fun a => (ρ a).comp s) e he F.toLinearMap
    (fun a => (T a).toLinearMap) (fun a => quotient_stable (ρ a) (T a) q (hrel a) s hs) hmap

variable (hF : ∀ x ∈ ρ₀.invariants, F x ∈ ρ₀.invariants)
include he hmap hrel hs hn hv hb hclose

theorem polynomial_packets :
    operatorPolynomial (restricted ρ₀ F.toLinearMap hF) =
      ∏ a ∈ Finset.univ.filter (fun a => j a = 0), (1 - C (c a) * X ^ n a) := by
  rw [polynomial_product ρ₀ (fun a => (ρ a).comp s) e he F.toLinearMap
    (fun a => (T a).toLinearMap) hF
    (fun a => quotient_stable (ρ a) (T a) q (hrel a) s hs) hmap]
  rw [Finset.prod_filter]
  apply Finset.prod_congr rfl
  intro a _
  rw [restricted_eq_factored]
  exact factored_local_polynomial (ρ a) (T a) q (hrel a) s hs (hn a) (b a) (j a) (hv a) (hb a) (c a) (hclose a)

theorem determinant_packets {κ : Type*} [Fintype κ] [DecidableEq κ]
    (B : Module.Basis κ ℂ ρ₀.invariants) :
    Matrix.det (1 - (X : ℂ[X]) • (LinearMap.toMatrix B B (restricted ρ₀ F.toLinearMap hF)).map C) =
      ∏ a ∈ Finset.univ.filter (fun a => j a = 0), (1 - C (c a) * X ^ n a) := by
  rw [← operatorPolynomial_eq_det]
  exact polynomial_packets ρ₀ ρ s hs e he F T q hrel hmap n hn b j v hv hb c hclose hF

theorem localFactor_packets :
    localFactor ρ₀ F.toLinearMap hF =
      ∏ a ∈ Finset.univ.filter (fun a => j a = 0),
        (algebraMap ℂ[X] (RatFunc ℂ) (1 - C (c a) * X ^ n a))⁻¹ := by
  rw [localFactor, polynomial_packets ρ₀ ρ s hs e he F T q hrel hmap n hn b j v hv hb c hclose hF]
  simp only [map_prod, Finset.prod_inv_distrib]

end PaperXI.TensorPolynomial
