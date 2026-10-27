import FrobeniusRestrictionNorm
import UnramifiedGaugeObstruction

/-! Compute localization compatibility with a SHARED global Frobenius correction.
The map is explicit: norms for restriction, coboundaries for local gauge. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum
variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable (D : Datum G A B)

def frobeniusLocalization (F : Aˣ) (degree : I → ℕ) :
    D.Kernel × (I → D.Kernel) →ₗ[ℤ] (I → D.Kernel) :=
  LinearMap.pi fun i =>
    (D.frobeniusNorm F (degree i)).comp (LinearMap.fst ℤ D.Kernel (I → D.Kernel)) +
    (LinearMap.proj i).comp (LinearMap.snd ℤ D.Kernel (I → D.Kernel)) -
    (D.conjugate (F ^ degree i)).comp
      ((LinearMap.proj i).comp (LinearMap.snd ℤ D.Kernel (I → D.Kernel)))

@[simp] theorem frobeniusLocalization_apply (F : Aˣ) (degree : I → ℕ)
    (x : D.Kernel) (z : I → D.Kernel) (i : I) :
    D.frobeniusLocalization F degree (x,z) i =
      D.frobeniusNorm F (degree i) x + z i - D.conjugate (F^degree i) (z i) := rfl

abbrev FrobeniusLocalizationCokernel (F : Aˣ) (degree : I → ℕ) :=
  (I → D.Kernel) ⧸ LinearMap.range (D.frobeniusLocalization F degree)

noncomputable def frobeniusMatchingClass (F : Aˣ) (degree : I → ℕ) (V : I → Aˣ)
    (hV : ∀ i, D.q (V i) = D.q (F^degree i)) :
    D.FrobeniusLocalizationCokernel F degree :=
  Submodule.Quotient.mk (fun i => D.unitMismatch (V i) (F^degree i) (hV i))

/-- One global change must serve all restrictions. The local gauge terms are independent. -/
theorem simultaneous_frobenius_matching_iff_class_zero
    (F : Aˣ) (degree : I → ℕ) (V : I → Aˣ)
    (hV : ∀ i, D.q (V i) = D.q (F^degree i)) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧
      ∃ u : I → Aˣ, (∀ i, D.q (u i) = 1) ∧
        ∀ i, u i * F'^degree i * (u i)⁻¹ = V i) ↔
    D.frobeniusMatchingClass F degree V hV = 0 := by
  change _ ↔ (Submodule.Quotient.mk _ : D.FrobeniusLocalizationCokernel F degree) = 0
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨F',hF',u,hu,hmatch⟩
    let x := D.unitMismatch F' F hF'
    classical
    choose z hz using fun i => D.every_residual_one_unit_is_kernelUnit (u i) (hu i)
    refine ⟨(x,z),?_⟩
    funext i
    have hx : D.kernelUnit x * F = F' := D.unitMismatch_spec F' F hF'
    have he := hmatch i
    rw [← hx, ← hz i, D.conjugate_kernel_perturbed_power] at he
    change D.frobeniusNorm F (degree i) x + z i - D.conjugate (F^degree i) (z i) = _
    apply D.kernelUnit_injective
    apply mul_right_cancel (b := F^degree i)
    rw [D.unitMismatch_spec]
    exact he
  · rintro ⟨⟨x,z⟩,hxz⟩
    refine ⟨D.kernelUnit x * F,?_,fun i => D.kernelUnit (z i),
      fun i => D.kernelUnit_residue _,?_⟩
    · change D.q ((D.kernelUnit x : A)*(F : A)) = D.q F
      rw [map_mul,D.kernelUnit_residue,one_mul]
    · intro i
      rw [D.conjugate_kernel_perturbed_power]
      have he := congrFun hxz i
      change D.frobeniusNorm F (degree i) x + z i - D.conjugate (F^degree i) (z i) = _ at he
      rw [he,D.unitMismatch_spec]

end Komorebi.StrongArtin.SquareZeroH2.Datum

namespace Komorebi.StrongArtin.Procyclic
variable {A B I : Type} [Ring A] [Ring B] [Finite A]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

/-- The actual v0.29 class and the explicit Frobenius norm cokernel have the same
vanishing criterion, without assuming a comparison of two unspecified H1 spaces. -/
theorem gauge_obstruction_zero_iff_explicit_norm_class_zero
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Zhat →ₜ* Bˣ) (degree : I → ℕ) (t : I → (Zhat →ₜ* Aˣ))
    (ht : ∀ i z, q (t i z) = (rho (degreeMap (degree i) z) : B))
    (F : Aˣ) (hF : q F = (rho frobenius : B))
    (hV : ∀ i, q (t i frobenius) = q (F^degree i)) :
    (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).localConjugacyObstruction
      (fun _ : I => Zhat)
      (SquareZeroH2.continuousSectionDatum_continuous_lift q hq hsq rho.toMonoidHom
        rho.continuous)
      (fun i => (degreeMap (degree i)).toMonoidHom) (fun i => (degreeMap (degree i)).continuous)
      (fun i => (t i).toMonoidHom) ht (fun i => (t i).continuous) = 0 ↔
    (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).frobeniusMatchingClass
      F degree (fun i => t i frobenius) hV = 0 := by
  rw [local_gauge_obstruction_zero_iff_frobenius_system]
  have he := (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).simultaneous_frobenius_matching_iff_class_zero F degree (fun i => t i frobenius) hV
  simpa only [SquareZeroH2.continuousSectionDatum, hF] using he

end Komorebi.StrongArtin.Procyclic
