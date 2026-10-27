import SurjectiveSquareZeroDatum
import Mathlib.Topology.Algebra.Group.Units
import Mathlib.Topology.Algebra.Ring.Basic

/-! Continuity for the actual square-zero coefficient action and defect.
The source carries its given topology; no discrete topology is imposed on it. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G]
variable [TopologicalSpace A] [DiscreteTopology A]

namespace Datum

variable (D : Datum G A B)

theorem continuous_kernel_action (hr : Continuous D.lift) :
    Continuous (fun z : G × D.Kernel => D.action z.1 z.2) := by
  have h : Continuous (fun z : Aˣ × D.Kernel => D.conjugate z.1 z.2) :=
    continuous_of_discreteTopology
  exact h.comp ((hr.comp continuous_fst).prodMk continuous_snd)

theorem continuous_normalizedDefect [IsTopologicalGroup G] (s : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (hc : Continuous s) :
    Continuous (D.normalizedDefect s hs) := by
  apply Continuous.subtype_mk
  change Continuous (fun z : G × G =>
    ((s z.1 : A) * (s z.2 : A) - s (z.1*z.2)) * ↑(s (z.1*z.2))⁻¹)
  exact (((Units.continuous_val.comp hc).comp continuous_fst).mul
    ((Units.continuous_val.comp hc).comp continuous_snd) |>.sub
      ((Units.continuous_val.comp hc).comp continuous_mul)).mul
      ((Units.continuous_coe_inv.comp hc).comp continuous_mul)

theorem continuous_liftDifference (s t : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (ht : ∀ g, D.q (t g) = D.rho g)
    (hsc : Continuous s) (htc : Continuous t) :
    Continuous (D.liftDifference s t hs ht) := by
  apply Continuous.subtype_mk
  change Continuous (fun g => ((t g : A)-(s g : A))*↑(s g)⁻¹)
  exact ((Units.continuous_val.comp htc).sub
    (Units.continuous_val.comp hsc)).mul (Units.continuous_coe_inv.comp hsc)

theorem continuous_correctedLift (hr : Continuous D.lift)
    {b : G → D.Kernel} (hb : Continuous b) : Continuous (D.correctedLift b) := by
  have hu : Continuous D.kernelUnit := continuous_of_discreteTopology
  exact (hu.comp hb).mul hr

theorem continuous_liftFromPrimitive (hr : Continuous D.lift)
    (b : G → D.Kernel) (hc : Continuous b)
    (hb : ∀ g h, D.normalizedDefect D.lift D.lift_residue (g,h) =
      D.action g (b h) - b (g*h) + b g) :
    Continuous (D.liftFromPrimitive b hb) := by
  exact D.continuous_correctedLift hr hc.neg

end Datum

/-- Normalize the section at the residual unit, not just at g=1.
This ensures the section composed with a continuous residual map is continuous. -/
noncomputable def normalizedUnitSection (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0) : Bˣ → Aˣ := by
  classical
  exact fun u => if u=1 then 1 else
    Classical.choose (units_lift_across_square_zero q hq hsq u)

omit [TopologicalSpace A] [DiscreteTopology A] in
@[simp] theorem normalizedUnitSection_one (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0) :
    normalizedUnitSection q hq hsq 1 = 1 := by
  classical
  simp [normalizedUnitSection]

omit [TopologicalSpace A] [DiscreteTopology A] in
theorem normalizedUnitSection_residue (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0) (u : Bˣ) :
    q (normalizedUnitSection q hq hsq u) = (u : B) := by
  classical
  by_cases hu : u=1
  · subst u; simp
  · simp only [normalizedUnitSection, hu, ite_false]
    exact Classical.choose_spec (units_lift_across_square_zero q hq hsq u)

noncomputable def continuousSectionDatum (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0) (rho : G →* Bˣ) : Datum G A B where
  q := q
  squareZero := hsq
  rho := (Units.coeHom B).comp rho
  lift := fun g => normalizedUnitSection q hq hsq (rho g)
  lift_one := by simp
  lift_residue := fun g => normalizedUnitSection_residue q hq hsq (rho g)

omit [DiscreteTopology A] in
theorem continuousSectionDatum_continuous_lift
    [TopologicalSpace B] [DiscreteTopology B]
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho) :
    Continuous (continuousSectionDatum q hq hsq rho).lift := by
  exact (continuous_of_discreteTopology : Continuous (normalizedUnitSection q hq hsq)).comp hrho

end Komorebi.StrongArtin.SquareZeroH2
