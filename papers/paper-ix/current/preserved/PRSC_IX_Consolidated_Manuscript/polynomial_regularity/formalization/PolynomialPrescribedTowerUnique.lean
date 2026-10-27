module
public import PolynomialParameterChart
public import PolynomialPrescribedSystem

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPrescribedTowerUnique

open Komorebi.PolynomialObstruction Komorebi.PolynomialPadicLift
open Komorebi.PolynomialParameterSystem Komorebi.PolynomialParameterChart
open Komorebi.PolynomialLocalSurjective

variable {e k : ℕ}

/-- In the square solved case the rectangular interface is the existing chart block. -/
theorem solvedJacobian_square (p : ℕ)
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ) (x : Fin (e + k) → ℤ) :
    PolynomialPrescribedSystem.solvedJacobian p F x =
      PolynomialParameterSystem.solvedJacobian p F x := rfl

/-- Every exact root with the prescribed parameters is the checked chart point.
The solved block is square; its actual reduction at the initial integer point is surjective. -/
theorem prescribed_root_eq_chartPoint (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ) (x : Fin (e + k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (PolynomialPrescribedSystem.solvedJacobian p F x))
    (t : residueBall p L (freePart x)) (b : Fin (e + k) → ℤ_[p])
    (hb : ∀ i, padicEval p F b i = 0)
    (hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p]))
    (ht : freePart b = t.val) :
    b = (chartPoint p L hL F x hx (by simpa only [solvedJacobian_square] using hJ) t).val := by
  exact congrArg Subtype.val (chartPoint_unique p L hL F x hx
    (by simpa only [solvedJacobian_square] using hJ) t ⟨b, hbx⟩ (funext hb) ht)

/-- Two roots in the initial ball with the same parameters coincide when the solved block is square. -/
theorem prescribed_root_unique (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ) (x : Fin (e + k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (PolynomialPrescribedSystem.solvedJacobian p F x))
    (b c : Fin (e + k) → ℤ_[p])
    (hb : ∀ i, padicEval p F b i = 0) (hc : ∀ i, padicEval p F c i = 0)
    (hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p]))
    (hcx : ∀ i, (p : ℤ_[p])^L ∣ c i - (x i : ℤ_[p]))
    (hparams : freePart b = freePart c) : b = c := by
  let t : residueBall p L (freePart x) :=
    ⟨freePart b, fun j => hbx (Fin.natAdd e j)⟩
  exact (prescribed_root_eq_chartPoint p L hL F x hx hJ t b hb hbx rfl).trans
    (prescribed_root_eq_chartPoint p L hL F x hx hJ t c hc hcx hparams.symm).symm

/-- Tower and parameter-approximation choices do not affect the square-case endpoint.
Only the initial retained precision is needed to place both exact endpoints in the uniqueness ball. -/
theorem prescribed_tower_endpoints_unique (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ) (x : Fin (e + k) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (PolynomialPrescribedSystem.solvedJacobian p F x))
    (z w : ℕ → Fin (e + k) → ℤ) (hz0 : z 0 = x) (hw0 : w 0 = x)
    (b c : Fin (e + k) → ℤ_[p]) (τ : Fin k → ℤ_[p])
    (hb : ∀ i, padicEval p F b i = 0) (hc : ∀ i, padicEval p F c i = 0)
    (hbz : ∀ n i, (p : ℤ_[p])^(L+n) ∣ b i - (z n i : ℤ_[p]))
    (hcw : ∀ n i, (p : ℤ_[p])^(L+n) ∣ c i - (w n i : ℤ_[p]))
    (hbτ : freePart b = τ) (hcτ : freePart c = τ) : b = c := by
  apply prescribed_root_unique p L hL F x hx hJ b c hb hc
  · simpa only [Nat.add_zero, hz0] using hbz 0
  · simpa only [Nat.add_zero, hw0] using hcw 0
  · exact hbτ.trans hcτ.symm

end Komorebi.PolynomialPrescribedTowerUnique
