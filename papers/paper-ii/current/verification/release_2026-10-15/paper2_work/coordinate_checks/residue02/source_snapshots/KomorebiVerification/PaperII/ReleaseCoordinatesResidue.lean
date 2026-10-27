import KomorebiVerification.PaperII.ResidueFourierCRT
import KomorebiVerification.PaperII.CommonRefinement

/-! Actual residue packet families, onto parent maps, and formal-series coordinates. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.Residue
open Komorebi.Foundation Komorebi.PaperII.NestedRefinement
universe u v
variable {R : Type u} {A : Type v}

/-- Residue selectors packaged as a complete family on all coefficient sequences. -/
def residueFamily [Semiring R] [AddCommMonoid A] [Module R A]
    (N : Nat) (hN : 0 < N) : LinearProjectorFamily R (Nat → A) (Fin N) :=
  Packet.fibreLinearProjectorFamily (residueAddress N hN)

theorem residueProj_nonzero [Semiring R] [AddCommMonoid A] [Module R A] [Nontrivial A]
    (N : Nat) (hN : 0 < N) (j : Fin N) :
    residueProj (R := R) (A := A) N hN j ≠ 0 := by
  obtain ⟨a, ha⟩ := exists_ne (0 : A)
  intro hz
  have hj : residueAddress N hN j.val = j := Fin.ext (Nat.mod_eq_of_lt j.isLt)
  have h := congrArg (fun f : Module.End R (Nat → A) => f (fun _ => a) j.val) hz
  have : a = 0 := by simpa [residueProj_apply, Packet.fibreProj, hj] using h
  exact ha this

theorem residueFamily_nonzero [Semiring R] [AddCommMonoid A] [Module R A] [Nontrivial A]
    (N : Nat) (hN : 0 < N) :
    Komorebi.PaperII.CommonRefinement.Nonzero (residueFamily (R := R) (A := A) N hN) :=
  residueProj_nonzero N hN

/-- The actual parent for arbitrary positive divisible moduli. -/
def divisorParent (N M : Nat) (hN : 0 < N) : Fin M → Fin N :=
  fun s => ⟨s.val % N, Nat.mod_lt s.val hN⟩

theorem divisorParent_surjective (N M : Nat) (hN : 0 < N) (hM : 0 < M)
    (hdiv : N ∣ M) : Function.Surjective (divisorParent N M hN) := by
  intro j
  refine ⟨⟨j.val, lt_of_lt_of_le j.isLt (Nat.le_of_dvd hM hdiv)⟩, ?_⟩
  exact Fin.ext (Nat.mod_eq_of_lt j.isLt)

theorem divisorParent_address (N M : Nat) (hN : 0 < N) (hM : 0 < M)
    (hdiv : N ∣ M) :
    divisorParent N M hN ∘ residueAddress M hM = residueAddress N hN := by
  funext n
  exact Fin.ext (Nat.mod_mod_of_dvd n hdiv)

/-- The manuscript divisibility refinement, with an explicitly onto parent. -/
theorem residueFamily_refines [Semiring R] [AddCommMonoid A] [Module R A]
    (N M : Nat) (hN : 0 < N) (hM : 0 < M) (hdiv : N ∣ M) :
    Refines (residueFamily (R := R) (A := A) N hN)
      (residueFamily (R := R) (A := A) M hM) (divisorParent N M hN) := by
  classical
  refine ⟨divisorParent_surjective N M hN hM hdiv, ?_⟩
  intro j
  change Packet.fibreLinearProj (R := R) (M := A) (residueAddress N hN) j = _
  rw [← divisorParent_address N M hN hM hdiv]
  have h := Packet.fibreLinearProj_refinement (R := R) (M := A)
    (residueAddress M hM) (divisorParent N M hN) j
  simpa [Function.comp_def, residueFamily, Packet.fibreLinearProjectorFamily,
    children, Finset.sum_filter] using h

/-- Coefficients and the power-series constructor are inverse linear maps. -/
def coefficientEquiv [Semiring R] : PowerSeries R ≃ₗ[R] (Nat → R) where
  toFun f n := PowerSeries.coeff n f
  invFun := PowerSeries.mk
  left_inv f := by ext n; simp
  right_inv x := by funext n; simp
  map_add' f g := by funext n; exact map_add (PowerSeries.coeff n) f g
  map_smul' c f := by funext n; exact map_smul (PowerSeries.coeff n) c f

@[simp] theorem coefficientEquiv_apply [Semiring R] (f : PowerSeries R) (n : Nat) :
    coefficientEquiv f n = PowerSeries.coeff n f := rfl

