import PaperXII.LocalQuotients
import PaperXII.ClassSpines
import Mathlib.Algebra.MvPolynomial.Eval

/-! Effectivity for declared polynomial quotient conditions on actual matrix
entries. Every positive precision detects the same ideal. Arbitrary arithmetic
conditions are not identified with such an ideal without a separate argument. -/
set_option autoImplicit false
namespace PaperXII.AdicLocalConditions

open ContinuousMonoidHom Matrix
open AdicMatrixGroups AdicCompanions ClassCompanions ContinuousClasses LocalQuotients

variable {R S : Type} [CommRing R] [CommRing S] (I : Ideal R)

/-- Vanishing on an ideal is detected at every positive adic precision. -/
theorem ideal_killed_iff_positive [IsHausdorff I R] (J : Ideal S) (f : S →+* R) :
    J ≤ RingHom.ker f ↔ ∀ n, 0 < n → J ≤ RingHom.ker ((quotientMap I n).comp f) := by
  constructor
  · intro h n _ a ha
    change quotientMap I n (f a) = 0
    rw [show f a = 0 from h ha, map_zero]
  · intro h a ha
    change f a = 0
    apply PaperX.RepresentationLimits.scalar_ext I
    intro n
    cases n with
    | zero =>
      have : Subsingleton (R ⧸ I ^ 0) := coeff_zero_subsingleton I
      exact Subsingleton.elim _ _
    | succ n =>
      have hn := h (n + 1) (Nat.succ_pos n) ha
      change (Ideal.Quotient.mk (I ^ (n + 1))) (f a) = 0 at hn
      simpa only [map_zero] using hn

/-- Actual quotient factorization is detected by all positive finite reductions. -/
theorem factors_iff_positive [IsHausdorff I R] (J : Ideal S) (f : S →+* R) :
    Factors J f ↔ ∀ n, 0 < n → Factors J ((quotientMap I n).comp f) := by
  simp only [factors_iff, ideal_killed_iff_positive I]

variable {Γ ι : Type} [Group Γ] [TopologicalSpace Γ] [Fintype ι] [DecidableEq ι]

/-- Coordinates are the actual matrix entries at specified group elements. -/
abbrev Coordinates := Γ × ι × ι

/-- Evaluate the coordinate polynomial ring on the actual continuous adic representation. -/
def point (ρ : AdicRep (Γ := Γ) (ι := ι) I) : MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R →+* R :=
  MvPolynomial.eval₂Hom (RingHom.id R) (fun x ↦ (ρ x.1).val x.2.1 x.2.2)

/-- Finite evaluation uses the same polynomial coefficients reduced modulo I^n. -/
def finitePoint (n : ℕ) (σ : Γ →ₜ* GL ι (Coeff I n)) :
    MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R →+* Coeff I n :=
  MvPolynomial.eval₂Hom (quotientMap I n) (fun x ↦ (σ x.1).val x.2.1 x.2.2)

/-- Evaluation commutes with the actual reduction of continuous representations. -/
theorem point_reduces (ρ : AdicRep (Γ := Γ) (ι := ι) I) (n : ℕ) :
    (quotientMap I n).comp (point I ρ) = finitePoint I n (reduceRep I n ρ) := by
  rw [point, MvPolynomial.comp_eval₂Hom]
  rfl

/-- Every relation in a declared coordinate ideal holds integrally if it holds at all positive levels. -/
theorem ideal_effective [IsHausdorff I R]
    (J : Ideal (MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R))
    (ρ : AdicRep (Γ := Γ) (ι := ι) I)
    (h : ∀ n, 0 < n → J ≤ RingHom.ker (finitePoint I n (reduceRep I n ρ))) :
    J ≤ RingHom.ker (point I ρ) := by
  apply (ideal_killed_iff_positive I J (point I ρ)).mpr
  intro n hn
  rw [point_reduces]
  exact h n hn

/-- The original evaluation point has a unique map from the actual condition quotient. -/
theorem exists_unique_condition_factor [IsHausdorff I R]
    (J : Ideal (MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R))
    (ρ : AdicRep (Γ := Γ) (ι := ι) I)
    (h : ∀ n, 0 < n → J ≤ RingHom.ker (finitePoint I n (reduceRep I n ρ))) :
    ∃! g : (MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R) ⧸ J →+* R,
      g.comp (Ideal.Quotient.mk J) = point I ρ := by
  obtain ⟨g, hg⟩ := (factors_iff J (point I ρ)).mpr (ideal_effective I J ρ h)
  exact ⟨g, hg, fun k hk ↦ factor_unique J (point I ρ) k g hk hg⟩

/-- Class completion preserves the actual quotient condition when every allowed frame satisfies it. -/
theorem class_condition_preserved [IsHausdorff I R]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (J : Ideal (MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R))
    (ρ : AdicRealization I (Framed I C))
    (h : ∀ n, 0 < n → ∀ σ, Framed I C n σ → J ≤ RingHom.ker (finitePoint I n σ)) :
    Factors J (point I ρ.val) := by
  apply (factors_iff J _).mpr
  apply ideal_effective I J ρ.val
  intro n hn
  exact h n hn (reduceRep I n ρ.val) (ρ.property n)

/-- A whole indexed family of declared local ideals survives the same completion. -/
theorem all_class_conditions_preserved [IsHausdorff I R] {V : Type}
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (J : V → Ideal (MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R))
    (ρ : AdicRealization I (Framed I C))
    (h : ∀ v n, 0 < n → ∀ σ, Framed I C n σ → J v ≤ RingHom.ker (finitePoint I n σ)) :
    ∀ v, Factors (J v) (point I ρ.val) := fun v ↦ class_condition_preserved I C (J v) ρ (h v)

/-- Actual continuous class realizations exist with all specified polynomial quotient conditions. -/
theorem exists_class_realization_with_conditions [IsAdicComplete I R]
    (hI : I.FG) [Finite (R ⧸ I)]
    (C : ∀ n, LevelClass (Γ := Γ) (ι := ι) I n → Prop)
    (hC : ∀ n c, C (n + 1) c → C n (classStep I n c))
    (finiteC : ∀ n, 0 < n → Finite {c // C n c})
    (hc : ∀ n, 0 < n → ∀ c, C n c → PaperX.ClassInvariants.ClassContinuous c)
    (hne : ∀ n, 0 < n → ∃ c, C n c)
    {V : Type} (J : V → Ideal (MvPolynomial (Coordinates (Γ := Γ) (ι := ι)) R))
    (h : ∀ v n, 0 < n → ∀ σ, Framed I C n σ → J v ≤ RingHom.ker (finitePoint I n σ)) :
    ∃ ρ : AdicRealization I (Framed I C), ∀ v, Factors (J v) (point I ρ.val) := by
  obtain ⟨ρ⟩ := exists_class_realization_positive I hI C hC finiteC hc hne
  exact ⟨ρ, all_class_conditions_preserved I C J ρ h⟩

end PaperXII.AdicLocalConditions
