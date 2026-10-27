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

omit [H.Normal] in
include hq hr hθ hU hcov in
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


section Existence
variable {G P A V : Type*} [Group G] [Group P] [CommGroup A]
  [AddCommGroup V] [Module ℂ V]

/-- The full finite-action interface: actual groups, original characters,
exact quotient maps, honest coprime automorphisms and equal labelled commutators
construct an irreducible actual action with its original theta and the unchanged
packet generator. No scalar cochain or covariance correction is assumed. -/
theorem exists_equivariant_actual_action
    (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
    (hinv : TypeSideDescent.Invariant D θ)
    (q : G →* A) (hker : q.ker = D)
    (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1)
    (H : Subgroup P) [H.Normal] (χ : H →* ℂˣ)
    (hχinv : TypeSideDescent.Invariant H χ)
    (r : P →* A) (hkerP : r.ker = H)
    (u : A → P) (hu : ∀ a, r (u a) = a) (hu1 : u 1 = 1)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (χ h : ℂ) • LinearMap.id)
    (α : G ≃* G) (γ : P ≃* P) (β : A ≃* A)
    (hq : ∀ g, q (α g) = β (q g)) (hr : ∀ p, r (γ p) = β (r p))
    (hθ : ∀ d : D, θ (subgroupMap D q hker α β hq d) = θ d)
    (hχ : ∀ h : H, χ (subgroupMap H r hkerP γ β hr h) = χ h)
    (U : V ≃ₗ[ℂ] V) (hU : ∀ p v, U (ρ p v) = ρ (γ p) (U v))
    (n m : ℕ) (hα : α ^ n = 1) (hγ : γ ^ n = 1)
    (hm : ∀ a : A, a ^ m = 1) (hcop : n.Coprime m)
    (hcomm : ∀ a b,
      sectionCocycle D θ q hker t ht a b / sectionCocycle D θ q hker t ht b a =
        sectionCocycle H χ r hkerP u hu a b / sectionCocycle H χ r hkerP u hu b a) :
    ∃ Ξ : Representation ℂ G V,
      IsIrreducible Ξ ∧ TypeSideDescent.Contains D θ Ξ ∧
        (∀ d : D, Ξ d = (θ d : ℂ) • LinearMap.id) ∧
        (∀ g v, U (Ξ g v) = Ξ (α g) (U v)) := by
  let c := actualScalarCocycle D θ hinv q hker t ht ht1
  let d := actualScalarCocycle H χ hχinv r hkerP u hu hu1
  let L := actualLift D θ hinv q hker t ht ht1 α β hq hθ
  let M := actualLift H χ hχinv r hkerP u hu hu1 γ β hr hχ
  have hβ : β ^ n = 1 := quotient_power_eq_one q t ht α β hq n hα
  have hL : L.action ^ n = 1 :=
    actualLift_power_eq_one D θ hinv q hker t ht ht1 α β hq hθ n hα
  have hM : M.action ^ n = 1 :=
    actualLift_power_eq_one H χ hχinv r hkerP u hu hu1 γ β hr hχ n hγ
  obtain ⟨s, hs1, hc, hsCov⟩ :=
    exists_equivariant_cochain c d β L M n m hβ hL hM hm hcop hcomm
  have hcov : ∀ a, actualPhase D θ q hker t ht α a * s (β a) =
      s a * actualPhase H χ r hkerP u hu γ a := by
    intro a
    simpa only [L, M, actualLift_phase] using hsCov a
  let Ξ := scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space ρ
  refine ⟨Ξ, scalarTransport_irreducible D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc,
    scalarTransport_contains D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc,
    scalarTransport_on_subgroup D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc, ?_⟩
  exact scalarTransport_covariant D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ
    α γ β hq hr hθ U hU s hs1 hc hcov

end Existence

end PaperXI.EquivariantRepresentation113
