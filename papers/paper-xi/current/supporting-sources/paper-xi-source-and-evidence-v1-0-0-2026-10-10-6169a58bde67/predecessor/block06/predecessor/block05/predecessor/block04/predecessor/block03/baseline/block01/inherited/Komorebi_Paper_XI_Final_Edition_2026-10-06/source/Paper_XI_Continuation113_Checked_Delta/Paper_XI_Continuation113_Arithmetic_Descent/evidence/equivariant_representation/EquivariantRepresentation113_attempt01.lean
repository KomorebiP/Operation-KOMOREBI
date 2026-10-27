import PaperXI.ActualScalarLift113

/-! The corrected scalar cochain constructs an actual representation that
retains the original theta and intertwines the original packet generator.
Actual groups and their full automorphisms remain explicit inputs. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.EquivariantRepresentation113
open Representation ScalarRepresentation112 ActualScalarLift113 CyclicDefect113

section Covariance
variable {G P A V : Type*} [Group G] [Group P] [CommGroup A]
  [AddCommGroup V] [Module ℂ V]
  (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
  (hinv : TypeSideDescent.Invariant D θ)
  (q : G →* A) (hker : q.ker = D)
  (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1)
  (H : Subgroup P) [H.Normal] (χ : H →* ℂˣ)
  (r : P →* A) (hkerP : r.ker = H)
  (u : A → P) (hu : ∀ a, r (u a) = a) (hu1 : u 1 = 1)
  (ρ : Representation ℂ P V)
  (hρ : ∀ h : H, ρ h = (χ h : ℂ) • LinearMap.id)
  (α : G ≃* G) (γ : P ≃* P) (β : A ≃* A)
  (hq : ∀ g, q (α g) = β (q g)) (hr : ∀ p, r (γ p) = β (r p))
  (hθ : ∀ d : D, θ (subgroupMap D q hker α β hq d) = θ d)
  (U : V ≃ₗ[ℂ] V) (hU : ∀ p v, U (ρ p v) = ρ (γ p) (U v))
  (s : A → ℂˣ) (hs1 : s 1 = 1)
  (hc : ∀ a b, sectionCocycle D θ q hker t ht a b =
    (s a * s b / s (a*b)) * sectionCocycle H χ r hkerP u hu a b)
  (hcov : ∀ a, actualPhase D θ q hker t ht α a * s (β a) =
    s a * actualPhase H χ r hkerP u hu γ a)

/-- A covariant comparison cochain transfers the original packet generator
without changing that operator or the original theta. The final existence
theorem below derives the required cochain covariance. -/
theorem scalarTransport_covariant (g : G) (v : V) :
    U (scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc g v) =
      scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc (α g) (U v) := by
  have hcoeff :
      (sectionScalar D θ q hker t ht g * s (q g)) * actualPhase H χ r hkerP u hu γ (q g) =
        sectionScalar D θ q hker t ht (α g) * s (q (α g)) := by
    rw [sectionScalar_action D θ hinv q hker t ht ht1 α β hq hθ, hq]
    rw [mul_assoc, ← hcov, mul_assoc]
  change U (((sectionScalar D θ q hker t ht g * s (q g) : ℂˣ) : ℂ) • ρ (u (q g)) v) =
    ((sectionScalar D θ q hker t ht (α g) * s (q (α g)) : ℂˣ) : ℂ) •
      ρ (u (q (α g))) (U v)
  rw [map_smul, hU, packet_normalForm H χ r hkerP u hu ρ hρ (γ (u (q g)))]
  simp only [LinearMap.smul_apply, smul_smul]
  change (((sectionScalar D θ q hker t ht g * s (q g) : ℂˣ) : ℂ) *
    (actualPhase H χ r hkerP u hu γ (q g) : ℂ)) •
      ρ (u (r (γ (u (q g))))) (U v) = _
  rw [← Units.val_mul, hcoeff, hr, hu, hq]

end Covariance

end PaperXI.EquivariantRepresentation113