/-- A series residue projector, expressed through its actual coefficient mask. -/
def seriesResidueProj [Semiring R] (N : Nat) (hN : 0 < N) (j : Fin N) :
    Module.End R (PowerSeries R) :=
  coefficientEquiv.symm.toLinearMap.comp
    ((residueProj (R := R) (A := R) N hN j).comp coefficientEquiv.toLinearMap)

@[simp] theorem seriesResidueProj_coeff [Semiring R]
    (N : Nat) (hN : 0 < N) (j : Fin N) (f : PowerSeries R) (n : Nat) :
    PowerSeries.coeff n (seriesResidueProj N hN j f) =
      if residueAddress N hN n = j then PowerSeries.coeff n f else 0 := by
  simp [seriesResidueProj, coefficientEquiv, residueProj_apply, Packet.fibreProj]

@[simp] theorem coefficient_seriesResidueProj [Semiring R]
    (N : Nat) (hN : 0 < N) (j : Fin N) (f : PowerSeries R) :
    coefficientEquiv (seriesResidueProj N hN j f) =
      residueProj (R := R) (A := R) N hN j (coefficientEquiv f) := by
  simp [seriesResidueProj]

/-- The formal-series family carries the exact selector axioms. -/
def seriesResidueFamily [Semiring R] (N : Nat) (hN : 0 < N) :
    LinearProjectorFamily R (PowerSeries R) (Fin N) where
  proj := seriesResidueProj N hN
  idempotent j f := by
    apply coefficientEquiv.injective
    simp only [coefficient_seriesResidueProj]
    exact (residueFamily (R := R) (A := R) N hN).idempotent j _
  orthogonal := by
    intro i j hij f
    apply coefficientEquiv.injective
    simp only [coefficient_seriesResidueProj, map_zero]
    exact (residueFamily (R := R) (A := R) N hN).orthogonal hij _
  complete f := by
    apply coefficientEquiv.injective
    simp only [map_sum, coefficient_seriesResidueProj]
    exact (residueFamily (R := R) (A := R) N hN).complete _

theorem seriesResidueProj_nonzero [Semiring R] [Nontrivial R]
    (N : Nat) (hN : 0 < N) (j : Fin N) :
    seriesResidueProj (R := R) N hN j ≠ 0 := by
  intro hz
  apply residueProj_nonzero (R := R) (A := R) N hN j
  ext x n
  have h := congrArg (fun T : Module.End R (PowerSeries R) =>
    coefficientEquiv (T (coefficientEquiv.symm x)) n) hz
  simpa only [coefficient_seriesResidueProj, LinearEquiv.apply_symm_apply,
    LinearMap.zero_apply, map_zero, Pi.zero_apply] using h

theorem seriesResidueFamily_refines [Semiring R]
    (N M : Nat) (hN : 0 < N) (hM : 0 < M) (hdiv : N ∣ M) :
    Refines (seriesResidueFamily (R := R) N hN) (seriesResidueFamily M hM)
      (divisorParent N M hN) := by
  refine ⟨divisorParent_surjective N M hN hM hdiv, ?_⟩
  intro j
  ext f n
  have h := LinearMap.congr_fun
    (residueFamily_refines (R := R) (A := R) N M hN hM hdiv).coarse_eq_sum_children j
  have hh := congrFun (h (coefficientEquiv f)) n
  simpa [seriesResidueFamily, LinearMap.sum_apply, ← coefficientEquiv_apply,
    coefficient_seriesResidueProj, map_sum, residueFamily,
    Packet.fibreLinearProjectorFamily, residueProj] using hh

/-- The exact CRT selector identity on formal series, not merely coefficient sequences. -/
theorem seriesResidueProj_crt [Semiring R]
    (m n : Nat) (hm : 0 < m) (hn : 0 < n) (hc : m.Coprime n)
    (s : Fin (m * n)) :
    (seriesResidueProj (R := R) m hm (crtComponents m n hm hn s).1).comp
        (seriesResidueProj n hn (crtComponents m n hm hn s).2) =
      seriesResidueProj (m * n) (Nat.mul_pos hm hn) s := by
  ext f
  apply coefficientEquiv.injective
  simp only [LinearMap.comp_apply, coefficient_seriesResidueProj]
  exact LinearMap.congr_fun (residueProj_crt (R := R) (A := R) m n hm hn hc s) _

end Komorebi.Residue
#print axioms Komorebi.Residue.residueFamily_refines
#print axioms Komorebi.Residue.seriesResidueFamily_refines
#print axioms Komorebi.Residue.seriesResidueProj_crt
